#!/usr/bin/env python3
"""Aggregate blinded human review files into dimension profiles; never computes a total ranking."""
from __future__ import annotations
import argparse, json, statistics
from pathlib import Path
from collections import defaultdict

DIMENSIONS = [
    "source_fidelity", "claim_traceability", "uncertainty_discipline", "adversarial_fairness",
    "distributional_coverage", "scenario_reasoning", "public_input_interpretation",
    "non_erasure_value_pluralism", "actionability_accountability"
]
VALID = {"0", "1", "2", "N/A"}


def aggregate(reviews: list[dict], key: dict | None = None) -> dict:
    if not reviews:
        raise ValueError("At least one review JSON is required.")
    exp_ids = {r.get("experiment_id") for r in reviews}
    if len(exp_ids) != 1:
        raise ValueError("Review files belong to different experiments; aggregate separately.")
    pack_ids = {r.get("blind_pack_id") for r in reviews if r.get("blind_pack_id")}
    if len(pack_ids) > 1:
        raise ValueError("Review files belong to different blind packs; aggregate separately.")
    review_pack_id = next(iter(pack_ids), None)
    if key and key.get("blind_pack_id") and review_pack_id and key["blind_pack_id"] != review_pack_id:
        raise ValueError("The private mapping key does not match this blind pack.")
    if key and key.get("mapping"):
        aliases = set(key["mapping"])
        if aliases != {"A", "B", "C"} or len(set(key["mapping"].values())) != 3:
            raise ValueError("Invalid private mapping key: expected unique mappings for A, B, C.")
    observations = defaultdict(list)
    critical = defaultdict(list)
    reviewer_count = defaultdict(set)
    for review in reviews:
        rid = str(review.get("reviewer_id", "unspecified"))
        for candidate in review.get("candidates", []):
            cid = candidate.get("candidate_id")
            method = key.get("mapping", {}).get(cid, cid) if key else cid
            reviewer_count[method].add(rid)
            for dim in DIMENSIONS:
                item = candidate.get("ratings", {}).get(dim, {})
                val = str(item.get("score", "N/A"))
                if val not in VALID:
                    raise ValueError(f"Invalid score {val!r} for {cid}/{dim}")
                if val in {"0", "1", "2"}:
                    observations[(method, dim)].append(int(val))
            for flag in candidate.get("critical_flags", []):
                critical[method].append({"reviewer_id": rid, "flag": flag, "candidate_id": cid})
    profiles = {}
    methods = sorted({method for method, _ in observations} | {m for m in reviewer_count})
    for method in methods:
        profiles[method] = {"reviewer_count": len(reviewer_count[method]), "dimensions": {}}
        for dim in DIMENSIONS:
            vals = observations[(method, dim)]
            profiles[method]["dimensions"][dim] = {
                "n_ratings": len(vals),
                "median": statistics.median(vals) if vals else None,
                "range": [min(vals), max(vals)] if vals else None,
                "ratings": vals,
            }
        profiles[method]["critical_flags"] = critical[method]
    return {
        "experiment_id": reviews[0].get("experiment_id"),
        "blind_pack_id": review_pack_id,
        "case_id": reviews[0].get("case_id"),
        "review_count": len(reviews),
        "methods_or_aliases": profiles,
        "reporting_rule": "Dimension profiles only. No composite total or overall winner is calculated. Reviewers' critical issue flags must be investigated separately; do not average away material errors.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("review_dir", type=Path)
    p.add_argument("--key", type=Path, default=None, help="PRIVATE mapping key; use only after all blinded reviews are locked")
    p.add_argument("--out", type=Path, default=Path("review_aggregate.json"))
    args = p.parse_args()
    review_paths = sorted(args.review_dir.glob("*.json"))
    if not review_paths:
        raise SystemExit(f"No JSON review files found in {args.review_dir}")
    reviews = [json.loads(pth.read_text(encoding="utf-8")) for pth in review_paths if "blind_review_pack" not in pth.name and "mapping_key" not in pth.name]
    key = json.loads(args.key.read_text(encoding="utf-8")) if args.key else None
    result = aggregate(reviews, key)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}. No overall method score or winner was computed.")

if __name__ == "__main__":
    main()
