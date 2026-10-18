"""Adversarial CONFORMANCE probe, NOT independent document-extraction accuracy.

Every case and its label is authored for this protocol. Comparator asks whether
legacy v0.4 staging *accepted* a batch (including empty and duplicates), versus
v0.5 coverage audit readiness. Both still need trusted reviewer approval.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import replace, asdict
from hybrid_gateway import (
    SourceDocument, ClaimProposal, HybridGateway, ScriptedNeuralAdapter,
    TrustedClause, TrustedContractRegistry, ContractedHybridPipeline,
    CoverageAuditor, ExtractionPlan,
)

DATE = '2026-10-01T00:00:00Z'
SOURCE = SourceDocument('fictional-policy', 'fictional-shop', 'urn:fictional:policy',
    'Refunds allowed within 14 days. Loyalty members earn 21 points per order. '
    'EXAMPLE ONLY: Refunds allowed within 60 days. '
    'Refunds not allowed within 90 days. Online orders: refunds within 10 days.')
CLAUSES = [
    TrustedClause(SOURCE.source_id, SOURCE.digest, SOURCE.tenant, 'refunds',
        'window_days', 'in_store', 'Refunds allowed within 14 days.', 'refund_days_v1', DATE),
    TrustedClause(SOURCE.source_id, SOURCE.digest, SOURCE.tenant, 'loyalty',
        'points_per_order', 'members', 'Loyalty members earn 21 points per order.', 'loyalty_points_v1', DATE),
]


def propose(which, claim_id):
    if which == 'refund':
        c = CLAUSES[0]
    elif which == 'loyalty':
        c = CLAUSES[1]
    else:
        raise ValueError(which)
    return ClaimProposal(claim_id, SOURCE.tenant, c.subject, c.predicate, c.scope,
        c.parsed_value, DATE, SOURCE.source_id, c.exact_quote)


def cases():
    """Four families * 8 cases, including subtypes; deterministic no RNG."""
    out=[]
    variations=['base','renamed','both','reversed','subplan_refund','subplan_loyalty','empty_plan','reordered']
    for i, v in enumerate(variations):
        if v == 'subplan_refund':
            required=('refund',); vals=['refund']
        elif v == 'subplan_loyalty':
            required=('loyalty',); vals=['loyalty']
        elif v == 'empty_plan':
            required=(); vals=[]
        else:
            required=('refund','loyalty'); vals=['refund','loyalty']
        if v in ('reversed','reordered'):
            vals=vals[::-1]
        out.append({'id':f'complete_{v}', 'family':'complete', 'selected':required,
            'candidates':[propose(x,f'{i}-{n}') for n,x in enumerate(vals)], 'should_ready': True})
    missing_variations=['no_values','refund_missing','loyalty_missing','missing_both','omit_only','omit_refund','omit_loyalty','subplan_empty']
    for i,v in enumerate(missing_variations):
        required=('refund','loyalty')
        vals=([] if v in ('no_values','missing_both') else
              ['loyalty'] if v in ('refund_missing','omit_refund') else
              ['refund'])
        if v=='subplan_empty':required=('refund',); vals=[]
        out.append({'id':f'missing_{v}', 'family':'missing', 'selected':required,
            'candidates':[propose(x,f'm{i}-{n}') for n,x in enumerate(vals)], 'should_ready':False})
    for i in range(8):
        vals=['refund','loyalty']+(['refund'] if i%2==0 else ['loyalty'])
        if i%4==3: vals.append('refund')
        out.append({'id':f'duplicate_{i}', 'family':'duplicate', 'selected':('refund','loyalty'),
            'candidates':[propose(x,f'd{i}-{n}') for n,x in enumerate(vals)], 'should_ready':False})
    for i in range(8):
        candidates=[propose('refund',f'x{i}-0'),propose('loyalty',f'x{i}-1')]
        evil=propose('refund',f'x{i}-evil')
        mods=[{'value':'60','evidence_quote':'Refunds allowed within 60 days.'},
              {'value':'90','evidence_quote':'Refunds not allowed within 90 days.'},
              {'value':'21','evidence_quote':'Loyalty members earn 21 points per order.'},
              {'tenant':'other-tenant'}, {'scope':'online'},
              {'valid_from':'2026-09-01T00:00:00Z'},
              {'supersedes':('not-approved',)}, {'source_id':'other-source'}]
        candidates.append(replace(evil, **mods[i]))
        out.append({'id':f'extra_{i}', 'family':'unexpected', 'selected':('refund','loyalty'),
           'candidates':candidates, 'should_ready':False})
    return out


def evaluate():
    evaluated=[]
    for row in cases():
        registry=TrustedContractRegistry([SOURCE], CLAUSES)
        gateway=HybridGateway(semantic_validator=registry.validate_claim)
        gateway.register_source(SOURCE)
        adapter=ScriptedNeuralAdapter('not-a-model',{SOURCE.source_id:row['candidates']})
        legacy=ContractedHybridPipeline(gateway,adapter,registry)
        try:
            legacy.stage(SOURCE)
            old_accepted=True
        except (ValueError, TypeError):
            old_accepted=False
        required_map={'refund':CLAUSES[0].fingerprint,'loyalty':CLAUSES[1].fingerprint}
        plan=ExtractionPlan.create(registry,SOURCE.source_id,
                                    selected=tuple(required_map[v] for v in row['selected']))
        new=CoverageAuditor(gateway,adapter,registry,plan).audit(SOURCE)
        now_ready=new.receipt.disposition=='READY_FOR_REVIEW'
        assert now_ready==row['should_ready'], row['id']
        assert gateway.head_digest is None
        evaluated.append({'id':row['id'],'family':row['family'], 'expected_plan_complete':row['should_ready'],
                          'legacy_staging_accepted':old_accepted,
                          'v05_ready_for_review':now_ready,
                          'v05_disposition':new.receipt.disposition})
    groups={}
    for f in ('complete','missing','duplicate','unexpected'):
        group=[r for r in evaluated if r['family']==f]
        groups[f]={'n':len(group),'legacy_accepted':sum(r['legacy_staging_accepted'] for r in group),
                   'v05_ready':sum(r['v05_ready_for_review'] for r in group)}
    return {'method':'author-constructed contract-conformance exercise, not a model quality eval',
            'version':'v0.5','case_count':len(evaluated),'group_summary':groups,
            'cases':evaluated}

if __name__=='__main__':
    output=evaluate()
    file=Path(__file__).resolve().parent/'results'/'coverage_eval_v0.5.json'
    file.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'case_count':output['case_count'],'group_summary':output['group_summary']},indent=2))
    print('results: '+str(file))
