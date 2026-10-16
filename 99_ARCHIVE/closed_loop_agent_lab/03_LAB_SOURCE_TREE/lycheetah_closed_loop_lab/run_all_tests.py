"""Run the four original local research suites (v0.1 through v0.6)."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITES = [
    (ROOT, ["-m", "unittest", "-v", "test_harness", "test_observer_stress"]),
    (ROOT / "observer_probe_v0_3", ["-m", "unittest", "-v", "test_probe", "test_correlated_observers"]),
    (ROOT, ["-m", "unittest", "discover", "-s", "authority_boundary_lab", "-p", "test_*.py", "-v"]),
    (ROOT / "authority_boundary_lab_v0_5", ["-m", "unittest", "-v", "test_authority_gate_v0_5", "test_fake_host_adapter"]),
]

for cwd, args in SUITES:
    label = cwd.relative_to(ROOT).as_posix() if cwd != ROOT else "."
    print(f"\n=== {label}: python {' '.join(args)} ===", flush=True)
    completed = subprocess.run(
        [sys.executable, *args], cwd=cwd, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    print(completed.stdout, end="", flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
print("\nALL LEGACY SUITES PASSED (66 tests)", flush=True)
