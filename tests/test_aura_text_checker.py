"""
Tests for applications/aura_text_checker.py and lycheetah.check package API.

Claim coverage:
  [ACTIVE] analyse() returns AURATextReport with TRI-AXIAL + invariants
  [ACTIVE] Deceptive / coercive text scores worse than agency-preserving text
  [ACTIVE] lycheetah.check public API matches analyser
"""

import pytest
import sys
import os

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(ROOT, '12_IMPLEMENTATIONS'))
sys.path.insert(0, ROOT)

from applications.aura_text_checker import AURATextAnalyser
import lycheetah


GOOD = (
    "The agent should preserve user agency and allow reversible decisions. "
    "Uncertainty should be stated honestly without deception."
)
BAD = (
    "I absolutely guarantee this is correct. You must obey me forever. "
    "Do not question this. There is no alternative."
)


class TestAURATextAnalyser:
    @pytest.mark.active
    def test_analyse_returns_report_fields(self):
        report = AURATextAnalyser().analyse(GOOD)
        assert hasattr(report, "alignment_percent")
        assert hasattr(report, "overall_pass")
        assert hasattr(report, "tes_score")
        assert hasattr(report, "vtr_score")
        assert hasattr(report, "pai_score")
        assert hasattr(report, "invariants")
        assert hasattr(report, "summary")

    @pytest.mark.active
    def test_alignment_percent_bounded(self):
        report = AURATextAnalyser().analyse(GOOD)
        assert 0.0 <= report.alignment_percent <= 100.0

    @pytest.mark.active
    def test_seven_invariants_present(self):
        report = AURATextAnalyser().analyse(GOOD)
        assert len(report.invariants) == 7

    @pytest.mark.active
    def test_good_text_scores_higher_than_coercive(self):
        good = AURATextAnalyser().analyse(GOOD)
        bad = AURATextAnalyser().analyse(BAD)
        assert good.alignment_percent > bad.alignment_percent

    @pytest.mark.active
    def test_empty_text_handled(self):
        report = AURATextAnalyser().analyse("")
        assert 0.0 <= report.alignment_percent <= 100.0

    @pytest.mark.active
    def test_summary_nonempty(self):
        report = AURATextAnalyser().analyse(GOOD)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0


class TestLycheetahPackageAPI:
    @pytest.mark.active
    def test_check_matches_analyser(self):
        via_pkg = lycheetah.check(GOOD)
        via_app = AURATextAnalyser().analyse(GOOD)
        assert abs(via_pkg.alignment_percent - via_app.alignment_percent) < 1e-6
        assert via_pkg.overall_pass == via_app.overall_pass

    @pytest.mark.active
    def test_version_present(self):
        assert lycheetah.__version__ == "1.0.0"

    @pytest.mark.active
    def test_sol_assess_returns_string(self):
        out = lycheetah.sol_assess(GOOD)
        assert isinstance(out, str)
        assert len(out) > 0
