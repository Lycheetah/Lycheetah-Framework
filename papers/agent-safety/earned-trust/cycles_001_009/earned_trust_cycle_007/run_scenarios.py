"""Fixed scenario matrix. Each scenario starts in a clean synthetic SQLite DB."""
import json
from collections import Counter
from pathlib import Path
import tempfile
from dispatch_fence import Fence
from test_dispatch_fence import ACTION, KEYS, seed

SCENARIOS=(
    'clean', 'challenge_before_claim', 'challenge_refreshed', 'unrelated_challenge_cached',
    'unrelated_challenge_refreshed', 'revoke_before_claim', 'revoke_refreshed',
    'evidence_becomes_fail', 'evidence_changes_but_stays_pass',
    'action_substitution', 'tampered_witness', 'expired_approval',
    'forged_challenge_ignored', 'challenge_after_claim', 'false_trusted_evidence',
    'resolve_and_refinalize', 'duplicate_dispatch', 'missing_witness',
    'challenge_to_unregistered_source', 'fresh_cache_on_cleared_challenge',
)

def one(name):
    with tempfile.TemporaryDirectory() as td:
        f=Fence(Path(td)/'fence.sqlite',**KEYS)
        witness=seed(f)
        act=ACTION
        now=120
        ground_truth=True
        if name in {'challenge_before_claim','challenge_refreshed',
                    'challenge_after_claim','resolve_and_refinalize',
                    'fresh_cache_on_cleared_challenge'}:
            if name == 'challenge_after_claim':
                first=f.claim('effect-1',ACTION,witness,now)
            else:
                first=None
            body=f.challenge_body('origin-crm','c-'+name)
            assert f.challenge(body,f.sign_challenge(body))
            if name=='challenge_refreshed':witness=f.witness('effect-1')
            if name in {'resolve_and_refinalize','fresh_cache_on_cleared_challenge'}:
                resolution=f.resolution_body('origin-crm','r-'+name)
                assert f.resolve(resolution,[f.sign_resolution(resolution,'north'),f.sign_resolution(resolution,'south')])
                if name=='resolve_and_refinalize':witness=f.witness('effect-1')
        if name in {'unrelated_challenge_cached','unrelated_challenge_refreshed'}:
            b=f.challenge_body('unrelated-root','unrelated-'+name)
            assert f.challenge(b,f.sign_challenge(b))
            if name=='unrelated_challenge_refreshed':witness=f.witness('effect-1')
        if name in {'revoke_before_claim','revoke_refreshed'}:
            f.revoke('agent-1')
            if name=='revoke_refreshed':witness=f.witness('effect-1')
        if name=='evidence_becomes_fail':
            assert f.update_evidence('refund-eligibility',2,'FAIL','fictitious-001')
            witness=f.witness('effect-1')
        if name=='evidence_changes_but_stays_pass':
            assert f.update_evidence('refund-eligibility',2,'PASS','fictitious-001')
            witness=f.witness('effect-1')
        if name=='action_substitution':act={**ACTION,'amount_cents':9999}
        if name=='tampered_witness':
            witness=dict(witness);witness['seal']='0'*64
        if name=='expired_approval':now=201
        if name=='forged_challenge_ignored':
            b=f.challenge_body('origin-crm','forged')
            assert not f.challenge(b,'0'*64)
        if name=='false_trusted_evidence':ground_truth=False
        if name=='missing_witness':witness=None
        if name=='challenge_to_unregistered_source':
            b=f.challenge_body('unregistered','forged-target')
            assert not f.challenge(b,f.sign_challenge(b))
        if name=='challenge_after_claim':decision=first
        else:decision=f.claim('effect-1',act,witness,now)
        repeated=None
        if name=='duplicate_dispatch':
            repeated=f.claim('effect-1',act,witness,now).reason
        out={'case':name,'allowed':decision.allowed,'reason':decision.reason,
             'status':f.state('effect-1')['status'],'ground_truth_correct':ground_truth,
             'ledger_valid':f.verify_audit()}
        if repeated is not None:out['retry_reason']=repeated
        return out


def run():
    rows=[one(name) for name in SCENARIOS]
    assert len(rows)==len(SCENARIOS)
    assert all(x['ledger_valid'] for x in rows)
    return {'description':'20 locally authored scenario fixtures, no provider effects',
            'n':len(rows), 'allowed':sum(x['allowed'] for x in rows),
            'paused':sum(not x['allowed'] for x in rows),
            'false_world_confirmations':sum(x['allowed'] and not x['ground_truth_correct'] for x in rows),
            'by_reason':dict(Counter(x['reason'] for x in rows)), 'cases':rows}

if __name__=='__main__':
    output=run()
    Path(__file__).with_name('scenario_results.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='cases'},indent=2))
