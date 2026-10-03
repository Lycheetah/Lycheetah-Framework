#!/usr/bin/env python3
"""Reproduce the synthetic control comparison without providers or dependencies."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

from safety_sim.scenarios import run_experiments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parent / "reports")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    report = run_experiments()
    report["runtime"] = {"python": platform.python_version(), "implementation": platform.python_implementation()}
    report["source_sha256"] = {
        str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.py"))
    }
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "scripted-controls.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    lines = ["# Scripted Control Experiment", "", "**Stage 1 only: synthetic, self-authored, in-process.**", "",
        "No language model, real provider, independent review, or natural-language understanding is evaluated.", "",
        f"Cases per arm: **{report['cases_per_arm']}**.",
        f"All expected outcomes met: **{report['all_expected_outcomes_met']}**.",
        f"Matched aggregate outcomes equivalent: **{report['matched_outcomes_equivalent']}**.", "",
        "| Case | Expected effects | C observed | D observed | Expected outcome met in both |", "|---|---:|---:|---:|---|"]
    c, d = report["arms"].values()
    for left, right in zip(c, d):
        lines.append(f"| {left['case']} | {left['expected_effects']} | {left['observation']['effect_count']} | {right['observation']['effect_count']} | {left['met_expected_outcome'] and right['met_expected_outcome']} |")
    lines += ["", "The permitted-harm fixture produces one synthetic harm marker in each arm. The already-admitted fixture completes after revocation in each arm. These are exposed limits, not protective successes.", "",
        "C and D share the broker, evidence validator, resource ledger, and synthetic provider. Their permission stores are separately implemented. Equal outcomes establish no empirical superiority or statistical equivalence beyond these cases.", "",
        "Structured evidence uses exact fields and a controlled rendering template. A harmless paraphrase is outside the accepted language. Faithfulness does not establish source truth.", "",
        "Raw outcomes, admission/revocation order, effects, and source hashes are in [scripted-controls.json](scripted-controls.json). Concurrent schedules can differ; aggregate requirements remain fixed.", ""]
    (args.output / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"cases_per_arm": report["cases_per_arm"],
        "all_expected_outcomes_met": report["all_expected_outcomes_met"],
        "matched_outcomes_equivalent": report["matched_outcomes_equivalent"],
        "report": str(target)}, indent=2))
    return 0 if report["all_expected_outcomes_met"] and report["matched_outcomes_equivalent"] else 1


if __name__ == "__main__":
    sys.exit(main())
