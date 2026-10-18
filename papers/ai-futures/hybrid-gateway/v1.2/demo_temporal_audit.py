"""Offline synthetic history: weak latest-known baseline vs a temporal ledger.

This exercises CASCADE *adapter mechanics* using an openly declared fake engine.
Run `demo_cascade_canonical.py --framework-root ...` separately with the genuine
pinned Lycheetah repo to execute actual CASCADE code.
"""
from __future__ import annotations
import json
from dataclasses import dataclass

from hybrid_gateway import (HybridGateway, SourceDocument, ClaimProposal,
                            EvidenceWeights, TemporalCase, audit_temporal_cases,
                            public_report)


@dataclass
class FixtureBlock:
    id: str
    content: str
    domain: str
    paradigm: str
    evidence_strength: float
    explanatory_power: float
    uncertainty: float
    regime: str = 'universal'

    @property
    def pressure(self):
        return self.evidence_strength * self.explanatory_power / self.uncertainty


class FixtureEngine:
    """Declared emulation for testing the interface; NOT original CASCADE."""
    def __init__(self):
        self.blocks = []
        self.cascade_events = []

    def add_block(self, block):
        for old in self.blocks:
            if old.domain == block.domain and old.paradigm != block.paradigm and (block.pressure > old.pressure + .3):
                old.regime = 'qualified'
                self.cascade_events.append({'reason': 'stronger fictional pressure'})
        self.blocks.append(block)

    def coherence(self):
        return 1.0 if len({b.paradigm for b in self.blocks if b.regime == 'universal'}) <= 1 else .5


def main():
    g = HybridGateway()
    for cid, val, start, known, supers in (
        ('old', '14', '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z', ()),
        ('new', '30', '2026-02-01T00:00:00Z', '2026-02-03T00:00:00Z', ('old',)),
        ('disputed', '60', '2026-02-01T00:00:00Z', '2026-02-05T00:00:00Z', ()),
    ):
        src = SourceDocument('src-' + cid, 'fiction', 'urn:' + cid,
                             f'Refunds allowed within {val} days.')
        g.register_source(src)
        claim = ClaimProposal(cid, 'fiction', 'refunds', 'window_days', 'online', val,
                              start, src.source_id, src.body, supersedes=supers)
        assert g.ingest(claim, recorded_at=known, reviewer_approved=True).disposition == 'ALLOW'
    weights_a = {x: EvidenceWeights(.5, 1.5, .5) for x in ('old', 'new', 'disputed')}
    weights_b = {**weights_a, 'new': EvidenceWeights(.9, 2, .2),
                 'disputed': EvidenceWeights(.2, 1, .8)}
    cases = [TemporalCase(k, 'fiction', 'refunds', 'window_days', 'online', eff, known) for k, eff, known in (
        ('historical', '2026-01-15T00:00:00Z', '2026-03-01T00:00:00Z'),
        ('knowledge_before_revision', '2026-02-10T00:00:00Z', '2026-02-02T00:00:00Z'),
        ('revision_known', '2026-02-10T00:00:00Z', '2026-02-04T00:00:00Z'),
        ('disputed', '2026-02-10T00:00:00Z', '2026-02-06T00:00:00Z'),
    )]
    checks = audit_temporal_cases(g, cases, weight_profiles={'flat': weights_a, 'skewed': weights_b},
                                  engine_factory=FixtureEngine, block_factory=FixtureBlock)
    print(json.dumps(public_report(checks), indent=2))
    print('FIXTURE ONLY. No real model or canonical CASCADE was executed.')


if __name__ == '__main__':
    main()
