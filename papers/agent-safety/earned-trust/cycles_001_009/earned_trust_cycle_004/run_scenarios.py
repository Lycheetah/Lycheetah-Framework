"""Reproduce fixed lab cases; no probabilistic benchmark or live action."""
from __future__ import annotations
import json, copy, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "earned_trust_cycle_003"))
from authenticated_provider import SignedSQLiteProvider, TrustedIssuer, hash_obj
from independent_witness import IndependentObserver, OutcomeVerifier
from conventional_baseline import conventional_reconcile

AUTH, PROVIDER, OBSERVER = b'A'*32, b'B'*32, b'C'*32
ACTION = {'actor':'agent', 'subject':'fictional-order-88', 'scope':'refund:create', 'amount_cents':1200}


def case(name, *, actual_truth=True, observer_status='COMMITTED', observer_correctness='TRUE',
         missing_observer=False, wrong_observer_action=False, stale_observer=False,
         corrupted_provider=False, missing_provider=False):
    with tempfile.TemporaryDirectory() as tmp:
        p = SignedSQLiteProvider(Path(tmp)/'provider.db', authority_secret=AUTH, provider_secret=PROVIDER)
        o = IndependentObserver(Path(tmp)/'observer.db', secret=OBSERVER)
        p.seed(ACTION, truth=actual_truth)
        sv,pv=p.snapshot(ACTION['subject'])
        token=TrustedIssuer(AUTH).issue(action=ACTION,effect_id='e1',approval_id='a1',
                                        subject_version=sv,policy_version=pv,now=100,expires_at=200,nonce='n1')
        if not missing_provider:
            outcome=p.commit(ACTION,token,now=110)
            assert outcome.code=='COMMITTED', outcome.code
        witness=None
        if not missing_observer:
            witness=o.observe(effect_id='e1',token_sha256=hash_obj(token),
                              action_sha256=('a'*64 if wrong_observer_action else hash_obj(ACTION)),
                              status=observer_status,correctness=observer_correctness,observed_at=120)
            if stale_observer:
                o.observe(effect_id='e1',token_sha256=hash_obj(token),action_sha256=hash_obj(ACTION),
                          status='COMMITTED',correctness='FALSE',observed_at=121)
        if corrupted_provider:
            import sqlite3
            with sqlite3.connect(p.path) as db:
                db.execute("UPDATE effects SET receipt_json='{' WHERE effect_id='e1'")
        receipt_only=p.lookup('e1') if not corrupted_provider else None
        baseline='CONFIRMED' if receipt_only is not None and p.verify_proof(receipt_only,token=token,action=ACTION) else 'UNKNOWN'
        result=OutcomeVerifier(p,o).reconcile(effect_id='e1',token=token,action=ACTION,supplied_witness=witness)
        conventional=conventional_reconcile(p,o,'e1',token,ACTION,observed=witness)
        return {'case':name,'ground_truth_correct':actual_truth,
                'receipt_only':baseline,'conventional_matched':conventional,'two_record':result.result,'reason':result.reason,
                'provider_auth':result.provider_authenticated,
                'observer_auth':result.independent_observation_authenticated}

if __name__=='__main__':
    cases=[
        case('legitimate'),
        case('false-evidence-found',actual_truth=False,observer_correctness='FALSE'),
        case('correlated-false-oracle',actual_truth=False,observer_correctness='TRUE'),
        case('missing-observation',missing_observer=True),
        case('observer-not-committed',observer_status='NOT_COMMITTED'),
        case('observer-unknown',observer_status='UNKNOWN',observer_correctness='UNKNOWN'),
        case('observer-action-disagreement',wrong_observer_action=True),
        case('outdated-signed-observation',stale_observer=True),
        case('provider-record-corruption',corrupted_provider=True),
        case('no-provider-commit',missing_provider=True),
    ]
    payload={'status':'LOCAL_SYNTHETIC_REPRODUCED','design':'author-authored deterministic cases',
             'cases':cases,'totals':{'total_cases':len(cases),
                 'two_record_confirmed':sum(x['two_record']=='CONFIRMED' for x in cases),
                 'two_record_review':sum(x['two_record']=='REVIEW' for x in cases),
                 'two_record_conflict':sum(x['two_record']=='CONFLICT' for x in cases),
                 'two_record_unknown':sum(x['two_record']=='UNKNOWN' for x in cases),
                 'receipt_only_confirmed':sum(x['receipt_only']=='CONFIRMED' for x in cases),
                 'matched_baseline_disagreements':sum(x['two_record']!=x['conventional_matched'] for x in cases)}}
    print(json.dumps(payload,indent=2))
