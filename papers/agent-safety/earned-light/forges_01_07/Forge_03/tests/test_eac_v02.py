from dataclasses import replace
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from earned_authority import EarnedAuthorityGate, canonical, digest
from demo_fixtures import default_request, grant_for, origin_for

@pytest.fixture
def fx():
    auth = Ed25519PrivateKey.generate()
    ingress = Ed25519PrivateKey.generate()
    request = default_request()
    grant = grant_for(auth, request)
    proof = origin_for(ingress, request, grant, "recipient")
    gate = EarnedAuthorityGate({"auth-service": auth.public_key()},
                               {"trusted-ingress": ingress.public_key()})
    return auth, ingress, request, grant, proof, gate


def test_legitimate_user_recipient_allowed(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(r, g, [p], now=200).code == "EAC_ALLOW"


def test_legitimate_crm_recipient_allowed(fx):
    _, ingress, r, g, p, gate = fx
    assert gate.evaluate(r, g, [origin_for(ingress, r, g, "recipient", kind="trusted_crm")], now=200).allowed

@pytest.mark.parametrize("source", ["untrusted_email", "untrusted_web", "agent_inference", "retrieved_pdf"])
def test_injected_recipient_denied(fx, source):
    _, ingress, r, g, _, gate = fx
    p = origin_for(ingress, r, g, "recipient", kind=source)
    assert gate.check_grant(r, g, now=200).allowed
    assert gate.evaluate(r, g, [p], now=200).code == "ORIGIN_DISALLOWED"


def test_untrusted_claim_without_attester_signature_denied(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(r, g, [replace(p, origin_kind="trusted_crm")], now=200).code == "ORIGIN_UNTRUSTED"


def test_tampered_destination_denied(fx):
    _, _, r, g, p, gate = fx
    new = replace(r, arguments={**r.arguments, "recipient":"attacker@example.test"})
    assert gate.evaluate(new, g, [p], now=200).code == "ORIGIN_VALUE_MISMATCH"


def test_recipient_missing_proof_denied(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(r, g, [], now=200).code == "FIELD_PROOF_MISSING"


def test_unknown_effect_field_denied(fx):
    _, _, r, g, p, gate = fx
    new=replace(r, arguments={**r.arguments, "forward_all": True})
    assert gate.evaluate(new, g, [p], now=200).code == "UNRECOGNIZED_EFFECT_FIELD"


def test_hidden_bcc_requires_own_proof(fx):
    _, ingress, r, g, p, gate = fx
    new=replace(r, arguments={**r.arguments, "bcc":"attacker@example.test"})
    assert gate.evaluate(new, g, [p], now=200).code == "FIELD_PROOF_MISSING"
    bcc=origin_for(ingress,new,g,"bcc",kind="untrusted_email")
    assert gate.evaluate(new,g,[p,bcc],now=200).code == "ORIGIN_DISALLOWED"


def test_missing_required_field_denied(fx):
    _, _, r, g, p, gate = fx
    new=replace(r, arguments={"recipient":"customer@example.test", "subject":"Hi"})
    assert gate.evaluate(new,g,[p],now=200).code == "REQUIRED_FIELD_MISSING"


def test_proof_wrong_session_denied(fx):
    _, ingress, r, g, _, gate = fx
    bad=origin_for(ingress, r, g, "recipient")
    bad=replace(bad, session_id="some-other-session")
    bad=replace(bad, signature=ingress.sign(canonical(bad.payload())).hex())
    assert gate.evaluate(r,g,[bad],now=200).code == "ORIGIN_CONTEXT_MISMATCH"


def test_wrong_grant_binding_denied(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(replace(r, agent_id="agent-b"),g,[p],now=200).code == "GRANT_BINDING_MISMATCH"
    assert gate.evaluate(replace(r, scope="admin"),g,[p],now=200).code == "GRANT_BINDING_MISMATCH"
    assert gate.evaluate(replace(r, state_version="state-8"),g,[p],now=200).code == "GRANT_BINDING_MISMATCH"


def test_tampered_grant_denied(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(r,replace(g, principal="other-user"),[p],now=200).code == "GRANT_UNTRUSTED"


def test_expired_or_future_grant_denied(fx):
    _, _, r, g, p, gate = fx
    assert gate.evaluate(r,g,[p],now=500).code == "GRANT_NOT_CURRENT"
    assert gate.evaluate(r,g,[p],now=90).code == "GRANT_NOT_CURRENT"


def test_expired_proof_denied(fx):
    _, ingress, r, g, p, gate=fx
    expired=origin_for(ingress,r,g,"recipient",expires=150)
    assert gate.evaluate(r,g,[expired],now=200).code == "ORIGIN_NOT_CURRENT"


def test_revoked_grant_denied(fx):
    _, _, r, g, p, gate=fx
    gate.revoked.add(g.grant_id)
    assert gate.evaluate(r,g,[p],now=200).code == "GRANT_REVOKED"


def test_grant_missing_denied(fx):
    _, _, r, g, p, gate=fx
    assert gate.evaluate(r,None,[p],now=200).code == "GRANT_MISSING"


def test_wrong_signing_keys_denied(fx):
    auth, ingress, r, g, p, gate=fx
    wrong=EarnedAuthorityGate({"auth-service": ingress.public_key()}, {"trusted-ingress": auth.public_key()})
    assert wrong.evaluate(r,g,[p],now=200).code == "GRANT_UNTRUSTED"
    wrong2=EarnedAuthorityGate({"auth-service": auth.public_key()}, {"trusted-ingress": auth.public_key()})
    assert wrong2.evaluate(r,g,[p],now=200).code == "ORIGIN_UNTRUSTED"


def test_duplicate_proof_denied(fx):
    _, _, r, g, p, gate=fx
    assert gate.evaluate(r,g,[p,p],now=200).code == "EXTRA_OR_DUPLICATE_PROOF"


def test_unknown_operation_fails_closed(fx):
    _, _, r, g, p, gate=fx
    assert gate.evaluate(replace(r, operation="delete_all"),g,[p],now=200).code == "OPERATION_NOT_POLICY_CONTROLLED"


def test_json_canonicalization_protects_special_types():
    assert digest({"a":1,"b":[True]}) == digest({"b":[True],"a":1})
    with pytest.raises(ValueError): canonical({"x":float("nan")})
    with pytest.raises(ValueError): canonical({1:"bad key"})


def test_no_real_execution_is_invoked(fx):
    # This probe is intentionally only a gate; existing Lycheetah harness
    # must enforce that the gate is required before its side-effect executor.
    _, _, r, g, p, gate=fx
    assert gate.evaluate(r,g,[p],now=200).allowed


def test_mock_side_effect_runs_only_when_allowed(fx):
    from airlock import evaluate_then_invoke, AuthorityRejected
    _, ingress, r, g, p, gate=fx
    side_effects=[]
    effect=lambda: side_effects.append("mail_sent")
    with pytest.raises(AuthorityRejected) as denied:
        evaluate_then_invoke(gate,r,g,[origin_for(ingress,r,g,"recipient",kind="untrusted_email")],
                             now=200,effect=effect)
    assert denied.value.decision.code=="ORIGIN_DISALLOWED"
    assert side_effects==[]
    dec, _=evaluate_then_invoke(gate,r,g,[p],now=200,effect=effect)
    assert dec.allowed and side_effects==["mail_sent"]


def test_racing_revocation_prevents_later_mock_effect(fx):
    from airlock import evaluate_then_invoke, AuthorityRejected
    _, _, r, g, p, gate=fx
    # Earlier planning verdict is NOT durable authorization to execute later.
    assert gate.evaluate(r,g,[p],now=200).allowed
    gate.revoked.add(g.grant_id)
    invoked=[]
    with pytest.raises(AuthorityRejected):
        evaluate_then_invoke(gate,r,g,[p],now=201,effect=lambda: invoked.append("effect"))
    assert invoked==[]


def test_hundred_destination_mutations_fail_provenance_binding(fx):
    _, _, r, g, p, gate=fx
    for i in range(100):
        changed=replace(r,arguments={**r.arguments,"recipient":f"unapproved-{i}@example.test"})
        d=gate.evaluate(changed,g,[p],now=200)
        assert not d.allowed and d.code=="ORIGIN_VALUE_MISMATCH"


def test_failure_museum_counterexample_trusted_ingress_lies(fx):
    # Inherent trust-root weakness: proof verifies if attester key is trusted,
    # even if its origin classification is false. This is NOT a passing
    # security property; we preserve a known limitation as regression evidence.
    _, _, r, g, p, gate=fx
    actually_untrusted_mail_was_mislabeled_as_human=True
    assert actually_untrusted_mail_was_mislabeled_as_human
    assert gate.evaluate(r,g,[p],now=200).allowed
