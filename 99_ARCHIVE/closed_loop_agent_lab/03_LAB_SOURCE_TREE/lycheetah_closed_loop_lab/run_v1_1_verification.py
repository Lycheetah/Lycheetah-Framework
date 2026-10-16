#!/usr/bin/env python3
"""Run exactly one research test suite per invocation.

Individual invocations keep the run inside constrained execution windows and
make a timeout local to one suite rather than hiding a partial aggregate.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "verification_v1_1"
LOG_DIR.mkdir(exist_ok=True)
PY = sys.executable
SUITES = {
    "legacy_v0_1_to_v0_6": (ROOT, [PY, str(ROOT / "run_all_tests.py")], 66, 45),
    "crash_recovery_v0_7": (ROOT / "authority_boundary_lab_v0_7", [PY, "-S", "-m", "unittest", "-v", "test_crash_recovery"], 26, 60),
    "trusted_catalog_v0_8": (ROOT, [PY, "-m", "unittest", "discover", "-s", str(ROOT / "authority_boundary_lab_v0_8"), "-p", "test_*.py", "-v"], 18, 30),
    "catalog_issuance_v0_9": (ROOT / "authority_boundary_lab_v0_9", [PY, "-S", "-m", "unittest", "-v", "test_tool_catalog"], 21, 30),
    "crash_recovery_v0_9": (ROOT / "authority_boundary_lab_v0_9", [PY, "-S", "-m", "unittest", "-v", "test_crash_recovery"], 28, 60),
    "policy_parser_source_equivalent_fixture": (ROOT / "r2_policy_parser_audit", [PY, "test_policy_parser.py"], 7, 20),
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--suite", required=True, choices=sorted(SUITES), help="run one suite only")
args = parser.parse_args()
name = args.suite
cwd, command, expected_methods, timeout = SUITES[name]
started = time.monotonic()
try:
    completed = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=timeout, check=False)
    output = completed.stdout
    status = "PASS" if completed.returncode == 0 else "FAIL"
    returncode = completed.returncode
    detail = f"exit_code={returncode}"
except subprocess.TimeoutExpired as exc:
    stdout = exc.stdout or ""
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    output = stdout + f"\nTIMEOUT after {timeout}s; this is not a pass.\n"
    status = "TIMEOUT"
    returncode = None
    detail = f"timeout_seconds={timeout}"
elapsed = round(time.monotonic() - started, 3)
(LOG_DIR / f"{name}.log").write_text(output, encoding="utf-8")
result = {"suite": name, "status": status, "expected_test_methods": expected_methods,
          "elapsed_seconds": elapsed, "detail": detail,
          "command": [str(x) for x in command], "cwd": str(cwd)}
(LOG_DIR / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"{status}: {name} ({elapsed:.2f}s; {detail})", flush=True)
print(output[-2400:], end="" if output.endswith("\n") else "\n", flush=True)
if status != "PASS":
    raise SystemExit(1)
