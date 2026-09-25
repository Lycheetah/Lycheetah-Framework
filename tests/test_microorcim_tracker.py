"""
Tests for microorcim_tracker.py — drift, stability, sovereignty.

Claim coverage:
  [ACTIVE] ρ_drift = |intended − actual| / Δt  (Δt = 24h daily budget)
  [ACTIVE] Sovereignty_score = (1 − ρ_drift) · ρ_stability ∈ [0,1]
  [ACTIVE] Zero drift when intended == actual
  [ACTIVE] Persistence to data_dir
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from microorcim_tracker import MicroorcimTracker


@pytest.fixture
def tracker(tmp_path):
    return MicroorcimTracker(data_dir=tmp_path)


class TestDrift:
    @pytest.mark.active
    def test_zero_drift_when_matched(self, tracker):
        tracker.add_intention("focus", 4.0)
        tracker.add_actual("focus", 4.0)
        drift, details = tracker.calculate_drift()
        assert abs(drift) < 1e-12
        assert details[0]["drift"] == 0.0

    @pytest.mark.active
    def test_drift_formula_one_hour_miss(self, tracker):
        """|4−3|/24 = 1/24 ≈ 0.04167"""
        tracker.add_intention("focus", 4.0)
        tracker.add_actual("focus", 3.0)
        drift, details = tracker.calculate_drift()
        assert abs(drift - (1.0 / 24.0)) < 1e-9
        assert abs(details[0]["drift"] - (1.0 / 24.0)) < 1e-9

    @pytest.mark.active
    def test_drift_non_negative(self, tracker):
        tracker.add_intention("a", 2.0)
        tracker.add_actual("a", 5.0)  # overshoot still |diff|
        drift, _ = tracker.calculate_drift()
        assert drift >= 0.0

    @pytest.mark.active
    def test_empty_day_zero_drift(self, tracker):
        drift, details = tracker.calculate_drift()
        assert drift == 0.0
        assert details == []


class TestStability:
    @pytest.mark.active
    def test_stability_increases_with_events(self, tracker):
        s0, _ = tracker.calculate_stability()
        tracker.record_stability_event("focus", 30)
        s1, details = tracker.calculate_stability()
        assert s1 >= s0
        assert len(details) == 1

    @pytest.mark.active
    def test_stability_bounded(self, tracker):
        for i in range(5):
            tracker.record_stability_event("focus", 120)
        stab, _ = tracker.calculate_stability()
        assert 0.0 <= stab <= 1.0


class TestSovereignty:
    @pytest.mark.active
    def test_score_in_unit_interval(self, tracker):
        tracker.add_intention("work", 6.0)
        tracker.add_actual("work", 5.0)
        tracker.record_stability_event("deep", 90)
        result = tracker.calculate_sovereignty_score()
        assert 0.0 <= result["sovereignty_score"] <= 1.0
        assert "interpretation" in result
        assert "date" in result

    @pytest.mark.active
    def test_formula_product_of_factors(self, tracker):
        tracker.add_intention("work", 4.0)
        tracker.add_actual("work", 4.0)
        tracker.record_stability_event("focus", 60)
        result = tracker.calculate_sovereignty_score()
        drift = result["drift"]
        stab = result["stability"]
        expected = (1.0 - drift) * stab
        assert abs(result["sovereignty_score"] - expected) < 1e-9

    @pytest.mark.active
    def test_high_drift_lowers_score(self, tracker):
        tracker.record_stability_event("focus", 60)
        # matched day
        tracker.add_intention("a", 4.0)
        tracker.add_actual("a", 4.0)
        good = tracker.calculate_sovereignty_score()["sovereignty_score"]
        # restart with bad match in fresh dir
        with tempfile.TemporaryDirectory() as d:
            t2 = MicroorcimTracker(data_dir=Path(d))
            t2.record_stability_event("focus", 60)
            t2.add_intention("a", 8.0)
            t2.add_actual("a", 1.0)
            bad = t2.calculate_sovereignty_score()["sovereignty_score"]
        assert bad < good

    @pytest.mark.active
    def test_close_day_persists(self, tracker, tmp_path):
        tracker.add_intention("x", 2.0)
        tracker.add_actual("x", 2.0)
        closed = tracker.close_day()
        assert isinstance(closed, dict)
        # history file should exist after close
        hist = list(tmp_path.glob("*"))
        assert len(hist) >= 1

    @pytest.mark.active
    def test_daily_cli_report_is_string(self, tracker):
        tracker.add_intention("x", 1.0)
        tracker.add_actual("x", 1.0)
        report = tracker.daily_cli_report()
        assert isinstance(report, str)
        assert len(report) > 0


# =============================================================================
# ROUND 3 — persistence reload, interpretation bands, report detail lines
# =============================================================================


class TestPersistenceReload:
    @pytest.mark.active
    def test_reloads_today_and_history_from_disk(self, tmp_path):
        t1 = MicroorcimTracker(data_dir=tmp_path)
        t1.add_intention("deep", 3.0, context="morning")
        t1.add_actual("deep", 2.5)
        t1.record_stability_event("focus", 45)
        closed = t1.close_day()
        assert "sovereignty_score" in closed

        t2 = MicroorcimTracker(data_dir=tmp_path)
        assert len(t2.history) >= 1
        # today file exists — intentions reloaded or fresh day structure present
        assert "intentions" in t2.today_data
        assert "actuals" in t2.today_data


class TestInterpretationBands:
    @pytest.mark.active
    def test_interpret_score_all_bands(self, tracker):
        assert "STRONG" in tracker._interpret_score(0.85)
        assert "MODERATE" in tracker._interpret_score(0.65)
        assert "TRANSITIONAL" in tracker._interpret_score(0.45)
        assert "RECOVERING" in tracker._interpret_score(0.25)
        assert "CRITICAL" in tracker._interpret_score(0.05)

    @pytest.mark.active
    def test_score_bar_width(self):
        bar = MicroorcimTracker._score_bar(0.5, width=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5
        assert len(bar) == 10


class TestReportDetails:
    @pytest.mark.active
    def test_cli_report_includes_drift_and_stability_lines(self, tracker):
        tracker.add_intention("code", 4.0)
        tracker.add_actual("code", 3.0)
        tracker.record_stability_event("deep_work", 60)
        report = tracker.daily_cli_report()
        assert "Drift" in report or "ρ_drift" in report
        assert "deep_work" in report or "Stability" in report
        assert "Sovereignty" in report

    @pytest.mark.active
    def test_unmatched_actual_ignored_in_drift(self, tracker):
        tracker.add_intention("planned", 2.0)
        tracker.add_actual("other", 5.0)  # no matching intention
        drift, details = tracker.calculate_drift()
        assert drift == 0.0
        assert details == []

    @pytest.mark.active
    def test_close_day_appends_history(self, tracker):
        tracker.add_intention("x", 1.0)
        tracker.add_actual("x", 1.0)
        n0 = len(tracker.history)
        tracker.close_day()
        assert len(tracker.history) == n0 + 1
