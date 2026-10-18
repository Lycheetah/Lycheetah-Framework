"""Deterministic synthetic identities; never import these lab keys in production."""
from crashsafe_authority import CrashSafeAuthority, SimulatedIdempotentProvider
K_A=b'A'*32; K_C=b'C'*32; K_F=b'F'*32; K_P=b'P'*32
REVIEWERS={'reviewer1':('org_1',b'1'*32),'reviewer2':('org_2',b'2'*32)}
GRAPH={'crm':(), 'dashboard':('crm',),'merchant':()}
ACTION={'subject':'customer-123','refund_cents':1000,'tool':'refund.create'}

def authority(db):
    return CrashSafeAuthority(db,provider_receipt_key=K_P,approval_key=K_A,auditor_key=K_C,
                              reviewer_keys=REVIEWERS,fence_key=K_F,source_parents=GRAPH)

def provider(db):
    return SimulatedIdempotentProvider(db,receipt_key=K_P)

def setup_effect(authority, effect_id='effect-001', action=ACTION, source='dashboard', key='eligibility', revision=1):
    assert authority.update_evidence(key,revision,'PASS',action['subject'])
    body=authority.approval_body('approval-'+effect_id,'agent',action,'refund',10000)
    assert authority.approve(body,authority.sign_approval(body))
    assert authority.prepare(effect_id,body['approval_id'],action,'refund',[source],{key:revision})
    assert authority.enqueue(effect_id)
    return authority.witness(effect_id)
