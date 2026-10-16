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
    ALLOWED_EVENT_TYPES, InboxAction, InboxIntegrityError, StripeWebhookInbox,
    WebhookVerificationError, MAX_WEBHOOK_BODY_BYTES,
)

NOW = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)
TS = int(NOW.timestamp())
SECRET = "whsec_local_test_secret_value_for_unit_tests"
OLD_SECRET = "whsec_previous_rotation_secret_for_tests"
KEY = b"local-unit-test-hmac-integrity-key-material-32+bytes"


def _sign(raw: bytes, *, secret: str = SECRET, timestamp: int = TS,
          extras: tuple[str, ...] = ()) -> str:
    msg = str(timestamp).encode("ascii") + b"." + raw
    sig = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    parts = [f"t={timestamp}", *[f"v0={x}" for x in extras], f"v1={sig}"]
    return ",".join(parts)


def event_body(*, event_id="evt_test_001", event_type="refund.updated",
               operation_id="op_001", refund_id="re_test_001", amount=2500,
               currency="usd", status="succeeded", charge="ch_test_001",
               payment_intent="pi_test_001", livemode=False, account=None,
               extras=None):
    refund = {
        "id": refund_id,
        "object": "refund",
        "charge": charge,
        "payment_intent": payment_intent,
        "amount": amount,
        "currency": currency,
        "status": status,
        "livemode": livemode,
        "metadata": {"lycheetah_operation_id": operation_id, "customer_note": "DO_NOT_PERSIST"},
        "description": "PRIVATE DESCRIPTION MUST NOT BE SAVED",
        "client_secret": "secret_do_not_store",
        "receipt_url": "https://example.invalid/private-receipt",
    }
    body = {
        "id": event_id,
        "object": "event",
        "type": event_type,
        "created": TS - 10,
        "livemode": False,
        "data": {"object": refund, "previous_attributes": {"status": "pending"}},
    }
    if account is not None:
        body["account"] = account
    if extras:
        body.update(extras)
    return json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class InboxCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "webhook-inbox.sqlite")
        self.inbox = self.make_inbox()

    def tearDown(self):
        self.temp.cleanup()

    def make_inbox(self, *, secrets=None, expected_account=None, key=KEY,
                   allow_test_clock_override=True, tolerance=300):
        return StripeWebhookInbox(
            path=self.path,
            integrity_key=key,
            endpoint_secrets=secrets or {"current": SECRET},
            expected_account=expected_account,
            timestamp_tolerance_seconds=tolerance,
            allow_test_clock_override=allow_test_clock_override,
        )

    def send(self, raw=None, *, header=None, secret=SECRET, timestamp=TS, now=NOW):
        raw = raw if raw is not None else event_body()
        header = header if header is not None else _sign(raw, secret=secret, timestamp=timestamp)
        return self.inbox.ingest(raw, header, now=now)

    def test_valid_event_is_ingested_then_readable_after_restart(self):
        raw = event_body()
        result = self.send(raw)
        self.assertEqual(result.action, InboxAction.INGESTED)
        self.assertEqual(result.event_id, "evt_test_001")
        restarted = self.make_inbox()
        record = restarted.get("evt_test_001")
        self.assertEqual(record["refund_id"], "re_test_001")
        self.assertEqual(record["operation_id"], "op_001")
        self.assertFalse(record["livemode"])

    def test_verified_webhook_never_directly_claims_success(self):
        self.send()
        hint = self.inbox.reconciliation_hint(
            operation_id="op_001", expected_target="pi_test_001",
            expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.RETRIEVE_CURRENT_PROVIDER_STATE)
        self.assertEqual(hint.refund_id, "re_test_001")
        self.assertIn("only-a-reconciliation-signal", hint.reason)

    def test_target_accepts_either_charge_or_payment_intent_when_both_present(self):
        self.send()
        hint = self.inbox.reconciliation_hint(
            operation_id="op_001", expected_target="ch_test_001",
            expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.RETRIEVE_CURRENT_PROVIDER_STATE)

    def test_duplicate_delivery_is_idempotently_deduplicated(self):
        raw = event_body()
        self.assertEqual(self.send(raw).action, InboxAction.INGESTED)
        # A delivery retry may receive a fresh valid signature timestamp, but body/event are the same.
        self.assertEqual(self.send(raw, timestamp=TS + 1,
                                   header=_sign(raw, timestamp=TS + 1),
                                   now=NOW + timedelta(seconds=1)).action, InboxAction.DUPLICATE)

    def test_multiple_v1_signatures_and_old_secret_rotation_are_supported(self):
        raw = event_body()
        header = _sign(raw, secret=OLD_SECRET) + "," + _sign(raw).split(",", 1)[1]
        inbox = self.make_inbox(secrets={"current": SECRET, "previous": OLD_SECRET})
        result = inbox.ingest(raw, header, now=NOW)
        self.assertEqual(result.action, InboxAction.INGESTED)
        self.assertIn(inbox.get(result.event_id)["signing_secret_label"], {"current", "previous"})

    def test_signature_mismatch_does_not_write_event(self):
        raw = event_body()
        result = self.send(raw, header="t=" + str(TS) + ",v1=" + "0" * 64)
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertIsNone(self.inbox.get("evt_test_001"))

    def test_one_byte_body_mutation_invalidates_signature(self):
        raw = event_body()
        header = _sign(raw)
        changed = raw.replace(b"2500", b"2501", 1)
        result = self.send(changed, header=header)
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertEqual(result.reason, "signature-mismatch")

    def test_expired_and_future_signatures_rejected(self):
        raw = event_body()
        expired = self.send(raw, timestamp=TS - 301, now=NOW)
        future = self.send(raw, timestamp=TS + 301, now=NOW)
        self.assertEqual(expired.reason, "signature-timestamp-outside-tolerance")
        self.assertEqual(future.reason, "signature-timestamp-outside-tolerance")

    def test_timestamp_tolerance_boundary_is_inclusive(self):
        raw = event_body()
        ok = self.send(raw, timestamp=TS + 300, now=NOW)
        self.assertEqual(ok.action, InboxAction.INGESTED)

    def test_duplicate_timestamp_signature_header_is_rejected(self):
        raw = event_body()
        sig = _sign(raw)
        result = self.send(raw, header=sig + ",t=" + str(TS))
        self.assertEqual(result.reason, "signature-timestamp-invalid")

    def test_missing_v1_signature_is_rejected(self):
        result = self.send(header=f"t={TS},v0={'a'*64}")
        self.assertEqual(result.reason, "signature-v1-missing")

    def test_oversized_body_is_rejected_before_storage(self):
        raw = b"{" + b" " * MAX_WEBHOOK_BODY_BYTES + b"}"
        result = self.send(raw, header="t=" + str(TS) + ",v1=" + "0" * 64)
        self.assertEqual(result.reason, "payload-too-large")
        with sqlite3.connect(self.path) as db:
            count = db.execute("select count(*) from stripe_webhook_inbox").fetchone()[0]
        self.assertEqual(count, 0)

    def test_empty_body_is_rejected(self):
        result = self.send(b"")
        self.assertEqual(result.reason, "raw-body-required")

    def test_invalid_utf8_is_rejected(self):
        raw = b"\xff"
        self.assertEqual(self.send(raw).reason, "payload-not-valid-utf8")

    def test_invalid_json_is_rejected(self):
        raw = b"{invalid"
        self.assertEqual(self.send(raw).reason, "payload-json-invalid")

    def test_duplicate_json_keys_are_rejected(self):
        raw = b'{"id":"evt_test_001","id":"evt_test_002"}'
        self.assertEqual(self.send(raw).reason, "payload-contains-duplicate-json-key")

    def test_nonstandard_nan_is_rejected(self):
        raw = b'{"foo":NaN}'
        self.assertEqual(self.send(raw).reason, "payload-contains-nonstandard-number")

    def test_non_object_root_rejected(self):
        raw = b"[]"
        self.assertEqual(self.send(raw).reason, "payload-root-must-be-object")

    def test_unknown_event_type_rejected(self):
        raw = event_body(event_type="payment_intent.succeeded")
        self.assertEqual(self.send(raw).reason, "event-type-not-allowed")

    def test_non_string_event_type_rejected_without_exception(self):
        raw = event_body(event_type=[])  # malformed but correctly signed
        result = self.send(raw)
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertEqual(result.reason, "event-type-not-allowed")

    def test_live_mode_event_rejected(self):
        raw = event_body(extras={"livemode": True})
        self.assertEqual(self.send(raw).reason, "event-not-explicitly-test-mode")

    def test_live_mode_refund_object_rejected(self):
        raw = event_body(livemode=True)
        self.assertEqual(self.send(raw).reason, "refund-not-explicitly-test-mode")

    def test_wrong_connected_account_rejected(self):
        inbox = self.make_inbox(expected_account="acct_expected")
        raw = event_body(account="acct_other")
        result = inbox.ingest(raw, _sign(raw), now=NOW)
        self.assertEqual(result.reason, "event-connected-account-mismatch")

    def test_connect_event_rejected_on_platform_inbox(self):
        raw = event_body(account="acct_connected")
        self.assertEqual(self.send(raw).reason, "connected-account-event-not-allowed-on-platform-inbox")

    def test_expected_connect_account_accepts_correct_event(self):
        inbox = self.make_inbox(expected_account="acct_connected")
        raw = event_body(account="acct_connected")
        result = inbox.ingest(raw, _sign(raw), now=NOW)
        self.assertEqual(result.action, InboxAction.INGESTED)

    def test_failed_event_type_must_match_failed_refund_state(self):
        raw = event_body(event_type="refund.failed", status="succeeded")
        result = self.send(raw)
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertEqual(result.reason, "refund-failed-event-status-mismatch")

    def test_database_reopened_under_wrong_connected_account_cannot_route_event(self):
        first = self.make_inbox(expected_account="acct_original")
        raw = event_body(account="acct_original")
        self.assertEqual(first.ingest(raw, _sign(raw), now=NOW).action, InboxAction.INGESTED)
        wrong_config = self.make_inbox(expected_account="acct_other")
        hint = wrong_config.reconciliation_hint(
            operation_id="op_001", expected_target="ch_test_001",
            expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.MANUAL_RECONCILIATION)
        self.assertIn("account-scope", hint.reason)

    def test_wrong_refund_object_rejected(self):
        body = json.loads(event_body())
        body["data"]["object"]["object"] = "charge"
        raw = json.dumps(body, separators=(",", ":")).encode()
        self.assertEqual(self.send(raw).reason, "event-data-object-not-refund")

    def test_missing_target_rejected(self):
        body = json.loads(event_body())
        body["data"]["object"]["charge"] = None
        body["data"]["object"]["payment_intent"] = None
        raw = json.dumps(body, separators=(",", ":")).encode()
        self.assertEqual(self.send(raw).reason, "refund-target-missing")

    def test_boolean_amount_rejected(self):
        raw = event_body(amount=True)
        self.assertEqual(self.send(raw).reason, "refund-amount-invalid")

    def test_currency_mismatch_goes_to_manual_reconciliation(self):
        self.send(event_body(currency="eur"))
        hint = self.inbox.reconciliation_hint(operation_id="op_001", expected_target="ch_test_001",
                                              expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.MANUAL_RECONCILIATION)

    def test_amount_mismatch_goes_to_manual_reconciliation(self):
        self.send(event_body(amount=2501))
        hint = self.inbox.reconciliation_hint(operation_id="op_001", expected_target="ch_test_001",
                                              expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.MANUAL_RECONCILIATION)

    def test_different_refund_ids_for_one_operation_force_manual_reconciliation(self):
        self.send(event_body(event_id="evt_one", refund_id="re_one"))
        self.send(event_body(event_id="evt_two", refund_id="re_two"))
        hint = self.inbox.reconciliation_hint(operation_id="op_001", expected_target="ch_test_001",
                                              expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.MANUAL_RECONCILIATION)
        self.assertIn("multiple-refund-ids", hint.reason)

    def test_unrelated_valid_event_is_stored_but_does_not_correlate(self):
        self.send(event_body(operation_id="other_op"))
        hint = self.inbox.reconciliation_hint(operation_id="op_001", expected_target="ch_test_001",
                                              expected_amount=2500, expected_currency="usd")
        self.assertEqual(hint.action, InboxAction.NO_CORRELATED_EVENT)

    def test_raw_body_and_sensitive_provider_fields_are_not_persisted(self):
        raw = event_body()
        self.send(raw)
        with sqlite3.connect(self.path) as db:
            dump = " ".join(str(row) for row in db.execute("select * from stripe_webhook_inbox").fetchall())
        for secret in ("secret_do_not_store", "PRIVATE DESCRIPTION", "DO_NOT_PERSIST", "receipt_url", "previous_attributes"):
            self.assertNotIn(secret, dump)
        self.assertNotIn(raw.decode(), dump)

    def test_stored_row_tampering_is_detected(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("update stripe_webhook_inbox set refund_status='pending' where event_id='evt_test_001'")
        with self.assertRaises(InboxIntegrityError):
            self.inbox.get("evt_test_001")

    def test_duplicate_event_id_with_different_valid_payload_is_rejected(self):
        self.send(event_body())
        other = event_body(event_id="evt_test_001", refund_id="re_different")
        result = self.send(other)
        self.assertEqual(result.action, InboxAction.REJECTED)
        self.assertEqual(result.reason, "event-id-reused-with-different-payload")

    def test_secret_values_never_appear_in_result_diagnostics(self):
        raw = event_body()
        result = self.send(raw, header="t=" + str(TS) + ",v1=" + "0" * 64)
        self.assertNotIn(SECRET, result.reason)
        self.assertNotIn("DO_NOT_PERSIST", result.reason)

    def test_production_clock_override_is_disabled_by_default(self):
        inbox = self.make_inbox(allow_test_clock_override=False)
        with self.assertRaises(ValueError):
            inbox.ingest(event_body(), _sign(event_body()), now=NOW)

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            self.make_inbox(key=b"short")
        with self.assertRaises(ValueError):
            self.make_inbox(secrets={"bad label!": SECRET})
        with self.assertRaises(ValueError):
            self.make_inbox(tolerance=True)

    def test_concurrent_duplicate_event_ingestion_is_single_insert(self):
        raw = event_body()
        header = _sign(raw)
        barrier = threading.Barrier(3)
        results = []
        lock = threading.Lock()
        def call():
            barrier.wait()
            result = self.inbox.ingest(raw, header, now=NOW)
            with lock:
                results.append(result)
        t1 = threading.Thread(target=call)
        t2 = threading.Thread(target=call)
        t1.start(); t2.start(); barrier.wait(); t1.join(); t2.join()
        self.assertEqual(sorted(r.action.value for r in results), sorted([InboxAction.INGESTED.value, InboxAction.DUPLICATE.value]))
        with sqlite3.connect(self.path) as db:
            count = db.execute("select count(*) from stripe_webhook_inbox").fetchone()[0]
        self.assertEqual(count, 1)

    def test_read_path_checks_hmac_for_all_correlated_events(self):
        self.send()
        with sqlite3.connect(self.path) as db:
            db.execute("update stripe_webhook_inbox set amount=1 where event_id='evt_test_001'")
        with self.assertRaises(InboxIntegrityError):
            self.inbox.find_by_operation("op_001")

    def test_adversarial_json_type_mutation_matrix_never_raises(self):
        paths = [
            ("id",), ("object",), ("type",), ("created",), ("livemode",),
            ("account",), ("data",), ("data", "object"),
            ("data", "object", "id"), ("data", "object", "object"),
            ("data", "object", "amount"), ("data", "object", "currency"),
            ("data", "object", "status"), ("data", "object", "livemode"),
            ("data", "object", "metadata"),
        ]
        bad_values = [None, False, True, 0, -1, 1.5, "", [], {}, "not_an_id", float("nan"), float("inf")]
        case = 0
        for path in paths:
            for value in bad_values:
                with self.subTest(path=path, value=repr(value)):
                    body = json.loads(event_body(event_id=f"evt_fuzz_{case}"))
                    parent = body
                    for key in path[:-1]:
                        parent = parent.setdefault(key, {})
                    parent[path[-1]] = value
                    raw = json.dumps(body, separators=(",", ":"), allow_nan=True).encode("utf-8")
                    result = self.send(raw)
                    self.assertIn(result.action, set(InboxAction))
                    case += 1
        self.assertEqual(case, len(paths) * len(bad_values))

    def test_expected_target_currency_validation(self):
        with self.assertRaises(ValueError):
            self.inbox.reconciliation_hint(operation_id="op_001", expected_target="nope",
                                           expected_amount=2500, expected_currency="usd")
        with self.assertRaises(ValueError):
            self.inbox.reconciliation_hint(operation_id="op_001", expected_target="ch_test_001",
                                           expected_amount=True, expected_currency="usd")


if __name__ == "__main__":
    unittest.main(verbosity=2)
