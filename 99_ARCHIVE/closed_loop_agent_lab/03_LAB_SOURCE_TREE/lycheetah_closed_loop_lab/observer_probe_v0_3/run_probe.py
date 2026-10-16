#!/usr/bin/env python3
"""Compare weak public checks with contract-driven checks on known variants.

This is evaluator calibration, not an LLM benchmark. Candidate labels are
specified before results are computed. All task implementations are local.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from candidates import CANDIDATES

ROOT = Path(__file__).resolve().parent

# The toy/public suite deliberately checks only common operating points.
PUBLIC_CASES = [
    ("base_attempt_zero", (0, 1.0, 100.0), 1.0),
    ("first_retry", (1, 1.0, 100.0), 2.0),
    ("ordinary_growth", (3, 1.0, 100.0), 8.0),
]

# The contract suite adds boundaries, invalid inputs, cap invariants and huge attempts.
VALUE_CASES = [
    ("zero_attempt", (0, 1.0, 100.0), 1.0),
    ("one_attempt", (1, 1.0, 100.0), 2.0),
    ("ordinary_growth", (3, 1.0, 100.0), 8.0),
    ("cap_small", (10, 1.0, 5.0), 5.0),
    ("very_large_attempt", (10000, 1.0, 30.0), 30.0),
    ("zero_base", (999, 0.0, 30.0), 0.0),
    ("zero_cap", (999, 3.0, 0.0), 0.0),
    ("base_above_cap", (0, 8.0, 5.0), 5.0),
    ("fractional_base", (2, 0.25, 3.0), 1.0),
    ("fractional_cap", (10, 0.25, 0.9), 0.9),
]
ERROR_CASES = [
    ("negative_attempt", (-1, 1.0, 10.0), ValueError),
    ("bool_attempt", (True, 1.0, 10.0), TypeError),
    ("float_attempt", (1.0, 1.0, 10.0), TypeError),
    ("negative_base", (0, -1.0, 10.0), ValueError),
    ("negative_cap", (0, 1.0, -1.0), ValueError),
    ("nan_base", (0, float("nan"), 10.0), ValueError),
    ("inf_cap", (0, 1.0, float("inf")), ValueError),
    ("string_base", (0, "1", 10.0), TypeError),
    ("bool_base", (0, True, 10.0), TypeError),
]


def outcome(fn, args, expected_value=None, expected_error=None):
    try:
        result = fn(*args)
    except Exception as exc:  # fixture intentionally captures expected and unexpected exceptions
        if expected_error and isinstance(exc, expected_error):
            return True, f"expected {type(exc).__name__}"
        return False, f"raised {type(exc).__name__}: {exc}"
    if expected_error:
        return False, f"expected {expected_error.__name__}, returned {result!r}"
    if isinstance(result, bool) or not isinstance(result, (int, float)):
        return False, f"non-numeric or boolean result: {result!r}"
    if not math.isfinite(float(result)):
        return False, f"non-finite result: {result!r}"
    if not math.isclose(float(result), float(expected_value), rel_tol=1e-12, abs_tol=1e-12):
        return False, f"expected {expected_value!r}, got {result!r}"
    # Contract invariant: output remains in [0, cap].
    if result < 0 or result > args[2]:
        return False, f"out-of-range result {result!r} for cap {args[2]!r}"
    return True, f"returned {result!r}"


def evaluate(fn, cases, include_errors=False):
    failures = []
    for name, args, expected in cases:
        ok, detail = outcome(fn, args, expected_value=expected)
        if not ok:
            failures.append({"case": name, "detail": detail})
    for name, args, err in ERROR_CASES if include_errors else []:
        ok, detail = outcome(fn, args, expected_error=err)
        if not ok:
            failures.append({"case": name, "detail": detail})
    return {"checks": len(cases) + (len(ERROR_CASES) if include_errors else 0),
            "passed": len(cases) + (len(ERROR_CASES) if include_errors else 0) - len(failures),
            "failures": failures,
            "accepted": not failures}


def main():
    rows = []
    for name, (fn, known_valid) in CANDIDATES.items():
        public = evaluate(fn, PUBLIC_CASES)
        contract = evaluate(fn, VALUE_CASES, include_errors=True)
        rows.append({
            "candidate": name,
            "predeclared_label": "valid_alternative" if known_valid else "planted_defect",
            "public_checks_passed": public["passed"],
            "public_checks_total": public["checks"],
            "public_suite_accepts": public["accepted"],
            "contract_checks_passed": contract["passed"],
            "contract_checks_total": contract["checks"],
            "contract_suite_accepts": contract["accepted"],
            "contract_failures": contract["failures"],
        })
    public_accepted = [r for r in rows if r["public_suite_accepts"]]
    contract_accepted = [r for r in rows if r["contract_suite_accepts"]]
    valid_names = {r["candidate"] for r in rows if r["predeclared_label"] == "valid_alternative"}
    summary = {
        "status": "LOCAL_EVALUATOR_CALIBRATION_NOT_AGENT_EVALUATION",
        "task": "bounded exponential retry delay with strict input contract and overflow-safe cap",
        "candidate_count": len(rows),
        "known_valid_implementations": sorted(valid_names),
        "planted_defect_count": sum(not r["predeclared_label"] == "valid_alternative" for r in rows),
        "public_suite": {
            "checks": len(PUBLIC_CASES),
            "accepted_candidates": [r["candidate"] for r in public_accepted],
            "accepted_known_defects": [r["candidate"] for r in public_accepted if r["predeclared_label"] == "planted_defect"],
            "false_accepts_among_known_defects": sum(r["predeclared_label"] == "planted_defect" for r in public_accepted),
            "valid_alternatives_rejected": [r["candidate"] for r in rows if r["predeclared_label"] == "valid_alternative" and not r["public_suite_accepts"]],
        },
        "contract_suite": {
            "checks": len(VALUE_CASES) + len(ERROR_CASES),
            "accepted_candidates": [r["candidate"] for r in contract_accepted],
            "accepted_known_defects": [r["candidate"] for r in contract_accepted if r["predeclared_label"] == "planted_defect"],
            "known_defects_rejected": [r["candidate"] for r in rows if r["predeclared_label"] == "planted_defect" and not r["contract_suite_accepts"]],
            "valid_alternatives_rejected": [r["candidate"] for r in rows if r["predeclared_label"] == "valid_alternative" and not r["contract_suite_accepts"]],
        },
        "rows": rows,
        "limitations": [
            "All candidates and labels are authored in one small local fixture.",
            "The exercise measures test-suite discrimination on planted variants, not real agent success or safety.",
            "The contract suite is a second oracle written for this task, not an independent external adjudicator.",
            "Passing this suite is not proof that the specification or reference implementation is complete.",
        ],
    }
    (ROOT / "probe_results.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [
        "# Observer probe v0.3 — results", "",
        "**Status: local evaluator calibration; not agent evaluation.**", "",
        f"Candidates tested: {len(rows)} (2 known-valid implementations, {len(rows)-2} planted defects).", "",
        "## Comparison", "",
        "| Candidate | Expected label | Public checks | Public accepts | Contract checks | Contract accepts |", "|---|---|---:|---|---:|---|",
    ]
    for r in rows:
        label = "valid" if r["predeclared_label"] == "valid_alternative" else "defect"
        lines.append(f"| `{r['candidate']}` | {label} | {r['public_checks_passed']}/{r['public_checks_total']} | {'yes' if r['public_suite_accepts'] else 'no'} | {r['contract_checks_passed']}/{r['contract_checks_total']} | {'yes' if r['contract_suite_accepts'] else 'no'} |")
    lines += ["", "## What this demonstrates", "",
        f"The three-case public suite accepts **{len(public_accepted)} of {len(rows)}** candidates, including **{summary['public_suite']['false_accepts_among_known_defects']} known planted defects**.",
        f"The contract suite accepts **{len(contract_accepted)} candidates**: {len([r for r in contract_accepted if r['predeclared_label']=='valid_alternative'])} predeclared-valid alternatives and {summary['contract_suite']['accepted_known_defects']} planted defects.",
        "", "A valid alternative implementation is retained to check that the oracle grades behavior, not code shape. The test is intentionally small and hand-authored; the results are a calibration demonstration, not generalizable rates.", "",
        "## Contract failures by candidate", ""]
    for r in rows:
        if r["contract_failures"]:
            lines.append(f"### `{r['candidate']}`")
            for f in r["contract_failures"]:
                lines.append(f"- `{f['case']}`: {f['detail']}")
            lines.append("")
    (ROOT / "PROBE_RESULTS.md").write_text("\n".join(lines).rstrip()+"\n")
    print("STATUS:", summary["status"])
    print("Public accepted:", [r["candidate"] for r in public_accepted])
    print("Public accepted planted defects:", summary["public_suite"]["accepted_known_defects"])
    print("Contract accepted:", [r["candidate"] for r in contract_accepted])
    print("Contract valid alternatives rejected:", summary["contract_suite"]["valid_alternatives_rejected"])

if __name__ == "__main__":
    main()
