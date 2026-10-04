#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import itertools
import json
import tempfile
import threading

from evidence_finality import Action
from evidence_finality import (
    AdmissionOnlyEvidenceBaseline,
    ConventionalDependencyOracle,
    EvidenceFinalityGate,
    EvidenceRequirement,
    GlobalEpochFreshnessBaseline,
)

ACCOUNT="deploy-budget"
PRINCIPAL="deploy-agent"
SCOPE="production:deploy"


def act(eid,sha="A"):
    return Action(
        principal=PRINCIPAL, tool="deployment", operation="promote",
        object_id=sha, destination="production",
        arguments={"artifact_sha":sha}, effect_id=eid
    )


def setup(db,budget=3):
    g=EvidenceFinalityGate(db)
    g.create_account(ACCOUNT,budget)
    g.activate(PRINCIPAL,SCOPE)
    g.put_evidence("ci-required","A","tests-1","PASS")
    g.put_evidence("security-scan","A","scan-1","PASS")
    g.put_evidence("unrelated-doc","docs","doc-1","PASS")
    return g


REQ_STATUS = EvidenceRequirement(
    "ci-required","SUBJECT_STATUS",required_status="PASS",
    required_subject_hash="A"
)
REQ_EXACT = EvidenceRequirement("security-scan","EXACT")


def scripted(tmp: Path):
    rows=[]

    # 1 happy path
    g=setup(tmp/"happy.sqlite")
    a=act("happy")
    ad=g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS,REQ_EXACT])
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"fresh-evidence-commits",
        "pass":ad.state=="RESERVED" and cm.state=="COMMITTED"
               and g.outbox_row(a.effect_id) is not None,
        "observed":{"admit":ad.__dict__,"commit":cm.__dict__}
    })

    # 2 reproduce admission-only gap
    b=AdmissionOnlyEvidenceBaseline()
    admitted=b.admit("old-gap",True)
    unsafe_after_change=b.commit("old-gap")
    rows.append({
        "case":"admission-only-baseline-counterexample",
        "pass":admitted and unsafe_after_change,
        "observed":{"admitted":admitted,"committed_after_evidence_change":unsafe_after_change},
        "interpretation":"Intentional counterexample: baseline does not revalidate."
    })

    # 3 required status flips to FAIL before finality
    g=setup(tmp/"status-fail.sqlite")
    a=act("status-fail")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,2,[REQ_STATUS])
    g.put_evidence("ci-required","A","tests-2","FAIL")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    snap=g.snapshot(ACCOUNT)
    rows.append({
        "case":"required-evidence-failure-blocks-finality-and-releases-reservation",
        "pass":cm.state=="DENY" and cm.reason=="evidence-stale-at-finality"
               and snap["reserved"]==0 and snap["committed_pending"]==0
               and g.outbox_row(a.effect_id) is None,
        "observed":{"commit":cm.__dict__,"snapshot":snap}
    })

    # 4 semantically equivalent newer PASS remains usable in SUBJECT_STATUS mode
    g=setup(tmp/"equiv-pass.sqlite")
    a=act("equiv-pass")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    g.put_evidence("ci-required","A","tests-2-new-receipt","PASS")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"newer-equivalent-pass-preserves-liveness",
        "pass":cm.state=="COMMITTED",
        "observed":cm.__dict__
    })

    # 5 exact witness rejects any revision change
    g=setup(tmp/"exact.sqlite")
    a=act("exact")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_EXACT])
    g.put_evidence("security-scan","A","scan-2","PASS")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"exact-evidence-mode-rejects-new-revision",
        "pass":cm.state=="DENY" and cm.evidence_key=="security-scan",
        "observed":cm.__dict__
    })

    # 6 unrelated churn does not block dependency-scoped gate, but global epoch does
    g=setup(tmp/"unrelated.sqlite")
    a=act("unrelated")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    global_gate=GlobalEpochFreshnessBaseline()
    global_gate.admit("unrelated")
    g.put_evidence("unrelated-doc","docs","doc-2","PASS")
    global_gate.update()
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"unrelated-evidence-change-does-not-cause-global-staleness",
        "pass":cm.state=="COMMITTED" and global_gate.commit("unrelated") is False,
        "observed":{
            "dependency_scoped":cm.__dict__,
            "global_epoch_would_allow":global_gate.commit("unrelated")
        }
    })

    # 7 evidence is PASS but for a different subject/artifact
    g=setup(tmp/"subject.sqlite")
    a=act("subject")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    g.put_evidence("ci-required","B","tests-B","PASS")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"pass-for-different-artifact-does-not-certify-target",
        "pass":cm.state=="DENY",
        "observed":cm.__dict__
    })

    # 8 evidence and authority are independent requirements
    g=setup(tmp/"authority.sqlite")
    a=act("authority")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    g.revoke(PRINCIPAL,SCOPE)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"fresh-evidence-cannot-override-revoked-authority",
        "pass":cm.state=="DENY" and g.outbox_row(a.effect_id) is None,
        "observed":cm.__dict__
    })

    # 9 restart preserves evidence witness
    db=tmp/"restart.sqlite"
    g=setup(db)
    a=act("restart")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    g=EvidenceFinalityGate(db)
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"restart-preserves-bound-evidence-witness",
        "pass":cm.state=="COMMITTED",
        "observed":cm.__dict__
    })

    # 10 unrelated status FAILURE still irrelevant when not a dependency
    g=setup(tmp/"unrelated-fail.sqlite")
    a=act("unrelated-fail")
    g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
    g.put_evidence("unrelated-doc","docs","doc-bad","FAIL")
    cm=g.commit(a.effect_id,a,{"sha":"A"})
    rows.append({
        "case":"unrelated-failure-does-not-poison-effect",
        "pass":cm.state=="COMMITTED",
        "observed":cm.__dict__
    })

    return rows


def concurrent_change_vs_commit(tmp: Path,trials=64):
    violations=[]
    finality_first=0
    evidence_first=0

    for i in range(trials):
        db=tmp/f"race-{i}.sqlite"
        g=setup(db,1)
        a=act(f"race-{i}")
        g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS])
        barrier=threading.Barrier(2)

        def do_commit(barrier=barrier, db=db, a=a, i=i):
            barrier.wait()
            EvidenceFinalityGate(db).commit(a.effect_id,a,{"i":i})

        def do_change(barrier=barrier, db=db, i=i):
            barrier.wait()
            EvidenceFinalityGate(db).put_evidence(
                "ci-required","A",f"tests-fail-{i}","FAIL"
            )

        t1=threading.Thread(target=do_commit)
        t2=threading.Thread(target=do_change)
        t1.start();t2.start();t1.join();t2.join()

        gate=EvidenceFinalityGate(db)
        audit=gate.audit()
        evseq=max(
            x["sequence"] for x in audit
            if x["kind"]=="EVIDENCE_UPDATE" and x["evidence_key"]=="ci-required"
        )
        finals=[x["sequence"] for x in audit if x["kind"]=="FINALITY_COMMIT"]
        stale=[x["sequence"] for x in audit if x["kind"]=="EVIDENCE_STALE"]

        if finals:
            finality_first+=1
            if not finals[0] < evseq:
                violations.append({"trial":i,"reason":"finality after invalidating evidence","audit":audit})
        else:
            evidence_first+=1
            if not stale or not evseq < stale[-1]:
                violations.append({"trial":i,"reason":"missing stale denial after evidence update","audit":audit})
            if gate.outbox_row(a.effect_id) is not None:
                violations.append({"trial":i,"reason":"outbox created despite evidence-first ordering","audit":audit})
        if not gate.invariant_holds(ACCOUNT):
            violations.append({"trial":i,"reason":"resource invariant failed","audit":audit})

    return {
        "trials":trials,
        "finality_ordered_first":finality_first,
        "invalidating_evidence_ordered_first":evidence_first,
        "violations":len(violations),
        "property_holds":not violations,
        "examples":violations[:5],
    }


def bounded_trace_check(tmp: Path):
    """All traces len 0..4 over:
       ADMIT, COMMIT, FAIL, EQUIV_PASS, UNRELATED
    = 1+5+25+125+625 = 781.
    Compare with independent dependency-scoped oracle.
    """
    alphabet=("AD","CM","FL","EP","UN")
    total=0
    correct=0
    mismatches=[]

    for length in range(5):
        for trace in itertools.product(alphabet,repeat=length):
            total+=1
            db=tmp/f"trace-{total}.sqlite"
            g=setup(db,1)
            oracle=ConventionalDependencyOracle()
            a=act(f"trace-{total}")
            obs=[]; exp=[]

            for op in trace:
                if op=="AD":
                    obs.append(g.admit(PRINCIPAL,SCOPE,ACCOUNT,a,1,[REQ_STATUS]).state)
                    exp.append(oracle.admit())
                elif op=="CM":
                    try:
                        obs.append(g.commit(a.effect_id,a,{"x":1}).state)
                    except KeyError:
                        obs.append("MISSING")
                    exp.append(oracle.commit())
                elif op=="FL":
                    g.put_evidence("ci-required","A",f"fail-{len(obs)}","FAIL")
                    oracle.required_fail()
                    obs.append("UPDATED");exp.append("UPDATED")
                elif op=="EP":
                    g.put_evidence("ci-required","A",f"pass-{len(obs)}","PASS")
                    oracle.required_equivalent_pass()
                    obs.append("UPDATED");exp.append("UPDATED")
                elif op=="UN":
                    g.put_evidence("unrelated-doc","docs",f"doc-{len(obs)}","PASS")
                    oracle.unrelated_change()
                    obs.append("UPDATED");exp.append("UPDATED")

            outbox = g.outbox_row(a.effect_id) is not None
            state_ok = (
                outbox == oracle.outbox
                and g.invariant_holds(ACCOUNT)
            )
            ok=obs==exp and state_ok
            correct+=int(ok)
            if not ok and len(mismatches)<10:
                mismatches.append({
                    "trace":trace,"observed":obs,"expected":exp,
                    "outbox":outbox,"oracle_outbox":oracle.outbox,
                    "audit":g.audit(),
                })

    return {
        "trace_space":"all AD/CM/FL/EP/UN traces length 0..4",
        "traces":total,"correct":correct,
        "all_correct":correct==total,
        "mismatches":mismatches
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lycheetah-evidence-finality-") as td:
        tmp=Path(td)
        cases=scripted(tmp)
        races=concurrent_change_vs_commit(tmp,64)
        traces=bounded_trace_check(tmp)

    report={
        "schema":"LYCHEETAH-DEPENDENCY-SCOPED-EVIDENCE-FINALITY-REPORT-1.0",
        "status":"SYNTHETIC_ENGINEERING_VALIDATED",
        "scripted_cases":cases,
        "scripted_summary":{
            "passed":sum(x["pass"] for x in cases),
            "total":len(cases)
        },
        "concurrent_evidence_vs_finality":races,
        "bounded_trace_check":traces,
        "deployment":"NOT_DEPLOYED",
        "boundaries":[
            "No real CI system, deployment platform, repository, or cloud provider was mutated.",
            "SQLite is the single serialization boundary; distributed replicas and telemetry delay are not modeled.",
            "Evidence producers are trusted control-plane writers in this prototype; signatures/attestation are not implemented.",
            "SUBJECT_STATUS precision depends on the declared predicate being complete for the hazard being controlled.",
            "EXACT mode can overblock benign equivalent revisions; SUBJECT_STATUS can underblock if its semantic predicate omits a relevant clause.",
            "The admission-only and global-epoch baselines are intentionally limited comparison points, not claims about all conventional systems.",
            "Dependency-scoped commit predicates, optimistic concurrency, and protected enforcement points are established ideas; novelty is not claimed."
        ]
    }
    Path("reports/report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True),encoding="utf-8"
    )

    print("Lycheetah Dependency-Scoped Evidence Finality Gate v1.0")
    print("=======================================================")
    print(f"Scripted checks: {report['scripted_summary']['passed']}/{report['scripted_summary']['total']}")
    print(f"Evidence/finality races: {races['trials']} violations={races['violations']} split={races['finality_ordered_first']}/{races['invalidating_evidence_ordered_first']}")
    print(f"Bounded traces: {traces['correct']}/{traces['traces']}")
    print("Status: synthetic engineering validation; not deployed.")


if __name__=="__main__":
    main()
