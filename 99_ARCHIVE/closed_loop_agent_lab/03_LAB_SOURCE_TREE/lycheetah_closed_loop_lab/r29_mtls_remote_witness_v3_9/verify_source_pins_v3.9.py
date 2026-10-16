#!/usr/bin/env python3
"""Verify inherited and local source fingerprints for the v3.9 lab."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "SOURCE_PIN_v3.9.json").read_text(encoding="utf-8"))
failures = []
for relative, record in manifest["files"].items():
    path = ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
    expected = record["sha256"]
    status = "PASS" if actual == expected else "FAIL"
    print(f"{status} {relative} sha256={actual}")
    if actual != expected:
        failures.append(relative)
if failures:
    raise SystemExit("source-pin-verification-failed: " + ", ".join(failures))
print(f"PASS: {len(manifest['files'])} file fingerprints verified")
