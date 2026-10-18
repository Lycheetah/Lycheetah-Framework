"""Tests for `lycheetah-cascade` CLI entry point.

Claim coverage:
  [ACTIVE] `lycheetah-cascade demo` executes quantum and germ domain historical traces
  [ACTIVE] `lycheetah-cascade eval` calculates truth pressure Pi = E*P/S on user-provided blocks
  [ACTIVE] `lycheetah-cascade eval --json` outputs structured layer distribution and coherence
"""
from __future__ import annotations

import io
import json
import pytest

from lycheetah.cli import cascade_cli


@pytest.mark.active
def test_cascade_cli_demo_quantum(capsys):
    cascade_cli(["demo", "--domain", "quantum"])
    out = capsys.readouterr().out
    assert "HISTORICAL TRACE: Classical → Quantum Mechanics" in out
    assert "CASCADE! Compressed:" in out
    assert "FINAL STRUCTURE:" in out
    assert "[FOUNDATION]" in out
    assert "Score: 7/7" in out


@pytest.mark.active
def test_cascade_cli_demo_germ(capsys):
    cascade_cli(["demo", "--domain", "germ"])
    out = capsys.readouterr().out
    assert "HISTORICAL TRACE: Miasma → Germ Theory" in out
    assert "Score: 5/5" in out


@pytest.mark.active
def test_cascade_cli_eval_file(tmp_path, capsys):
    claims_file = tmp_path / "claims.json"
    claims_data = [
        {
            "id": "claim_geocentric",
            "content": "Ptolemaic epicycles explain celestial movement",
            "domain": "astronomy",
            "paradigm": "ptolemaic",
            "evidence_strength": 0.4,
            "explanatory_power": 1.2,
            "uncertainty": 0.6,
        },
        {
            "id": "claim_heliocentric",
            "content": "Keplerian elliptical orbits explain celestial movement",
            "domain": "astronomy",
            "paradigm": "copernican",
            "evidence_strength": 0.95,
            "explanatory_power": 2.7,
            "uncertainty": 0.08,
        },
    ]
    claims_file.write_text(json.dumps(claims_data), encoding="utf-8")

    # Text mode
    cascade_cli(["eval", str(claims_file)])
    out = capsys.readouterr().out
    assert "CASCADE KNOWLEDGE REORGANIZATION EVALUATION" in out
    assert "Total Blocks:   2" in out
    assert "claim_heliocentric" in out
    assert "claim_geocentric" in out

    # JSON mode
    cascade_cli(["eval", str(claims_file), "--json"])
    json_data = json.loads(capsys.readouterr().out)
    assert json_data["total_blocks"] == 2
    assert "coherence" in json_data
    assert "layers" in json_data
    assert len(json_data["blocks"]) == 2


@pytest.mark.active
def test_cascade_cli_eval_stdin(monkeypatch, capsys):
    claims_data = [
        {
            "id": "synthetic_claim",
            "content": "Single claim piped via stdin",
            "domain": "test",
            "paradigm": "standard",
            "evidence_strength": 0.8,
            "explanatory_power": 1.5,
            "uncertainty": 0.2,
        }
    ]
    fake_stdin = io.StringIO(json.dumps(claims_data))
    monkeypatch.setattr("sys.stdin", fake_stdin)

    cascade_cli(["eval", "-", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["total_blocks"] == 1
    assert data["blocks"][0]["id"] == "synthetic_claim"
    assert data["blocks"][0]["layer"] == "FOUNDATION"
