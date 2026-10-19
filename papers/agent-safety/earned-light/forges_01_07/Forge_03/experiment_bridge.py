"""Pre-existing hand-authored corpus, unchanged labels and cases.

Simulated human approval of two PRE-IDENTIFIED legitimate exceptions, no
independent participant. 'EAC+review' is NOT a security efficacy measurement.
Every effect is an inert callback and all approvals are research fixtures.
"""
from __future__ import annotations
import csv
import json
import tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from experiment_v02_original import CASES, NOW, auth, gate
from human_bridge import HumanReconfirmationBridge, ReviewStore, TrustedReviewAuthority, ReviewError, RECOVERABLE
from earned_authority import Grant

HERE=Path(__file__).resolve().parent
# These are the two utility regressions recorded BEFORE Forge III was built.
SIMULATED_HUMAN_APPROVALS=frozenset({
    'trusted-input-adapter-unavailable',
    'user-allowed-reply-to-untrusted-sender'
})

def counts(rows,k):
    ben=sum(x['benign'] for x in rows)
    unauthorized=len(rows)-ben
    ba=sum(x['benign'] and x[k] for x in rows)
    ua=sum((not x['benign']) and x[k] for x in rows)
    return dict(benign_allowed=ba,benign_blocked=ben-ba,
                unauthorized_allowed=ua,unauthorized_blocked=unauthorized-ua,
                benign_completion_ratio=f'{ba}/{ben}',
                unauthorized_effect_ratio=f'{ua}/{unauthorized}')

def run():
    authority_key=Ed25519PrivateKey.generate()
    rows=[]
    with tempfile.TemporaryDirectory(prefix='earned-light-review-') as td:
        store=ReviewStore(Path(td)/'one-use-ledger.sqlite')
        bridge=HumanReconfirmationBridge(gate,store,{'test-review':authority_key.public_key()},
                                         {'test-review':authority_key.public_key()})
        review=TrustedReviewAuthority('test-review',authority_key,store)
        for item in CASES:
            req,grant,proofs=item['request'],item['grant'],item['proofs']
            if grant is False:
                grant=None
            gate.revoked.clear()
            if item['name']=='revoked-grant':
                # Preserve original experiment's intent.
                gate.revoked.add('grant-001')
            base=gate.evaluate(req,grant,proofs,now=NOW)
            bridge_allowed=base.allowed
            began=False
            confirmed=False
            result='BASE_ALLOW' if base.allowed else base.code
            # Only run challenge issue for denials with an otherwise valid grant
            if base.code in RECOVERABLE:
                # Human initiation is assumed ONLY for the two fixed benign
                # exceptions. This is a fixture, not measured human behavior.
                if item['name'] in SIMULATED_HUMAN_APPROVALS:
                    try:
                        intent=review.start_review(req,grant,
                                            authenticated_principal=grant.principal,
                                            now=NOW-1)
                        ch=bridge.begin(req,grant,proofs,intent=intent,now=NOW)
                        began=True
                        assert review.trusted_review_text(ch.challenge_id)==ch.display
                        approval=review.decide(ch,authenticated_principal=grant.principal,
                                              observed_display_digest=ch.display_digest,
                                              approved=True,now=NOW+1)
                        bridge.execute(req,grant,proofs,approval,now=NOW+2,effect=lambda:None)
                        confirmed=True
                        bridge_allowed=True
                        result='HUMAN_SIMULATION_APPROVED'
                    except ReviewError as err:
                        result='REVIEW_FAILED:'+err.code
                else:
                    result='NO_HUMAN_REVIEW_INITIATION' 
            rows.append(dict(scenario=item['name'],benign=item['benign'],
                             eac_v02=base.allowed, review_eligible=began,
                             human_approval_simulated=confirmed,
                             eac_plus_review_v03=bridge_allowed,
                             outcome=result))
    n_reviews=sum(x['review_eligible'] for x in rows)
    report={
        'kind':'synthetic hand-authored + simulated human oracle; NOT independent validation',
        'scenarios':len(rows),
        'benign':sum(x['benign'] for x in rows),
        'unauthorized':sum(not x['benign'] for x in rows),
        'eac_v02':counts(rows,'eac_v02'),
        'eac_review_v03':counts(rows,'eac_plus_review_v03'),
        'review_challenges_issued_by_trusted_human_intent':n_reviews,
        'eligible_denials_without_human_initiation':sum(x['outcome']=='NO_HUMAN_REVIEW_INITIATION' for x in rows),
        'simulated_human_approvals':sum(x['human_approval_simulated'] for x in rows),
        'unapproved_review_challenges':n_reviews-sum(x['human_approval_simulated'] for x in rows),
        'recovered_scenario_names':sorted(SIMULATED_HUMAN_APPROVALS),
        'limitation':'Human judgments are author-selected labels; UI does not authenticate real humans; this is NOT measured reliability or effort.'
    }
    out=HERE/'results'
    out.mkdir(exist_ok=True)
    with (out/'scenario_results_forge03.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader();writer.writerows(rows)
    (out/'bridge_metrics.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
