from __future__ import annotations

from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
from datetime import timedelta
import unittest
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import DOMAIN_RECORD, canonical, b64, make_snapshot, sha_json, utc_now, iso, verify_record
from checkpoint_witness_quorum import (
    CheckpointWitness, EquivocationError, SQLiteCASGuard, WitnessProtocolError,
    VERSION, DOMAIN_WITNESS, create_certificate, find_equivocation,
    quorum_threshold, verified_head, verify_certificate, verify_certificate_chain,
    new_freshness_challenge, verify_fresh_head_quorum, verify_current_chain,
)

DBID = "lycheetah.operations.main"
ANCHOR_KEY_ID = "primary.anchor.v1"


def make_record(anchor_private, *, sequence: int, parent_hash: str | None, variant: str = "main"):
    snap = make_snapshot(
        ("a" if variant == "main" else "d") * 64,
        ("b" if variant == "main" else "e") * 64,
        {"events": sequence, "operations": 1},
        {"signed": sequence},
    )
    body = {
        "sequence": sequence,
        "database_id": DBID,
        **snap,
        "approval_id": "approval_" + uuid.uuid4().hex,
        "approval_nonce": "nonce_" + uuid.uuid4().hex,
        "reason_code": "approved.state.change",
        "created_at": iso(utc_now()),
        "previous_record_sha256": parent_hash,
        "request_id": "req_" + uuid.uuid4().hex,
        "request_sha256": ("c" if variant == "main" else "f") * 64,
        "server_key_id": ANCHOR_KEY_ID,
    }
    rh = sha_json(body)
    sig = anchor_private.sign(DOMAIN_RECORD + canonical({"body": body, "record_sha256": rh, "server_key_id": ANCHOR_KEY_ID}))
    return {"body": body, "record_sha256": rh, "server_key_id": ANCHOR_KEY_ID, "signature_b64": b64(sig)}


def forge_vote_for_test(witness_id, private_key, record):
    """Models a compromised witness key double-signing; never used by production code."""
    head = verified_head(record, {ANCHOR_KEY_ID: forge_vote_for_test.anchor_public})
    body = {"version": VERSION, "witness_id": witness_id, **head.to_dict()}
    return {**body, "signature_b64": b64(private_key.sign(DOMAIN_WITNESS + canonical(body)))}


class CheckpointWitnessQuorumTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-witness-quorum-v32-")
        self.root = Path(self.tmp.name)
        self.anchor_private = Ed25519PrivateKey.generate()
        self.anchor_keys = {ANCHOR_KEY_ID: self.anchor_private.public_key()}
        forge_vote_for_test.anchor_public = self.anchor_private.public_key()
        self.witness_privates = {f"witness-{i}": Ed25519PrivateKey.generate() for i in range(1, 5)}
        self.witness_keys = {name: key.public_key() for name, key in self.witness_privates.items()}
        self.witnesses = {}
        for wid, key in self.witness_privates.items():
            guard = SQLiteCASGuard(self.root / f"{wid}-guard.sqlite")
            self.witnesses[wid] = CheckpointWitness(
                wid, key, self.root / f"{wid}-votes.sqlite", guard, self.anchor_keys
            )
        self.r1 = make_record(self.anchor_private, sequence=1, parent_hash=None)
        self.r2a = make_record(self.anchor_private, sequence=2, parent_hash=self.r1["record_sha256"], variant="main")
        self.r2b = make_record(self.anchor_private, sequence=2, parent_hash=self.r1["record_sha256"], variant="fork")

    def tearDown(self):
        self.tmp.cleanup()

    def bootstrap(self):
        return {wid: witness.attest(self.r1) for wid, witness in self.witnesses.items()}

    def attest_all(self, record):
        return {wid: witness.attest(record) for wid, witness in self.witnesses.items()}

    def test_primary_anchor_signature_is_required(self):
        bad = dict(self.r1)
        bad["signature_b64"] = b64(b"x" * 64)
        with self.assertRaises(WitnessProtocolError):
            self.witnesses["witness-1"].attest(bad)

    def test_guard_and_vote_ledger_must_not_share_sqlite_file(self):
        shared = self.root / "shared-guard-votes.sqlite"
        guard = SQLiteCASGuard(shared)
        with self.assertRaisesRegex(WitnessProtocolError, "independent-storage"):
            CheckpointWitness("witness-extra", Ed25519PrivateKey.generate(), shared, guard, self.anchor_keys)

    def test_first_checkpoint_must_be_genesis(self):
        not_genesis = make_record(self.anchor_private, sequence=2, parent_hash="a" * 64)
        with self.assertRaises(WitnessProtocolError):
            self.witnesses["witness-1"].attest(not_genesis)

    def test_first_vote_and_same_head_retry_are_idempotent(self):
        first = self.witnesses["witness-1"].attest(self.r1)
        retry = self.witnesses["witness-1"].attest(self.r1)
        self.assertEqual(first, retry)

    def test_witness_rejects_conflicting_head_at_same_sequence(self):
        self.witnesses["witness-1"].attest(self.r1)
        self.witnesses["witness-1"].attest(self.r2a)
        with self.assertRaises(EquivocationError):
            self.witnesses["witness-1"].attest(self.r2b)

    def test_witness_requires_next_linked_sequence(self):
        self.witnesses["witness-1"].attest(self.r1)
        gap = make_record(self.anchor_private, sequence=3, parent_hash=self.r1["record_sha256"])
        with self.assertRaises(WitnessProtocolError):
            self.witnesses["witness-1"].attest(gap)

    def test_three_of_four_votes_create_valid_quorum(self):
        self.bootstrap()
        votes = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2", "witness-3")]
        cert = create_certificate(self.r2a, votes, self.anchor_keys, self.witness_keys)
        head = verify_certificate(cert, self.anchor_keys, self.witness_keys)
        self.assertEqual(head.record_sha256, self.r2a["record_sha256"])
        self.assertEqual(cert["threshold"], 3)

    def test_certificate_chain_accepts_contiguous_quorum_history(self):
        votes1 = list(self.bootstrap().values())
        cert1 = create_certificate(self.r1, votes1, self.anchor_keys, self.witness_keys)
        votes2 = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2", "witness-3")]
        cert2 = create_certificate(self.r2a, votes2, self.anchor_keys, self.witness_keys)
        heads = verify_certificate_chain([cert1, cert2], self.anchor_keys, self.witness_keys)
        self.assertEqual([h.sequence for h in heads], [1, 2])

    def test_certificate_chain_rejects_skipped_sequence(self):
        votes1 = list(self.bootstrap().values())
        cert1 = create_certificate(self.r1, votes1, self.anchor_keys, self.witness_keys)
        r3 = make_record(self.anchor_private, sequence=3, parent_hash=self.r1["record_sha256"])
        forged_votes = [forge_vote_for_test(w, self.witness_privates[w], r3) for w in ("witness-1", "witness-2", "witness-3")]
        cert3 = create_certificate(r3, forged_votes, self.anchor_keys, self.witness_keys)
        with self.assertRaisesRegex(WitnessProtocolError, "sequence-gap"):
            verify_certificate_chain([cert1, cert3], self.anchor_keys, self.witness_keys)

    def test_nonce_fresh_quorum_matches_current_head(self):
        self.bootstrap()
        self.attest_all(self.r2a)
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        fresh = verify_fresh_head_quorum(reports, self.witness_keys, database_id=DBID, challenge_nonce=nonce)
        self.assertEqual(fresh.sequence, 2)
        self.assertEqual(fresh.record_sha256, self.r2a["record_sha256"])
        self.assertEqual(len(fresh.agreeing_witness_ids), 4)

    def test_replayed_freshness_report_fails_new_challenge(self):
        self.bootstrap()
        old_nonce = new_freshness_challenge()
        old_reports = [w.report_head(DBID, old_nonce) for w in self.witnesses.values()]
        new_nonce = new_freshness_challenge()
        with self.assertRaisesRegex(WitnessProtocolError, "challenge-mismatch"):
            verify_fresh_head_quorum(old_reports, self.witness_keys, database_id=DBID, challenge_nonce=new_nonce)

    def test_three_matching_fresh_heads_tolerate_one_dissenting_witness(self):
        self.bootstrap()
        for wid in ("witness-1", "witness-2", "witness-3"):
            self.witnesses[wid].attest(self.r2a)
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        fresh = verify_fresh_head_quorum(reports, self.witness_keys, database_id=DBID, challenge_nonce=nonce)
        self.assertEqual(fresh.sequence, 2)
        self.assertEqual(fresh.dissenting_witness_ids, ("witness-4",))

    def test_two_two_freshness_split_has_no_quorum(self):
        self.bootstrap()
        for wid in ("witness-1", "witness-2"):
            self.witnesses[wid].attest(self.r2a)
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        with self.assertRaisesRegex(WitnessProtocolError, "quorum-disagreement"):
            verify_fresh_head_quorum(reports, self.witness_keys, database_id=DBID, challenge_nonce=nonce)

    def test_duplicate_fresh_head_reports_are_rejected(self):
        self.bootstrap()
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        with self.assertRaisesRegex(WitnessProtocolError, "duplicate-fresh-head-witness"):
            verify_fresh_head_quorum(reports + [reports[0]], self.witness_keys,
                                     database_id=DBID, challenge_nonce=nonce)

    def test_stale_report_is_rejected_even_with_valid_signature(self):
        self.bootstrap()
        nonce = new_freshness_challenge()
        report = self.witnesses["witness-1"].report_head(DBID, nonce)
        report["issued_at"] = iso(utc_now() - timedelta(minutes=10))
        body = {k: v for k, v in report.items() if k != "signature_b64"}
        report["signature_b64"] = b64(self.witness_privates["witness-1"].sign(DOMAIN_WITNESS + canonical(body)))
        with self.assertRaisesRegex(WitnessProtocolError, "report-stale"):
            verify_fresh_head_quorum([report], self.witness_keys, database_id=DBID,
                                     challenge_nonce=nonce, max_clock_skew_seconds=30)

    def test_current_chain_rejects_previously_valid_but_stale_certificate(self):
        votes1 = list(self.bootstrap().values())
        cert1 = create_certificate(self.r1, votes1, self.anchor_keys, self.witness_keys)
        self.attest_all(self.r2a)
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        fresh = verify_fresh_head_quorum(reports, self.witness_keys, database_id=DBID, challenge_nonce=nonce)
        with self.assertRaisesRegex(WitnessProtocolError, "not-current"):
            verify_current_chain([cert1], fresh, self.anchor_keys, self.witness_keys)

    def test_current_chain_matches_live_fresh_head(self):
        votes1 = list(self.bootstrap().values())
        cert1 = create_certificate(self.r1, votes1, self.anchor_keys, self.witness_keys)
        votes2 = list(self.attest_all(self.r2a).values())
        cert2 = create_certificate(self.r2a, votes2, self.anchor_keys, self.witness_keys)
        nonce = new_freshness_challenge()
        reports = [w.report_head(DBID, nonce) for w in self.witnesses.values()]
        fresh = verify_fresh_head_quorum(reports, self.witness_keys, database_id=DBID, challenge_nonce=nonce)
        heads = verify_current_chain([cert1, cert2], fresh, self.anchor_keys, self.witness_keys)
        self.assertEqual(heads[-1].record_sha256, fresh.record_sha256)

    def test_two_votes_are_insufficient_for_four_witness_roster(self):
        self.bootstrap()
        votes = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2")]
        with self.assertRaisesRegex(WitnessProtocolError, "quorum-insufficient"):
            create_certificate(self.r2a, votes, self.anchor_keys, self.witness_keys)

    def test_duplicate_witness_vote_does_not_count_twice(self):
        self.bootstrap()
        vote = self.witnesses["witness-1"].attest(self.r2a)
        with self.assertRaisesRegex(WitnessProtocolError, "duplicate-witness-vote"):
            create_certificate(self.r2a, [vote, vote, vote], self.anchor_keys, self.witness_keys)

    def test_malformed_witness_registry_fails_closed(self):
        with self.assertRaisesRegex(WitnessProtocolError, "registry-invalid"):
            create_certificate(self.r1, [], self.anchor_keys, {"witness-1": object()})

    def test_untrusted_witness_key_is_rejected(self):
        self.bootstrap()
        trusted_votes = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2")]
        rogue_private = Ed25519PrivateKey.generate()
        rogue_vote = forge_vote_for_test("rogue-witness", rogue_private, self.r2a)
        with self.assertRaisesRegex(WitnessProtocolError, "untrusted"):
            create_certificate(self.r2a, trusted_votes + [rogue_vote], self.anchor_keys, self.witness_keys)

    def test_certificate_digest_mutation_is_rejected(self):
        self.bootstrap()
        votes = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2", "witness-3")]
        cert = create_certificate(self.r2a, votes, self.anchor_keys, self.witness_keys)
        cert["logical_sha256"] = "0" * 64
        with self.assertRaisesRegex(WitnessProtocolError, "head-mismatch|digest-invalid"):
            verify_certificate(cert, self.anchor_keys, self.witness_keys)

    def test_fault_budget_cannot_be_downgraded_in_certificate(self):
        self.bootstrap()
        votes = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2", "witness-3")]
        cert = create_certificate(self.r2a, votes, self.anchor_keys, self.witness_keys)
        with self.assertRaisesRegex(WitnessProtocolError, "policy-mismatch"):
            verify_certificate(cert, self.anchor_keys, self.witness_keys, expected_max_byzantine=0)

    def test_external_guard_surviving_local_ledger_restore_blocks_fork(self):
        witness = self.witnesses["witness-1"]
        witness.attest(self.r1)
        # Take a consistent SQLite backup before sequence 2.
        backup = self.root / "witness-backup.sqlite"
        with closing(sqlite3.connect(witness.local_ledger_path)) as src, closing(sqlite3.connect(backup)) as dst:
            src.backup(dst)
        witness.attest(self.r2a)
        # Simulate restoring only the witness's local vote database; external guard remains at r2a.
        with closing(sqlite3.connect(witness.local_ledger_path)) as dst, closing(sqlite3.connect(backup)) as src:
            src.backup(dst)
        with self.assertRaises(EquivocationError):
            witness.attest(self.r2b)

    def test_local_stored_vote_tampering_is_refused(self):
        witness = self.witnesses["witness-1"]
        witness.attest(self.r1)
        with closing(sqlite3.connect(witness.local_ledger_path)) as db:
            db.execute("UPDATE witness_votes SET vote_json=? WHERE database_id=? AND sequence=1", (json.dumps({"forged": True}), DBID))
            db.commit()
        with self.assertRaisesRegex(WitnessProtocolError, "stored-witness-vote-failed-authentication"):
            witness.attest(self.r1)

    def test_concurrent_conflicting_heads_only_one_guard_cas_wins(self):
        self.bootstrap()
        witness = self.witnesses["witness-1"]
        barrier = threading.Barrier(2)
        outcomes = []
        def run(record):
            try:
                barrier.wait(timeout=3)
                outcomes.append(("ok", witness.attest(record)["record_sha256"]))
            except WitnessProtocolError as exc:
                outcomes.append(("reject", str(exc)))
        a = threading.Thread(target=run, args=(self.r2a,))
        b = threading.Thread(target=run, args=(self.r2b,))
        a.start(); b.start(); a.join(timeout=5); b.join(timeout=5)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertEqual(sum(x[0] == "ok" for x in outcomes), 1)
        self.assertEqual(sum(x[0] == "reject" for x in outcomes), 1)

    def test_one_compromised_witness_cannot_make_a_conflicting_quorum(self):
        self.bootstrap()
        # Treat witness-1 as compromised; the three honest witnesses lock branch A.
        honest_a = [self.witnesses[w].attest(self.r2a) for w in ("witness-2", "witness-3", "witness-4")]
        cert_a = create_certificate(self.r2a, honest_a, self.anchor_keys, self.witness_keys)
        bad_vote_b = forge_vote_for_test("witness-1", self.witness_privates["witness-1"], self.r2b)
        # Every honest witness refuses to endorse the competing head after locking A.
        for wid in ("witness-2", "witness-3", "witness-4"):
            with self.assertRaises(EquivocationError):
                self.witnesses[wid].attest(self.r2b)
        with self.assertRaisesRegex(WitnessProtocolError, "quorum-insufficient"):
            create_certificate(self.r2b, [bad_vote_b], self.anchor_keys, self.witness_keys)
        self.assertEqual(verify_certificate(cert_a, self.anchor_keys, self.witness_keys).record_sha256, self.r2a["record_sha256"])

    def test_two_compromised_witnesses_create_detectable_fork_evidence(self):
        self.bootstrap()
        votes_a = [self.witnesses[w].attest(self.r2a) for w in ("witness-1", "witness-2", "witness-3")]
        cert_a = create_certificate(self.r2a, votes_a, self.anchor_keys, self.witness_keys)
        # The fourth honest witness has not voted at sequence 2 and can lock the alternate branch.
        vote_4b = self.witnesses["witness-4"].attest(self.r2b)
        vote_1b = forge_vote_for_test("witness-1", self.witness_privates["witness-1"], self.r2b)
        vote_2b = forge_vote_for_test("witness-2", self.witness_privates["witness-2"], self.r2b)
        cert_b = create_certificate(self.r2b, [vote_1b, vote_2b, vote_4b], self.anchor_keys, self.witness_keys)
        evidence = find_equivocation(cert_a, cert_b, self.anchor_keys, self.witness_keys)
        self.assertEqual([e["witness_id"] for e in evidence], ["witness-1", "witness-2"])

    def test_quorum_threshold_intersection_exceeds_fault_budget(self):
        for faults in range(0, 4):
            for count in range(3 * faults + 1, 13):
                threshold = quorum_threshold(count, faults)
                self.assertGreaterEqual(2 * threshold - count, faults + 1)
                self.assertLessEqual(2 * (threshold - 1) - count, faults)

    def test_quorum_threshold_enforces_fault_model(self):
        self.assertEqual(quorum_threshold(4, 1), 3)
        self.assertEqual(quorum_threshold(5, 1), 4)
        self.assertEqual(quorum_threshold(6, 1), 4)
        self.assertEqual(quorum_threshold(7, 2), 5)
        with self.assertRaisesRegex(WitnessProtocolError, "too-small"):
            quorum_threshold(3, 1)

    def test_witness_guard_tracks_each_database_identity_independently(self):
        other = make_record(self.anchor_private, sequence=1, parent_hash=None)
        # The primary record is signed but the witness's monotonic guard is already bound to DBID.
        first = self.witnesses["witness-1"].attest(self.r1)
        self.assertEqual(first["database_id"], DBID)
        # A record for another valid database identity cannot reuse the same branch's parent sequence
        other_body = dict(other["body"])
        other_body["database_id"] = "lycheetah.operations.other"
        other_hash = sha_json(other_body)
        other_sig = self.anchor_private.sign(DOMAIN_RECORD + canonical({"body": other_body, "record_sha256": other_hash, "server_key_id": ANCHOR_KEY_ID}))
        other = {"body": other_body, "record_sha256": other_hash, "server_key_id": ANCHOR_KEY_ID, "signature_b64": b64(other_sig)}
        vote = self.witnesses["witness-1"].attest(other)
        self.assertEqual(vote["database_id"], "lycheetah.operations.other")


if __name__ == "__main__":
    unittest.main(verbosity=2)
