"""Lycheetah Action Gateway — high-level execution airlock for autonomous AI agents.

Binds agent tool execution to:
1. Evidence-capped policy evaluation (ALLOW / REVIEW / BLOCK).
2. Durable SQLite state machine (PREPARED -> DISPATCHING -> SUCCEEDED / FAILED / UNKNOWN).
3. Monotonic Ed25519-signed external checkpoints.
4. Tamper-evident Assurance Receipts.

Mutations use the checkpoint-gated workflow and reject uncheckpointed history.
Dispatch re-evaluates the current policy and records that evaluated policy even
if a later callback changes it. Approval identities remain caller-supplied
metadata; this gateway does not authenticate a human or bind an arbitrary Python
executor's implementation to an action description.
"""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from .action_guard import PersistentActionGuard, action_digest
from .checkpoint_authority import (
    CheckpointError,
    CheckpointHTTPClient,
    CheckpointStore,
)
from .checkpointed_workflow import CheckpointedWorkflow, WorkflowBlocked
from .models import (
    AssuranceEvent,
    ClaimStatus,
    ControlReference,
    Disposition,
    Finding,
    Phase,
    Severity,
)
from .policy import AssurancePolicy, default_policy
from .receipt import AssuranceReceipt
from .runtime import ASSURANCE_VERSION, AssuranceRuntime


@dataclass(frozen=True)
class GateDecision:
    """Decision produced when an agent proposes an action."""

    allowed: bool
    disposition: Disposition
    reason: str
    action_hash: str
    approval_id: str | None = None
    effect_id: str | None = None
    findings: tuple[Finding, ...] = ()
    checkpoint_generation: int | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Outcome of a dispatched tool action."""

    status: Literal["SUCCEEDED", "FAILED", "UNKNOWN", "DENIED", "BLOCKED"]
    reason: str
    effect_id: str | None
    action_hash: str
    provider_called: bool
    result: dict[str, Any] | None = None
    receipt: AssuranceReceipt | None = None
    checkpoint_generation: int | None = None


class CommandExecutor:
    """Safely executes an OS command with timeouts and output capture."""

    def __init__(
        self,
        command: list[str] | str,
        timeout: float = 30.0,
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
    ):
        self.command = command
        self.timeout = timeout
        self.cwd = str(cwd) if cwd is not None else None
        self.env = env

    def __call__(self) -> dict[str, Any]:
        shell = isinstance(self.command, str)
        proc = subprocess.run(
            self.command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            cwd=self.cwd,
            env=self.env,
        )
        return {
            "status": "success" if proc.returncode == 0 else "failure",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


class ActionGateway:
    """Unified action execution gateway integrating policy, checkpoints, and durable state."""

    def __init__(
        self,
        guard: PersistentActionGuard,
        checkpoints: CheckpointHTTPClient | CheckpointStore,
        journal_id: str = "lycheetah-action-gateway",
        policy: AssurancePolicy | None = None,
    ):
        self.guard = guard
        self.checkpoints = checkpoints
        self.journal_id = journal_id
        self.runtime = AssuranceRuntime(policy=policy or default_policy())
        self.workflow = CheckpointedWorkflow(guard, checkpoints, journal_id)

    @property
    def policy(self) -> AssurancePolicy:
        """The policy used by the evaluator, rather than a second mutable copy."""
        return self.runtime.policy

    @policy.setter
    def policy(self, value: AssurancePolicy) -> None:
        if not isinstance(value, AssurancePolicy):
            raise TypeError("policy must be an AssurancePolicy")
        with self.workflow.effect_session():
            self.runtime.policy = value

    @classmethod
    def open_local(
        cls,
        base_dir: str | Path,
        journal_id: str = "lycheetah-action-gateway",
        policy: AssurancePolicy | None = None,
    ) -> ActionGateway:
        """Create a local gateway using embedded file stores."""
        root = Path(base_dir)
        guard_db = root / "ledger" / "guard.sqlite3"
        auth_db = root / "authority" / "authority.sqlite3"
        key_path = root / "authority" / "ed25519-private.pem"
        guard = PersistentActionGuard(guard_db)
        store = CheckpointStore(auth_db, key_path)
        gw = cls(guard, store, journal_id=journal_id, policy=policy)
        gw.bootstrap()
        return gw

    def _get_latest_checkpoint(self) -> dict[str, Any] | None:
        if isinstance(self.checkpoints, CheckpointHTTPClient):
            return self.checkpoints.get_latest(self.journal_id)
        return self.checkpoints.latest(self.journal_id)

    def bootstrap(self) -> dict[str, Any]:
        """Anchor genesis or verify an existing journal without trusting a dirty tail."""
        result = self.workflow.bootstrap_empty_journal()
        if not result.checkpointed or not result.decision.allowed:
            raise RuntimeError("checkpoint bootstrap failed")
        latest = self._get_latest_checkpoint()
        if latest is None:
            raise RuntimeError("checkpoint missing after bootstrap")
        return latest

    def _sync_checkpoint(self) -> dict[str, Any]:
        """Verify synchronization; never publish previously uncheckpointed history."""
        return self.workflow._trusted_checkpoint()

    def evaluate_policy(
        self,
        action: dict[str, Any],
        scope: str,
        actor: str,
        approver_id: str | None = None,
    ) -> tuple[Disposition, tuple[Finding, ...]]:
        """Evaluate action dictionary against versioned assurance policy."""
        # The policy evaluates action/scope; this argument is API metadata and
        # does not authenticate an identity. Keep the keyword-compatible API.
        _ = actor
        # Static check for destructive system commands
        cmd_val = action.get("command", "")
        if isinstance(cmd_val, list):
            cmd_flat = " ".join(str(c) for c in cmd_val).lower()
        else:
            cmd_flat = str(cmd_val).lower()
        action_str = json.dumps(action).lower() + " " + cmd_flat
        if "rm -rf /" in action_str or ":(){ :|:& };:" in action_str:
            control = ControlReference(
                framework="SYSTEM_INTEGRITY",
                control_id="LYCHEETAH-01",
                title="Destructive Command Prohibition",
            )
            finding = Finding.create(
                finding_id="destructive_command_prohibited",
                title="Destructive Command Prohibited",
                description="Detected destructive system wipe command sequence",
                severity=Severity.CRITICAL,
                requested_disposition=Disposition.BLOCK,
                claim_status=ClaimStatus.ACTIVE,
                deterministic=True,
                evaluator="ActionGatewayStaticRule",
                controls=(control,),
            )
            return Disposition.BLOCK, (finding,)

        tool_name = str(action.get("tool", action.get("name", "generic_tool")))
        scopes_tuple = (scope,) if scope else ()
        side_effect = bool(action.get("side_effect", False))
        human_approved = True if approver_id is not None else None
        event = AssuranceEvent(
            phase=Phase.TOOL,
            tool_name=tool_name,
            tool_arguments=action,
            scopes=scopes_tuple,
            side_effect=side_effect,
            human_approved=human_approved,
        )
        receipt = self.runtime.evaluate(event)
        return receipt.decision, receipt.findings

    def propose(
        self,
        action: dict[str, Any],
        actor: str,
        scope: str,
        approver_id: str | None = None,
        ttl_seconds: int = 300,
        approval_id: str | None = None,
        effect_id: str | None = None,
    ) -> GateDecision:
        """Propose an action: check policy, register single-use approval, prepare effect."""
        with self.workflow.effect_session():
            try:
                self._sync_checkpoint()
                return self._propose_locked(
                    action, actor, scope, approver_id, ttl_seconds, approval_id, effect_id
                )
            except (WorkflowBlocked, CheckpointError) as exc:
                return GateDecision(
                    allowed=False,
                    disposition=Disposition.BLOCK,
                    reason=str(exc),
                    action_hash=action_digest(action),
                )

    def _propose_locked(
        self,
        action: dict[str, Any],
        actor: str,
        scope: str,
        approver_id: str | None,
        ttl_seconds: int,
        approval_id: str | None,
        effect_id: str | None,
    ) -> GateDecision:
        digest = action_digest(action)
        disposition, findings = self.evaluate_policy(action, scope, actor, approver_id=approver_id)

        if disposition == Disposition.BLOCK:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason="policy_blocked",
                action_hash=digest,
                findings=findings,
            )

        if disposition == Disposition.REVIEW and approver_id is None:
            return GateDecision(
                allowed=False,
                disposition=Disposition.REVIEW,
                reason="human_approval_required",
                action_hash=digest,
                findings=findings,
            )

        now = int(time.time())
        aid = approval_id or f"app-{sha256(f'{digest}:{now}:{actor}'.encode()).hexdigest()[:16]}"
        eid = effect_id or f"eff-{sha256(f'{aid}:{now}'.encode()).hexdigest()[:16]}"
        approver = approver_id or "policy_auto_allow"

        approval = self.workflow.issue_approval(
            approval_id=aid,
            actor=actor,
            approver_id=approver,
            action=action,
            scope=scope,
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        decision = approval.decision
        if not approval.checkpointed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason="checkpoint_unavailable",
                action_hash=digest,
                approval_id=aid,
            )
        if not decision.allowed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason=decision.reason,
                action_hash=digest,
            )

        preparation = self.workflow.prepare_effect(
            effect_id=eid,
            approval_id=aid,
            actor=actor,
            action=action,
            scope=scope,
            now=now,
        )
        prepared = preparation.decision
        if not preparation.checkpointed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason="checkpoint_unavailable",
                action_hash=digest,
                approval_id=aid,
                effect_id=eid,
            )
        if not prepared.allowed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason=prepared.reason,
                action_hash=digest,
                approval_id=aid,
            )

        return GateDecision(
            allowed=True,
            disposition=disposition,
            reason="prepared",
            action_hash=digest,
            approval_id=aid,
            effect_id=eid,
            findings=findings,
            checkpoint_generation=preparation.checkpoint_generation,
        )

    def dispatch(
        self,
        effect_id: str,
        executor: Callable[[], dict[str, Any]],
        current_action: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """Linearize dispatch, execute tool, record outcome, and mint assurance receipt."""
        with self.workflow.effect_session():
            return self._dispatch_locked(effect_id, executor, current_action)

    def _dispatch_locked(
        self,
        effect_id: str,
        executor: Callable[[], dict[str, Any]],
        current_action: dict[str, Any] | None,
    ) -> ExecutionResult:
        effect = self.guard.get_effect(effect_id)
        if effect is None:
            return ExecutionResult(
                status="BLOCKED",
                reason="effect_not_found",
                effect_id=effect_id,
                action_hash="",
                provider_called=False,
            )

        intended_action = effect["action"]
        live_action = intended_action if current_action is None else current_action
        digest = effect["action_hash"]
        now = int(time.time())

        try:
            self._sync_checkpoint()
        except (WorkflowBlocked, CheckpointError) as exc:
            return ExecutionResult(
                status="BLOCKED",
                reason=str(exc),
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )

        approval = self.guard.get_approval(effect["approval_id"])
        approver_id = (
            approval["approver_id"]
            if approval is not None and approval["approver_id"] != "policy_auto_allow"
            else None
        )
        evaluated_policy = self.policy
        disposition, policy_findings = self.evaluate_policy(
            intended_action, effect["scope"], effect["actor"], approver_id
        )
        if disposition == Disposition.BLOCK or (
            disposition == Disposition.REVIEW and approver_id is None
        ):
            return ExecutionResult(
                status="DENIED",
                reason=(
                    "policy_blocked"
                    if disposition == Disposition.BLOCK
                    else "human_approval_required"
                ),
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )

        try:
            claim = self.workflow.claim_dispatch(effect_id, now, live_action)
        except (WorkflowBlocked, CheckpointError) as exc:
            return ExecutionResult(
                status="BLOCKED",
                reason=str(exc),
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )
        if not claim.decision.allowed or not claim.checkpointed:
            return ExecutionResult(
                status="DENIED",
                reason=claim.decision.reason if claim.checkpointed else "checkpoint_unavailable",
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )

        # Execute the tool
        provider_called = True
        try:
            raw_result = executor()
            outcome: Literal["success", "failure", "unknown"] = (
                "success" if raw_result.get("status") == "success" else "failure"
            )
            status_text: Literal["SUCCEEDED", "FAILED", "UNKNOWN"] = (
                "SUCCEEDED" if outcome == "success" else "FAILED"
            )
            result_details = raw_result
        except TimeoutError:
            outcome = "unknown"
            status_text = "UNKNOWN"
            result_details = {"error": "executor_timeout_requires_reconciliation"}
        except Exception as exc:
            outcome = "unknown"
            status_text = "UNKNOWN"
            result_details = {
                "error": "executor_exception_requires_reconciliation",
                "exception": str(exc),
            }

        try:
            recording = self.workflow.record_result(
                effect_id=effect_id,
                now=int(time.time()),
                outcome=outcome,
                details=result_details,
            )
            if not recording.checkpointed or not recording.decision.allowed:
                raise WorkflowBlocked("result_not_checkpointed_requires_reconciliation")
            final_cp = self._sync_checkpoint()
        except (WorkflowBlocked, CheckpointError) as exc:
            return ExecutionResult(
                status="UNKNOWN",
                reason=str(exc),
                effect_id=effect_id,
                action_hash=digest,
                provider_called=True,
                result=result_details,
            )

        disposition = (
            Disposition.ALLOW
            if status_text == "SUCCEEDED"
            else (Disposition.REVIEW if status_text == "UNKNOWN" else Disposition.BLOCK)
        )
        receipt = AssuranceReceipt.issue(
            runtime={
                "name": "lycheetah-action-gateway",
                "version": ASSURANCE_VERSION,
                "status": ClaimStatus.ACTIVE.value,
            },
            policy={
                "id": evaluated_policy.policy_id,
                "version": evaluated_policy.version,
                "sha256": evaluated_policy.digest,
            },
            event={
                "phase": Phase.TOOL.value,
                "tool_name": str(intended_action.get("tool", "tool")),
                "scope": effect["scope"],
                "side_effect": True,
                "actor": effect["actor"],
                "human_approved": approver_id is not None,
            },
            decision=disposition,
            findings=policy_findings,
            metrics={
                "effect_id": effect_id,
                "execution_status": status_text,
                "checkpoint_generation": final_cp.get("generation"),
                "checkpoint_envelope_hash": final_cp.get("envelope_hash"),
            },
            limitations=("local_execution_cell_boundary",),
            trace_id=f"gw-{effect_id}",
        )

        return ExecutionResult(
            status=status_text,
            reason=recording.decision.reason if status_text != "UNKNOWN" else "uncertain_outcome",
            effect_id=effect_id,
            action_hash=digest,
            provider_called=provider_called,
            result=result_details,
            receipt=receipt,
            checkpoint_generation=final_cp.get("generation"),
        )

    def execute(
        self,
        action: dict[str, Any],
        actor: str,
        scope: str,
        executor: Callable[[], dict[str, Any]],
        approver_id: str | None = None,
    ) -> ExecutionResult:
        """One-shot helper: propose, gate, dispatch, and witness."""
        gate = self.propose(action, actor, scope, approver_id=approver_id)
        if not gate.allowed:
            return ExecutionResult(
                status="DENIED" if gate.disposition == Disposition.REVIEW else "BLOCKED",
                reason=gate.reason,
                effect_id=gate.effect_id,
                action_hash=gate.action_hash,
                provider_called=False,
            )
        assert gate.effect_id is not None
        return self.dispatch(gate.effect_id, executor, current_action=action)
