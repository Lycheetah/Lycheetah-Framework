"""
Tests for framework-threads-2026-09-24 load-bearing / useful thread finishes.

Covers path-root repairs, import-time crashers, optional-dep soft fails,
and chorus agent module split (re-exports).
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT / "12_IMPLEMENTATIONS"
CHORUS = ROOT / "19_MULTI_AGENT_CHORUS"
PY = sys.executable


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_alexandria_framework_dir_is_repo_root():
    alex = _load("alexandria_agent_under_test", IMPL / "alexandria_agent.py")
    assert alex.FRAMEWORK_DIR.resolve() == ROOT.resolve()


def test_alexandria_health_finds_core_modules():
    alex = _load("alexandria_agent_health", IMPL / "alexandria_agent.py")
    status, report = alex.health_check()
    assert "ALL MODULES PASS" in report
    for name in alex.CORE_MODULES:
        assert status[name] == "OK" or status[name].startswith("OK")


def test_alexandria_gaps_mostly_green():
    alex = _load("alexandria_agent_gaps", IMPL / "alexandria_agent.py")
    status, report = alex.gap_report()
    assert status["unit_tests"] == "GREEN"
    assert status["ci_workflow"] == "GREEN"
    assert status["k1_k4_calibration"] == "GREEN"
    assert status["domain_experiments_2plus"] == "GREEN"
    # Curriculum absent — labeled MISSING_SPEC (do not invent 12_WEEK_*.md)
    assert status["12_week_curriculum"] == "MISSING_SPEC"


def test_agent_init_load_frameworks():
    # Import without running main
    init = _load("agent_init_under_test", IMPL / "agent-init.py")
    assert init.load_frameworks() is True


def test_phi_bandit_imports_without_running_suite():
    """Regression: suite used to execute at import time (~minutes)."""
    code = (
        "import sys, time; "
        f"sys.path.insert(0, {str(IMPL)!r}); "
        "t0=time.time(); import phi_bandit; "
        "assert time.time()-t0 < 3.0; "
        "assert hasattr(phi_bandit, 'main'); "
        "assert abs(phi_bandit.PHI_INV - 0.618) < 0.01"
    )
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=8)
    assert r.returncode == 0, r.stderr


def test_web_demo_imports_without_flask():
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(IMPL)!r}); "
        "from applications.web_demo import app, FLASK_AVAILABLE; "
        "assert FLASK_AVAILABLE in (True, False)"
    )
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, r.stderr


def test_lycheetah_guard_imports_without_mcp():
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(IMPL)!r}); "
        "from applications import lycheetah_guard_mcp as g; "
        "assert hasattr(g, 'MCP_AVAILABLE'); "
        "assert hasattr(g, 'build_server')"
    )
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, r.stderr


def test_knowledge_genome_has_json_and_time():
    kg = _load("knowledge_genome_under_test", IMPL / "systems" / "knowledge_genome.py")
    assert hasattr(kg, "json")
    assert hasattr(kg, "time")


def test_sol_companion_runs_without_rich():
    r = subprocess.run(
        [PY, str(IMPL / "applications" / "sol_companion.py"), "notify", "thread-test"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, r.stderr
    out = (r.stdout or "") + (r.stderr or "")
    assert "thread-test" in out


@pytest.mark.parametrize(
    "module_name,class_name",
    [
        ("albedo_synthesizer", "AlbedoSynthesizer"),
        ("solstice_illuminator", "SolsticeIlluminator"),
        ("protector_guardian", "ProtectorGuardian"),
        ("healer_transmuter", "HealerTransmuter"),
        ("beacon_reflector", "BeaconReflector"),
        ("cascade_architect", "CascadeArchitect"),
        ("harmonia_resonator", "HarmoniaResonator"),
    ],
)
def test_chorus_split_modules_export(module_name, class_name):
    path = CHORUS / f"{module_name}.py"
    assert path.exists(), f"missing {path}"
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(CHORUS)!r}); "
        f"import {module_name} as m; "
        f"assert hasattr(m, {class_name!r}); "
        f"a = m.{class_name}(); assert a is not None"
    )
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr


def test_run_chorus_typing_import_present():
    src = (CHORUS / "run_chorus.py").read_text(encoding="utf-8")
    assert "from typing import Dict" in src


def test_cli_guard_reports_missing_mcp_clearly():
    """lycheetah-guard should exit 1 with a clear message when mcp is absent."""
    # Invoke guard_cli via python -c using the package path
    code = (
        "import sys, os; "
        f"sys.path.insert(0, {str(ROOT)!r}); "
        f"sys.path.insert(0, {str(IMPL)!r}); "
        "from lycheetah.cli import guard_cli; "
        "sys.argv = ['lycheetah-guard']; "
        "try:\n"
        "    guard_cli()\n"
        "except SystemExit as e:\n"
        "    sys.exit(e.code if e.code is not None else 0)"
    )
    # The above nested try is awkward in -c; use a small script file instead via stdin
    script = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
sys.path.insert(0, {str(IMPL)!r})
from lycheetah.cli import guard_cli
sys.argv = ["lycheetah-guard"]
guard_cli()
"""
    r = subprocess.run([PY, "-c", script], capture_output=True, text=True, timeout=15)
    # Without mcp extra, expect non-zero and helpful message
    combined = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0:
        pytest.skip("mcp is installed in this environment")
    assert "mcp" in combined.lower()


def test_chrysopoeia_post_init_clamps_bounds():
    import sys
    import numpy as np
    sys.path.insert(0, str(IMPL / "core"))
    from chrysopoeia_engine import TransformationState
    s = TransformationState(vector=np.zeros(2), coherence=1.7, entropy=-0.5)
    assert 0.0 <= s.coherence <= 1.0
    assert 0.0 <= s.entropy <= 1.0


def test_harmonia_calculator_constructs_without_empty_init():
    import sys
    sys.path.insert(0, str(IMPL / "core"))
    from harmonia_calculator import HarmoniaCalculator
    assert HarmoniaCalculator().interval_name(0.0) == "unison"


def test_unified_field_from_vector_uses_field_names():
    import sys
    import numpy as np
    sys.path.insert(0, str(IMPL / "systems"))
    from unified_field import FieldState, Domain
    shapes = {d: (2,) for d in Domain}
    fs = FieldState.from_vector(np.arange(12, dtype=float), shapes)
    assert fs.physics.shape == (2,)
    assert isinstance(fs.timestamp, float)


def test_visualizer_export_all_data_uses_timeseries_schema(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "14_MYSTERY_SCHOOL" / "implementations"))
    from visualization_system import Visualizer, TimeSeriesData
    v = Visualizer()
    data = TimeSeriesData([0, 1], [0.1, 0.2], "agent-a")
    v.plot_drift_over_time({"agent-a": data})  # records series even without matplotlib show
    out = tmp_path / "viz.json"
    payload = v.export_all_data(str(out))
    assert out.exists()
    assert payload["series"]["drift:agent-a"]["label"] == "agent-a"


def test_chorus_readme_marks_ci_workflow_missing():
    readme = (CHORUS / "README.md").read_text(encoding="utf-8")
    assert "MISSING" in readme
    assert "multi-agent-chorus.yml" in readme
