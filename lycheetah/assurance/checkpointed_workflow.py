"""Checkpoint-gated workflow around the PersistentActionGuard ledger.

Every mutation is bracketed by a signed external checkpoint. The workflow refuses
to act if its journal is ahead of, behind, or inconsistent with the external receipt.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from threading import RLock
from typing import Any

from .action_guard import AUDIT_GENESIS, Decision, PersistentActionGuard
from .checkpoint_authority import CheckpointError, CheckpointHTTPClient, CheckpointStore


class WorkflowBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class OperationReceipt:
    decision: Decision
    checkpointed: bool
    checkpoint_generation: int | None = None
    error: str | None = None


class CheckpointedWorkflow:
    """Fail-closed adapter that checkpoints every local state transition."""

    def __init__(
        self,
        guard: PersistentActionGuard,
        checkpoints: CheckpointHTTPClient | CheckpointStore,
        journal_id: str = "lycheetah-action-guard",
    ):
        self.guard = guard
        self.checkpoints = checkpoints
        self.journal_id = journal_id
        self._lock = RLock()

    @contextmanager
    def effect_session(self) -> Iterator[None]:
        """Hold the per-instance operation lock over claim -> provider call -> result."""
        with self._lock:
            yield

    @staticmethod
    def _anchor(envelope: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_count": envelope["event_count"],
            "last_seq": envelope["last_seq"],
            "root_hash": envelope["root_hash"],
        }

    def _get_latest(self) -> dict[str, Any] | None:
        if isinstance(self.checkpoints, CheckpointHTTPClient):
            return self.checkpoints.get_latest(self.journal_id)
        return self.checkpoints.latest(self.journal_id)

    def _publish(self, anchor: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
        if isinstance(self.checkpoints, CheckpointHTTPClient):
            return self.checkpoints.publish(self.journal_id, anchor, events)
        return self.checkpoints.store(self.journal_id, anchor, events)

    def bootstrap_empty_journal(self) -> OperationReceipt:
        """Create first external anchor only for a truly empty journal."""
        latest = self._get_latest()
        if latest is not None:
            status = self.guard.verify_audit_chain(self._anchor(latest))
            current = self.guard.audit_anchor()
            consistency = self.guard.verify_state_consistency()
            if not status["valid"] or current != self._anchor(latest) or not consistency["valid"]:
                raise WorkflowBlocked("bootstrap_requires_synchronized_journal")
            return OperationReceipt(
                Decision(True, "already_bootstrapped"), True, latest["generation"]
            )
        current = self.guard.audit_anchor()
        consistency = self.guard.verify_state_consistency()
        if not consistency["valid"]:
            raise WorkflowBlocked("refusing_to_anchor_inconsistent_operational_ledger")
        if current != {
            "event_count": 0,
            "last_seq": None,
            "root_hash": AUDIT_GENESIS,
        }:
            raise WorkflowBlocked("refusing_to_anchor_preexisting_uncheckpointed_history")
        try:
            envelope = self._publish(current, [])
        except CheckpointError as exc:
            return OperationReceipt(
                Decision(False, "checkpoint_unavailable"), False, error=str(exc)
            )
        return OperationReceipt(Decision(True, "bootstrapped"), True, envelope["generation"])

    def _trusted_checkpoint(self) -> dict[str, Any]:
        envelope = self._get_latest()
        if envelope is None:
            raise WorkflowBlocked("external_checkpoint_missing")
        trusted_anchor = self._anchor(envelope)
        status = self.guard.verify_audit_chain(trusted_anchor)
        if not status["valid"]:
            raise WorkflowBlocked("audit_history_invalid_against_external_checkpoint")
        consistency = self.guard.verify_state_consistency()
        if not consistency["valid"]:
            raise WorkflowBlocked("operational_ledger_inconsistent_against_audit")
        current_anchor = self.guard.audit_anchor()
        if current_anchor != trusted_anchor:
            raise WorkflowBlocked("uncheckpointed_audit_tail_detected")
        return envelope

    def synchronize_status(self) -> dict[str, Any]:
        """Read-only operational status check against the external checkpoint authority."""
        latest = self._get_latest()
        if latest is None:
            return {"synchronized": False, "reason": "no_external_checkpoint"}
        trusted_anchor = self._anchor(latest)
        audit_status = self.guard.verify_audit_chain(trusted_anchor)
        consistency = self.guard.verify_state_consistency()
        current_anchor = self.guard.audit_anchor() if audit_status["valid"] else None
        synchronized = (
            audit_status["valid"] and consistency["valid"] and current_anchor == trusted_anchor
        )
        return {
            "synchronized": synchronized,
            "audit_chain_valid": audit_status["valid"],
            "state_consistency_valid": consistency["valid"],
            "checkpoint_generation": latest.get("generation"),
            "event_count": latest.get("event_count"),
            "last_seq": latest.get("last_seq"),
            "root_hash": latest.get("root_hash"),
            "reason": "ok" if synchronized else "journal_and_checkpoint_out_of_sync",
        }

    def _run_checkpointed_mutation(
        self,
        mutation: Any,
        expected_prior_checkpoint: dict[str, Any],
    ) -> OperationReceipt:
        try:
            decision = mutation()
        except Exception as exc:
            return OperationReceipt(Decision(False, "mutation_exception"), False, error=str(exc))
        try:
            new_anchor = self.guard.audit_anchor()
            prior_last_seq = expected_prior_checkpoint.get("last_seq")
            events = self.guard.audit_chain_events_after(prior_last_seq)
            if events:
                envelope = self._publish(new_anchor, events)
                generation = envelope.get("generation")
            else:
                generation = expected_prior_checkpoint.get("generation")
            return OperationReceipt(decision, True, generation)
        except (CheckpointError, RuntimeError) as exc:
            return OperationReceipt(decision, False, error=str(exc))

    def issue_approval(
        self,
        approval_id: str,
        actor: str,
        approver_id: str,
        action: dict[str, Any],
        scope: str,
        issued_at: int,
        expires_at: int,
    ) -> OperationReceipt:
        with self._lock:
            trusted = self._trusted_checkpoint()
            return self._run_checkpointed_mutation(
                lambda: self.guard.issue_approval(
                    approval_id, actor, approver_id, action, scope, issued_at, expires_at
                ),
                trusted,
            )

    def prepare_effect(
        self,
        effect_id: str,
        approval_id: str,
        actor: str,
        action: dict[str, Any],
        scope: str,
        now: int,
    ) -> OperationReceipt:
        with self._lock:
            trusted = self._trusted_checkpoint()
            return self._run_checkpointed_mutation(
                lambda: self.guard.prepare_effect(
                    effect_id, approval_id, actor, action, scope, now
                ),
                trusted,
            )

    def claim_dispatch(
        self, effect_id: str, now: int, current_action: dict[str, Any]
    ) -> OperationReceipt:
        with self._lock:
            trusted = self._trusted_checkpoint()
            trusted_anchor = self._anchor(trusted)
            return self._run_checkpointed_mutation(
                lambda: self.guard.claim_dispatch(
                    effect_id,
                    now,
                    current_action,
                    expected_audit_anchor=trusted_anchor,
                    require_exact_audit_anchor=True,
                ),
                trusted,
            )

    def record_result(
        self,
        effect_id: str,
        now: int,
        outcome: Any,
        details: dict[str, Any] | None = None,
    ) -> OperationReceipt:
        with self._lock:
            trusted = self._trusted_checkpoint()
            return self._run_checkpointed_mutation(
                lambda: self.guard.record_result(effect_id, now, outcome, details),
                trusted,
            )

    def revoke_all(self, actor: str, now: int) -> OperationReceipt:
        with self._lock:
            trusted = self._trusted_checkpoint()
            return self._run_checkpointed_mutation(
                lambda: Decision(True, "revoked", effect_id=str(self.guard.revoke_all(actor, now))),
                trusted,
            )
