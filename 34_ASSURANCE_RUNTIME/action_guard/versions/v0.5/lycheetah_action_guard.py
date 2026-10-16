"""Lycheetah Action Guard v0.5 — reference monitor research prototype.

Purpose: demonstrate action-bound, short-lived, revocable approvals for agent tools.
No network/provider integration. In-memory state only. Python standard library.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

def canonical_action(action: dict[str, Any]) -> str:
    """Canonicalize exact action intent; rejects non-JSON values."""
    return json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def action_digest(action: dict[str, Any]) -> str:
    return sha256(canonical_action(action).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Approval:
    approval_id: str
    actor: str
    action_hash: str
    scope: str
    issued_at: int
    expires_at: int
    authority_epoch: int

@dataclass
class Decision:
    allowed: bool
    reason: str
    effect_id: str | None = None

class ActionGuard:
    """Fail-closed reference monitor for exact-action approval.

    The caller must supply trusted current time and authoritative current epoch.
    In production those must come from trusted services/storage, not the agent.
    """
    def __init__(self):
        self.current_epoch: dict[str, int] = {}
        self.approvals: dict[str, Approval] = {}
        self.effects: set[str] = set()
        self.audit: list[dict[str, Any]] = []

    def set_epoch(self, actor: str, epoch: int) -> None:
        old = self.current_epoch.get(actor, 0)
        if epoch < old:
            raise ValueError("authority epoch cannot move backwards")
        self.current_epoch[actor] = epoch

    def issue(self, approval_id: str, actor: str, action: dict[str, Any],
              scope: str, issued_at: int, expires_at: int) -> Approval:
        if not actor or not scope or expires_at <= issued_at:
            raise ValueError("invalid approval")
        approval = Approval(approval_id, actor, action_digest(action), scope,
                            issued_at, expires_at, self.current_epoch.get(actor, 0))
        self.approvals[approval_id] = approval
        return approval

    def revoke_all(self, actor: str) -> int:
        self.current_epoch[actor] = self.current_epoch.get(actor, 0) + 1
        return self.current_epoch[actor]

    def authorize_and_commit(self, approval_id: str, actor: str,
                             action: dict[str, Any], required_scope: str,
                             now: int, effect_id: str) -> Decision:
        """Single-process linearization point for check+effect registration."""
        a = self.approvals.get(approval_id)
        reason = "allowed"
        if a is None: reason = "missing_approval"
        elif a.actor != actor: reason = "actor_mismatch"
        elif a.action_hash != action_digest(action): reason = "action_mismatch"
        elif a.scope != required_scope: reason = "scope_mismatch"
        elif now < a.issued_at: reason = "not_yet_valid"
        elif now >= a.expires_at: reason = "expired"
        elif a.authority_epoch != self.current_epoch.get(actor, 0): reason = "revoked"
        elif effect_id in self.effects: reason = "replay"
        if reason != "allowed":
            self.audit.append({"effect_id": effect_id, "actor": actor,
                               "approval_id": approval_id, "decision": "DENY",
                               "reason": reason, "time": now})
            return Decision(False, reason)
        # In a real system this must be a transaction with the provider or
        # an idempotency/outbox protocol; local registration alone is not atomic
        # with a remote side effect.
        self.effects.add(effect_id)
        self.audit.append({"effect_id": effect_id, "actor": actor,
                           "approval_id": approval_id, "decision": "ALLOW",
                           "reason": reason, "time": now,
                           "action_hash": a.action_hash, "scope": a.scope})
        return Decision(True, "allowed", effect_id)

class NaiveACL:
    """Conventional weak baseline: role can call tool; no action-bound approval."""
    def __init__(self, allowed_tools: set[str]):
        self.allowed_tools = allowed_tools
        self.effects: list[dict[str, Any]] = []
    def execute(self, actor_role: str, action: dict[str, Any]) -> Decision:
        if action.get("tool") not in self.allowed_tools:
            return Decision(False, "tool_not_allowed")
        self.effects.append({"role": actor_role, "action": action})
        return Decision(True, "role_allows_tool", f"effect-{len(self.effects)}")
