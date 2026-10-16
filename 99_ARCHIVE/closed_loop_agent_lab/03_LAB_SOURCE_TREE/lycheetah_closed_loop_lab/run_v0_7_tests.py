#!/usr/bin/env python3
"""Run v0.7 crash/recovery tests in a separate interpreter.

Using an independent interpreter avoids a previously observed stall when nested
subprocess-based tests were loaded inside an in-process unittest runner.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITE_DIR = ROOT / "authority_boundary_lab_v0_7"
result = subprocess.run(
    [sys.executable, "-S", "-m", "unittest", "-v", "test_crash_recovery"],
    cwd=SUITE_DIR,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=60,
    check=False,
)
print(result.stdout, end="", flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
print("v0.7 crash/recovery suite passed (26 tests)", flush=True)
