"""Optional v0.8 subprocess smoke against a checked-out canonical engine.

Usage: python demo_cascade_isolated.py --framework-root /path/to/Lycheetah-Framework
Requires NumPy in local Python, and the pinned canonical Git blob from 2026-10-18.
A local checkout trusted by its operator is NOT supplied in the ZIP.
"""
import argparse
import json
from dataclasses import asdict
from hybrid_gateway.core import HybridGateway,SourceDocument,ClaimProposal
from hybrid_gateway.cascade_bridge import EvidenceWeights
from hybrid_gateway.isolated_cascade import diagnose_isolated


def run(root):
    g=HybridGateway()
    source=SourceDocument('fictional-s','fictional','urn:fictional','Refunds allowed within 14 days.')
    g.register_source(source)
    p=ClaimProposal('fictional-c','fictional','refunds','window_days','online','14',
                    '2026-10-01T00:00:00Z',source.source_id,source.body)
    assert g.ingest(p,recorded_at='2026-10-02T00:00:00Z',reviewer_approved=True).disposition=='ALLOW'
    head=g.head_digest
    result=diagnose_isolated(g,tenant='fictional',subject='refunds',predicate='window_days',
                 scope='online', effective_at='2026-10-04T00:00:00Z',known_at='2026-10-04T00:00:00Z',
                 calibrated_weights={'fictional-c':EvidenceWeights(.6,1.5,.3)},framework_root=root)
    assert g.head_digest==head and g.verify_chain(anchored_head=head)
    print(json.dumps({'canonical_loaded_in_child':True,'subprocess_boundary':True,
                     'diagnostic':asdict(result),'calibration':'ILLUSTRATIVE, NOT VALIDATED'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework-root',required=True)
    args=parser.parse_args()
    run(args.framework_root)
