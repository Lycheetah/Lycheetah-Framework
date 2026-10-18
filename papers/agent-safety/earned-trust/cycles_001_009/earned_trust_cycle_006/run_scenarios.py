"""Fixed authored cases; no external provider calls or model-safety benchmark."""
import json
from pathlib import Path
from test_governed_registry import ARGS, fresh, witnesses, cosigned
from provenance_gate import naive_signed_quorum, sign_statement
from conventional_governance_baseline import decide


def scenario(name, preparation=None, names=("w_a","w_b"),
             witness_preparation=None, alterations=None, args_override=None,
             world_true=None):
    r=fresh()
    old=witnesses(r,names)
    if preparation:
        preparation(r)
    if witness_preparation:
        bound=witness_preparation(r)
    else:
        bound=witnesses(r,names)
    if alterations:
        alterations(bound)
    args={**ARGS, **(args_override or {})}
    if name == "no-trusted-checkpoint":
        anchor=None
    elif name == "stale-trusted-checkpoint":
        anchor={"genesis":r.genesis,"revision":0,"head":r.genesis}
    else:
        anchor=r.checkpoint()
    got=r.evaluate(bound,trusted_checkpoint=anchor,**args)
    conventional=decide(r,bound,trusted_checkpoint=anchor,**args)
    try:
        baseline=naive_signed_quorum(r._registry,[x["statement"] for x in bound],**args)
    except Exception as ex:
        baseline="ERROR:"+str(ex)
    return {"case":name,"naive_signed_quorum":baseline,"governed":got.decision,
            "conventional_matched":conventional,"reason":got.reason,"world_true":world_true}


def patch_shared(r):
    p=r.prepare("PATCH","w_b",controller="witness-b",upstream=["root_a"])
    r.apply(p,cosigned(r,p))

def challenge_root(r):
    p=r.prepare("CHALLENGE","root_a",reason="Investigator disputes its ancestry")
    r.apply(p,[r.sign(p,"auditor")])

def resolve_root(r):
    challenge_root(r)
    p=r.prepare("RESOLVE","root_a",resolution="DISMISSED",reason="Reviewed and dismissed by committee")
    r.apply(p,cosigned(r,p))

def change_unrelated(r):
    p=r.prepare("PATCH","w_c",controller="witness-c",upstream=["root_a"])
    r.apply(p,cosigned(r,p))

def stale_bound(r):
    # Fresh witness signed against previous head, then a valid registry change.
    pass

def swap(b): b[0]["statement"] = b[1]["statement"]
def bad_mac(b): b[0]["binding_mac"] = "0" * 64

def duplicate(b): b.append(b[0].copy())


def bad_observation(r):
    claims=witnesses(r)
    claims[0]=r.sign_bound_witness(sign_statement(r._registry,"w_a",effect_id=ARGS["effect_id"],
                    action_sha256=ARGS["action_sha256"],token_sha256=ARGS["token_sha256"],
                    status="NOT_COMMITTED",observed_at=110))
    return claims


def uncertain_observation(r):
    claims=witnesses(r)
    claims[0]=r.sign_bound_witness(sign_statement(r._registry,"w_a",effect_id=ARGS["effect_id"],
                    action_sha256=ARGS["action_sha256"],token_sha256=ARGS["token_sha256"],
                    correctness="UNKNOWN",observed_at=110))
    return claims


def copied_from_same_root(r):
    patch_shared(r)
    return witnesses(r)


def older_binding(r):
    old=witnesses(r)
    change_unrelated(r)
    return old


def main():
    rows=[
      scenario("clean-independent"),
      scenario("same-source-disclosed",witness_preparation=copied_from_same_root),
      scenario("challenge-active",preparation=challenge_root),
      scenario("challenge-dismissed",preparation=resolve_root),
      scenario("unaffected-witnesses",preparation=challenge_root,names=("w_b","w_c")),
      scenario("stale-registry-witness",witness_preparation=older_binding),
      scenario("no-trusted-checkpoint"),
      scenario("stale-trusted-checkpoint",preparation=change_unrelated),
      scenario("binding-tampered",alterations=bad_mac),
      scenario("statement-substituted",alterations=swap),
      scenario("duplicate-witness",alterations=duplicate),
      scenario("no-current-revision",args_override={"current_revisions":None}),
      scenario("stale-observation",args_override={"now":1000}),
      scenario("wrong-action",args_override={"action_sha256":"f"*64}),
      scenario("unverified-provider",args_override={"provider_receipt_valid":False}),
      scenario("explicit-negative",witness_preparation=bad_observation),
      scenario("uncertain-observation",witness_preparation=uncertain_observation),
      scenario("false-independent-world",world_true=False),
      scenario("hidden-shared-source",world_true=False),
      scenario("three-independent",names=("w_a","w_b","w_c")),
    ]
    assert len(rows)==20
    assert all(row["governed"]==row["conventional_matched"] for row in rows),rows
    return rows

if __name__=="__main__":
    print(json.dumps(main(),indent=2))
