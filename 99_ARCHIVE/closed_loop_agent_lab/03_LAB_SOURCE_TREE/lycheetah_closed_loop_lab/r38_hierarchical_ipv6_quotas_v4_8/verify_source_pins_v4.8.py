#!/usr/bin/env python3
"""Verify immutable local source/document fingerprints for v4.8."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "SOURCE_PIN_v4.8.json").read_text(encoding="utf-8"))
errors=[]
for name, item in DATA["files"].items():
    path=ROOT / name
    if not path.is_file():
        errors.append(f"MISSING {name}")
        continue
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        errors.append(f"HASH_MISMATCH {name}: expected={item['sha256']} actual={actual}")
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print(f"PASS: {len(DATA['files'])} exact local artifact fingerprints verified")
print(f"observed_upstream_commit={DATA['observed_upstream_commit']}; upstream_modified={DATA['upstream_modified']}")
