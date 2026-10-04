#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse, json


def classify(required, enabled):
    required = set(required)
    enabled = set(enabled)
    hit = sorted(required & enabled)
    missing = sorted(required - enabled)
    if not missing:
        status = "FULL"
    elif not hit:
        status = "GAP"
    else:
        status = "PARTIAL"
    return {
        "status": status,
        "covered": hit,
        "missing": missing,
        "coverage_fraction": 1.0 if not required else len(hit)/len(required),
    }


def audit(manifest, challenges):
    enabled = set(manifest["enabled_controls"])
    rows = []
    for challenge in challenges:
        c = classify(challenge["required_controls"], enabled)
        rows.append({
            "id": challenge["id"],
            "name": challenge["name"],
            "source_family": challenge["source_family"],
            "status": c["status"],
            "covered": c["covered"],
            "missing": c["missing"],
            "coverage_fraction": c["coverage_fraction"],
        })
    return {
        "manifest_name": manifest["name"],
        "controls_enabled": sorted(enabled),
        "full": sum(x["status"]=="FULL" for x in rows),
        "partial": sum(x["status"]=="PARTIAL" for x in rows),
        "gap": sum(x["status"]=="GAP" for x in rows),
        "rows": rows,
    }


def minimum_missing(report):
    # Union of controls needed to make every challenge FULL.
    return sorted({m for row in report["rows"] for m in row["missing"]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--challenges", default="external_challenges.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    challenges = json.loads(Path(args.challenges).read_text())
    report = audit(manifest, challenges)
    report["minimum_controls_to_full_declared_coverage"] = minimum_missing(report)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"Agent Boundary Audit: {report['manifest_name']}")
    print("=" * (22 + len(report['manifest_name'])))
    print(f"FULL={report['full']} PARTIAL={report['partial']} GAP={report['gap']}")
    for row in report["rows"]:
        print(f"{row['id']} {row['status']:<7} {row['name']}")
        if row["missing"]:
            print("  missing:", ", ".join(row["missing"]))
    print("Minimum additions for full declared coverage:")
    print(" ", ", ".join(report["minimum_controls_to_full_declared_coverage"]))
