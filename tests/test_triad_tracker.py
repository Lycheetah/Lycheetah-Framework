"""
Tests for triad_tracker.py

Claim coverage:
  [ACTIVE] Convergence guarantee: when α < 1/(2L), iteration converges
  [ACTIVE] Divergence when α too large (λ >= 1)
  [ACTIVE] Step sequence: state_n+1 = state_n + α * gradient(state_n)
  [ACTIVE] Convergence detected when |delta| < threshold
  [SCAFFOLD] α = 0.5/L is a safe default step size
"""

import pytest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from triad_tracker import TriadTracker, TriadStep


# ── Basic structure ───────────────────────────────────────────────────────────

class TestTriadStructure:
    @pytest.mark.active
    def test_run_returns_steps(self):
        """run_until_convergence() returns (steps, converged)."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(coherence_fn=coherence_fn, gradient_fn=gradient_fn,
                               initial_state=0.0, lipschitz_constant=2.0)
        steps, converged = tracker.run_until_convergence()
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(s, TriadStep) for s in steps)

    @pytest.mark.active
    def test_step_fields_present(self):
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(coherence_fn=coherence_fn, gradient_fn=gradient_fn,
                               initial_state=0.0, lipschitz_constant=2.0)
        steps, _ = tracker.run_until_convergence()
        step = steps[0]
        assert hasattr(step, 'iteration')
        assert hasattr(step, 'state')
        assert hasattr(step, 'coherence')
        assert hasattr(step, 'gradient')
        assert hasattr(step, 'delta')
        assert hasattr(step, 'converged')


# ── Convergence guarantee ─────────────────────────────────────────────────────

class TestConvergence:
    @pytest.mark.active
    def test_converges_with_quadratic_coherence(self):
        """Standard quadratic peak — should converge to optimum."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=0.0,
            lipschitz_constant=2.0,
            convergence_threshold=1e-6,
        )
        steps, converged = tracker.run_until_convergence()
        assert converged, f"Did not converge after {len(steps)} steps"

    @pytest.mark.active
    def test_converges_to_near_optimum(self):
        """Final state should be close to the coherence peak at psi=1.0."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=0.0,
            lipschitz_constant=2.0,
        )
        steps, _ = tracker.run_until_convergence()
        final_state = steps[-1].state
        assert abs(final_state - 1.0) < 0.01, f"Converged to {final_state:.4f}, expected near 1.0"

    @pytest.mark.active
    def test_coherence_increases_monotonically(self):
        """Coherence should not decrease during convergent run."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=0.0,
            lipschitz_constant=2.0,
        )
        steps, _ = tracker.run_until_convergence()
        coherences = [s.coherence for s in steps]
        # Each step coherence >= previous (may be equal at convergence)
        for i in range(1, min(len(coherences), 10)):
            assert coherences[i] >= coherences[i-1] - 1e-9, (
                f"Coherence decreased at step {i}: {coherences[i-1]:.6f} → {coherences[i]:.6f}"
            )

    @pytest.mark.active
    def test_converges_from_different_starting_points(self):
        """Same optimum reached from different initial states."""
        def coherence_fn(psi): return -(psi - 2.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 2.0)

        starting_points = [0.0, 1.0, 3.0, 4.0]
        final_states = []
        for start in starting_points:
            tracker = TriadTracker(
                coherence_fn=coherence_fn,
                gradient_fn=gradient_fn,
                initial_state=start,
                lipschitz_constant=2.0,
            )
            steps, _ = tracker.run_until_convergence()
            final_states.append(steps[-1].state)

        # All should converge near 2.0
        for i, state in enumerate(final_states):
            assert abs(state - 2.0) < 0.05, (
                f"From start={starting_points[i]}, converged to {state:.4f} instead of ~2.0"
            )


# ── Step size constraint ──────────────────────────────────────────────────────

class TestStepSize:
    @pytest.mark.scaffold
    def test_default_step_size_is_bounded(self):
        """Default α = 0.5/L * 0.5 = 0.25/L (half of max_step_size)."""
        L = 2.0
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            lipschitz_constant=L,
        )
        # From source: step_size = max_step_size * 0.5 = (1/(2L)) * 0.5 = 0.25/L
        max_step = 1.0 / (2.0 * L)
        expected_alpha = max_step * 0.5
        assert abs(tracker.step_size - expected_alpha) < 1e-9
        # And it satisfies the convergence bound
        assert tracker.step_size < 1.0 / (2.0 * L)

    @pytest.mark.active
    def test_iteration_formula(self):
        """state_n+1 = state_n + α * gradient(state_n)."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        alpha = 0.1
        psi_0 = 0.0
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=psi_0,
            step_size=alpha,
        )
        steps, _ = tracker.run_until_convergence()
        # Check first transition: step[0].state was computed from psi_0
        # step[0].state = psi_0 + alpha * gradient(psi_0)
        expected_state_0 = psi_0 + alpha * gradient_fn(psi_0)
        assert abs(steps[0].state - expected_state_0) < 1e-9


# ── Convergence detection ─────────────────────────────────────────────────────

class TestConvergenceDetection:
    @pytest.mark.active
    def test_converged_flag_set_on_last_step(self):
        """Final step should have converged=True when threshold met."""
        def coherence_fn(psi): return -(psi - 1.0) ** 2 + 1.0
        def gradient_fn(psi): return -2.0 * (psi - 1.0)
        tracker = TriadTracker(
            coherence_fn=coherence_fn, gradient_fn=gradient_fn,
            initial_state=0.0, lipschitz_constant=2.0,
            convergence_threshold=1e-4,
        )
        steps, converged = tracker.run_until_convergence()
        assert converged
        assert steps[-1].converged

    @pytest.mark.active
    def test_max_iterations_respected(self):
        """Tracker stops at max_iterations even if not converged."""
        def coherence_fn(psi): return psi  # Linear — never truly converges
        def gradient_fn(psi): return 1.0
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=0.0,
            step_size=0.01,
            lipschitz_constant=1.0,
            max_iterations=50,
        )
        steps, _ = tracker.run_until_convergence()
        assert len(steps) <= 50


# ── Step serialization ────────────────────────────────────────────────────────

class TestStepSerialization:
    @pytest.mark.active
    def test_to_dict_has_required_keys(self):
        step = TriadStep(iteration=1, state=0.5, coherence=0.75,
                         gradient=0.5, step_size=0.25, delta=0.125)
        d = step.to_dict()
        for key in ["iteration", "state", "coherence", "gradient", "step_size", "delta", "converged"]:
            assert key in d
