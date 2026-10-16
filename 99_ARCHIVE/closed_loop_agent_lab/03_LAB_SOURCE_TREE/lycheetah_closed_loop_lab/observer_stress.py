#!/usr/bin/env python3
"""Expected-count sensitivity analysis for a task-outcome observer.

This is an analytical, assumption-driven stress grid. It is NOT an empirical estimate
of any model, repository, benchmark, or deployed system. Only Python's standard library.
"""
from __future__ import annotations
import csv
import itertools
import json
from pathlib import Path

N = 10_000
INVALID_PREVALENCES = (0.05, 0.20, 0.50)
SENSITIVITIES = (0.50, 0.70, 0.80, 0.90, 0.95, 0.98)
SPECIFICITIES = (0.80, 0.90, 0.95, 0.98)
UNKNOWN_VALID = 0.02
UNKNOWN_INVALID = 0.02


def evaluate(prevalence_invalid: float, sensitivity: float, specificity: float,
             unknown_valid: float = UNKNOWN_VALID,
             unknown_invalid: float = UNKNOWN_INVALID,
             n: int = N) -> dict:
    """Compute expected counts for a baseline and candidate observer.

    The baseline in this isolated green-lane model auto-accepts tasks that pass
    conventional process gates. Candidate sensor outcomes are defined by assumed
    sensitivity/specificity/unknown rates against an independent true label.
    The candidate's 'failed' outcome blocks, 'unknown' reviews, and 'satisfied' accepts.
    """
    vals = (prevalence_invalid, sensitivity, specificity, unknown_valid, unknown_invalid)
    if any(not 0 <= v <= 1 for v in vals):
        raise ValueError("All rates must be in [0, 1].")
    if sensitivity + unknown_invalid > 1 + 1e-12:
        raise ValueError("Invalid-task sensitivity + unknown rate cannot exceed 1.")
    if specificity + unknown_valid > 1 + 1e-12:
        raise ValueError("Valid-task specificity + unknown rate cannot exceed 1.")
    if n <= 0:
        raise ValueError("n must be positive")

    invalid = n * prevalence_invalid
    valid = n - invalid

    # Baseline: all cases already passed conventional process checks.
    base_invalid_accept = invalid
    base_valid_accept = valid

    # Candidate: rates refer to independently labelled correctness, not model confidence.
    cand_invalid_accept = invalid * (1 - sensitivity - unknown_invalid)
    cand_invalid_block = invalid * sensitivity
    cand_invalid_review = invalid * unknown_invalid
    cand_valid_accept = valid * specificity
    cand_valid_block = valid * (1 - specificity - unknown_valid)
    cand_valid_review = valid * unknown_valid

    return {
        "n": n,
        "invalid_prevalence": prevalence_invalid,
        "sensitivity_to_invalid": sensitivity,
        "specificity_for_valid": specificity,
        "unknown_valid_rate": unknown_valid,
        "unknown_invalid_rate": unknown_invalid,
        "ground_truth_invalid_expected": invalid,
        "ground_truth_valid_expected": valid,
        "baseline": {
            "invalid_auto_accept_expected": base_invalid_accept,
            "valid_auto_accept_expected": base_valid_accept,
            "valid_block_expected": 0.0,
            "review_expected": 0.0,
        },
        "candidate": {
            "invalid_auto_accept_expected": cand_invalid_accept,
            "invalid_block_expected": cand_invalid_block,
            "invalid_review_expected": cand_invalid_review,
            "valid_auto_accept_expected": cand_valid_accept,
            "valid_block_expected": cand_valid_block,
            "valid_review_expected": cand_valid_review,
            "total_review_expected": cand_valid_review + cand_invalid_review,
        },
        "delta_vs_baseline": {
            "invalid_auto_accepts_avoided_expected": base_invalid_accept - cand_invalid_accept,
            "valid_auto_accepts_lost_expected": base_valid_accept - cand_valid_accept,
            "valid_work_blocked_expected": cand_valid_block,
            "review_load_added_expected": cand_valid_review + cand_invalid_review,
        },
        "status": "ANALYTICAL_SENSITIVITY_SCENARIO_NOT_EMPIRICAL_RESULT",
    }


def generate_grid() -> list[dict]:
    rows = []
    for prevalence, sensitivity, specificity in itertools.product(
        INVALID_PREVALENCES, SENSITIVITIES, SPECIFICITIES
    ):
        rows.append(evaluate(prevalence, sensitivity, specificity))
    return rows


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    grid = generate_grid()
    (out_dir / "observer_stress_results.json").write_text(
        json.dumps({
            "status": "ANALYTICAL_SENSITIVITY_GRID_NOT_EMPIRICAL_RESULT",
            "description": "Expected counts per scenario from explicitly assumed sensor rates.",
            "assumptions": {
                "tasks_per_scenario": N,
                "invalid_task_prevalences": INVALID_PREVALENCES,
                "sensor_sensitivities": SENSITIVITIES,
                "sensor_specificities": SPECIFICITIES,
                "unknown_rate_on_valid_tasks": UNKNOWN_VALID,
                "unknown_rate_on_invalid_tasks": UNKNOWN_INVALID,
                "baseline": "All cases in this green-lane model pass conventional process gates and are accepted.",
                "candidate": "Failed postcondition blocks; unknown reviews; satisfied accepts.",
            },
            "scenarios": grid,
            "limitations": [
                "Rates are hypothetical inputs, not measured observer performance.",
                "The ground-truth labels are assumed independent and correct; real studies must audit them.",
                "A human review is counted as work deferred, not as a guaranteed correct decision.",
                "This isolates task-observer effects after conventional gates pass; it does not model the whole runtime.",
                "Expected counts may be fractional because this uses analytical rates, not random sampling.",
            ],
        }, indent=2) + "\n", encoding="utf-8"
    )
    with (out_dir / "observer_stress_grid.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "invalid_prevalence", "sensitivity_to_invalid", "specificity_for_valid",
            "invalid_auto_accepts_baseline", "invalid_auto_accepts_candidate",
            "invalid_auto_accepts_avoided", "valid_auto_accepts_lost",
            "valid_work_blocked", "total_review_load_added",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in grid:
            w.writerow({
                "invalid_prevalence": r["invalid_prevalence"],
                "sensitivity_to_invalid": r["sensitivity_to_invalid"],
                "specificity_for_valid": r["specificity_for_valid"],
                "invalid_auto_accepts_baseline": r["baseline"]["invalid_auto_accept_expected"],
                "invalid_auto_accepts_candidate": r["candidate"]["invalid_auto_accept_expected"],
                "invalid_auto_accepts_avoided": r["delta_vs_baseline"]["invalid_auto_accepts_avoided_expected"],
                "valid_auto_accepts_lost": r["delta_vs_baseline"]["valid_auto_accepts_lost_expected"],
                "valid_work_blocked": r["candidate"]["valid_block_expected"],
                "total_review_load_added": r["candidate"]["total_review_expected"],
            })

    # Illustrative mid-grid case, chosen for interpretation—not as a recommended prior.
    ex = evaluate(0.20, 0.90, 0.95)
    print("STATUS: ANALYTICAL_SENSITIVITY_GRID_NOT_EMPIRICAL_RESULT")
    print("scenarios:", len(grid), "tasks per scenario:", N)
    print("illustrative scenario: 20% invalid, sensitivity 90%, specificity 95%, unknown 2% each")
    print("  baseline invalid auto-accepts:", round(ex["baseline"]["invalid_auto_accept_expected"]))
    print("  candidate invalid auto-accepts:", round(ex["candidate"]["invalid_auto_accept_expected"]))
    print("  invalid auto-accepts avoided:", round(ex["delta_vs_baseline"]["invalid_auto_accepts_avoided_expected"]))
    print("  valid work blocked:", round(ex["candidate"]["valid_block_expected"]))
    print("  total reviews added:", round(ex["candidate"]["total_review_expected"]))
    print("Outputs: observer_stress_results.json, observer_stress_grid.csv")

if __name__ == "__main__":
    main()
