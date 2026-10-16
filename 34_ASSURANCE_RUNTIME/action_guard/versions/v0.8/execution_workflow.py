"""End-to-end checkpoint-gated simulation. Provider effects are synthetic only."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from action_guard_v07 import Decision, FakeMergeProvider
from checkpointed_workflow import CheckpointedWorkflow, OperationReceipt
from github_rest_adapter import build_merge_request


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    reason: str
    provider_called: bool
    decision: Decision | None = None
    checkpointed: bool = False
    request_preview: dict[str, Any] | None = None
    provider_result: dict[str, Any] | None = None


class SimulatedMergeExecutor:
    """Run the guard around a synthetic provider, never around live GitHub.

    The request preview mirrors the documented GitHub REST merge request. The fake
    provider enforces expected head/base SHA and records a simulated merge in memory.
    """
    def __init__(self, workflow: CheckpointedWorkflow, provider: FakeMergeProvider,
                 repo: str, pull_request: int):
        self.workflow = workflow
        self.provider = provider
        self.repo = repo
        self.pull_request = pull_request

    def execute(self, effect_id: str, now: int) -> ExecutionResult:
        # The same wrapper lock spans the claim, provider operation and local result
        # checkpoint. This is process-local; multi-process callers need a distributed
        # lease/CAS or single-writer service, which is explicitly not implemented here.
        with self.workflow.effect_session():
            try:
                current_action = self.provider.read_action(self.repo, self.pull_request)
            except Exception:
                return ExecutionResult("BLOCKED", "provider_state_unavailable", False)
            claim = self.workflow.claim_dispatch(effect_id, now, current_action)
            if not claim.checkpointed:
                return ExecutionResult("BLOCKED", claim.error or "checkpoint_not_confirmed", False,
                                       claim.decision, False)
            if not claim.decision.allowed:
                return ExecutionResult("DENIED", claim.decision.reason, False,
                                       claim.decision, True)
            action = claim.decision.action
            try:
                preview = build_merge_request(action)
                response = self.provider.merge(action, effect_id)
            except TimeoutError:
                unknown = self.workflow.record_result(effect_id, now + 1, "unknown",
                                                      {"reason": "provider_timeout_after_dispatch_attempt"})
                return ExecutionResult("UNKNOWN", "provider_timeout_requires_reconciliation", True,
                                       claim.decision, unknown.checkpointed,
                                       provider_result={"status": "unknown"})
            except Exception as exc:
                failed = self.workflow.record_result(effect_id, now + 1, "unknown",
                                                     {"reason": "provider_exception", "exception_type": type(exc).__name__})
                return ExecutionResult("UNKNOWN", "provider_exception_requires_reconciliation", True,
                                       claim.decision, failed.checkpointed,
                                       provider_result={"status": "unknown"})

            outcome = "success" if response.get("status") == "success" else "failure"
            recorded = self.workflow.record_result(effect_id, now + 1, outcome, response)
            if not recorded.checkpointed:
                return ExecutionResult("EFFECT_RESULT_UNCHECKPOINTED", "external_checkpoint_unavailable_after_provider_result",
                                       True, claim.decision, False,
                                       {"method": preview.method, "url": preview.url,
                                        "headers": preview.headers, "json_body": preview.json_body}, response)
            return ExecutionResult("SUCCEEDED" if outcome == "success" else "FAILED",
                                   response.get("reason", outcome), True, claim.decision, True,
                                   {"method": preview.method, "url": preview.url,
                                    "headers": preview.headers, "json_body": preview.json_body}, response)
