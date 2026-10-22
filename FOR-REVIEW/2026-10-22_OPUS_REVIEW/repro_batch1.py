#!/usr/bin/env python3
"""Reproduce the two frozen-source defects from Opus review batch 1.

Both targets are checksummed research artifacts, so they are imported and
exercised here without being modified. Run from the repository root:

    python3 FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch1.py

Exit status 0 means both counterexamples still reproduce.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ("papers/agent-safety/frontier-controls/"
               "06_hazard_lineage_policy_evolution_v1_2/policy_evolution_gate.py")
AGG = ROOT / ("23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/"
              "Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/"
              "Anon_Politician_Policy_Lab_v0_2/evaluation/aggregate_reviews.py")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(mod)
    return mod


def rv11() -> dict:
    g = load(GATE, "policy_evolution_gate")
    a = g.Obligation("a", "H1", "ka")
    b = g.Obligation("b", "H1", "kb")
    # Active v2 repeats group G1, so its formula is a AND b.
    v2 = g.Policy("P", 2, (g.Group("G1", (b,)), g.Group("G1", (a,))))
    # Candidate v3 keeps only G1 = a: strictly easier to satisfy than v2.
    v3 = g.Policy("P", 3, (g.Group("G1", (a,)),))
    structural = g.semantic_relation_structural(v2, v3)
    oracle = g.brute_force_relation(v2, v3)
    return {
        "structural_classifier": structural,
        "truth_table_oracle": oracle,
        "reproduced": structural == "EQUIVALENT" and oracle == "WEAKER",
    }


def rv12() -> dict:
    m = load(AGG, "aggregate_reviews")
    review = {
        "experiment_id": "E1", "case_id": "C1", "reviewer_id": "r1",
        "candidates": [{"candidate_id": "A",
                        "ratings": {"source_fidelity": {"score": "2"}}}],
    }
    dup = m.aggregate([review, review])
    prof = dup["methods_or_aliases"]["A"]
    duplicate_inflates = (prof["reviewer_count"] == 1
                          and prof["dimensions"]["source_fidelity"]["n_ratings"] == 2)

    lower = json.loads(json.dumps(review))
    lower["candidates"][0]["candidate_id"] = "a"
    key = {"mapping": {"A": "m1", "B": "m2", "C": "m3"}}
    mixed = m.aggregate([review, lower], key)
    unmapped_alias_survives = "a" in mixed["methods_or_aliases"]

    other_case = json.loads(json.dumps(review))
    other_case["case_id"] = "C2"
    other_case["reviewer_id"] = "r2"
    mixed_cases = m.aggregate([review, other_case])
    second_case_hidden = mixed_cases["case_id"] == "C1"

    return {
        "duplicate_review_inflates_ratings": duplicate_inflates,
        "lowercase_alias_bypasses_mapping_key": unmapped_alias_survives,
        "different_case_ids_merged_silently": second_case_hidden,
        "reproduced": duplicate_inflates and unmapped_alias_survives,
    }


if __name__ == "__main__":
    out = {"RV11": rv11(), "RV12": rv12()}
    print(json.dumps(out, indent=2))
    sys.exit(0 if all(v["reproduced"] for v in out.values()) else 1)
