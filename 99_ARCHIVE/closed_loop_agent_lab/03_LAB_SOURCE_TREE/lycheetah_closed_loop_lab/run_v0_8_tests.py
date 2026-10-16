#!/usr/bin/env python3
"""Run the v0.8 trusted catalog suite independently from project root."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "authority_boundary_lab_v0_8"), "-p", "test_*.py", "-v"]
result = subprocess.run(cmd, cwd=ROOT, text=True)
if result.returncode == 0:
    print("v0.8 trusted catalog suite passed (18 tests)")
raise SystemExit(result.returncode)
