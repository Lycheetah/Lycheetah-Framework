"""Cycle 004 *UNEXECUTED* contract using actual Framework classes.

Run inside Lycheetah-Framework (master):
  PYTHONPATH=/path/to/Lycheetah-Framework:/path/to/earned_trust_cycle_003:/path/to/earned_trust_cycle_004 \
     python -m unittest -v test_framework_bridge_candidate

Deliberately no substitute/mock of the Framework. Only local SQLite side effects.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'earned_trust_cycle_003'))
from authenticated_provider import SignedSQLiteProvider, TrustedIssuer, hash_obj
from independent_witness import IndependentObserver, OutcomeVerifier


def run_simulated_refund(home: Path, *, stale_before_finality: bool = False,
                         stale_after_dispatch: bool = False,
                         false_world_fact: bool = False) -> dict[str, Any]:
    # Import only real repository classes. If absent, FAIL, do not substitute.
    from lycheetah.assurance.models import AssuranceEvent, Phase
    from lycheetah.assurance.policy import AssurancePolicy
    from lycheetah.assurance.runtime import AssuranceRuntime
    from lycheetah.assurance.finality import (
        FinalityGate, MappingEvidenceStore, EvidenceRecord, EvidenceRequirement,
    )
    from lycheetah.assurance.action_guard import PersistentActionGuard

    home.mkdir(parents=True,exist_ok=True)
    action={'actor':'lab-agent','subject':'fictional-order-88',
            'amount_cents':1200,'scope':'refund:create'}
    authority_key=b'A'*32
    provider_key=b'B'*32
    observer_key=b'C'*32
    provider=SignedSQLiteProvider(home/'provider.sqlite',authority_secret=authority_key,
                                  provider_secret=provider_key)
    provider.seed(action,truth=not false_world_fact)
    observer=IndependentObserver(home/'observer.sqlite',secret=observer_key)
    policy=AssurancePolicy(policy_id='earned-trust.simulator',version='1.0.0',
                           tool_allowlist=('refund.create',), require_approval_for_side_effects=True)
    runtime=AssuranceRuntime(policy)
    event=AssuranceEvent(phase=Phase.TOOL,tool_name='refund.create',tool_arguments=action,
                         scopes=('refund:create',),side_effect=True,human_approved=True,
                         event_id='proposal-1',trace_id='cycle-004-fixture-1')
    evidence=MappingEvidenceStore([EvidenceRecord('eligibility:fictional-order-88','1',
                                       'fictional-order-88','digest:1','PASS')])
    gate=FinalityGate(runtime,evidence)
    requirement=EvidenceRequirement('eligibility:fictional-order-88',
                                     required_subject_hash='fictional-order-88')
    admission=gate.admit(event,[requirement])
    if not admission.ready_for_finality or admission.witness is None:
        return {'result':'REVIEW','where':'admission','reason':admission.reason}
    guard=PersistentActionGuard(home/'guard.sqlite')
    # THIS IS NOT AUTHENTICATED HUMAN APPROVAL. The trusted fixture asserts it.
    approved=guard.issue_approval('grant-1','lab-agent','fixture-claims-human',
                                   action,'refund:create',100,200)
    prepared=guard.prepare_effect('effect-1','grant-1','lab-agent',action,'refund:create',110)
    if not approved.allowed or not prepared.allowed:
        return {'result':'REVIEW','where':'guard','reason':prepared.reason}
    if stale_before_finality:
        evidence.put(EvidenceRecord('eligibility:fictional-order-88','2',
                                     'fictional-order-88','digest:2','FAIL'))
    finality=gate.finalize(admission.witness,event)
    if not finality.ready:
        return {'result':'REVIEW','where':'finality','reason':finality.reason,
                'guard_status':guard.get_effect('effect-1')['status']}
    claim=guard.claim_dispatch('effect-1',115,action,
                               expected_audit_anchor=guard.audit_anchor())
    if not claim.allowed:
        return {'result':'REVIEW','where':'dispatch','reason':claim.reason}
    sv,pv=provider.snapshot(action['subject'])
    token=TrustedIssuer(authority_key).issue(action=action,effect_id='effect-1',
                                            approval_id='a1',subject_version=sv,
                                            policy_version=pv,now=100,expires_at=200,nonce='lab-nonce')
    if stale_after_dispatch:
        provider.change(subject=action['subject'],status='FAIL')
    result=provider.commit(action,token,now=120)
    if not result.committed:
        guard.record_result('effect-1',121,'failure',{'provider_code':result.code})
        return {'result':'REVIEW','where':'provider','reason':result.code,
                'guard_status':guard.get_effect('effect-1')['status']}
    guard.record_result('effect-1',121,'success',
                        {'lab_receipt_sha256':hash_obj(result.receipt)})
    observer.observe(effect_id='effect-1',token_sha256=hash_obj(token),
                     action_sha256=hash_obj(action),status='COMMITTED',
                     correctness='FALSE' if false_world_fact else 'TRUE',observed_at=122)
    reconciled=OutcomeVerifier(provider,observer).reconcile(effect_id='effect-1',
                                                             action=action,token=token)
    return {'result':reconciled.result,'reason':reconciled.reason,
            'guard_status':guard.get_effect('effect-1')['status'],
            'provider_effects':provider.effect_count()}
