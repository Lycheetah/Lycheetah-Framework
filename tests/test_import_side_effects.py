"""Importing a library module must neither require nor rewrite the host's stdout."""
import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT / "12_IMPLEMENTATIONS"
MODULES = ["triad_wuwei", "harmonia_calculator", "calibrate_master_equation", "sovereign_pipeline",
           "aura_score_hexie", "triad_tracker", "microorcim_tracker"]

# Import the module three times: with no stdout (pythonw), with a StringIO
# (encoding None), and with an ASCII stream whose encoding must survive.
PROBE = """
import io, sys
sys.path[:0] = sys.argv[2:]
real = sys.stdout
host = io.TextIOWrapper(io.BytesIO(), encoding="ascii")
for stream in (None, io.StringIO(), host):
    sys.stdout = stream
    try:
        __import__(sys.argv[1])
    finally:
        sys.stdout = real
    sys.modules.pop(sys.argv[1])
print(host.encoding)
"""


@pytest.mark.parametrize("module", MODULES)
def test_import_leaves_stdout_alone(module, tmp_path):
    paths = [str(IMPL / "core"), str(IMPL), str(IMPL / "applications")]
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run([sys.executable, "-c", PROBE, module, *paths], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, proc.stderr[-600:]
    assert proc.stdout.strip().splitlines()[-1] == "ascii"


def _library_nodes(tree):
    script = set()
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test):
            script.update(id(n) for n in ast.walk(node))
    return [n for n in ast.walk(tree) if id(n) not in script]


def test_only_script_entry_points_touch_stdout():
    offenders = []
    for path in sorted(IMPL.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in _library_nodes(tree):
            rebinds = isinstance(node, ast.Assign) and any(ast.unparse(t) == "sys.stdout" for t in node.targets)
            reconfigures = isinstance(node, ast.Call) and ast.unparse(node.func) == "sys.stdout.reconfigure"
            if rebinds or reconfigures:
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert offenders == []


def test_demo_runs_twice_without_rebinding_stdout(capsys):
    tri_axial = importlib.import_module("lycheetah.core.tri_axial_checker")
    before = sys.stdout
    tri_axial.demo()
    tri_axial.demo()
    assert sys.stdout is before
    assert capsys.readouterr().out.count("TRI-AXIAL CONSTITUTIONAL METRICS CHECKER") == 2
