"""OPTIONAL integration smoke using the genuine external Lycheetah CASCADE classes.

Requirements: checkout a copy of Lycheetah/Lycheetah-Framework separately and pass its
root path. The script verifies the upstream file against the pinned blob SHA-1
from the 2026-10-18 linked repository inspection before executing it. It
deliberately does not vendor or replace the canonical engine.

python demo_cascade_canonical.py --framework-root ../Lycheetah-Framework

This is a diagnostic experiment with ARBITRARY sample weights, NOT calibration.
"""
import argparse

from hybrid_gateway import (SourceDocument, HybridGateway, ClaimProposal,
    refund_window_quote_validator, diagnose_with_cascade, EvidenceWeights, load_canonical_classes)


def run(framework_root):
    upstream = load_canonical_classes(framework_root)
    CascadeEngine, KnowledgeBlock = upstream.engine_factory, upstream.block_factory
    src = SourceDocument('s', 'fictional', 'urn:example', 'Refunds allowed within 14 days.')
    gateway = HybridGateway(semantic_validator=refund_window_quote_validator)
    gateway.register_source(src)
    p = ClaimProposal('c', 'fictional', 'refunds', 'window_days', 'online', '14',
                      '2026-10-01T00:00:00Z', 's', src.body)
    assert gateway.ingest(p, recorded_at='2026-10-02T00:00:00Z', reviewer_approved=True).disposition == 'ALLOW'
    head = gateway.head_digest
    result = diagnose_with_cascade(gateway, tenant='fictional', subject='refunds',
        predicate='window_days', scope='online', effective_at='2026-10-04T00:00:00Z',
        known_at='2026-10-04T00:00:00Z',
        calibrated_weights={'c': EvidenceWeights(0.6, 1.5, 0.3)},
        engine_factory=CascadeEngine, block_factory=KnowledgeBlock)
    assert result.claim_ids == ('c',)
    assert gateway.head_digest == head
    assert gateway.verify_chain(anchored_head=head)
    print('CANONICAL_SMOKE_PASSED:', result)
    print('PINNED_CANONICAL_GIT_BLOB:', upstream.blob_sha)
    print('WARNING: these weights are illustrative, not calibrated.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--framework-root', required=True)
    args = parser.parse_args()
    run(args.framework_root)
