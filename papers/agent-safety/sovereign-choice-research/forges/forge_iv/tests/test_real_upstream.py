"""Actual-repository tests, intentionally SKIPPED unless LYCHEETAH_REPO_ROOT is set.

Run inside a checkout (from Forge IV root):
  LYCHEETAH_REPO_ROOT=/path/to/Lycheetah-Framework python -m unittest -v tests.test_real_upstream

This uses the live upstream CommitFence and Action objects WITHOUT modifying them.
"""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from intent_bridge import IntentAuthorityBridge

ROOT = Path(os.getenv("LYCHEETAH_REPO_ROOT", "/unavailable/LYCHEETAH_REPO_ROOT")).expanduser()
SUPPORT = ROOT / "papers" / "agent-safety" / "frontier-controls"
FENCE_DIR = SUPPORT / "01_commit_time_authority_v0_7"
AVAILABLE = (SUPPORT / "research_support.py").is_file() and (FENCE_DIR / "commit_fence.py").is_file()

if AVAILABLE:
    sys.path.insert(0, str(SUPPORT))
    sys.path.insert(0, str(FENCE_DIR))
    from research_support import Action
    from commit_fence import CommitFence


@unittest.skipUnless(AVAILABLE, "set LYCHEETAH_REPO_ROOT to a real Lycheetah-Framework checkout")
class RealUpstreamBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.fence = CommitFence(root / "upstream_fence.sqlite")
        self.bridge = IntentAuthorityBridge(self.fence, root / "intent_journal.sqlite")

    def action(self, *, subject="one", effect_id="fx-1"):
        return Action(principal="alice", tool="email", operation="send",
                      object_id="draft-1", destination="sample@example.test",
                      arguments={"subject":subject}, effect_id=effect_id)

    def test_currently_endorsed_action_commits(self):
        act = self.action()
        record = self.bridge.grant("alice", "email", "Send a particular email", act)
        self.assertEqual(record.version, 1)
        verdict = self.bridge.issue("alice", "email", act)
        self.assertTrue(verdict.allowed)
        result = self.bridge.commit(verdict.handle, act)
        self.assertEqual(result.state, "COMMITTED")
        self.assertEqual(self.fence.effect_count(), 1)

    def test_revocation_fences_uncommitted_action(self):
        act = self.action()
        self.bridge.grant("alice", "email", "initial approval", act)
        handle = self.bridge.issue("alice", "email", act).handle
        self.bridge.withdraw("alice", "email")
        self.assertEqual(self.bridge.commit(handle, act).state, "DENY")
        self.assertEqual(self.fence.effect_count(), 0)

    def test_revision_fences_prior_action_and_permits_new_one(self):
        original = self.action()
        new = self.action(subject="two", effect_id="fx-2")
        self.bridge.grant("alice", "email", "initial", original)
        old_handle = self.bridge.issue("alice", "email", original).handle
        self.bridge.grant("alice", "email", "changed", new)
        self.assertEqual(self.bridge.commit(old_handle, original).state, "DENY")
        self.assertFalse(self.bridge.issue("alice", "email", original).allowed)
        new_handle = self.bridge.issue("alice", "email", new).handle
        self.assertEqual(self.bridge.commit(new_handle, new).state, "COMMITTED")
        self.assertEqual(self.fence.effect_count(), 1)

    def test_existing_effect_not_reversed_by_later_withdrawal(self):
        act = self.action()
        self.bridge.grant("alice", "email", "initial", act)
        handle = self.bridge.issue("alice", "email", act).handle
        self.assertEqual(self.bridge.commit(handle, act).state, "COMMITTED")
        self.bridge.withdraw("alice", "email")
        self.assertEqual(self.fence.effect_count(), 1)
        self.assertEqual(self.bridge.commit(handle, act).state, "CONFIRMED")

if __name__ == "__main__":
    unittest.main()
