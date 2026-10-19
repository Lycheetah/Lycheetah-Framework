"""Replay the original Forge VIII archive plus the omitted Forge II/III suites.

All extraction and result-writing happen in temporary directories. The archived
142-test runner covers Forges IV-VIII, not II-VIII. Additional II/III suites
bring the execution count to 207. Requires cryptography; Node enables JS parity.
"""
from pathlib import Path, PurePosixPath
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent


def extract(archive, destination):
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            path = PurePosixPath(member.filename)
            if path.is_absolute() or ".." in path.parts or (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Unsafe archive member")
        if source.testzip() is not None:
            raise ValueError("Archive CRC mismatch")
        source.extractall(destination)


def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix="sovereign-choice-replay-") as tmp:
        work = Path(tmp)
        shutil.copytree(ROOT / "forges", work / "primary")
        for name, args, expected in [
            ("forge_ii", ["-m", "unittest", "discover", "-s", "tests", "-v"], 28),
            ("forge_iii", ["-m", "unittest", "-v", "test_choice_fence"], 37),
        ]:
            proc = subprocess.run([sys.executable, *args], cwd=work / "primary" / name,
                                  env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                  capture_output=True, text=True, timeout=120)
            output = proc.stdout + proc.stderr
            match = re.search(r"Ran (\d+) tests? in", output)
            count = int(match[1]) if match else 0
            passed = proc.returncode == 0 and count == expected and not re.search(r"\bskipped(?:=|\b)", output)
            rows.append({"suite": name, "tests": count, "expected": expected,
                         "passed": bool(passed), "exit_code": proc.returncode, "output": output})
        extract(ROOT / "source_archives" / "LYCHEETAH_SOVEREIGN_CHOICE_FORGE_VIII_COMPLETE_v0.1.zip", work / "archive")
        proc = subprocess.run([sys.executable, "run_verification.py"],
                              cwd=work / "archive" / "sovereign_choice_forge_viii",
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                              capture_output=True, text=True, timeout=300)
        historical = json.loads(proc.stdout)
        passed = (proc.returncode == 0 and historical.get("all_passed") is True
                  and historical.get("combined_tests") == 142)
        rows.append({"suite": "original_forges_iv_through_viii", "tests": historical.get("combined_tests", 0),
                     "expected": 142, "passed": passed, "exit_code": proc.returncode,
                     "verification": historical, "stderr": proc.stderr})
    report = {"scope": "Self-authored local fixtures; not production or independent validation",
              "all_passed": all(row["passed"] for row in rows),
              "test_executions": sum(row["tests"] for row in rows),
              "node_available": shutil.which("node") is not None, "suites": rows}
    print(json.dumps(report, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
