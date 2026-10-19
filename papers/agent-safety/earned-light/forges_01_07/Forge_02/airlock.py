"""Minimal simulated side-effect boundary for EAC experiments.

For integrating with Lycheetah's real SovereignExecutionHarness:
 - Require EAC proof before issue_permit, and verify again directly at the
   actual effect boundary inside the gateway, not merely in an agent prompt.
 - Keep SovereignExecutionHarness' own scope/hash/nonce/state checks.
 - Do NOT use this small wrapper as a replacement for the real gateway.
"""
from collections.abc import Callable, Sequence
from typing import Any
from earned_authority import Decision, EarnedAuthorityGate, Grant, OriginProof, Request


class AuthorityRejected(PermissionError):
    def __init__(self, decision: Decision) -> None:
        self.decision = decision
        super().__init__(decision.code)


def evaluate_then_invoke(gate: EarnedAuthorityGate,
                         request: Request, grant: Grant | None,
                         proofs: Sequence[OriginProof], *, now: int,
                         effect: Callable[[], Any]) -> tuple[Decision, Any]:
    """Research-only, synchronous mock effect boundary; raises on deny.

    In a deployed system the execution adapter must be sole effect path and
    revocation/state check must be atomic with effect claims where possible.
    """
    decision = gate.evaluate(request, grant, proofs, now=now)
    if not decision.allowed:
        raise AuthorityRejected(decision)
    return decision, effect()
