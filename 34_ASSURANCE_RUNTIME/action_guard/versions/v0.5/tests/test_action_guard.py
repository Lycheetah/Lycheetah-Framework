import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lycheetah_action_guard import ActionGuard, NaiveACL

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.g = ActionGuard()
        self.g.set_epoch("mac", 3)
        self.action = {"tool":"github.merge", "repo":"Lycheetah/demo",
                       "pull_request":17, "head_sha":"abc123", "base_sha":"def456"}
        self.g.issue("ap-1", "mac", self.action, "merge:Lycheetah/demo#17",
                     issued_at=100, expires_at=200)

    def test_exact_action_allowed(self):
        d = self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-1")
        self.assertTrue(d.allowed)

    def test_parameter_tamper_denied(self):
        changed = dict(self.action, head_sha="attacker-sha")
        d = self.g.authorize_and_commit("ap-1","mac",changed,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-2")
        self.assertEqual(d.reason,"action_mismatch")

    def test_scope_change_denied(self):
        d = self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:other/repo#17",now=150,effect_id="fx-2")
        self.assertEqual(d.reason,"scope_mismatch")

    def test_expired_denied(self):
        d = self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:Lycheetah/demo#17",now=200,effect_id="fx-2")
        self.assertEqual(d.reason,"expired")

    def test_revocation_denied(self):
        self.g.revoke_all("mac")
        d = self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-2")
        self.assertEqual(d.reason,"revoked")

    def test_replay_denied(self):
        self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-1")
        d = self.g.authorize_and_commit("ap-1","mac",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-1")
        self.assertEqual(d.reason,"replay")

    def test_unknown_approval_denied(self):
        d = self.g.authorize_and_commit("missing","mac",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-2")
        self.assertEqual(d.reason,"missing_approval")

    def test_wrong_actor_denied(self):
        d = self.g.authorize_and_commit("ap-1","other",self.action,
               "merge:Lycheetah/demo#17",now=150,effect_id="fx-2")
        self.assertEqual(d.reason,"actor_mismatch")

    def test_baseline_allows_mutated_action(self):
        baseline = NaiveACL({"github.merge"})
        changed = dict(self.action, head_sha="attacker-sha")
        self.assertTrue(baseline.execute("maintainer", changed).allowed)
        self.assertEqual(len(baseline.effects), 1)

    def test_guard_denies_mutated_action_baseline_allows(self):
        baseline = NaiveACL({"github.merge"})
        changed = dict(self.action, head_sha="attacker-sha")
        b = baseline.execute("maintainer", changed)
        g = self.g.authorize_and_commit("ap-1","mac",changed,
            "merge:Lycheetah/demo#17",now=150,effect_id="fx-2")
        self.assertTrue(b.allowed)
        self.assertFalse(g.allowed)

if __name__ == "__main__":
    unittest.main()
