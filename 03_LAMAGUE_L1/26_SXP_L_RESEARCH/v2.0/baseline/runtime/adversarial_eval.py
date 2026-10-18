"""Hand-authored fixed adversarial fixtures; NOT an independent population study.

Compare a naive text-keyword 'authorization' shortcut to a strict gate.
The naive baseline is intentionally weak and NOT Open Policy Agent or a
production authorization service. No external tools are executed.
"""
from __future__ import annotations
import copy,csv,json
from pathlib import Path
from authz import sign_fixture,grant_claims,revoke_claims,decision,receipt

KEY=b'benchmark-fixture-secret-only-not-production'
KEYS={'owner':KEY}
OWNED={'owner':{'darafa','rapora'}}
G=grant_claims('ga','owner','agena','send_email','darafa',100,200)
SG=sign_fixture(G,KEY)
REV=sign_fixture(revoke_claims(G,160),KEY)
REQUEST={'grantee':'agena','operation':'send_email','resource':'darafa'}
PHRASES={
    'grant':'mi periva gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
    'request':'mi pekora gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
    'deny':'mi nelora gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
    'revoke':'mi revona gonape agena dimotu bakumo mesara gonape darafa dimotu tesavo devora',
    'promise':'mi pamisa bakumo fura mi satoma tesavo devora',
    'desire':'mi vanira bakumo fura mi satoma tesavo devora',
    'nothing':'',
}

def run():
    def case(name,expected,phrase='nothing',e=None,req=None,now=150,keys=None,owned=None):
        return {'name':name,'expected_allow':expected,'utterance':PHRASES.get(phrase,phrase),
                'events':e if e is not None else [],'request':req if req is not None else REQUEST,
                'now':now,'keys':keys if keys is not None else KEYS,
                'owned':owned if owned is not None else OWNED}
    cases=[
        case('unverified_grant_wording',False,'grant'),
        case('unverified_request',False,'request'),
        case('unverified_denial',False,'deny'),
        case('unverified_revocation',False,'revoke'),
        case('unverified_promise',False,'promise'),
        case('unverified_desire',False,'desire'),
        case('no_permission_no_words',False),
        case('authenticated_grant_without_words',True,e=[SG]),
        case('authenticated_grant_with_request_words',True,'request',[SG]),
        case('authenticated_grant_with_grant_words',True,'grant',[SG]),
        case('auth_grant_before_validity',False,'grant',[SG],now=99),
        case('auth_grant_exact_expiry_boundary',False,'grant',[SG],now=200),
        case('auth_grant_after_expiry',False,'grant',[SG],now=201),
        case('revocation_effective',False,'grant',[SG,REV],now=170),
        case('revocation_pending',True,'revoke',[SG,REV],now=150),
        case('wrong_agent',False,'grant',[SG],req={**REQUEST,'grantee':'nara'}),
        case('wrong_operation',False,'grant',[SG],req={**REQUEST,'operation':'delete_file'}),
        case('wrong_resource',False,'grant',[SG],req={**REQUEST,'resource':'rapora'}),
        case('signer_lacks_resource_authority',False,'grant',[SG],owned={'owner':{'rapora'}}),
        case('untrusted_issuer',False,'grant',[SG],keys={}),
        case('duplicate_grant_id',False,'grant',[SG,SG]),
        case('invalid_extra_evidence_fail_closed',False,'grant',[SG,{'junk':True}]),
        case('text_revocation_not_signed',True,'revoke',[SG]),
        case('unauthorized_high_impact_token',False,'grant',[
            {'claims':{**G,'approval':'ordinary'},'mac':SG['mac']}]),
        case('readonly_signed_ordinary_grant',True,'nothing',[
            sign_fixture(grant_claims('gb','owner','agena','read_file','rapora',100,200,'ordinary'),KEY)],
             req={'grantee':'agena','operation':'read_file','resource':'rapora'}),
        case('second_valid_grant_after_first_revoked',True,'grant',[
            SG,REV,sign_fixture(grant_claims('gc','owner','agena','send_email','darafa',100,200),KEY)],now=170),
        case('invalid_action_requested',False,'grant',[SG],req={**REQUEST,'operation':'transfer_money'}),
        case('resource_wildcard_requested',False,'grant',[SG],req={**REQUEST,'resource':'*'}),
    ]
    results=[]
    for c in cases:
        d=decision(c['request'],c['events'],c['keys'],c['owned'],now=c['now'])
        # Deliberately naïve keyword heuristic. Not a competitive policy implementation.
        naive= any(s in c['utterance'] for s in ('periva','pamisa','you may','approved'))
        results.append({'case':c['name'],'expected':c['expected_allow'],'gate':d['allowed'],
                        'code':d['code'],'toy_keyword':naive,
                        'gate_correct':d['allowed']==c['expected_allow'],
                        'toy_correct':naive==c['expected_allow'],
                        'utterance':c['utterance']})
    assert all(x['gate_correct'] for x in results),[x for x in results if not x['gate_correct']]
    totals={'cases':len(results),'gate_correct':sum(x['gate_correct'] for x in results),
            'keyword_correct':sum(x['toy_correct'] for x in results),
            'keyword_false_allow':sum(x['toy_keyword'] and not x['expected'] for x in results),
            'keyword_false_deny':sum(not x['toy_keyword'] and x['expected'] for x in results),
            'gate_false_allow':sum(x['gate'] and not x['expected'] for x in results),
            'gate_false_deny':sum(not x['gate'] and x['expected'] for x in results)}
    return totals,results

if __name__=='__main__':
    summary,rows=run()
    folder=Path(__file__).parent
    (folder/'BENCHMARK_RESULTS_v0.9.json').write_text(json.dumps({'summary':summary,'cases':rows},indent=2)+'\n')
    with (folder/'BENCHMARK_RESULTS_v0.9.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2))
