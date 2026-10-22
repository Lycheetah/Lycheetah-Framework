"""The LAMAGUE status register must take status from exit codes, not from printed words."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "03_LAMAGUE_L1"
SPEC = importlib.util.spec_from_file_location("lamague_register_under_test", ROOT / "lamague_register.py")
register = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = register  # dataclasses resolve their module by name
SPEC.loader.exec_module(register)

N36_FILES = ("validate_lamague_native36_v0.3.py", "LAMAGUE_NATIVE36_v0.3_MACHINE_CANON_REGISTRY.json")


def suite(tmp_path, body):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(
        "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_a(self):\n" + body)
    return tmp_path


def native36(tmp_path, mutate=None):
    for name in N36_FILES:
        shutil.copy(ROOT / "02_NATIVE36" / name, tmp_path / name)
    if mutate:
        path = tmp_path / N36_FILES[1]
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return register.passes([N36_FILES[0]], tmp_path)


def stub(tmp_path, code):
    (tmp_path / "spl.py").write_text(f"raise SystemExit({code})\n")
    return register.spoken_entry(tmp_path)


def test_failing_suite_that_prints_ok_is_not_counted(tmp_path):
    assert register.run_tests(suite(tmp_path, "        self.fail('TOKEN mismatch')\n")) is None


def test_passing_suite_reports_its_count(tmp_path):
    assert register.run_tests(suite(tmp_path, "        pass\n")) == 1


def test_invalid_native36_registry_is_not_valid(tmp_path):
    # the validator prints "INVALID", which contains "VALID"
    assert native36(tmp_path, mutate=lambda d: d["base_glyphs"].reverse()) is False


def test_committed_native36_registry_is_valid(tmp_path):
    assert native36(tmp_path) is True


@pytest.mark.parametrize("code, status", [(0, "MEASURED"), (1, "SCAFFOLD")])
def test_spoken_status_follows_its_verifier(tmp_path, code, status):
    assert stub(tmp_path, code).register == status


def test_committed_register_matches_a_fresh_derivation():
    committed = json.loads((ROOT / "LAMAGUE_STATUS_REGISTER.json").read_text(encoding="utf-8"))
    fresh = {(e.path, e.register) for e in register.derive()}
    assert {(e["path"], e["register"]) for e in committed["entries"]} == fresh


def test_retired_kernel_is_not_measured():
    retired = [e for e in register.derive() if e.path.startswith("13_RETIRED")]
    assert retired and all(e.register == "SCAFFOLD" for e in retired)
