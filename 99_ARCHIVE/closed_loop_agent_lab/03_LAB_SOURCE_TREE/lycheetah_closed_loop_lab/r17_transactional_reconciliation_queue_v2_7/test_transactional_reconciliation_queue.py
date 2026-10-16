from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stripe_webhook_inbox import (
    InboxAction,
    InboxIntegrityError,
    ReconciliationQueueError,
    StripeWebhookInbox,
)

NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)
TS = int(NOW.timestamp())
SECRET = "whsec_local_test_secret_value_for_unit_tests"
KEY = b"local-unit-test-hmac-integrity-key-material-32+bytes"


def sign(raw: bytes, timestamp: int = TS) -> str:
    message = str(timestamp).encode("ascii") + b"." + raw
    sig = hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


def event_body(*, event_id="evt_queue_001", operation_id="op_queue_001",
               event_type="refund.updated", status="succeeded", include_operation=True,
               refund_id="re_queue_001", charge="ch_queue_001", payment_intent="pi_queue_001"):
    metadata = {"customer_note": "PRIVATE SHOULD NOT PERSIST"}
    if include_operation:
        metadata["lycheetah_operation_id"] = operation_id
    payload = {
        "id": event_id,
        "object": "event",
        "type": event_type,
        "created": TS - 10,
        "livemode": False,
        "data": {"object": {
            "object": "refund", "id": refund_id, "charge": charge,
            "payment_intent": payment_intent, "amount": 2500, "currency": "usd",
            "status": status, "livemode": False, "metadata": metadata,
            "description": "DO NOT RETAIN", "client_secret": "secret-never-store",
        }},
    }
    return json.dumps(payload, separators=(",", ":")).encode()


class TransactionalQueueCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "inbox.sqlite")
        self.inbox = self.make_inbox()

    def tearDown(self):
        self.temp.cleanup()

    def make_inbox(self):
        return StripeWebhookInbox(
            path=self.path, integrity_key=KEY,
            endpoint_secrets={"current": SECRET},
            timestamp_tolerance_seconds=300,
            allow_test_clock_override=True,
        )

    def send(self, raw=None, *, now=NOW, timestamp=TS):
        raw = raw or event_body()
        return self.inbox.ingest(raw, sign(raw, timestamp), now=now)

    def job(self, event_id="evt_queue_001"):
        return self.inbox.get_reconciliation_job(event_id)

    def claim(self, *, worker="worker-001", now=NOW, lease_seconds=60):
        values = self.inbox.claim_reconciliation_jobs(
            worker_id=worker, limit=10, lease_seconds=lease_seconds, now=now
        )
        return values

    def test_ingestion_and_reconciliation_job_are_created_together(self):
        result = self.send()
        self.assertEqual(result.action, InboxAction.INGESTED)
        row = self.job()
        self.assertEqual(row["state"], "PENDING")
        self.assertEqual(row["operation_id"], "op_queue_001")
        self.assertEqual(row["refund_id"], "re_queue_001")
        self.assertEqual(row["attempts"], 0)

    def test_queue_write_failure_rolls_back_inbox_insert(self):
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TRIGGER force_queue_failure BEFORE INSERT ON stripe_reconciliation_jobs
                          BEGIN SELECT RAISE(ABORT, 'synthetic queue write failure'); END""")
        result = self.send()
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertIsNone(self.inbox.get("evt_queue_001"))
        self.assertIsNone(self.job())

    def test_duplicate_delivery_creates_only_one_job(self):
        raw = event_body()
        self.assertEqual(self.send(raw).action, InboxAction.INGESTED)
        self.assertEqual(self.send(raw, now=NOW + timedelta(seconds=1), timestamp=TS + 1).action,
                         InboxAction.DUPLICATE)
        self.assertEqual(len(self.inbox.list_reconciliation_jobs(operation_id="op_queue_001")), 1)

    def test_event_without_operation_correlation_goes_to_manual_queue(self):
        result = self.send(event_body(include_operation=False))
        self.assertEqual(result.action, InboxAction.INGESTED)
        job = self.job()
        self.assertEqual(job["state"], "MANUAL")
        self.assertEqual(job["last_error_code"], "missing-operation-correlation")
        self.assertEqual(self.claim(), [])

    def test_webhook_event_status_is_not_copied_into_refund_success_state(self):
        self.send(event_body(status="succeeded"))
        job = self.job()
        self.assertEqual(job["state"], "PENDING")
        self.assertNotIn("provider_refund_state", job)
        self.assertNotEqual(job["state"], "SUCCEEDED")

    def test_claim_returns_single_use_token_but_database_stores_only_digest(self):
        self.send()
        claimed = self.claim()
        self.assertEqual(len(claimed), 1)
        token = claimed[0]["claim_token"]
        self.assertGreaterEqual(len(token), 32)
        with sqlite3.connect(self.path) as db:
            stored = db.execute("SELECT claim_token_sha256 FROM stripe_reconciliation_jobs WHERE event_id=?",
                                ("evt_queue_001",)).fetchone()[0]
        self.assertEqual(stored, hashlib.sha256(token.encode()).hexdigest())
        self.assertNotEqual(stored, token)

    def test_two_concurrent_workers_cannot_both_claim_one_job(self):
        self.send()
        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()

        def worker(name):
            barrier.wait()
            value = self.inbox.claim_reconciliation_jobs(worker_id=name, limit=1,
                                                         lease_seconds=60, now=NOW)
            with lock:
                outcomes.append((name, value))

        threads = [threading.Thread(target=worker, args=(name,)) for name in ("worker-A", "worker-B")]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(sum(len(value) for _, value in outcomes), 1)

    def test_wrong_worker_cannot_finish_job(self):
        self.send()
        item = self.claim(worker="worker-A")[0]
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-B",
                claim_token=item["claim_token"], disposition="RECONCILED", now=NOW)

    def test_wrong_claim_token_cannot_finish_job(self):
        self.send()
        item = self.claim()[0]
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
                claim_token="x" * len(item["claim_token"]), disposition="RECONCILED", now=NOW)

    def test_claimed_lease_expiry_requeues_work_and_invalidates_old_token(self):
        self.send()
        first = self.claim(lease_seconds=5)[0]
        later = NOW + timedelta(seconds=6)
        second = self.claim(worker="worker-002", now=later, lease_seconds=30)[0]
        self.assertNotEqual(first["claim_token"], second["claim_token"])
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=first["event_id"], worker_id="worker-001",
                claim_token=first["claim_token"], disposition="RECONCILED", now=later)

    def test_expired_claim_cannot_be_completed_even_before_reclaimed(self):
        self.send()
        item = self.claim(lease_seconds=5)[0]
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
                claim_token=item["claim_token"], disposition="RECONCILED", now=NOW + timedelta(seconds=5))

    def test_retry_delay_prevents_immediate_reclaim(self):
        self.send()
        item = self.claim()[0]
        result = self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
            claim_token=item["claim_token"], disposition="RETRY", now=NOW,
            retry_after_seconds=30, reason_code="provider-timeout")
        self.assertEqual(result.state, "PENDING")
        self.assertEqual(self.claim(now=NOW + timedelta(seconds=29)), [])
        self.assertEqual(len(self.claim(worker="worker-002", now=NOW + timedelta(seconds=30))), 1)

    def test_retry_attempt_limit_routes_to_manual_reconciliation(self):
        self.send()
        now = NOW
        for attempt in range(8):
            claimed = self.claim(worker=f"worker-{attempt+100}", now=now, lease_seconds=60)
            self.assertEqual(len(claimed), 1)
            self.inbox.finish_reconciliation_job(event_id=claimed[0]["event_id"],
                worker_id=f"worker-{attempt+100}", claim_token=claimed[0]["claim_token"],
                disposition="RETRY", now=now, retry_after_seconds=1, reason_code="provider-timeout")
            now += timedelta(seconds=2)
        job = self.job()
        self.assertEqual(job["state"], "MANUAL")
        self.assertEqual(job["last_error_code"], "max-attempts-exhausted")

    def test_eighth_crashed_lease_exhaustion_routes_to_manual(self):
        self.send()
        now = NOW
        for attempt in range(8):
            claimed = self.claim(worker=f"crasher-{attempt+100}", now=now, lease_seconds=1)
            self.assertEqual(len(claimed), 1)
            now += timedelta(seconds=2)
        # The last issued lease also needs to expire; then recovery must move it
        # to MANUAL instead of issuing a ninth attempt.
        self.assertEqual(self.claim(now=now), [])
        job = self.job()
        self.assertEqual(job["state"], "MANUAL")
        self.assertEqual(job["last_error_code"], "lease-expired-max-attempts")

    def test_reconciled_means_queue_work_recorded_not_refund_success(self):
        self.send()
        item = self.claim()[0]
        result = self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
            claim_token=item["claim_token"], disposition="RECONCILED", now=NOW)
        self.assertEqual(result.state, "DONE")
        self.assertEqual(result.reason, "reconciliation-work-recorded")
        self.assertNotIn("refund_status", result.to_dict())

    def test_done_job_is_persistent_across_restart(self):
        self.send()
        item = self.claim()[0]
        self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
            claim_token=item["claim_token"], disposition="RECONCILED", now=NOW)
        self.inbox = self.make_inbox()
        self.assertEqual(self.job()["state"], "DONE")
        self.assertEqual(self.claim(), [])

    def test_job_row_tamper_is_detected(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE stripe_reconciliation_jobs SET state='DONE' WHERE event_id=?", ("evt_queue_001",))
        with self.assertRaises(InboxIntegrityError):
            self.job()

    def test_event_row_and_job_row_rollback_together_if_inbox_write_fails(self):
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TRIGGER force_inbox_failure BEFORE INSERT ON stripe_webhook_inbox
                          BEGIN SELECT RAISE(ABORT, 'synthetic inbox write failure'); END""")
        result = self.send()
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertEqual(self.inbox.list_reconciliation_jobs(), [])

    def test_failed_or_pending_webhook_still_only_enqueues_reconciliation(self):
        self.send(event_body(event_id="evt_pending", status="pending"))
        self.send(event_body(event_id="evt_failed", event_type="refund.failed", status="failed"),
                  now=NOW + timedelta(seconds=1), timestamp=TS + 1)
        self.assertEqual(self.job("evt_pending")["state"], "PENDING")
        self.assertEqual(self.job("evt_failed")["state"], "PENDING")

    def test_queue_mac_is_checked_before_claim(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE stripe_reconciliation_jobs SET attempts=4 WHERE event_id=?", ("evt_queue_001",))
        with self.assertRaises(InboxIntegrityError):
            self.claim()

    def test_invalid_finish_disposition_is_rejected(self):
        self.send()
        item = self.claim()[0]
        with self.assertRaises(ValueError):
            self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
                claim_token=item["claim_token"], disposition="SUCCEEDED", now=NOW)

    def test_retry_reason_code_cannot_store_arbitrary_provider_text(self):
        self.send()
        item = self.claim()[0]
        with self.assertRaises(ValueError):
            self.inbox.finish_reconciliation_job(event_id=item["event_id"], worker_id="worker-001",
                claim_token=item["claim_token"], disposition="RETRY", now=NOW,
                retry_after_seconds=30, reason_code="private cardholder details")

    def test_public_queue_api_does_not_expose_integrity_or_claim_digest(self):
        self.send()
        item = self.claim()[0]
        for forbidden in ("row_hmac_sha256", "claim_token_sha256"):
            self.assertNotIn(forbidden, item)
        listed = self.inbox.list_reconciliation_jobs()[0]
        for forbidden in ("row_hmac_sha256", "claim_token_sha256", "claim_token"):
            self.assertNotIn(forbidden, listed)


    def test_reopen_database_under_different_connected_account_routes_job_to_manual(self):
        connected_inbox = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            expected_account="acct_123", allow_test_clock_override=True,
        )
        raw = event_body()
        body = json.loads(raw)
        body["account"] = "acct_123"
        raw = json.dumps(body, separators=(",", ":")).encode()
        connected_inbox.ingest(raw, sign(raw), now=NOW)

        wrong_scope = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            expected_account="acct_456", allow_test_clock_override=True,
        )
        self.assertEqual(wrong_scope.claim_reconciliation_jobs(worker_id="worker-004", now=NOW), [])
        job = wrong_scope.get_reconciliation_job("evt_queue_001")
        self.assertEqual(job["state"], "MANUAL")
        self.assertEqual(job["last_error_code"], "inbox-account-scope-mismatch")

    def test_reopen_platform_database_under_connect_scope_cannot_claim_old_job(self):
        self.send()
        wrong_scope = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            expected_account="acct_999", allow_test_clock_override=True,
        )
        self.assertEqual(wrong_scope.claim_reconciliation_jobs(worker_id="worker-005", now=NOW), [])
        self.assertEqual(wrong_scope.get_reconciliation_job("evt_queue_001")["state"], "MANUAL")

    def test_scope_change_after_claim_prevents_job_completion(self):
        connected_inbox = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            expected_account="acct_123", allow_test_clock_override=True,
        )
        body = json.loads(event_body())
        body["account"] = "acct_123"
        raw = json.dumps(body, separators=(",", ":")).encode()
        connected_inbox.ingest(raw, sign(raw), now=NOW)
        item = connected_inbox.claim_reconciliation_jobs(worker_id="worker-006", now=NOW)[0]
        switched_scope = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            expected_account="acct_456", allow_test_clock_override=True,
        )
        with self.assertRaises(ReconciliationQueueError):
            switched_scope.finish_reconciliation_job(event_id=item["event_id"],
                worker_id="worker-006", claim_token=item["claim_token"],
                disposition="RECONCILED", now=NOW)


    def test_upgrade_backfills_verified_legacy_inbox_rows_into_queue(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE stripe_reconciliation_jobs")
        upgraded = self.make_inbox()
        jobs = upgraded.list_reconciliation_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["event_id"], "evt_queue_001")
        self.assertEqual(jobs[0]["state"], "PENDING")
        self.assertEqual(len(upgraded.claim_reconciliation_jobs(worker_id="migration-worker", now=NOW)), 1)

    def test_upgrade_refuses_to_backfill_tampered_legacy_inbox_row(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE stripe_reconciliation_jobs")
            db.execute("UPDATE stripe_webhook_inbox SET operation_id='forged-op' WHERE event_id=?",
                       ("evt_queue_001",))
        with self.assertRaises(InboxIntegrityError):
            self.make_inbox()


    def test_fifty_repeated_two_worker_claim_races_never_double_claim_an_event(self):
        for index in range(50):
            event_id = f"evt_race_{index:03d}"
            operation_id = f"op-race-{index:03d}"
            raw = event_body(event_id=event_id, operation_id=operation_id,
                             refund_id=f"re_race_{index:03d}",
                             charge=f"ch_race_{index:03d}",
                             payment_intent=f"pi_race_{index:03d}")
            self.send(raw, now=NOW, timestamp=TS)
            barrier = threading.Barrier(2)
            claims = []
            lock = threading.Lock()
            def compete(name):
                barrier.wait()
                result = self.inbox.claim_reconciliation_jobs(
                    worker_id=name, limit=1, lease_seconds=60, now=NOW
                )
                with lock:
                    claims.extend(result)
            threads = [threading.Thread(target=compete, args=(f"race-worker-{index}-a",)),
                       threading.Thread(target=compete, args=(f"race-worker-{index}-b",))]
            for thread in threads: thread.start()
            for thread in threads: thread.join(timeout=5)
            self.assertTrue(all(not thread.is_alive() for thread in threads))
            self.assertEqual(len(claims), 1, f"event {event_id} was claimed {len(claims)} times")
            self.assertEqual(claims[0]["event_id"], event_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
