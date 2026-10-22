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


class TestAdmission:
    """Invalid inputs are refused before they reach the debt ledger.

    Unchecked, a NaN restoration clipped to gamma = +1 and recorded a forcing
    correction as fully grain-aligned and coherent.
    """

    @pytest.mark.active
    @pytest.mark.parametrize("field", ["intervention", "restoration"])
    @pytest.mark.parametrize("bad", [math.nan, math.inf])
    def test_non_finite_vectors_are_refused(self, field, bad):
        vectors = {"intervention": np.array([0.3]), "restoration": np.array([-1.0])}
        vectors[field] = np.array([bad])
        with pytest.raises(ValueError):
            grain_alignment(vectors["intervention"], vectors["restoration"])

    @pytest.mark.active
    @pytest.mark.parametrize("intervention, restoration", [([0.3], [math.nan]), ([math.inf], [-1.0])])
    def test_refused_step_leaves_the_ledger_untouched(self, intervention, restoration):
        triad = WuweiTriad(mu=1.0)
        triad.step(np.array([1.0]), np.array([-0.3]), restoration=np.array([-1.0]))
        before = (triad.standard_debt, triad.wuwei_debt, len(triad.history))
        with pytest.raises(ValueError):
            triad.step(np.array([1.0]), np.array(intervention), restoration=np.array(restoration))
        assert (triad.standard_debt, triad.wuwei_debt, len(triad.history)) == before

    @pytest.mark.active
    def test_intervention_must_match_state_dimension(self):
        with pytest.raises(ValueError, match="dimension"):
            WuweiTriad().step(np.zeros(3), np.array([0.1]), restoration=np.array([1.0]))

    @pytest.mark.active
    @pytest.mark.parametrize("kwargs", [{"mu": math.nan}, {"mu": math.inf}, {"k_cost": math.nan},
                                        {"theta_wuwei": math.nan}, {"theta_wuwei": 5.0}])
    def test_constructor_refuses_invalid_parameters(self, kwargs):
        with pytest.raises(ValueError):
            WuweiTriad(**kwargs)

    @pytest.mark.active
    @pytest.mark.parametrize("gamma, p", [(-2.0, 2.5), (0.0, math.nan), (math.nan, 2.0)])
    def test_bounded_modulator_refuses_outside_its_domain(self, gamma, p):
        with pytest.raises(ValueError):
            grain_cost_modulator_bounded(gamma, p=p)

    @pytest.mark.active
    @pytest.mark.parametrize("gamma, mu", [(0.0, math.nan), (math.nan, 1.0), (-1.0, 1000.0)])
    def test_exp_modulator_refuses_invalid_or_overflowing_inputs(self, gamma, mu):
        with pytest.raises(ValueError):
            grain_cost_modulator_exp(gamma, mu=mu)

    @pytest.mark.active
    @pytest.mark.parametrize("h", [-1.0, math.nan])
    def test_modulator_output_must_be_a_non_negative_cost(self, h):
        triad = WuweiTriad(modulator=lambda g: h)
        with pytest.raises(ValueError):
            triad.step(np.array([1.0]), np.array([-0.3]), restoration=np.array([-1.0]))
        assert triad.wuwei_debt == 0.0 and triad.history == []

    @pytest.mark.active
    def test_step_coherence_uses_the_triads_threshold(self):
        triad = WuweiTriad(theta_wuwei=0.9)
        # gamma = cos 45° ≈ 0.707: coherent at the old default 0.3, not at this triad's 0.9
        s = triad.step(np.array([1.0, 1.0]), np.array([-1.0, 0.0]), restoration=np.array([-1.0, -1.0]))
        assert s.is_wuwei_coherent() is False
        assert s.is_wuwei_coherent(0.3) is True

    @pytest.mark.active
    @pytest.mark.parametrize("rate", [math.nan, -1.0])
    def test_trajectory_rate_must_be_a_finite_non_negative_bound(self, rate):
        triad = WuweiTriad(restoration_fn=restoration_from_potential(lambda x: x))
        triad.step(np.array([1.0]), np.array([-0.1]))
        with pytest.raises(ValueError):
            triad.report().is_trajectory_coherent(max_debt_growth_rate=rate)
