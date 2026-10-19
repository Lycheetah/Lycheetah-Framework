"""Forge IV exploratory agency-preservation model.

No claim that these proxies measure philosophical free will, human flourishing,
or actual ability without task-specific empirical calibration. The engine only
computes an observable frontier of *claimed* potential outcomes and NEVER acts.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class FutureOutcome:
    label: str
    family: str                 # equivalent results should share a family
    personal_value: float      # user-provided task-specific value, not model-inferred
    effort: float              # user-estimated accessible effort units
    minimum_skill: int
    independently_possible: bool
    verified: bool             # evidence gate, not a truth oracle

@dataclass(frozen=True)
class Candidate:
    name: str
    immediate_value: float
    skill_after: int
    futures: tuple[FutureOutcome, ...]
    exit_cost: float
    reversal_verified: bool
    authorized: bool
    duration: float

@dataclass(frozen=True)
class Context:
    min_value: float
    effort_budget: float
    deadline: float

@dataclass(frozen=True)
class Assessment:
    name: str
    immediate_value: float
    meaningful_outcomes: int
    independent_outcomes: int
    exit_cost: float
    reversal_verified: bool


def assess(candidate: Candidate, ctx: Context) -> Assessment:
    # Count distinct outcome equivalence families, not UI buttons.
    # Only include options that are evidenced, affordable, skilled and valuable.
    by_family: dict[str, FutureOutcome] = {}
    for f in candidate.futures:
        if (not f.verified or f.personal_value < ctx.min_value or
            f.effort > ctx.effort_budget or f.minimum_skill > candidate.skill_after):
            continue
        previous = by_family.get(f.family)
        if previous is None or (f.independently_possible and not previous.independently_possible):
            by_family[f.family] = f
    return Assessment(candidate.name, candidate.immediate_value,
                      len(by_family), sum(f.independently_possible for f in by_family.values()),
                      candidate.exit_cost, candidate.reversal_verified)


def eligible(c: Candidate, ctx: Context) -> bool:
    return c.authorized and c.duration <= ctx.deadline


def dominates(a: Assessment, b: Assessment) -> bool:
    # Multiple dimensions deliberately retained; no fabricated universal score.
    ge = (a.immediate_value >= b.immediate_value and
          a.meaningful_outcomes >= b.meaningful_outcomes and
          a.independent_outcomes >= b.independent_outcomes and
          a.exit_cost <= b.exit_cost and
          int(a.reversal_verified) >= int(b.reversal_verified))
    strict = (a.immediate_value > b.immediate_value or
              a.meaningful_outcomes > b.meaningful_outcomes or
              a.independent_outcomes > b.independent_outcomes or
              a.exit_cost < b.exit_cost or
              int(a.reversal_verified) > int(b.reversal_verified))
    return ge and strict


def compare(candidates: Iterable[Candidate], ctx: Context) -> dict:
    """Present allowed tradeoffs; do not authorize, execute, or pick for person."""
    permitted = [c for c in candidates if eligible(c, ctx)]
    if not permitted:
        return {'myopic_pick': None, 'frontier': [], 'assessments': [], 'human_decision_required': True}
    measures = [assess(c, ctx) for c in permitted]
    myopic = max(measures, key=lambda a: a.immediate_value).name
    front = [a.name for a in measures if not any(dominates(b, a) for b in measures if b is not a)]
    return {
        'myopic_pick': myopic,
        'frontier': front,
        'assessments': [a.__dict__ for a in measures],
        'human_decision_required': True,
    }
