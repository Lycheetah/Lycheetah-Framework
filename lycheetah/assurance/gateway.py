"""Lycheetah Action Gateway — high-level execution airlock for autonomous AI agents.

Binds agent tool execution to:
1. Evidence-capped policy evaluation (ALLOW / REVIEW / BLOCK).
2. Durable SQLite state machine (PREPARED -> DISPATCHING -> COMMITTED / FAILED / UNKNOWN).
3. Monotonic Ed25519-signed external checkpoints.
4. Tamper-evident Assurance Receipts.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Literal

from .action_guard import Decision, PersistentActionGuard, action_digest, canonical_action
from .checkpoint_authority import (
    CHECKPOINT_GENESIS,
    CheckpointError,
    CheckpointHTTPClient,
    CheckpointStore,
)
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
        self.policy = policy or default_policy()
        self.runtime = AssuranceRuntime(policy=self.policy)

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

    def _publish_checkpoint(
        self, anchor: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if isinstance(self.checkpoints, CheckpointHTTPClient):
            return self.checkpoints.publish(self.journal_id, anchor, events)
        return self.checkpoints.store(self.journal_id, anchor, events)

    def bootstrap(self) -> dict[str, Any]:
        """Ensure the journal is anchored at genesis."""
        latest = self._get_latest_checkpoint()
        if latest is not None:
            return latest
        current = self.guard.audit_anchor()
        if current["event_count"] != 0:
            raise RuntimeError("cannot bootstrap preexisting uncheckpointed audit history")
        return self._publish_checkpoint(current, [])

    def _sync_checkpoint(self) -> dict[str, Any]:
        latest = self._get_latest_checkpoint()
        if latest is None:
            raise RuntimeError("checkpoint authority missing initial anchor")
        last_seq = latest.get("last_seq")
        new_events = self.guard.audit_chain_events_after(last_seq)
        if not new_events:
            return latest
        new_anchor = self.guard.audit_anchor()
        return self._publish_checkpoint(new_anchor, new_events)

    def evaluate_policy(
        self,
        action: dict[str, Any],
        scope: str,
        actor: str,
        approver_id: str | None = None,
    ) -> tuple[Disposition, tuple[Finding, ...]]:
        """Evaluate action dictionary against versioned assurance policy."""
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
        digest = action_digest(action)
        disposition, findings = self.evaluate_policy(
            action, scope, actor, approver_id=approver_id
        )

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

        decision = self.guard.issue_approval(
            approval_id=aid,
            actor=actor,
            approver_id=approver,
            action=action,
            scope=scope,
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        if not decision.allowed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason=decision.reason,
                action_hash=digest,
            )

        prepared = self.guard.prepare_effect(
            effect_id=eid,
            approval_id=aid,
            actor=actor,
            action=action,
            scope=scope,
            now=now,
        )
        if not prepared.allowed:
            return GateDecision(
                allowed=False,
                disposition=Disposition.BLOCK,
                reason=prepared.reason,
                action_hash=digest,
                approval_id=aid,
            )

        checkpoint = self._sync_checkpoint()
        return GateDecision(
            allowed=True,
            disposition=disposition,
            reason="prepared",
            action_hash=digest,
            approval_id=aid,
            effect_id=eid,
            findings=findings,
            checkpoint_generation=checkpoint.get("generation"),
        )

    def dispatch(
        self,
        effect_id: str,
        executor: Callable[[], dict[str, Any]],
        current_action: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """Linearize dispatch, execute tool, record outcome, and mint assurance receipt."""
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
        live_action = current_action or intended_action
        digest = effect["action_hash"]
        now = int(time.time())

        latest_cp = self._get_latest_checkpoint()
        if latest_cp is None:
            return ExecutionResult(
                status="BLOCKED",
                reason="checkpoint_missing",
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )

        claim_decision = self.guard.claim_dispatch(
            effect_id=effect_id,
            now=now,
            current_action=live_action,
            expected_audit_anchor={
                "event_count": latest_cp["event_count"],
                "last_seq": latest_cp["last_seq"],
                "root_hash": latest_cp["root_hash"],
            },
        )
        if not claim_decision.allowed:
            return ExecutionResult(
                status="DENIED",
                reason=claim_decision.reason,
                effect_id=effect_id,
                action_hash=digest,
                provider_called=False,
            )

        # Checkpoint the claimed dispatch state
        self._sync_checkpoint()

        # Execute the tool
        provider_called = True
        try:
            raw_result = executor()
            outcome: Literal["success", "failure"] = (
                "success" if raw_result.get("status") == "success" else "failure"
            )
            status_text: Literal["SUCCEEDED", "FAILED"] = (
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

        rec_decision = self.guard.record_result(
            effect_id=effect_id,
            now=int(time.time()),
            outcome=outcome,
            details=result_details,
        )
        final_cp = self._sync_checkpoint()

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
                "id": self.policy.policy_id,
                "version": self.policy.version,
                "sha256": self.policy.digest,
            },
            event={
                "phase": Phase.TOOL.value,
                "tool_name": str(intended_action.get("tool", "tool")),
                "scope": effect["scope"],
                "side_effect": True,
                "actor": effect["actor"],
            },
            decision=disposition,
            findings=(),
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
            reason=rec_decision.reason if status_text != "UNKNOWN" else "uncertain_outcome",
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
