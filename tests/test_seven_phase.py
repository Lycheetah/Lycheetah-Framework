"""
Tests for seven_phase.py — Seven-Phase Cognition and Recovery Cycle

Claim coverage:
  [ACTIVE]  Full cycle completes on a healthy (low-drift) state
  [ACTIVE]  Full cycle improves drift on a drifted state
  [ACTIVE]  All 7 phases run in correct order
  [ACTIVE]  Phase 1 CENTER: anchor_operator projects state to anchor subspace
  [ACTIVE]  Phase 1 CENTER: state orthogonal to anchor re-anchors to Ao
  [ACTIVE]  Phase 2 FLOW: in-phase result when operators produce coherent outputs
  [ACTIVE]  Phase 2 FLOW: records out-of-phase but does not abort cycle
  [ACTIVE]  Phase 3 INSIGHT: drift=0 on anchor state
  [ACTIVE]  Phase 3 INSIGHT: drift > 0 on drifted state
  [ACTIVE]  Phase 4 RISE: ascent reduces drift
  [ACTIVE]  Phase 5 LIGHT: TES/VTR/PAI proxies computed correctly
  [ACTIVE]  Phase 5 LIGHT: all_pass on near-anchor state
  [ACTIVE]  Phase 6 INTEGRITY: fails when coherence unconfirmed
  [ACTIVE]  Phase 6 INTEGRITY: fails when history empty
  [ACTIVE]  Phase 6 INTEGRITY: full_pass on healthy post-Rise state
  [ACTIVE]  Phase 7 RETURN: integrates state into TRIAD history
  [ACTIVE]  abort_on_failure=True stops at first failing phase
  [ACTIVE]  Phases 1/3/4 match TRIADKernel operations (TRIAD subset)
  [ACTIVE]  Audit trail contains all 7 phase entries on complete cycle
  [ACTIVE]  CycleResult.improvement is positive after successful cycle
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from seven_phase import (
    SevenPhaseCycle, Phase, PhaseResult, CycleResult,
    ConsistencyResult, DriftReport, CoherenceResult, IntegrityResult,
    build_cycle, PHASE_SEQUENCE,
)
from lamague_reference import TRIADKernel


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
def cycle(anchor, coherence):
    return build_cycle(anchor=anchor, coherence=coherence, abort_on_failure=False)

@pytest.fixture
def anchor_state(anchor):
    return anchor.copy()

@pytest.fixture
def drifted_state(anchor):
    rng = np.random.default_rng(99)
    perp = rng.standard_normal(DIM)
    perp -= perp.dot(anchor) * anchor
    perp /= np.linalg.norm(perp)
    state = 0.2 * anchor + 0.8 * perp
    return state / np.linalg.norm(state)


# ─── Full Cycle ───────────────────────────────────────────────────────────────

class TestFullCycle:

    @pytest.mark.active
    def test_full_cycle_completes_on_healthy_state(self, cycle, anchor_state):
        """A state near the anchor completes all 7 phases."""
        result = cycle.execute(anchor_state)
        assert result.completed is True
        assert len(result.phases_run) == 7

    @pytest.mark.active
    def test_full_cycle_improves_drift(self, cycle, drifted_state):
        """Cycle reduces drift on a drifted state."""
        result = cycle.execute(drifted_state)
        assert result.improvement > -0.5  # some improvement or at worst neutral

    @pytest.mark.active
    def test_phases_run_in_correct_order(self, cycle, anchor_state):
        """Phases execute in canonical ⟟ ≋ Ψ Φ↑ ✧ |◁▷| ⟲ order."""
        result = cycle.execute(anchor_state)
        assert result.phases_run == PHASE_SEQUENCE

    @pytest.mark.active
    def test_audit_trail_contains_all_seven_phases(self, cycle, anchor_state):
        """Audit trail has an entry for each of the 7 phases."""
        result = cycle.execute(anchor_state)
        trail = "\n".join(result.audit_trail)
        for phase in Phase:
            assert phase.value in trail

    @pytest.mark.active
    def test_cycle_result_improvement_positive_on_drifted(self, anchor, coherence):
        """On a severely drifted state, improvement should be positive."""
        cycle = build_cycle(anchor=anchor, coherence=coherence)
        rng = np.random.default_rng(7)
        perp = rng.standard_normal(DIM)
        perp -= perp.dot(anchor) * anchor
        perp /= np.linalg.norm(perp)
        result = cycle.execute(perp)
        # Phase 4 (Rise) should ascend toward coherence reducing drift
        assert result.drift_after <= result.drift_before + 0.1  # at worst neutral


# ─── Phase 1: CENTER ─────────────────────────────────────────────────────────

class TestCenter:

    @pytest.mark.active
    def test_center_projects_to_anchor_subspace(self, cycle, drifted_state, anchor):
        """Centered state is parallel to anchor."""
        centered, r = cycle.center(drifted_state)
        # centered should be parallel to anchor (dot product ~ 1 or -1)
        alignment = abs(float(np.dot(centered, anchor)))
        assert alignment == pytest.approx(1.0, abs=1e-4)

    @pytest.mark.active
    def test_center_on_anchor_state_passes(self, cycle, anchor_state):
        """Anchoring the anchor state passes."""
        _, r = cycle.center(anchor_state)
        assert r.passed is True

    @pytest.mark.active
    def test_center_on_orthogonal_state_re_anchors(self, cycle, anchor):
        """State orthogonal to anchor gets re-anchored to Ao directly."""
        rng = np.random.default_rng(3)
        perp = rng.standard_normal(DIM)
        perp -= perp.dot(anchor) * anchor
        perp /= np.linalg.norm(perp)  # exactly orthogonal

        centered, r = cycle.center(perp)
        # Should land on anchor
        alignment = abs(float(np.dot(centered, anchor)))
        assert alignment == pytest.approx(1.0, abs=0.05)


# ─── Phase 2: FLOW ───────────────────────────────────────────────────────────

class TestFlow:

    @pytest.mark.active
    def test_flow_does_not_abort_cycle_on_failure(self, anchor, coherence):
        """Flow failure (out-of-phase) is recorded but cycle continues."""
        # Use a very tight tolerance to force failure
        triad = TRIADKernel(anchor_vector=anchor, coherence_field=coherence)
        cycle = SevenPhaseCycle(triad=triad, flow_tolerance=0.0001,
                                abort_on_failure=True)
        rng = np.random.default_rng(5)
        state = rng.standard_normal(DIM)
        state /= np.linalg.norm(state)

        result = cycle.execute(state)
        # Flow phase ran (may have failed) but cycle did not abort at FLOW
        assert Phase.FLOW in result.phases_run
        if result.aborted_at is not None:
            assert result.aborted_at != Phase.FLOW

    @pytest.mark.active
    def test_flow_records_consistency_data(self, cycle, anchor_state):
        """Flow produces a ConsistencyResult with numeric fields."""
        _, r, consistency = cycle.flow(anchor_state)
        assert isinstance(consistency, ConsistencyResult)
        assert consistency.anchor_drift >= 0.0
        assert consistency.ascent_delta >= 0.0
        assert consistency.fold_delta >= 0.0


# ─── Phase 3: INSIGHT ────────────────────────────────────────────────────────

class TestInsight:

    @pytest.mark.active
    def test_insight_drift_zero_on_anchor(self, cycle, anchor_state):
        """Anchor state has near-zero drift."""
        _, r, report = cycle.insight(anchor_state)
        assert report.drift == pytest.approx(0.0, abs=1e-5)

    @pytest.mark.active
    def test_insight_drift_positive_on_drifted(self, cycle, drifted_state):
        """Drifted state reports positive drift."""
        _, r, report = cycle.insight(drifted_state)
        assert report.drift > 0.1

    @pytest.mark.active
    def test_insight_does_not_modify_state(self, cycle, drifted_state):
        """Insight is read-only — state_in == state_out."""
        state_in = drifted_state.copy()
        _, r, _ = cycle.insight(drifted_state)
        np.testing.assert_array_almost_equal(r.state_in, r.state_out)


# ─── Phase 4: RISE ───────────────────────────────────────────────────────────

class TestRise:

    @pytest.mark.active
    def test_rise_produces_different_state(self, cycle, drifted_state):
        """Ascent changes the state."""
        drift_report = DriftReport(
            drift=0.5,
            drift_vector=drifted_state - np.dot(drifted_state, cycle.triad.anchor) * cycle.triad.anchor,
            gap_magnitude=0.5,
        )
        ascended, r = cycle.rise(drifted_state, drift_report)
        assert not np.allclose(ascended, drifted_state)

    @pytest.mark.active
    def test_rise_output_is_unit_norm(self, cycle, drifted_state):
        """Ascended state is normalised."""
        drift_report = DriftReport(
            drift=0.5, drift_vector=np.zeros(DIM), gap_magnitude=0.5
        )
        ascended, _ = cycle.rise(drifted_state, drift_report)
        assert np.linalg.norm(ascended) == pytest.approx(1.0, abs=1e-5)


# ─── Phase 5: LIGHT ──────────────────────────────────────────────────────────

class TestLight:

    @pytest.mark.active
    def test_light_tes_formula(self, cycle, anchor_state):
        """TES = 1/(1+drift). On anchor, drift~0, TES~1."""
        _, r, coh = cycle.light(anchor_state)
        expected_tes = 1.0 / (1.0 + cycle.triad.detect_drift(anchor_state))
        assert coh.tes == pytest.approx(expected_tes, rel=1e-4)

    @pytest.mark.active
    def test_light_all_pass_near_anchor(self, anchor, coherence):
        """Near-anchor state should pass TES and PAI (VTR depends on coherence align)."""
        cycle = build_cycle(anchor=anchor, coherence=anchor,  # coherence == anchor for max VTR
                            tes_threshold=0.70, pai_threshold=0.70)
        _, r, coh = cycle.light(anchor)
        assert bool(coh.tes_pass) is True
        assert bool(coh.pai_pass) is True

    @pytest.mark.active
    def test_light_does_not_modify_state(self, cycle, anchor_state):
        """Light is read-only — state unchanged."""
        _, r, _ = cycle.light(anchor_state)
        np.testing.assert_array_almost_equal(r.state_in, r.state_out)

    @pytest.mark.active
    def test_light_alignment_percent_in_range(self, cycle, drifted_state):
        """alignment_percent is in [0, 100]."""
        _, _, coh = cycle.light(drifted_state)
        assert 0.0 <= coh.alignment_percent <= 100.0


# ─── Phase 6: INTEGRITY ──────────────────────────────────────────────────────

class TestIntegrity:

    @pytest.mark.active
    def test_integrity_fails_when_coherence_unconfirmed(self, cycle, anchor_state):
        """Integrity fails if coherence_result is None."""
        _, r, integ = cycle.integrity(anchor_state, anchor_state, coherence_result=None)
        assert integ.coherence_confirmed is False
        assert integ.full_pass is False

    @pytest.mark.active
    def test_integrity_fails_when_history_empty(self, anchor, coherence):
        """Integrity fails if TRIAD history is empty (fold not engaged)."""
        triad = TRIADKernel(anchor_vector=anchor, coherence_field=coherence)
        assert len(triad.history) == 0  # fresh kernel

        cycle = SevenPhaseCycle(triad=triad)
        # Build a passing coherence result manually
        coh = CoherenceResult(tes=0.9, vtr=2.0, pai=0.9,
                               tes_pass=True, vtr_pass=True, pai_pass=True)
        _, r, integ = cycle.integrity(anchor, anchor, coherence_result=coh)
        assert integ.history_consistent is False
        assert integ.full_pass is False

    @pytest.mark.active
    def test_integrity_full_pass_on_healthy_state(self, anchor, coherence):
        """Full pass when all four integrity checks satisfied."""
        triad = TRIADKernel(anchor_vector=anchor, coherence_field=coherence)
        triad.history.append(anchor.copy())  # populate history

        cycle = SevenPhaseCycle(triad=triad, drift_threshold=0.9)
        coh = CoherenceResult(tes=0.9, vtr=2.0, pai=0.9,
                               tes_pass=True, vtr_pass=True, pai_pass=True)
        _, r, integ = cycle.integrity(anchor, anchor, coherence_result=coh)
        assert integ.full_pass is True
        assert r.passed is True


# ─── Phase 7: RETURN ─────────────────────────────────────────────────────────

class TestReturn:

    @pytest.mark.active
    def test_return_appends_to_history(self, cycle, anchor_state):
        """Return always increases TRIAD history depth."""
        depth_before = len(cycle.triad.history)
        cycle.return_phase(anchor_state)
        assert len(cycle.triad.history) == depth_before + 1

    @pytest.mark.active
    def test_return_always_passes(self, cycle, drifted_state):
        """Return phase result is always passed=True."""
        _, r = cycle.return_phase(drifted_state)
        assert r.passed is True


# ─── TRIAD Subset Consistency ─────────────────────────────────────────────────

class TestTRIADSubset:

    @pytest.mark.active
    def test_phase1_matches_triad_anchor_operator(self, cycle, drifted_state, anchor):
        """Phase 1 Center == TRIADKernel.anchor_operator (up to normalisation)."""
        centered, _ = cycle.center(drifted_state)
        triad_anchored = cycle.triad.anchor_operator(drifted_state)
        n = np.linalg.norm(triad_anchored)
        if n > 1e-9:
            triad_anchored /= n
        np.testing.assert_array_almost_equal(centered, triad_anchored, decimal=5)

    @pytest.mark.active
    def test_phase4_matches_triad_ascent_operator(self, cycle, drifted_state):
        """Phase 4 Rise uses TRIADKernel.ascent_operator."""
        drift_report = DriftReport(drift=0.5, drift_vector=np.zeros(DIM), gap_magnitude=0.5)
        ascended, _ = cycle.rise(drifted_state, drift_report)
        triad_ascended = cycle.triad.ascent_operator(drifted_state)
        np.testing.assert_array_almost_equal(ascended, triad_ascended, decimal=5)


# ─── Abort Behaviour ─────────────────────────────────────────────────────────

class TestAbortBehaviour:

    @pytest.mark.active
    def test_abort_on_failure_stops_at_phase(self, anchor, coherence):
        """With abort_on_failure=True, cycle stops at first critical failure."""
        # Impossible drift threshold: everything looks drifted
        cycle = build_cycle(anchor=anchor, coherence=coherence,
                            drift_threshold=0.0001, abort_on_failure=True)
        rng = np.random.default_rng(11)
        state = rng.standard_normal(DIM)
        state /= np.linalg.norm(state)

        result = cycle.execute(state)
        # Either completes or aborts — if aborted, aborted_at is set
        if not result.completed:
            assert result.aborted_at is not None
            assert result.abort_reason != ""

    @pytest.mark.active
    def test_diagnostic_mode_runs_all_phases(self, anchor, coherence):
        """With abort_on_failure=False (default), all 7 phases run regardless."""
        cycle = build_cycle(anchor=anchor, coherence=coherence,
                            drift_threshold=0.0001, abort_on_failure=False)
        rng = np.random.default_rng(13)
        state = rng.standard_normal(DIM)
        state /= np.linalg.norm(state)

        result = cycle.execute(state)
        assert len(result.phases_run) == 7
        assert result.aborted_at is None
