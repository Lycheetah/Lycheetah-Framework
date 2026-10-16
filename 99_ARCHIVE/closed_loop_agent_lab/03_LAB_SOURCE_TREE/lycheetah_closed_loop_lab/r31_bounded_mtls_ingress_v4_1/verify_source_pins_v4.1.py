#!/usr/bin/env python3
"""Verify exact reference files included in the v4.1 research package."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIN = ROOT / "SOURCE_PIN_v4.1.json"

def main() -> int:
    data = json.loads(PIN.read_text(encoding="utf-8"))
    failures = []
    for rel, metadata in data["files"].items():
        path = ROOT / rel
        if not path.is_file():
            print(f"FAIL missing {rel}")
            failures.append(rel)
            continue
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = metadata["sha256"]
        if got != expected:
            print(f"FAIL {rel} expected={expected} got={got}")
            failures.append(rel)
        else:
            print(f"PASS {rel} sha256={got}")
    if failures:
        print(f"FAIL: {len(failures)} source pin mismatch(es)")
        return 1
    print(f"PASS: {len(data['files'])} file fingerprints verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
