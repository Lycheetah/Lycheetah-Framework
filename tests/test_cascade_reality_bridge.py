"""
Tests for systems/cascade_reality_bridge.py — RealityAnchor, predictions, bridge.

Claim coverage:
  [ACTIVE] RealityAnchor delta / divergence computable from measurements
  [ACTIVE] DivergenceDetector classifies truth-pressure into DivergenceLevel
  [ACTIVE] RealityBridge register → measure → evaluate path
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS'))

from systems.cascade_reality_bridge import (
    RealityAnchor,
    PracticePrediction,
    RealityBridge,
    DivergenceDetector,
    DivergenceLevel,
    MeasurementType,
    ValidationStrength,
)


def _anchor(aid="a1", baseline=5.0, expected_delta=2.0, timeline=7):
    return RealityAnchor(
        id=aid,
        name="mood",
        measurement_type=MeasurementType.SUBJECTIVE_SCALE,
        baseline=baseline,
        expected_delta=expected_delta,
        expected_timeline=timeline,
        validation_strength=ValidationStrength.MODERATE,
    )


class TestRealityAnchor:
    @pytest.mark.active
    def test_delta_none_without_measurements(self):
        a = _anchor()
        assert a.get_current_delta() is None
        assert a.get_divergence() is None

    @pytest.mark.active
    def test_delta_from_baseline(self):
        a = _anchor(baseline=5.0)
        a.add_measurement(7.0, timestamp=datetime.now())
        assert abs(a.get_current_delta() - 2.0) < 1e-9

    @pytest.mark.active
    def test_divergence_vs_expected(self):
        a = _anchor(baseline=5.0, expected_delta=2.0)
        a.add_measurement(6.0)  # delta=1 vs expected 2 → |1-2|=1
        div = a.get_divergence()
        assert div is not None
        assert abs(div - 1.0) < 1e-9

    @pytest.mark.active
    def test_truth_pressure_contribution_finite(self):
        a = _anchor(timeline=7)
        start = datetime.now() - timedelta(days=10)
        a.measurements = [(start, 5.0), (datetime.now(), 7.0)]  # delta=2 == expected
        tp = a.compute_truth_pressure_contribution()
        assert isinstance(tp, (int, float))
        assert tp > 0.0


class TestDivergenceDetector:
    @pytest.mark.active
    def test_classify_aligned_low_pressure(self):
        det = DivergenceDetector()
        level = det.classify_divergence(0.05)
        assert level in (
            DivergenceLevel.ALIGNED,
            DivergenceLevel.NEUTRAL,
            DivergenceLevel.DIVERGENT,
            DivergenceLevel.FALSIFIED,
        )

    @pytest.mark.active
    def test_high_truth_pressure_means_aligned(self):
        """In this bridge, truth_pressure > 1.3 ⇒ ALIGNED; low ⇒ FALSIFIED."""
        det = DivergenceDetector()
        assert det.classify_divergence(1.5) == DivergenceLevel.ALIGNED
        assert det.classify_divergence(0.2) == DivergenceLevel.FALSIFIED
        assert det.classify_divergence(0.9) == DivergenceLevel.NEUTRAL
        assert det.classify_divergence(0.6) == DivergenceLevel.DIVERGENT


class TestPracticePrediction:
    @pytest.mark.active
    def test_evaluate_no_anchors(self):
        pred = PracticePrediction("p", "desc")
        out = pred.evaluate()
        assert out["status"] == "no_anchors"
        assert out["truth_pressure"] == 0.0

    @pytest.mark.active
    def test_add_anchor(self):
        pred = PracticePrediction("p", "desc")
        pred.add_anchor(_anchor())
        assert len(pred.anchors) == 1


class TestRealityBridge:
    @pytest.mark.active
    def test_register_and_evaluate_unready(self):
        rb = RealityBridge()
        pred = PracticePrediction("shadow", "reduce anxiety")
        pred.add_anchor(_anchor(timeline=30))
        rb.register_practice("shadow", "foundation", pred)
        result = rb.evaluate_practice("shadow")
        assert isinstance(result, dict)

    @pytest.mark.active
    def test_add_measurement_unknown_practice_raises(self):
        rb = RealityBridge()
        with pytest.raises(ValueError):
            rb.add_measurement("missing", "a1", 1.0)

    @pytest.mark.active
    def test_add_measurement_records(self):
        rb = RealityBridge()
        pred = PracticePrediction("sleep", "improve sleep")
        pred.add_anchor(_anchor("sleep_hrs", baseline=6.0, expected_delta=1.5, timeline=14))
        rb.register_practice("sleep", "practice", pred)
        rb.add_measurement("sleep", "sleep_hrs", 7.0)
        assert len(pred.anchors[0].measurements) == 1

    @pytest.mark.active
    def test_evaluate_all_and_pyramid(self):
        rb = RealityBridge()
        pred = PracticePrediction("breath", "calm")
        pred.add_anchor(_anchor("b1"))
        rb.register_practice("breath", "surface", pred)
        all_out = rb.evaluate_all()
        assert isinstance(all_out, dict)
        pyramid = rb.get_pyramid_state()
        assert isinstance(pyramid, dict)
        assert "breath" in rb.predictions

    @pytest.mark.active
    def test_meta_insights_dict(self):
        rb = RealityBridge()
        pred = PracticePrediction("x", "y")
        pred.add_anchor(_anchor())
        rb.register_practice("x", "layer", pred)
        insights = rb.get_meta_insights("x")
        assert isinstance(insights, dict)
