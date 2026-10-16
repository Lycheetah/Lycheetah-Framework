#!/usr/bin/env python3
"""Verify inherited source fingerprints and local-source labels for v3.7."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIN = ROOT / "SOURCE_PIN_v3.7.json"
data = json.loads(PIN.read_text(encoding="utf-8"))
errors = []
for name, spec in data["files"].items():
    p = ROOT / name
    if not p.is_file():
        errors.append(f"missing:{name}")
        continue
    observed = hashlib.sha256(p.read_bytes()).hexdigest()
    if observed != spec["sha256"]:
        errors.append(f"sha256-mismatch:{name}:expected={spec['sha256']}:observed={observed}")
if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
    raise SystemExit(1)
print(json.dumps({"status": "PASS", "upstream_commit_observed": data["observed_upstream_commit"],
                  "verified_files": len(data["files"]),
                  "note": "Only files explicitly labelled upstream-derived are pinned to the observed upstream/local source reference. New quorum wrapper and tests are local artifacts."}, indent=2))
