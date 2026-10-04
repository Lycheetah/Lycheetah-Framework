#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import itertools
import json
import tempfile
import threading

from hazard_obligation_gate import (
    Action,
    ConventionalChecklistOracle,
    HazardObligationGate,
    Obligation,
    PresentedEvidenceBaseline,
)

ACCOUNT="deploy-budget"
PRINCIPAL="deploy-agent"
SCOPE="production:deploy"
CLASS="production-deploy"


POLICY_V1 = (
    Obligation("G_TESTS","O_TESTS","H_UNTESTED","ci-required"),
    Obligation("G_SECURITY","O_SECURITY","H_VULNERABLE","security-scan"),
    Obligation("G_REVERSIBLE","O_ROLLBACK","H_UNRECOVERABLE","rollback-plan"),
    Obligation("G_REVERSIBLE","O_BLUEGREEN","H_UNRECOVERABLE","bluegreen-ready"),
    Obligation("G_CANARY","O_CANARY","H_UNHEALTHY_ROLLOUT","canary-health"),
)

POLICY_V2 = POLICY_V1 + (
    Obligation("G_SIGNED","O_SIGNED","H_UNTRUSTED_ARTIFACT","artifact-signature"),
)


def action(eid,sha="A"):
    return Action(
        principal=PRINCIPAL,tool="deployment",operation="promote",
        object_id=sha,destination="production",
        arguments={"artifact_sha":sha},effect_id=eid
    )


def setup(db,policy_version=1):
    g=HazardObligationGate(db)
    g.create_account(ACCOUNT,3)
    g.activate_authority(PRINCIPAL,SCOPE)
    g.install_policy(CLASS,policy_version,POLICY_V1 if policy_version==1 else POLICY_V2)
    g.put_evidence("ci-required","A","PASS")
    g.put_evidence("security-scan","A","PASS")
    g.put_evidence("rollback-plan","A","PASS")
    g.put_evidence("bluegreen-ready","A","FAIL")
    g.put_evidence("canary-health","A","PASS")
    if policy_version >= 2:
        g.put_evidence("artifact-signature","A","PASS")
    return g


def scripted(tmp: Path):
    rows=[]

    # 1 complete policy happy path
    g=setup(tmp/"happy.sqlite")
    a=action("happy")
    ad=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"complete-hazard-obligation-policy-commits",
        "pass":ad.state=="RESERVED" and cm.state=="COMMITTED",
        "observed":{"admit":ad.__dict__,"commit":cm.__dict__}
    })

    # 2 weak baseline: only green tests and canary presented; security/rollback omitted
    weak=PresentedEvidenceBaseline.allow(["PASS","PASS"])
    g=setup(tmp/"omission.sqlite")
    g.put_evidence("security-scan","A","FAIL")
    g.put_evidence("rollback-plan","A","FAIL")
    g.put_evidence("bluegreen-ready","A","FAIL")
    denied=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,action("omission"),1)
    rows.append({
        "case":"caller-cannot-omit-mandatory-groups",
        "pass":weak is True and denied.state=="DENY"
               and denied.reason=="mandatory-obligation-unsatisfied",
        "observed":{"weak_presented_evidence_allows":weak,"gate":denied.__dict__}
    })

    # 3 one mandatory singleton fails
    g=setup(tmp/"security-fail.sqlite")
    g.put_evidence("security-scan","A","FAIL")
    d=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,action("security-fail"),1)
    rows.append({
        "case":"mandatory-security-group-noncompensatory",
        "pass":d.state=="DENY" and d.group_id=="G_SECURITY",
        "observed":d.__dict__
    })

    # 4 rollback alternative fails but bluegreen alternative passes => liveness
    g=setup(tmp/"alternative.sqlite")
    g.put_evidence("rollback-plan","A","FAIL")
    g.put_evidence("bluegreen-ready","A","PASS")
    a=action("alternative")
    ad=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"allowed-alternative-control-preserves-liveness",
        "pass":ad.state=="RESERVED" and cm.state=="COMMITTED",
        "observed":{"admit":ad.__dict__,"commit":cm.__dict__}
    })

    # 5 both reversible controls fail
    g=setup(tmp/"alt-fail.sqlite")
    g.put_evidence("rollback-plan","A","FAIL")
    g.put_evidence("bluegreen-ready","A","FAIL")
    d=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,action("alt-fail"),1)
    rows.append({
        "case":"all-alternatives-failing-blocks-group",
        "pass":d.state=="DENY" and d.group_id=="G_REVERSIBLE",
        "observed":d.__dict__
    })

    # 6 policy becomes stricter after admission
    g=setup(tmp/"policy-change.sqlite")
    a=action("policy-change")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
    g.put_evidence("artifact-signature","A","PASS")
    g.install_policy(CLASS,2,POLICY_V2)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"policy-version-change-invalidates-old-admission",
        "pass":cm.state=="DENY" and cm.reason=="policy-version-changed"
               and g.outbox_row(a.effect_id) is None,
        "observed":cm.__dict__
    })

    # 7 update to an unrelated effect class does not invalidate deploy
    g=setup(tmp/"unrelated-policy.sqlite")
    a=action("unrelated-policy")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
    g.install_policy(
        "public-report",1,
        (Obligation("G_REVIEW","O_REVIEW","H_UNREVIEWED","report-review",
                    bind_subject_to_action_object=False),)
    )
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"unrelated-policy-update-does-not-block",
        "pass":cm.state=="COMMITTED",
        "observed":cm.__dict__
    })

    # 8 required evidence fails after admission, before finality
    g=setup(tmp/"late-fail.sqlite")
    a=action("late-fail")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,2)
    g.put_evidence("canary-health","A","FAIL")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    snap=g.snapshot(ACCOUNT)
    rows.append({
        "case":"mandatory-obligation-rechecked-at-finality",
        "pass":cm.state=="DENY" and cm.group_id=="G_CANARY"
               and snap["reserved"]==0 and g.outbox_row(a.effect_id) is None,
        "observed":{"commit":cm.__dict__,"snapshot":snap}
    })

    # 9 evidence PASS for wrong artifact
    g=setup(tmp/"wrong-subject.sqlite")
    g.put_evidence("ci-required","B","PASS")
    d=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,action("wrong-subject","A"),1)
    rows.append({
        "case":"green-check-for-wrong-artifact-does-not-cover-obligation",
        "pass":d.state=="DENY" and d.group_id=="G_TESTS",
        "observed":d.__dict__
    })

    # 10 missing evidence is closed-world deny, not "not mentioned"
    g=HazardObligationGate(tmp/"missing.sqlite")
    g.create_account(ACCOUNT,3)
    g.activate_authority(PRINCIPAL,SCOPE)
    g.install_policy(CLASS,1,POLICY_V1)
    g.put_evidence("ci-required","A","PASS")
    # intentionally omit security, rollback/bluegreen, canary
    d=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,action("missing"),1)
    rows.append({
        "case":"missing-mandatory-evidence-denies",
        "pass":d.state=="DENY",
        "observed":d.__dict__
    })

    # 11 authority remains independent of obligation coverage
    g=setup(tmp/"authority.sqlite")
    a=action("authority")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
    g.revoke_authority(PRINCIPAL,SCOPE)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"complete-obligation-coverage-cannot-override-revocation",
        "pass":cm.state=="DENY" and g.outbox_row(a.effect_id) is None,
        "observed":cm.__dict__
    })

    return rows


def exhaustive_boolean_coverage(tmp: Path):
    """All 2^5 evidence states for T,S,R,B,C.

    Oracle = T and S and C and (R or B).
    """
    correct=0
    total=0
    mismatches=[]
    for bits in itertools.product((False,True),repeat=5):
        T,S,R,B,C=bits
        total+=1
        db=tmp/f"bool-{total}.sqlite"
        g=HazardObligationGate(db)
        g.create_account(ACCOUNT,1)
        g.activate_authority(PRINCIPAL,SCOPE)
        g.install_policy(CLASS,1,POLICY_V1)
        for key,val in (
            ("ci-required",T),("security-scan",S),("rollback-plan",R),
            ("bluegreen-ready",B),("canary-health",C)
        ):
            g.put_evidence(key,"A","PASS" if val else "FAIL")
        a=action(f"bool-{total}")
        observed=g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1).state=="RESERVED"
        expected=ConventionalChecklistOracle.allow(T,S,R,B,C)
        ok=observed==expected
        correct+=int(ok)
        if not ok:
            mismatches.append({"bits":bits,"observed":observed,"expected":expected})
    return {
        "states":total,"correct":correct,"all_correct":correct==total,
        "mismatches":mismatches[:10]
    }


def policy_update_vs_commit_race(tmp: Path,trials=64):
    violations=[]
    finality_first=0
    policy_first=0

    for i in range(trials):
        db=tmp/f"race-{i}.sqlite"
        g=setup(db)
        a=action(f"race-{i}")
        g.admit(PRINCIPAL,SCOPE,ACCOUNT,CLASS,a,1)
        g.put_evidence("artifact-signature","A","PASS")
        barrier=threading.Barrier(2)

        def do_commit(barrier=barrier, db=db, a=a, i=i):
            barrier.wait()
            HazardObligationGate(db).commit(a.effect_id,a,{"trial":i})

        def do_policy(barrier=barrier, db=db):
            barrier.wait()
            HazardObligationGate(db).install_policy(CLASS,2,POLICY_V2)

        t1=threading.Thread(target=do_commit)
        t2=threading.Thread(target=do_policy)
        t1.start();t2.start();t1.join();t2.join()

        gate=HazardObligationGate(db)
        audit=gate.audit()
        pseq=max(
            x["sequence"] for x in audit
            if x["kind"]=="POLICY_INSTALL" and x["effect_class"]==CLASS
        )
        finals=[x["sequence"] for x in audit if x["kind"]=="FINALITY_COMMIT"]
        stale=[x["sequence"] for x in audit if x["kind"]=="POLICY_STALE"]

        if finals:
            finality_first+=1
            if not finals[0] < pseq:
                violations.append({"trial":i,"reason":"finality after policy update","audit":audit})
        else:
            policy_first+=1
            if not stale or not pseq < stale[-1]:
                violations.append({"trial":i,"reason":"no stale denial after policy-first","audit":audit})
            if gate.outbox_row(a.effect_id) is not None:
                violations.append({"trial":i,"reason":"outbox exists after policy-first","audit":audit})
        if not gate.invariant_holds(ACCOUNT):
            violations.append({"trial":i,"reason":"resource invariant failed","audit":audit})

    return {
        "trials":trials,
        "finality_ordered_first":finality_first,
        "policy_update_ordered_first":policy_first,
        "violations":len(violations),
        "property_holds":not violations,
        "examples":violations[:5]
    }


def omission_subsets():
    """Illustrate the weak caller-presented-check problem.

    Required singleton names shown to the human: tests/security/canary/rollback.
    Any nonempty subset of PASS values fools the weak baseline; only full
    hazard coverage should authorize. This is diagnostic, not a production rate.
    """
    names=("tests","security","reversible","canary")
    rows=[]
    for r in range(1,len(names)+1):
        for subset in itertools.combinations(names,r):
            weak=PresentedEvidenceBaseline.allow(["PASS"]*len(subset))
            complete=set(subset)==set(names)
            rows.append({
                "presented":subset,
                "weak_allow":weak,
                "actually_complete":complete,
                "unsafe_weak_allow":weak and not complete
            })
    return {
        "nonempty_subsets":len(rows),
        "unsafe_weak_allows":sum(x["unsafe_weak_allow"] for x in rows),
        "complete_subsets":sum(x["actually_complete"] for x in rows),
        "rows":rows
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lycheetah-obligations-") as td:
        tmp=Path(td)
        cases=scripted(tmp)
        finite=exhaustive_boolean_coverage(tmp)
        races=policy_update_vs_commit_race(tmp,64)
    omissions=omission_subsets()

    report={
        "schema":"LYCHEETAH-HAZARD-OBLIGATION-COVERAGE-GATE-REPORT-1.1",
        "status":"SYNTHETIC_ENGINEERING_VALIDATED",
        "scripted_cases":cases,
        "scripted_summary":{
            "passed":sum(x["pass"] for x in cases),
            "total":len(cases)
        },
        "finite_coverage_verification":finite,
        "policy_update_vs_finality":races,
        "presented_evidence_omission_diagnostic":omissions,
        "deployment":"NOT_DEPLOYED",
        "boundaries":[
            "The declared hazard policy is self-authored and not a complete production hazard analysis.",
            "Passing every declared obligation proves only policy-relative coverage, not universal safety.",
            "Evidence producers are trusted structured inputs in this prototype.",
            "No real CI system, deployment service, repository, or cloud provider was modified.",
            "SQLite is one-node serialized state; distributed policy propagation is not modeled.",
            "The weak presented-evidence baseline is intentionally omission-blind and is not representative of mature deployment checklists.",
            "The matched conventional checklist is expected to tie the closed-world policy semantics.",
            "STPA/hazard-derived requirements, safety checklists, conjunctions, alternative controls, and policy versioning are established approaches; novelty is not claimed."
        ]
    }
    Path("reports/report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True),encoding="utf-8"
    )

    print("Lycheetah Hazard Obligation Coverage Gate v1.1")
    print("==============================================")
    print(f"Scripted checks: {report['scripted_summary']['passed']}/{report['scripted_summary']['total']}")
    print(f"Finite evidence states: {finite['correct']}/{finite['states']}")
    print(f"Policy/finality races: {races['trials']} violations={races['violations']} split={races['finality_ordered_first']}/{races['policy_update_ordered_first']}")
    print(f"Weak presented-check omission diagnostic: unsafe allows={omissions['unsafe_weak_allows']}/{omissions['nonempty_subsets']} nonempty subsets")
    print("Status: synthetic engineering validation; not deployed.")


if __name__=="__main__":
    main()
