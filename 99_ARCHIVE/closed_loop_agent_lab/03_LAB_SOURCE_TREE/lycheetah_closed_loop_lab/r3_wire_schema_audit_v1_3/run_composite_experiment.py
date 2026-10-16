#!/usr/bin/env python3
"""Run a receipt-shaped wire-mutation experiment against a source-equivalent fixture."""
from __future__ import annotations
import json
from pathlib import Path
from composite_receipt_fixture import (
    baseline_parse_and_verify, finalize_receipt, mutate, strict_parse_and_verify, valid_receipt_body,
)
from source_equivalent_wire_fixture import WireError

ROOT = Path(__file__).resolve().parent
CASES = [
    ("schema_version_number", "top-level schema_version string -> number"),
    ("control_title_boolean", "nested ControlReference title string -> boolean"),
    ("finding_title_boolean", "nested Finding title string -> boolean"),
    ("confidence_boolean", "nested Finding confidence 1.0 -> boolean true"),
    ("evidence_integer", "nested evidence string -> integer"),
]


def main() -> int:
    original = finalize_receipt(valid_receipt_body())
    expected, original_valid = baseline_parse_and_verify(original)
    results = []
    for case, description in CASES:
        changed = mutate(original, case)
        try:
            normalized, baseline_valid = baseline_parse_and_verify(changed)
            baseline_same_body = normalized == expected
        except Exception as exc:
            baseline_valid, baseline_same_body = False, False
            baseline_error = f"{type(exc).__name__}: {exc}"
        else:
            baseline_error = None
        try:
            strict_parse_and_verify(changed)
            strict_rejects = False
            strict_error = None
        except WireError as exc:
            strict_rejects = True
            strict_error = str(exc)
        results.append({
            "case": case,
            "description": description,
            "baseline_accepts_and_digest_verifies": bool(baseline_valid),
            "baseline_normalizes_to_original_body": bool(baseline_same_body),
            "strict_candidate_rejects": strict_rejects,
            "baseline_error": baseline_error,
            "strict_error": strict_error,
        })
    passed = original_valid and all(
        row["baseline_accepts_and_digest_verifies"] and row["baseline_normalizes_to_original_body"] and row["strict_candidate_rejects"]
        for row in results
    )
    payload = {
        "status": "SOURCE_EQUIVALENT_RECEIPT_FIXTURE_NOT_UPSTREAM_PACKAGE_TEST",
        "original_receipt_digest_verifies": original_valid,
        "case_count": len(results),
        "baseline_normalized_digest_matches": sum(row["baseline_accepts_and_digest_verifies"] for row in results),
        "strict_rejections": sum(row["strict_candidate_rejects"] for row in results),
        "fixture_assertions_passed": passed,
        "cases": results,
    }
    (ROOT / "composite_receipt_results_v1_3.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
