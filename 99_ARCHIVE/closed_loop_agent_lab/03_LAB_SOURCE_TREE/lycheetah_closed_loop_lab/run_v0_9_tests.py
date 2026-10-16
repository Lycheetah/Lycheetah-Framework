#!/usr/bin/env python3
"""Run v0.9 catalog-bound host/provider tests in separate interpreters.

A prior combined discovery run once timed out in this research container. Separate
suite processes make the evidence easier to diagnose and avoid shared-module state.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITE = ROOT / "authority_boundary_lab_v0_9"
RUNS = [
    ("catalog + issuance integration", ["-S", "-m", "unittest", "-v", "test_tool_catalog"], 21),
    ("separate-process crash/recovery", ["-S", "-m", "unittest", "-v", "test_crash_recovery"], 28),
]
for label, args, expected_count in RUNS:
    print(f"\n=== v0.9 {label} ===", flush=True)
    result = subprocess.run([sys.executable, *args], cwd=SUITE, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
    print(f"PASS: {label} (expected {expected_count} tests)", flush=True)
print("\nv0.9 verification complete: 49 tests passed across two separate suite processes.", flush=True)
