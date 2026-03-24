"""
Tests for cascade_engine.py

Claim coverage:
  [ACTIVE] Theorem 4.1 — Coherence Non-Decrease: post_coherence >= pre_coherence after cascade
  [ACTIVE] Information Preservation: info_content >= initial after cascade
  [ACTIVE] Entropy Preservation: total_entropy >= initial after cascade
  [ACTIVE] Truth pressure formula: Π = (E·P) / S
  [ACTIVE] Demotion accuracy: truth-pressure guidance selects correctly
  [ACTIVE] Knowledge contextualization — old blocks preserved as qualified, not deleted
  [SCAFFOLD] Layer assignment thresholds (defaults: foundation=1.5, theory=1.2)
  [SCAFFOLD] Trigger margin parameter (default: 0.3)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from cascade_engine import KnowledgeBlock, CascadeEngine, StaticBaseline, NoPressureBaseline


# ── Truth pressure ─────────────────────────────────────────────────────────────

class TestTruthPressure:
    @pytest.mark.active
    def test_formula_basic(self):
        """Π = (E·P) / S"""
        block = KnowledgeBlock(
            id="b", content="", domain="d", paradigm="p",
            evidence_strength=0.8,
            explanatory_power=2.0,
            uncertainty=0.4,
        )
        assert abs(block.truth_pressure - (0.8 * 2.0) / 0.4) < 1e-9

    @pytest.mark.active
    def test_higher_evidence_increases_pressure(self):
        b1 = KnowledgeBlock(id="b1", content="", domain="d", paradigm="p",
                            evidence_strength=0.5, explanatory_power=2.0, uncertainty=0.5)
        b2 = KnowledgeBlock(id="b2", content="", domain="d", paradigm="p",
                            evidence_strength=0.9, explanatory_power=2.0, uncertainty=0.5)
        assert b2.truth_pressure > b1.truth_pressure

    @pytest.mark.active
    def test_higher_uncertainty_decreases_pressure(self):
        b1 = KnowledgeBlock(id="b1", content="", domain="d", paradigm="p",
                            evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.2)
        b2 = KnowledgeBlock(id="b2", content="", domain="d", paradigm="p",
                            evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.8)
        assert b1.truth_pressure > b2.truth_pressure

    @pytest.mark.active
    def test_near_zero_uncertainty_handled(self):
        """uncertainty=0 is guarded against division by zero."""
        block = KnowledgeBlock(id="b", content="", domain="d", paradigm="p",
                               evidence_strength=0.9, explanatory_power=2.5, uncertainty=0.0)
        # Should not raise; uses max(S, 0.01) guard
        pi = block.truth_pressure
        assert pi > 0
        assert pi < float('inf')


# ── Layer assignment ───────────────────────────────────────────────────────────

class TestLayerAssignment:
    @pytest.mark.scaffold
    def test_high_pressure_becomes_foundation(self):
        """Π >= 1.5 → FOUNDATION (default threshold)."""
        engine = CascadeEngine()
        block = KnowledgeBlock(
            id="b", content="", domain="d", paradigm="p",
            evidence_strength=0.9, explanatory_power=2.0, uncertainty=0.2,
        )
        # Π = 0.9*2.0/0.2 = 9.0 — well above 1.5
        engine.add_block(block)
        assert block.layer == "FOUNDATION"

    @pytest.mark.scaffold
    def test_medium_pressure_becomes_theory(self):
        """1.2 <= Π < 1.5 → THEORY."""
        engine = CascadeEngine()
        block = KnowledgeBlock(
            id="b", content="", domain="d", paradigm="p",
            evidence_strength=0.6, explanatory_power=1.1, uncertainty=0.45,
        )
        pi = block.truth_pressure  # 0.6*1.1/0.45 ≈ 1.467 — just under 1.5
        assert 1.2 <= pi < 1.5
        engine.add_block(block)
        assert block.layer == "THEORY"

    @pytest.mark.scaffold
    def test_low_pressure_becomes_edge(self):
        """Π < 1.2 → EDGE."""
        engine = CascadeEngine()
        block = KnowledgeBlock(
            id="b", content="", domain="d", paradigm="p",
            evidence_strength=0.3, explanatory_power=1.0, uncertainty=0.9,
        )
        pi = block.truth_pressure  # 0.3*1.0/0.9 ≈ 0.33
        assert pi < 1.2
        engine.add_block(block)
        assert block.layer == "EDGE"


# ── Contradiction detection ────────────────────────────────────────────────────

class TestContradiction:
    @pytest.mark.active
    def test_same_domain_different_paradigm_contradicts(self):
        engine = CascadeEngine()
        b1 = KnowledgeBlock(id="b1", content="", domain="physics",
                            paradigm="classical", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        b2 = KnowledgeBlock(id="b2", content="", domain="physics",
                            paradigm="quantum", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        assert engine.contradicts(b1, b2)

    @pytest.mark.active
    def test_different_domain_does_not_contradict(self):
        engine = CascadeEngine()
        b1 = KnowledgeBlock(id="b1", content="", domain="physics",
                            paradigm="classical", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        b2 = KnowledgeBlock(id="b2", content="", domain="chemistry",
                            paradigm="classical", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        assert not engine.contradicts(b1, b2)

    @pytest.mark.active
    def test_same_paradigm_does_not_contradict(self):
        engine = CascadeEngine()
        b1 = KnowledgeBlock(id="b1", content="", domain="physics",
                            paradigm="classical", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        b2 = KnowledgeBlock(id="b2", content="", domain="physics",
                            paradigm="classical", evidence_strength=0.5,
                            explanatory_power=1.2, uncertainty=0.5)
        assert not engine.contradicts(b1, b2)

    @pytest.mark.active
    def test_qualified_block_does_not_contradict(self):
        """Once demoted to qualified, block no longer counts as contradiction."""
        engine = CascadeEngine()
        b1 = KnowledgeBlock(id="b1", content="", domain="physics",
                            paradigm="classical", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        b1.regime = "qualified"
        b2 = KnowledgeBlock(id="b2", content="", domain="physics",
                            paradigm="quantum", evidence_strength=0.7,
                            explanatory_power=1.5, uncertainty=0.3)
        assert not engine.contradicts(b1, b2)


# ── Cascade invariants (Theorem 4.1) ──────────────────────────────────────────

class TestCascadeInvariants:
    @pytest.mark.active
    def test_coherence_non_decrease(self, simple_blocks):
        """Theorem 4.1: coherence >= pre_coherence after every cascade."""
        engine = CascadeEngine()
        for block in simple_blocks:
            event = engine.add_block(block)
        if engine.cascade_events:
            for ev in engine.cascade_events:
                assert ev["coherence_preserved"], (
                    f"Coherence decreased: {ev['pre_coherence']:.4f} → {ev['post_coherence']:.4f}"
                )

    @pytest.mark.active
    def test_information_preservation(self, simple_blocks):
        """Information content does not decrease across cascade."""
        engine = CascadeEngine()
        for block in simple_blocks:
            engine.add_block(block)
        for ev in engine.cascade_events:
            assert ev["info_preserved"], "Information content decreased during cascade"

    @pytest.mark.active
    def test_entropy_preservation(self, simple_blocks):
        """Total entropy does not decrease (contextualization increases S)."""
        engine = CascadeEngine()
        for block in simple_blocks:
            engine.add_block(block)
        for ev in engine.cascade_events:
            assert ev["entropy_preserved"], "Total entropy decreased during cascade"

    @pytest.mark.active
    def test_coherence_non_decrease_physics(self, physics_blocks):
        """Theorem 4.1 holds for physics paradigm shift."""
        engine = CascadeEngine()
        for block in physics_blocks:
            event = engine.add_block(block)
        assert len(engine.cascade_events) > 0, "Expected cascade did not fire"
        for ev in engine.cascade_events:
            assert ev["coherence_preserved"]

    @pytest.mark.active
    def test_invariants_hold_multi_block(self):
        """Invariants hold with 5+ blocks across 2 domains."""
        from cascade_engine import KnowledgeBlock
        engine = CascadeEngine()
        blocks = [
            KnowledgeBlock(id="a1", content="", domain="optics", paradigm="wave",
                           evidence_strength=0.6, explanatory_power=1.5, uncertainty=0.4),
            KnowledgeBlock(id="a2", content="", domain="optics", paradigm="particle",
                           evidence_strength=0.95, explanatory_power=2.8, uncertainty=0.05),
            KnowledgeBlock(id="b1", content="", domain="gravity", paradigm="newton",
                           evidence_strength=0.7, explanatory_power=2.0, uncertainty=0.3),
            KnowledgeBlock(id="b2", content="", domain="gravity", paradigm="einstein",
                           evidence_strength=0.99, explanatory_power=2.9, uncertainty=0.02),
            KnowledgeBlock(id="c1", content="", domain="thermal", paradigm="phlogiston",
                           evidence_strength=0.2, explanatory_power=1.1, uncertainty=0.8),
        ]
        for b in blocks:
            engine.add_block(b)
        for ev in engine.cascade_events:
            assert ev["coherence_preserved"]
            assert ev["info_preserved"]


# ── Knowledge preservation (contextualization not deletion) ───────────────────

class TestKnowledgePreservation:
    @pytest.mark.active
    def test_demoted_block_still_exists(self, physics_blocks):
        """Old knowledge demoted to qualified — not deleted."""
        engine = CascadeEngine()
        for block in physics_blocks:
            engine.add_block(block)
        assert len(engine.cascade_events) > 0
        # The old block should still be in the engine
        assert "newtonian_mechanics" in engine.blocks

    @pytest.mark.active
    def test_demoted_block_is_qualified(self, physics_blocks):
        """Demoted block has regime='qualified'."""
        engine = CascadeEngine()
        for block in physics_blocks:
            engine.add_block(block)
        demoted = engine.blocks["newtonian_mechanics"]
        assert demoted.regime == "qualified"

    @pytest.mark.active
    def test_new_block_is_universal(self, physics_blocks):
        """New higher-Π block remains universal after cascade."""
        engine = CascadeEngine()
        for block in physics_blocks:
            engine.add_block(block)
        new_block = engine.blocks["special_relativity"]
        assert new_block.regime == "universal"

    @pytest.mark.active
    def test_total_block_count_preserved(self, physics_blocks):
        """No blocks are deleted — count is always additive."""
        engine = CascadeEngine()
        count = 0
        for block in physics_blocks:
            engine.add_block(block)
            count += 1
        assert len(engine.blocks) == count


# ── Demotion accuracy ─────────────────────────────────────────────────────────

class TestDemotionAccuracy:
    @pytest.mark.active
    def test_lower_pi_block_is_demoted(self, simple_blocks):
        """The block with lower truth pressure is the one demoted."""
        old, new = simple_blocks
        assert new.truth_pressure > old.truth_pressure

        engine = CascadeEngine()
        for block in simple_blocks:
            engine.add_block(block)

        # old_claim should be qualified (demoted), new_claim should be universal
        assert engine.blocks["old_claim"].regime == "qualified"
        assert engine.blocks["new_claim"].regime == "universal"

    @pytest.mark.active
    def test_trigger_margin_prevents_premature_cascade(self):
        """If Π difference < trigger_margin, no cascade fires."""
        engine = CascadeEngine(trigger_margin=0.5)
        b1 = KnowledgeBlock(id="b1", content="", domain="d", paradigm="p1",
                            evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4)
        b2 = KnowledgeBlock(id="b2", content="", domain="d", paradigm="p2",
                            evidence_strength=0.85, explanatory_power=2.0, uncertainty=0.4)
        # Π difference should be small — less than trigger_margin
        pi_diff = abs(b2.truth_pressure - b1.truth_pressure)
        engine.add_block(b1)
        engine.add_block(b2)
        assert len(engine.cascade_events) == 0 or pi_diff > 0.5


# ── Coherence metric ──────────────────────────────────────────────────────────

class TestCoherenceMetric:
    @pytest.mark.active
    def test_empty_engine_coherence_is_one(self):
        engine = CascadeEngine()
        assert engine.coherence() == 1.0

    @pytest.mark.active
    def test_single_block_coherence_is_one(self):
        engine = CascadeEngine()
        engine.add_block(KnowledgeBlock(id="b", content="", domain="d", paradigm="p",
                                        evidence_strength=0.5, explanatory_power=1.5, uncertainty=0.5))
        assert engine.coherence() == 1.0

    @pytest.mark.active
    def test_unresolved_contradictions_lower_coherence(self):
        """Static baseline (no demotion) has lower coherence than CASCADE."""
        from cascade_engine import KnowledgeBlock
        blocks = [
            KnowledgeBlock(id="b1", content="", domain="d", paradigm="p1",
                           evidence_strength=0.8, explanatory_power=2.0, uncertainty=0.4),
            KnowledgeBlock(id="b2", content="", domain="d", paradigm="p2",
                           evidence_strength=0.9, explanatory_power=2.5, uncertainty=0.2),
        ]
        engine = CascadeEngine()
        static = StaticBaseline()
        for b in blocks:
            engine.add_block(b)
        for b in blocks:
            static.add_block(b)
        # CASCADE resolves contradictions; static leaves them
        assert engine.coherence() >= static.coherence()


# ── No-pressure baseline (ablation) ──────────────────────────────────────────

class TestNoPressureBaseline:
    @pytest.mark.active
    def test_no_pressure_demotion_is_random(self):
        """NoPressureBaseline demotes randomly — accuracy should be near 0.5."""
        import numpy as np
        accuracies = []
        for seed in range(100):
            baseline = NoPressureBaseline(seed=seed)
            b1 = KnowledgeBlock(id="b1", content="", domain="d", paradigm="p1",
                                evidence_strength=0.4, explanatory_power=1.5, uncertainty=0.5)
            b2 = KnowledgeBlock(id="b2", content="", domain="d", paradigm="p2",
                                evidence_strength=0.9, explanatory_power=2.5, uncertainty=0.1)
            baseline.add_block(b1)
            baseline.add_block(b2)
            if baseline.cascade_events:
                acc = sum(1 for e in baseline.cascade_events if e["demotion_correct"]) / len(baseline.cascade_events)
                accuracies.append(acc)
        if accuracies:
            mean_acc = np.mean(accuracies)
            # Should be near 0.5 (random), not near 1.0 (truth-pressure guided)
            assert 0.3 <= mean_acc <= 0.7, f"Random baseline accuracy {mean_acc:.2f} unexpectedly extreme"


# ── Reset ─────────────────────────────────────────────────────────────────────

class TestReset:
    @pytest.mark.active
    def test_reset_clears_state(self, simple_blocks):
        engine = CascadeEngine()
        for block in simple_blocks:
            engine.add_block(block)
        engine.reset()
        assert len(engine.blocks) == 0
        assert len(engine.cascade_events) == 0
        assert len(engine.coherence_trace) == 0
        assert engine.step == 0
