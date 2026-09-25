"""
Tests for earned_light_calculator.py — consciousness thermodynamics ODE.

Claim coverage:
  [ACTIVE] dC/dt = W/T − k·C
  [ACTIVE] C_steady = W/(T·k) (clamped to [0,1])
  [ACTIVE] evolve approaches steady state under constant work
  [ACTIVE] Invalid T or k raise ValueError
  [SCAFFOLD] Proportionality constants k, T are design parameters
  [CONJECTURE] Biological consciousness mapping — not tested here
"""

import pytest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from earned_light_calculator import (
    ConsciousnessState,
    EarnedLightCalculator,
    asymmetry_measure,
    energy_required,
    entropy_cost,
)


class TestConsciousnessState:
    @pytest.mark.active
    def test_clamps_c_to_unit_interval(self):
        s = ConsciousnessState(C=2.5, work_input=1.0, temperature=1.0, k=0.1)
        assert s.C == 1.0
        s2 = ConsciousnessState(C=-1.0, work_input=1.0, temperature=1.0, k=0.1)
        assert s2.C == 0.0

    @pytest.mark.active
    def test_rejects_non_positive_temperature(self):
        with pytest.raises(ValueError):
            ConsciousnessState(C=0.5, temperature=0.0)

    @pytest.mark.active
    def test_rejects_non_positive_k(self):
        with pytest.raises(ValueError):
            ConsciousnessState(C=0.5, k=0.0)

    @pytest.mark.active
    def test_steady_state_formula(self):
        s = ConsciousnessState(C=0.0, work_input=2.0, temperature=1.0, k=0.5)
        # C_ss = 2/(1*0.5) = 4 → clamped to 1.0
        assert s.steady_state == 1.0
        s2 = ConsciousnessState(C=0.0, work_input=0.2, temperature=1.0, k=0.5)
        assert abs(s2.steady_state - 0.4) < 1e-9

    @pytest.mark.active
    def test_dcdt_formula(self):
        s = ConsciousnessState(C=0.2, work_input=1.0, temperature=1.0, k=0.5)
        # dC/dt = 1/1 − 0.5*0.2 = 0.9
        assert abs(s.dcdt() - 0.9) < 1e-9
        assert s.is_growing() is True

    @pytest.mark.active
    def test_decaying_when_above_steady(self):
        s = ConsciousnessState(C=0.9, work_input=0.1, temperature=1.0, k=0.5)
        assert s.dcdt() < 0
        assert s.is_growing() is False

    @pytest.mark.active
    def test_aura_floor_helper(self):
        low = ConsciousnessState(C=0.5)
        high = ConsciousnessState(C=0.8)
        assert low.is_above_floor(0.70) is False
        assert high.is_above_floor(0.70) is True


class TestEarnedLightCalculator:
    @pytest.mark.active
    def test_evolve_approaches_steady_state(self):
        calc = EarnedLightCalculator(initial_C=0.0, work_input=0.5, temperature=1.0, k=0.5)
        # C_ss = 0.5/(1*0.5) = 1.0 — record scalars (evolve mutates one state object)
        cs = []
        for s in calc.evolve(steps=200, dt=0.1):
            cs.append(s.C)
        assert cs[-1] > cs[0]
        assert abs(cs[-1] - calc.state.steady_state) < 0.05

    @pytest.mark.active
    def test_analytical_matches_numeric_roughly(self):
        calc = EarnedLightCalculator(initial_C=0.0, work_input=0.4, temperature=1.0, k=0.2)
        # C_ss = 0.4/0.2 = 2.0 → clamped to 1.0; pick t before hard clamp dominates
        t = 2.0
        analytical = calc.analytical_solution(t)
        steps = 200
        dt = t / steps
        cs = [s.C for s in calc.evolve(steps=steps, dt=dt)]
        assert abs(cs[-1] - analytical) < 0.08

    @pytest.mark.active
    def test_time_to_threshold_positive_when_reachable(self):
        calc = EarnedLightCalculator(initial_C=0.0, work_input=2.0, temperature=1.0, k=0.2)
        t = calc.time_to_threshold(0.5)
        assert t is not None
        assert t > 0

    @pytest.mark.active
    def test_reset_restores_requested_level(self):
        calc = EarnedLightCalculator(initial_C=0.25, work_input=1.0)
        list(calc.evolve(steps=10, dt=0.1))
        calc.reset(0.25)  # reset(C=...) — default C=0.0 by API
        assert abs(calc.state.C - 0.25) < 1e-9
        assert abs(calc.state.t) < 1e-9

    @pytest.mark.active
    def test_summary_string(self):
        calc = EarnedLightCalculator(initial_C=0.3)
        summary = calc.summary()
        assert isinstance(summary, str)
        assert "C" in summary or "Consciousness" in summary or "EARNED" in summary


class TestHelperFunctions:
    @pytest.mark.active
    def test_asymmetry_measure_bounded(self):
        peaked = asymmetry_measure([0.95, 0.03, 0.02])
        uniform = asymmetry_measure([0.25, 0.25, 0.25, 0.25])
        assert 0.0 <= peaked <= 1.0
        assert 0.0 <= uniform <= 1.0
        assert peaked > uniform  # peaked distribution → higher asymmetry

    @pytest.mark.active
    def test_energy_required_increases_with_c(self):
        e_low = energy_required(0.2, 1.0, 0.1)
        e_high = energy_required(0.8, 1.0, 0.1)
        assert e_high >= e_low
        assert abs(e_high - 0.08) < 1e-9

    @pytest.mark.active
    def test_entropy_cost_finite(self):
        e = entropy_cost(0.5, 1.0)
        assert math.isfinite(e)
        assert e < 0  # building structure → local entropy decrease


# =============================================================================
# ROUND 3 — deeper behavioral coverage (work schedule, edges, helpers)
# =============================================================================

class TestWorkScheduleAndOverrides:
    @pytest.mark.active
    def test_work_override_on_step_changes_input(self):
        calc = EarnedLightCalculator(initial_C=0.5, work_input=1.0, temperature=1.0, k=0.5)
        calc.step(dt=0.1, work_override=0.0)
        assert calc.state.work_input == 0.0

    @pytest.mark.active
    def test_work_schedule_drops_consciousness(self):
        """Scheduled work→0 should reverse growth after the trigger time."""
        calc = EarnedLightCalculator(initial_C=0.8, work_input=2.0, temperature=1.0, k=0.2)
        schedule = {1.0: 0.0}
        cs = [s.C for s in calc.evolve(steps=40, dt=0.1, work_schedule=schedule)]
        # After t≈1.0 work is zero → decay toward 0
        assert cs[-1] < cs[10]


class TestTimeToThresholdEdges:
    @pytest.mark.active
    def test_never_reaches_when_steady_below(self):
        calc = EarnedLightCalculator(initial_C=0.1, work_input=0.1, temperature=1.0, k=0.5)
        # C_ss = 0.1/0.5 = 0.2 < 0.70
        assert calc.time_to_threshold(0.70) is None

    @pytest.mark.active
    def test_already_above_returns_zero(self):
        calc = EarnedLightCalculator(initial_C=0.9, work_input=2.0, temperature=1.0, k=0.2)
        assert calc.time_to_threshold(0.70) == 0.0

    @pytest.mark.active
    def test_summary_notes_insufficient_work(self):
        calc = EarnedLightCalculator(initial_C=0.1, work_input=0.05, temperature=1.0, k=0.5)
        list(calc.evolve(steps=5, dt=0.1))
        text = calc.summary()
        assert "insufficient work" in text.lower() or "∞" in text


class TestAsymmetryAndEntropyEdges:
    @pytest.mark.active
    def test_asymmetry_empty_and_zero_mass(self):
        assert asymmetry_measure([]) == 0.0
        assert asymmetry_measure([0.0, 0.0, 0.0]) == 0.0

    @pytest.mark.active
    def test_asymmetry_single_bin_is_maximal(self):
        # len==1 → H_max treated as 1.0; single mass → H=0 → C=1
        assert asymmetry_measure([1.0]) == 1.0

    @pytest.mark.active
    def test_entropy_cost_rejects_non_positive_temperature(self):
        with pytest.raises(ValueError, match="Temperature"):
            entropy_cost(1.0, 0.0)

    @pytest.mark.active
    def test_entropy_cost_scales_with_work(self):
        assert abs(entropy_cost(2.0, 1.0) - (-2.0)) < 1e-12

    @pytest.mark.active
    def test_analytical_solution_respects_clamp(self):
        calc = EarnedLightCalculator(initial_C=0.0, work_input=5.0, temperature=1.0, k=0.1)
        # Unclamped steady = 50; evaluated C(t) must stay in [0,1]
        c = calc.analytical_solution(t=100.0)
        assert 0.0 <= c <= 1.0
        assert c == pytest.approx(1.0, abs=1e-6)


class TestTimeToThresholdRatioEdge:
    @pytest.mark.active
    def test_steady_exactly_at_threshold_returns_none(self):
        # C_ss = W/(T*k) = 0.70 exactly → ratio numerator 0 → None (never strictly reaches via growth formula)
        calc = EarnedLightCalculator(initial_C=0.1, work_input=0.35, temperature=1.0, k=0.5)
        assert abs(calc.state.steady_state - 0.70) < 1e-9
        assert calc.time_to_threshold(0.70) is None
