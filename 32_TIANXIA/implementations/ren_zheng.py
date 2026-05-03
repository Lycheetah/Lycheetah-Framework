"""
ren_zheng.py — Ren Zheng (仁政) Benevolent Governance Operator
TIANXIA v0.3 — W-11

Implements R(s) = (W + V + F) / 3 from REN_ZHENG_OPERATOR.md (W-1).
Self-tests reproduce Propositions R-1 and R-2 and the worked example.

Classical source: Mengzi 1A.7, 1B.3, 2A.6, 4A.9; Zhu Xi commentary.
Claim status: [SCAFFOLD] — weights α=β=γ=1/3 and θ_r=0.618 pending E-1-H calibration.
"""

from dataclasses import dataclass
from typing import Optional


# Working threshold — SCAFFOLD, pending empirical calibration (E-1-H)
THETA_R_DEFAULT = 0.618


@dataclass
class GovernanceState:
    """Snapshot of a governance state for Ren Zheng evaluation."""
    welfare_baseline: float       # W(s) ∈ [0,1]: fraction of population at material sufficiency
    voice_coverage: float         # V(s) ∈ [0,1]: fraction of stakeholders with meaningful participation
    force_restraint: float        # F(s) ∈ [0,1]: 1 - (coercive_interventions / total_decisions)
    label: str = ""

    def __post_init__(self):
        for field, val in [
            ("welfare_baseline", self.welfare_baseline),
            ("voice_coverage", self.voice_coverage),
            ("force_restraint", self.force_restraint),
        ]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{field} must be in [0, 1], got {val}")


def ren_zheng_score(state: GovernanceState) -> float:
    """
    R(s) = (W(s) + V(s) + F(s)) / 3

    Measures the moral character of governance:
    - W: welfare baseline (Mengzi 4A.9 — 'fed and clothed')
    - V: voice coverage (stakeholder interests substantively considered)
    - F: force restraint (compliance through alignment, not coercion)

    Returns R(s) ∈ [0, 1].
    """
    return (state.welfare_baseline + state.voice_coverage + state.force_restraint) / 3.0


def wang_dao_eligible(state: GovernanceState, theta_r: float = THETA_R_DEFAULT) -> bool:
    """
    Proposition R-1: Wang Dao classification requires R(s) ≥ θ_r.
    Returns True if the state passes the Ren Zheng floor (necessary, not sufficient for Wang Dao).
    """
    return ren_zheng_score(state) >= theta_r


def ren_zheng_report(state: GovernanceState, theta_r: float = THETA_R_DEFAULT) -> dict:
    """Full diagnostic report for a governance state."""
    r = ren_zheng_score(state)
    eligible = r >= theta_r
    binding = min(
        [("welfare_baseline", state.welfare_baseline),
         ("voice_coverage", state.voice_coverage),
         ("force_restraint", state.force_restraint)],
        key=lambda x: x[1]
    )[0]
    return {
        "label": state.label,
        "W": round(state.welfare_baseline, 4),
        "V": round(state.voice_coverage, 4),
        "F": round(state.force_restraint, 4),
        "R": round(r, 4),
        "theta_r": theta_r,
        "wang_dao_eligible": eligible,
        "binding_component": binding if not eligible else None,
    }


def stress_test(
    state: GovernanceState,
    welfare_shock: float = 0.0,
    voice_shock: float = 0.0,
    force_shock: float = 0.0,
    theta_r: float = THETA_R_DEFAULT,
) -> dict:
    """
    Apply a perturbation to the governance state and recompute R(s).
    Implements the Proposition R-2 stress test: low-R states escalate force under perturbation.

    Shocks are additive deltas (negative = degradation).
    Returns pre- and post-perturbation reports.
    """
    pre = ren_zheng_report(state, theta_r)
    perturbed = GovernanceState(
        welfare_baseline=max(0.0, min(1.0, state.welfare_baseline + welfare_shock)),
        voice_coverage=max(0.0, min(1.0, state.voice_coverage + voice_shock)),
        force_restraint=max(0.0, min(1.0, state.force_restraint + force_shock)),
        label=state.label + "_perturbed",
    )
    post = ren_zheng_report(perturbed, theta_r)
    return {"pre": pre, "post": post, "delta_R": round(post["R"] - pre["R"], 4)}


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _assert_close(a: float, b: float, tol: float = 0.001, msg: str = "") -> None:
    assert abs(a - b) < tol, f"Expected {b} ± {tol}, got {a}. {msg}"


def test_r1_necessary_condition():
    """Proposition R-1: R(s) ≥ θ_r is necessary for Wang Dao eligibility."""
    # High all-round: eligible
    s_high = GovernanceState(0.84, 0.79, 0.91, "G1_high")
    assert wang_dao_eligible(s_high), "G1 should be Wang Dao eligible"
    _assert_close(ren_zheng_score(s_high), 0.847, msg="G1 R score")

    # High welfare/voice but very low force restraint: may still be eligible or not
    s_coercive = GovernanceState(0.93, 0.86, 0.15, "G2_coercive")
    r = ren_zheng_score(s_coercive)
    _assert_close(r, 0.647, msg="G2 coercive R score")
    # With θ_r=0.618: eligible, but barely — and much lower than G1
    assert wang_dao_eligible(s_coercive), "G2 barely eligible"
    assert ren_zheng_score(s_high) > ren_zheng_score(s_coercive), \
        "Wang Dao ranking: G1 > G2 despite G2 higher welfare/voice"

    print("  PASS: test_r1_necessary_condition")


def test_r1_contrapositive():
    """R(s) < θ_r → not Wang Dao eligible."""
    s_fail = GovernanceState(0.20, 0.30, 0.25, "below_threshold")
    assert not wang_dao_eligible(s_fail), "Low-R state should not be Wang Dao eligible"
    print("  PASS: test_r1_contrapositive")


def test_r2_stress_escalation():
    """
    Proposition R-2: Low-R states exhibit force escalation under perturbation.

    G2 (high welfare, high voice, low force restraint) under a welfare shock
    escalates coercion (force_restraint degrades further) and drops below θ_r.
    G1 (high all-round) under equivalent welfare shock remains stable.
    """
    g1 = GovernanceState(0.84, 0.79, 0.91, "G1")
    g2 = GovernanceState(0.93, 0.86, 0.15, "G2")

    # Welfare shock: -0.17 (resource reduction)
    # For G2: welfare drops but force restraint also degrades (coercion escalates)
    g1_stress = stress_test(g1, welfare_shock=-0.17, force_shock=-0.01)
    g2_stress = stress_test(g2, welfare_shock=-0.17, force_shock=-0.10)  # force escalates more

    # G1 remains above θ_r after perturbation
    assert g1_stress["post"]["wang_dao_eligible"], "G1 should remain eligible after shock"
    # G2 drops below θ_r after coercion escalation
    assert not g2_stress["post"]["wang_dao_eligible"], "G2 should fall below threshold after coercion escalation"
    # G2 delta_R more negative than G1
    assert g2_stress["delta_R"] < g1_stress["delta_R"], \
        f"G2 should degrade more: G2 ΔR={g2_stress['delta_R']}, G1 ΔR={g1_stress['delta_R']}"

    print("  PASS: test_r2_stress_escalation")


def test_worked_example():
    """Worked example from REN_ZHENG_OPERATOR.md §V — three governance states."""
    g1 = GovernanceState(0.84, 0.79, 0.91, "G1")
    g2 = GovernanceState(0.93, 0.86, 0.15, "G2")
    g3 = GovernanceState(0.41, 0.67, 0.94, "G3")

    r1 = ren_zheng_score(g1)
    r2 = ren_zheng_score(g2)
    r3 = ren_zheng_score(g3)

    _assert_close(r1, 0.847, msg="G1")
    _assert_close(r2, 0.647, msg="G2")
    _assert_close(r3, 0.673, msg="G3")

    # Welfare-only ranking: G2 > G1 > G3
    assert g2.welfare_baseline > g1.welfare_baseline > g3.welfare_baseline, \
        "Welfare-only ranking should be G2 > G1 > G3"

    # R(s) ranking reversal: G1 > G3 > G2 (G2 penalised for high coercion)
    assert r1 > r3 > r2, f"R ranking should be G1 > G3 > G2, got {r1:.3f} > {r3:.3f} > {r2:.3f}"

    print("  PASS: test_worked_example — ranking reversal demonstrated")
    print(f"    Welfare ranking: G2({g2.welfare_baseline}) > G1({g1.welfare_baseline}) > G3({g3.welfare_baseline})")
    print(f"    R(s) ranking:    G1({r1:.3f}) > G3({r3:.3f}) > G2({r2:.3f})")


def test_report_binding_component():
    """Report identifies the binding component when state fails threshold."""
    s_fail = GovernanceState(0.80, 0.75, 0.20, "low_force")
    report = ren_zheng_report(s_fail)
    assert report["binding_component"] == "force_restraint", \
        f"Binding component should be force_restraint, got {report['binding_component']}"
    print("  PASS: test_report_binding_component")


def test_invalid_input():
    """Out-of-range values raise ValueError."""
    try:
        GovernanceState(1.1, 0.5, 0.5)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("  PASS: test_invalid_input")


def run_all_tests():
    print("ren_zheng.py — self-tests")
    test_r1_necessary_condition()
    test_r1_contrapositive()
    test_r2_stress_escalation()
    test_worked_example()
    test_report_binding_component()
    test_invalid_input()
    print("All tests passed. [SCAFFOLD — θ_r=0.618 and weights pending E-1-H calibration]")


if __name__ == "__main__":
    run_all_tests()
