from __future__ import annotations
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import stat
import sys
import tempfile
import threading
from contextlib import closing
import unittest

HERE = Path(__file__).resolve().parent
R19 = HERE.parent / "r19_integrity_key_rotation_v2_9"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(R19))

from external_checkpoint import (
    CheckpointError,
    DatabaseSnapshot,
    SQLiteReferenceAnchor,
    StateChangeApproval,
    capture_database_snapshot,
    publish_checkpoint,
    verify_database_against_anchor,
)
from operation_ledger import TrustedOperationLedger
from stripe_webhook_inbox import StripeWebhookInbox, InboxAction

INTEGRITY_KEY = b"v3-primary-integrity-test-key-32-bytes-minimum"
ANCHOR_KEY = b"v3-external-anchor-test-key-material-32-bytes"
OPERATOR_KEY = b"v3-checkpoint-operator-key-material-32-bytes"
WRONG_KEY = b"v3-untrusted-wrong-key-material-32-bytes"
ENDPOINT_SECRET = "whsec_v3_synthetic_only"
DATABASE_ID = "lycheetah.operations.main"
NOW = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)
OP = "op_v3_checkpoint_001"
EVENT = "evt_v3_checkpoint_001"
REFUND = "re_v3_checkpoint_001"
CHARGE = "ch_v3_checkpoint_001"
PI = "pi_v3_checkpoint_001"


def seed_database(path: Path) -> None:
    inbox = StripeWebhookInbox(
        path=str(path), integrity_key=INTEGRITY_KEY,
        endpoint_secrets={"test-secret": ENDPOINT_SECRET},
        timestamp_tolerance_seconds=300, allow_test_clock_override=True,
    )
    ledger = TrustedOperationLedger(path=str(path), integrity_key=INTEGRITY_KEY)
    ledger.register_operation(operation_id=OP, account_scope="platform", target_type="charge",
                              target_id=CHARGE, amount=1250, currency="usd", now=NOW)
    event = {
        "id": EVENT, "object": "event", "type": "refund.updated",
        "created": int(NOW.timestamp()) - 2, "livemode": False,
        "data": {"object": {
            "object": "refund", "id": REFUND, "charge": CHARGE,
            "payment_intent": PI, "amount": 1250, "currency": "usd",
            "status": "pending", "livemode": False,
            "metadata": {"lycheetah_operation_id": OP, "note": "DO_NOT_STORE"},
            "client_secret": "cs_test_MUST_NOT_BE_IN_CHECKPOINT",
        }},
    }
    raw = json.dumps(event, separators=(",", ":")).encode()
    ts = str(int(NOW.timestamp()))
    sig = hmac.new(ENDPOINT_SECRET.encode(), ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    result = inbox.ingest(raw, f"t={ts},v1={sig}", now=NOW)
    assert result.action == InboxAction.INGESTED, result
    ledger.record_provider_observation(
        operation_id=OP, event_id=EVENT,
        snapshot={"id": REFUND, "status": "pending", "charge": CHARGE,
                  "payment_intent": PI, "amount": 1250, "currency": "usd",
                  "livemode": False, "metadata_operation_id": OP,
                  "client_secret": "cs_test_SHOULD_NOT_PERSIST"}, now=NOW,
    )


class ExternalCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lyc-v3-checkpoint-")
        self.root = Path(self.temp.name)
        self.primary = self.root / "operations.sqlite"
        self.anchor_path = self.root / "anchor.sqlite"
        seed_database(self.primary)
        self.anchor = SQLiteReferenceAnchor(
            self.anchor_path, anchor_key=ANCHOR_KEY, anchor_key_id="anchor-v3-test",
            operator_key=OPERATOR_KEY, allow_test_clock_override=True,
        )

    def tearDown(self):
        self.temp.cleanup()

    def approval(self, *, approval_id="approval_v3_initial_001", nonce="nonce_v3_initial_000001",
                 reason="initial.trusted.snapshot", previous=None, snapshot=None,
                 issued=NOW, expires=None, operator_key=OPERATOR_KEY):
        snapshot = snapshot or capture_database_snapshot(self.primary, INTEGRITY_KEY)
        expires = expires or (issued + timedelta(minutes=15))
        return StateChangeApproval.issue(
            operator_key=operator_key, approval_id=approval_id, nonce=nonce,
            database_id=DATABASE_ID, previous_checkpoint_sha256=previous,
            proposed_logical_sha256=snapshot.logical_sha256, reason_code=reason,
            issued_at=issued.isoformat().replace("+00:00", "Z"),
            expires_at=expires.isoformat().replace("+00:00", "Z"),
        )

    def publish_initial(self):
        approval = self.approval()
        return publish_checkpoint(self.primary, database_id=DATABASE_ID,
                                  integrity_key=INTEGRITY_KEY, anchor=self.anchor,
                                  approval=approval, operator_key=OPERATOR_KEY, now=NOW)

    def test_startup_without_anchor_is_never_ready(self):
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "NO_ANCHOR")
        self.assertFalse(result["safe_to_continue"])

    def test_initial_checkpoint_and_startup_verification_match(self):
        record = self.publish_initial()
        self.assertEqual(record.sequence, 1)
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "MATCH")
        self.assertTrue(result["safe_to_continue"])

    def test_old_primary_snapshot_is_detected_against_latest_anchor(self):
        self.publish_initial()
        stale_snapshot = self.root / "stale.sqlite"
        with closing(sqlite3.connect(self.primary)) as src, closing(sqlite3.connect(stale_snapshot)) as dst:
            src.backup(dst)
        ledger = TrustedOperationLedger(path=str(self.primary), integrity_key=INTEGRITY_KEY)
        ledger.mark_manual(OP, "operator-reviewed-reconciliation", now=NOW + timedelta(seconds=2))
        new_snap = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        latest = self.anchor.history()[-1]
        approval = self.approval(approval_id="approval_v3_second_002", nonce="nonce_v3_second_000002",
                                 reason="operator-reviewed.reconciliation", previous=latest.record_sha256,
                                 snapshot=new_snap, issued=NOW + timedelta(seconds=3))
        published = publish_checkpoint(self.primary, database_id=DATABASE_ID,
                                       integrity_key=INTEGRITY_KEY, anchor=self.anchor,
                                       approval=approval, operator_key=OPERATOR_KEY,
                                       now=NOW + timedelta(seconds=3))
        self.assertEqual(published.sequence, 2)
        # All primary connections are closed before restoring the old logical snapshot.
        shutil.copyfile(stale_snapshot, self.primary)
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "STALE_SNAPSHOT")
        self.assertFalse(result["safe_to_continue"])
        self.assertTrue(result["matches_older_checkpoint"])

    def test_uncheckpointed_validly_signed_state_is_blocked(self):
        self.publish_initial()
        ledger = TrustedOperationLedger(path=str(self.primary), integrity_key=INTEGRITY_KEY)
        ledger.mark_manual(OP, "operator-reviewed-reconciliation", now=NOW + timedelta(seconds=5))
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "CHECKPOINT_MISMATCH")
        self.assertFalse(result["safe_to_continue"])

    def test_changed_schema_is_blocked(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("CREATE TABLE later_added_table (id INTEGER PRIMARY KEY, value TEXT)")
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "SCHEMA_CHANGED")

    def test_wrong_integrity_key_blocks_startup(self):
        self.publish_initial()
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=WRONG_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "PRIMARY_DATABASE_UNVERIFIED")
        self.assertFalse(result["safe_to_continue"])

    def test_modified_authenticated_row_blocks_startup(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("UPDATE lycheetah_refund_operation_ledger SET expected_amount=expected_amount+1 WHERE operation_id=?", (OP,))
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "PRIMARY_DATABASE_UNVERIFIED")

    def test_approval_bound_to_exact_snapshot(self):
        snapshot_a = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        approval = self.approval(snapshot=snapshot_a)
        ledger = TrustedOperationLedger(path=str(self.primary), integrity_key=INTEGRITY_KEY)
        ledger.mark_manual(OP, "operator-reviewed-reconciliation", now=NOW + timedelta(seconds=1))
        with self.assertRaisesRegex(CheckpointError, "snapshot-mismatch"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID,
                               integrity_key=INTEGRITY_KEY, anchor=self.anchor,
                               approval=approval, operator_key=OPERATOR_KEY, now=NOW + timedelta(seconds=1))
        self.assertEqual(self.anchor.history(), [])

    def test_approval_bound_to_database_identity(self):
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        bad = StateChangeApproval.issue(
            operator_key=OPERATOR_KEY, approval_id="approval_v3_wrong_db_001",
            nonce="nonce_v3_wrong_db_000001", database_id="lycheetah.operations.other",
            previous_checkpoint_sha256=None, proposed_logical_sha256=snapshot.logical_sha256,
            reason_code="initial.trusted.snapshot", issued_at=NOW.isoformat().replace("+00:00", "Z"),
            expires_at=(NOW + timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
        )
        with self.assertRaisesRegex(CheckpointError, "database-mismatch"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=bad, operator_key=OPERATOR_KEY, now=NOW)

    def test_expired_approval_is_rejected(self):
        approval = self.approval(issued=NOW - timedelta(minutes=20), expires=NOW - timedelta(seconds=1))
        with self.assertRaisesRegex(CheckpointError, "lifetime|expired|not-yet-valid"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=approval, operator_key=OPERATOR_KEY, now=NOW)

    def test_wrong_operator_key_is_rejected(self):
        approval = self.approval()
        with self.assertRaisesRegex(CheckpointError, "signature-invalid"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=approval, operator_key=WRONG_KEY, now=NOW)

    def test_read_only_anchor_verification_does_not_require_operator_key(self):
        self.publish_initial()
        readonly_anchor = SQLiteReferenceAnchor(self.anchor_path, anchor_key=ANCHOR_KEY,
                                                anchor_key_id="anchor-v3-test")
        self.assertEqual(verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                        integrity_key=INTEGRITY_KEY, anchor=readonly_anchor)["status"], "MATCH")

    def test_independent_keys_are_required(self):
        with self.assertRaisesRegex(CheckpointError, "independent"):
            SQLiteReferenceAnchor(self.root / "bad-anchor.sqlite", anchor_key=ANCHOR_KEY,
                                  operator_key=ANCHOR_KEY)

    def test_anchor_record_tampering_is_detected(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.anchor_path)) as db, db:
            db.execute("DROP TRIGGER anchor_records_no_update")
            db.execute("UPDATE anchor_records SET logical_sha256=? WHERE sequence=1", ("f" * 64,))
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "ANCHOR_UNVERIFIED")
        self.assertFalse(result["safe_to_continue"])

    def test_anchor_key_id_mutation_is_authenticated(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.anchor_path)) as db, db:
            db.execute("DROP TRIGGER anchor_records_no_update")
            db.execute("UPDATE anchor_records SET anchor_key_id='anchor-other' WHERE sequence=1")
        with self.assertRaisesRegex(CheckpointError, "key-id-mismatch"):
            self.anchor.history()

    def test_approval_use_index_tampering_is_detected(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.anchor_path)) as db, db:
            db.execute("DROP TRIGGER used_approvals_no_update")
            db.execute("UPDATE used_approvals SET nonce='nonce_tampered_000000' WHERE approval_id=?", ("approval_v3_initial_001",))
        with self.assertRaisesRegex(CheckpointError, "approval-use-index-inconsistent"):
            self.anchor.history()

    def test_anchor_database_id_switch_is_refused(self):
        self.publish_initial()
        other = self.approval(approval_id="approval_v3_other_db_001", nonce="nonce_v3_other_db_000001")
        with self.assertRaisesRegex(CheckpointError, "database-mismatch"):
            publish_checkpoint(self.primary, database_id="lycheetah.operations.other", integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=other, operator_key=OPERATOR_KEY, now=NOW)

    def test_approval_nonce_must_be_safe_and_long_enough(self):
        snap = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        with self.assertRaisesRegex(CheckpointError, "nonce"):
            StateChangeApproval.issue(operator_key=OPERATOR_KEY, approval_id="approval_v3_badnonce_001",
                                      nonce="tiny", database_id=DATABASE_ID, previous_checkpoint_sha256=None,
                                      proposed_logical_sha256=snap.logical_sha256, reason_code="initial.trusted.snapshot",
                                      issued_at=NOW.isoformat().replace("+00:00", "Z"),
                                      expires_at=(NOW + timedelta(minutes=3)).isoformat().replace("+00:00", "Z"))


    def test_anchor_file_permissions_are_owner_only(self):
        mode = stat.S_IMODE(self.anchor_path.stat().st_mode)
        self.assertEqual(mode, 0o600)

    def test_primary_key_cannot_be_reused_as_anchor_or_operator_key(self):
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        approval = self.approval(snapshot=snapshot)
        with self.assertRaisesRegex(CheckpointError, "operator-keys-must-be-independent"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=approval,
                               operator_key=INTEGRITY_KEY, now=NOW)
        same_key_anchor = SQLiteReferenceAnchor(self.root / "same-key-anchor.sqlite",
                                                anchor_key=INTEGRITY_KEY, anchor_key_id="anchor-same-key-v3",
                                                operator_key=OPERATOR_KEY, allow_test_clock_override=True)
        approval2 = self.approval(approval_id="approval_v3_samekey_001", nonce="nonce_v3_samekey_000001",
                                  snapshot=snapshot)
        with self.assertRaisesRegex(CheckpointError, "anchor-keys-must-be-independent"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=same_key_anchor, approval=approval2,
                               operator_key=OPERATOR_KEY, now=NOW)

    def test_anchor_history_is_append_only_through_api(self):
        self.publish_initial()
        with closing(sqlite3.connect(self.anchor_path)) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM anchor_records WHERE sequence=1")

    def test_logical_fingerprint_includes_non_lycheetah_table_data(self):
        snap0 = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY, secret TEXT)")
            db.execute("INSERT INTO unrelated(secret) VALUES('demo')")
        snap1 = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        self.assertNotEqual(snap0.schema_sha256, snap1.schema_sha256)
        self.assertNotEqual(snap0.logical_sha256, snap1.logical_sha256)

    def test_logical_digest_independent_of_row_insertion_order(self):
        # Canonical logical state sorts typed rows; physical insertion order is not state.
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("CREATE TABLE unordered (value TEXT NOT NULL)")
            db.executemany("INSERT INTO unordered(value) VALUES(?)", [("a",), ("b",), ("c",)])
        before = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("DELETE FROM unordered")
            db.executemany("INSERT INTO unordered(value) VALUES(?)", [("c",), ("a",), ("b",)])
        after = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        self.assertEqual(before.logical_sha256, after.logical_sha256)

    def test_used_approval_cannot_be_replayed_after_checkpoint(self):
        approval = self.approval()
        publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                           anchor=self.anchor, approval=approval, operator_key=OPERATOR_KEY, now=NOW)
        snap = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        with self.assertRaisesRegex(CheckpointError, "stale-parent|already-used"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=approval, operator_key=OPERATOR_KEY, now=NOW)

    def test_checkpoint_record_chain_is_monotonic(self):
        first = self.publish_initial()
        ledger = TrustedOperationLedger(path=str(self.primary), integrity_key=INTEGRITY_KEY)
        ledger.mark_manual(OP, "operator-reviewed-reconciliation", now=NOW + timedelta(seconds=1))
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        second_approval = self.approval(approval_id="approval_v3_second_chain_001", nonce="nonce_v3_second_chain_0001",
                                       reason="operator-reviewed.reconciliation", previous=first.record_sha256,
                                       snapshot=snapshot, issued=NOW + timedelta(seconds=2))
        second = publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                                    anchor=self.anchor, approval=second_approval, operator_key=OPERATOR_KEY,
                                    now=NOW + timedelta(seconds=2))
        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.previous_record_sha256, first.record_sha256)
        self.assertEqual(len(self.anchor.history()), 2)

    def test_concurrent_checkpoint_append_has_one_cas_winner(self):
        first = self.publish_initial()
        ledger = TrustedOperationLedger(path=str(self.primary), integrity_key=INTEGRITY_KEY)
        ledger.mark_manual(OP, "operator-reviewed-reconciliation", now=NOW + timedelta(seconds=1))
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        a1 = self.approval(approval_id="approval_v3_race_a_001", nonce="nonce_v3_race_a_000001",
                           reason="operator-reviewed.race", previous=first.record_sha256,
                           snapshot=snapshot, issued=NOW + timedelta(seconds=2))
        a2 = self.approval(approval_id="approval_v3_race_b_001", nonce="nonce_v3_race_b_000001",
                           reason="operator-reviewed.race", previous=first.record_sha256,
                           snapshot=snapshot, issued=NOW + timedelta(seconds=2))
        barrier = threading.Barrier(2)
        results = []
        lock = threading.Lock()
        def runner(approval):
            barrier.wait()
            try:
                rec = self.anchor.append_checkpoint(expected_sequence=1, expected_head_sha256=first.record_sha256,
                    database_id=DATABASE_ID, snapshot=snapshot, approval=approval,
                    operator_key=OPERATOR_KEY, now=NOW + timedelta(seconds=3))
                value = ("ok", rec.sequence)
            except CheckpointError as exc:
                value = ("refused", str(exc))
            with lock:
                results.append(value)
        threads = [threading.Thread(target=runner, args=(a,)) for a in (a1, a2)]
        for t in threads: t.start()
        for t in threads: t.join(10)
        self.assertTrue(all(not t.is_alive() for t in threads), "checkpoint append thread hung")
        self.assertEqual(sum(1 for kind, _ in results if kind == "ok"), 1, results)
        self.assertEqual(len(self.anchor.history()), 2)

    def test_untrusted_anchor_key_fails_closed(self):
        self.publish_initial()
        wrong_anchor = SQLiteReferenceAnchor(self.anchor_path, anchor_key=WRONG_KEY,
                                             anchor_key_id="anchor-v3-test")
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=wrong_anchor)
        self.assertEqual(result["status"], "ANCHOR_UNVERIFIED")


    def test_forged_snapshot_components_cannot_be_anchored(self):
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        forged = DatabaseSnapshot(
            schema_sha256=snapshot.schema_sha256,
            data_sha256="0" * 64,
            logical_sha256=snapshot.logical_sha256,
            row_counts=snapshot.row_counts,
            verified_table_counts=snapshot.verified_table_counts,
        )
        approval = self.approval(snapshot=snapshot)
        with self.assertRaisesRegex(CheckpointError, "components-inconsistent"):
            self.anchor.append_checkpoint(
                expected_sequence=0, expected_head_sha256=None, database_id=DATABASE_ID,
                snapshot=forged, approval=approval, operator_key=OPERATOR_KEY, now=NOW,
            )
        forged_counts = DatabaseSnapshot(
            schema_sha256=snapshot.schema_sha256,
            data_sha256=snapshot.data_sha256,
            logical_sha256=snapshot.logical_sha256,
            row_counts={**snapshot.row_counts, "fabricated_table": 999},
            verified_table_counts=snapshot.verified_table_counts,
        )
        with self.assertRaisesRegex(CheckpointError, "components-inconsistent"):
            self.anchor.append_checkpoint(
                expected_sequence=0, expected_head_sha256=None, database_id=DATABASE_ID,
                snapshot=forged_counts, approval=approval, operator_key=OPERATOR_KEY, now=NOW,
            )
        self.assertEqual(self.anchor.history(), [])

    def test_cli_publish_and_verify_keep_operator_key_out_of_argv_and_output(self):
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        approval = self.approval(snapshot=snapshot, issued=datetime.now(timezone.utc))
        approval_path = self.root / "approval.json"
        approval_path.write_text(json.dumps(approval.to_dict()), encoding="utf-8")
        env = os.environ.copy()
        env.update({
            "LYC_PRIMARY_INTEGRITY_KEY_B64": base64.b64encode(INTEGRITY_KEY).decode("ascii"),
            "LYC_EXTERNAL_ANCHOR_KEY_B64": base64.b64encode(ANCHOR_KEY).decode("ascii"),
            "LYC_CHECKPOINT_OPERATOR_KEY_B64": base64.b64encode(OPERATOR_KEY).decode("ascii"),
        })
        cli = HERE / "external_checkpoint_cli.py"
        base_args = [sys.executable, str(cli), "--database", str(self.primary),
                     "--database-id", DATABASE_ID, "--anchor-database", str(self.anchor_path),
                     "--anchor-key-id", "anchor-v3-cli"]
        publish = subprocess.run(base_args + ["--mode", "publish", "--approval-json", str(approval_path)],
                                 env=env, capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(publish.returncode, 0, publish.stderr)
        self.assertEqual(json.loads(publish.stdout)["status"], "CHECKPOINT_PUBLISHED")
        self.assertNotIn(base64.b64encode(ANCHOR_KEY).decode("ascii"), publish.stdout + publish.stderr)
        verify_env = env.copy()
        verify_env.pop("LYC_CHECKPOINT_OPERATOR_KEY_B64", None)
        verify = subprocess.run(base_args + ["--mode", "verify"], env=verify_env,
                                capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertEqual(json.loads(verify.stdout)["status"], "MATCH")

    def test_cli_refuses_missing_anchor_for_verify(self):
        env = os.environ.copy()
        env["LYC_PRIMARY_INTEGRITY_KEY_B64"] = base64.b64encode(INTEGRITY_KEY).decode("ascii")
        env["LYC_EXTERNAL_ANCHOR_KEY_B64"] = base64.b64encode(ANCHOR_KEY).decode("ascii")
        cli = HERE / "external_checkpoint_cli.py"
        result = subprocess.run([sys.executable, str(cli), "--mode", "verify",
                                 "--database", str(self.primary), "--database-id", DATABASE_ID],
                                env=env, capture_output=True, text=True, timeout=10, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["status"], "REFUSED")

    def test_state_approval_json_rejects_unknown_fields_and_bad_digest(self):
        approval = self.approval().to_dict()
        with self.assertRaisesRegex(CheckpointError, "fields-invalid"):
            StateChangeApproval.from_dict({**approval, "bypass": True})
        bad = dict(approval)
        bad["proposed_logical_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(CheckpointError, "digest-invalid"):
            StateChangeApproval.from_dict(bad)

    def test_schema_changes_require_new_state_approval_even_when_rows_authenticate(self):
        first = self.publish_initial()
        with closing(sqlite3.connect(self.primary)) as db, db:
            db.execute("CREATE TABLE schema_extension (key TEXT PRIMARY KEY, value TEXT)")
        result = verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                                                integrity_key=INTEGRITY_KEY, anchor=self.anchor)
        self.assertEqual(result["status"], "SCHEMA_CHANGED")
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        approval = self.approval(approval_id="approval_v3_schema_extension_001",
                                 nonce="nonce_v3_schema_extension_0001",
                                 reason="approved.schema.extension", previous=first.record_sha256,
                                 snapshot=snapshot, issued=NOW + timedelta(seconds=5))
        record = publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                                    anchor=self.anchor, approval=approval, operator_key=OPERATOR_KEY,
                                    now=NOW + timedelta(seconds=5))
        self.assertEqual(record.sequence, 2)
        self.assertEqual(verify_database_against_anchor(self.primary, database_id=DATABASE_ID,
                            integrity_key=INTEGRITY_KEY, anchor=self.anchor)["status"], "MATCH")

    def test_no_checkpoint_publish_when_anchor_head_was_changed(self):
        first = self.publish_initial()
        latest = self.anchor.history()[-1]
        snapshot = capture_database_snapshot(self.primary, INTEGRITY_KEY)
        stale_approval = self.approval(approval_id="approval_v3_stale_head_001", nonce="nonce_v3_stale_head_0001",
                                       previous=None, snapshot=snapshot)
        with self.assertRaisesRegex(CheckpointError, "stale-parent"):
            publish_checkpoint(self.primary, database_id=DATABASE_ID, integrity_key=INTEGRITY_KEY,
                               anchor=self.anchor, approval=stale_approval, operator_key=OPERATOR_KEY, now=NOW)


if __name__ == "__main__":
    unittest.main(verbosity=2)
