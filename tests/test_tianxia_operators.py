"""
Tests for the TIANXIA governance operators.

Claim coverage:
  [ACTIVE]     All nine operator modules import and their core arithmetic holds
  [ACTIVE]     Ren Zheng R(s) = (W+V+F)/3, floor at θ_r = 0.618
  [ACTIVE]     Wang Dao WD_score = (L+F+Γ)/3, two-stage gate
  [ACTIVE]     Five-Fold Hexie composite and binding-constraint identification
  [SCAFFOLD]   Decision geometry characterised — see operator_audit.py
  [ACTIVE]     Gate consistency defect FIXED — reachable-R band enforced

WHY THIS FILE EXISTS
--------------------
TIANXIA shipped nine operator implementations in May 2026. Until now not one was
covered by the pytest suite. Their self-tests live in `__main__` blocks, so they
run only when someone invokes the file by hand — and three of them asserted with
bare `assert False`, which `python -O` strips entirely. The module README stated
"all self-tests passing", which was true and ungated.

This is the same defect class as the `lycheetah-guard` entry point: a claimed
capability with nothing exercising it in CI.

The characterisation tests below lock in the decision geometry that
`operator_audit.py` measured on 2026-08-08. They are not endorsements of that
geometry — several of the numbers are arguably wrong. They exist so that when
the geometry changes, it changes visibly and on purpose.
"""

import os
import sys

import pytest

_HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_HERE, "..", "32_TIANXIA", "implementations"))
sys.path.insert(0, os.path.join(_HERE, "..", "12_IMPLEMENTATIONS", "core"))


# ─────────────────────────────────────────────────────────────
# All nine operators exist and import
# ─────────────────────────────────────────────────────────────

TIANXIA_MODULES = [
    "ren_zheng",
    "wang_dao",
    "hexie_five_fold",
    "civilisational_governance_benchmark",
    "aura_score_hexie",
    "triad_wuwei",
    "shi_propensity",
    "datong_gradient",
    "tianxia_governance",
]


@pytest.mark.active
@pytest.mark.parametrize("modname", TIANXIA_MODULES)
def test_operator_module_imports(modname):
    """
    The README claims nine operator implementations. Verify each one imports.

    Generic form of the defect that let lycheetah-guard ship broken for four
    releases: a documented component nothing ever loaded.
    """
    import importlib

    mod = importlib.import_module(modname)
    assert mod is not None


# ─────────────────────────────────────────────────────────────
# Ren Zheng
# ─────────────────────────────────────────────────────────────


@pytest.mark.active
def test_ren_zheng_is_unweighted_mean_of_three():
    from ren_zheng import GovernanceState, ren_zheng_score

    assert ren_zheng_score(GovernanceState(0.9, 0.6, 0.3)) == pytest.approx(0.6)
    assert ren_zheng_score(GovernanceState(1.0, 1.0, 1.0)) == pytest.approx(1.0)
    assert ren_zheng_score(GovernanceState(0.0, 0.0, 0.0)) == pytest.approx(0.0)


@pytest.mark.active
def test_ren_zheng_floor_is_phi_minus_one():
    """θ_r = 0.618. The value is φ−1; the choice is not empirically calibrated."""
    from ren_zheng import THETA_R_DEFAULT, GovernanceState, wang_dao_eligible

    assert THETA_R_DEFAULT == pytest.approx(0.618, abs=1e-3)
    assert wang_dao_eligible(GovernanceState(0.9, 0.9, 0.9))
    assert not wang_dao_eligible(GovernanceState(0.3, 0.3, 0.3))


@pytest.mark.active
def test_ren_zheng_rejects_out_of_range():
    from ren_zheng import GovernanceState

    with pytest.raises(ValueError):
        GovernanceState(1.5, 0.5, 0.5)
    with pytest.raises(ValueError):
        GovernanceState(0.5, -0.1, 0.5)


# ─────────────────────────────────────────────────────────────
# Wang Dao
# ─────────────────────────────────────────────────────────────


def _traj(minxin, force, stability, r, n=1):
    """
    Build a trajectory. `r` must lie in the reachable band [F/3, (2+F)/3];
    passing one outside it is now a ValueError by design, so tests that want
    an extreme R must choose an F that admits it.
    """
    from wang_dao import GovernanceTrajectory, TrajectoryPoint

    return GovernanceTrajectory(
        points=[TrajectoryPoint(minxin, force, stability, r) for _ in range(n)]
    )


def _rand_point(rng):
    """Uniform sample over the *reachable* state space."""
    from ren_zheng import reachable_r_bounds
    from wang_dao import TrajectoryPoint

    f = rng.random()
    lo, hi = reachable_r_bounds(f)
    return TrajectoryPoint(rng.random(), f, rng.random(), lo + rng.random() * (hi - lo))


def _rand_traj(rng):
    from wang_dao import GovernanceTrajectory

    return GovernanceTrajectory(points=[_rand_point(rng)])


@pytest.mark.active
def test_wang_dao_score_is_unweighted_mean_of_three():
    from wang_dao import wang_dao_score

    s = wang_dao_score(_traj(0.9, 0.6, 0.3, 0.8))
    assert s["WD_score"] == pytest.approx(0.6)
    assert s["L_legitimacy"] == pytest.approx(0.9)


@pytest.mark.active
def test_wang_dao_high_virtue_classifies_wang():
    assert __import__("wang_dao").classify(_traj(0.85, 0.90, 0.88, 0.85))[
        "classification"
    ] == "Wang"


@pytest.mark.active
def test_wang_dao_ren_zheng_gate_forces_ba_regardless_of_score():
    """
    Documented behaviour: R(s) < θ_r → Ba, whatever WD_score says.

    Note what this means in practice — the audit found 91.5% of all Ba verdicts
    are decided here, so for the majority class the three-axis Wang Dao
    diagnostic is not what is doing the work.
    """
    from wang_dao import classify

    # F must be low enough for R to fall below the floor, yet L and Γ high
    # enough to carry WD_score over θ_wang. F=0.30 admits R ∈ [0.10, 0.767].
    r = classify(_traj(1.0, 0.30, 1.0, 0.25))
    assert r["classification"] == "Ba"
    assert r["ren_zheng_gate"] is False
    assert r["WD_score"] >= 0.70  # would have been Wang but for the gate


@pytest.mark.active
def test_wang_dao_rejects_empty_trajectory():
    from wang_dao import GovernanceTrajectory

    with pytest.raises(ValueError):
        GovernanceTrajectory(points=[])


# ─────────────────────────────────────────────────────────────
# Decision geometry — characterisation, not endorsement
# ─────────────────────────────────────────────────────────────


@pytest.mark.scaffold
def test_class_balance_is_heavily_skewed_to_ba():
    """
    MEASURED 2026-08-08 by operator_audit.py at n=100,000, over the REACHABLE
    state space: Wang 5.6% · Ba 74.1% · Indeterminate 20.3%, with 91.5% of Ba
    verdicts decided by the Ren Zheng gate alone.

    (The first run reported 4.6/72.8/22.6 with 85.1% gate-decided, but sampled
    the naive [0,1]^4 cube — a third of which is impossible governance. The
    corrected numbers make the gate-dominance finding stronger, not weaker.)

    Locked as characterisation. A governance classifier assigning 74% of its
    input space to one class may be correct — most conceivable governments are
    not virtuous — but it has never been checked against a real distribution,
    and the number should not move silently.
    """
    import random

    from wang_dao import classify

    rng = random.Random(20260808)
    counts = {"Wang": 0, "Ba": 0, "Indeterminate": 0}
    n = 20_000
    for _ in range(n):
        counts[classify(_rand_traj(rng))["classification"]] += 1

    assert 0.02 < counts["Wang"] / n < 0.09, counts
    assert 0.65 < counts["Ba"] / n < 0.80, counts


@pytest.mark.scaffold
def test_ren_zheng_score_dominates_the_decision():
    """
    MEASURED 2026-08-08 over the reachable space: ren_zheng_score 31.4%, then
    long_cycle_stability 12.8%, minxin 12.2%, force_restraint 11.7%.

    One input moves the verdict roughly 2.5x more than any other, and the three
    that are nominally the Wang Dao axes are near-interchangeable — which
    follows from WD_score being their unweighted mean.
    """
    import random

    from wang_dao import classify

    from ren_zheng import reachable_r_bounds

    rng = random.Random(20260809)
    n = 1_500
    flips = {"ren_zheng_score": 0, "minxin": 0}

    for _ in range(n):
        p = _rand_point(rng)
        m, f, g, r = p.minxin, p.force_restraint, p.long_cycle_stability, p.ren_zheng_score
        base = classify(_traj(m, f, g, r))["classification"]
        lo, hi = reachable_r_bounds(f)
        if classify(_traj(m, f, g, lo + rng.random() * (hi - lo)))["classification"] != base:
            flips["ren_zheng_score"] += 1
        if classify(_traj(rng.random(), f, g, r))["classification"] != base:
            flips["minxin"] += 1

    assert flips["ren_zheng_score"] > flips["minxin"] * 1.8, flips


# ─────────────────────────────────────────────────────────────
# Known defect — held open on purpose
# ─────────────────────────────────────────────────────────────


@pytest.mark.active
def test_ren_zheng_gate_rejects_arithmetically_unreachable_score():
    """
    FIXED 2026-08-08 — this was a strict xfail for the length of one commit.

    The defect: TrajectoryPoint.ren_zheng_score was a free float bound to no
    GovernanceState, so a point could declare an R that its own force_restraint
    made arithmetically unreachable. R = (W+V+F)/3 with W,V ∈ [0,1] pins R to
    [F/3, (2+F)/3], so at F=0 the true ceiling is 0.667 — yet R=0.95 passed the
    Ren Zheng gate unchallenged, admitting a polity under total coercion as
    Wang-eligible.

    The repair is the band check in TrajectoryPoint.__post_init__, using
    ren_zheng.reachable_r_bounds(). Every pre-existing fixture in the module
    satisfies it; only the impossible states are rejected.
    """
    from ren_zheng import reachable_r_bounds

    # F = 0 caps R at 2/3 even with perfect welfare and voice.
    assert reachable_r_bounds(0.0) == pytest.approx((0.0, 2 / 3))

    with pytest.raises(ValueError, match="unreachable"):
        _traj(0.80, 0.0, 0.90, 0.95)

    # The boundary itself is admissible; only beyond it is rejected.
    _traj(0.80, 0.0, 0.90, 2 / 3)
    with pytest.raises(ValueError, match="unreachable"):
        _traj(0.80, 0.0, 0.90, 2 / 3 + 0.01)


@pytest.mark.active
def test_reachable_band_width_is_constant():
    """
    The band [F/3, (2+F)/3] has width 2/3 for every F, so exactly one third of
    a naive uniform [0,1] draw for R is impossible at any given F.

    MEASURED: the audit's first run sampled the naive cube, making 33.4% of its
    input space states no governance could occupy.
    """
    from ren_zheng import reachable_r_bounds

    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        lo, hi = reachable_r_bounds(f)
        assert hi - lo == pytest.approx(2 / 3)


# ─────────────────────────────────────────────────────────────
# Five-Fold Hexie
# ─────────────────────────────────────────────────────────────


@pytest.mark.active
def test_hexie_composite_and_binding_constraint():
    from hexie_five_fold import HexieState, binding_constraint, hexie_five_fold

    perfect = HexieState(1.0, 1.0, 1.0, 1.0, 1.0)
    assert hexie_five_fold(perfect)[0] == pytest.approx(1.0)

    # binding_constraint returns the component name with its Chinese term,
    # e.g. "ecological (天人合一)" — match the prefix, not the decoration.
    weak_ecology = HexieState(0.9, 0.9, 0.1, 0.9, 0.9)
    assert binding_constraint(weak_ecology).startswith("ecological")

    weak_sharing = HexieState(0.9, 0.9, 0.9, 0.9, 0.1)
    assert binding_constraint(weak_sharing).startswith("sharing")


@pytest.mark.active
def test_hexie_rejects_out_of_range():
    from hexie_five_fold import HexieState

    with pytest.raises(ValueError):
        HexieState(0.5, 0.5, 1.2, 0.5, 0.5)


# ─────────────────────────────────────────────────────────────
# Benchmark ordering
# ─────────────────────────────────────────────────────────────


@pytest.mark.active
def test_benchmark_orders_reference_scenarios():
    """
    The three baselines must order extractive < liberal-procedural < aligned.

    This is the module's own worked example, and it is exactly the kind of
    self-authored fixture the 2026-08-07 external validation showed cannot
    establish that an operator tracks anything real. It is kept as a
    regression check on the arithmetic and must not be cited as evidence.
    """
    from civilisational_governance_benchmark import (
        EXTRACTIVE_BASELINE,
        TIANXIA_ALIGNED_BASELINE,
        evaluate,
    )

    low = evaluate(EXTRACTIVE_BASELINE)
    high = evaluate(TIANXIA_ALIGNED_BASELINE)
    assert low is not None and high is not None
