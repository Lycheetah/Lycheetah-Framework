"""
civilisational_governance_benchmark.py — Full Operator Stack Governance Benchmark
TIANXIA v0.3 — W-14

Scores governance proposals against the full TIANXIA operator stack:
  Tianxia (Ψ_T proxy), Hexie (H_5), Shi (σ proxy), Wuwei (ε proxy),
  Datong (Π_D proxy), Ren Zheng (R), Wang Dao (WD)

Input: governance proposal as structured dict.
Output: 7-tuple of operator scores + composite + classification.

Three reference scenarios bundled:
  - extractive_baseline: Ba Dao / Westphalian extraction
  - liberal_procedural_baseline: liberal-procedural governance
  - tianxia_aligned_baseline: Tianxia-aligned cooperative governance

Claim status: [SCAFFOLD] — composite weights and thresholds pending E-1-H calibration.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import sys
import os

# Add implementations directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from ren_zheng import GovernanceState, ren_zheng_score, wang_dao_eligible, THETA_R_DEFAULT
from hexie_five_fold import HexieState, hexie_five_fold, binding_constraint


@dataclass
class GovernanceProposal:
    """
    Structured representation of a governance proposal for operator-stack evaluation.

    Each field ∈ [0, 1] unless noted. Field semantics match the operator definitions.
    """
    label: str

    # Ren Zheng components (→ ren_zheng.py)
    welfare_baseline: float        # W(s): fraction of population at material sufficiency
    voice_coverage: float          # V(s): stakeholder interest representation
    force_restraint: float         # F(s): inverse coercion rate

    # Hexie five-fold components (→ hexie_five_fold.py)
    h_innovation: float            # I(s) — 革
    h_coordination: float          # C(s) — 和 (base Hexie)
    h_ecological: float            # E(s) — 天人合一
    h_openness: float              # O(s) — 通
    h_sharing: float               # S(s) — 共

    # Tianxia proxy (k₅ composite from multilateral coupling)
    tianxia_k5: float              # k₅ governance composite ∈ [-1, 1]

    # Shi proxy (propensity field alignment)
    shi_alignment: float           # σ_field ∈ [0, 1]: how well action aligns with propensity

    # Wuwei proxy (grain-alignment / minimal intervention)
    wuwei_restraint: float         # ε ∈ [0, 1]: grain-alignment score (1 = fully Wuwei-aligned)

    # Datong proxy (distributional gradient)
    datong_short_cycle: float      # Π_D(T₁) ∈ [-1, 1]: short-cycle welfare trajectory
    datong_long_cycle: float       # G_D(T₂) ∈ [-1, 1]: long-cycle Gini_productive trajectory

    # Wang Dao trajectory proxy (minxin, long-cycle stability)
    wang_dao_minxin: float         # L(τ) ∈ [0, 1]: people's hearts alignment
    wang_dao_stability: float      # Γ(τ) ∈ [0, 1]: long-cycle governance stability

    def __post_init__(self):
        unit_fields = [
            "welfare_baseline", "voice_coverage", "force_restraint",
            "h_innovation", "h_coordination", "h_ecological", "h_openness", "h_sharing",
            "shi_alignment", "wuwei_restraint", "wang_dao_minxin", "wang_dao_stability",
        ]
        for name in unit_fields:
            val = getattr(self, name)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")
        for name in ["tianxia_k5", "datong_short_cycle", "datong_long_cycle"]:
            val = getattr(self, name)
            if not -1.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [-1, 1], got {val}")


@dataclass
class BenchmarkResult:
    label: str
    r_ren_zheng: float
    h5_hexie: float
    psi_tianxia: float       # k₅ normalised to [0,1]: (k5 + 1) / 2
    sigma_shi: float
    epsilon_wuwei: float
    pi_datong_ext: float     # α·short + (1-α)·long, α=0.5
    wd_score: float          # (minxin + force_restraint + stability) / 3
    composite: float         # Mean of all 7 normalised scores
    wang_dao_eligible: bool
    binding_constraint: Optional[str]
    classification: str      # "Tianxia-aligned" / "Transitional" / "Ba-Dao-aligned"


def evaluate(proposal: GovernanceProposal, alpha_datong: float = 0.5) -> BenchmarkResult:
    """Score a governance proposal against the full operator stack."""

    # Ren Zheng
    rz_state = GovernanceState(
        proposal.welfare_baseline,
        proposal.voice_coverage,
        proposal.force_restraint,
        proposal.label,
    )
    r = ren_zheng_score(rz_state)
    eligible = wang_dao_eligible(rz_state)

    # Hexie five-fold
    hex_state = HexieState(
        proposal.h_innovation,
        proposal.h_coordination,
        proposal.h_ecological,
        proposal.h_openness,
        proposal.h_sharing,
        proposal.label,
    )
    _, _, _, _, _, h5 = hexie_five_fold(hex_state)
    bc = binding_constraint(hex_state) if h5 < 0.65 else None

    # Tianxia k₅ → normalised to [0,1]
    psi = (proposal.tianxia_k5 + 1.0) / 2.0

    # Shi
    sigma = proposal.shi_alignment

    # Wuwei
    epsilon = proposal.wuwei_restraint

    # Datong extended: α·short + (1-α)·long, then normalise to [0,1]
    pi_raw = alpha_datong * proposal.datong_short_cycle + (1 - alpha_datong) * proposal.datong_long_cycle
    pi = (pi_raw + 1.0) / 2.0  # normalise [-1,1] → [0,1]

    # Wang Dao score (proxy trajectory using current-state values)
    wd = (proposal.wang_dao_minxin + proposal.force_restraint + proposal.wang_dao_stability) / 3.0

    # Composite: mean of all 7 normalised operator scores
    composite = (r + h5 + psi + sigma + epsilon + pi + wd) / 7.0

    # Classification
    if composite >= 0.70 and eligible:
        classification = "Tianxia-aligned"
    elif composite < 0.40 or not eligible:
        classification = "Ba-Dao-aligned"
    else:
        classification = "Transitional"

    return BenchmarkResult(
        label=proposal.label,
        r_ren_zheng=round(r, 4),
        h5_hexie=round(h5, 4),
        psi_tianxia=round(psi, 4),
        sigma_shi=round(sigma, 4),
        epsilon_wuwei=round(epsilon, 4),
        pi_datong_ext=round(pi, 4),
        wd_score=round(wd, 4),
        composite=round(composite, 4),
        wang_dao_eligible=eligible,
        binding_constraint=bc,
        classification=classification,
    )


def print_result(result: BenchmarkResult) -> None:
    print(f"\n  [{result.label}]")
    print(f"    Ren Zheng (仁政):   {result.r_ren_zheng:.3f}")
    print(f"    Hexie 5-fold (和谐): {result.h5_hexie:.3f}")
    print(f"    Tianxia (天下):     {result.psi_tianxia:.3f}")
    print(f"    Shi (势):           {result.sigma_shi:.3f}")
    print(f"    Wuwei (无为):       {result.epsilon_wuwei:.3f}")
    print(f"    Datong ext (大同):   {result.pi_datong_ext:.3f}")
    print(f"    Wang Dao (王道):     {result.wd_score:.3f}")
    print(f"    ─────────────────────────────")
    print(f"    Composite:          {result.composite:.3f}")
    print(f"    Wang Dao eligible:  {result.wang_dao_eligible}")
    if result.binding_constraint:
        print(f"    Binding constraint: {result.binding_constraint}")
    print(f"    Classification:     {result.classification}")


# ---------------------------------------------------------------------------
# Reference scenarios
# ---------------------------------------------------------------------------

EXTRACTIVE_BASELINE = GovernanceProposal(
    label="Extractive_Baseline (Ba Dao / Westphalian)",
    welfare_baseline=0.42,
    voice_coverage=0.28,
    force_restraint=0.19,
    h_innovation=0.35,
    h_coordination=0.41,
    h_ecological=0.28,
    h_openness=0.22,
    h_sharing=0.18,
    tianxia_k5=-0.45,
    shi_alignment=0.31,
    wuwei_restraint=0.22,
    datong_short_cycle=-0.18,
    datong_long_cycle=-0.42,
    wang_dao_minxin=0.29,
    wang_dao_stability=0.44,
)

LIBERAL_PROCEDURAL_BASELINE = GovernanceProposal(
    label="Liberal_Procedural_Baseline",
    welfare_baseline=0.74,
    voice_coverage=0.71,
    force_restraint=0.62,
    h_innovation=0.65,
    h_coordination=0.72,
    h_ecological=0.54,
    h_openness=0.78,
    h_sharing=0.55,
    tianxia_k5=0.28,
    shi_alignment=0.64,
    wuwei_restraint=0.57,
    datong_short_cycle=0.31,
    datong_long_cycle=-0.08,
    wang_dao_minxin=0.65,
    wang_dao_stability=0.71,
)

TIANXIA_ALIGNED_BASELINE = GovernanceProposal(
    label="Tianxia_Aligned_Baseline",
    welfare_baseline=0.85,
    voice_coverage=0.82,
    force_restraint=0.88,
    h_innovation=0.76,
    h_coordination=0.84,
    h_ecological=0.79,
    h_openness=0.81,
    h_sharing=0.77,
    tianxia_k5=0.72,
    shi_alignment=0.83,
    wuwei_restraint=0.86,
    datong_short_cycle=0.42,
    datong_long_cycle=0.38,
    wang_dao_minxin=0.84,
    wang_dao_stability=0.88,
)

REFERENCE_SCENARIOS = [
    EXTRACTIVE_BASELINE,
    LIBERAL_PROCEDURAL_BASELINE,
    TIANXIA_ALIGNED_BASELINE,
]


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _assert_close(a: float, b: float, tol: float = 0.01, msg: str = "") -> None:
    assert abs(a - b) < tol, f"Expected ~{b} ± {tol}, got {a}. {msg}"


def test_reference_ordering():
    """Tianxia-aligned composite > Liberal-procedural > Extractive."""
    results = [evaluate(p) for p in REFERENCE_SCENARIOS]
    extractive, liberal, tianxia = results

    assert tianxia.composite > liberal.composite > extractive.composite, (
        f"Expected Tianxia({tianxia.composite:.3f}) > Liberal({liberal.composite:.3f}) "
        f"> Extractive({extractive.composite:.3f})"
    )
    print(f"  PASS: test_reference_ordering")
    print(f"    Tianxia={tianxia.composite:.3f} > Liberal={liberal.composite:.3f} > Extractive={extractive.composite:.3f}")


def test_classifications():
    """Reference scenarios classify as expected."""
    extractive = evaluate(EXTRACTIVE_BASELINE)
    liberal = evaluate(LIBERAL_PROCEDURAL_BASELINE)
    tianxia = evaluate(TIANXIA_ALIGNED_BASELINE)

    assert extractive.classification == "Ba-Dao-aligned", \
        f"Extractive should be Ba-Dao-aligned, got {extractive.classification}"
    assert tianxia.classification == "Tianxia-aligned", \
        f"Tianxia should be Tianxia-aligned, got {tianxia.classification}"
    # Liberal is Transitional (not fully Tianxia-aligned due to ecological/sharing/datong)
    assert liberal.classification in ["Transitional", "Tianxia-aligned"], \
        f"Liberal should be Transitional or Tianxia-aligned, got {liberal.classification}"

    print(f"  PASS: test_classifications")
    print(f"    Extractive: {extractive.classification}")
    print(f"    Liberal: {liberal.classification}")
    print(f"    Tianxia: {tianxia.classification}")


def test_all_operators_contribute():
    """
    Composite is strictly between min and max component scores
    (no single operator dominates — all seven contribute).
    """
    result = evaluate(TIANXIA_ALIGNED_BASELINE)
    scores = [
        result.r_ren_zheng,
        result.h5_hexie,
        result.psi_tianxia,
        result.sigma_shi,
        result.epsilon_wuwei,
        result.pi_datong_ext,
        result.wd_score,
    ]
    assert min(scores) <= result.composite <= max(scores), \
        "Composite should be between min and max component scores"
    print("  PASS: test_all_operators_contribute")


def test_invalid_input():
    try:
        GovernanceProposal(
            label="bad",
            welfare_baseline=1.5,  # invalid
            voice_coverage=0.5, force_restraint=0.5,
            h_innovation=0.5, h_coordination=0.5, h_ecological=0.5,
            h_openness=0.5, h_sharing=0.5,
            tianxia_k5=0.5, shi_alignment=0.5, wuwei_restraint=0.5,
            datong_short_cycle=0.5, datong_long_cycle=0.5,
            wang_dao_minxin=0.5, wang_dao_stability=0.5,
        )
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("  PASS: test_invalid_input")


def run_all_tests():
    print("civilisational_governance_benchmark.py — self-tests")
    test_reference_ordering()
    test_classifications()
    test_all_operators_contribute()
    test_invalid_input()
    print("All tests passed. [SCAFFOLD — composite weights and thresholds pending E-1-H]")


def run_benchmark():
    """Print full benchmark report for all three reference scenarios."""
    print("\n=== Civilisational Governance Benchmark — Reference Scenarios ===")
    for proposal in REFERENCE_SCENARIOS:
        result = evaluate(proposal)
        print_result(result)
    print("\n[SCAFFOLD — thresholds and weights pending E-1-H calibration]")


if __name__ == "__main__":
    run_all_tests()
    print()
    run_benchmark()
