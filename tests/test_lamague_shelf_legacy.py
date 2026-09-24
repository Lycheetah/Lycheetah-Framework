"""
Bridge for LAMAGUE shelf packages that cannot share one import session.

Ontology v0.2 and Algebra v0.1 both install as `lamague_core`, so they collide
with Operator Algebra v0.3 when collected in-process. RUNTIME v0.2 tests are
already included under RUNTIME v0.3's test_runtime_v02.py.

This module runs the colliding suites in isolated subprocesses with correct
PYTHONPATH so they still gate the root `pytest` suite.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable

LEGACY_SUITES = [
    {
        "id": "core_ontology_v0.2",
        "root": REPO / "03_LAMAGUE_L1/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ONTOLOGY_v0.2",
        "tests": "tests",
    },
    {
        "id": "core_algebra_v0.1",
        "root": REPO / "03_LAMAGUE_L1/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ALGEBRA_v0.1",
        "tests": "tests",
    },
]


@pytest.mark.lamague_shelf
@pytest.mark.parametrize("suite", LEGACY_SUITES, ids=[s["id"] for s in LEGACY_SUITES])
def test_legacy_shelf_suite_green(suite):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(suite["root"]) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [PY, "-m", "pytest", suite["tests"], "-q", "--tb=line"],
        cwd=str(suite["root"]),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"{suite['id']} failed (exit {proc.returncode})\n"
        f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
    )
