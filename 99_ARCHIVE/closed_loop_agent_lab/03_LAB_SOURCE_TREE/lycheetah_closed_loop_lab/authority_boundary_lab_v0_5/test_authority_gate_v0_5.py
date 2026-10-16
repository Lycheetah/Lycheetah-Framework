from __future__ import annotations

import base64
import hashlib
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from authority_gate_v0_5 import (
    ActionIntent, ApprovalAuthority, ConsequenceGate, DispatchRegistry,
    GateDenied, RegisteredDispatcher,
)

KEY = b"fixture-only-key-do-not-use-production-32-bytes-plus"
POLICY = hashlib.sha256(b"policy-v1").hexdigest()
POLICY2 = hashlib.sha256(b"policy-v2").hexdigest()
NOW = 2_000_000_000.0
AUDIENCE = "lycheetah-test:dev"


def tamper_signature(token):
    """Flip an actual HMAC byte so the test cannot change only unused pad bits."""
    body, encoded = token.split(".", 1)
    raw = bytearray(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    raw[0] ^= 0x01
    changed = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"{body}.{changed}"


class TestBoundDispatcherApproval(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "nonce.sqlite"
        self.calls = []
        self.lock = threading.Lock()
        self.clock_state = {"now": NOW}
        self.policy_state = {"sha256": POLICY}
        self.clock = lambda: self.clock_state["now"]
        self.policy_provider = lambda: self.policy_state["sha256"]

        def refund(payload):
            with self.lock:
                self.calls.append(("refund", payload))
            return {"status": "refunded", "order_id": payload["arguments"]["order_id"]}

        def delete(payload):
            with self.lock:
                self.calls.append(("delete", payload))
            return {"status": "deleted"}

        self.registry = DispatchRegistry([
            RegisteredDispatcher("refund_order", "provider.refund", "2", refund),
            RegisteredDispatcher("delete_account", "provider.identity-delete", "1", delete),
        ])
        self.authority = ApprovalAuthority(KEY, audience_id=AUDIENCE, clock=self.clock)
        self.gate = ConsequenceGate(
            KEY, self.db, self.registry, audience_id=AUDIENCE,
            policy_provider=self.policy_provider, clock=self.clock,
        )
        self.action = self.registry.make_intent(
            agent_id="agent-test", tool_name="refund_order",
            arguments={"order_id": "ORD-77", "amount": 12.5},
            scopes=("orders:refund",), workspace_id="case-77",
        )

    def tearDown(self):
        self.temp.cleanup()

    def set_context(self, *, now=NOW + 1, policy=POLICY):
        self.clock_state["now"] = now
        self.policy_state["sha256"] = policy

    def token(self, action=None, policy=POLICY, ttl=120, issued_at=NOW):
        original = self.clock_state["now"]
        try:
            self.clock_state["now"] = issued_at
            return self.authority.issue(
                action or self.action, policy_sha256=policy,
                reviewer_id="reviewer-1", approval_ref="approval-77", ttl_seconds=ttl,
            )
        finally:
            self.clock_state["now"] = original

    def test_valid_approval_dispatches_only_registered_refund(self):
        token = self.token()
        self.set_context()
        result = self.gate.execute(token, self.action)
        self.assertEqual(result, {"status": "refunded", "order_id": "ORD-77"})
        self.assertEqual([kind for kind, _ in self.calls], ["refund"])

    def test_no_execution_callback_argument_exists(self):
        token = self.token()
        self.set_context()
        # API design property: caller cannot swap an arbitrary callback at execution time.
        with self.assertRaises(TypeError):
            self.gate.execute(token, self.action, effect=lambda _: "wrong")
        self.assertEqual(self.calls, [])

    def test_no_policy_override_argument_exists(self):
        token = self.token()
        self.set_context()
        with self.assertRaises(TypeError):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY)
        self.assertEqual(self.calls, [])

    def test_model_cannot_claim_approval_with_boolean(self):
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "approval-token-required-or-malformed"):
            self.gate.execute("approved=true", self.action)
        self.assertEqual(self.calls, [])

    def test_action_mutation_requires_new_approval(self):
        token = self.token()
        changed = self.registry.make_intent(
            agent_id="agent-test", tool_name="refund_order",
            arguments={"order_id": "ORD-77", "amount": 999999},
            scopes=("orders:refund",), workspace_id="case-77",
        )
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "action-mismatch"):
            self.gate.execute(token, changed)
        self.assertEqual(self.calls, [])

    def test_source_mapping_mutation_does_not_change_dispatched_snapshot(self):
        source = {"order_id": "ORD-77", "amount": 12.5}
        action = self.registry.make_intent(agent_id="a", tool_name="refund_order",
            arguments=source, scopes=("orders:refund",), workspace_id="w")
        token = self.token(action)
        source["amount"] = 99999
        self.set_context()
        self.gate.execute(token, action)
        self.assertEqual(self.calls[-1][1]["arguments"]["amount"], 12.5)

    def test_changed_policy_is_denied_from_trusted_provider(self):
        token = self.token(policy=POLICY)
        self.set_context(policy=POLICY2)
        with self.assertRaisesRegex(GateDenied, "policy-changed"):
            self.gate.execute(token, self.action)
        self.assertEqual(self.calls, [])

    def test_expired_and_future_tokens_are_denied(self):
        expired = self.token(ttl=5, issued_at=NOW)
        self.set_context(now=NOW + 5)
        with self.assertRaisesRegex(GateDenied, "token-expired"):
            self.gate.execute(expired, self.action)
        future = self.token(issued_at=NOW + 50)
        self.set_context(now=NOW)
        with self.assertRaisesRegex(GateDenied, "token-not-yet-valid"):
            self.gate.execute(future, self.action)
        self.assertEqual(self.calls, [])

    def test_policy_bound_to_registered_dispatcher_identity_and_version(self):
        token = self.token()
        changed_registry = DispatchRegistry([
            RegisteredDispatcher("refund_order", "provider.refund-v2", "3", lambda _: "wrong"),
            RegisteredDispatcher("delete_account", "provider.identity-delete", "1", lambda _: "delete"),
        ])
        other_gate = ConsequenceGate(
            KEY, self.db, changed_registry, audience_id=AUDIENCE,
            policy_provider=self.policy_provider, clock=self.clock,
        )
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "dispatcher-binding-changed"):
            other_gate.execute(token, self.action)
        self.assertEqual(self.calls, [])

    def test_unknown_tool_cannot_get_an_intent(self):
        with self.assertRaisesRegex(GateDenied, "tool-not-registered"):
            self.registry.make_intent(agent_id="a", tool_name="shell_exec", arguments={},
                scopes=("host:*",), workspace_id="w")

    def test_approval_for_one_registered_tool_cannot_authorize_another(self):
        token = self.token()
        delete_action = self.registry.make_intent(agent_id="agent-test", tool_name="delete_account",
            arguments={"account_id": "A-99"}, scopes=("identity:delete",), workspace_id="case-77")
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "action-mismatch"):
            self.gate.execute(token, delete_action)
        self.assertEqual(self.calls, [])

    def test_revoked_token_is_denied_before_dispatch(self):
        token = self.token()
        self.set_context(now=NOW + 0.5)
        self.gate.revoke(token, reason="reviewer-cancelled")
        self.set_context(now=NOW + 1)
        with self.assertRaisesRegex(GateDenied, "token-revoked"):
            self.gate.execute(token, self.action)
        self.assertEqual(self.calls, [])

    def test_replay_is_denied(self):
        token = self.token()
        self.set_context(now=NOW + 1)
        self.gate.execute(token, self.action)
        self.set_context(now=NOW + 2)
        with self.assertRaisesRegex(GateDenied, "token-replayed"):
            self.gate.execute(token, self.action)
        self.assertEqual(len(self.calls), 1)

    def test_replay_remains_denied_after_gate_reconstruction(self):
        token = self.token()
        self.set_context(now=NOW + 1)
        self.gate.execute(token, self.action)
        restarted = ConsequenceGate(
            KEY, self.db, self.registry, audience_id=AUDIENCE,
            policy_provider=self.policy_provider, clock=self.clock,
        )
        self.set_context(now=NOW + 2)
        with self.assertRaisesRegex(GateDenied, "token-replayed"):
            restarted.execute(token, self.action)
        self.assertEqual(len(self.calls), 1)

    def test_eight_concurrent_replays_dispatch_exactly_once(self):
        token = self.token()
        self.set_context()
        def attempt(_):
            try:
                self.gate.execute(token, self.action)
                return "allowed"
            except GateDenied as exc:
                return exc.reason
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(8)))
        self.assertEqual(results.count("allowed"), 1)
        self.assertEqual(results.count("token-replayed"), 7)
        self.assertEqual(len(self.calls), 1)

    def test_effect_exception_consumes_token(self):
        def fail(payload):
            raise RuntimeError("provider may have acted before timeout")
        registry = DispatchRegistry([RegisteredDispatcher("refund_order", "provider.refund", "2", fail)])
        gate = ConsequenceGate(
            KEY, self.db, registry, audience_id=AUDIENCE,
            policy_provider=self.policy_provider, clock=self.clock,
        )
        action = registry.make_intent(agent_id="a", tool_name="refund_order", arguments={"order_id":"X"},
                                      scopes=("orders:refund",), workspace_id="w")
        token = self.token(action)
        self.set_context(now=NOW + 1)
        with self.assertRaisesRegex(GateDenied, "reconcile-before-retry"):
            gate.execute(token, action)
        self.set_context(now=NOW + 2)
        with self.assertRaisesRegex(GateDenied, "token-replayed"):
            gate.execute(token, action)

    def test_token_cannot_cross_deployment_audience(self):
        token = self.token()
        other_gate = ConsequenceGate(
            KEY, self.db, self.registry, audience_id="lycheetah-test:prod",
            policy_provider=self.policy_provider, clock=self.clock,
        )
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "token-audience-mismatch"):
            other_gate.execute(token, self.action)
        self.assertEqual(self.calls, [])

    def test_policy_source_failure_fails_closed(self):
        token = self.token()
        def unavailable():
            raise RuntimeError("policy store down")
        gate = ConsequenceGate(KEY, self.db, self.registry, audience_id=AUDIENCE,
            policy_provider=unavailable, clock=self.clock)
        self.set_context()
        with self.assertRaisesRegex(GateDenied, "policy-source-unavailable-or-invalid"):
            gate.execute(token, self.action)
        self.assertEqual(self.calls, [])

    def test_issuer_rejects_nonfinite_clock_and_bool_ttl(self):
        self.clock_state["now"] = float("nan")
        with self.assertRaises(ValueError):
            self.authority.issue(self.action, policy_sha256=POLICY,
                reviewer_id="r", approval_ref="a")
        self.clock_state["now"] = NOW
        with self.assertRaises(ValueError):
            self.authority.issue(self.action, policy_sha256=POLICY,
                reviewer_id="r", approval_ref="a", ttl_seconds=True)

    def test_tamper_helper_changes_decoded_signature_byte(self):
        token = self.token()
        body, encoded = token.split(".", 1)
        original = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        altered = tamper_signature(token)
        changed_body, changed_encoded = altered.split(".", 1)
        changed = base64.urlsafe_b64decode(
            changed_encoded + "=" * (-len(changed_encoded) % 4)
        )
        self.assertEqual(body, changed_body)
        self.assertNotEqual(original, changed)

    def test_hmac_tampering_is_denied(self):
        token = self.token()
        altered = tamper_signature(token)
        self.set_context()
        with self.assertRaises(GateDenied):
            self.gate.execute(altered, self.action)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
