"""Tests for `lycheetah-alexandria` CLI entry point.

Claim coverage:
  [ACTIVE] `lycheetah-alexandria health` smoke tests core modules
  [ACTIVE] `lycheetah-alexandria health --json` outputs structured module pass/fail dictionary
  [ACTIVE] `lycheetah-alexandria drift` audits spec constants vs code bindings
  [ACTIVE] `lycheetah-alexandria gaps` verifies known gap checklist
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from lycheetah.cli import alexandria_cli


@pytest.mark.active
def test_alexandria_cli_health_text(capsys):
    alexandria_cli(["health"])
    out = capsys.readouterr().out
    assert "ALEXANDRIA HEALTH CHECK" in out
    assert "cascade_engine" in out
    assert "ALL MODULES PASS" in out


@pytest.mark.active
def test_alexandria_cli_health_json(capsys):
    alexandria_cli(["health", "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["all_passed"] is True
    assert "cascade_engine" in data["modules"]
    assert "harmonia_calculator" in data["modules"]


@pytest.mark.active
def test_alexandria_cli_drift_text_and_json(capsys):
    # Text mode
    alexandria_cli(["drift"])
    out = capsys.readouterr().out
    assert "ALEXANDRIA DRIFT AUDIT" in out
    assert "NO DIVERGENCE DETECTED" in out

    # JSON mode
    alexandria_cli(["drift", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["has_divergence"] is False
    assert data["divergence_count"] == 0


@pytest.mark.active
def test_alexandria_cli_gaps_text_and_json(capsys):
    # Text mode
    with pytest.raises(SystemExit) as text_error:
        alexandria_cli(["gaps"])
    assert text_error.value.code == 1
    out = capsys.readouterr().out
    assert "ALEXANDRIA GAP REPORT" in out
    assert "k1_k4_calibration" in out

    # JSON mode
    with pytest.raises(SystemExit) as json_error:
        alexandria_cli(["gaps", "--json"])
    assert json_error.value.code == 1
    data = json.loads(capsys.readouterr().out)
    assert data["all_green"] is False
    assert data["red_count"] == 0
    assert data["pending_count"] >= 1
    assert data["gaps"]["12_week_curriculum"] == "MISSING_SPEC"
    assert "unit_tests" in data["gaps"]


@pytest.mark.active
def test_alexandria_cli_scaffold_mocked(monkeypatch, capsys):
    monkeypatch.setattr(
        "alexandria_agent.scaffold_new_domain",
        lambda name, desc: Path(f"/mocked/path/{name}.py"),
    )
    alexandria_cli(["scaffold", "quantum_gravity", "--description", "Test domain"])
    out = capsys.readouterr().out
    assert "✓ Created domain experiment: /mocked/path/quantum_gravity.py" in out
