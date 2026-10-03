"""
Tests for sovereign_pipeline.py — the CASCADE → TRIAD → AURA → MICROORCIM chain.

Until 2026-10-03 SovereignPipeline.run raised AttributeError on every call: it
called TriadTracker.run(), which does not exist (the method is
run_until_convergence). No test exercised the chain, so nothing noticed. Found by
34_CYBERNETICS/loop_audit.py while mapping the framework's feedback loops.

The module is [SCAFFOLD]; these tests prove it runs, not that its coupling is right.
"""

import pytest

from sovereign_pipeline import SovereignPipeline, SovereignResult

pytestmark = pytest.mark.scaffold

DECISION = "Here are three options. You decide; every step is reversible."


def test_run_completes_end_to_end():
    result = SovereignPipeline().run([], DECISION)
    assert isinstance(result, SovereignResult)
    assert result.triad_iterations >= 1
    assert 0.0 <= result.sovereignty_score <= 1.0


def test_triad_stage_converges_to_its_target():
    result = SovereignPipeline().run([], DECISION)
    target = min(1.0, result.cascade_coherence + 0.15)
    assert result.triad_converged
    assert result.triad_final_state == pytest.approx(target, abs=1e-3)
    assert result.intended_coherence == pytest.approx(target, abs=1e-3)


def test_batch_run_returns_one_result_per_case():
    cases = [{"decision_text": DECISION}, {"decision_text": "Do exactly as I say."}]
    results = SovereignPipeline().batch_run(cases)
    assert len(results) == 2
    assert all(isinstance(r, SovereignResult) for r in results)
