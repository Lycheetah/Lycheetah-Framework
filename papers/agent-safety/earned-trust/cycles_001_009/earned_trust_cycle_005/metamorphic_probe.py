"""Deterministic synthetic property probe; NOT external validation or fuzzed untrusted data."""
import json,random
from test_provenance_gate import fixture,signed,verdict
from conventional_baseline import conventional_decide


def run(seed=1956,trials=1000):
    rng=random.Random(seed)
    registry,gate=fixture()
    ids=['witness-a','witness-b','witness-c','witness-d','witness-e']
    differences=order_changes=tampered_allow=common_root_accepts=0
    count_confirms=0
    sample=[]
    for i in range(trials):
        names=rng.sample(ids,rng.randint(1,len(ids)))
        claims=[signed(registry,name,observed_at=100,revision=1) for name in names]
        revisions={name:1 for name in names}
        params={'effect_id':'effect-1','action_sha256':'a'*64,'token_sha256':'b'*64,
                'now':105,'current_revisions':revisions,'provider_receipt_valid':True}
        got=gate.evaluate(claims,**params).decision
        other=conventional_decide(registry,claims,**params)
        if got!=other: differences+=1;sample.append({'round':i,'error':'baseline','ids':names})
        rotated=list(reversed(claims))
        if gate.evaluate(rotated,**params).decision!=got:
            order_changes+=1;sample.append({'round':i,'error':'order'})
        if gate.evaluate(claims,**{**params,'action_sha256':'f'*64}).decision=='CONFIRMED':
            tampered_allow+=1;sample.append({'round':i,'error':'action'})
        roots=set().union(*(registry.exposure(s)[0] for s in names))
        if len(roots)==1 and got=='CONFIRMED':
            common_root_accepts+=1;sample.append({'round':i,'error':'common-root'})
        count_confirms+=(got=='CONFIRMED')
    return {'status':'SYNTHETIC_DETERMINISTIC','seed':seed,'cases':trials,
            'matched_baseline_disagreements':differences,
            'order_invariance_failures':order_changes,
            'mismatched_action_confirmations':tampered_allow,
            'single_root_confirmations':common_root_accepts,
            'confirmations_total':count_confirms,
            'recorded_counterexamples':sample[:10]}

if __name__=='__main__':print(json.dumps(run(),indent=2))
