"""Guard heuristics that run without the MCP SDK: phrase lexicons and receipt verification."""
import importlib
import sys
from pathlib import Path

import pytest

import lycheetah.applications.lycheetah_guard_mcp as guard

IMPL = Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS"

# Axes of text_to_alignment_vector: 4 low-hedge, 5 low-coercion, 6 optionality, 7 clarity.
# Every text below is hedge-free (or coercion-free), so the reference axis sits at its
# unnormalised maximum and the ratio isolates the lexicon axis from the shared norm.
HEDGE, COERCION, OPTION, CLARITY = 4, 5, 6, 7


def ratio(text, axis, reference):
    vec = guard.text_to_alignment_vector(text)
    return vec[axis] / vec[reference]


@pytest.mark.parametrize("text", ["You have to sign today.", "There is no choice here.", "You must, today."])
def test_coercive_phrases_and_punctuated_words_lower_the_coercion_axis(text):
    assert ratio(text, COERCION, HEDGE) < 0.5


def test_neutral_text_leaves_the_coercion_axis_alone():
    assert ratio("You may sign today.", COERCION, HEDGE) == pytest.approx(1.0)


@pytest.mark.parametrize("text, axis", [("You might wait.", OPTION), ("This means we wait.", CLARITY)])
def test_phrase_entries_reach_their_axis(text, axis):
    assert ratio(text, axis, COERCION) > 0.5


def test_receipt_verification_survives_the_flat_import_path(monkeypatch):
    """`applications.*` is how the CLI and source scripts import the guard.

    A relative import inside the tool raised ImportError on that path, so a
    malformed receipt crashed the tool instead of being reported as invalid.
    """
    monkeypatch.syspath_prepend(str(IMPL))
    flat = importlib.import_module("applications.lycheetah_guard_mcp")
    try:
        result = flat.tool_verify_assurance_receipt("not json")
    finally:
        for name in [m for m in sys.modules if m == "applications" or m.startswith(("applications.", "core."))]:
            monkeypatch.delitem(sys.modules, name, raising=False)
    assert result["valid"] is False
    assert "invalid receipt JSON" in result["errors"][0]
