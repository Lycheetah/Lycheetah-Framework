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

import re
import secrets
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
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

# The approver recorded when policy allows an action without review.
AUTO_ALLOW_APPROVER = "policy_auto_allow"

ResultStatus = Literal["SUCCEEDED", "FAILED", "UNKNOWN", "DENIED", "BLOCKED"]
_OUTCOME_STATUS: dict[str, Literal["SUCCEEDED", "FAILED", "UNKNOWN"]] = {
    "success": "SUCCEEDED",
    "failure": "FAILED",
    "unknown": "UNKNOWN",
}
_SETTLED_STATUS: dict[str, ResultStatus] = {"SUCCEEDED": "SUCCEEDED", "FAILED": "FAILED"}


_FORK_BOMB = re.compile(r"([\w:]+)\(\)\{\1\|\1&\};\1")
_WIPE_TARGET = ("/", "~", "$home", "${home}")


def _command_texts(value: Any) -> list[str]:
    """Every string in an action, plus each list joined as one command line."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for key, item in value.items() for text in (str(key), *_command_texts(item))]
    if isinstance(value, (list, tuple)):
        joined = " ".join(str(item) for item in value)
        return [text for item in value for text in _command_texts(item)] + [joined]
    return []


def _destructive_command(action: dict[str, Any]) -> bool:
    """A tripwire for spelled-out wipes, not a sandbox.

    It catches a recursive ``rm`` of an absolute or home path in any flag order,
    and a fork bomb in any spacing. An encoded, scripted or aliased command
    passes it; the policy's tool allowlist is the control.
    """
    for text in _command_texts(action):
        lowered = text.lower()
        if _FORK_BOMB.search("".join(lowered.split())):
            return True
        for segment in re.split(r"[;&|\n]+", lowered):
            tokens = [token.strip("'\"") for token in segment.split()]
            for index, token in enumerate(tokens):
                if token != "rm" and not token.endswith("/rm"):
                    continue
                recursive = wipe = options_ended = False
                for argument in tokens[index + 1 :]:
                    if not options_ended and argument == "--":
                        options_ended = True
                    elif not options_ended and argument.startswith("--"):
                        recursive = recursive or argument == "--recursive"
                    elif not options_ended and argument.startswith("-") and len(argument) > 1:
                        recursive = recursive or "r" in argument[1:]
                    elif argument.startswith(_WIPE_TARGET):
                        wipe = True
                if recursive and wipe:
                    return True
    return False


def _declared_approver(approver_id: Any) -> str | None:
    """A blank name or the auto-allow marker is no approver, at propose and dispatch alike."""
    if not isinstance(approver_id, str) or not approver_id.strip():
        return None
    return None if approver_id == AUTO_ALLOW_APPROVER else approver_id


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

    status: ResultStatus
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
        """Create a local gateway using embedded file stores.

        The ledger, the checkpoint history and the signing key all live under
        ``base_dir``. The signed checkpoint catches a damaged or rolled-back
        ledger, but a writer who can change the whole directory can roll the
        ledger and its checkpoints back together and replay a finished effect.
        Where that writer is in the threat model, run the authority in another
        process or host (``make_server``) and pass a ``CheckpointHTTPClient``.
        """
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
        # Static tripwire for spelled-out destructive commands; see _destructive_command.
        if _destructive_command(action):
            control = ControlReference(
                framework="SYSTEM_INTEGRITY",
                control_id="LYCHEETAH-01",
                title="Destructive Command Prohibition",
            )
            finding = Finding.create(
                finding_id="destructive_command_prohibited",
                title="Destructive Command Prohibited",
                description="Detected a recursive removal of an absolute or home path, "
                "or a fork bomb",
                severity=Severity.CRITICAL,
                requested_disposition=Disposition.BLOCK,
                claim_status=ClaimStatus.ACTIVE,
                deterministic=True,
                evaluator="ActionGatewayStaticRule",
                controls=(control,),
            )
            return Disposition.BLOCK, (finding,)

        event = self._tool_event(action, scope, approver_id)
        receipt = self.runtime.evaluate(event)
        return receipt.decision, receipt.findings

    @staticmethod
    def _tool_event(action: dict[str, Any], scope: str, approver_id: str | None) -> AssuranceEvent:
        """Use the same declared tool subject for policy evaluation and receipts."""
        return AssuranceEvent(
            phase=Phase.TOOL,
            tool_name=str(action.get("tool", action.get("name", "generic_tool"))),
            tool_arguments=action,
            scopes=(scope,) if scope else (),
            side_effect=bool(action.get("side_effect", False)),
            human_approved=True if _declared_approver(approver_id) is not None else None,
        )

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
        approver_id = _declared_approver(approver_id)
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
        # Default ids are unique per proposal. Deriving them from the action,
        # actor and wall-clock second made two legitimate proposals of one
        # action in the same second collide, and the second was refused.
        aid = approval_id or f"app-{secrets.token_hex(8)}"
        eid = effect_id or f"eff-{secrets.token_hex(8)}"
        approver = approver_id or AUTO_ALLOW_APPROVER

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
                # Names the earlier effect an operator must reconcile first.
                effect_id=(
                    prepared.effect_id if prepared.reason == "prior_effect_unresolved" else None
                ),
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
        approver_id = _declared_approver(approval["approver_id"]) if approval is not None else None
        evaluated_policy = self.policy
        policy_record = {
            "id": evaluated_policy.policy_id,
            "version": evaluated_policy.version,
            "sha256": evaluated_policy.digest,
        }
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

        # Snapshot the evaluated event before the callback can update policy.
        # This retains the runtime's subject hashing, replay and privacy rules.
        event_record = self.runtime._event_record(
            self._tool_event(intended_action, effect["scope"], approver_id)
        )
        event_record.update(
            {
                "scope": effect["scope"],
                "actor": effect["actor"],
                "action_hash": digest,
                "approver_id": approver_id,
            }
        )

        # Execute the tool
        provider_called = True
        try:
            raw_result = executor()
            # Only an explicit "failure" is a known failure. Any other answer
            # ("pending", "accepted", a typo) may have taken effect.
            reported = raw_result.get("status")
            outcome: Literal["success", "failure", "unknown"] = (
                reported if reported in ("success", "failure") else "unknown"
            )
            status_text = _OUTCOME_STATUS[outcome]
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

        # A policy decision and a provider outcome answer different questions.
        # Keep the evaluated decision; execution_status records what happened.
        receipt = AssuranceReceipt.issue(
            runtime={
                "name": "lycheetah-action-gateway",
                "version": ASSURANCE_VERSION,
                "status": ClaimStatus.ACTIVE.value,
            },
            policy=policy_record,
            event=event_record,
            decision=disposition,
            findings=policy_findings,
            metrics={
                "effect_id": effect_id,
                "execution_status": status_text,
                "checkpoint_generation": final_cp.get("generation"),
                "checkpoint_envelope_hash": final_cp.get("envelope_hash"),
            },
            # The runtime's caveats (approval is caller-declared, an unsealed
            # digest is not authentication) hold for this receipt too.
            limitations=(
                *self.runtime._limitations(event_record),
                "local_execution_cell_boundary",
            ),
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

    def reconcile(
        self,
        effect_id: str,
        outcome: Literal["success", "failure"],
        evidence: dict[str, Any],
    ) -> ExecutionResult:
        """Settle an UNKNOWN or interrupted effect from an authoritative provider read.

        Until this runs, the guard refuses to prepare the same action again.
        """
        with self.workflow.effect_session():
            effect = self.guard.get_effect(effect_id)
            digest = effect["action_hash"] if effect is not None else ""
            try:
                settled = self.workflow.reconcile_effect(
                    effect_id, int(time.time()), outcome, evidence
                )
            except (WorkflowBlocked, CheckpointError) as exc:
                return ExecutionResult(
                    status="BLOCKED",
                    reason=str(exc),
                    effect_id=effect_id,
                    action_hash=digest,
                    provider_called=False,
                )
        decision = settled.decision
        status: ResultStatus
        if not settled.checkpointed:
            status, reason = "UNKNOWN", "reconciliation_not_checkpointed"
        elif not decision.allowed:
            status, reason = "DENIED", decision.reason
        else:
            # The guard settles only to SUCCEEDED or FAILED; anything else stays unknown.
            status, reason = _SETTLED_STATUS.get(decision.status or "", "UNKNOWN"), "reconciled"
        return ExecutionResult(
            status=status,
            reason=reason,
            effect_id=effect_id,
            action_hash=digest,
            provider_called=False,
            result=evidence if decision.allowed else None,
            checkpoint_generation=settled.checkpoint_generation,
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
