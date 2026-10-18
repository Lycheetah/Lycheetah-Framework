"""Dated Cycle 005 fixture correction, 18 October 2026.

Original source is retained under cycles_001_009/earned_trust_cycle_005/.
Changes: explicit historical import root; seed the provider with the same
approval identity placed in its token. The provider check is not weakened.
The optional provider_approval_id exposes the mismatch for a regression test.

Locally executed real-Lycheetah integration candidate.

Requires pinned Lycheetah-Framework checkout and Cycles 003 and 004 files.
No fake fallback for imported Framework classes. The human flag and
independence registry are controlled synthetic fixtures, not credentials.
"""
from __future__ import annotations
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cycles_001_009'
sys.path.insert(0,str(BASE/'earned_trust_cycle_003'))
sys.path.insert(0,str(BASE/'earned_trust_cycle_005'))
from authenticated_provider import SignedSQLiteProvider, TrustedIssuer, hash_obj
from provenance_gate import Source, TrustedRegistry, ProvenanceGate, sign_statement


def run_real_framework_path(home: Path, *, common_origin=False,
                            wrong_world_fact=False, stale_before_finality=False,
                            provider_approval_id="approval-1"):
    # Import specifically real repo classes. Missing package = failed import.
    from lycheetah.assurance.models import AssuranceEvent, Phase
    from lycheetah.assurance.policy import AssurancePolicy
    from lycheetah.assurance.runtime import AssuranceRuntime
    from lycheetah.assurance.finality import (
        FinalityGate, MappingEvidenceStore, EvidenceRecord, EvidenceRequirement)
    from lycheetah.assurance.action_guard import PersistentActionGuard

    home.mkdir(parents=True,exist_ok=True)
    action={'actor':'lab-agent','subject':'fictional-order-88',
            'scope':'refund:create','amount_cents':1200}
    akey,pkey=b'A'*32,b'B'*32
    provider=SignedSQLiteProvider(home/'provider.sqlite',authority_secret=akey,provider_secret=pkey)
    provider.seed(action,approval_id=provider_approval_id,truth=not wrong_world_fact)
    policy=AssurancePolicy(policy_id='earned-trust.probe',version='1.0.0',
                           tool_allowlist=('refund.create',),require_approval_for_side_effects=True)
    event=AssuranceEvent(phase=Phase.TOOL,tool_name='refund.create',tool_arguments=action,
                         scopes=('refund:create',),side_effect=True,human_approved=True,
                         event_id='cycle005-ev-1',trace_id='cycle005-trace')
    store=MappingEvidenceStore([EvidenceRecord('eligibility','1',action['subject'],'hash-1','PASS')])
    gate=FinalityGate(AssuranceRuntime(policy),store)
    admission=gate.admit(event,[EvidenceRequirement('eligibility',required_subject_hash=action['subject'])])
    if admission.witness is None or not admission.ready_for_finality:
        return {'decision':'REVIEW','boundary':'admission','reason':admission.reason}
    guard=PersistentActionGuard(home/'guard.sqlite')
    approved=guard.issue_approval('approval-1','lab-agent','fixture-human-assertion',
                                  action,'refund:create',100,200)
    prepared=guard.prepare_effect('effect-1','approval-1','lab-agent',action,'refund:create',110)
    if not approved.allowed or not prepared.allowed:
        return {'decision':'REVIEW','boundary':'guard-preparation'}
    if stale_before_finality:
        store.put(EvidenceRecord('eligibility','2',action['subject'],'hash-2','FAIL'))
    result=gate.finalize(admission.witness,event)
    if not result.ready:
        return {'decision':'REVIEW','boundary':'finality','reason':result.reason,
                'guard_status':guard.get_effect('effect-1')['status']}
    claimed=guard.claim_dispatch('effect-1',115,action,expected_audit_anchor=guard.audit_anchor())
    if not claimed.allowed:
        return {'decision':'REVIEW','boundary':'dispatch','reason':claimed.reason}
    subj_version,policy_version=provider.snapshot(action['subject'])
    token=TrustedIssuer(akey).issue(action=action,effect_id='effect-1',approval_id='approval-1',
                                   subject_version=subj_version,policy_version=policy_version,
                                   now=100,expires_at=200,nonce='cycle005')
    effect=provider.commit(action,token,now=120)
    if not effect.committed:
        guard.record_result('effect-1',121,'failure',{'code':effect.code})
        return {'decision':'REVIEW','boundary':'provider','reason':effect.code}
    guard.record_result('effect-1',121,'success',{'lab_receipt_sha256':hash_obj(effect.receipt)})
    # Prover is current LOCAL lab provider; signatures do not independently prove world truth.
    receipt=provider.lookup('effect-1')
    proof_ok=(receipt is not None and provider.verify_proof(receipt,token=token,action=action)
              and provider.verify_stored_effect('effect-1',token=token)
              and provider.verify_audit().get('valid') is True)
    roots=[Source('crm-source','crm-admin'),Source('bank-source','bank-admin')]
    nodes=[Source('observer-one','observer-admin-one',('crm-source',),True),
           Source('observer-two','observer-admin-two',('crm-source' if common_origin else 'bank-source',),True)]
    reg=TrustedRegistry(roots+nodes,{'observer-one':b'C'*32,'observer-two':b'D'*32})
    claims=[sign_statement(reg,sid,effect_id='effect-1',action_sha256=hash_obj(action),
                            token_sha256=hash_obj(token),observed_at=122,revision=1)
            for sid in ('observer-one','observer-two')]
    v=ProvenanceGate(reg).evaluate(claims,effect_id='effect-1',action_sha256=hash_obj(action),
                                    token_sha256=hash_obj(token),now=125,
                                    current_revisions={'observer-one':1,'observer-two':1},
                                    provider_receipt_valid=proof_ok)
    return {'decision':v.decision,'boundary':'provenance',
            'reason':v.reason,'disjoint_witnesses':v.disjoint_witnesses,
            'guard_status':guard.get_effect('effect-1')['status'],
            'ground_truth_correct':not wrong_world_fact,'provider_proof_ok':proof_ok}
