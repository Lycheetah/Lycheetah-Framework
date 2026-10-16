"""Checkpoint-gated workflow around the v0.7 action guard.

Every mutation is bracketed by a signed external checkpoint. The workflow refuses
to act if its journal is ahead of, behind, or inconsistent with the external receipt.
This closes the easy failure mode where a caller silently mints a new checkpoint over
an unanchored or rewritten tail.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from contextlib import contextmanager
from typing import Any, Callable, Iterator

from action_guard_v07 import Decision, PersistentActionGuard
from checkpoint_authority import CheckpointError, CheckpointHTTPClient


class WorkflowBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class OperationReceipt:
    decision: Decision
    checkpointed: bool
    checkpoint_generation: int | None = None
    error: str | None = None


class CheckpointedWorkflow:
    """Fail-closed adapter that checkpoints every local state transition.

    It is important to route every security-relevant ledger mutation through this
    wrapper. Direct calls on the underlying guard bypass the external checkpoint
    cadence; this package labels that a caller integration error, not a safe mode.
    """

    def __init__(self, guard: PersistentActionGuard, checkpoints: CheckpointHTTPClient,
                 journal_id: str = "lycheetah-action-guard"):
        self.guard = guard
        self.checkpoints = checkpoints
        self.journal_id = journal_id
        # Serializes operations through this wrapper instance. Production still needs
        # a distributed per-journal lease/CAS when several processes are authorized.
        self._lock = RLock()

    @contextmanager
    def effect_session(self) -> Iterator[None]:
        """Hold the per-instance operation lock over claim → provider call → result."""
        with self._lock:
            yield

    @staticmethod
    def _anchor(envelope: dict[str, Any]) -> dict[str, Any]:
        return {"event_count": envelope["event_count"], "last_seq": envelope["last_seq"],
                "root_hash": envelope["root_hash"]}

    def bootstrap_empty_journal(self) -> OperationReceipt:
        """Create first external anchor only for a truly empty journal."""
        latest = self.checkpoints.get_latest(self.journal_id)
        if latest is not None:
            status = self.guard.verify_audit_chain(self._anchor(latest))
            current = self.guard.audit_anchor()
            consistency = self.guard.verify_state_consistency()
            if not status["valid"] or current != self._anchor(latest) or not consistency["valid"]:
                raise WorkflowBlocked("bootstrap_requires_synchronized_journal")
            return OperationReceipt(Decision(True, "already_bootstrapped"), True,
                                    latest["generation"])
        current = self.guard.audit_anchor()
        consistency = self.guard.verify_state_consistency()
        if not consistency["valid"]:
            raise WorkflowBlocked("refusing_to_anchor_inconsistent_operational_ledger")
        if current != {"event_count": 0, "last_seq": None,
                       "root_hash": self._genesis()}:
            raise WorkflowBlocked("refusing_to_anchor_preexisting_uncheckpointed_history")
        try:
            envelope = self.checkpoints.publish(self.journal_id, current, [])
        except CheckpointError as exc:
            return OperationReceipt(Decision(False, "checkpoint_unavailable"), False, error=str(exc))
        return OperationReceipt(Decision(True, "bootstrapped"), True, envelope["generation"])

    @staticmethod
    def _genesis() -> str:
        from action_guard_v07 import AUDIT_GENESIS
        return AUDIT_GENESIS

    def _trusted_checkpoint(self) -> dict[str, Any]:
        envelope = self.checkpoints.get_latest(self.journal_id)
        if envelope is None:
            raise WorkflowBlocked("external_checkpoint_missing")
        trusted_anchor = self._anchor(envelope)
        status = self.guard.verify_audit_chain(trusted_anchor)
        if not status["valid"]:
            raise WorkflowBlocked("audit_history_invalid_against_external_checkpoint")
        consistency = self.guard.verify_state_consistency()
        if not consistency["valid"]:
            raise WorkflowBlocked("operational_ledger_inconsistent_against_audit")
        # Prefix validity alone is not enough to extend trust automatically. If the
        # journal tail is ahead/behind the receipt, something changed without a
        # successful checkpoint; require explicit operator recovery instead of
        # automatically blessing that tail with a fresh signature.
        current = self.guard.audit_anchor()
        if current != trusted_anchor:
            raise WorkflowBlocked("journal_not_exactly_checkpointed")
        return envelope

    def _mutate_locked(self, fn: Callable[..., Any], *args: Any, claim: bool = False,
                       **kwargs: Any) -> OperationReceipt:
        try:
            current_envelope = self._trusted_checkpoint()
        except (WorkflowBlocked, CheckpointError, RuntimeError) as exc:
            return OperationReceipt(Decision(False, "workflow_blocked"), False, error=str(exc))

        if claim:
            # Re-read the externally signed checkpoint used by the guard; it is
            # signature-verified by get_latest and is exactly the current journal tail.
            # The exact-tail flag closes a race where an uncheckpointed concurrent
            # journal append could otherwise be treated as an acceptable new suffix.
            kwargs["expected_audit_anchor"] = self._anchor(current_envelope)
            kwargs["require_exact_audit_anchor"] = True
        try:
            decision = fn(*args, **kwargs)
        except Exception as exc:
            return OperationReceipt(Decision(False, "ledger_operation_error"), False, error=type(exc).__name__)

        try:
            # A mutation is not considered operationally cleared until the resulting
            # journal root has been signed and durably stored outside the guard DB.
            after = self.guard.audit_anchor()
            prior_status = self.guard.verify_audit_chain(self._anchor(current_envelope))
            if not prior_status["valid"]:
                raise WorkflowBlocked("prior_checkpoint_prefix_changed_during_mutation")
            state_status = self.guard.verify_state_consistency()
            if not state_status["valid"]:
                raise WorkflowBlocked("operational_ledger_inconsistent_after_mutation")
            delta = self.guard.audit_chain_events_after(self._anchor(current_envelope)["last_seq"])
            envelope = self.checkpoints.publish(self.journal_id, after, delta)
            if self._anchor(envelope) != after:
                raise WorkflowBlocked("checkpoint_receipt_does_not_match_journal")
            return OperationReceipt(decision, True, envelope["generation"])
        except (CheckpointError, WorkflowBlocked, RuntimeError) as exc:
            # The local mutation may have committed, but this wrapper deliberately
            # does not return an authorized-to-dispatch receipt. Subsequent operations
            # fail closed because local journal and external checkpoint diverge.
            return OperationReceipt(decision, False, error=str(exc))

    def _mutate(self, fn: Callable[..., Any], *args: Any, claim: bool = False,
                **kwargs: Any) -> OperationReceipt:
        with self._lock:
            return self._mutate_locked(fn, *args, claim=claim, **kwargs)

    def issue_approval(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.issue_approval, *args, **kwargs)

    def revoke_all(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.revoke_all, *args, **kwargs)

    def prepare_effect(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.prepare_effect, *args, **kwargs)

    def claim_dispatch(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.claim_dispatch, *args, claim=True, **kwargs)

    def record_result(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.record_result, *args, **kwargs)

    def reconcile_effect(self, *args: Any, **kwargs: Any) -> OperationReceipt:
        return self._mutate(self.guard.reconcile_effect, *args, **kwargs)

    def synchronize_status(self) -> dict[str, Any]:
        """Report whether local journal is exactly at its authenticated checkpoint."""
        with self._lock:
            try:
                envelope = self._trusted_checkpoint()
                return {"synchronized": True, "generation": envelope["generation"],
                        "event_count": envelope["event_count"], "last_seq": envelope["last_seq"]}
            except Exception as exc:
                return {"synchronized": False, "reason": str(exc)}
