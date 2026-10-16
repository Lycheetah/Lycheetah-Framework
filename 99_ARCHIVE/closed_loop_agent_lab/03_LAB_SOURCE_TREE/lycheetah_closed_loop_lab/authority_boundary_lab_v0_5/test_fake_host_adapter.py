from __future__ import annotations
import hashlib
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authority_gate_v0_5 import GateDenied
from fake_host_adapter import FakeHostAdapter

KEY = b"fixture-only-key-do-not-use-production-32-bytes-plus"
POLICY = hashlib.sha256(b"policy-v1").hexdigest()
POLICY2 = hashlib.sha256(b"policy-v2").hexdigest()
NOW = 2_000_000_000.0


class FakeHostIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.clock_state = {"now": NOW}
        self.policy_state = {"sha256": POLICY}
        self.host = FakeHostAdapter(
            Path(self.temp.name) / "fake-host.sqlite", KEY,
            clock=lambda: self.clock_state["now"],
            policy_state=self.policy_state,
            audience="fixture:staging",
        )
        self.action = self.host.propose()
        self.token = self.host.approve(self.action)

    def tearDown(self):
        self.temp.cleanup()

    def set_context(self, now=NOW + 1, policy=POLICY):
        self.clock_state["now"] = now
        self.policy_state["sha256"] = policy

    def test_approval_ui_and_provider_share_same_frozen_operation(self):
        self.assertIsNotNone(self.token)
        self.assertEqual(self.host.ui.last_displayed_action, self.action.execution_payload())
        self.set_context()
        result = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(result["status"], "dispatched")
        self.assertEqual(result["provider_result"]["operation_id"], self.action.operation_id)
        self.assertEqual(self.host.provider.effect_count, 1)

    def test_unapproved_proposal_has_no_token_or_provider_effect(self):
        action = self.host.propose(arguments={"order_id": "ORD-NO", "amount": 1.0})
        self.host.ui.approve = False
        token = self.host.approve(action)
        self.assertIsNone(token)
        self.assertEqual(self.host.provider.effect_count, 0)

    def test_policy_drift_after_approval_denies_dispatch(self):
        self.set_context(policy=POLICY2)
        result = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(result, {"status": "denied", "gate_reason": "policy-changed"})
        self.assertEqual(self.host.provider.effect_count, 0)

    def test_changed_action_after_approval_denies_dispatch(self):
        changed = self.host.propose(arguments={"order_id": "ORD-42", "amount": 999999})
        self.set_context()
        result = self.host.execute_with_reconciliation(self.token, changed)
        self.assertEqual(result["status"], "denied")
        self.assertEqual(result["gate_reason"], "action-mismatch")
        self.assertEqual(self.host.provider.effect_count, 0)

    def test_revocation_before_dispatch_denies_action(self):
        self.set_context(now=NOW + 0.5)
        self.host.gate.revoke(self.token, reason="reviewer-cancelled")
        self.set_context(now=NOW + 1)
        result = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(result, {"status": "denied", "gate_reason": "token-revoked"})
        self.assertEqual(self.host.provider.effect_count, 0)

    def test_timeout_after_provider_commit_is_reconciled_without_second_effect(self):
        self.host.provider.timeout_after_commit_once = True
        self.set_context()
        result = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(result["status"], "reconciled-after-timeout")
        self.assertEqual(result["provider_result"]["operation_id"], self.action.operation_id)
        self.assertEqual(self.host.provider.effect_count, 1)

    def test_timeout_before_commit_stops_for_human_reconciliation(self):
        self.host.provider.timeout_before_commit_once = True
        self.set_context()
        result = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(result["status"], "unknown-effect-needs-human-reconciliation")
        self.assertEqual(self.host.provider.effect_count, 0)
        # The consumed approval cannot be blindly replayed after an uncertain result.
        self.set_context(now=NOW + 2)
        replay = self.host.execute_with_reconciliation(self.token, self.action)
        self.assertEqual(replay["status"], "denied")
        self.assertEqual(replay["gate_reason"], "token-replayed")

    def test_concurrent_duplicate_calls_only_commit_one_provider_effect(self):
        self.set_context()
        def attempt(_):
            try:
                return self.host.gate.execute(self.token, self.action)["status"]
            except GateDenied as exc:
                return exc.reason
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(attempt, range(8)))
        self.assertEqual(outcomes.count("committed"), 1)
        self.assertEqual(outcomes.count("token-replayed"), 7)
        self.assertEqual(self.host.provider.effect_count, 1)


if __name__ == "__main__":
    unittest.main()
