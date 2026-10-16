#!/usr/bin/env python3
"""Verify inherited and local-reference source fingerprints for v3.8."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "SOURCE_PIN_v3.8.json").read_text(encoding="utf-8"))
errors = []
for name, spec in data["files"].items():
    path = ROOT / name
    if not path.is_file():
        errors.append(f"missing:{name}"); continue
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    if observed != spec["sha256"]:
        errors.append(f"hash-mismatch:{name}:expected={spec['sha256']}:observed={observed}")
if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2)); raise SystemExit(1)
print(json.dumps({"status": "PASS", "verified_files": len(data["files"]),
                  "observed_upstream_commit": data["observed_upstream_commit"],
                  "note": "Pinned hashes are reproducibility checks. Local reference modules are not claimed to be upstream source files."}, indent=2))
