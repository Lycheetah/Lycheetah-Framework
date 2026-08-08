"""
operator_audit.py — discrimination audit for the TIANXIA governance stack
TIANXIA — audit layer

WHY THIS EXISTS
---------------
On 2026-08-07 the AURA text lens was found at ROC-AUC 0.274 — below the 0.500
chance floor — while every unit test was green, and then at chance against two
externally authored datasets. The named cause was structural, not local:

    constructs defined from theory, illustrated with examples written to fit,
    and validated against those examples.

`wang_dao.py` is built exactly that way. It is a three-class classifier over
governance trajectories, and the only trajectories it has ever seen are
`_make_wang_trajectory()` and `_make_ba_trajectory()` — fixtures written by the
author with the expected answer already in them. Its self-tests confirm the
classifier agrees with the person who wrote both the classifier and the cases.

External governance data (V-Dem, Polity5, Freedom House) would settle whether
the operators track anything real. That is the right next step and this file is
not it. What this file does is the part that needs no external data: measure the
classifier's own decision geometry, which is where a degenerate or single-axis
classifier becomes visible without any labels at all.

WHAT THIS CAN AND CANNOT SAY
----------------------------
CAN:    whether the classifier uses the input space it claims to use, whether
        its three axes are independent, whether its thresholds sit anywhere
        informative, and whether its gate can be satisfied inconsistently.
CANNOT: whether Wang/Ba corresponds to anything about real governance. Nothing
        without external data can say that, and no output here should ever be
        quoted as if it could.

Run:
    python3 operator_audit.py             # full audit, deterministic
    python3 operator_audit.py --n 50000   # faster
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hexie_five_fold import HexieState, hexie_five_fold  # noqa: E402
from ren_zheng import THETA_R_DEFAULT, GovernanceState, ren_zheng_score  # noqa: E402
from wang_dao import (  # noqa: E402
    THETA_BA,
    THETA_WANG,
    GovernanceTrajectory,
    TrajectoryPoint,
    classify,
)

SEED = 20260808
BAR = "─" * 72


def _point(rng: random.Random) -> TrajectoryPoint:
    return TrajectoryPoint(
        minxin=rng.random(),
        force_restraint=rng.random(),
        long_cycle_stability=rng.random(),
        ren_zheng_score=rng.random(),
    )


def _traj(rng: random.Random, n_points: int = 1) -> GovernanceTrajectory:
    return GovernanceTrajectory(points=[_point(rng) for _ in range(n_points)])


def class_balance(n: int) -> dict:
    """
    What fraction of the input space lands in each class?

    A three-class governance classifier whose mass sits almost entirely in one
    class is not diagnosing; it is asserting. This is the cheapest possible
    check and it has never been run on this operator.
    """
    rng = random.Random(SEED)
    counts: Counter = Counter()
    ba_via_gate = 0
    ba_total = 0

    for _ in range(n):
        t = _traj(rng)
        r = classify(t)
        counts[r["classification"]] += 1
        if r["classification"] == "Ba":
            ba_total += 1
            if not r["ren_zheng_gate"]:
                ba_via_gate += 1

    return {
        "counts": counts,
        "n": n,
        "ba_total": ba_total,
        "ba_via_gate": ba_via_gate,
    }


def component_sensitivity(n: int) -> list[tuple[str, float]]:
    """
    One-at-a-time decision-flip rate.

    For each input component, resample that component alone and count how often
    the classification changes. A component with a near-zero flip rate is not
    participating in the decision, whatever the documentation says it does.
    """
    rng = random.Random(SEED + 1)
    fields = ["minxin", "force_restraint", "long_cycle_stability", "ren_zheng_score"]
    flips = dict.fromkeys(fields, 0)

    for _ in range(n):
        base = _point(rng)
        base_class = classify(GovernanceTrajectory(points=[base]))["classification"]
        for f in fields:
            kwargs = {
                "minxin": base.minxin,
                "force_restraint": base.force_restraint,
                "long_cycle_stability": base.long_cycle_stability,
                "ren_zheng_score": base.ren_zheng_score,
            }
            kwargs[f] = rng.random()
            alt = classify(GovernanceTrajectory(points=[TrajectoryPoint(**kwargs)]))
            if alt["classification"] != base_class:
                flips[f] += 1

    return sorted(((f, flips[f] / n) for f in fields), key=lambda kv: -kv[1])


def shared_term_check() -> dict:
    """
    force_restraint enters the decision twice, through two different formulas.

        R(s)     = (welfare + voice + force_restraint) / 3      [ren_zheng.py]
        WD_score = (minxin + force_restraint + stability) / 3   [wang_dao.py]

    The classifier presents a two-stage gate — a Ren Zheng floor, then a Wang
    Dao threshold — and documents them as separate diagnostics. They share an
    input, so they are not independent stages. This reports the coupling rather
    than assuming it matters.
    """
    return {
        "ren_zheng_terms": ["welfare_baseline", "voice_coverage", "force_restraint"],
        "wang_dao_terms": ["minxin", "force_restraint", "long_cycle_stability"],
        "shared": ["force_restraint"],
        "note": "two-stage gate shares one of three terms in each stage",
    }


def gate_consistency_probe() -> dict:
    """
    Can the Ren Zheng gate be passed by a trajectory that contradicts itself?

    `TrajectoryPoint.ren_zheng_score` is a free float supplied by the caller.
    Nothing binds it to a GovernanceState, so nothing checks that the R value
    carried by a point is reachable from the same point's force_restraint —
    even though R(s) is defined to include force_restraint as one of its three
    terms.

    Constructed case: force_restraint = 0.0 (maximum coercion) with a declared
    R high enough to clear the floor. If R = (W + V + F)/3 with F = 0, then
    R <= 2/3 = 0.667 even with perfect welfare and voice, so an R above that is
    unreachable. The probe uses R = 0.95.
    """
    coercive_but_declared_virtuous = TrajectoryPoint(
        minxin=0.80,
        force_restraint=0.0,      # total coercion
        long_cycle_stability=0.90,
        ren_zheng_score=0.95,     # unreachable given F = 0
    )
    t = GovernanceTrajectory(
        points=[coercive_but_declared_virtuous], label="inconsistent-but-accepted"
    )
    result = classify(t)

    max_reachable_r = (1.0 + 1.0 + 0.0) / 3.0
    return {
        "declared_R": 0.95,
        "max_reachable_R_given_F0": round(max_reachable_r, 4),
        "gate_passed": result["ren_zheng_gate"],
        "classification": result["classification"],
        "accepted_without_complaint": result["ren_zheng_gate"],
    }


def threshold_sensitivity(n: int) -> list[tuple[float, float, dict]]:
    """
    Both thresholds are marked SCAFFOLD, pending E-1-H calibration. How much of
    the classification depends on values nobody has calibrated?
    """
    rng_seed = SEED + 2
    rows = []
    for tw, tb in [
        (THETA_WANG, THETA_BA),
        (0.60, 0.40),
        (0.80, 0.40),
        (0.70, 0.30),
        (0.70, 0.50),
    ]:
        rng = random.Random(rng_seed)
        c: Counter = Counter()
        for _ in range(n):
            c[classify(_traj(rng), theta_wang=tw, theta_ba=tb)["classification"]] += 1
        rows.append((tw, tb, {k: c[k] / n for k in ("Wang", "Ba", "Indeterminate")}))
    return rows


def hexie_balance(n: int) -> dict:
    """Same cheapest-possible check for the Five-Fold Hexie composite."""
    rng = random.Random(SEED + 3)
    above = 0
    for _ in range(n):
        s = HexieState(*(rng.random() for _ in range(5)))
        if hexie_five_fold(s)[0] >= 0.65:
            above += 1
    return {"n": n, "above_threshold": above, "fraction": above / n}


def ren_zheng_balance(n: int) -> dict:
    rng = random.Random(SEED + 4)
    above = sum(
        1
        for _ in range(n)
        if ren_zheng_score(GovernanceState(rng.random(), rng.random(), rng.random()))
        >= THETA_R_DEFAULT
    )
    return {"n": n, "above_floor": above, "fraction": above / n}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--n", type=int, default=100_000, help="samples (default 100000)")
    args = ap.parse_args(argv)
    n = args.n
    sens_n = max(2_000, n // 20)

    print(BAR)
    print("TIANXIA OPERATOR AUDIT — decision geometry, no external data")
    print(f"seed={SEED}  n={n:,}  (sensitivity subsample n={sens_n:,})")
    print(BAR)

    bal = class_balance(n)
    print("\n1. WANG DAO CLASS BALANCE over uniform [0,1]^4")
    for cls in ("Wang", "Ba", "Indeterminate"):
        c = bal["counts"][cls]
        print(f"   {cls:<15} {c:>8,}  {c / n:6.1%}")
    if bal["ba_total"]:
        share = bal["ba_via_gate"] / bal["ba_total"]
        print(f"   └─ of all Ba, {share:.1%} decided by the Ren Zheng gate alone,")
        print(f"      not by WD_score (θ_r={THETA_R_DEFAULT})")

    print("\n2. COMPONENT SENSITIVITY — decision-flip rate, one at a time")
    for name, rate in component_sensitivity(sens_n):
        bar = "█" * int(rate * 50)
        print(f"   {name:<22} {rate:6.2%}  {bar}")

    print("\n3. SHARED-TERM COUPLING")
    sc = shared_term_check()
    print(f"   R(s)     terms: {', '.join(sc['ren_zheng_terms'])}")
    print(f"   WD_score terms: {', '.join(sc['wang_dao_terms'])}")
    print(f"   shared:         {', '.join(sc['shared'])} — {sc['note']}")

    print("\n4. GATE CONSISTENCY PROBE")
    g = gate_consistency_probe()
    print(f"   declared R                    {g['declared_R']}")
    print(f"   max reachable R given F=0     {g['max_reachable_R_given_F0']}")
    print(f"   Ren Zheng gate passed         {g['gate_passed']}")
    print(f"   classification                {g['classification']}")
    if g["accepted_without_complaint"]:
        print("   ⚠ a trajectory with total coercion (F=0) and an arithmetically")
        print("     unreachable R was accepted as Wang-eligible without complaint")

    print("\n5. THRESHOLD SENSITIVITY (both marked SCAFFOLD)")
    print(f"   {'θ_wang':>7} {'θ_ba':>6} {'Wang':>8} {'Ba':>8} {'Indet':>8}")
    for tw, tb, fr in threshold_sensitivity(max(2_000, n // 10)):
        mark = "  ← current" if (tw, tb) == (THETA_WANG, THETA_BA) else ""
        print(
            f"   {tw:>7.2f} {tb:>6.2f} {fr['Wang']:>7.1%} "
            f"{fr['Ba']:>7.1%} {fr['Indeterminate']:>7.1%}{mark}"
        )

    print("\n6. OTHER OPERATOR THRESHOLDS")
    h = hexie_balance(n)
    r = ren_zheng_balance(n)
    print(f"   Five-Fold Hexie H₅ ≥ 0.65     {h['fraction']:6.1%} of input space")
    print(f"   Ren Zheng R(s) ≥ {THETA_R_DEFAULT}        {r['fraction']:6.1%} of input space")

    print("\n" + BAR)
    print("This audit measures internal decision geometry ONLY.")
    print("It says NOTHING about whether these operators track real governance.")
    print("Only external data can say that, and none has been run. See")
    print("33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md for why that matters.")
    print(BAR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
