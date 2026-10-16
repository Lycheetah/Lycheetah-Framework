"""In-process fake-host adapter and idempotent fake provider for integration tests.

Everything in this module is a test double. It does not authenticate a real
reviewer or contact an external provider.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from authority_gate_v0_5 import (
    ActionIntent, ApprovalAuthority, ConsequenceGate, DispatchRegistry, GateDenied,
    RegisteredDispatcher,
)


class FakeProvider:
    def __init__(self) -> None:
        self.effects: dict[str, dict[str, Any]] = {}
        self.effect_count = 0
        self.timeout_after_commit_once = False
        self.timeout_before_commit_once = False

    def refund_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        operation_id = payload["operation_id"]
        if operation_id in self.effects:
            # Mimic provider idempotency: the same operation_id returns the prior result.
            return {**self.effects[operation_id], "replayed_provider_request": True}
        if self.timeout_before_commit_once:
            self.timeout_before_commit_once = False
            raise TimeoutError("simulated timeout before provider commit")
        result = {
            "status": "committed",
            "operation_id": operation_id,
            "order_id": payload["arguments"].get("order_id"),
            "amount": payload["arguments"].get("amount"),
        }
        self.effects[operation_id] = result
        self.effect_count += 1
        if self.timeout_after_commit_once:
            self.timeout_after_commit_once = False
            raise TimeoutError("simulated timeout after provider commit")
        return result

    def lookup(self, operation_id: str) -> dict[str, Any] | None:
        return self.effects.get(operation_id)


@dataclass
class FakeApprovalUI:
    """Deterministic human-review double; it is not a real identity provider."""
    approve: bool = True
    last_displayed_action: dict[str, Any] | None = None
    reviewer_id: str = "fake-reviewer-1"
    approval_ref: str = "fake-approval-1"

    def confirm(self, action: ActionIntent) -> tuple[str, str] | None:
        self.last_displayed_action = action.execution_payload()
        if not self.approve:
            return None
        return self.reviewer_id, self.approval_ref


class FakeHostAdapter:
    """Trusted-host-shaped flow around an approval gate and a fake provider."""
    def __init__(self, db_path, key: bytes, *, clock, policy_state: dict[str, str], audience: str):
        self.provider = FakeProvider()
        self.ui = FakeApprovalUI()
        self.clock = clock
        self.policy_state = policy_state
        self.audience = audience
        self.policy_provider = lambda: self.policy_state["sha256"]
        self.registry = DispatchRegistry([
            RegisteredDispatcher("refund_order", "fake-provider.refund", "1", self.provider.refund_order)
        ])
        self.authority = ApprovalAuthority(key, audience_id=audience, clock=clock)
        self.gate = ConsequenceGate(
            key, db_path, self.registry, audience_id=audience,
            policy_provider=self.policy_provider, clock=clock,
        )

    def propose(self, *, agent_id="fixture-agent", arguments=None, scopes=("orders:refund",), workspace_id="fixture"):
        return self.registry.make_intent(
            agent_id=agent_id, tool_name="refund_order",
            arguments=arguments or {"order_id": "ORD-42", "amount": 25.0},
            scopes=tuple(scopes), workspace_id=workspace_id,
        )

    def approve(self, action: ActionIntent) -> str | None:
        confirmation = self.ui.confirm(action)
        if confirmation is None:
            return None
        reviewer_id, approval_ref = confirmation
        # In a real host, authenticated identity/UI confirmation must guard this call.
        return self.authority.issue(
            action, policy_sha256=self.policy_provider(),
            reviewer_id=reviewer_id, approval_ref=approval_ref,
        )

    def execute_with_reconciliation(self, token: str, action: ActionIntent) -> dict[str, Any]:
        try:
            result = self.gate.execute(token, action)
            return {"status": "dispatched", "provider_result": result}
        except GateDenied as exc:
            if exc.reason == "effect-error-token-consumed-reconcile-before-retry":
                recovered = self.provider.lookup(action.operation_id)
                if recovered is not None:
                    return {
                        "status": "reconciled-after-timeout",
                        "provider_result": recovered,
                        "gate_reason": exc.reason,
                    }
                return {
                    "status": "unknown-effect-needs-human-reconciliation",
                    "provider_result": None,
                    "gate_reason": exc.reason,
                }
            return {"status": "denied", "gate_reason": exc.reason}
