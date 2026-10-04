#!/usr/bin/env python3
"""Practical provider adapter for the v0.8 shared resource ledger.

The adapter deliberately treats transport/provider uncertainty as a retained
reservation. Retrying an UNKNOWN effect does not invoke the provider again until
an external reconciliation step resolves the prior attempt.
"""
from dataclasses import dataclass
from typing import Callable, Optional

from resource_ledger import SharedResourceLedger, BudgetDecision


@dataclass(frozen=True)
class ProviderOutcome:
    state: str  # CONFIRMED | CERTIFIED_NO_EFFECT | UNKNOWN
    actual_cost: int | None = None
    receipt: str | None = None


@dataclass(frozen=True)
class BudgetedCallResult:
    state: str
    reason: str
    budget: BudgetDecision
    provider_receipt: str | None = None


def budgeted_call(
    ledger: SharedResourceLedger,
    account_id: str,
    broker_id: str,
    effect_id: str,
    max_cost: int,
    provider_call: Callable[[], ProviderOutcome],
) -> BudgetedCallResult:
    reservation = ledger.reserve(account_id, broker_id, effect_id, max_cost)

    # A prior unresolved/settled/released effect is not permission to invoke the
    # provider again. The caller must reconcile or accept the prior terminal state.
    if reservation.state == "DENY":
        return BudgetedCallResult("DENY", reservation.reason, reservation)
    if reservation.state == "UNKNOWN":
        return BudgetedCallResult(
            "PENDING", "prior-outcome-unresolved-no-retry", reservation
        )
    if reservation.state == "SETTLED":
        return BudgetedCallResult(
            "CONFIRMED", "already-settled-no-retry", reservation
        )
    if reservation.state == "RELEASED":
        return BudgetedCallResult(
            "NO_EFFECT", "already-certified-no-effect", reservation
        )
    if reservation.state != "RESERVED":
        return BudgetedCallResult(
            "INDETERMINATE", "unexpected-reservation-state", reservation
        )

    # Distinguish a fresh reservation from an idempotent retry that still has a
    # RESERVED record. If the effect existed before this call, reserve() returns
    # existing-reservation; do not blind-retry an already released request.
    if reservation.reason == "existing-reservation":
        pending = ledger.mark_unknown(effect_id)
        return BudgetedCallResult(
            "PENDING", "existing-reservation-requires-reconciliation", pending
        )

    try:
        outcome = provider_call()
    except Exception:
        pending = ledger.mark_unknown(effect_id)
        return BudgetedCallResult(
            "PENDING", "provider-exception-outcome-unknown", pending
        )

    if outcome.state == "CONFIRMED":
        if outcome.actual_cost is None:
            pending = ledger.mark_unknown(effect_id)
            return BudgetedCallResult(
                "PENDING", "confirmed-without-cost-unresolved", pending,
                outcome.receipt,
            )
        settled = ledger.settle(effect_id, outcome.actual_cost)
        if settled.state == "SETTLED":
            return BudgetedCallResult(
                "CONFIRMED", "provider-effect-settled", settled,
                outcome.receipt,
            )
        return BudgetedCallResult(
            settled.state, settled.reason, settled, outcome.receipt
        )

    if outcome.state == "CERTIFIED_NO_EFFECT":
        released = ledger.release_no_effect(effect_id)
        return BudgetedCallResult(
            "NO_EFFECT", "provider-certified-no-effect", released,
            outcome.receipt,
        )

    pending = ledger.mark_unknown(effect_id)
    return BudgetedCallResult(
        "PENDING", "provider-outcome-unknown", pending, outcome.receipt
    )


def reconcile_budgeted_effect(
    ledger: SharedResourceLedger,
    effect_id: str,
    outcome: ProviderOutcome,
) -> BudgetedCallResult:
    row = ledger.reservation(effect_id)
    if row is None:
        raise KeyError(effect_id)

    if outcome.state == "CONFIRMED":
        if outcome.actual_cost is None:
            pending = ledger.mark_unknown(effect_id)
            return BudgetedCallResult(
                "PENDING", "reconciliation-missing-cost", pending,
                outcome.receipt,
            )
        settled = ledger.settle(effect_id, outcome.actual_cost)
        return BudgetedCallResult(
            "CONFIRMED" if settled.state == "SETTLED" else settled.state,
            "reconciled-confirmed-effect" if settled.state == "SETTLED" else settled.reason,
            settled,
            outcome.receipt,
        )

    if outcome.state == "CERTIFIED_NO_EFFECT":
        released = ledger.release_no_effect(effect_id)
        return BudgetedCallResult(
            "NO_EFFECT", "reconciled-certified-no-effect", released,
            outcome.receipt,
        )

    pending = ledger.mark_unknown(effect_id)
    return BudgetedCallResult(
        "PENDING", "reconciliation-still-unknown", pending,
        outcome.receipt,
    )
