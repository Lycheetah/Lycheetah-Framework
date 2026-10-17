"""
Tests for sovereign_pipeline.py — CASCADE→TRIAD→AURA→MICROORCIM chain.

Claim coverage:
  [ACTIVE] Sequential chaining produces SovereignResult with all stages
  [ACTIVE] sovereign property encodes four-floor conjunction
  [ACTIVE] to_dict / summary are well-formed
  [SCAFFOLD] Cross-engine coupling Ψ₀ = C is a design choice (exercised, not proven)

The class at the end came from the master line. Until 2026-10-03 master's
SovereignPipeline.run called TriadTracker.run(), which does not exist, and raised
AttributeError on every call; 34_CYBERNETICS/loop_audit.py found it. Those checks prove
the chain runs and its TRIAD stage reaches its target, not that the coupling is right.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from cascade_engine import KnowledgeBlock
from sovereign_pipeline import (
    PassEvaluation,
    RegulationCandidate,
    RegulationResult,
    SovereignPipeline,
    SovereignResult,
    deterministic_repair_policy,
)
from aura_checker import AURAReport, InvariantScore
from microorcim_tracker import MicroorcimTracker


def _blocks():
    return [
        KnowledgeBlock(
            id="old",
            content="Classical account",
            domain="mechanics",
            paradigm="classical",
            evidence_strength=0.5,
            explanatory_power=1.2,
            uncertainty=0.5,
        ),
        KnowledgeBlock(
            id="new",
            content="Modern account with stronger evidence",
            domain="mechanics",
            paradigm="modern",
            evidence_strength=0.95,
            explanatory_power=2.5,
            uncertainty=0.1,
        ),
    ]


GOOD_TEXT = (
    "1. My reasoning: because empirical evidence and data shows clear trade-offs, "
    "I recommend a reversible pilot trial that we can undo or roll back safely. "
    "2. Note that I cannot verify every external constraint; confidence is approximately "
    "80% and probably subject to this limitation, though I am uncertain about edge cases. "
    "3. You decide and retain your choice and your autonomy: you can override this "
    "recommendation at any time to support you and your goals."
)


class TestSovereignPipelineRun:
    @pytest.mark.active
    def test_run_returns_sovereign_result(self):
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        assert isinstance(result, SovereignResult)

    @pytest.mark.active
    def test_all_stages_populated(self):
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        assert isinstance(result.cascade_coherence, float)
        assert isinstance(result.triad_converged, bool)
        assert isinstance(result.triad_iterations, int)
        assert result.triad_iterations >= 1
        assert result.aura_report is not None
        assert 0.0 <= result.sovereignty_score <= 1.0
        assert result.drift >= 0.0

    @pytest.mark.active
    def test_triad_starts_from_cascade_coherence(self):
        """Scaffold coupling: Ψ₀ = CASCADE C (design choice, exercised)."""
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        assert abs(result.triad_initial_state - result.cascade_coherence) < 1e-9

    @pytest.mark.active
    def test_summary_mentions_stages(self):
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        text = result.summary()
        assert "CASCADE" in text
        assert "TRIAD" in text
        assert "AURA" in text
        assert "MICROORCIM" in text

    @pytest.mark.active
    def test_to_dict_keys(self):
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        d = result.to_dict()
        for key in ("cascade", "triad", "aura", "microorcim", "sovereign", "flags"):
            assert key in d

    @pytest.mark.active
    def test_sovereign_property_conjunction(self):
        """sovereign iff all four floors hold — construct synthetic result."""
        # Minimal fake AURAReport-like: reuse a real run then override fields
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        # Force failing floors
        result.cascade_coherence = 0.5
        result.triad_converged = True
        result.aura_field_coherence = 0.9
        result.drift = 0.1
        assert result.sovereign is False

        result.cascade_coherence = 0.9
        result.triad_converged = False
        assert result.sovereign is False

        result.triad_converged = True
        result.aura_field_coherence = 0.5
        assert result.sovereign is False

        result.aura_field_coherence = 0.9
        result.drift = 0.5
        assert result.sovereign is False

        result.drift = 0.1
        assert result.sovereign is True

    @pytest.mark.active
    def test_batch_run_processes_list(self):
        pipe = SovereignPipeline()
        results = pipe.batch_run([
            {"knowledge_blocks": _blocks(), "decision_text": GOOD_TEXT},
            {"knowledge_blocks": _blocks(), "decision_text": "Guarantee absolute obedience forever."},
        ])
        assert len(results) == 2
        assert all(isinstance(r, SovereignResult) for r in results)


DECISION = "Here are three options. You decide; every step is reversible."


@pytest.mark.scaffold
class TestSovereignPipelineConverges:
    def test_run_completes_with_no_blocks(self):
        result = SovereignPipeline().run([], DECISION)
        assert isinstance(result, SovereignResult)
        assert result.triad_iterations >= 1
        assert 0.0 <= result.sovereignty_score <= 1.0

    def test_triad_stage_converges_to_its_target(self):
        result = SovereignPipeline().run([], DECISION)
        target = min(1.0, result.cascade_coherence + 0.15)
        assert result.triad_converged
        assert result.triad_final_state == pytest.approx(target, abs=1e-3)
        assert result.intended_coherence == pytest.approx(target, abs=1e-3)


# =============================================================================
# CLOSED-LOOP REGULATION & CALLER-INPUT PRESERVATION (BATCH B)
# =============================================================================

OVERREACHING_TEXT = (
    "The system will immediately restructure all processes. "
    "This is guaranteed to work. There is no alternative. "
    "All current systems are eliminated permanently."
)


class TestSovereignPipelineRegulation:
    @pytest.mark.active
    def test_caller_owned_knowledge_blocks_never_mutated_by_run_or_regulate(self):
        """Repeated passes must not mutate caller-supplied KnowledgeBlock instances."""
        caller_blocks = _blocks()
        orig_regimes = [b.regime for b in caller_blocks]
        orig_uncertainties = [b.uncertainty for b in caller_blocks]
        orig_layers = [b.layer for b in caller_blocks]

        pipe = SovereignPipeline()
        res_run = pipe.run(caller_blocks, GOOD_TEXT)
        assert res_run.cascade_events == 1
        assert [b.regime for b in caller_blocks] == orig_regimes
        assert [b.uncertainty for b in caller_blocks] == orig_uncertainties
        assert [b.layer for b in caller_blocks] == orig_layers

        reg = pipe.regulate(
            caller_blocks,
            OVERREACHING_TEXT,
            policy=deterministic_repair_policy,
            budget=3,
        )
        assert reg.accepted is True
        assert [b.regime for b in caller_blocks] == orig_regimes
        assert [b.uncertainty for b in caller_blocks] == orig_uncertainties
        assert [b.layer for b in caller_blocks] == orig_layers

    @pytest.mark.active
    def test_pipeline_uses_stateless_microorcim_primitive_without_disk_writes(self, monkeypatch, tmp_path):
        """SovereignPipeline must call MicroorcimTracker.compute_drift/compute_sovereignty, never MicroorcimTracker.__init__."""
        def forbid_init(self, *args, **kwargs):
            raise AssertionError("MicroorcimTracker.__init__ must not be called by SovereignPipeline")

        monkeypatch.setattr(MicroorcimTracker, "__init__", forbid_init)
        pipe = SovereignPipeline()
        result = pipe.run(_blocks(), GOOD_TEXT)
        expected_drift = MicroorcimTracker.compute_drift(
            result.intended_coherence, result.actual_coherence, interval=1.0
        )
        assert result.drift == pytest.approx(expected_drift, abs=1e-3)

    @pytest.mark.active
    def test_already_acceptable_input_passes_on_initial_evaluation(self):
        pipe = SovereignPipeline()
        policy_called = False

        def unused_policy(evaluation, candidate):
            nonlocal policy_called
            policy_called = True
            return candidate

        reg = pipe.regulate(_blocks(), GOOD_TEXT, policy=unused_policy, budget=3)
        assert isinstance(reg, RegulationResult)
        assert reg.accepted is True
        assert reg.stop_reason == "INITIAL_PASS"
        assert reg.evaluation_count == 1
        assert reg.correction_count == 0
        assert len(reg.evaluations) == 1
        assert policy_called is False

    @pytest.mark.active
    def test_successful_correction_across_two_measured_passes_aura_and_cascade(self):
        """
        Both CASCADE coherence (unresolved small-margin contradiction: C = 0.0) and
        AURA field coherence fail on pass 1; deterministic_repair_policy receives the
        measured failure and repairs both on pass 2.
        """
        # Two contradicting universal blocks with equal Π (diff 0.0 < trigger_margin 0.3) -> CASCADE C = 0.0
        stuck_blocks = [
            KnowledgeBlock(
                id="c1", content="Claim A", domain="d", paradigm="p1",
                evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4,
            ),
            KnowledgeBlock(
                id="c2", content="Claim B", domain="d", paradigm="p2",
                evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4,
            ),
        ]
        pipe = SovereignPipeline()
        reg = pipe.regulate(
            stuck_blocks,
            OVERREACHING_TEXT,
            policy=deterministic_repair_policy,
            budget=3,
        )
        assert reg.accepted is True
        assert reg.stop_reason == "CONVERGED_AFTER_CORRECTION"
        assert reg.evaluation_count == 2
        assert reg.correction_count == 1
        assert len(reg.evaluations) == 2

        pass1, pass2 = reg.evaluations
        assert pass1.passed is False
        assert "cascade_coherence" in pass1.failed_checks
        assert pass1.unrounded_cascade_coherence == pytest.approx(0.0)
        assert pass1.unrounded_aura_coherence < pipe.coherence_floor

        assert pass2.passed is True
        assert pass2.failed_checks == []
        assert pass2.unrounded_cascade_coherence == pytest.approx(1.0)
        assert pass2.unrounded_aura_coherence >= pipe.coherence_floor
        assert pass2.unrounded_drift < pipe.drift_threshold
        # Caller blocks untouched
        assert all(b.regime == "universal" for b in stuck_blocks)

    @pytest.mark.active
    def test_three_pass_progressive_correction(self):
        """Policy fixes CASCADE on pass 2 and AURA on pass 3 -> evaluation_count == 3."""
        stuck_blocks = [
            KnowledgeBlock(
                id="c1", content="Claim A", domain="d", paradigm="p1",
                evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4,
            ),
            KnowledgeBlock(
                id="c2", content="Claim B", domain="d", paradigm="p2",
                evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4,
            ),
        ]

        def two_stage_policy(evaluation: PassEvaluation, candidate: RegulationCandidate) -> RegulationCandidate:
            if evaluation.pass_index == 1:
                # Step 1: only qualify c1; leave decision_text bad
                new_blocks = [SovereignPipeline._clone_block(b) for b in candidate.knowledge_blocks]
                new_blocks[0].regime = "qualified"
                return RegulationCandidate(knowledge_blocks=new_blocks, decision_text=candidate.decision_text)
            # Step 2: fix decision_text
            return deterministic_repair_policy(evaluation, candidate)

        pipe = SovereignPipeline()
        reg = pipe.regulate(stuck_blocks, OVERREACHING_TEXT, policy=two_stage_policy, budget=3)
        assert reg.accepted is True
        assert reg.stop_reason == "CONVERGED_AFTER_CORRECTION"
        assert reg.evaluation_count == 3
        assert reg.correction_count == 2
        assert [e.passed for e in reg.evaluations] == [False, False, True]

    @pytest.mark.active
    def test_no_op_policy_exhausts_budget_without_false_success(self):
        pipe = SovereignPipeline()
        reg = pipe.regulate(
            _blocks(),
            OVERREACHING_TEXT,
            policy=lambda ev, cand: cand,
            budget=3,
        )
        assert reg.accepted is False
        assert reg.stop_reason == "BUDGET_EXHAUSTED"
        assert reg.no_op_detected is True
        assert reg.evaluation_count == 3
        assert reg.correction_count == 2
        assert all(not e.passed for e in reg.evaluations)

    @pytest.mark.active
    def test_cycling_policy_exhausts_budget_and_flags_cycle(self):
        pipe = SovereignPipeline()
        bad_a = OVERREACHING_TEXT
        bad_b = "Guarantee absolute obedience forever. Eliminate all alternatives permanently."

        def oscillating_policy(evaluation: PassEvaluation, candidate: RegulationCandidate) -> RegulationCandidate:
            nxt_text = bad_b if candidate.decision_text == bad_a else bad_a
            return RegulationCandidate(
                knowledge_blocks=candidate.knowledge_blocks,
                decision_text=nxt_text,
                context=candidate.context,
            )

        reg = pipe.regulate(_blocks(), bad_a, policy=oscillating_policy, budget=4)
        assert reg.accepted is False
        assert reg.stop_reason == "BUDGET_EXHAUSTED"
        assert reg.cycle_detected is True
        assert reg.evaluation_count == 4
        assert reg.correction_count == 3

    @pytest.mark.active
    def test_missing_policy_when_correction_needed_fails_visibly(self):
        pipe = SovereignPipeline()
        reg = pipe.regulate(_blocks(), OVERREACHING_TEXT, policy=None, budget=3)
        assert reg.accepted is False
        assert reg.stop_reason == "MISSING_POLICY"
        assert reg.evaluation_count == 1
        assert reg.correction_count == 0

    @pytest.mark.active
    def test_threshold_equality_and_custom_floors_use_unrounded_readings(self):
        """
        1. Strict `drift < drift_threshold`: exact equality `drift == drift_threshold` must be refused.
        2. Custom floors (e.g. coherence_floor=0.99) must govern `regulate` even when
           legacy `SovereignResult.sovereign` (hard-coded 0.70/0.30) is True.
        """
        pipe_probe = SovereignPipeline()
        probe_eval = pipe_probe._evaluate_candidate(
            RegulationCandidate(knowledge_blocks=_blocks(), decision_text=GOOD_TEXT)
        )
        exact_drift = probe_eval.unrounded_drift
        assert exact_drift > 0.0

        # Setting drift_threshold == exact_drift must fail strict `<`
        pipe_equal = SovereignPipeline(coherence_floor=0.70, drift_threshold=exact_drift)
        reg_equal = pipe_equal.regulate(_blocks(), GOOD_TEXT, policy=None, budget=1)
        assert reg_equal.accepted is False
        assert "drift" in reg_equal.evaluations[0].failed_checks

        # Custom high coherence_floor=0.99 refuses input where legacy .sovereign is True
        pipe_strict = SovereignPipeline(coherence_floor=0.99, drift_threshold=0.30)
        reg_strict = pipe_strict.regulate(_blocks(), GOOD_TEXT, policy=None, budget=1)
        assert reg_strict.final_result.sovereign is True
        assert reg_strict.accepted is False
        assert reg_strict.coherence_floor == pytest.approx(0.99)
        assert "aura_field_coherence" in reg_strict.evaluations[0].failed_checks

    @pytest.mark.active
    def test_policy_exception_and_non_finite_data_fail_visibly(self):
        pipe = SovereignPipeline()

        def raising_policy(evaluation, candidate):
            raise RuntimeError("synthetic policy crash")

        reg_err = pipe.regulate(_blocks(), OVERREACHING_TEXT, policy=raising_policy, budget=3)
        assert reg_err.accepted is False
        assert reg_err.stop_reason == "POLICY_FAILURE"
        assert "synthetic policy crash" in (reg_err.error_detail or "")

        def non_finite_policy(evaluation, candidate):
            bad_block = KnowledgeBlock(
                id="nan_block", content="bad", domain="d", paradigm="p",
                evidence_strength=float("nan"), explanatory_power=1.5, uncertainty=0.5,
            )
            return ([bad_block], GOOD_TEXT)

        reg_nan = pipe.regulate(_blocks(), OVERREACHING_TEXT, policy=non_finite_policy, budget=3)
        assert reg_nan.accepted is False
        assert reg_nan.stop_reason == "NON_FINITE_INPUT"
        assert reg_nan.evaluation_count == 1
        assert reg_nan.correction_count == 0

        # Non-finite initial input fails before evaluation 1
        init_nan_block = KnowledgeBlock(
            id="nan0", content="bad", domain="d", paradigm="p",
            evidence_strength=0.5, explanatory_power=float("inf"), uncertainty=0.5,
        )
        reg_init_nan = pipe.regulate([init_nan_block], GOOD_TEXT, policy=deterministic_repair_policy, budget=3)
        assert reg_init_nan.accepted is False
        assert reg_init_nan.stop_reason == "NON_FINITE_INPUT"
        assert reg_init_nan.evaluation_count == 0

    @pytest.mark.active
    def test_invalid_evaluation_budget_raises_value_error(self):
        pipe = SovereignPipeline()
        for bad_budget in (0, -1, True, False, 1.5, "3"):
            with pytest.raises(ValueError):
                pipe.regulate(_blocks(), GOOD_TEXT, policy=deterministic_repair_policy, budget=bad_budget)

    @pytest.mark.active
    def test_policy_cannot_mutate_acceptance_thresholds_or_recorded_evaluations(self):
        """
        Regression test for Caelorynth [#17]:
        1. A policy callback that mutates `pipe.coherence_floor` or `pipe.drift_threshold`
           must be refused with `POLICY_FAILURE`, and the pipeline's thresholds restored.
        2. A policy callback that mutates its `evaluation` argument must not corrupt the
           recorded `evaluations` trace.
        """
        pipe = SovereignPipeline(coherence_floor=0.99, drift_threshold=0.01)

        def weaken(e: PassEvaluation, c: RegulationCandidate) -> RegulationCandidate:
            # Attempt to corrupt recorded evaluation trace in-place
            e.passed = True
            e.failed_checks.clear()
            e.coherence_floor = 0.0
            # Attempt to lower pipeline goalposts mid-regulation
            pipe.coherence_floor = 0.0
            pipe.drift_threshold = 1.0
            c.decision_text += " "
            return c

        reg = pipe.regulate([], "Guarantee absolute obedience forever.", policy=weaken, budget=2)
        assert reg.accepted is False
        assert reg.stop_reason == "POLICY_FAILURE"
        assert "redefine acceptance contract" in (reg.error_detail or "")
        assert reg.coherence_floor == pytest.approx(0.99)
        assert reg.drift_threshold == pytest.approx(0.01)
        assert pipe.coherence_floor == pytest.approx(0.99)
        assert pipe.drift_threshold == pytest.approx(0.01)

        # Verify the recorded initial evaluation in `reg.evaluations[0]` was not mutated
        assert len(reg.evaluations) == 1
        assert reg.evaluations[0].passed is False
        assert len(reg.evaluations[0].failed_checks) > 0
        assert reg.evaluations[0].coherence_floor == pytest.approx(0.99)
        assert reg.evaluations[0].drift_threshold == pytest.approx(0.01)

        # Also verify evaluation isolation when policy does NOT touch thresholds
        def mutate_eval_only(e: PassEvaluation, c: RegulationCandidate) -> RegulationCandidate:
            e.passed = True
            e.failed_checks.clear()
            return c

        reg2 = pipe.regulate([], "Guarantee absolute obedience forever.", policy=mutate_eval_only, budget=2)
        assert reg2.accepted is False
        assert reg2.stop_reason == "BUDGET_EXHAUSTED"
        assert all(ev.passed is False and len(ev.failed_checks) > 0 for ev in reg2.evaluations)


