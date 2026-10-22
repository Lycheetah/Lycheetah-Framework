"""
Tests for applications/cascade_curriculum_architect.py — reality anchors and report honesty.

Claim coverage:
  [ACTIVE] a forecast change is Cohen's d in SD units, never d times the scale range
  [ACTIVE] raw-point change appears only when the scale carries a sourced SD
  [ACTIVE] the report does not promise automatic evaluation or demotion
  [ACTIVE] the shadow-work protocol does not claim cohort evidence it does not cite
"""

import dataclasses
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS'))

from applications.cascade_curriculum_architect import (  # noqa: E402
    CurriculumArchitect,
    EvidenceLevel,
)


@pytest.fixture(scope="module")
def architect():
    return CurriculumArchitect()


def _anchors(protocol):
    return {a["name"]: a for a in protocol.generate_reality_anchors()}


def test_breathwork_anxiety_is_d_in_sd_units(architect):
    a = _anchors(architect.generate_breathwork_course())["Anxiety"]
    assert a["expected_delta_sd"] == pytest.approx(-0.55)
    assert a["expected_delta"] is None  # GAD-7 carries no sourced SD


def test_raw_change_uses_sd_not_range(architect, monkeypatch):
    protocol = architect.generate_breathwork_course()
    scale = protocol._match_scale_to_outcome("Anxiety")
    with_sd = dataclasses.replace(scale, population_sd=5.0)
    monkeypatch.setattr(type(protocol), "_match_scale_to_outcome", lambda self, name: with_sd)
    a = _anchors(protocol)["Anxiety"]
    assert a["expected_delta"] == pytest.approx(-0.55 * 5.0)


@pytest.mark.parametrize("course", ["generate_breathwork_course",
                                    "generate_shadow_work_course",
                                    "generate_mindfulness_course"])
def test_no_forecast_exceeds_one_and_a_half_sd(architect, course):
    for a in getattr(architect, course)().generate_reality_anchors():
        assert abs(a["expected_delta_sd"]) <= 1.5, a


def test_report_promises_no_automatic_demotion(architect):
    report = architect.generate_research_report(architect.generate_mindfulness_course())
    assert "automatically demoted" not in report
    assert "will be automatically" not in report
    assert "SD" in report


def test_shadow_work_does_not_claim_cohort_evidence(architect):
    p = architect.generate_shadow_work_course()
    assert p.evidence_level != EvidenceLevel.COHORT
    assert not any("Stein (2004)" in s for s in p.key_studies)
