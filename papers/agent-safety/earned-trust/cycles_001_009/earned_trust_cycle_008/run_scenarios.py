"""Fixed, labelled synthetic challenge matrix for EARNED TRUST C008."""
import json
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

from lab_fixture import ACTION,authority,provider,setup_effect
from upstream_dispatch_fence import _ClosingConnection

CASES=[
    ('valid_reservation','NORMAL'),
    ('challenge_precedes_reservation','STOP'),
    ('fresh_witness_still_challenged','STOP'),
    ('unrelated_challenge_cached_witness','STOP'),
    ('unrelated_challenge_refreshed_witness','NORMAL'),
    ('revoked_actor','STOP'),
    ('expired_approval','STOP'),
    ('changed_evidence','STOP'),
    ('changed_subject','STOP'),
    ('changed_action_amount','STOP'),
    ('tampered_witness','STOP'),
    ('duplicate_reservation','STOP'),
    ('crash_after_reservation_no_provider_effect','UNKNOWN'),
    ('lost_response_after_provider_commit','CONFIRMED'),
    ('missing_provider_observation','UNKNOWN'),
    ('forged_success_receipt','STOP'),
    ('wrong_key_provider_receipt','STOP'),
    ('materialized_state_rewind','STOP'),
    ('challenge_after_reservation','NOT_RETROACTIVE'),
    ('false_trusted_evidence','FALSE_EVIDENCE_PASSED'),
    ('direct_provider_bypass','BYPASS'),
    ('external_registry_challenge_not_relayed','SPLIT_STORE_GAP'),
]

def run_one(case_id, root):
    f=authority(root/'auth.db');p=provider(root/'provider.db');w=setup_effect(f)
    eid='effect-001'
    if case_id=='valid_reservation':
        return 'NORMAL' if f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    if case_id in ('challenge_precedes_reservation','fresh_witness_still_challenged'):
        b=f.challenge_body('crm','nonce-1');assert f.challenge(b,f.sign_challenge(b))
        if case_id=='fresh_witness_still_challenged':w=f.witness(eid)
        return 'STOP' if not f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    if case_id.startswith('unrelated_challenge'):
        b=f.challenge_body('merchant','nonce-1');assert f.challenge(b,f.sign_challenge(b))
        if case_id=='unrelated_challenge_refreshed_witness':w=f.witness(eid)
        return 'NORMAL' if f.reserve_send(eid,ACTION,w,50).allowed else 'STOP'
    if case_id=='revoked_actor':f.revoke('agent')
    elif case_id=='expired_approval': return 'STOP' if not f.reserve_send(eid,ACTION,w,10000).allowed else 'ERROR'
    elif case_id=='changed_evidence':f.update_evidence('eligibility',2,'FAIL',ACTION['subject'])
    elif case_id=='changed_subject': return 'STOP' if not f.reserve_send(eid,dict(ACTION,subject='wrong'),w,50).allowed else 'ERROR'
    elif case_id=='changed_action_amount': return 'STOP' if not f.reserve_send(eid,dict(ACTION,refund_cents=5000),w,50).allowed else 'ERROR'
    elif case_id=='tampered_witness':w['seal']='0'*64
    elif case_id=='duplicate_reservation':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        return 'STOP' if not f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    elif case_id=='crash_after_reservation_no_provider_effect':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        assert f.recover()==1
        return 'UNKNOWN' if f.state_pair(eid)['outbox']['state']=='UNKNOWN' and p.lookup(eid) is None else 'ERROR'
    elif case_id=='lost_response_after_provider_commit':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        p.apply(eid,ACTION)
        assert f.recover()==1
        return 'CONFIRMED' if f.acknowledge(eid,p.lookup(eid)) else 'ERROR'
    elif case_id=='missing_provider_observation':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        f.recover()
        return 'UNKNOWN' if p.lookup(eid) is None and f.state_pair(eid)['effect']=='UNKNOWN' else 'ERROR'
    elif case_id=='forged_success_receipt':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        return 'STOP' if not f.acknowledge(eid,{'effect_id':eid,'outcome':'SUCCEEDED'}) else 'ERROR'
    elif case_id=='wrong_key_provider_receipt':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        r=p.apply(eid,ACTION);r['signature']='0'*64
        return 'STOP' if not f.acknowledge(eid,r) else 'ERROR'
    elif case_id=='materialized_state_rewind':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        with sqlite3.connect(str(root/'auth.db'),factory=_ClosingConnection) as c:
            c.execute("UPDATE effects SET status='PREPARED',dispatch_seq=NULL WHERE effect_id=?",(eid,))
            c.execute("UPDATE outbox SET state='PENDING',attempt=0,reserve_audit_seq=NULL WHERE effect_id=?",(eid,))
        return 'STOP' if not f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    elif case_id=='challenge_after_reservation':
        assert f.reserve_send(eid,ACTION,w,50).allowed
        b=f.challenge_body('crm','nonce-late');assert f.challenge(b,f.sign_challenge(b))
        return 'NOT_RETROACTIVE' if p.apply(eid,ACTION)['outcome']=='SUCCEEDED' else 'ERROR'
    elif case_id=='false_trusted_evidence':
        truth={'customer_eligible':False}
        assert not truth['customer_eligible']
        return 'FALSE_EVIDENCE_PASSED' if f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    elif case_id=='direct_provider_bypass':
        return 'BYPASS' if p.apply(eid,ACTION)['outcome']=='SUCCEEDED' and f.state_pair(eid)['outbox']['state']=='PENDING' else 'ERROR'
    elif case_id=='external_registry_challenge_not_relayed':
        ext=authority(root/'other_registry.db')
        body=ext.challenge_body('crm','nonce-remote');assert ext.challenge(body,ext.sign_challenge(body))
        return 'SPLIT_STORE_GAP' if f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'
    return 'STOP' if not f.reserve_send(eid,ACTION,w,50).allowed else 'ERROR'

def main():
    results=[]
    with tempfile.TemporaryDirectory() as t:
        for index,(cid,expect) in enumerate(CASES):
            folder=Path(t)/f'{index:02d}';folder.mkdir()
            observed=run_one(cid,folder)
            results.append({'case_id':cid,'expected':expect,'observed':observed,'pass':observed==expect})
    output={'schema':'EARNED_TRUST_C008_SCENARIOS','total':len(results),
            'passed':sum(x['pass'] for x in results),'counts':dict(Counter(x['observed'] for x in results)),
            'cases':results,'scope':'author-authored synthetic cases; not real-world safety rates'}
    Path('scenario_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'total':output['total'],'passed':output['passed'],'counts':output['counts']},indent=2))
    if not all(x['pass'] for x in results):raise SystemExit(1)

if __name__=='__main__': main()
