from __future__ import annotations

from contextlib import closing

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from operation_ledger import (
    OperationLedgerError, OperationLedgerIntegrityError, TrustedOperationLedger,
)
from reconciliation_worker import (
    ProviderNotFoundError, TransientProviderReadError, TrustedReconciliationWorker,
)
from stripe_webhook_inbox import InboxAction, InboxIntegrityError, ReconciliationQueueError, StripeWebhookInbox

NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)
TS = int(NOW.timestamp())
SECRET = "whsec_local_test_secret_value_for_unit_tests"
KEY = b"local-unit-test-hmac-integrity-key-material-32+bytes"
OP = "op_worker_001"
EVENT = "evt_worker_001"
REFUND = "re_worker_001"
CHARGE = "ch_worker_001"
PI = "pi_worker_001"


def sign(raw: bytes, timestamp: int = TS) -> str:
    mac = hmac.new(SECRET.encode(), str(timestamp).encode() + b"." + raw, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={mac}"


def webhook_body(*, event_id: str = EVENT, operation_id: str | None = OP,
                 refund_id: str = REFUND, charge: str = CHARGE,
                 payment_intent: str = PI, status: str = "pending",
                 amount: int = 2500, currency: str = "usd", account: str | None = None) -> bytes:
    metadata = {"note": "NEVER_STORE_THIS_PROVIDER_METADATA"}
    if operation_id is not None:
        metadata["lycheetah_operation_id"] = operation_id
    event = {
        "id": event_id, "object": "event", "type": "refund.updated",
        "created": TS - 2, "livemode": False, "data": {"object": {
            "object": "refund", "id": refund_id, "charge": charge,
            "payment_intent": payment_intent, "amount": amount, "currency": currency,
            "status": status, "livemode": False, "metadata": metadata,
            "description": "DO NOT PERSIST", "client_secret": "secret-never-store",
        }},
    }
    if account is not None:
        event["account"] = account
    return json.dumps(event, separators=(",", ":")).encode()


class FakeProvider:
    account_scope = "platform"
    livemode = False

    def __init__(self, status: str = "succeeded"):
        self.status = status
        self.calls: list[str] = []
        self.snapshot_extra: dict[str, Any] = {}
        self.error: Exception | None = None

    def retrieve_refund(self, refund_id: str) -> Mapping[str, Any]:
        self.calls.append(refund_id)
        if self.error is not None:
            raise self.error
        result: dict[str, Any] = {
            "id": REFUND, "object": "refund", "status": self.status,
            "charge": CHARGE, "payment_intent": PI, "amount": 2500,
            "currency": "usd", "livemode": False,
            "metadata": {"lycheetah_operation_id": OP, "unneeded-private-field": "DO NOT PERSIST"},
            "description": "PRIVATE RESPONSE FIELD",
            "client_secret": "cs_test_PRIVATE_NEVER_PERSIST",
            "receipt_number": "SENSITIVE-REFERENCE",
        }
        result.update(self.snapshot_extra)
        return result


class TrustedReconciliationWorkerCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "worker.sqlite")
        self.inbox = StripeWebhookInbox(
            path=self.path, integrity_key=KEY, endpoint_secrets={"current": SECRET},
            timestamp_tolerance_seconds=300, allow_test_clock_override=True,
        )
        self.ledger = TrustedOperationLedger(path=self.path, integrity_key=KEY)
        self.ledger.register_operation(operation_id=OP, account_scope="platform",
            target_type="charge", target_id=CHARGE, amount=2500, currency="usd", now=NOW)
        self.provider = FakeProvider("succeeded")
        self.worker = TrustedReconciliationWorker(inbox=self.inbox, ledger=self.ledger,
            provider=self.provider, worker_id="trusted-worker-01", retry_after_seconds=30)

    def tearDown(self):
        self.temp.cleanup()

    def ingest(self, raw: bytes | None = None, *, now: datetime = NOW, timestamp: int = TS):
        raw = raw or webhook_body()
        return self.inbox.ingest(raw, sign(raw, timestamp), now=now)

    def run_one(self, *, now: datetime = NOW, lease_seconds: int = 120):
        return self.worker.run_once(limit=10, lease_seconds=lease_seconds, now=now)

    def test_succeeded_provider_state_is_durably_recorded_before_queue_done(self):
        self.ingest()
        results = self.run_one()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].action, "RECONCILED")
        self.assertEqual(results[0].ledger_state, "PROVIDER_SUCCEEDED")
        self.assertEqual(self.inbox.get_reconciliation_job(EVENT)["state"], "DONE")
        self.assertEqual(self.ledger.get_operation(OP)["refund_status"], "succeeded")

    def test_pending_provider_state_is_recorded_then_job_retried(self):
        self.provider.status = "pending"
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "RETRY")
        self.assertEqual(result.ledger_state, "WAITING_PROVIDER")
        self.assertEqual(self.inbox.get_reconciliation_job(EVENT)["state"], "PENDING")
        self.assertEqual(self.ledger.get_operation(OP)["refund_status"], "pending")

    def test_pending_then_succeeded_reconciles_on_retry(self):
        self.provider.status = "pending"
        self.ingest()
        self.assertEqual(self.run_one()[0].action, "RETRY")
        self.provider.status = "succeeded"
        result = self.run_one(now=NOW + timedelta(seconds=30))[0]
        self.assertEqual(result.action, "RECONCILED")
        self.assertEqual(self.ledger.get_operation(OP)["state"], "PROVIDER_SUCCEEDED")

    def test_failed_refund_is_recorded_as_provider_failed_not_success(self):
        self.provider.status = "failed"
        self.ingest(webhook_body(status="failed", event_id=EVENT))
        result = self.run_one()[0]
        self.assertEqual(result.action, "RECONCILED")
        self.assertEqual(result.ledger_state, "PROVIDER_FAILED")
        self.assertNotEqual(result.ledger_state, "PROVIDER_SUCCEEDED")

    def test_canceled_refund_is_recorded_distinctly(self):
        self.provider.status = "canceled"
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.ledger_state, "PROVIDER_CANCELED")

    def test_requires_action_routes_to_manual(self):
        self.provider.status = "requires_action"
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(self.ledger.get_operation(OP)["state"], "MANUAL")

    def test_unknown_operation_is_manual_without_provider_call(self):
        self.ingest(webhook_body(operation_id="op_unknown_001"))
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(self.provider.calls, [])

    def test_provider_scope_mismatch_is_manual_without_provider_call(self):
        self.provider.account_scope = "acct_wrong"
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(self.provider.calls, [])

    def test_live_mode_provider_client_is_rejected(self):
        self.provider.livemode = True
        self.ingest()
        self.assertEqual(self.run_one()[0].action, "MANUAL")
        self.assertEqual(self.provider.calls, [])

    def test_provider_refund_id_mismatch_is_manual(self):
        self.provider.snapshot_extra["id"] = "re_other_001"
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(result.reason, "provider-refund-id-mismatch")

    def test_provider_operation_metadata_mismatch_is_manual(self):
        self.provider.snapshot_extra["metadata"] = {"lycheetah_operation_id": "op_wrong_001"}
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-operation-correlation-mismatch")

    def test_provider_target_mismatch_is_manual(self):
        self.provider.snapshot_extra["charge"] = "ch_another_001"
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-target-mismatch")

    def test_provider_amount_mismatch_is_manual(self):
        self.provider.snapshot_extra["amount"] = 2499
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-amount-mismatch")

    def test_provider_currency_mismatch_is_manual(self):
        self.provider.snapshot_extra["currency"] = "eur"
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-currency-mismatch")

    def test_live_mode_refund_snapshot_is_manual(self):
        self.provider.snapshot_extra["livemode"] = True
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-livemode-mismatch")

    def test_wrong_snapshot_shape_is_manual(self):
        self.provider.snapshot_extra["object"] = "charge"
        self.ingest()
        self.assertEqual(self.run_one()[0].reason, "provider-object-type-invalid")

    def test_transient_provider_read_retries_without_finishing_job(self):
        self.provider.error = TransientProviderReadError("do not persist this text")
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "RETRY")
        self.assertEqual(self.inbox.get_reconciliation_job(EVENT)["state"], "PENDING")
        self.assertNotIn("do not persist", json.dumps(self.inbox.get_reconciliation_job(EVENT)))

    def test_provider_not_found_is_not_interpreted_as_refund_absence(self):
        self.provider.error = ProviderNotFoundError("not found")
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "RETRY")
        self.assertNotEqual(result.ledger_state, "PROVIDER_FAILED")

    def test_unknown_provider_exception_routes_manual_without_leaking_error(self):
        self.provider.error = RuntimeError("PRIVATE KEY SECRET RESPONSE")
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertNotIn("PRIVATE KEY", result.reason)
        self.assertNotIn("PRIVATE KEY", json.dumps(self.inbox.list_reconciliation_jobs()))

    def test_ledger_does_not_persist_full_provider_object_or_metadata(self):
        self.ingest()
        self.run_one()
        with closing(sqlite3.connect(self.path)) as db, db:
            raw = db.execute("SELECT * FROM lycheetah_refund_operation_ledger").fetchall()
        blob = json.dumps(raw)
        for marker in ("PRIVATE RESPONSE FIELD", "cs_test_PRIVATE_NEVER_PERSIST", "SENSITIVE-REFERENCE", "DO NOT PERSIST"):
            self.assertNotIn(marker, blob)
        with closing(sqlite3.connect(self.path)) as db:
            names = [row[1] for row in db.execute("PRAGMA table_info(lycheetah_refund_operation_ledger)")]
        self.assertIn("observation_sha256", names)

    def test_ledger_tampering_routes_manual_and_never_queries_provider(self):
        self.ingest()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE lycheetah_refund_operation_ledger SET state='PROVIDER_SUCCEEDED' WHERE operation_id=?", (OP,))
        result = self.run_one()[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(result.reason, "operation-ledger-authentication-failed")
        self.assertEqual(self.provider.calls, [])

    def test_queue_done_is_rejected_without_a_terminal_authenticated_record(self):
        self.ingest()
        job = self.inbox.claim_reconciliation_jobs(worker_id="trusted-worker-01", now=NOW)[0]
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=job["event_id"], worker_id="trusted-worker-01",
                claim_token=job["claim_token"], disposition="RECONCILED", now=NOW)

    def test_direct_db_row_tamper_of_ledger_after_observation_rejected_by_queue_guard(self):
        self.ingest()
        # A valid worker run commits the terminal record and acknowledges queue.
        self.run_one()
        # Done rows already complete, so prove guard on a second independent event.
        event2 = "evt_worker_002"
        self.ingest(webhook_body(event_id=event2), now=NOW + timedelta(seconds=1), timestamp=TS + 1)
        job = self.inbox.claim_reconciliation_jobs(worker_id="trusted-worker-02", now=NOW + timedelta(seconds=1))[0]
        # Restore job as claimed but tamper ledger state without recomputing MAC.
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("UPDATE lycheetah_refund_operation_ledger SET state='PROVIDER_FAILED' WHERE operation_id=?", (OP,))
        with self.assertRaises(InboxIntegrityError):
            self.inbox.finish_reconciliation_job(event_id=job["event_id"], worker_id="trusted-worker-02",
                claim_token=job["claim_token"], disposition="RECONCILED", now=NOW + timedelta(seconds=1))

    def test_out_of_order_webhook_does_not_override_retrieved_current_state(self):
        self.ingest(webhook_body(event_id=EVENT, status="pending"))
        self.provider.status = "succeeded"
        first = self.run_one()[0]
        self.assertEqual(first.ledger_state, "PROVIDER_SUCCEEDED")
        # A late separate event whose snapshot says pending is only a trigger;
        # provider retrieve still returns the current succeeded state.
        event2 = "evt_worker_old_002"
        self.ingest(webhook_body(event_id=event2, status="pending"), now=NOW + timedelta(seconds=1), timestamp=TS + 1)
        second = self.run_one(now=NOW + timedelta(seconds=1))[0]
        self.assertEqual(second.ledger_state, "PROVIDER_SUCCEEDED")

    def test_same_operation_id_cannot_be_registered_with_different_intent(self):
        with self.assertRaises(OperationLedgerError):
            self.ledger.register_operation(operation_id=OP, account_scope="platform",
                target_type="charge", target_id=CHARGE, amount=1, currency="usd", now=NOW)

    def test_exact_registration_is_idempotent(self):
        first = self.ledger.register_operation(operation_id=OP, account_scope="platform",
            target_type="charge", target_id=CHARGE, amount=2500, currency="usd", now=NOW)
        second = self.ledger.register_operation(operation_id=OP, account_scope="platform",
            target_type="charge", target_id=CHARGE, amount=2500, currency="usd", now=NOW + timedelta(seconds=1))
        self.assertEqual(first["state"], second["state"])
        self.assertEqual(first["updated_at"], second["updated_at"])

    def test_terminal_state_cannot_regress_to_pending(self):
        self.ingest()
        self.run_one()
        # A conflicting live retrieval that says pending after terminal success is escalated.
        self.provider.status = "pending"
        event2 = "evt_worker_regression_002"
        self.ingest(webhook_body(event_id=event2), now=NOW + timedelta(seconds=1), timestamp=TS + 1)
        result = self.run_one(now=NOW + timedelta(seconds=1))[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(self.ledger.get_operation(OP)["state"], "MANUAL")
        self.assertEqual(self.ledger.get_operation(OP)["manual_reason"], "provider-status-regressed")

    def test_lost_queue_ack_after_ledger_commit_is_recoverable(self):
        self.ingest()
        original = self.inbox.finish_reconciliation_job
        called = {"first": True}
        def fail_once(**kwargs):
            if called["first"]:
                called["first"] = False
                raise RuntimeError("synthetic queue ack crash")
            return original(**kwargs)
        self.inbox.finish_reconciliation_job = fail_once  # type: ignore[method-assign]
        with self.assertRaises(RuntimeError):
            self.run_one(lease_seconds=1)
        self.assertEqual(self.ledger.get_operation(OP)["state"], "PROVIDER_SUCCEEDED")
        self.inbox.finish_reconciliation_job = original  # type: ignore[method-assign]
        result = self.run_one(now=NOW + timedelta(seconds=2), lease_seconds=10)[0]
        self.assertEqual(result.action, "RECONCILED")
        self.assertEqual(self.ledger.get_operation(OP)["state"], "PROVIDER_SUCCEEDED")

    def test_platform_ledger_record_is_scoped_to_platform_webhook(self):
        connected = StripeWebhookInbox(path=self.path, integrity_key=KEY,
            endpoint_secrets={"current": SECRET}, expected_account="acct_123",
            timestamp_tolerance_seconds=300, allow_test_clock_override=True)
        raw = webhook_body(event_id="evt_worker_connect_001", account="acct_123")
        connected.ingest(raw, sign(raw), now=NOW)
        # Connected inbox cannot use platform provider account configuration.
        worker = TrustedReconciliationWorker(inbox=connected, ledger=self.ledger,
            provider=self.provider, worker_id="connected-worker-01")
        result = worker.run_once(now=NOW)[0]
        self.assertEqual(result.action, "MANUAL")
        self.assertEqual(self.provider.calls, [])

    def test_queue_done_guard_accepts_matching_authenticated_terminal_record(self):
        self.ingest()
        job = self.inbox.claim_reconciliation_jobs(worker_id="trusted-worker-01", now=NOW)[0]
        self.ledger.record_provider_observation(operation_id=OP, event_id=EVENT, snapshot={
            "id": REFUND, "status": "succeeded", "charge": CHARGE, "payment_intent": PI,
            "amount": 2500, "currency": "usd", "livemode": False,
            "metadata_operation_id": OP,
        }, now=NOW)
        # The job itself is still bound to correct params; forged function call should pass only if
        # the authenticated ledger binds matching amount/account/target/refund.
        result = self.inbox.finish_reconciliation_job(event_id=job["event_id"], worker_id="trusted-worker-01",
            claim_token=job["claim_token"], disposition="RECONCILED", now=NOW)
        self.assertEqual(result.state, "DONE")


    def test_inbox_and_operation_ledger_must_share_one_database(self):
        other_path = str(Path(self.temp.name) / "other.sqlite")
        other_ledger = TrustedOperationLedger(path=other_path, integrity_key=KEY)
        with self.assertRaises(ValueError):
            TrustedReconciliationWorker(inbox=self.inbox, ledger=other_ledger,
                provider=self.provider, worker_id="worker-other-db")

    def test_queue_done_guard_requires_observation_bound_to_same_event(self):
        self.ingest(webhook_body(event_id=EVENT))
        other_event = "evt_worker_other_002"
        self.ingest(webhook_body(event_id=other_event), now=NOW + timedelta(seconds=1), timestamp=TS + 1)
        # A trusted current-state observation tied to event A must not be used to
        # acknowledge event B without an event-B reconciliation.
        self.ledger.record_provider_observation(operation_id=OP, event_id=EVENT, snapshot={
            "id": REFUND, "status": "succeeded", "charge": CHARGE, "payment_intent": PI,
            "amount": 2500, "currency": "usd", "livemode": False,
            "metadata_operation_id": OP,
        }, now=NOW)
        claimed_a = self.inbox.claim_reconciliation_jobs(
            worker_id="event-bound-worker", limit=10, now=NOW)
        self.assertEqual([job["event_id"] for job in claimed_a], [EVENT])
        claimed_b = self.inbox.claim_reconciliation_jobs(
            worker_id="event-bound-worker", limit=10, now=NOW + timedelta(seconds=1))
        self.assertEqual([job["event_id"] for job in claimed_b], [other_event])
        with self.assertRaises(ReconciliationQueueError):
            self.inbox.finish_reconciliation_job(event_id=other_event, worker_id="event-bound-worker",
                claim_token=claimed_b[0]["claim_token"], disposition="RECONCILED", now=NOW + timedelta(seconds=1))


    def test_authenticated_terminal_record_keeps_done_job_across_restart(self):
        self.ingest()
        result = self.run_one()[0]
        self.assertEqual(result.action, "RECONCILED")
        self.inbox = StripeWebhookInbox(path=self.path, integrity_key=KEY,
            endpoint_secrets={"current": SECRET}, timestamp_tolerance_seconds=300,
            allow_test_clock_override=True)
        self.assertEqual(self.inbox.get_reconciliation_job(EVENT)["state"], "DONE")

    def test_unsupported_target_configuration_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.register_operation(operation_id="op_bad_target", account_scope="platform",
                target_type="charge", target_id=PI, amount=1, currency="usd", now=NOW)

    def test_provider_nonmapping_json_shape_is_manual(self):
        self.provider.retrieve_refund = lambda _refund_id: ["not", "mapping"]  # type: ignore[method-assign]
        self.ingest()
        self.assertEqual(self.run_one()[0].action, "MANUAL")

    def test_ledger_records_no_raw_provider_response_and_only_hashed_observation(self):
        self.ingest()
        self.run_one()
        row = self.ledger.get_operation(OP)
        self.assertRegex(row["observation_sha256"], r"^[a-f0-9]{64}$")
        self.assertNotIn("metadata", row)
        self.assertNotIn("client_secret", row)
        self.assertNotIn("description", row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
