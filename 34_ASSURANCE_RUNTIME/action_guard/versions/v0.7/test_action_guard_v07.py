import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from action_guard_v07 import PersistentActionGuard, FakeMergeProvider

class GuardV07Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "ledger.sqlite3"
        self.g = PersistentActionGuard(self.db)
        self.provider = FakeMergeProvider()
        self.provider.seed_pr("Lycheetah/demo", 17, "head-A", "base-A")
        self.action = self.provider.read_action("Lycheetah/demo", 17)
        self.scope = "merge:Lycheetah/demo#17"
        self.actor = "lycheetah-coding-agent"
        self.approver = "human-mac"
        self.assertTrue(self.g.issue_approval("ap-1", self.actor, self.approver, self.action, self.scope, 100, 200).allowed)

    def tearDown(self):
        self.tmp.cleanup()

    def prepare(self, eid="fx-1", action=None):
        result = self.g.prepare_effect(eid, "ap-1", self.actor, action or self.action, self.scope, 120)
        if result.allowed:
            # In production this checkpoint must be copied into an independent trusted store.
            self.latest_anchor = self.g.audit_anchor()
        return result

    def claim(self, eid="fx-1", now=130):
        return self.g.claim_dispatch(eid, now, self.provider.read_action("Lycheetah/demo", 17),
                                     getattr(self, "latest_anchor", None))

    def test_normal_dispatch_persists_success(self):
        self.assertTrue(self.prepare().allowed)
        claim = self.claim()
        self.assertTrue(claim.allowed)
        result = self.provider.merge(claim.action, "fx-1")
        self.assertEqual(result["status"], "success")
        recorded = self.g.record_result("fx-1", 131, "success", result)
        self.assertEqual(recorded.status, "SUCCEEDED")

    def test_changed_pr_state_cancelled_before_dispatch(self):
        self.prepare()
        self.provider.seed_pr("Lycheetah/demo", 17, "head-B", "base-A")
        claim = self.claim()
        self.assertFalse(claim.allowed)
        self.assertEqual(claim.reason, "live_state_mismatch")
        self.assertEqual(self.g.get_effect("fx-1")["status"], "CANCELLED")

    def test_provider_conditional_check_closes_read_to_write_gap(self):
        self.prepare()
        # Last trusted read was approved head-A; provider changes immediately after claim.
        claim = self.claim()
        self.assertTrue(claim.allowed)
        self.provider.seed_pr("Lycheetah/demo", 17, "head-C", "base-A")
        outcome = self.provider.merge(claim.action, "fx-1")
        self.assertEqual(outcome["reason"], "stale_sha")
        self.g.record_result("fx-1", 131, "failure", outcome)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "FAILED")

    def test_revocation_after_prepare_blocks_claim(self):
        self.prepare()
        self.g.revoke_all(self.actor, 125)
        # The external checkpoint service would keep a checkpoint of the new legitimate event.
        # The prior prefix checkpoint is still valid too.
        claim = self.claim()
        self.assertFalse(claim.allowed)
        self.assertEqual(claim.reason, "revoked")

    def test_revocation_before_prepare_blocks_old_approval(self):
        self.g.revoke_all(self.actor, 110)
        d = self.prepare()
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "revoked")

    def test_approval_is_single_use_even_with_different_effect_ids(self):
        self.assertTrue(self.prepare("fx-1").allowed)
        d = self.prepare("fx-2")
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "approval_already_consumed")

    def test_persistence_across_restart_and_replay_protection(self):
        self.prepare()
        self.g = PersistentActionGuard(self.db)  # simulate process restart
        row = self.g.get_effect("fx-1")
        self.assertEqual(row["status"], "PREPARED")
        d = self.prepare("fx-2")
        self.assertFalse(d.allowed)
        claim = self.claim()
        self.assertTrue(claim.allowed)
        self.g = PersistentActionGuard(self.db)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "DISPATCHING")

    def test_unknown_outcome_does_not_allow_reclaim(self):
        self.prepare()
        self.assertTrue(self.claim().allowed)
        self.g.record_result("fx-1", 131, "unknown", {"reason": "timeout"})
        second = self.claim(now=132)
        self.assertFalse(second.allowed)
        self.assertEqual(second.reason, "effect_not_prepared")
        self.assertEqual(self.g.get_effect("fx-1")["status"], "UNKNOWN")

    def test_unknown_reconciles_only_with_definitive_evidence(self):
        self.prepare()
        self.assertTrue(self.claim().allowed)
        self.g.record_result("fx-1", 131, "unknown", {"reason": "timeout_after_send"})
        missing = self.g.reconcile_effect("fx-1", 140, "success", {})
        self.assertFalse(missing.allowed)
        self.assertEqual(missing.reason, "reconciliation_evidence_required")
        resolved = self.g.reconcile_effect("fx-1", 141, "success",
                                           {"provider_check": "PR merged", "observed_head_sha": "head-A"})
        self.assertTrue(resolved.allowed)
        self.assertEqual(resolved.status, "SUCCEEDED")
        self.assertTrue(any(e["event"] == "PROVIDER_RECONCILED" for e in self.g.audit_events("fx-1")))

    def test_idempotent_provider_recovers_crash_after_remote_effect(self):
        self.prepare()
        claim = self.claim()
        first = self.provider.merge(claim.action, "fx-1")
        self.assertTrue(self.provider.current_pr[("Lycheetah/demo", 17)]["merged"])
        # Simulated crash: provider returned success, local ledger was not updated.
        self.g = PersistentActionGuard(self.db)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "DISPATCHING")
        second = self.provider.merge(claim.action, "fx-1")  # only safe because fake provider guarantees idempotency
        self.assertEqual(first, second)
        self.assertEqual(self.provider.calls, 1)
        self.g.record_result("fx-1", 140, "success", second)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "SUCCEEDED")

    def test_expired_approval_denied(self):
        d = self.g.prepare_effect("fx-1", "ap-1", self.actor, self.action, self.scope, 200)
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "expired")

    def test_approval_bound_to_exact_action(self):
        changed = dict(self.action, head_sha="tampered")
        d = self.prepare(action=changed)
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "action_mismatch")

    def test_concurrent_prepare_has_only_one_winner(self):
        barrier = threading.Barrier(8)
        results = []
        lock = threading.Lock()
        def worker(i):
            g = PersistentActionGuard(self.db)
            barrier.wait()
            d = g.prepare_effect(f"thread-{i}", "ap-1", self.actor, self.action, self.scope, 120)
            with lock: results.append(d)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=10)
        self.assertTrue(all(not t.is_alive() for t in threads))
        self.assertEqual(sum(d.allowed for d in results), 1)
        self.assertEqual(len([e for e in self.g.audit_events() if e["event"] == "EFFECT_PREPARED"]), 1)


    def test_audit_chain_verifies_and_anchor_detects_tail_truncation(self):
        self.prepare()
        baseline = self.g.verify_audit_chain()
        self.assertTrue(baseline["valid"], baseline)
        anchor = self.g.audit_anchor()
        self.assertEqual(anchor["event_count"], baseline["event_count"])
        # A separately retained checkpoint detects deletion of the latest journal event.
        import sqlite3
        with sqlite3.connect(self.db) as c:
            c.execute("DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)")
        internal = self.g.verify_audit_chain()
        self.assertTrue(internal["valid"], internal)  # cannot infer tail loss without an anchor
        anchored = self.g.verify_audit_chain(anchor)
        self.assertFalse(anchored["valid"])
        self.assertEqual(anchored["reason"], "external_anchor_mismatch")

    def test_cannot_mint_checkpoint_from_internally_corrupt_chain(self):
        self.prepare()
        import sqlite3
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE audit SET details_json='{}' WHERE seq=(SELECT MAX(seq) FROM audit)")
        with self.assertRaisesRegex(RuntimeError, "audit_chain_invalid"):
            self.g.audit_anchor()

    def test_audit_edit_blocks_dispatch(self):
        self.prepare()
        import sqlite3
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE audit SET details_json='{}' WHERE seq=(SELECT MAX(seq) FROM audit)")
        check = self.g.verify_audit_chain()
        self.assertFalse(check["valid"], check)
        claim = self.claim()
        self.assertFalse(claim.allowed)
        self.assertEqual(claim.reason, "audit_chain_invalid")
        self.assertEqual(self.provider.calls, 0)


    def test_dispatch_requires_separate_trusted_audit_anchor(self):
        self.prepare()
        denied = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.reason, "trusted_audit_anchor_required")
        self.assertEqual(self.provider.calls, 0)

    def test_tail_truncation_blocks_dispatch_with_previously_saved_anchor(self):
        self.prepare()
        import sqlite3
        with sqlite3.connect(self.db) as c:
            c.execute("DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)")
        # Internal hash chain alone can't identify tail truncation, but the saved external
        # checkpoint proves the expected event count/root no longer match.
        decision = self.claim()
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "audit_chain_invalid")
        self.assertEqual(self.provider.calls, 0)


    def test_external_anchor_detects_a_forged_recomputed_chain(self):
        self.prepare()
        saved_anchor = self.latest_anchor
        import sqlite3
        # Simulate a database writer who edits a row and recomputes every hash in the chain.
        with sqlite3.connect(self.db) as raw:
            raw.row_factory = sqlite3.Row
            raw.execute("UPDATE audit SET details_json='{}' WHERE seq=1")
            rows = raw.execute("SELECT * FROM audit ORDER BY seq").fetchall()
            previous = ""  # replaced below with the protocol genesis value
            from action_guard_v07 import AUDIT_GENESIS
            previous = AUDIT_GENESIS
            for row in rows:
                digest = PersistentActionGuard._audit_hash(
                    row["seq"], row["at"], row["actor"], row["approval_id"], row["effect_id"],
                    row["event"], row["reason"], row["details_json"], previous)
                raw.execute("UPDATE audit SET prev_hash=?,event_hash=? WHERE seq=?",
                            (previous, digest, row["seq"]))
                previous = digest
        self.assertTrue(self.g.verify_audit_chain()["valid"])  # internal chain was rebuilt consistently
        self.assertFalse(self.g.verify_audit_chain(saved_anchor)["valid"])
        decision = self.claim()
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "audit_chain_invalid")
        self.assertEqual(self.provider.calls, 0)

    def test_migrates_legacy_v06_audit_rows(self):
        import sqlite3
        legacy_db = Path(self.tmp.name) / "legacy-v06.sqlite3"
        with sqlite3.connect(legacy_db) as raw:
            raw.execute("""CREATE TABLE audit (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL,
                actor TEXT NOT NULL, approval_id TEXT, effect_id TEXT,
                event TEXT NOT NULL, reason TEXT NOT NULL, details_json TEXT NOT NULL)""")
            raw.execute("INSERT INTO audit(at,actor,approval_id,effect_id,event,reason,details_json) VALUES(1,'legacy-agent',NULL,NULL,'LEGACY_EVENT','migrated','{}')")
        migrated = PersistentActionGuard(legacy_db)
        check = migrated.verify_audit_chain()
        self.assertTrue(check["valid"], check)
        self.assertEqual(check["event_count"], 1)
        self.assertEqual(migrated.audit_events()[0]["event"], "LEGACY_EVENT")

    def test_audit_sequence_middle_deletion_is_detected(self):
        self.prepare()
        self.g.revoke_all(self.actor, 125)  # create a third event so row 2 is not the tail
        import sqlite3
        with sqlite3.connect(self.db) as c:
            c.execute("DELETE FROM audit WHERE seq=2")
        result = self.g.verify_audit_chain()
        self.assertFalse(result["valid"])
        self.assertIn(result["reason"], {"sequence_gap", "previous_hash_mismatch", "event_hash_mismatch"})

    def test_audit_chain_grows_verifiably(self):
        before = self.g.verify_audit_chain()
        self.assertTrue(before["valid"], before)
        self.prepare()
        after = self.g.verify_audit_chain()
        self.assertTrue(after["valid"], after)
        self.assertGreater(after["event_count"], before["event_count"])

    def test_audit_survives_restart(self):
        self.prepare()
        self.g = PersistentActionGuard(self.db)
        events = self.g.audit_events("fx-1")
        self.assertTrue(any(e["event"] == "EFFECT_PREPARED" for e in events))

if __name__ == "__main__":
    unittest.main(verbosity=2)
