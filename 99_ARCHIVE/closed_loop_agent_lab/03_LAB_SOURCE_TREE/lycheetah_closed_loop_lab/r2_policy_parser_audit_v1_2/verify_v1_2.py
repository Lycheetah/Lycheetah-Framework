#!/usr/bin/env python3
"""Run bounded v1.2 checks without importing an upstream checkout."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parent
PATCH = ROOT / "strict_text_rule_parser_v1_2.patch"
CONTEXT = ROOT / "synthetic_policy_context_target.py"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def main():
    results=[]
    test = run([sys.executable, "-m", "unittest", "-v", "test_strict_candidate"], cwd=ROOT)
    results.append({"suite":"source_equivalent_candidate_unittest","exit_code":test.returncode,"stdout":test.stdout,"stderr":test.stderr})
    comp = run([sys.executable, "run_expanded_comparison.py"], cwd=ROOT)
    results.append({"suite":"source_equivalent_comparison","exit_code":comp.returncode,"stdout":comp.stdout,"stderr":comp.stderr})
    pyc = run([sys.executable, "-m", "py_compile", "test_assurance_policy_text_rule_types_v1_2.py", "preflight_upstream_v1_2.py"], cwd=ROOT)
    results.append({"suite":"upstream_test_syntax_compile","exit_code":pyc.returncode,"stdout":pyc.stdout,"stderr":pyc.stderr})

    temp = Path(tempfile.mkdtemp(prefix="lycheetah-patch-context-"))
    try:
        target=temp/"lycheetah/assurance/policy.py"
        target.parent.mkdir(parents=True)
        shutil.copyfile(CONTEXT,target)
        init=run(["git","init","-q"],cwd=temp)
        add=run(["git","add",str(target.relative_to(temp))],cwd=temp)
        commit=run(["git","-c","user.name=PatchFixture","-c","user.email=patch-fixture@example.invalid","commit","-qm","fixture baseline"],cwd=temp)
        preflight=run(["git","apply","--check",str(PATCH)],cwd=temp)
        results.append({"suite":"synthetic_patch_context_check","exit_code":preflight.returncode,"stdout":preflight.stdout,"stderr":preflight.stderr})
        if preflight.returncode == 0:
            apply=run(["git","apply",str(PATCH)],cwd=temp)
            diff=run(["git","diff","--",str(target.relative_to(temp))],cwd=temp)
            results.append({"suite":"synthetic_patch_apply","exit_code":apply.returncode,"stdout":diff.stdout,"stderr":apply.stderr})
            content=target.read_text(encoding="utf-8")
            results.append({"suite":"synthetic_patch_assertions","exit_code":0 if all(s in content for s in ["text rule.{field_name} must be a string","status_basis=data.get(\"status_basis\", \"\")","title=data.get(\"title\", data[\"id\"])"]) else 1,"stdout":"required strict checks present" if all(s in content for s in ["text rule.{field_name} must be a string","status_basis=data.get(\"status_basis\", \"\")","title=data.get(\"title\", data[\"id\"])"]) else "missing expected strict check","stderr":""})
    finally:
        shutil.rmtree(temp,ignore_errors=True)

    comparison=json.loads((ROOT/"comparison_results_v1_2.json").read_text(encoding="utf-8"))
    comparison_ok=(comparison["invalid_type_cases"]==30 and comparison["baseline_accepted_invalid_types"]==27 and comparison["candidate_rejected_invalid_types"]==30 and len(comparison["valid_compatibility_cases"])==4 and all(row["status"]=="ACCEPT" for row in comparison["valid_compatibility_cases"]))
    results.append({"suite":"comparison_result_contract","exit_code":0 if comparison_ok else 1,"stdout":json.dumps({k:comparison[k] for k in ("invalid_type_cases","baseline_accepted_invalid_types","candidate_rejected_invalid_types")},sort_keys=True),"stderr":"" if comparison_ok else "comparison contract failed"})

    payload={"status":"PASS_SEPARATE_LOCAL_CHECKS" if all(x["exit_code"]==0 for x in results) else "FAIL","upstream_package_tested":False,"tests":results,"note":"Synthetic context check is not a full upstream checkout or package test."}
    (ROOT/"verification_v1_2.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    with (ROOT/"verification_v1_2.log").open("w",encoding="utf-8") as f:
        for row in results:
            f.write(f"[{row['suite']}] exit_code={row['exit_code']}\n")
            if row["stdout"]: f.write(row["stdout"]+"\n")
            if row["stderr"]: f.write("STDERR:\n"+row["stderr"]+"\n")
    print(json.dumps({"status":payload["status"],"suites":[{"suite":x["suite"],"exit_code":x["exit_code"]} for x in results]},indent=2))
    return 0 if payload["status"]=="PASS_SEPARATE_LOCAL_CHECKS" else 1

if __name__=="__main__":
    raise SystemExit(main())
