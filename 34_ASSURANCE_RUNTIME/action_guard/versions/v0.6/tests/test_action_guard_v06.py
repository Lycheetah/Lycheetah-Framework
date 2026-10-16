import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from action_guard_v06 import PersistentActionGuard, FakeMergeProvider

class GuardV06Tests(unittest.TestCase):
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
        return self.g.prepare_effect(eid, "ap-1", self.actor, action or self.action, self.scope, 120)

    def test_normal_dispatch_persists_success(self):
        self.assertTrue(self.prepare().allowed)
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
        self.assertTrue(claim.allowed)
        result = self.provider.merge(claim.action, "fx-1")
        self.assertEqual(result["status"], "success")
        recorded = self.g.record_result("fx-1", 131, "success", result)
        self.assertEqual(recorded.status, "SUCCEEDED")

    def test_changed_pr_state_cancelled_before_dispatch(self):
        self.prepare()
        self.provider.seed_pr("Lycheetah/demo", 17, "head-B", "base-A")
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
        self.assertFalse(claim.allowed)
        self.assertEqual(claim.reason, "live_state_mismatch")
        self.assertEqual(self.g.get_effect("fx-1")["status"], "CANCELLED")

    def test_provider_conditional_check_closes_read_to_write_gap(self):
        self.prepare()
        # Last trusted read was approved head-A; provider changes immediately after claim.
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
        self.assertTrue(claim.allowed)
        self.provider.seed_pr("Lycheetah/demo", 17, "head-C", "base-A")
        outcome = self.provider.merge(claim.action, "fx-1")
        self.assertEqual(outcome["reason"], "stale_sha")
        self.g.record_result("fx-1", 131, "failure", outcome)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "FAILED")

    def test_revocation_after_prepare_blocks_claim(self):
        self.prepare()
        self.g.revoke_all(self.actor, 125)
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
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
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
        self.assertTrue(claim.allowed)
        self.g = PersistentActionGuard(self.db)
        self.assertEqual(self.g.get_effect("fx-1")["status"], "DISPATCHING")

    def test_unknown_outcome_does_not_allow_reclaim(self):
        self.prepare()
        self.assertTrue(self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17)).allowed)
        self.g.record_result("fx-1", 131, "unknown", {"reason": "timeout"})
        second = self.g.claim_dispatch("fx-1", 132, self.provider.read_action("Lycheetah/demo", 17))
        self.assertFalse(second.allowed)
        self.assertEqual(second.reason, "effect_not_prepared")
        self.assertEqual(self.g.get_effect("fx-1")["status"], "UNKNOWN")

    def test_unknown_reconciles_only_with_definitive_evidence(self):
        self.prepare()
        self.assertTrue(self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17)).allowed)
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
        claim = self.g.claim_dispatch("fx-1", 130, self.provider.read_action("Lycheetah/demo", 17))
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

    def test_audit_survives_restart(self):
        self.prepare()
        self.g = PersistentActionGuard(self.db)
        events = self.g.audit_events("fx-1")
        self.assertTrue(any(e["event"] == "EFFECT_PREPARED" for e in events))

if __name__ == "__main__":
    unittest.main(verbosity=2)
