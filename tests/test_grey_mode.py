"""
Tests for grey_mode.py — AURA Isolation and Recovery Protocol

Claim coverage:
  [ACTIVE]   Two-parameter trigger: BOTH delta_s AND delta_phi must exceed thresholds
  [ACTIVE]   Single-parameter breach → WATCHING, not GREY
  [ACTIVE]   Two consecutive dual-parameter breaches → GREY activated
  [ACTIVE]   Alert count resets when both parameters are within bounds
  [ACTIVE]   WATCHING clears back to HEALTHY when single parameter resolves
  [ACTIVE]   activate() produces IsolationRecord with correct fields
  [ACTIVE]   recovery_cycle() returns a state closer to anchor than input
  [ACTIVE]   compute_psi_r() returns drift ∈ [0, 1]
  [ACTIVE]   reentry_test() returns True when psi_r < r_c_new
  [ACTIVE]   reentry_test() returns False when psi_r >= r_c_new
  [ACTIVE]   compute_r_merge() decreases with increasing isolation time
  [ACTIVE]   compute_r_merge() uses sigma_local/sigma_global ratio
  [ACTIVE]   run() marks status HEALTHY after successful recovery
  [ACTIVE]   run() marks status GREY after max_cycles exhausted without convergence
  [ACTIVE]   run() audit trail records each cycle and final decision
  [SCAFFOLD] Permanent isolation AURA PRIME escalation logged in audit trail
"""

import pytest
import time
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from grey_mode import (
    GreyModeMonitor, GreyModeStatus, NetworkStats,
    IsolationRecord, RecoveryResult, build_monitor,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────

DIM = 8

@pytest.fixture
def anchor():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(DIM)
    return v / np.linalg.norm(v)

@pytest.fixture
def coherence(anchor):
    rng = np.random.default_rng(1)
    v = rng.standard_normal(DIM)
    return v / np.linalg.norm(v)

@pytest.fixture
def monitor(anchor, coherence):
    return build_monitor(
        kappa=1.5,
        sigma_hat=0.1,     # s_threshold = 0.15
        theta_x=0.3,
        anchor=anchor,
        coherence=coherence,
        alert_threshold=2,
    )

@pytest.fixture
def net_stats():
    return NetworkStats(sigma_local=0.05, sigma_global=0.10, node_count=5)

@pytest.fixture
def drifted_state(anchor):
    """A state vector noticeably away from anchor."""
    rng = np.random.default_rng(99)
    noise = rng.standard_normal(DIM)
    noise /= np.linalg.norm(noise)
    state = 0.3 * anchor + 0.7 * noise
    return state / np.linalg.norm(state)


# ─── Phase 1: Detection — trigger logic ──────────────────────────────────────

class TestTriggerLogic:

    @pytest.mark.active
    def test_both_thresholds_exceeded_fires_alert(self, monitor):
        """Both ΔS and Δφ above threshold → alert fires, count increments."""
        status = monitor.check(delta_s=0.20, delta_phi=0.40)  # both over threshold
        assert monitor.alert_count == 1
        assert monitor.trigger_log[-1].alert_fired is True

    @pytest.mark.active
    def test_only_delta_s_exceeded_no_alert(self, monitor):
        """ΔS above threshold but Δφ within bounds → WATCHING, no alert."""
        status = monitor.check(delta_s=0.20, delta_phi=0.10)  # only s
        assert monitor.alert_count == 0
        assert status == GreyModeStatus.WATCHING
        assert monitor.trigger_log[-1].alert_fired is False

    @pytest.mark.active
    def test_only_delta_phi_exceeded_no_alert(self, monitor):
        """Δφ above threshold but ΔS within bounds → WATCHING, no alert."""
        status = monitor.check(delta_s=0.05, delta_phi=0.40)  # only phi
        assert monitor.alert_count == 0
        assert status == GreyModeStatus.WATCHING
        assert monitor.trigger_log[-1].alert_fired is False

    @pytest.mark.active
    def test_two_consecutive_dual_breaches_activate_grey(self, monitor):
        """Two consecutive dual-parameter breaches → GREY (alert_threshold=2)."""
        monitor.check(delta_s=0.20, delta_phi=0.40)
        assert monitor.status == GreyModeStatus.HEALTHY  # not yet

        monitor.check(delta_s=0.20, delta_phi=0.40)
        assert monitor.status == GreyModeStatus.GREY      # activated

    @pytest.mark.active
    def test_alert_count_resets_on_clean_check(self, monitor):
        """One alert fires, then clean check → count resets to 0."""
        monitor.check(delta_s=0.20, delta_phi=0.40)  # count = 1
        assert monitor.alert_count == 1

        monitor.check(delta_s=0.05, delta_phi=0.05)  # clean
        assert monitor.alert_count == 0

    @pytest.mark.active
    def test_watching_clears_to_healthy_on_clean_check(self, monitor):
        """Single parameter breach puts into WATCHING; clean check → HEALTHY."""
        monitor.check(delta_s=0.20, delta_phi=0.10)  # only s breached
        assert monitor.status == GreyModeStatus.WATCHING

        monitor.check(delta_s=0.05, delta_phi=0.05)  # clean
        assert monitor.status == GreyModeStatus.HEALTHY

    @pytest.mark.active
    def test_both_within_bounds_status_healthy(self, monitor):
        """Both parameters within bounds → HEALTHY, no alert."""
        status = monitor.check(delta_s=0.05, delta_phi=0.10)
        assert status == GreyModeStatus.HEALTHY
        assert monitor.alert_count == 0
        assert monitor.trigger_log[-1].alert_fired is False


# ─── Phase 2: Quarantine — activate() ────────────────────────────────────────

class TestActivate:

    @pytest.mark.active
    def test_activate_returns_isolation_record(self, monitor, drifted_state):
        """activate() returns a populated IsolationRecord."""
        monitor.check(delta_s=0.20, delta_phi=0.40)
        monitor.check(delta_s=0.20, delta_phi=0.40)  # trigger

        record = monitor.activate("node-1", drifted_state)
        assert isinstance(record, IsolationRecord)
        assert record.agent_id == "node-1"
        assert record.alert_count == 2

    @pytest.mark.active
    def test_activate_stores_entry_state(self, monitor, drifted_state):
        """activate() stores a copy of the state at isolation time."""
        monitor.check(delta_s=0.20, delta_phi=0.40)
        monitor.check(delta_s=0.20, delta_phi=0.40)

        record = monitor.activate("node-1", drifted_state)
        np.testing.assert_array_equal(record.entry_state, drifted_state)

    @pytest.mark.active
    def test_activate_produces_audit_trail(self, monitor, drifted_state):
        """activate() audit trail mentions the agent_id."""
        monitor.check(delta_s=0.20, delta_phi=0.40)
        monitor.check(delta_s=0.20, delta_phi=0.40)

        record = monitor.activate("node-42", drifted_state)
        trail = "\n".join(record.audit_trail)
        assert "node-42" in trail
        assert "GREY MODE ACTIVATED" in trail


# ─── Phase 3: Recovery ────────────────────────────────────────────────────────

class TestRecovery:

    @pytest.mark.active
    def test_recovery_cycle_reduces_drift(self, monitor, drifted_state, anchor):
        """After recovery, state is closer to anchor than the input."""
        drift_before = monitor.compute_psi_r(drifted_state)
        recovered = monitor.recovery_cycle(drifted_state)
        drift_after = monitor.compute_psi_r(recovered)
        assert drift_after < drift_before

    @pytest.mark.active
    def test_compute_psi_r_range(self, monitor, drifted_state):
        """psi_r is in [0, 1]."""
        psi_r = monitor.compute_psi_r(drifted_state)
        assert 0.0 <= psi_r <= 1.0

    @pytest.mark.active
    def test_compute_psi_r_anchor_is_zero(self, monitor, anchor):
        """Anchor state itself has zero drift."""
        psi_r = monitor.compute_psi_r(anchor)
        assert psi_r == pytest.approx(0.0, abs=1e-6)


# ─── Adaptive Threshold — r_merge ────────────────────────────────────────────

class TestRMerge:

    @pytest.mark.active
    def test_r_merge_decreases_with_isolation_time(self, monitor, net_stats):
        """Longer isolation → lower r_merge (tighter re-entry bar)."""
        r_short = monitor.compute_r_merge(1.0, net_stats)
        r_long  = monitor.compute_r_merge(10.0, net_stats)
        assert r_long < r_short

    @pytest.mark.active
    def test_r_merge_formula_manual(self, monitor, net_stats):
        """r_merge matches formula: exp(-β·Δt) · (1 + γ·σ_local/σ_global)."""
        import math
        delta_t = 5.0
        expected = (
            math.exp(-monitor.beta * delta_t)
            * (1.0 + monitor.gamma * net_stats.sigma_local / net_stats.sigma_global)
        )
        result = monitor.compute_r_merge(delta_t, net_stats)
        assert result == pytest.approx(expected, rel=1e-6)

    @pytest.mark.active
    def test_r_merge_sigma_ratio_effect(self, monitor):
        """Higher local/global variance ratio → higher r_merge (more lenient)."""
        low_local  = NetworkStats(sigma_local=0.01, sigma_global=0.10)
        high_local = NetworkStats(sigma_local=0.09, sigma_global=0.10)
        r_low  = monitor.compute_r_merge(3.0, low_local)
        r_high = monitor.compute_r_merge(3.0, high_local)
        assert r_high > r_low


# ─── Phase 4: Re-entry test ───────────────────────────────────────────────────

class TestReentryTest:

    @pytest.mark.active
    def test_reentry_passes_when_psi_r_below_threshold(self, monitor):
        """psi_r < r_c_new → re-entry approved."""
        assert monitor.reentry_test(psi_r=0.05, r_c_new=0.20) is True

    @pytest.mark.active
    def test_reentry_fails_when_psi_r_at_threshold(self, monitor):
        """psi_r == r_c_new → re-entry denied (strict less-than)."""
        assert monitor.reentry_test(psi_r=0.20, r_c_new=0.20) is False

    @pytest.mark.active
    def test_reentry_fails_when_psi_r_above_threshold(self, monitor):
        """psi_r > r_c_new → re-entry denied."""
        assert monitor.reentry_test(psi_r=0.30, r_c_new=0.20) is False


# ─── Full protocol: run() ─────────────────────────────────────────────────────

class TestRun:

    def _trigger_grey(self, monitor):
        monitor.check(delta_s=0.20, delta_phi=0.40)
        monitor.check(delta_s=0.20, delta_phi=0.40)

    @pytest.mark.active
    def test_run_converges_on_anchor_state(self, anchor, coherence, net_stats):
        """Recovery from a severely drifted state converges and reintegrates."""
        monitor = build_monitor(
            kappa=1.5, sigma_hat=0.1, theta_x=0.3,
            anchor=anchor, coherence=coherence, alert_threshold=2,
        )
        self._trigger_grey(monitor)

        # Near-orthogonal state (severe drift)
        rng = np.random.default_rng(7)
        perp = rng.standard_normal(DIM)
        perp -= perp.dot(anchor) * anchor
        perp /= np.linalg.norm(perp)

        result = monitor.run(
            "node-1", perp, net_stats,
            psi_inv=anchor, max_cycles=20,
            r_c_static=0.5,       # lenient re-entry for test
        )
        assert result.converged is True
        assert monitor.status == GreyModeStatus.HEALTHY

    @pytest.mark.active
    def test_run_exhausted_cycles_stays_grey(self, anchor, coherence, net_stats):
        """If max_cycles=1 and threshold impossibly tight → remains GREY."""
        monitor = build_monitor(
            kappa=1.5, sigma_hat=0.1, theta_x=0.3,
            anchor=anchor, coherence=coherence, alert_threshold=2,
        )
        self._trigger_grey(monitor)

        rng = np.random.default_rng(13)
        drifted = rng.standard_normal(DIM)
        drifted /= np.linalg.norm(drifted)

        result = monitor.run(
            "node-2", drifted, net_stats,
            max_cycles=1,
            r_c_static=0.0,   # impossible threshold
        )
        assert result.converged is False
        assert monitor.status == GreyModeStatus.GREY

    @pytest.mark.active
    def test_run_audit_trail_records_cycles(self, anchor, coherence, net_stats):
        """run() audit trail contains cycle-level entries."""
        monitor = build_monitor(
            kappa=1.5, sigma_hat=0.1, theta_x=0.3,
            anchor=anchor, coherence=coherence, alert_threshold=2,
        )
        self._trigger_grey(monitor)

        rng = np.random.default_rng(5)
        drifted = rng.standard_normal(DIM)
        drifted /= np.linalg.norm(drifted)

        result = monitor.run(
            "node-3", drifted, net_stats,
            max_cycles=3, r_c_static=0.5,
        )
        trail = "\n".join(result.audit_trail)
        assert "Cycle" in trail
        assert "Ψ_r" in trail

    @pytest.mark.scaffold
    def test_run_exhausted_mentions_aura_prime(self, anchor, coherence, net_stats):
        """When cycles exhausted, audit trail mentions AURA PRIME escalation."""
        monitor = build_monitor(
            kappa=1.5, sigma_hat=0.1, theta_x=0.3,
            anchor=anchor, coherence=coherence, alert_threshold=2,
        )
        self._trigger_grey(monitor)

        rng = np.random.default_rng(17)
        drifted = rng.standard_normal(DIM)
        drifted /= np.linalg.norm(drifted)

        result = monitor.run(
            "node-4", drifted, net_stats,
            max_cycles=1, r_c_static=0.0,
        )
        trail = "\n".join(result.audit_trail)
        assert "AURA PRIME" in trail
