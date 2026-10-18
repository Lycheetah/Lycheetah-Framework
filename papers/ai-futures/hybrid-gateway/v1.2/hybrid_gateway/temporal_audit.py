"""Bitemporal ledger versus explicitly weaker baseline, with CASCADE diagnostics.

No LLM inference, no automatic trust, no inferred weights. This harness intentionally
surfaces CASCADE sensitivity to heuristic calibration without giving it authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping

from .core import HybridGateway, utc
from .cascade_bridge import EvidenceWeights, diagnose_with_cascade, gateway_snapshot_digest


@dataclass(frozen=True)
class TemporalCase:
    case_id: str
    tenant: str
    subject: str
    predicate: str
    scope: str
    effective_at: str
    known_at: str

    def __post_init__(self):
        if any(not isinstance(getattr(self, k), str) or not getattr(self, k) for k in
               ('case_id', 'tenant', 'subject', 'predicate', 'scope')):
            raise ValueError('case identity required')
        utc(self.effective_at)
        utc(self.known_at)


@dataclass(frozen=True)
class CaseAudit:
    case_id: str
    ledger_disposition: str
    ledger_value: str | None
    latest_known_value: str | None
    baseline_matches_ledger: bool
    citation_count: int
    cascade_event_counts: tuple[tuple[str, int], ...]
    cascade_coherences: tuple[tuple[str, float | None], ...]
    cascade_changed_across_profiles: bool
    warning: str = 'CASCADE is an advisory score on visible survivors, NOT a competing policy answer'


def naive_latest_known(gateway: HybridGateway, case: TemporalCase) -> str | None:
    """Deliberately weak baseline: newest admitted claim, ignores valid-time and withdrawal.

    Still honors tenant and exact scope. Tie-break by claim_id for reproducibility.
    This is *not* state-of-the-art temporal RAG. It exists to expose regressions.
    """
    known = utc(case.known_at)
    relevant = [c for c in gateway.claims.values() if
                (c.tenant, c.subject, c.predicate, c.scope) ==
                (case.tenant, case.subject, case.predicate, case.scope) and
                gateway.admitted_at[c.claim_id] <= known]
    if not relevant:
        return None
    return max(relevant, key=lambda c: (gateway.admitted_at[c.claim_id], c.claim_id)).value


def audit_temporal_cases(gateway: HybridGateway, cases: list[TemporalCase], *,
                         weight_profiles: Mapping[str, Mapping[str, EvidenceWeights]],
                         engine_factory: Callable, block_factory: Callable) -> tuple[CaseAudit, ...]:
    """Collect diagnostics across *caller-supplied* calibration profiles.

    All read-only checks are integrity snapshots, not process isolation. A malicious
    injected factory could still mutate gateway state before the check fails.
    """
    if not cases or len({c.case_id for c in cases}) != len(cases):
        raise ValueError('cases must be nonempty with unique IDs')
    if not weight_profiles or any(not name or not isinstance(name, str) for name in weight_profiles):
        raise ValueError('at least one named profile required')
    if any(not isinstance(c, TemporalCase) for c in cases):
        raise TypeError('cases must be TemporalCase instances')
    before = gateway_snapshot_digest(gateway)
    head = gateway.head_digest
    rows = []
    for case in cases:
        q = gateway.query(tenant=case.tenant, subject=case.subject,
                          predicate=case.predicate, scope=case.scope,
                          effective_at=case.effective_at, known_at=case.known_at)
        baseline = naive_latest_known(gateway, case)
        results = []
        for name, weights in sorted(weight_profiles.items()):
            diag = diagnose_with_cascade(gateway,
                tenant=case.tenant, subject=case.subject, predicate=case.predicate,
                scope=case.scope, effective_at=case.effective_at,
                known_at=case.known_at, calibrated_weights=weights,
                engine_factory=engine_factory, block_factory=block_factory)
            if tuple(x['claim_id'] for x in q.citations) != diag.claim_ids:
                raise RuntimeError('CASCADE and ledger citation identity drift')
            results.append((name, diag.event_count, diag.diagnostic_coherence))
        changed = len({(events, coherence) for _, events, coherence in results}) > 1
        rows.append(CaseAudit(case.case_id, q.disposition, q.value, baseline,
                    baseline == q.value, len(q.citations),
                    tuple((name, events) for name, events, _ in results),
                    tuple((name, coherence) for name, _, coherence in results), changed))
    if gateway.head_digest != head or gateway_snapshot_digest(gateway) != before:
        raise RuntimeError('audit changed ledger state')
    return tuple(rows)


def public_report(audits: tuple[CaseAudit, ...]) -> dict:
    """Privacy-minimised report: strips values, quotes, cases IDs, source/tenant metadata."""
    return {
        'cases': len(audits),
        'baseline_matches': sum(r.baseline_matches_ledger for r in audits),
        'baseline_mismatches': sum(not r.baseline_matches_ledger for r in audits),
        'cascade_profile_sensitive': sum(r.cascade_changed_across_profiles for r in audits),
        'abstentions': sum(r.ledger_disposition != 'ANSWER' for r in audits),
        'rows': [{'index': i, 'ledger_disposition': r.ledger_disposition,
                  'baseline_matches_ledger': r.baseline_matches_ledger,
                  'citation_count': r.citation_count,
                  'cascade_changed_across_profiles': r.cascade_changed_across_profiles} 
                 for i, r in enumerate(audits)],
        'claim': 'Internal fixture comparison; not neural-model accuracy, not independent evaluation.'
    }
