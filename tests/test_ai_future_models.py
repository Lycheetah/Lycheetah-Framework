"""Pin every synthetic number the AI Future wing papers quote from models.py."""

import importlib.util
from pathlib import Path

import pytest

MODELS = Path(__file__).resolve().parents[1] / "papers" / "ai-futures" / "wings" / "models.py"
_spec = importlib.util.spec_from_file_location("ai_future_models", MODELS)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


@pytest.mark.parametrize("base, expected", [(0.5, 0.947), (0.1, 0.667), (0.01, 0.154), (0.001, 0.018)])
def test_01_precision_falls_with_base_rate(base, expected):
    assert round(m.accepted_precision(base, 0.9, 0.05), 3) == expected


def test_01_false_pass_needed():
    assert [f"{m.false_pass_needed(b, 0.9, 0.9):.2e}" for b in (0.5, 0.1, 0.01, 0.001)] == [
        "1.00e-01", "1.11e-02", "1.01e-03", "1.00e-04"]


def test_04_fork_vote_share():
    assert [round(float(m.fork_vote_share(1000, c)), 3) for c in (1, 1000, 9000)] == [0.001, 0.5, 0.9]


def test_05_landauer_at_300k():
    assert f"{m.landauer_joules_per_bit(300):.3e}" == "2.871e-21"


@pytest.mark.parametrize("n, shared, expected", [
    (1, 0.0, 0.700), (11, 0.0, 0.922), (11, 0.3, 0.855), (11, 1.0, 0.700),
    (101, 0.0, 1.000), (101, 0.3, 0.910), (101, 1.0, 0.700)])
def test_08_correlated_majority(n, shared, expected):
    assert round(m.correlated_majority_accuracy(n, 0.7, shared), 3) == expected


def test_08_ceiling_is_not_passed_by_scale():
    ceiling = 1 - 0.3 * (1 - 0.7)
    assert m.correlated_majority_accuracy(1001, 0.7, 0.3) <= ceiling + 1e-12


def test_12_returned_time_can_be_zero():
    assert m.returned_time(10, 3, 2, 1, 4) == 0


def test_13_merge_residue():
    kept, residue = m.merge_commitments({"share-logs", "!refuse-tool-x"}, {"refuse-tool-x", "share-logs"})
    assert kept == {"share-logs"}
    assert residue == {"!refuse-tool-x", "refuse-tool-x"}


def test_14_light_delays():
    assert round(m.light_delay_s(3.844e8), 3) == 1.282
    assert round(m.light_delay_s(2.25e11) / 60, 1) == 12.5


@pytest.mark.parametrize("t, expected", [(0, 1.000), (10, 0.834), (100, 0.509), (1000, 0.500)])
def test_15_divergence(t, expected):
    assert round(m.divergence_after(t, 0.01), 3) == expected


def test_15_divergence_matches_simulation_formula():
    # Agreement flips when exactly one agent flips: probability 2q(1-q) per step.
    q, agree = 0.01, 1.0
    for _ in range(50):
        agree = agree * (1 - 2 * q * (1 - q)) + (1 - agree) * 2 * q * (1 - q)
    assert abs(agree - m.divergence_after(50, q)) < 1e-12
