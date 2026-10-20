"""Counterexamples for numerical admission and truthful iteration receipts."""

import math

import pytest

from lycheetah.core.tri_axial_checker import TriAxialChecker
from lycheetah.core.triad_tracker import TriadTracker


def tracker(**kwargs):
    return TriadTracker(lambda x: -(x - 1.0) ** 2, lambda x: -2 * (x - 1.0), **kwargs)


def test_tiny_step_does_not_certify_stationarity():
    t = TriadTracker(lambda x: x, lambda x: 1.0, step_size=1e-12, max_iterations=3)
    steps, converged = t.run_until_convergence()
    assert not converged
    assert len(steps) == 3


def test_step_receipt_pairs_new_state_with_its_coherence():
    t = tracker(initial_state=0.0, step_size=0.1)
    step = t.single_step()
    assert step.coherence == pytest.approx(-(step.state - 1.0) ** 2)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_invalid_gradient_does_not_commit_state_or_history(bad):
    t = TriadTracker(lambda x: x, lambda x: bad, initial_state=0.5)
    with pytest.raises(ValueError, match="finite"):
        t.single_step()
    assert t.state == 0.5
    assert t.history == []
    assert t.iteration_count == 0


@pytest.mark.parametrize("setting", [
    {"step_size": 0.0}, {"step_size": -0.1}, {"step_size": math.nan},
    {"lipschitz_constant": 0.0}, {"convergence_threshold": math.nan},
    {"max_iterations": 0}, {"max_iterations": True},
])
def test_invalid_iteration_configuration_is_rejected(setting):
    with pytest.raises(ValueError):
        tracker(**setting)


@pytest.mark.parametrize("field", ["h_output", "drift", "value_added", "friction"])
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_metric_inputs_are_rejected(field, bad):
    with pytest.raises(ValueError, match="finite"):
        TriAxialChecker().check(**{field: bad})


def test_incomplete_vector_cannot_be_replaced_by_passing_fallback():
    checker = TriAxialChecker(constitution_vector=[1.0, 0.0])
    with pytest.raises(ValueError, match="dimension"):
        checker.check(identity_vector=[1.0])


@pytest.mark.parametrize("bad", [-1, 0.5, True])
def test_invalid_violation_count_cannot_inflate_purpose_score(bad):
    with pytest.raises(ValueError, match="violation_count"):
        TriAxialChecker().compute_pai(violation_count=bad)


def test_negative_friction_cannot_turn_negative_value_into_a_pass():
    with pytest.raises(ValueError, match="friction"):
        TriAxialChecker().compute_vtr(value_added=-10.0, friction=-1.0)


def test_cosine_is_scale_invariant_for_large_finite_vectors():
    checker = TriAxialChecker(constitution_vector=[1e308, 1e308])
    assert checker.compute_pai(identity_vector=[1e308, 1e308]).score == pytest.approx(1.0)


@pytest.mark.parametrize("vector", [[], [math.nan, 1.0], [math.inf, 1.0], [[1.0], [1.0]]])
def test_invalid_vectors_are_rejected(vector):
    checker = TriAxialChecker(constitution_vector=[1.0, 0.0])
    with pytest.raises(ValueError):
        checker.compute_pai(identity_vector=vector)


def test_configured_vector_mode_requires_an_identity_vector():
    with pytest.raises(ValueError, match="both"):
        TriAxialChecker(constitution_vector=[1.0, 0.0]).compute_pai()


def test_valid_quadratic_and_default_scores_still_work():
    t = tracker(initial_state=0.0)
    steps, converged = t.run_until_convergence()
    assert converged and abs(steps[-1].state - 1.0) < 1e-4
    assert TriAxialChecker().check().passes
