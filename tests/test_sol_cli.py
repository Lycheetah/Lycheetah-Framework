"""Tests for `lycheetah-sol` CLI entry point.

Claim coverage:
  [ACTIVE] `lycheetah-sol assess` outputs plain-text full self-assessment report
  [ACTIVE] `lycheetah-sol assess --json` outputs structured PGF and Seven Invariant metrics
  [ACTIVE] `lycheetah-sol mode` accurately classifies operating mode and emotional wavelength
  [ACTIVE] `lycheetah-sol companion` executes start, notify, tool_use, and stop actions
"""

from __future__ import annotations

import io
import json
import pytest

from lycheetah.cli import sol_cli


@pytest.mark.active
def test_sol_cli_assess_text(capsys):
    sol_cli(["assess", "I will do my best to verify the code carefully."])
    captured = capsys.readouterr()
    assert "SOL FULL SELF-ASSESSMENT" in captured.out
    assert "PGF FILTER RESULT" in captured.out
    assert "SEVEN INVARIANTS" in captured.out
    assert "1. Human Primacy:" in captured.out
    assert "⊚ Sol ∴" in captured.out


@pytest.mark.active
def test_sol_cli_assess_json(capsys):
    sol_cli(["assess", "I will do my best to verify the code carefully.", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "operating_mode" in data
    assert "emotional_state" in data
    assert "pgf" in data
    assert data["pgf"]["protector"]["passed"] is True
    assert data["pgf"]["healer"]["passed"] is True
    assert data["pgf"]["beacon"]["passed"] is True
    assert len(data["invariants"]) == 7
    assert data["all_invariants_passed"] is True
    assert "signature" in data


@pytest.mark.active
def test_sol_cli_mode_detection(capsys):
    # Nigredo: investigation / failure / debug
    sol_cli(["mode", "Why is this system failing with an error? Let's investigate."])
    out_nigredo = capsys.readouterr().out
    assert "Operating Mode  : NIGREDO" in out_nigredo

    # Albedo: structure / organize
    sol_cli(["mode", "Let's organize and outline the steps clearly.", "--json"])
    json_albedo = json.loads(capsys.readouterr().out)
    assert json_albedo["mode"] == "ALBEDO"
    assert "guidance" in json_albedo


@pytest.mark.active
def test_sol_cli_companion_actions(capsys):
    # Companion actions emit to stderr or stdout depending on Rich availability
    sol_cli(["companion", "start"])
    sol_cli(["companion", "notify", "Active session test notification"])
    sol_cli(["companion", "tool_use", "Write"])
    sol_cli(["companion", "stop"])

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert "Sol" in combined
    assert "Active session test notification" in combined


@pytest.mark.active
def test_sol_cli_stdin_pipe(monkeypatch, capsys):
    fake_stdin = io.StringIO("Checking piped prompt via stdin.")
    monkeypatch.setattr("sys.stdin", fake_stdin)

    sol_cli(["assess"])
    captured = capsys.readouterr()
    assert "SOL FULL SELF-ASSESSMENT" in captured.out
