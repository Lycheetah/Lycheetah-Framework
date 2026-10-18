"""Fixed provider-only matched baseline, plus explicitly scoped negative controls."""
from __future__ import annotations
import json,os,tempfile,time,copy
from pathlib import Path
from conventional_baseline import ConventionalProvider
from protected_provider import ProtectedProvider,CapabilityIssuer
from lab_fixture import ACTION,K_P
from upstream_dispatch_fence import mac


def single_scenario(case):
    with tempfile.TemporaryDirectory() as tmp:
        key=b'G'*32
        issue=CapabilityIssuer(key)
        provider=ProtectedProvider(Path(tmp)/'protected.db',capability_keys={'gateway-v1':key},receipt_key=K_P)
        baseline=ConventionalProvider(Path(tmp)/'conventional.db',key)
        now=int(time.time())
        act=dict(ACTION)
        cap=issue.mint('effect-001',act,3,now=now)
        if case=='unsigned': cap={}
        elif case=='bad-signature':cap['signature']='0'*64
        elif case=='expired':cap=issue.mint('effect-001',act,3,now=now-100)
        elif case=='future':cap=issue.mint('effect-001',act,3,now=now+100)
        elif case=='changed-action':act['refund_cents']=2000
        elif case=='changed-subject':act['subject']='customer-999'
        elif case=='wrong-tool':
            act['tool']='database.drop';cap=issue.mint('effect-001',act,3,now=now)
        elif case=='oversized-refund':
            act['refund_cents']=1_000_001;cap=issue.mint('effect-001',act,3,now=now)
        elif case=='wrong-kid':
            cap['body']['kid']='other'
        elif case=='forged-seq':
            cap['body']['dispatch_seq']=4
        elif case=='compromised-key':
            cap=issue.mint('UNAUTHORIZED-no-broker',act,999,now=now)
        elif case=='stolen-valid-capability': pass
        elif case=='authorized': pass
        elif case=='replay': pass
        elif case=='mismatched-replay': pass
        else:raise ValueError(case)
        a=provider.apply(act,cap,now).status
        b=baseline.apply(act,cap,now)
        outcome_a='COMMITTED' if a==201 else 'REPLAY' if a==200 else 'DENIED'
        if case=='replay':
            a=provider.apply(act,cap,now).status
            b=baseline.apply(act,cap,now)
            outcome_a='REPLAY' if a==200 else 'DENIED'
        if case=='mismatched-replay':
            provider.apply(act,cap,now);baseline.apply(act,cap,now)
            cap=issue.mint('effect-001',act,4,now=now)
            a=provider.apply(act,cap,now).status;b=baseline.apply(act,cap,now)
            outcome_a='DENIED' if a==409 else 'COMMITTED' if a==201 else 'REPLAY'
        return {'case':case,'protected':outcome_a,'conventional':b,
                'agree':outcome_a==b,
                'risk':case in ('compromised-key','stolen-valid-capability')}

def main():
    cases=['authorized','unsigned','bad-signature','expired','future','changed-action','changed-subject',
           'wrong-tool','oversized-refund','wrong-kid','forged-seq','replay','mismatched-replay',
           'compromised-key','stolen-valid-capability']
    results=[single_scenario(c) for c in cases]
    summary={'schema':'earned-trust-C009-provider-baseline','scope':'provider-only; not a whole-agent benchmark',
             'cases':len(results),'agreements':sum(r['agree'] for r in results),
             'source':'fixed author-written synthetic scenarios','results':results}
    Path(__file__).with_name('scenario_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert all(r['agree'] for r in results),results
    print(json.dumps({'cases':len(results),'agreements':summary['agreements'],
                      'key_compromise_allowed':next(r['protected'] for r in results if r['case']=='compromised-key')}))
if __name__=='__main__':main()
