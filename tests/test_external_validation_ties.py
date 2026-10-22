"""The external-validation AUC tests must correct for tied scores.

The hand-written lens gives most texts one identical score (96% of the persona
statements). The Mann-Whitney null SE without the tie correction then overstates
the noise, and a significant result was published as "not distinguishable from
chance" (review RV23, 2026-10-22). These tests hold both scripts' statistics to
scipy's tie-corrected asymptotic test, and keep the untied case unchanged.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

stats = pytest.importorskip("scipy.stats")

APPS = Path(__file__).resolve().parents[1] / "33_APPLICATIONS"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_rv23_{name}", APPS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


EXT = _load("external_validation")
IPT = _load("independent_publisher_test")

# Shaped like the persona result: one modal score, a few texts moved off it.
HIGHER = [85.0] * 489 + [70.0] * 9 + [61.5] * 2
LOWER = [85.0] * 473 + [70.0] * 13 + [64.4] * 14


def _scipy_p(higher, lower) -> float:
    return float(stats.mannwhitneyu(higher, lower, alternative="two-sided",
                                    method="asymptotic", use_continuity=False).pvalue)


def _auc(higher, lower) -> float:
    return EXT.roc_auc(list(higher), list(lower))


def test_tied_scores_match_scipy_in_both_scripts():
    a = _auc(HIGHER, LOWER)
    want = _scipy_p(HIGHER, LOWER)
    _, p_ext = EXT.auc_significance(a, len(HIGHER), len(LOWER), HIGHER + LOWER)
    _, p_ipt = IPT.auc_sig(a, len(HIGHER), len(LOWER), HIGHER + LOWER)
    assert math.isclose(p_ext, want, rel_tol=1e-9)
    assert math.isclose(p_ipt, want, rel_tol=1e-9)
    assert want < 0.05


def test_ignoring_ties_is_the_published_error():
    a = _auc(HIGHER, LOWER)
    _, p_uncorrected = EXT.auc_significance(a, len(HIGHER), len(LOWER))
    _, p_corrected = EXT.auc_significance(a, len(HIGHER), len(LOWER), HIGHER + LOWER)
    assert p_uncorrected > 0.05 > p_corrected


def test_untied_scores_are_unchanged_by_the_correction():
    higher = [float(i) for i in range(0, 400, 2)]
    lower = [float(i) + 0.5 for i in range(0, 380, 2)]
    a = _auc(higher, lower)
    plain = EXT.auc_significance(a, len(higher), len(lower))
    pooled = EXT.auc_significance(a, len(higher), len(lower), higher + lower)
    assert plain == pooled
    assert math.isclose(pooled[1], _scipy_p(higher, lower), rel_tol=1e-9)
    assert IPT.auc_sig(a, len(higher), len(lower), higher + lower) == pooled
