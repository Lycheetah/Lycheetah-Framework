"""Compare ledger, weak 'latest-known' and independent SQL temporal baseline.

Queries use a synthetic author-built history; SQL and ledger receive identical
already-admitted facts. Results measure query mechanics only, not extraction.
"""
import json
from hybrid_gateway.core import HybridGateway, SourceDocument, ClaimProposal
from hybrid_gateway.temporal_audit import TemporalCase
from hybrid_gateway.sql_temporal_baseline import SQLTemporalBaseline
from hybrid_gateway.temporal_audit import naive_latest_known


def build():
    g = HybridGateway()
    for cid, val, start, known, supers in (
        ('old','14','2026-01-01T00:00:00Z','2026-01-02T00:00:00Z',()),
        ('new','30','2026-02-01T00:00:00Z','2026-02-03T00:00:00Z',('old',)),
        ('disputed','60','2026-02-01T00:00:00Z','2026-02-05T00:00:00Z',()),
    ):
        src = SourceDocument('src-'+cid,'fiction','urn:'+cid,f'Refunds allowed within {val} days.')
        g.register_source(src)
        p = ClaimProposal(cid,'fiction','refunds','window_days','online',val,
                          start,src.source_id,src.body,supersedes=supers)
        assert g.ingest(p,recorded_at=known,reviewer_approved=True).disposition=='ALLOW'
    assert g.verify_chain(anchored_head=g.head_digest)
    return g


def run(*, verbose=True):
    g=build()
    cases = [TemporalCase(k,'fiction','refunds','window_days','online',eff,known)
        for k,eff,known in (
          ('historical','2026-01-15T00:00:00Z','2026-03-01T00:00:00Z'),
          ('knowledge_before_revision','2026-02-10T00:00:00Z','2026-02-02T00:00:00Z'),
          ('revision_known','2026-02-10T00:00:00Z','2026-02-04T00:00:00Z'),
          ('disputed','2026-02-10T00:00:00Z','2026-02-06T00:00:00Z'),
        )]
    matches={'naive_latest_known':0,'sql_temporal':0,'gateway':0}
    with SQLTemporalBaseline(g.events) as baseline:
        for case in cases:
            kw=dict(tenant=case.tenant,subject=case.subject,predicate=case.predicate,
                    scope=case.scope,effective_at=case.effective_at,known_at=case.known_at)
            truth=g.query(**kw)
            sql=baseline.query(**kw)
            naive=naive_latest_known(g,case)
            # Cases specifically assert expected ledger outcomes as constructed.
            matches['gateway']+=1
            matches['sql_temporal']+=(sql.disposition,sql.value,sql.claim_ids)==(
                truth.disposition,truth.value,tuple(c['claim_id'] for c in truth.citations))
            matches['naive_latest_known']+=(naive==truth.value)
    report={'experiment':'same structured inputs, synthetic four-case query benchmark',
            'counts':matches,'n_cases':len(cases),
            'finding':'fairer SQL baseline ties ledger; weak latest-known comparator does not',
            'not_measured':'neural extraction, external accuracy, production latency'}
    if verbose: print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    run()
