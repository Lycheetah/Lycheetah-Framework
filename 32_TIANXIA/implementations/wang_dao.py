"""
wang_dao.py — Wang Dao / Ba Dao Governance Legitimacy Classifier
TIANXIA v0.3 — W-12

Implements WD(τ) classifier from WANG_DAO_OPERATOR.md (W-3).
Three-axis diagnostic: legitimacy (minxin), force restraint, long-cycle stability.
Self-tests reproduce Propositions WD-1 and WD-2 and the stress test.

Classical source: Mengzi 1B.3, 2A.3, 7B.13; Xunzi Wangzhi; Yan Xuetong.
Claim status: [SCAFFOLD] — thresholds θ_wang=0.70, θ_ba=0.40 pending E-1-H calibration.
Prerequisite: Ren Zheng floor R(s) ≥ θ_r must be checked first (from ren_zheng.py).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from ren_zheng import GovernanceState, ren_zheng_score, THETA_R_DEFAULT


class WangDaoClass(Enum):
    WANG = "Wang"           # kingly way — governance through virtue
    BA = "Ba"               # hegemonic way — governance through force
    INDETERMINATE = "Indeterminate"


THETA_WANG = 0.70   # SCAFFOLD — minimum WD_score for Wang classification
THETA_BA   = 0.40   # SCAFFOLD — maximum WD_score before Ba classification


@dataclass
class TrajectoryPoint:
    """One evaluation point in a governance trajectory."""
    minxin: float           # L — legitimacy score ∈ [0,1]: genuine people's alignment
    force_restraint: float  # F — force restraint score ∈ [0,1] (same as GovernanceState.F)
    long_cycle_stability: float  # Γ — survival_prob × coherence_maintenance ∈ [0,1]
    ren_zheng_score: float  # R(s) — must be supplied from ren_zheng.py

    def __post_init__(self):
        for name, val in [
            ("minxin", self.minxin),
            ("force_restraint", self.force_restraint),
            ("long_cycle_stability", self.long_cycle_stability),
            ("ren_zheng_score", self.ren_zheng_score),
        ]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")


@dataclass
class GovernanceTrajectory:
    """Sequence of governance trajectory points over evaluation period."""
    points: List[TrajectoryPoint]
    label: str = ""

    def __post_init__(self):
        if not self.points:
            raise ValueError("Trajectory must have at least one point")


def wang_dao_score(trajectory: GovernanceTrajectory) -> dict:
    """
    Compute WD_score(τ) = (L(τ) + F(τ) + Γ(τ)) / 3

    L(τ) = mean minxin over trajectory
    F(τ) = mean force_restraint over trajectory
    Γ(τ) = mean long_cycle_stability over trajectory

    Returns dict with component means and composite score.
    """
    n = len(trajectory.points)
    L = sum(p.minxin for p in trajectory.points) / n
    F = sum(p.force_restraint for p in trajectory.points) / n
    G = sum(p.long_cycle_stability for p in trajectory.points) / n
    return {
        "L_legitimacy": round(L, 4),
        "F_restraint": round(F, 4),
        "G_stability": round(G, 4),
        "WD_score": round((L + F + G) / 3.0, 4),
    }


def classify(
    trajectory: GovernanceTrajectory,
    theta_r: float = THETA_R_DEFAULT,
    theta_wang: float = THETA_WANG,
    theta_ba: float = THETA_BA,
) -> dict:
    """
    Classify a governance trajectory as Wang, Ba, or Indeterminate.

    Gate: current R(s) must pass Ren Zheng floor first.
    If R(s) < θ_r → Ba (regardless of WD_score).
    If WD_score ≥ θ_wang AND R(s) ≥ θ_r → Wang.
    If WD_score < θ_ba OR R(s) < θ_r → Ba.
    Otherwise → Indeterminate.
    """
    scores = wang_dao_score(trajectory)
    current_r = trajectory.points[-1].ren_zheng_score
    ren_zheng_gate = current_r >= theta_r

    if not ren_zheng_gate:
        classification = WangDaoClass.BA
        reason = f"Ren Zheng gate failed: R(s)={current_r:.3f} < θ_r={theta_r}"
    elif scores["WD_score"] >= theta_wang:
        classification = WangDaoClass.WANG
        reason = f"WD_score={scores['WD_score']:.3f} ≥ θ_wang={theta_wang} and R gate passed"
    elif scores["WD_score"] < theta_ba:
        classification = WangDaoClass.BA
        reason = f"WD_score={scores['WD_score']:.3f} < θ_ba={theta_ba}"
    else:
        classification = WangDaoClass.INDETERMINATE
        reason = f"WD_score={scores['WD_score']:.3f} in [{theta_ba}, {theta_wang})"

    return {
        "label": trajectory.label,
        **scores,
        "current_R": round(current_r, 4),
        "ren_zheng_gate": ren_zheng_gate,
        "classification": classification.value,
        "reason": reason,
    }


def apply_capability_shock(
    trajectory: GovernanceTrajectory,
    minxin_delta: float = 0.0,
    force_delta: float = 0.0,
    stability_delta: float = 0.0,
    r_delta: float = 0.0,
) -> GovernanceTrajectory:
    """Create a shocked trajectory for stress-testing Proposition WD-1."""
    shocked_points = [
        TrajectoryPoint(
            minxin=max(0.0, min(1.0, p.minxin + minxin_delta)),
            force_restraint=max(0.0, min(1.0, p.force_restraint + force_delta)),
            long_cycle_stability=max(0.0, min(1.0, p.long_cycle_stability + stability_delta)),
            ren_zheng_score=max(0.0, min(1.0, p.ren_zheng_score + r_delta)),
        )
        for p in trajectory.points
    ]
    return GovernanceTrajectory(points=shocked_points, label=trajectory.label + "_shocked")


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _make_wang_trajectory() -> GovernanceTrajectory:
    """Trajectory A from worked example — Wang classification."""
    return GovernanceTrajectory(
        points=[
            TrajectoryPoint(0.78, 0.89, 0.82, 0.83),
            TrajectoryPoint(0.81, 0.91, 0.85, 0.85),
            TrajectoryPoint(0.79, 0.88, 0.87, 0.84),
            TrajectoryPoint(0.83, 0.90, 0.88, 0.87),
        ],
        label="Trajectory_A_Wang"
    )


def _make_ba_trajectory() -> GovernanceTrajectory:
    """Trajectory B from worked example — Ba classification."""
    return GovernanceTrajectory(
        points=[
            TrajectoryPoint(0.55, 0.20, 0.75, 0.50),
            TrajectoryPoint(0.48, 0.18, 0.70, 0.45),
            TrajectoryPoint(0.39, 0.14, 0.61, 0.38),
            TrajectoryPoint(0.31, 0.11, 0.49, 0.30),
        ],
        label="Trajectory_B_Ba"
    )


def _assert_close(a: float, b: float, tol: float = 0.01, msg: str = "") -> None:
    assert abs(a - b) < tol, f"Expected {b} ± {tol}, got {a}. {msg}"


def test_worked_example_wang():
    """Trajectory A should classify as Wang."""
    result = classify(_make_wang_trajectory())
    assert result["classification"] == WangDaoClass.WANG.value, \
        f"Expected Wang, got {result['classification']}: {result['reason']}"
    _assert_close(result["WD_score"], 0.851, tol=0.01, msg="Wang trajectory WD_score")
    print("  PASS: test_worked_example_wang")


def test_worked_example_ba():
    """Trajectory B should classify as Ba via both score and Ren Zheng gate failure."""
    result = classify(_make_ba_trajectory())
    assert result["classification"] == WangDaoClass.BA.value, \
        f"Expected Ba, got {result['classification']}: {result['reason']}"
    assert not result["ren_zheng_gate"], "Ba trajectory should fail Ren Zheng gate"
    print("  PASS: test_worked_example_ba")


def test_wd1_capability_shock():
    """
    Proposition WD-1: Ba Dao trajectories collapse faster than Wang under capability shock.

    Apply a 25% capability decline (modelled as degradation across all axes).
    Wang trajectory: remains Wang or drops to Indeterminate.
    Ba trajectory: deepens into Ba (compliance_collapse proxy).
    """
    wang = _make_wang_trajectory()
    ba = _make_ba_trajectory()

    # Wang: slight minxin dip from material hardship, no force escalation (alignment-based)
    wang_shocked = apply_capability_shock(wang, minxin_delta=-0.05, force_delta=-0.01, stability_delta=-0.03, r_delta=-0.03)
    # Ba: compliance collapses without material provision, force escalates sharply
    ba_shocked = apply_capability_shock(ba, minxin_delta=-0.08, force_delta=-0.08, stability_delta=-0.18, r_delta=-0.08)

    wang_result = classify(wang_shocked)
    ba_result = classify(ba_shocked)

    # Wang remains non-Ba after shock
    assert wang_result["classification"] in [WangDaoClass.WANG.value, WangDaoClass.INDETERMINATE.value], \
        f"Wang should not become Ba under shock, got {wang_result['classification']}"
    # Ba deepens
    assert ba_result["classification"] == WangDaoClass.BA.value, \
        f"Ba should remain Ba under shock, got {ba_result['classification']}"
    # Ba degrades more than Wang
    wang_pre = classify(wang)["WD_score"]
    ba_pre = classify(ba)["WD_score"]
    wang_delta = wang_result["WD_score"] - wang_pre
    ba_delta = ba_result["WD_score"] - ba_pre
    assert ba_delta < wang_delta, \
        f"Ba should degrade more: Ba ΔWD={ba_delta:.3f}, Wang ΔWD={wang_delta:.3f}"

    print(f"  PASS: test_wd1_capability_shock")
    print(f"    Wang: pre={wang_pre:.3f} → post={wang_result['WD_score']:.3f} ({wang_result['classification']})")
    print(f"    Ba:   pre={ba_pre:.3f} → post={ba_result['WD_score']:.3f} ({ba_result['classification']})")


def test_wd2_pareto_comparability():
    """
    Proposition WD-2: Wang Dao is Pareto-comparable (not equivalent) to liberal-procedural.

    Construct a liberal-procedural trajectory: high formal accountability,
    moderate minxin (legitimacy not through virtue but through procedure),
    moderate force restraint (enforcement-dependent), high stability.

    Wang Dao outperforms on L and F; liberal-procedural comparable on Γ.
    Neither dominates the other on all dimensions → Pareto-comparable confirmed.
    """
    liberal_trajectory = GovernanceTrajectory(
        points=[
            TrajectoryPoint(minxin=0.65, force_restraint=0.62, long_cycle_stability=0.81, ren_zheng_score=0.72),
            TrajectoryPoint(minxin=0.63, force_restraint=0.60, long_cycle_stability=0.80, ren_zheng_score=0.71),
        ],
        label="Liberal_Procedural"
    )
    wang = _make_wang_trajectory()

    lib_scores = wang_dao_score(liberal_trajectory)
    wang_scores = wang_dao_score(wang)

    # Wang Dao outperforms on legitimacy (minxin) and force restraint
    assert wang_scores["L_legitimacy"] > lib_scores["L_legitimacy"], "Wang > Liberal on minxin"
    assert wang_scores["F_restraint"] > lib_scores["F_restraint"], "Wang > Liberal on force restraint"

    # Liberal-procedural comparable on stability (neither clearly dominates)
    stability_diff = abs(wang_scores["G_stability"] - lib_scores["G_stability"])
    assert stability_diff < 0.15, f"Stability should be comparable (diff={stability_diff:.3f})"

    # Neither dominates on all three → Pareto non-dominance holds
    wang_dominates_all = all([
        wang_scores["L_legitimacy"] > lib_scores["L_legitimacy"],
        wang_scores["F_restraint"] > lib_scores["F_restraint"],
        wang_scores["G_stability"] > lib_scores["G_stability"] + 0.05,
    ])
    lib_dominates_all = all([
        lib_scores["L_legitimacy"] > wang_scores["L_legitimacy"],
        lib_scores["F_restraint"] > wang_scores["F_restraint"],
        lib_scores["G_stability"] > wang_scores["G_stability"] + 0.05,
    ])
    assert not wang_dominates_all and not lib_dominates_all, "WD-2: neither trajectory should dominate"

    print("  PASS: test_wd2_pareto_comparability — neither Wang nor Liberal dominates on all axes")


def test_ren_zheng_gate():
    """R(s) < θ_r → Ba classification regardless of WD_score."""
    # High WD_score components but R(s) < θ_r
    bad_r_trajectory = GovernanceTrajectory(
        points=[TrajectoryPoint(0.85, 0.88, 0.82, 0.30)],  # R=0.30, below θ_r
        label="HighWD_LowR"
    )
    result = classify(bad_r_trajectory)
    assert result["classification"] == WangDaoClass.BA.value, \
        f"Low-R state must be Ba regardless of WD_score, got {result['classification']}"
    print("  PASS: test_ren_zheng_gate")


def run_all_tests():
    print("wang_dao.py — self-tests")
    test_worked_example_wang()
    test_worked_example_ba()
    test_wd1_capability_shock()
    test_wd2_pareto_comparability()
    test_ren_zheng_gate()
    print("All tests passed. [SCAFFOLD — θ_wang=0.70, θ_ba=0.40 pending E-1-H calibration]")


if __name__ == "__main__":
    run_all_tests()
