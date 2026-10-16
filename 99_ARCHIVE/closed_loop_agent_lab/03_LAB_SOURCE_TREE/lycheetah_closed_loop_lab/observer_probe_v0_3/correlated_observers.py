#!/usr/bin/env python3
"""Analytical common-mode error model for two binary observers.

No empirical observer data is used. Marginal miss rate and error correlation
are illustrative inputs. The model shows why the independence assumption matters.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def joint_miss_probability(marginal_miss_rate: float, correlation: float) -> float:
    """P(both miss | invalid task), for equal Bernoulli miss rates and rho >= 0.

    For Bernoulli variables X,Y with P(X=1)=P(Y=1)=p, Cov(X,Y)=rho*p*(1-p),
    therefore P(X=1,Y=1)=p^2 + rho*p*(1-p). Here 1 means 'miss'.
    Only the non-negative correlation range is used in this sensitivity study.
    """
    p = float(marginal_miss_rate)
    rho = float(correlation)
    if not 0 <= p <= 1:
        raise ValueError("marginal_miss_rate must lie in [0, 1]")
    if not 0 <= rho <= 1:
        raise ValueError("correlation must lie in [0, 1]")
    return p * p + rho * p * (1 - p)


def build_grid() -> list[dict]:
    rates = [0.05, 0.10, 0.20]
    correlations = [0.0, 0.25, 0.5, 0.75, 1.0]
    invalid_tasks = 2000  # illustrative 20% of 10,000 gated tasks
    rows = []
    for p in rates:
        for rho in correlations:
            both_miss = joint_miss_probability(p, rho)
            rows.append({
                "single_observer_miss_rate": p,
                "observer_error_correlation": rho,
                "both_observers_miss_probability": both_miss,
                "expected_false_accepts_per_2000_invalid_tasks": invalid_tasks * both_miss,
                "independence_assumed_probability": p * p,
                "independence_assumption_underestimates_by_factor": (both_miss / (p*p)) if p > 0 else None,
            })
    return rows


def main() -> None:
    rows = build_grid()
    (ROOT / "correlated_observer_results.json").write_text(json.dumps({
        "status": "ANALYTICAL_SENSITIVITY_NOT_EMPIRICAL",
        "formula": "P(both miss) = p^2 + rho*p*(1-p)",
        "assumptions": [
            "Both observers have the same marginal miss rate p on invalid tasks.",
            "rho is the correlation of their Bernoulli miss indicators conditional on an invalid task.",
            "Acceptance requires both observers to miss the defect.",
            "Expected counts use a hypothetical 2,000 invalid tasks; no task trials were run.",
        ],
        "rows": rows,
    }, indent=2) + "\n")
    with (ROOT / "correlated_observer_grid.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Common-mode error: why two observers may not equal two safeguards", "",
        "**Status: mathematical sensitivity analysis, not measured AI observer performance.**", "",
        "Let each observer miss an invalid outcome with probability `p`. Let `rho` be the correlation between the two observers' miss indicators, conditional on the task actually being invalid. If acceptance requires both observers to miss the defect, then:", "",
        r"`P(both miss) = p² + rho × p × (1 − p)`", "",
        "When errors are independent (`rho = 0`), joint misses are `p²`. When the observers share the same blind spot (`rho = 1`), the joint miss rate is `p`. The number of checks is therefore not a sufficient measure of evidence diversity.", "",
        "## Example: each observer misses 10% of invalid outcomes", "",
        "| Error correlation | Both miss | Expected false accepts per 2,000 invalid tasks |", 
        "|---:|---:|---:|",
    ]
    for row in rows:
        if row["single_observer_miss_rate"] == 0.1:
            lines.append(f"| {row['observer_error_correlation']:.2f} | {row['both_observers_miss_probability']:.1%} | {row['expected_false_accepts_per_2000_invalid_tasks']:.0f} |")
    lines += [
        "", "The counts are expected values from assumed rates, not observations. The 2,000 invalid cases represent a hypothetical 20% invalid prevalence among 10,000 candidates already passing conventional process gates.", "",
        "## Design implications", "",
        "- A unit-test suite and an LLM judge that both inherit the same ambiguous task contract may have correlated failures.",
        "- A second check should ideally use different evidence: for example, a frozen behavioral contract plus a trusted execution receipt and blinded human outcome adjudication.",
        "- Different code, different filenames, or different model calls do not by themselves establish independence.",
        "- Measure agreement and error overlap on held-out cases. Do not assume `rho = 0` just because there are two checks.",
        "", "## Limitations", "",
        "This model assumes equal marginal error rates, non-negative correlation and binary miss indicators. Real errors may be asymmetric, multi-class, conditional on task family, or have different miss rates. The formula is a sensitivity aid, not a calibrated safety estimator.", "",
    ]
    (ROOT / "COMMON_MODE_ERRORS.md").write_text("\n".join(lines))
    print("STATUS: ANALYTICAL_SENSITIVITY_NOT_EMPIRICAL")
    for row in rows:
        if row["single_observer_miss_rate"] == .1:
            print(f"rho={row['observer_error_correlation']:.2f}: both_miss={row['both_observers_miss_probability']:.3f}; expected_false_accepts={row['expected_false_accepts_per_2000_invalid_tasks']:.1f}")

if __name__ == "__main__":
    main()
