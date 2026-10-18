"""Earned Trust Cycle 001: synthetic, executable TOCTOU control comparison.

NOT a replica or benchmark of the Lycheetah runtime; tests a narrowly specified
reference contract inspired by its FinalityGate/ActionGuard.  No actual external
API is called.  Standard library only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from collections import Counter
from typing import Optional


def digest(obj: object) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Action:
    subject: str = 'ORDER-001'
    amount_cents: int = 5000
    effect_id: str = 'refund-001'

    @property
    def hash(self) -> str:
        return digest({'subject': self.subject, 'amount_cents': self.amount_cents,
                       'effect_id': self.effect_id})


@dataclass
class World:
    eligible: Optional[bool] = True
    actual_eligible: bool = True  # independent modeled ground truth, may differ from records
    evidence_subject: str = 'ORDER-001'
    evidence_version: int = 1
    max_refund_cents: int = 10000
    policy_version: int = 1
    approved_hash: str = ''
    approval_expires: int = 10
    clock: int = 0
    applied: set[str] | None = None
    effects: int = 0

    def __post_init__(self):
        if self.applied is None:
            self.applied = set()

    def current_permission(self, action: Action) -> bool:
        """Independent outcome oracle: exact authority and live subject state."""
        return (self.approved_hash == action.hash
                and self.clock < self.approval_expires
                and self.eligible is True
                and self.evidence_subject == action.subject
                and 0 < action.amount_cents <= self.max_refund_cents
                and action.effect_id not in self.applied)

    def truth_permission(self, action: Action) -> bool:
        """Oracle is deliberately distinct from records the controls can read."""
        return self.actual_eligible and self.current_permission(action)

    def read_snapshot(self, action: Action):
        if not self.current_permission(action):
            return None
        return (action.hash, self.policy_version, self.evidence_version)

    def unsafe_apply(self, action: Action) -> None:
        """Intentionally unsafe provider: applies any received request."""
        self.applied.add(action.effect_id)
        self.effects += 1

    def conditional_commit(self, action: Action) -> bool:
        """Simulated atomic provider enforcement: predicate checked with write.

        This represents a capability ASSUMPTION, not something ordinary refund
        APIs necessarily supply. In a real system, the provider would need to
        own or authenticate the approval and policy state as well as the order.
        """
        if not self.current_permission(action):
            return False
        # One indivisible transaction in the *simulator*.
        self.applied.add(action.effect_id)
        self.effects += 1
        return True


@dataclass(frozen=True)
class Scenario:
    name: str
    mutation: str
    when: str  # 'admission_to_finality', or 'finality_to_commit', or 'none'


MUTATIONS = (
    'eligibility_revoked', 'policy_lowered', 'action_amount_changed',
    'approval_revoked', 'approval_expired', 'already_processed',
    'evidence_subject_swapped', 'evidence_deleted', 'evidence_lies',
)

SCENARIOS = (
    Scenario('stable_eligible', 'none', 'none'),
    Scenario('benign_evidence_revision', 'benign_revision', 'admission_to_finality'),
    *(Scenario(f'{m}_between_admission_finality', m, 'admission_to_finality') for m in MUTATIONS),
    *(Scenario(f'{m}_between_finality_commit', m, 'finality_to_commit') for m in MUTATIONS),
)


def mutate(world: World, action: Action, mutation: str) -> Action:
    if mutation == 'none':
        pass
    elif mutation == 'benign_revision':
        world.evidence_version += 1  # still eligible: SUBJECT_STATUS semantics
    elif mutation == 'eligibility_revoked':
        world.eligible = False
        world.evidence_version += 1
    elif mutation == 'policy_lowered':
        world.max_refund_cents = 1000
        world.policy_version += 1
    elif mutation == 'action_amount_changed':
        action = replace(action, amount_cents=9000)  # under old cap, not approved
    elif mutation == 'approval_revoked':
        world.approved_hash = 'REVOKED'
    elif mutation == 'approval_expired':
        world.clock = 20
    elif mutation == 'already_processed':
        world.applied.add(action.effect_id)  # preexisting external effect
    elif mutation == 'evidence_subject_swapped':
        world.evidence_subject = 'OTHER-ORDER'
        world.evidence_version += 1
    elif mutation == 'evidence_deleted':
        world.eligible = None
        world.evidence_version += 1
    elif mutation == 'evidence_lies':
        world.actual_eligible = False  # source remains PASS, a trusted-source failure
    else:
        raise ValueError(mutation)
    return action


def finality_ready(world: World, action: Action, admitted: tuple | None) -> bool:
    if admitted is None:
        return False
    # A normalized miniature of the proposal: exact action, current permission,
    # policy version pinned, and current evidence predicate, not exact revision.
    action_hash, admitted_policy_version, _ = admitted
    return (action.hash == action_hash and
            world.policy_version == admitted_policy_version and
            world.current_permission(action))


@dataclass(frozen=True)
class Observation:
    case: str
    strategy: str
    safe_at_commit: bool
    performed: bool
    correct: bool
    reason: str


STRATEGIES = ('admission_only', 'finality_recheck', 'conditional_provider',
              'conventional_atomic')


def run_one(case: Scenario, strategy: str) -> Observation:
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    w, action = World(), Action()
    w.approved_hash = action.hash
    admission = w.read_snapshot(action)
    assert admission is not None

    if case.when == 'admission_to_finality':
        action = mutate(w, action, case.mutation)
    w.clock = max(1, w.clock)

    if strategy == 'admission_only':
        ready = admission is not None
    else:
        ready = finality_ready(w, action, admission)

    if case.when == 'finality_to_commit':
        action = mutate(w, action, case.mutation)
    w.clock = max(2, w.clock)

    # Independent oracle is read exactly at modeled execution boundary.
    safe = w.truth_permission(action)
    if not ready:
        performed, reason = False, 'paused_at_finality'
    elif strategy in ('conditional_provider', 'conventional_atomic'):
        performed = w.conditional_commit(action)
        reason = 'conditional_committed' if performed else 'conditional_rejected'
    else:
        w.unsafe_apply(action)
        performed, reason = True, 'unconditional_provider_commit'
    return Observation(case.name, strategy, safe, performed, safe == performed, reason)


def audit_chain_verify(events: list[dict]) -> bool:
    prev = digest({'genesis': 'earned-trust-001'})
    for event in events:
        body = {'case': event['case'], 'strategy': event['strategy'],
                'performed': event['performed'], 'prev': prev}
        if event['prev'] != prev or event['sha256'] != digest(body):
            return False
        prev = event['sha256']
    return True


def audit_chain(observations: list[Observation]) -> list[dict]:
    prev = digest({'genesis': 'earned-trust-001'})
    events = []
    for o in observations:
        body = {'case': o.case, 'strategy': o.strategy,
                'performed': o.performed, 'prev': prev}
        h = digest(body)
        events.append({**body, 'sha256': h})
        prev = h
    return events


def run_all() -> dict:
    observations = [run_one(case, strategy)
                    for case in SCENARIOS for strategy in STRATEGIES]
    aggregate = {}
    for strategy in STRATEGIES:
        rows = [o for o in observations if o.strategy == strategy]
        aggregate[strategy] = {
            'cases': len(rows),
            'correct_decisions': sum(o.correct for o in rows),
            'unsafe_effects': sum(o.performed and not o.safe_at_commit for o in rows),
            'missed_authorized_effects': sum((not o.performed) and o.safe_at_commit for o in rows),
            'executed': sum(o.performed for o in rows),
        }
    chain = audit_chain(observations)
    return {
        'status': 'SYNTHETIC_REFERENCE_MODEL_NOT_REAL_LYCHEETAH_RUNTIME',
        'description': 'single-threaded atomic-provider assumption; 20 scenarios x 4 strategies, including false evidence',
        'scenario_count': len(SCENARIOS),
        'observation_count': len(observations),
        'results': aggregate,
        'rows': [vars(o) for o in observations],
        'audit_chain_valid': audit_chain_verify(chain),
        'audit_chain': chain,
    }


if __name__ == '__main__':
    print(json.dumps(run_all(), indent=2))
