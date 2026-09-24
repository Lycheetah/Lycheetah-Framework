"""
Tests for harmonia_calculator.py — consonance, Barlow dissonance, Kuramoto sync.

Claim coverage:
  [ACTIVE] Perfect fifth (3:2) is highly consonant / low Barlow dissonance
  [ACTIVE] Interval naming near 702 cents → perfect_fifth
  [ACTIVE] Kuramoto order parameter rises under strong coupling
  [SCAFFOLD] Barlow-proxy is intentional approximation of continued-fraction C(r)
"""

import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from harmonia_calculator import HarmoniaCalculator, KuramotoSimulator, FrequencyPair


class TestFrequencyPair:
    @pytest.mark.active
    def test_normalized_ratio_within_octave(self):
        """normalized_ratio is brought into [0.5, 2.0] (may be < 1 when f2 < f1)."""
        pair = FrequencyPair(660, 440, "fifth")
        assert 0.5 <= pair.normalized_ratio <= 2.0

    @pytest.mark.active
    def test_octave_ratio_is_two(self):
        pair = FrequencyPair(440, 880, "octave")
        assert abs(pair.normalized_ratio - 2.0) < 1e-9


class TestConsonance:
    @pytest.mark.active
    def test_perfect_fifth_high_consonance(self):
        hc = HarmoniaCalculator()
        out = hc.calculate_consonance(440, 660, label="P5")
        assert out["interval_name"] == "perfect_fifth"
        assert out["consonance"] >= 0.9
        assert out["dissonance"] <= 0.1

    @pytest.mark.active
    def test_unison_perfect(self):
        hc = HarmoniaCalculator()
        out = hc.calculate_consonance(440, 440, label="unison")
        assert out["consonance"] >= 0.9
        assert out["dissonance"] <= 0.1

    @pytest.mark.active
    def test_result_has_required_keys(self):
        hc = HarmoniaCalculator()
        out = hc.calculate_consonance(300, 400)
        for key in ("ratio", "dissonance", "consonance", "interval_name", "interval_cents"):
            assert key in out

    @pytest.mark.active
    def test_consonance_bounded(self):
        hc = HarmoniaCalculator()
        out = hc.calculate_consonance(100, 173)  # awkward ratio
        assert 0.0 <= out["consonance"] <= 1.0
        assert out["dissonance"] >= 0.0

    @pytest.mark.active
    def test_interval_name_near_702_cents(self):
        hc = HarmoniaCalculator()
        assert hc.interval_name(702.0) == "perfect_fifth"

    @pytest.mark.active
    def test_barlow_dissonance_non_negative(self):
        hc = HarmoniaCalculator()
        for r in (1.0, 1.5, 1.25, np.sqrt(2)):
            assert hc.barlow_dissonance(r) >= 0.0

    @pytest.mark.scaffold
    def test_awkward_ratio_more_dissonant_than_fifth(self):
        """Directionality of Barlow proxy — not the exact continued-fraction form."""
        hc = HarmoniaCalculator()
        fifth = hc.barlow_dissonance(1.5)
        awkward = hc.barlow_dissonance(1.41421356237)
        assert awkward >= fifth


class TestKuramoto:
    @pytest.mark.active
    def test_strong_coupling_raises_order_parameter(self):
        freqs = [1.0, 1.02, 0.98, 1.05, 0.95]
        ks = KuramotoSimulator(frequencies=freqs, coupling_strength=3.0)
        before = float(ks.order_parameter)
        hist = ks.simulate(steps=250, dt=0.05)
        after = float(ks.order_parameter)
        assert len(hist) == 250
        assert after > before
        assert after > 0.7

    @pytest.mark.active
    def test_order_parameter_bounded(self):
        ks = KuramotoSimulator(frequencies=[1.0, 1.1, 0.9], coupling_strength=0.5)
        r = float(ks.order_parameter)
        assert 0.0 <= r <= 1.0 + 1e-9

    @pytest.mark.active
    def test_zero_coupling_does_not_force_sync(self):
        freqs = [1.0, 1.3, 0.7, 1.5, 0.5]
        ks = KuramotoSimulator(frequencies=freqs, coupling_strength=0.0)
        ks.simulate(steps=200, dt=0.05)
        # Without coupling, oscillators drift — order param should stay modest
        assert float(ks.order_parameter) < 0.95

    @pytest.mark.active
    def test_synchronization_strength_from_history(self):
        ks = KuramotoSimulator(frequencies=[1.0, 1.0, 1.0], coupling_strength=2.0)
        hist = ks.simulate(steps=120, dt=0.05)
        sync = ks.synchronization_strength(hist)
        assert isinstance(sync, dict)
        assert "final_order_parameter" in sync
        assert sync["synchronized"] is True or sync["final_order_parameter"] > 0.5

    @pytest.mark.active
    def test_step_advances_phases(self):
        ks = KuramotoSimulator(frequencies=[1.0, 1.1], coupling_strength=1.0)
        # capture via simulate length invariant
        hist = ks.simulate(steps=10, dt=0.1)
        assert len(hist) == 10


# =============================================================================
# ROUND 3 — FrequencyPair edges, quality bands, sync analysis edges
# =============================================================================

from harmonia_calculator import HarmoniaCalculator as _HC


class TestFrequencyPairEdges:
    @pytest.mark.active
    def test_non_positive_frequency_cents_zero(self):
        assert FrequencyPair(0.0, 440.0).interval_cents == 0
        assert FrequencyPair(440.0, -1.0).interval_cents == 0

    @pytest.mark.active
    def test_normalized_ratio_folds_wide_octaves(self):
        # while ratio > 2: /=2 — pure power-of-two multiples land on octave boundary 2.0
        for mult in (4, 8, 16):
            pair = FrequencyPair(440.0, 440.0 * mult)
            assert 0.5 <= pair.normalized_ratio <= 2.0
            assert abs(pair.normalized_ratio - 2.0) < 1e-9
        # non-power fold: ×3 → 1.5
        pair3 = FrequencyPair(440.0, 440.0 * 3)
        assert abs(pair3.normalized_ratio - 1.5) < 1e-9

    @pytest.mark.active
    def test_normalized_ratio_folds_sub_octave(self):
        pair = FrequencyPair(880.0, 110.0)  # ratio 0.125 → fold up into [0.5, 2]
        assert 0.5 <= pair.normalized_ratio <= 2.0


class TestConsonanceQualityBands:
    @pytest.mark.active
    def test_quality_labels_span_spectrum(self):
        hc = HarmoniaCalculator()
        # Drive quality via known consonance levels on the helper
        assert "PERFECT" in hc._consonance_quality(0.95)
        assert "CLEAR" in hc._consonance_quality(0.65)
        assert "MIXED" in hc._consonance_quality(0.45)
        assert "TENSE" in hc._consonance_quality(0.25)
        assert "HARSH" in hc._consonance_quality(0.05)

    @pytest.mark.active
    def test_octave_report_includes_quality(self):
        out = HarmoniaCalculator().calculate_consonance(261.63, 523.26, "octave")
        assert "consonance_quality" in out
        assert out["interval_name"] == "octave"
        assert out["consonance"] >= 0.8

    @pytest.mark.active
    def test_barlow_folds_ratio_outside_octave(self):
        hc = HarmoniaCalculator()
        # ratio > 2 and < 1 branches inside barlow_dissonance
        d_hi = hc.barlow_dissonance(3.0)
        d_lo = hc.barlow_dissonance(0.4)
        assert d_hi >= 0.0 and d_lo >= 0.0


class TestKuramotoAnalysisEdges:
    @pytest.mark.active
    def test_final_phases_keys(self):
        ks = KuramotoSimulator(frequencies=[1.0, 1.1], coupling_strength=1.0)
        ks.simulate(steps=5, dt=0.05)
        phases = ks.final_phases()
        assert set(phases.keys()) == {"osc_0", "osc_1"}

    @pytest.mark.active
    def test_empty_history_sync_report(self):
        ks = KuramotoSimulator(frequencies=[1.0], coupling_strength=0.5)
        assert ks.synchronization_strength([]) == {}

    @pytest.mark.active
    def test_weak_coupling_convergence_label(self):
        freqs = [1.0, 2.5, 0.3, 3.1, 0.7]
        ks = KuramotoSimulator(frequencies=freqs, coupling_strength=0.01)
        hist = ks.simulate(steps=80, dt=0.05)
        sync = ks.synchronization_strength(hist)
        assert sync["convergence_speed"] in ("fast", "slow", "incoherent")


class TestDescendingIntervalNaming:
    @pytest.mark.active
    def test_descending_fifth_named_perfect_fifth(self):
        """f2 < f1 must not mis-label a fifth as unison (abs-cents naming)."""
        hc = HarmoniaCalculator()
        asc = hc.calculate_consonance(440.0, 660.0, "asc")
        desc = hc.calculate_consonance(660.0, 440.0, "desc")
        assert asc["interval_name"] == "perfect_fifth"
        assert desc["interval_name"] == "perfect_fifth"
        assert desc["interval_cents"] < 0  # direction preserved
        assert asc["consonance"] == pytest.approx(desc["consonance"], abs=1e-9)
