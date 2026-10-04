#!/usr/bin/env python3
"""Independent integration-packet reproducer for v1.4.

The original standalone v1.4 benchmark.py was not present in the mounted
standalone artifact when this integration packet was assembled. This script is
newly authored for the integration packet. It does not replace or rewrite the
frozen standalone report; it independently reruns the declared boundary-auditor
semantics against the copied challenge/manifests and checks the frozen headline
counts.
"""
from pathlib import Path
import itertools, json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from boundary_auditor import audit, classify, minimum_missing  # noqa: E402

def finite_classifier():
    controls = ("a","b","c","d")
    required_sets = [{"a"},{"a","b"},{"b","c","d"},set(controls)]
    total = correct = 0
    for req in required_sets:
        for bits in itertools.product((False,True), repeat=len(controls)):
            enabled = {c for c,b in zip(controls,bits) if b}
            total += 1
            observed = classify(req, enabled)["status"]
            overlap = len(req & enabled)
            expected = "FULL" if overlap == len(req) else ("GAP" if overlap == 0 else "PARTIAL")
            correct += int(observed == expected)
    return correct, total

def main():
    challenges = json.loads((HERE/"external_challenges.json").read_text())
    current = json.loads((HERE/"examples/current_lycheetah_coding_agent.json").read_text())
    extended = json.loads((HERE/"examples/proposed_extended_coding_agent.json").read_text())
    frozen = json.loads((HERE/"reports/report.json").read_text())

    current_report = audit(current, challenges)
    extended_report = audit(extended, challenges)

    single_total = single_correct = 0
    for ch in challenges:
        req = set(ch["required_controls"])
        for control in req:
            single_total += 1
            if classify(req, req-{control})["status"] != "FULL":
                single_correct += 1

    finite_correct, finite_total = finite_classifier()

    expected = {
        "challenge_packets": 12,
        "current": (0,9,3),
        "extended": (12,0,0),
        "single_removal": (46,46),
        "finite": (64,64),
    }
    observed = {
        "challenge_packets": len(challenges),
        "current": (current_report["full"], current_report["partial"], current_report["gap"]),
        "extended": (extended_report["full"], extended_report["partial"], extended_report["gap"]),
        "single_removal": (single_correct, single_total),
        "finite": (finite_correct, finite_total),
    }

    frozen_headline = {
        "challenge_packets": frozen["external_challenge_packets"],
        "current": (
            frozen["current_manifest"]["full"],
            frozen["current_manifest"]["partial"],
            frozen["current_manifest"]["gap"],
        ),
        "extended": (
            frozen["extended_manifest"]["full"],
            frozen["extended_manifest"]["partial"],
            frozen["extended_manifest"]["gap"],
        ),
        "single_removal": (
            frozen["single_required_control_removal"]["correct"],
            frozen["single_required_control_removal"]["total"],
        ),
        "finite": (
            frozen["finite_classifier_verification"]["correct"],
            frozen["finite_classifier_verification"]["states"],
        ),
    }

    ok = observed == expected == frozen_headline
    print("v1.4 integration reproducer")
    print("Observed:", observed)
    print("Frozen:  ", frozen_headline)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
