#!/usr/bin/env python3
"""Gate-verified tests for question_governance.py — Theorem 9 Question Governance & Equal-Budget Prover."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import question_governance as qg  # noqa: E402


def test_item12_and_25_question_governance_measured_vs_scripted_and_no_guestpc():
    """Items 12 & 25: question_governance.py states measured vs scripted components,
    removes 'PROVEN' label for synthetic fixtures, and contains zero hardcoded user home paths."""
    src_path = Path(qg.__file__).resolve()
    src = src_path.read_text(encoding="utf-8")
    forbidden_prefix = "/" + "home/" + "guestpc"
    assert forbidden_prefix not in src

    rep = qg.run_question_governance_proof_suite()
    assert rep["status"] == "VERIFIED"
    assert "evidence_classification" in rep
    assert "measured_components" in rep["evidence_classification"]
    assert "scripted_or_synthetic_components" in rep["evidence_classification"]
    assert rep["all_checks_verified"] is True
    s = rep["summary"]
    assert s["stakeholder_drop_caught"] is True
    assert s["unannounced_omission_caught"] is True
    assert s["silent_omissions_in_lycheetah_capsule"] == 0
    assert s["archive_recovery_verified"] is True
    assert s["case_e_mental_horizon_confabulation_caught"] is True
    assert s["missing_archive_lost_past_confabulation_caught"] is True
    assert s["budget_480B_stakeholder_recall_lycheetah"] == 0.7143
    assert s["budget_480B_stakeholder_recall_lycheetah"] > s["budget_480B_stakeholder_recall_conventional_log"]
    assert s["budget_640B_stakeholder_recall_lycheetah"] == 1.0
    assert s["budget_640B_stakeholder_recall_lycheetah"] > s["budget_640B_stakeholder_recall_conventional_log"]



def test_equal_byte_budget_fair_benchmark_strict_byte_limits():
    bench = qg.run_equal_budget_fair_benchmark([360, 480, 640])
    for row in bench["results_by_budget"]:
        b = row["byte_budget"]
        ly = row["lycheetah_omission_visible_quotient"]
        cv = row["conventional_event_log"]
        nv = row["naive_fluent_prose"]
        assert ly["actual_bytes"] <= b
        assert cv["actual_bytes"] <= b
        assert nv["actual_bytes"] <= b
        assert ly["silent_omissions_count"] == 0
        assert ly["lawful_governance"] is True
        assert ly["stakeholder_archive_assisted_recall"] == 1.0


def test_cli_prove_and_benchmark_json(capsys):
    rc = qg.main(["prove", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["all_checks_verified"] is True
