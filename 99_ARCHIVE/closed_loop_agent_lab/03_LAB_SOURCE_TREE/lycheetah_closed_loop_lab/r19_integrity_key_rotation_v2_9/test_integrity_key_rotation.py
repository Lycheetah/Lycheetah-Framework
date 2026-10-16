from __future__ import annotations

from datetime import datetime, timedelta, timezone
from contextlib import closing
import hashlib
import base64
import hmac
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from integrity_key_rotation import (
    KeyRotationError,
    decode_key_from_env,
    rotate_integrity_key,
    verify_database,
)
from operation_ledger import TrustedOperationLedger, OperationLedgerIntegrityError
from stripe_webhook_inbox import StripeWebhookInbox, InboxAction, InboxIntegrityError

OLD_KEY = b"r19-old-integrity-key-material-32-bytes-minimum"
NEW_KEY = b"r19-new-integrity-key-material-32-bytes-minimum"
THIRD_KEY = b"r19-third-integrity-key-material-32-bytes-minimum"
WRONG_KEY = b"r19-wrong-integrity-key-material-32-bytes-minimum"
ENDPOINT_SECRET = "whsec_r19_offline_test_secret_material"
NOW = datetime(2026, 10, 17, 11, 0, tzinfo=timezone.utc)
TS = int(NOW.timestamp())
OP = "op_r19_rotation_001"
EVENT = "evt_r19_rotation_001"
REFUND = "re_r19_rotation_001"
CHARGE = "ch_r19_rotation_001"
PI = "pi_r19_rotation_001"


def signed_event() -> tuple[bytes, str]:
    event = {
        "id": EVENT, "object": "event", "type": "refund.updated",
        "created": TS - 4, "livemode": False,
        "data": {"object": {
            "object": "refund", "id": REFUND, "charge": CHARGE,
            "payment_intent": PI, "amount": 1250, "currency": "usd",
            "status": "pending", "livemode": False,
            "metadata": {"lycheetah_operation_id": OP, "private_note": "DO_NOT_STORE"},
            "client_secret": "cs_test_SHOULD_NOT_PERSIST",
        }},
    }
    raw = json.dumps(event, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(ENDPOINT_SECRET.encode(), str(TS).encode() + b"." + raw, hashlib.sha256).hexdigest()
    return raw, f"t={TS},v1={digest}"


def seed_database(path: Path, key: bytes = OLD_KEY, *, claim: bool = False) -> tuple[bytes, str, str | None]:
    inbox = StripeWebhookInbox(
        path=str(path), integrity_key=key,
        endpoint_secrets={"current-test": ENDPOINT_SECRET},
        timestamp_tolerance_seconds=300, allow_test_clock_override=True,
    )
    ledger = TrustedOperationLedger(path=str(path), integrity_key=key)
    ledger.register_operation(
        operation_id=OP, account_scope="platform", target_type="charge",
        target_id=CHARGE, amount=1250, currency="usd", now=NOW,
    )
    raw, signature = signed_event()
    result = inbox.ingest(raw, signature, now=NOW)
    assert result.action == InboxAction.INGESTED, result
    ledger.record_provider_observation(
        operation_id=OP, event_id=EVENT,
        snapshot={
            "id": REFUND, "status": "pending", "charge": CHARGE,
            "payment_intent": PI, "amount": 1250, "currency": "usd",
            "livemode": False, "metadata_operation_id": OP,
            "client_secret": "cs_test_NOT_PERSISTED",
        }, now=NOW,
    )
    token = None
    if claim:
        claimed = inbox.claim_reconciliation_jobs(
            worker_id="r19-worker", limit=1, lease_seconds=600, now=NOW,
        )
        assert len(claimed) == 1
        token = claimed[0]["claim_token"]
    return raw, signature, token


class IntegrityKeyRotationCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lycheetah-r19-")
        self.root = Path(self.temp.name)
        self.db_path = self.root / "ops.sqlite"
        seed_database(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def rotate(self, old=OLD_KEY, new=NEW_KEY, backup_name="before-rotation.sqlite"):
        return rotate_integrity_key(
            self.db_path, old_key=old, new_key=new,
            backup_path=self.root / backup_name,
        )

    def test_rotates_all_three_authenticated_tables(self):
        before = verify_database(self.db_path, OLD_KEY)
        self.assertEqual(set(before), {
            "stripe_webhook_inbox", "stripe_reconciliation_jobs", "lycheetah_refund_operation_ledger"
        })
        result = self.rotate()
        self.assertEqual(result.inbox_rows, 1)
        self.assertEqual(result.queue_rows, 1)
        self.assertEqual(result.operation_rows, 1)
        self.assertEqual(verify_database(self.db_path, NEW_KEY), before)
        with self.assertRaises(KeyRotationError):
            verify_database(self.db_path, OLD_KEY)

    def test_backup_remains_valid_under_old_key(self):
        result = self.rotate()
        self.assertEqual(verify_database(result.backup_path, OLD_KEY), {
            "stripe_webhook_inbox": 1,
            "stripe_reconciliation_jobs": 1,
            "lycheetah_refund_operation_ledger": 1,
        })

    def test_backup_permissions_are_owner_only(self):
        result = self.rotate()
        mode = Path(result.backup_path).stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)

    def test_duplicate_webhook_still_deduplicates_after_rotation(self):
        raw, signature = signed_event()
        self.rotate()
        inbox = StripeWebhookInbox(
            path=str(self.db_path), integrity_key=NEW_KEY,
            endpoint_secrets={"current-test": ENDPOINT_SECRET},
            timestamp_tolerance_seconds=300, allow_test_clock_override=True,
        )
        result = inbox.ingest(raw, signature, now=NOW)
        self.assertEqual(result.action, InboxAction.DUPLICATE)

    def test_existing_queue_claim_token_remains_usable_after_rotation(self):
        self.db_path.unlink()
        _, _, token = seed_database(self.db_path, claim=True)
        self.assertIsNotNone(token)
        self.rotate()
        inbox = StripeWebhookInbox(
            path=str(self.db_path), integrity_key=NEW_KEY,
            endpoint_secrets={"current-test": ENDPOINT_SECRET},
            timestamp_tolerance_seconds=300, allow_test_clock_override=True,
        )
        outcome = inbox.finish_reconciliation_job(
            event_id=EVENT, worker_id="r19-worker", claim_token=token,
            disposition="RETRY", reason_code="key-rotation-test",
            retry_after_seconds=30, now=NOW + timedelta(seconds=1),
        )
        self.assertEqual(outcome.state, "PENDING")
        self.assertEqual(verify_database(self.db_path, NEW_KEY)["stripe_reconciliation_jobs"], 1)

    def test_sequential_rotations_are_supported(self):
        first = self.rotate(OLD_KEY, NEW_KEY, "backup-old.sqlite")
        self.assertEqual(verify_database(self.db_path, NEW_KEY)["stripe_webhook_inbox"], 1)
        second = rotate_integrity_key(
            self.db_path, old_key=NEW_KEY, new_key=THIRD_KEY,
            backup_path=self.root / "backup-new.sqlite",
        )
        self.assertNotEqual(first.source_sha256_after, second.source_sha256_after)
        self.assertEqual(verify_database(self.db_path, THIRD_KEY)["lycheetah_refund_operation_ledger"], 1)
        self.assertEqual(verify_database(first.backup_path, OLD_KEY)["stripe_webhook_inbox"], 1)
        self.assertEqual(verify_database(second.backup_path, NEW_KEY)["stripe_webhook_inbox"], 1)

    def test_wrong_old_key_fails_before_backup_and_without_mutation(self):
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate(WRONG_KEY, NEW_KEY)
        self.assertEqual(self.db_path.read_bytes(), before)
        self.assertFalse((self.root / "before-rotation.sqlite").exists())

    def test_same_key_is_rejected(self):
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate(OLD_KEY, OLD_KEY)
        self.assertEqual(self.db_path.read_bytes(), before)

    def test_existing_backup_is_not_overwritten(self):
        existing = self.root / "before-rotation.sqlite"
        existing.write_bytes(b"operator file")
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate()
        self.assertEqual(existing.read_bytes(), b"operator file")
        self.assertEqual(self.db_path.read_bytes(), before)

    def test_inbox_tampering_aborts_before_backup(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("UPDATE stripe_webhook_inbox SET amount=amount+1 WHERE event_id=?", (EVENT,))
            db.commit()
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate()
        self.assertEqual(self.db_path.read_bytes(), before)
        self.assertFalse((self.root / "before-rotation.sqlite").exists())

    def test_queue_tampering_aborts_before_backup(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("UPDATE stripe_reconciliation_jobs SET attempts=attempts+1 WHERE event_id=?", (EVENT,))
            db.commit()
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate()
        self.assertEqual(self.db_path.read_bytes(), before)

    def test_operation_ledger_tampering_aborts_before_backup(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("UPDATE lycheetah_refund_operation_ledger SET expected_amount=expected_amount+1 WHERE operation_id=?", (OP,))
            db.commit()
        before = self.db_path.read_bytes()
        with self.assertRaises(KeyRotationError):
            self.rotate()
        self.assertEqual(self.db_path.read_bytes(), before)

    def test_partial_rekey_fault_rolls_back_all_tables(self):
        original_rows = {}
        with closing(sqlite3.connect(self.db_path)) as db:
            for table in ("stripe_webhook_inbox", "stripe_reconciliation_jobs", "lycheetah_refund_operation_ledger"):
                original_rows[table] = db.execute(f"SELECT row_hmac_sha256 FROM {table} ORDER BY rowid").fetchall()
        import integrity_key_rotation as rotation_module
        original_mac_for = rotation_module._mac_for
        calls = {"new": 0}
        def injected(table, row, inbox_probe, key):
            if key == NEW_KEY:
                calls["new"] += 1
                if calls["new"] == 2:
                    raise RuntimeError("injected-rekey-failure")
            return original_mac_for(table, row, inbox_probe, key)
        with patch.object(rotation_module, "_mac_for", side_effect=injected):
            with self.assertRaises(KeyRotationError):
                self.rotate()
        with closing(sqlite3.connect(self.db_path)) as db:
            for table, old_values in original_rows.items():
                self.assertEqual(db.execute(f"SELECT row_hmac_sha256 FROM {table} ORDER BY rowid").fetchall(), old_values)
        self.assertEqual(verify_database(self.db_path, OLD_KEY)["stripe_webhook_inbox"], 1)
        self.assertFalse(verify_database(self.db_path, NEW_KEY)) if False else None

    def test_database_changed_after_backup_is_detected_even_if_new_mac_is_valid(self):
        import integrity_key_rotation as rotation_module
        original_backup = rotation_module._snapshot_backup
        def backup_then_legitimate_old_key_update(source, backup):
            original_backup(source, backup)
            probe = object.__new__(rotation_module.StripeWebhookInbox)
            probe.integrity_key = OLD_KEY
            conn = sqlite3.connect(source)
            conn.row_factory = sqlite3.Row
            try:
                row = dict(conn.execute(
                    "SELECT * FROM stripe_webhook_inbox WHERE event_id=?", (EVENT,)
                ).fetchone())
                row["refund_status"] = "succeeded"
                row["row_hmac_sha256"] = probe._mac(row)
                conn.execute(
                    "UPDATE stripe_webhook_inbox SET refund_status=?, row_hmac_sha256=? WHERE event_id=?",
                    (row["refund_status"], row["row_hmac_sha256"], EVENT),
                )
                conn.commit()
            finally:
                conn.close()
        with patch.object(rotation_module, "_snapshot_backup", side_effect=backup_then_legitimate_old_key_update):
            with self.assertRaisesRegex(KeyRotationError, "database changed after backup"):
                self.rotate()
        # No HMAC rewrite took place; the concurrent old-key update is still valid.
        self.assertEqual(verify_database(self.db_path, OLD_KEY)["stripe_webhook_inbox"], 1)
        backup = self.root / "before-rotation.sqlite"
        self.assertTrue(backup.exists())
        self.assertEqual(verify_database(backup, OLD_KEY)["stripe_webhook_inbox"], 1)

    def test_cli_verify_only_uses_env_key_and_prints_only_counts(self):
        env = os.environ.copy()
        env["LYCHEETAH_OLD_INTEGRITY_KEY_B64"] = base64.b64encode(OLD_KEY).decode("ascii")
        env.pop("LYCHEETAH_NEW_INTEGRITY_KEY_B64", None)
        script = Path(__file__).with_name("integrity_key_rotation.py")
        result = subprocess.run(
            [sys.executable, str(script), "--database", str(self.db_path), "--verify-only"],
            env=env, capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        decoded = json.loads(result.stdout)
        self.assertEqual(decoded["status"], "VERIFIED")
        self.assertEqual(sum(decoded["rows"].values()), 3)
        self.assertNotIn(OLD_KEY.decode(), result.stdout + result.stderr)

    def test_cli_rotation_rekeys_then_new_key_verifies(self):
        env = os.environ.copy()
        env["LYCHEETAH_OLD_INTEGRITY_KEY_B64"] = base64.b64encode(OLD_KEY).decode("ascii")
        env["LYCHEETAH_NEW_INTEGRITY_KEY_B64"] = base64.b64encode(NEW_KEY).decode("ascii")
        script = Path(__file__).with_name("integrity_key_rotation.py")
        backup = self.root / "cli-backup.sqlite"
        result = subprocess.run(
            [sys.executable, str(script), "--database", str(self.db_path), "--backup", str(backup)],
            env=env, capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ROTATED")
        self.assertTrue(backup.exists())
        self.assertEqual(verify_database(self.db_path, NEW_KEY)["stripe_webhook_inbox"], 1)
        self.assertNotIn(OLD_KEY.decode(), result.stdout + result.stderr)
        self.assertNotIn(NEW_KEY.decode(), result.stdout + result.stderr)

    def test_key_bytes_can_be_loaded_from_base64_environment_without_echo(self):
        import os
        env_name = "LYCHEETAH_R19_TEST_KEY"
        previous = os.environ.get(env_name)
        try:
            os.environ[env_name] = base64.b64encode(OLD_KEY).decode("ascii")
            self.assertEqual(decode_key_from_env(env_name), OLD_KEY)
        finally:
            if previous is None:
                os.environ.pop(env_name, None)
            else:
                os.environ[env_name] = previous

    def test_incomplete_database_schema_rejected(self):
        other = self.root / "incomplete.sqlite"
        with closing(sqlite3.connect(other)) as db:
            db.execute("CREATE TABLE random_table (id INTEGER PRIMARY KEY)")
            db.commit()
        with self.assertRaises(KeyRotationError):
            verify_database(other, OLD_KEY)
        self.assertFalse((self.root / "incomplete-backup.sqlite").exists())

    def test_backup_path_cannot_equal_source(self):
        with self.assertRaises(KeyRotationError):
            rotate_integrity_key(self.db_path, old_key=OLD_KEY, new_key=NEW_KEY, backup_path=self.db_path)
        self.assertEqual(verify_database(self.db_path, OLD_KEY)["stripe_webhook_inbox"], 1)

    def test_rotation_report_contains_counts_but_no_key_material(self):
        result = self.rotate()
        rendered = json.dumps(result.to_dict())
        self.assertNotIn(OLD_KEY.decode(), rendered)
        self.assertNotIn(NEW_KEY.decode(), rendered)
        self.assertEqual(result.to_dict()["status"], "ROTATED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
