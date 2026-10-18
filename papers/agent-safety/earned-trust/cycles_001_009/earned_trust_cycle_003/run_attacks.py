"""Named negative/positive probes; all invented refund data and local SQLite.

Each scenario has its own database and independent lab setup. This is not a
benchmark over real operational traffic, nor an estimate of safety accuracy.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import json

from authenticated_provider import LostResponse, SignedSQLiteProvider, TrustedIssuer
from test_authenticated_provider import AUTH, PROVIDER

ACTION={"actor":"lab-agent", "subject":"invented-refund-7", "amount_cents":1200,"scope":"refund:create"}


def run():
    cases={}
    with TemporaryDirectory() as temp:
        def fixture(scenario):
            p=SignedSQLiteProvider(Path(temp)/f"{scenario}.sqlite",authority_secret=AUTH,provider_secret=PROVIDER)
            p.seed(ACTION)
            e,pol=p.snapshot(ACTION["subject"])
            token=TrustedIssuer(AUTH).issue(action=ACTION,effect_id="e1",approval_id="a1",
                subject_version=e,policy_version=pol,now=100,expires_at=200,nonce="unique-per-case")
            return p,token

        def case(scenario, mutation=None, *, lose=False):
            provider,token=fixture(scenario)
            action=copy.deepcopy(ACTION)
            if mutation:
                mutation(provider,token,action)
            try:
                outcome=provider.commit(action,token,now=120,lose_response=lose)
                result={"code":outcome.code,"effect_count":provider.effect_count(),"receipt_verified":(
                    provider.verify_proof(outcome.receipt,action=action,token=token) if outcome.receipt else None)}
            except LostResponse:
                proof=provider.lookup("e1")
                result={"code":"RESPONSE_LOST_AFTER_COMMIT","effect_count":provider.effect_count(),
                    "receipt_verified":bool(proof and provider.verify_proof(proof,action=action,token=token))}
            result["local_ground_truth"] = provider.recorded_truth(ACTION["subject"])
            result["ledger_valid"] = provider.verify_audit()["valid"]
            cases[scenario]=result

        case("valid_approved_action")
        case("action_amount_swapped",lambda p,t,a:a.update(amount_cents=900))
        case("forged_token_body",lambda p,t,a:t["body"].update(expires_at=9999))
        case("revoked_actor",lambda p,t,a:p.change(revoke_actor=ACTION["actor"]))
        case("changed_evidence",lambda p,t,a:p.change(subject=ACTION["subject"],status="FAIL"))
        case("changed_policy",lambda p,t,a:p.change(max_cents=500))
        case("false_source_still_passes",lambda p,t,a:p.seed(ACTION, truth=False))
        case("lost_response_then_readback",lose=True)
    # These are authored scenario oracles, not independently labelled cases.
    assert cases["valid_approved_action"]["code"]=="COMMITTED"
    assert cases["action_amount_swapped"]["code"]=="ACTION_BINDING_MISMATCH"
    assert cases["forged_token_body"]["code"]=="INVALID_TOKEN_AUTH"
    assert cases["revoked_actor"]["code"]=="REVOKED"
    assert cases["changed_evidence"]["code"]=="EVIDENCE_UNSATISFIED"
    assert cases["changed_policy"]["code"]=="POLICY_REVISION_CHANGED"
    assert cases["false_source_still_passes"]["code"]=="COMMITTED"  # negative control: trusted record false
    assert cases["lost_response_then_readback"]["code"]=="RESPONSE_LOST_AFTER_COMMIT"
    return {"status":"LOCAL_LAB_ONLY", "count":len(cases),"cases":cases}

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
