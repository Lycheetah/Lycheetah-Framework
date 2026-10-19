"""Run the preserved Earned Light suites in a disposable copy, not the archive.

Requires Python 3.10+, pytest and cryptography. Forge VII binds a temporary
localhost HTTP provider and launches child processes; no external API is used.
Counts are test executions and include repeated historical coverage.
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SUITES = [
    ("Forge_02", ["-m", "pytest", "-q", "tests"], 28),
    ("Forge_03", ["-m", "pytest", "-q", "tests"], 76),
    ("Forge_04", ["-m", "pytest", "-q", "test_horizon.py"], 14),
    ("Forge_05", ["-m", "unittest", "discover", "-s", "tests", "-v"], 28),
    ("Forge_06", ["-m", "unittest", "discover", "-s", "tests", "-v"], 30),
    ("Forge_07", ["-m", "unittest", "discover", "-s", "tests", "-v"], 31),
]


def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix="earned-light-replay-") as tmp:
        work = Path(tmp) / "forges"
        shutil.copytree(ROOT / "forges_01_07", work)
        for name, arguments, expected in SUITES:
            try:
                proc = subprocess.run(
                    [sys.executable, *arguments], cwd=work / name,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                    capture_output=True, text=True, timeout=120,
                )
                output = proc.stdout + proc.stderr
                match = re.search(r"(\d+) passed", output) if "pytest" in arguments else re.search(r"Ran (\d+) tests? in", output)
                count = int(match[1]) if match else 0
                skipped = bool(re.search(r"\bskipped(?:=|\b)", output))
                passed = proc.returncode == 0 and count == expected and not skipped
                rows.append({"suite": name, "expected": expected, "tests": count,
                             "exit_code": proc.returncode, "passed": passed,
                             "skips_reported": skipped, "output": output})
            except (OSError, subprocess.TimeoutExpired) as exc:
                rows.append({"suite": name, "expected": expected, "tests": 0,
                             "passed": False, "status": "DID_NOT_COMPLETE", "error": str(exc)})
    report = {"scope": "Self-authored local fixtures; not production or independent validation",
              "all_passed": all(row["passed"] for row in rows),
              "test_executions": sum(row["tests"] for row in rows), "suites": rows}
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
