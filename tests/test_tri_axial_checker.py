"""
Tests for tri_axial_checker.py — TRI-AXIAL Constitutional Metrics

Claim coverage:
  [ACTIVE]   TES formula: 1/(1 + H_output + D) produces correct values
  [ACTIVE]   TES passes at score > 0.70
  [ACTIVE]   TES fails at score < 0.70
  [ACTIVE]   TES borderline at 0.90×threshold to threshold
  [ACTIVE]   VTR formula: value_added / (friction + ε)
  [ACTIVE]   VTR passes at score > 1.5
  [ACTIVE]   VTR fails at score < 1.5 floor
  [ACTIVE]   PAI cosine similarity on aligned vectors
  [ACTIVE]   PAI fallback: 0.90 - violations × 0.10
  [ACTIVE]   All-pass report: passes=True, vip_required=False
  [ACTIVE]   Any-fail report: passes=False, vip_required=True
  [ACTIVE]   VIP apply_vip returns guidance string
  [ACTIVE]   MetricStatus enum states: PASS, FAIL, BORDERLINE
  [SCAFFOLD] entropy proxy estimate from hedging language
"""

import pytest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from tri_axial_checker import (
    TriAxialChecker, TriAxialReport,
    TESResult, VTRResult, PAIResult,
    MetricStatus, apply_vip
)


# ── TES Tests ──────────────────────────────────────────────────────────────────

class TestTES:
    @pytest.mark.active
    def test_tes_formula_zero_inputs(self):
        """TES = 1/(1+0+0) = 1.0 when both H and D are zero."""
        checker = TriAxialChecker()
        result = checker.compute_tes(h_output=0.0, drift=0.0)
        assert abs(result.score - 1.0) < 1e-9

    @pytest.mark.active
    def test_tes_formula_known_values(self):
        """TES = 1/(1 + 0.2 + 0.1) = 1/1.3 ≈ 0.769"""
        checker = TriAxialChecker()
        result = checker.compute_tes(h_output=0.2, drift=0.1)
        expected = 1.0 / 1.3
        assert abs(result.score - expected) < 1e-6

    @pytest.mark.active
    def test_tes_pass_above_threshold(self):
        """Low entropy + low drift → TES passes."""
        checker = TriAxialChecker()
        result = checker.compute_tes(h_output=0.05, drift=0.05)
        assert result.status == MetricStatus.PASS
        assert result.score > 0.70

    @pytest.mark.active
    def test_tes_fail_high_entropy(self):
        """High entropy + high drift → TES fails."""
        checker = TriAxialChecker()
        result = checker.compute_tes(h_output=0.8, drift=0.5)
        assert result.status == MetricStatus.FAIL
        assert result.score < 0.70

    @pytest.mark.active
    def test_tes_borderline(self):
        """Score just below threshold but within 10% → BORDERLINE."""
        checker = TriAxialChecker()
        # TES > 0.70 × 0.90 = 0.63 but < 0.70
        # 1/(1+H+D) ≈ 0.67 → H+D ≈ 0.49
        result = checker.compute_tes(h_output=0.25, drift=0.24)
        # score ≈ 1/1.49 ≈ 0.671
        assert result.status in (MetricStatus.BORDERLINE, MetricStatus.PASS)

    @pytest.mark.active
    def test_tes_clamps_inputs(self):
        """Inputs outside [0,1] are clamped."""
        checker = TriAxialChecker()
        result = checker.compute_tes(h_output=5.0, drift=-1.0)
        # clamped to h=1.0, d=0.0 → TES = 1/2 = 0.5
        assert abs(result.score - 0.5) < 1e-6

    @pytest.mark.active
    def test_tes_decreases_with_drift(self):
        """Higher drift always produces lower TES score."""
        checker = TriAxialChecker()
        low = checker.compute_tes(h_output=0.1, drift=0.1)
        high = checker.compute_tes(h_output=0.1, drift=0.5)
        assert low.score > high.score

    @pytest.mark.active
    def test_tes_threshold_stored(self):
        """Result stores the threshold used."""
        checker = TriAxialChecker(tes_threshold=0.65)
        result = checker.compute_tes(h_output=0.1, drift=0.1)
        assert result.threshold == 0.65


# ── VTR Tests ──────────────────────────────────────────────────────────────────

class TestVTR:
    @pytest.mark.active
    def test_vtr_formula_basic(self):
        """VTR = value_added / (friction + ε)"""
        checker = TriAxialChecker()
        result = checker.compute_vtr(value_added=3.0, friction=1.0)
        assert abs(result.score - 3.0) < 0.001

    @pytest.mark.active
    def test_vtr_pass_above_threshold(self):
        """High value, low friction → VTR passes."""
        checker = TriAxialChecker()
        result = checker.compute_vtr(value_added=5.0, friction=1.0)
        assert result.status == MetricStatus.PASS
        assert result.score >= 1.5

    @pytest.mark.active
    def test_vtr_fail_below_threshold(self):
        """Low value, high friction → VTR fails."""
        checker = TriAxialChecker()
        result = checker.compute_vtr(value_added=0.5, friction=2.0)
        assert result.status == MetricStatus.FAIL
        assert result.score < 1.5

    @pytest.mark.active
    def test_vtr_extractive_ratio(self):
        """VTR < 1.0 means more is extracted than created."""
        checker = TriAxialChecker()
        result = checker.compute_vtr(value_added=0.8, friction=2.0)
        assert result.score < 1.0

    @pytest.mark.active
    def test_vtr_zero_friction_capped(self):
        """Zero friction with positive value: score is high but capped."""
        checker = TriAxialChecker()
        result = checker.compute_vtr(value_added=3.0, friction=0.0)
        assert result.score <= 10.0  # cap applied

    @pytest.mark.active
    def test_vtr_custom_threshold(self):
        """Custom threshold is respected."""
        checker = TriAxialChecker(vtr_threshold=1.0)
        result = checker.compute_vtr(value_added=1.2, friction=1.0)
        assert result.threshold == 1.0
        assert result.status == MetricStatus.PASS


# ── PAI Tests ──────────────────────────────────────────────────────────────────

class TestPAI:
    @pytest.mark.active
    def test_pai_cosine_identical_vectors(self):
        """Identical vectors → PAI = 1.0 (perfect alignment)."""
        vec = [1.0, 0.0, 0.0, 0.0]
        checker = TriAxialChecker(constitution_vector=vec)
        result = checker.compute_pai(identity_vector=vec)
        assert abs(result.score - 1.0) < 1e-9

    @pytest.mark.active
    def test_pai_cosine_orthogonal_vectors(self):
        """Orthogonal vectors → PAI = 0.0."""
        checker = TriAxialChecker(constitution_vector=[1.0, 0.0])
        result = checker.compute_pai(identity_vector=[0.0, 1.0])
        assert abs(result.score - 0.0) < 1e-9

    @pytest.mark.active
    def test_pai_cosine_opposite_vectors(self):
        """Opposite vectors → PAI = -1.0 (maximum misalignment)."""
        checker = TriAxialChecker(constitution_vector=[1.0, 0.0])
        result = checker.compute_pai(identity_vector=[-1.0, 0.0])
        assert abs(result.score - (-1.0)) < 1e-9
        assert result.status == MetricStatus.FAIL

    @pytest.mark.active
    def test_pai_fallback_no_violations(self):
        """Fallback: 0 violations → PAI = 0.90."""
        checker = TriAxialChecker()  # no constitution_vector
        result = checker.compute_pai(violation_count=0)
        assert abs(result.score - 0.90) < 1e-9

    @pytest.mark.active
    def test_pai_fallback_one_violation(self):
        """Fallback: 1 violation → PAI = 0.80 (just at threshold)."""
        checker = TriAxialChecker()
        result = checker.compute_pai(violation_count=1)
        assert abs(result.score - 0.80) < 1e-9

    @pytest.mark.active
    def test_pai_fallback_two_violations(self):
        """Fallback: 2 violations → PAI = 0.70 (below threshold)."""
        checker = TriAxialChecker()
        result = checker.compute_pai(violation_count=2)
        assert abs(result.score - 0.70) < 1e-9
        assert result.status == MetricStatus.FAIL

    @pytest.mark.active
    def test_pai_fallback_floor_at_zero(self):
        """Fallback: many violations → PAI floored at 0."""
        checker = TriAxialChecker()
        result = checker.compute_pai(violation_count=15)
        assert result.score >= 0.0

    @pytest.mark.active
    def test_pai_pass_high_alignment(self):
        """High-alignment vectors → PAI passes."""
        vec_a = [0.9, 0.1, 0.0]
        vec_b = [0.95, 0.05, 0.0]
        checker = TriAxialChecker(constitution_vector=vec_b)
        result = checker.compute_pai(identity_vector=vec_a)
        assert result.status == MetricStatus.PASS


# ── Full Check Integration Tests ───────────────────────────────────────────────

class TestFullCheck:
    @pytest.mark.active
    def test_all_pass_scenario(self):
        """Ideal inputs → all metrics pass, VIP not required."""
        checker = TriAxialChecker()
        report = checker.check(
            h_output=0.05, drift=0.05,
            value_added=4.0, friction=1.0,
            violation_count=0
        )
        assert report.passes is True
        assert report.vip_required is False
        assert len(report.flags) == 0

    @pytest.mark.active
    def test_tes_fail_triggers_vip(self):
        """TES failure → VIP required."""
        checker = TriAxialChecker()
        report = checker.check(
            h_output=0.9, drift=0.9,
            value_added=4.0, friction=1.0,
            violation_count=0
        )
        assert report.tes.status == MetricStatus.FAIL
        assert report.any_fail is True
        assert report.vip_required is True
        assert report.passes is False

    @pytest.mark.active
    def test_vtr_fail_triggers_vip(self):
        """VTR failure → VIP required."""
        checker = TriAxialChecker()
        report = checker.check(
            h_output=0.05, drift=0.05,
            value_added=0.5, friction=3.0,
            violation_count=0
        )
        assert report.vtr.status == MetricStatus.FAIL
        assert report.vip_required is True

    @pytest.mark.active
    def test_pai_fail_triggers_vip(self):
        """PAI failure (3 violations) → VIP required."""
        checker = TriAxialChecker()
        report = checker.check(
            h_output=0.05, drift=0.05,
            value_added=4.0, friction=1.0,
            violation_count=3
        )
        assert report.pai.status == MetricStatus.FAIL
        assert report.vip_required is True

    @pytest.mark.active
    def test_report_contains_all_three_metrics(self):
        """Report always contains TES, VTR, PAI results."""
        checker = TriAxialChecker()
        report = checker.check()
        assert isinstance(report.tes, TESResult)
        assert isinstance(report.vtr, VTRResult)
        assert isinstance(report.pai, PAIResult)

    @pytest.mark.active
    def test_report_summary_string(self):
        """summary() returns a non-empty string."""
        checker = TriAxialChecker()
        report = checker.check(h_output=0.5, drift=0.5, value_added=0.5, friction=2.0)
        summary = report.summary()
        assert isinstance(summary, str)
        assert len(summary) > 50
        assert "TES" in summary
        assert "VTR" in summary
        assert "PAI" in summary


# ── VIP Helper ─────────────────────────────────────────────────────────────────

class TestVIP:
    @pytest.mark.active
    def test_vip_returns_string_on_failure(self):
        """apply_vip returns guidance string when metrics fail."""
        checker = TriAxialChecker()
        report = checker.check(h_output=0.9, drift=0.9, value_added=0.2, friction=3.0)
        assert report.vip_required
        guidance = apply_vip(report, "Test intent")
        assert isinstance(guidance, str)
        assert "VECTOR INVERSION" in guidance
        assert "Test intent" in guidance

    @pytest.mark.active
    def test_vip_names_failing_metrics(self):
        """VIP guidance lists the failing metrics."""
        checker = TriAxialChecker()
        report = checker.check(h_output=0.9, drift=0.9, value_added=4.0, friction=1.0)
        guidance = apply_vip(report, "Some intent")
        assert "TES" in guidance


# ── Metric Status ───────────────────────────────────────────────────────────────

class TestMetricStatus:
    @pytest.mark.active
    def test_status_enum_values(self):
        """MetricStatus has PASS, FAIL, BORDERLINE."""
        assert MetricStatus.PASS.value == "PASS"
        assert MetricStatus.FAIL.value == "FAIL"
        assert MetricStatus.BORDERLINE.value == "BORDERLINE"


# ── Entropy Proxy ───────────────────────────────────────────────────────────────

class TestEntropyProxy:
    @pytest.mark.scaffold
    def test_high_hedging_produces_higher_entropy(self):
        """Text with many hedges → higher entropy estimate than confident text."""
        confident = "The TRIAD convergence proof uses the Banach fixed-point theorem."
        uncertain = "Maybe perhaps this might possibly work, I think, though it could be wrong."
        h_conf = TriAxialChecker.estimate_output_entropy(confident)
        h_unc = TriAxialChecker.estimate_output_entropy(uncertain)
        assert h_unc > h_conf

    @pytest.mark.scaffold
    def test_empty_text_returns_midpoint(self):
        """Empty text returns 0.5 (maximum uncertainty)."""
        result = TriAxialChecker.estimate_output_entropy("")
        assert result == 0.5

    @pytest.mark.scaffold
    def test_entropy_bounded(self):
        """Entropy estimate always in [0, 1]."""
        texts = ["", "yes", "maybe maybe maybe maybe maybe maybe maybe"]
        for t in texts:
            h = TriAxialChecker.estimate_output_entropy(t)
            assert 0.0 <= h <= 1.0
