#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import itertools, json, tempfile

from policy_evolution_gate import (
    Obligation, Group, Policy, PolicyEvolutionGate,
    brute_force_relation, semantic_relation_structural, policy_formula
)


PID="production-deploy"


def ob(oid,hid=None):
    return Obligation(oid,hid or f"H_{oid}",f"ev:{oid}")


BASE = Policy(PID,1,(
    Group("G_TESTS",(ob("T","H_UNTESTED"),)),
    Group("G_SECURITY",(ob("S","H_VULNERABLE"),)),
    Group("G_REVERSIBLE",(ob("R","H_UNRECOVERABLE"),ob("B","H_UNRECOVERABLE"))),
    Group("G_CANARY",(ob("C","H_UNHEALTHY"),)),
))

SIG_GROUP = Group("G_SIGNED",(ob("SIG","H_UNTRUSTED_ARTIFACT"),))


def base_fixtures(g):
    # One positive, plus one frozen negative per base group.
    all_good={"T":True,"S":True,"R":True,"B":False,"C":True,"SIG":True}
    g.add_fixture("F_ALLOW_BASE",PID,all_good,True,"initial-safety-case")
    g.add_fixture("F_DENY_NO_TEST",PID,{**all_good,"T":False},False,"initial-safety-case")
    g.add_fixture("F_DENY_NO_SECURITY",PID,{**all_good,"S":False},False,"initial-safety-case")
    g.add_fixture("F_DENY_NO_REVERSIBLE",PID,{**all_good,"R":False,"B":False},False,"initial-safety-case")
    g.add_fixture("F_DENY_NO_CANARY",PID,{**all_good,"C":False},False,"initial-safety-case")


def scripted(tmp: Path):
    rows=[]

    # 1 Incident creates known lesson; stronger policy + incident regression activates.
    db=tmp/"incident.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    g.record_incident("INC-001","H_UNTRUSTED_ARTIFACT","HIGH",
                      "Near-miss: unsigned artifact reached deployment queue")
    g.map_incident("INC-001","G_SIGNED")
    g.add_fixture(
        "F_INC001_UNSIGNED_DENY",PID,
        {"T":True,"S":True,"R":True,"B":False,"C":True,"SIG":False},
        False,"incident:INC-001"
    )
    v2=Policy(PID,2,BASE.groups+(SIG_GROUP,))
    rel=g.propose(v2); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"incident-derived-stronger-policy-activates",
        "pass":rel=="STRONGER" and d.state=="ACTIVE"
               and g.incident_state("INC-001")["state"]=="COVERED",
        "observed":{"relation":rel,"decision":d.__dict__,
                    "incident":g.incident_state("INC-001")}
    })

    # 2 Same incident, but candidate does not map its hazard.
    db=tmp/"wrong-map.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    g.record_incident("INC-002","H_UNTRUSTED_ARTIFACT","HIGH","unsigned artifact")
    g.map_incident("INC-002","G_TESTS")
    v2=Policy(PID,2,BASE.groups+(SIG_GROUP,))
    g.propose(v2); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"incident-must-map-to-matching-hazard-control",
        "pass":d.state=="STOPPED" and d.reason=="incident-mapping-not-covered-by-candidate",
        "observed":d.__dict__
    })

    # 3 High incident with no mapping blocks activation.
    db=tmp/"unmapped.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    g.record_incident("INC-003","H_UNTRUSTED_ARTIFACT","CRITICAL","unsigned")
    v2=Policy(PID,2,BASE.groups+(SIG_GROUP,))
    g.propose(v2); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"unmapped-high-severity-incident-blocks-policy-activation",
        "pass":d.state=="STOPPED" and d.reason=="high-severity-incident-unmapped",
        "observed":d.__dict__
    })

    # 4 Silent removal of mandatory security group is weakening.
    db=tmp/"remove-group.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    weak=Policy(PID,2,tuple(x for x in BASE.groups if x.group_id!="G_SECURITY"))
    rel=g.propose(weak); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"mandatory-group-removal-is-stopped",
        "pass":rel=="WEAKER" and d.state=="STOPPED",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 5 Adding an OR alternative weakens the hazard group.
    db=tmp/"add-alt.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    alt=Policy(PID,2,tuple(
        Group(x.group_id,x.obligations+(ob("MANUAL","H_UNRECOVERABLE"),))
        if x.group_id=="G_REVERSIBLE" else x
        for x in BASE.groups
    ))
    rel=g.propose(alt); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"adding-alternative-is-recognized-as-weaker",
        "pass":rel=="WEAKER" and d.state=="STOPPED",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 6 Removing an alternative tightens policy and can activate if fixtures pass.
    db=tmp/"remove-alt.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    strict=Policy(PID,2,tuple(
        Group(x.group_id,(ob("R","H_UNRECOVERABLE"),))
        if x.group_id=="G_REVERSIBLE" else x
        for x in BASE.groups
    ))
    rel=g.propose(strict); d=g.activate_candidate(PID,2)
    rows.append({
        "case":"removing-an-alternative-is-stronger",
        "pass":rel=="STRONGER" and d.state=="ACTIVE",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 7 Incomparable replacement is stopped.
    db=tmp/"replace.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    replacement=Policy(PID,2,tuple(
        Group(x.group_id,(ob("B","H_UNRECOVERABLE"),ob("MANUAL","H_UNRECOVERABLE")))
        if x.group_id=="G_REVERSIBLE" else x
        for x in BASE.groups
    ))
    rel=g.propose(replacement);d=g.activate_candidate(PID,2)
    rows.append({
        "case":"mixed-control-replacement-requires-external-review",
        "pass":rel=="INCOMPARABLE" and d.state=="STOPPED",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 8 Regression fixture can stop even a structurally stronger policy.
    # Add group G_SIGNED but frozen ALLOW_BASE fixture lacks SIG=True -> should fail.
    db=tmp/"regression.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE)
    # Deliberately fixture from legacy expected-allow state omits new obligation.
    g.add_fixture("F_LEGACY_ALLOW",PID,
                  {"T":True,"S":True,"R":True,"B":False,"C":True},
                  True,"legacy-release-fixture")
    v2=Policy(PID,2,BASE.groups+(SIG_GROUP,))
    rel=g.propose(v2);d=g.activate_candidate(PID,2)
    rows.append({
        "case":"stronger-policy-still-requires-regression-reconciliation",
        "pass":rel=="STRONGER" and d.state=="STOPPED"
               and d.reason=="regression-fixture-failed",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 9 Low-severity incident does not block activation in this v1.2 policy.
    db=tmp/"low.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    g.record_incident("INC-LOW","H_OBS","LOW","observational anomaly")
    equivalent=Policy(PID,2,BASE.groups)
    rel=g.propose(equivalent);d=g.activate_candidate(PID,2)
    rows.append({
        "case":"low-severity-observation-does-not-auto-block",
        "pass":rel=="EQUIVALENT" and d.state=="ACTIVE",
        "observed":{"relation":rel,"decision":d.__dict__}
    })

    # 10 Restart preserves proposed policy and incident linkage.
    db=tmp/"restart.sqlite"
    g=PolicyEvolutionGate(db);g.install_initial(BASE);base_fixtures(g)
    g.record_incident("INC-R","H_UNTRUSTED_ARTIFACT","HIGH","unsigned")
    g.map_incident("INC-R","G_SIGNED")
    g.add_fixture(
        "F_INC_R",PID,
        {"T":True,"S":True,"R":True,"B":False,"C":True,"SIG":False},
        False,"incident:INC-R"
    )
    v2=Policy(PID,2,BASE.groups+(SIG_GROUP,))
    g.propose(v2)
    g=PolicyEvolutionGate(db)
    d=g.activate_candidate(PID,2)
    rows.append({
        "case":"restart-preserves-policy-evolution-state",
        "pass":d.state=="ACTIVE",
        "observed":d.__dict__
    })

    return rows


def exhaustive_semantic_classifier():
    """Compare structural classifier to brute-force implication on 64 candidate
    policies derived from a base formula.

    Base: A ∧ B ∧ (C1∨C2)
    Candidate dimensions:
      G_A present/absent
      G_B present/absent
      G_C absent or any nonempty subset of C1,C2,C3 (8 options total)
      G_D present/absent
    => 2*2*8*2 = 64 candidates.
    """
    p0=Policy("P",1,(
        Group("GA",(ob("A"),)),
        Group("GB",(ob("B"),)),
        Group("GC",(ob("C1"),ob("C2"))),
    ))
    c_options=[None]+[
        tuple(ob(x) for x in subset)
        for r in (1,2,3)
        for subset in itertools.combinations(("C1","C2","C3"),r)
    ]
    rows=[]
    for ga in (False,True):
        for gb in (False,True):
            for gc in c_options:
                for gd in (False,True):
                    groups=[]
                    if ga: groups.append(Group("GA",(ob("A"),)))
                    if gb: groups.append(Group("GB",(ob("B"),)))
                    if gc is not None: groups.append(Group("GC",gc))
                    if gd: groups.append(Group("GD",(ob("D"),)))
                    cand=Policy("P",2,tuple(groups))
                    structural=semantic_relation_structural(p0,cand)
                    oracle=brute_force_relation(p0,cand)
                    rows.append({
                        "ga":ga,"gb":gb,
                        "gc":None if gc is None else [x.obligation_id for x in gc],
                        "gd":gd,"structural":structural,"oracle":oracle,
                        "match":structural==oracle
                    })
    return {
        "candidates":len(rows),
        "correct":sum(x["match"] for x in rows),
        "all_correct":all(x["match"] for x in rows),
        "mismatches":[x for x in rows if not x["match"]][:10]
    }


def naive_version_baseline_diagnostic():
    """Naive change control: accept any numerically newer version."""
    p0=Policy("P",1,(
        Group("GA",(ob("A"),)),
        Group("GB",(ob("B"),)),
        Group("GC",(ob("C1"),ob("C2"))),
    ))
    candidates=[
        Policy("P",2,(Group("GA",(ob("A"),)),Group("GC",(ob("C1"),ob("C2"))))), # remove GB
        Policy("P",2,p0.groups[:-1]), # remove GC
        Policy("P",2,(
            Group("GA",(ob("A"),)),Group("GB",(ob("B"),)),
            Group("GC",(ob("C1"),ob("C2"),ob("C3")))
        )),
    ]
    return {
        "newer_versions_accepted_by_naive_counter":len(candidates),
        "semantically_weaker":sum(
            brute_force_relation(p0,c)=="WEAKER" for c in candidates
        ),
        "relations":[brute_force_relation(p0,c) for c in candidates]
    }


def main():
    Path("reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lycheetah-policy-evolution-") as td:
        cases=scripted(Path(td))
    classifier=exhaustive_semantic_classifier()
    naive=naive_version_baseline_diagnostic()

    report={
        "schema":"LYCHEETAH-HAZARD-LINEAGE-POLICY-EVOLUTION-REPORT-1.2",
        "status":"SYNTHETIC_ENGINEERING_VALIDATED",
        "scripted_cases":cases,
        "scripted_summary":{
            "passed":sum(x["pass"] for x in cases),"total":len(cases)
        },
        "semantic_classifier_exhaustive":classifier,
        "naive_version_baseline":naive,
        "deployment":"NOT_DEPLOYED",
        "boundaries":[
            "Incident severity, hazard identity, mapping, and regression fixtures are self-authored synthetic inputs.",
            "v1.2 permits automatic activation only for semantically equivalent or stronger policies; legitimate weakening/control retirement needs an external process not implemented here.",
            "Monotonic strengthening can accumulate obsolete controls and harm availability if never reviewed.",
            "Regression fixtures can only catch scenarios represented in the fixture set.",
            "Incident traceability ensures known high/critical incidents are mapped, not that all real hazards have been discovered.",
            "No real production incident, CI/CD system, regulator, or deployment platform was used.",
            "Management of change, safety-case maintenance, hazard analysis, regression testing, and traceability are established prior art; novelty is not claimed."
        ]
    }
    Path("reports/report.json").write_text(
        json.dumps(report,indent=2,sort_keys=True),encoding="utf-8"
    )

    print("Lycheetah Hazard Lineage + Policy Evolution Gate v1.2")
    print("=====================================================")
    print(f"Scripted checks: {report['scripted_summary']['passed']}/{report['scripted_summary']['total']}")
    print(f"Semantic classifier: {classifier['correct']}/{classifier['candidates']}")
    print(f"Naive newer-version diagnostic: weaker accepted={naive['semantically_weaker']}/{naive['newer_versions_accepted_by_naive_counter']}")
    print("Status: synthetic engineering validation; not deployed.")


if __name__=="__main__":
    main()
