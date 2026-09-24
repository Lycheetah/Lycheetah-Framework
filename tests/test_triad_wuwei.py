"""
Tests for triad_wuwei.py — Wuwei grain-aligned integrity-debt (T-4).

Claim coverage:
  [SCAFFOLD] gamma / h / debt accumulation (spec T-4; mu empirical)
  [ACTIVE]   endpoint identities and §V equal-magnitude cost divergence
"""

import math
import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from triad_wuwei import (
    grain_alignment,
    grain_cost_modulator_exp,
    grain_cost_modulator_bounded,
    restoration_from_potential,
    WuweiTriad,
    WuweiStep,
)


def _approx(a, b, tol=1e-6):
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


class TestGrainAlignment:
    @pytest.mark.active
    def test_aligned_is_plus_one(self):
        assert _approx(grain_alignment(np.array([2.0, 0.0]), np.array([1.0, 0.0])), 1.0)

    @pytest.mark.active
    def test_anti_aligned_is_minus_one(self):
        assert _approx(grain_alignment(np.array([-3.0, 0.0]), np.array([1.0, 0.0])), -1.0)

    @pytest.mark.active
    def test_orthogonal_is_zero(self):
        assert _approx(grain_alignment(np.array([0.0, 4.0]), np.array([1.0, 0.0])), 0.0)

    @pytest.mark.active
    def test_zero_intervention_convention(self):
        assert grain_alignment(np.zeros(2), np.array([1.0, 0.0])) == 0.0

    @pytest.mark.active
    def test_zero_restoration_convention(self):
        assert grain_alignment(np.array([1.0, 0.0]), np.zeros(2)) == 0.0

    @pytest.mark.active
    def test_gamma_bounded(self):
        g = grain_alignment(np.array([1.0, 1.0]), np.array([1.0, -0.5]))
        assert -1.0 <= g <= 1.0


class TestModulators:
    @pytest.mark.active
    def test_exp_at_zero_is_one(self):
        assert _approx(grain_cost_modulator_exp(0.0, mu=1.0), 1.0)

    @pytest.mark.active
    def test_exp_aligned_cheaper_than_forced(self):
        assert grain_cost_modulator_exp(+1.0, mu=2.0) < 1.0
        assert grain_cost_modulator_exp(-1.0, mu=2.0) > 1.0

    @pytest.mark.active
    def test_bounded_endpoints_p2(self):
        assert _approx(grain_cost_modulator_bounded(-1.0, p=2.0), 2.0)
        assert _approx(grain_cost_modulator_bounded(0.0, p=2.0), 1.5)
        assert _approx(grain_cost_modulator_bounded(+1.0, p=2.0), 0.0)


class TestSectionVProposition4:
    """T-4 §V: equal-magnitude corrections diverge under Wuwei, not under standard."""

    @pytest.mark.scaffold
    def test_equal_magnitude_cost_divergence(self):
        state = np.array([1.0])
        R = np.array([-1.0])
        aligned = WuweiTriad(mu=1.0, k_cost=1.0).step(state, np.array([-0.3]), restoration=R)
        forced = WuweiTriad(mu=1.0, k_cost=1.0).step(state, np.array([+0.3]), restoration=R)
        assert _approx(aligned.intervention_norm, forced.intervention_norm)
        assert _approx(aligned.standard_debt_delta, forced.standard_debt_delta)
        assert _approx(aligned.gamma, +1.0)
        assert _approx(forced.gamma, -1.0)
        assert aligned.wuwei_debt_delta < aligned.standard_debt_delta
        assert forced.wuwei_debt_delta > forced.standard_debt_delta
        ratio = forced.wuwei_debt_delta / aligned.wuwei_debt_delta
        assert _approx(ratio, math.exp(2.0), tol=1e-3)


class TestWuweiBoundaries:
    @pytest.mark.active
    def test_zero_mu_recovers_standard(self):
        triad = WuweiTriad(mu=0.0, k_cost=1.0)
        state = np.array([1.0])
        R = np.array([-1.0])
        triad.step(state, np.array([-0.5]), restoration=R)
        triad.step(state, np.array([+0.5]), restoration=R)
        rep = triad.report()
        assert _approx(rep.standard_debt_total, rep.wuwei_debt_total)
        assert _approx(rep.divergence(), 0.0)

    @pytest.mark.active
    def test_orthogonal_no_modulation(self):
        triad = WuweiTriad(mu=2.0, k_cost=1.0)
        s = triad.step(np.array([1.0, 0.0]), np.array([0.0, 0.5]), restoration=np.array([-1.0, 0.0]))
        assert _approx(s.gamma, 0.0)
        assert _approx(s.h, 1.0)
        assert _approx(s.wuwei_debt_delta, s.standard_debt_delta)

    @pytest.mark.active
    def test_attractor_state_convention(self):
        triad = WuweiTriad(mu=1.0)
        s = triad.step(np.array([0.0]), np.array([0.1]), restoration=np.array([0.0]))
        assert s.gamma == 0.0
        assert _approx(s.h, 1.0)

    @pytest.mark.active
    def test_restoration_fn_from_potential(self):
        # U(x)=0.5 x^2 → grad=x → R=-x
        R = restoration_from_potential(lambda x: x)
        assert np.allclose(R(np.array([2.0])), np.array([-2.0]))

    @pytest.mark.active
    def test_step_requires_restoration_source(self):
        triad = WuweiTriad()  # no restoration_fn
        with pytest.raises(ValueError):
            triad.step(np.array([1.0]), np.array([0.1]))

    @pytest.mark.active
    def test_rejects_negative_mu(self):
        with pytest.raises(ValueError):
            WuweiTriad(mu=-0.1)

    @pytest.mark.active
    def test_coherent_step_flag(self):
        triad = WuweiTriad(mu=1.0, theta_wuwei=0.3)
        s = triad.step(np.array([1.0]), np.array([-0.3]), restoration=np.array([-1.0]))
        assert isinstance(s, WuweiStep)
        assert s.is_wuwei_coherent() is True

    @pytest.mark.scaffold
    def test_trajectory_coherence_positive_gamma(self):
        def grad_U(x: np.ndarray) -> np.ndarray:
            return x
        triad = WuweiTriad(restoration_fn=restoration_from_potential(grad_U), mu=1.0)
        state = np.array([1.0])
        for _ in range(5):
            # grain-aligned: push toward origin
            triad.step(state, intervention=np.array([-0.1]))
            state = state + np.array([-0.1])
        rep = triad.report()
        assert rep.average_gamma() > 0.0
        assert rep.is_trajectory_coherent(max_debt_growth_rate=1.0) is True
        assert "Wuwei" in rep.summary()

    @pytest.mark.active
    def test_bounded_modulator_in_triad(self):
        triad = WuweiTriad(
            mu=1.0,
            modulator=lambda g: grain_cost_modulator_bounded(g, p=2.0),
        )
        s = triad.step(np.array([1.0]), np.array([-0.3]), restoration=np.array([-1.0]))
        # gamma=+1 → bounded h=0
        assert _approx(s.h, 0.0)
        assert _approx(s.wuwei_debt_delta, 0.0)
