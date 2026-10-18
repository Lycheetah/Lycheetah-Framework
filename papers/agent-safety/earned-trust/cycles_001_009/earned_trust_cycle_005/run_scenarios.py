"""Fixed adversarial comparison of naive signature counts and root-aware checks.
No live provider; the provider_receipt_valid bit is a fixture assertion.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
from conventional_baseline import conventional_decide
from provenance_gate import ProvenanceGate, naive_signed_quorum
from test_provenance_gate import fixture, signed

REG,GATE=fixture()
P={'effect_id':'effect-1','action_sha256':'a'*64,'token_sha256':'b'*64,'now':105}

def scenario(name, signers=('witness-a','witness-c'), overrides=None,
             mutation=None, current=True, revisions=None, provider=True,
             actual_truth=True, minimum=2):
    overrides=overrides or {}
    witnesses=[signed(REG,s,**overrides.get(s,{})) for s in signers]
    if mutation:
        mutation(witnesses)
    rv={s:1 for s in signers} if current else None
    if revisions is not None:
        rv=revisions
    opts={**P,'current_revisions':rv,'provider_receipt_valid':provider}
    gate=ProvenanceGate(REG,min_independent=minimum)
    controlled=gate.evaluate(witnesses,**opts)
    normal=conventional_decide(REG,witnesses,**opts,min_independent=minimum)
    baseline=naive_signed_quorum(REG,witnesses,**opts)
    return {'name':name,'ground_truth_correct':actual_truth,
            'naive_signed_quorum':baseline,'provenance_gate':controlled.decision,
            'matched_conventional':normal,'reason':controlled.reason,
            'distinct_paths':controlled.disjoint_witnesses,
            'signed_witnesses':controlled.authenticated_signers}


def corrupt(witnesses):witnesses[0]['body']['correctness']='FALSE'
def action_swap(witnesses):witnesses[1]['body']['action_sha256']='x'*64
def duplicate(witnesses):witnesses.append(copy.deepcopy(witnesses[0]))

def generate():
    cases=[
      scenario('separate-crm-and-bank'),
      scenario('same-origin-two-signatures',('witness-a','witness-b')),
      scenario('same-controller-different-originals',('witness-a','witness-e')),
      scenario('three-signers-two-origins',('witness-a','witness-b','witness-c')),
      scenario('three-genuinely-disjoint-origins',('witness-a','witness-c','witness-d'),minimum=3),
      scenario('two-sources-agree-on-false-evidence',actual_truth=False),
      scenario('recorded-negative-evidence',overrides={'witness-c':{'correctness':'FALSE'}}),
      scenario('missing-outcome-observation',overrides={'witness-c':{'correctness':'UNKNOWN'}}),
      scenario('old-timestamp',overrides={'witness-a':{'observed_at':10}}),
      scenario('old-revision',revisions={'witness-a':2,'witness-c':1}),
      scenario('provider-proof-absent',provider=False),
      scenario('signature-corruption',mutation=corrupt),
      scenario('action-substitution',mutation=action_swap),
      scenario('replayed-signer',mutation=duplicate),
      scenario('no-current-readback',current=False),
      scenario('underspecified-independent-quorum',minimum=3),
    ]
    return {'status':'LOCAL_SYNTHETIC','cases':cases,'totals':{
       'cases':len(cases),
       'naive_confirmed':sum(c['naive_signed_quorum']=='CONFIRMED' for c in cases),
       'provenance_confirmed':sum(c['provenance_gate']=='CONFIRMED' for c in cases),
       'provenance_review':sum(c['provenance_gate']=='REVIEW' for c in cases),
       'provenance_conflict':sum(c['provenance_gate']=='CONFLICT' for c in cases),
       'matched_control_disagreements':sum(c['provenance_gate']!=c['matched_conventional'] for c in cases),
       'false_truth_confirmed':sum(c['provenance_gate']=='CONFIRMED' and not c['ground_truth_correct'] for c in cases),
    }}

if __name__=='__main__':
    print(json.dumps(generate(),indent=2))
