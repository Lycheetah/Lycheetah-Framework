from __future__ import annotations
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3
import shutil
import tempfile
import threading
import time
import unittest
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import DOMAIN_RECORD, canonical, b64, make_snapshot, sha_json, iso, utc_now
from checkpoint_witness_quorum import CheckpointWitness, SQLiteCASGuard, WitnessProtocolError, create_certificate, new_freshness_challenge
from durable_freshness_verifier import (
    ChallengeLifecycleError, DurableFreshnessVerifier, FreshnessChallenge,
)

DBID = "lycheetah.freshness.integration"
ANCHOR_ID = "primary.anchor.v1"
INTEGRITY_KEY = b"local-test-integrity-key-material-32bytes+"


def make_record(anchor_private):
    snap = make_snapshot("a" * 64, "b" * 64, {"events": 1}, {"signed": 1})
    body = {
        "sequence": 1, "database_id": DBID, **snap,
        "approval_id": "approval_" + uuid.uuid4().hex,
        "approval_nonce": "nonce_" + uuid.uuid4().hex,
        "reason_code": "approved.freshness.test",
        "created_at": iso(utc_now()), "previous_record_sha256": None,
        "request_id": "req_" + uuid.uuid4().hex,
        "request_sha256": "c" * 64, "server_key_id": ANCHOR_ID,
    }
    digest = sha_json(body)
    sig = anchor_private.sign(DOMAIN_RECORD + canonical({"body": body, "record_sha256": digest, "server_key_id": ANCHOR_ID}))
    return {"body": body, "record_sha256": digest, "server_key_id": ANCHOR_ID, "signature_b64": b64(sig)}


class DurableFreshnessVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-durable-challenge-")
        self.root = Path(self.tmp.name)
        self.anchor_private = Ed25519PrivateKey.generate()
        self.anchor_keys = {ANCHOR_ID: self.anchor_private.public_key()}
        self.private = {f"witness-{i}": Ed25519PrivateKey.generate() for i in range(1, 5)}
        self.public = {wid: key.public_key() for wid, key in self.private.items()}
        self.record = make_record(self.anchor_private)
        self.witnesses = {
            wid: CheckpointWitness(
                wid, key, self.root / f"{wid}-votes.sqlite",
                SQLiteCASGuard(self.root / f"{wid}-guard.sqlite"), self.anchor_keys,
            ) for wid, key in self.private.items()
        }
        votes = [w.attest(self.record) for w in self.witnesses.values()]
        self.certificate = create_certificate(self.record, votes, self.anchor_keys, self.public)
        self.ledger = self.root / "challenge-ledger.sqlite"
        self.verifier = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def issue_and_reports(self, verifier=None):
        verifier = verifier or self.verifier
        challenge = verifier.issue(DBID)
        reports = [w.report_head(DBID, challenge.nonce) for w in self.witnesses.values()]
        return challenge, reports

    def test_valid_current_chain_is_returned_and_challenge_consumed(self):
        challenge, reports = self.issue_and_reports()
        heads = self.verifier.verify_and_consume([self.certificate], reports, challenge)
        self.assertEqual(heads[-1].record_sha256, self.record["record_sha256"])
        with self.assertRaisesRegex(ChallengeLifecycleError, "already-consumed"):
            self.verifier.verify_and_consume([self.certificate], reports, challenge)

    def test_consumption_survives_verifier_process_restart(self):
        challenge, reports = self.issue_and_reports()
        self.verifier.verify_and_consume([self.certificate], reports, challenge)
        restarted = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY,
        )
        with self.assertRaisesRegex(ChallengeLifecycleError, "already-consumed"):
            restarted.verify_and_consume([self.certificate], reports, challenge)

    def test_many_concurrent_verifiers_only_one_consumes_challenge(self):
        challenge, reports = self.issue_and_reports()
        competitor_count = 8
        barrier = threading.Barrier(competitor_count)
        lock = threading.Lock()
        outcomes = []
        def worker():
            local = DurableFreshnessVerifier(
                self.ledger, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY,
            )
            barrier.wait(timeout=5)
            try:
                local.verify_and_consume([self.certificate], reports, challenge)
                value = "accepted"
            except ChallengeLifecycleError as exc:
                value = "rejected:" + str(exc)
            except Exception as exc:  # surfaced as a test failure below
                value = "unexpected:" + type(exc).__name__ + ":" + str(exc)
            with lock:
                outcomes.append(value)
        threads = [threading.Thread(target=worker) for _ in range(competitor_count)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=10)
        self.assertTrue(all(not t.is_alive() for t in threads), "concurrent verifier deadlocked")
        self.assertEqual(outcomes.count("accepted"), 1, outcomes)
        self.assertEqual(sum(v.startswith("rejected:") for v in outcomes), competitor_count - 1, outcomes)
        self.assertFalse(any(v.startswith("unexpected:") for v in outcomes), outcomes)

    def test_wrong_database_envelope_does_not_consume_real_challenge(self):
        challenge, reports = self.issue_and_reports()
        spoofed = replace(challenge, database_id="lycheetah.other.database")
        with self.assertRaisesRegex(ChallengeLifecycleError, "database-mismatch"):
            self.verifier.verify_and_consume([self.certificate], reports, spoofed)
        self.verifier.verify_and_consume([self.certificate], reports, challenge)

    def test_forged_unissued_nonce_is_rejected(self):
        fake = FreshnessChallenge(DBID, new_freshness_challenge(), int(time.time() * 1000), int(time.time() * 1000) + 10000)
        with self.assertRaisesRegex(ChallengeLifecycleError, "not-issued"):
            self.verifier.verify_and_consume([self.certificate], [], fake)

    def test_expired_challenge_is_rejected_before_report_validation(self):
        base = time.time_ns() // 1_000_000
        current = {"value": base}
        verifier = DurableFreshnessVerifier(
            self.root / "expiry.sqlite", self.anchor_keys, self.public,
            integrity_key=INTEGRITY_KEY, challenge_ttl_seconds=1,
            clock_ms=lambda: current["value"],
        )
        challenge = verifier.issue(DBID)
        current["value"] += 1000
        with self.assertRaisesRegex(ChallengeLifecycleError, "expired"):
            verifier.verify_and_consume([self.certificate], [], challenge)

    def test_expiry_rechecked_after_chain_validation_before_consumption(self):
        base = time.time_ns() // 1_000_000
        calls = {"n": 0}
        def clock():
            calls["n"] += 1
            # call 1 issues; call 2 pre-verifies; call 3 consumes, after expiry
            return base if calls["n"] == 1 else (base + 500 if calls["n"] == 2 else base + 1001)
        verifier = DurableFreshnessVerifier(
            self.root / "late-expiry.sqlite", self.anchor_keys, self.public,
            integrity_key=INTEGRITY_KEY, challenge_ttl_seconds=1, clock_ms=clock,
        )
        challenge = verifier.issue(DBID)
        reports = [w.report_head(DBID, challenge.nonce) for w in self.witnesses.values()]
        with self.assertRaisesRegex(ChallengeLifecycleError, "expired"):
            verifier.verify_and_consume([self.certificate], reports, challenge)

    def test_bad_signed_reports_do_not_consume_challenge(self):
        challenge, reports = self.issue_and_reports()
        reports = [dict(r) for r in reports]
        reports[0]["signature_b64"] = "A" * 88
        with self.assertRaises(Exception):
            self.verifier.verify_and_consume([self.certificate], reports, challenge)
        valid_reports = [w.report_head(DBID, challenge.nonce) for w in self.witnesses.values()]
        self.verifier.verify_and_consume([self.certificate], valid_reports, challenge)

    def test_pending_challenge_is_invalidated_when_trusted_roster_changes(self):
        challenge = self.verifier.issue(DBID)
        changed_privates = {f"new-witness-{i}": Ed25519PrivateKey.generate() for i in range(1, 5)}
        changed_public = {wid: key.public_key() for wid, key in changed_privates.items()}
        restarted = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, changed_public, integrity_key=INTEGRITY_KEY,
        )
        with self.assertRaisesRegex(ChallengeLifecycleError, "policy-changed"):
            restarted._load_pending(challenge.nonce, database_id=DBID)

    def test_pending_challenge_is_invalidated_when_fault_budget_changes(self):
        challenge = self.verifier.issue(DBID)
        restarted = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, self.public,
            integrity_key=INTEGRITY_KEY, max_byzantine=0,
        )
        with self.assertRaisesRegex(ChallengeLifecycleError, "policy-changed"):
            restarted._load_pending(challenge.nonce, database_id=DBID)

    def test_wrong_integrity_key_detects_ledger_rows(self):
        challenge = self.verifier.issue(DBID)
        restarted = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, self.public,
            integrity_key=b"different-key-material-that-is-also-32-bytes!",
        )
        with self.assertRaisesRegex(ChallengeLifecycleError, "integrity-invalid"):
            restarted._load_pending(challenge.nonce, database_id=DBID)

    def test_direct_sqlite_state_tampering_is_detected(self):
        challenge = self.verifier.issue(DBID)
        with closing(sqlite3.connect(self.ledger)) as db:
            db.execute("UPDATE freshness_challenges SET state='CONSUMED',consumed_at_ms=? WHERE nonce=?", (int(time.time() * 1000), challenge.nonce))
            db.commit()
        with self.assertRaisesRegex(ChallengeLifecycleError, "integrity-invalid"):
            self.verifier._load_pending(challenge.nonce, database_id=DBID)

    def test_caller_cannot_replace_stored_expiry_with_envelope_value(self):
        challenge = self.verifier.issue(DBID)
        spoofed = replace(challenge, expires_at_ms=challenge.expires_at_ms + 10_000_000)
        # Envelope fields beyond nonce and database ID are output/display only.
        self.assertEqual(self.verifier._load_pending(spoofed.nonce, database_id=DBID)["expires_at_ms"], challenge.expires_at_ms)

    def test_nonce_collision_is_bounded(self):
        nonce = new_freshness_challenge()
        verifier = DurableFreshnessVerifier(
            self.root / "nonce-collision.sqlite", self.anchor_keys, self.public,
            integrity_key=INTEGRITY_KEY, nonce_factory=lambda: nonce,
        )
        verifier.issue(DBID)
        with self.assertRaisesRegex(ChallengeLifecycleError, "collision-retry-exhausted"):
            verifier.issue(DBID)

    def test_known_limit_restoring_preconsume_snapshot_allows_replay(self):
        """Negative control: local HMAC + SQLite do not prevent whole-store rollback.

        This test intentionally proves a residual weakness. It should remain visible
        so later summaries do not confuse durable local state with anti-rollback state.
        """
        challenge, reports = self.issue_and_reports()
        snapshot = self.root / "pre-consumption-snapshot.sqlite"
        with closing(sqlite3.connect(self.ledger)) as source, closing(sqlite3.connect(snapshot)) as target:
            source.backup(target)

        self.verifier.verify_and_consume([self.certificate], reports, challenge)
        # Restore a coherent prior database snapshot, as a privileged backup/restore
        # operator or attacker able to roll back the host can do. The original HMAC key
        # remains valid, so local row authentication cannot detect temporal rollback.
        for suffix in ("-wal", "-shm"):
            Path(str(self.ledger) + suffix).unlink(missing_ok=True)
        shutil.copy2(snapshot, self.ledger)
        restored = DurableFreshnessVerifier(
            self.ledger, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY,
        )
        # This succeeds by design as a documented negative control, proving production
        # use needs an independently administered non-rollbackable spent-nonce store.
        heads = restored.verify_and_consume([self.certificate], reports, challenge)
        self.assertEqual(heads[-1].record_sha256, self.record["record_sha256"])

    def test_incompatible_preexisting_ledger_schema_is_rejected_explicitly(self):
        path = self.root / "legacy-ledger.sqlite"
        with closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE freshness_challenges (nonce TEXT PRIMARY KEY, database_id TEXT NOT NULL, issued_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL, max_byzantine INTEGER NOT NULL, max_clock_skew_seconds INTEGER NOT NULL, state TEXT NOT NULL, consumed_at_ms INTEGER, row_hmac TEXT NOT NULL)")
            db.commit()
        with self.assertRaisesRegex(ChallengeLifecycleError, "schema-incompatible"):
            DurableFreshnessVerifier(path, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY)

    def test_same_named_schema_without_nonce_primary_key_is_rejected(self):
        path = self.root / "no-primary-key-ledger.sqlite"
        with closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE freshness_challenges (nonce TEXT, database_id TEXT NOT NULL, issued_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL, max_byzantine INTEGER NOT NULL, max_clock_skew_seconds INTEGER NOT NULL, policy_sha256 TEXT NOT NULL, state TEXT NOT NULL, consumed_at_ms INTEGER, row_hmac TEXT NOT NULL)")
            db.commit()
        with self.assertRaisesRegex(ChallengeLifecycleError, "schema-incompatible"):
            DurableFreshnessVerifier(path, self.anchor_keys, self.public, integrity_key=INTEGRITY_KEY)

    def test_verifier_rejects_roster_too_small_for_fault_budget(self):
        three_keys = dict(list(self.public.items())[:3])
        with self.assertRaisesRegex(WitnessProtocolError, "roster-too-small"):
            DurableFreshnessVerifier(
                self.root / "undersized-roster.sqlite", self.anchor_keys, three_keys,
                integrity_key=INTEGRITY_KEY, max_byzantine=1,
            )

    def test_too_short_integrity_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at-least-32-bytes"):
            DurableFreshnessVerifier(self.root / "bad-key.sqlite", self.anchor_keys, self.public, integrity_key=b"short")


if __name__ == "__main__":
    unittest.main(verbosity=2)
