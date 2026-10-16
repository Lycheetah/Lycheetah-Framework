import base64
import hashlib
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from authority_gate import (
    ActionIntent, ApprovalAuthority, ConsequenceGate, GateDenied,
)

KEY = b"fixture-only-test-key-never-use-in-production-32bytes+"
POLICY = hashlib.sha256(b"fixture-policy-v1").hexdigest()
POLICY2 = hashlib.sha256(b"fixture-policy-v2").hexdigest()


def tamper_signature(token):
    """Flip a decoded signature byte; changing the final Base64URL character alone can alter only unused pad bits."""
    body, encoded = token.split(".", 1)
    raw = bytearray(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    raw[0] ^= 0x01
    changed = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"{body}.{changed}"


def intent(args=None, tool="refund_order"):
    return ActionIntent(
        agent_id="agent-fixture",
        tool_name=tool,
        arguments={"order_id": "ORD-1042", "amount": 12.50, **(args or {})},
        scopes=("orders:write",),
        workspace_id="case-fixture-01",
    )


class ConsequenceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "used_tokens.sqlite3"
        self.authority = ApprovalAuthority(KEY)
        self.gate = ConsequenceGate(KEY, self.db)
        self.action = intent()
        self.now = 1_800_000_000.0

    def tearDown(self):
        self.tmp.cleanup()

    def token(self, action=None, policy=POLICY, ttl=120):
        return self.authority.issue(
            action or self.action, policy_sha256=policy,
            reviewer_id="reviewer-7", approval_ref="approval-ui-889",
            ttl_seconds=ttl, now=self.now,
        )

    def test_valid_approval_dispatches_exact_snapshot(self):
        observed = []
        result = self.gate.execute(
            self.token(), self.action, current_policy_sha256=POLICY,
            effect=lambda payload: observed.append(payload) or "done", now=self.now + 1,
        )
        self.assertEqual(result, "done")
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["tool_name"], "refund_order")
        self.assertEqual(observed[0]["arguments"]["amount"], 12.5)

    def test_model_self_claim_without_host_token_is_denied(self):
        # A field like human_approved=True in an agent proposal is not a token.
        with self.assertRaisesRegex(GateDenied, "approval-token-required-or-malformed"):
            self.gate.execute(None, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_token_cannot_be_replayed(self):
        token = self.token()
        self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                          effect=lambda _: "first", now=self.now + 1)
        with self.assertRaisesRegex(GateDenied, "token-replayed"):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch twice"), now=self.now + 2)

    def test_token_is_bound_to_exact_action_arguments(self):
        with self.assertRaisesRegex(GateDenied, "action-mismatch"):
            self.gate.execute(self.token(), intent({"amount": 99.99}), current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_token_is_bound_to_tool_identity(self):
        with self.assertRaisesRegex(GateDenied, "action-mismatch"):
            self.gate.execute(self.token(), intent(tool="delete_customer"), current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_policy_change_invalidates_approval(self):
        with self.assertRaisesRegex(GateDenied, "policy-changed"):
            self.gate.execute(self.token(policy=POLICY), self.action, current_policy_sha256=POLICY2,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_expired_token_is_denied(self):
        token = self.token(ttl=5)
        with self.assertRaisesRegex(GateDenied, "token-expired"):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 5)

    def test_future_issued_token_is_denied(self):
        token = self.authority.issue(self.action, policy_sha256=POLICY,
                                     reviewer_id="r", approval_ref="a", now=self.now + 50)
        with self.assertRaisesRegex(GateDenied, "token-not-yet-valid"):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now)

    def test_tampered_token_is_denied(self):
        token = self.token()
        changed = tamper_signature(token)
        with self.assertRaises(GateDenied):
            self.gate.execute(changed, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_another_key_cannot_validate_token(self):
        other_gate = ConsequenceGate(b"different-fixture-key-that-is-also-at-least-32-bytes", self.db)
        with self.assertRaisesRegex(GateDenied, "token-authentication-failed"):
            other_gate.execute(self.token(), self.action, current_policy_sha256=POLICY,
                               effect=lambda _: self.fail("must not dispatch"), now=self.now + 1)

    def test_mutating_source_arguments_after_intent_creation_does_not_change_dispatch(self):
        source = {"order_id": "ORD-1042", "amount": 12.50}
        action = ActionIntent("agent-fixture", "refund_order", source,
                              ("orders:write",), "case-fixture-01")
        token = self.token(action)
        source["amount"] = 999999
        observed = []
        self.gate.execute(token, action, current_policy_sha256=POLICY,
                          effect=lambda payload: observed.append(payload), now=self.now + 1)
        self.assertEqual(observed[0]["arguments"]["amount"], 12.5)

    def test_executor_exception_consumes_token_and_requires_reconciliation(self):
        token = self.token()
        with self.assertRaisesRegex(GateDenied, "effect-error-token-consumed-reconcile-before-retry"):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: (_ for _ in ()).throw(RuntimeError("uncertain")),
                              now=self.now + 1)
        with self.assertRaisesRegex(GateDenied, "token-replayed"):
            self.gate.execute(token, self.action, current_policy_sha256=POLICY,
                              effect=lambda _: "unsafe second call", now=self.now + 2)

    def test_concurrent_replay_has_at_most_one_dispatch(self):
        token = self.token()
        calls = []
        call_lock = __import__("threading").Lock()

        def try_dispatch(_):
            try:
                result = self.gate.execute(
                    token, self.action, current_policy_sha256=POLICY,
                    effect=lambda payload: (call_lock.acquire(), calls.append(payload), call_lock.release(), "ok")[-1],
                    now=self.now + 1,
                )
                return ("allowed", result)
            except GateDenied as exc:
                return ("denied", exc.reason)

        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes = list(pool.map(try_dispatch, range(8)))
        self.assertEqual(sum(1 for status, _ in outcomes if status == "allowed"), 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(sum(1 for status, reason in outcomes if status == "denied" and reason == "token-replayed"), 7)

    def test_approval_authority_rejects_too_long_ttl(self):
        with self.assertRaises(ValueError):
            self.token(ttl=601)


if __name__ == "__main__":
    unittest.main()
