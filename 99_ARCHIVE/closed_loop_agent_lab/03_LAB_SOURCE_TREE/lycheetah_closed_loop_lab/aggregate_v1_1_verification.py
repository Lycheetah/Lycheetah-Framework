#!/usr/bin/env python3
"""Aggregate completed per-suite v1.1 records without rerunning any suite."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITES = [
    "legacy_v0_1_to_v0_6",
    "crash_recovery_v0_7",
    "trusted_catalog_v0_8",
    "catalog_issuance_v0_9",
    "crash_recovery_v0_9",
    "policy_parser_source_equivalent_fixture",
]
results = []
for name in SUITES:
    path = ROOT / "verification_v1_1" / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"missing per-suite result: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("suite") != name:
        raise SystemExit(f"unexpected suite identity in {path}")
    results.append(result)

comparison = json.loads((ROOT / "r2_policy_parser_audit/comparison_results.json").read_text(encoding="utf-8"))
checks = {
    "all_suites_pass": all(item.get("status") == "PASS" for item in results),
    "parser_probe_count_is_24": comparison.get("invalid_type_cases") == 24,
    "baseline_accepts_21_invalid_types": comparison.get("baseline_accepted_invalid_types") == 21,
    "candidate_rejects_all_24": comparison.get("candidate_rejected_invalid_types") == 24,
}
summary = {
    "version": "1.1",
    "status": "PASS_SEPARATE_SUITES" if all(checks.values()) else "FAIL_OR_INCOMPLETE",
    "tests_reported_across_completed_separate_suites": sum(int(item["expected_test_methods"]) for item in results),
    "suite_results": results,
    "checks": checks,
    "parser_comparison": {
        "status": comparison["status"],
        "malformed_type_cases": comparison["invalid_type_cases"],
        "baseline_accepts_invalid": comparison["baseline_accepted_invalid_types"],
        "candidate_rejects_invalid": comparison["candidate_rejected_invalid_types"],
    },
    "upstream_package_suite_run": False,
    "public_repository_modified": False,
    "limitations": [
        "The per-suite test methods are authored local reference/harness tests, not model-efficacy measures.",
        "The parser experiment uses a source-equivalent fixture; upstream patch/tests were not integrated because GitHub branch creation is read-only in this session.",
        "The inspected upstream CI baseline has unresolved failed checks with unavailable logs.",
        "No real provider, authenticated human reviewer, or production host was tested.",
    ],
}
(ROOT / "verification_v1_1.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": summary["status"], "test_methods": summary["tests_reported_across_completed_separate_suites"], "checks": checks}, indent=2))
if summary["status"] != "PASS_SEPARATE_SUITES":
    raise SystemExit(1)
