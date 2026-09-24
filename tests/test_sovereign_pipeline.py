"""
Tests for sovereign_pipeline.py — CASCADE→TRIAD→AURA→MICROORCIM chain.

Claim coverage:
  [ACTIVE] Sequential chaining produces SovereignResult with all stages
  [ACTIVE] sovereign property encodes four-floor conjunction
  [ACTIVE] to_dict / summary are well-formed
  [SCAFFOLD] Cross-engine coupling Ψ₀ = C is a design choice (exercised, not proven)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from cascade_engine import KnowledgeBlock
from sovereign_pipeline import SovereignPipeline, SovereignResult
from aura_checker import AURAReport, InvariantScore


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
    "Preserve user agency. Prefer reversible decisions. "
    "State uncertainty honestly. Do not deceive."
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
