"""
datong_gradient.py — T-5 TIANXIA Operator Implementation
Datong (大同) as the long-cycle telos gradient in HARMONIA value-space.

Classical source: Liji, Liyun chapter; Kang Youwei, Datong Shu (1902)
  "When the Great Way prevails, all under heaven is held in common."
Framework mapping: HARMONIA extended value-space — long-cycle architectural direction D-hat
Spec: CODEX_AURA_PRIME/32_TIANXIA/DATONG_GRADIENT.md (T-5)
Status: [SCAFFOLD] — formal structure declared; C, C_common, L operationalisation
  per deployment context pending empirical validation.
Negative space: does NOT claim D-hat is universal, that long-cycle outcomes are
  predictable, or that commons-holding is universally appropriate.
  Does NOT score real governments or policy systems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Extended value-space  (T-5 §IV Definition 1)
# ---------------------------------------------------------------------------

# Canonical dimension indices in the 7-dim extended value-space V
DIM_F_AVG = 0          # per-agent flourishing (mean across agents)
DIM_PHI_T = 1          # Tianxia potential (mutualistic coupling, T-1)
DIM_AURA_SHI = 2       # Shi-corrected AURA alignment (T-3)
DIM_D_INTEGRITY = 3    # integrity-debt (T-4); Datong direction is NEGATIVE here
DIM_CAP_DIST = 4       # capability distribution C — higher = more equal = better
DIM_COMMONS = 5        # common-resource health C_common
DIM_LONG_CYCLE = 6     # long-cycle stability L

N_DIMS = 7

# Raw Datong direction weights (T-5 §IV Definition 2)
# Positive on: F_avg, Phi_T, AURA_shi, capability_dist, commons, long_cycle
# Negative on: D_integrity (lower debt is better)
_D_RAW = np.array([1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0], dtype=float)


@dataclass
class DatongValueState:
    """
    A point in the extended value-space V (T-5 §IV Def 1).

    All values are dimensionless normalised scores unless noted.
    Negative-space: the operationalisation of capability_dist, commons_health,
    and long_cycle_stability is deployment-specific. Default values of 0.5
    signal unmeasured, not neutral.
    """
    f_avg: float = 0.5           # mean per-agent flourishing, [0, 1]
    phi_T: float = 0.5           # Tianxia potential, [0, 1]
    aura_shi: float = 0.5        # Shi-corrected AURA, [0, 1]
    d_integrity: float = 0.5     # integrity-debt, [0, 1]; lower is better
    capability_dist: float = 0.5 # capability distribution, [0, 1]; higher=more equal
    commons_health: float = 0.5  # common-resource health, [0, 1]
    long_cycle_stability: float = 0.5  # long-cycle stability, [0, 1]

    def to_array(self) -> np.ndarray:
        return np.array([
            self.f_avg,
            self.phi_T,
            self.aura_shi,
            self.d_integrity,
            self.capability_dist,
            self.commons_health,
            self.long_cycle_stability,
        ], dtype=float)

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "DatongValueState":
        if arr.shape != (N_DIMS,):
            raise ValueError(f"Array must have {N_DIMS} elements; got {arr.shape}")
        return cls(*arr.tolist())


# ---------------------------------------------------------------------------
# Datong direction  (T-5 §IV Definition 2)
# ---------------------------------------------------------------------------

def datong_direction(weights: Sequence[float] | None = None) -> np.ndarray:
    """
    D-hat — unit vector in value-space pointing toward Datong.  (Def 2)

    Default equal weighting across all seven dimensions; deployments may
    supply custom weights. Re-weighting is itself a Datong-relevant choice
    that should be recorded in the architectural register.

    Negative space: D-hat is not universal — different domains may calibrate
    it differently. This function returns the structural default.
    """
    if weights is None:
        raw = _D_RAW.copy()
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != (N_DIMS,):
            raise ValueError(f"weights must have {N_DIMS} elements; got {w.shape}")
        raw = _D_RAW * np.abs(w)  # weights scale magnitude, signs fixed by D_RAW signs
    norm = np.linalg.norm(raw)
    if norm < 1e-12:
        raise ValueError("datong_direction: zero-norm direction; check weights")
    return raw / norm


def datong_projection(
    delta_A: Sequence[float] | np.ndarray,
    d_hat: np.ndarray | None = None,
) -> float:
    """
    Pi_D(delta_A) = grad_A . D-hat — directional derivative of architectural
    change delta_A along Datong direction.  (Def 3)

    > 0  Datong-aligned choice
    = 0  Datong-neutral
    < 0  Datong-degrading

    delta_A is a change-vector in extended value-space (same dimensionality).
    Positive components mean dimension improves; negative means it degrades.
    For D_integrity (dim 3), improvement means decrease; the D-hat sign handles this.
    """
    if d_hat is None:
        d_hat = datong_direction()
    da = np.asarray(delta_A, dtype=float)
    if da.shape != (N_DIMS,):
        raise ValueError(f"delta_A must have {N_DIMS} elements; got {da.shape}")
    return float(np.dot(da, d_hat))


def gradient_magnitude(state: DatongValueState, d_hat: np.ndarray | None = None) -> float:
    """
    Distance of current state from the Datong ideal along D-hat.

    Measures how far the current state is from the maximum-Datong corner
    of value-space. A value close to 0 means the state is already aligned;
    a large value means substantial distance remains.

    Note: this is a distance metric, not a score — lower does not mean worse,
    higher does not mean better. It indicates work remaining.
    """
    if d_hat is None:
        d_hat = datong_direction()
    ideal = np.where(_D_RAW > 0, 1.0, 0.0)  # max on positive dims, min on negative dims
    current = state.to_array()
    diff = ideal - current
    return float(np.dot(diff, d_hat))


def is_datong_coherent(
    delta_A: Sequence[float] | np.ndarray,
    floors: Sequence[float] | None = None,
    d_hat: np.ndarray | None = None,
) -> tuple[bool, dict]:
    """
    Check whether an architectural choice delta_A is Datong-coherent.  (Def 4)

    Three conditions (all must hold):
      1. Pi_D(delta_A) >= 0  — non-degrading on Datong direction
      2. No dimension drops below its floor (no race-to-the-bottom equality)
      3. Short-cycle and long-cycle projections are both non-negative
         (here approximated: long_cycle component of delta_A must be >= 0)

    floors: minimum allowable delta per dimension (default all 0.0 — no decrease allowed
            on any dimension except integrity-debt, which may decrease).

    Returns (is_coherent, diagnostics_dict).
    """
    if d_hat is None:
        d_hat = datong_direction()
    da = np.asarray(delta_A, dtype=float)

    projection = datong_projection(da, d_hat)
    cond1 = projection >= 0.0

    if floors is None:
        # Default floors: all dimensions may not decrease, except D_integrity may decrease
        default_floors = np.zeros(N_DIMS)
        default_floors[DIM_D_INTEGRITY] = -np.inf  # integrity-debt decreasing is good
        fl = default_floors
    else:
        fl = np.asarray(floors, dtype=float)
    cond2 = bool(np.all(da >= fl))

    cond3 = da[DIM_LONG_CYCLE] >= 0.0  # long-cycle stability must not degrade

    return (cond1 and cond2 and cond3), {
        "projection": projection,
        "cond1_non_degrading": cond1,
        "cond2_no_floor_violation": cond2,
        "cond3_long_cycle_stable": cond3,
    }


def datong_trajectory(projections: Sequence[float]) -> float:
    """
    T_D(t) = sum of Pi_D(delta_A_tau) over all choices up to t.  (Def 3)

    Positive trajectory indicates cumulative Datong-aligned architectural progress.
    Negative trajectory indicates drift away from Datong telos.
    """
    return float(sum(projections))


# ---------------------------------------------------------------------------
# Convenience composite
# ---------------------------------------------------------------------------

@dataclass
class DatongEvaluation:
    """Complete Datong evaluation for one architectural choice."""
    delta_A: np.ndarray
    d_hat: np.ndarray
    projection: float
    is_coherent: bool
    diagnostics: dict


def evaluate(
    delta_A: Sequence[float] | np.ndarray,
    weights: Sequence[float] | None = None,
) -> DatongEvaluation:
    """Single-call interface for a complete Datong evaluation."""
    d_hat = datong_direction(weights)
    proj = datong_projection(delta_A, d_hat)
    coherent, diag = is_datong_coherent(delta_A, d_hat=d_hat)
    return DatongEvaluation(
        delta_A=np.asarray(delta_A, dtype=float),
        d_hat=d_hat,
        projection=proj,
        is_coherent=coherent,
        diagnostics=diag,
    )


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

def _assert_close(a: float, b: float, tol: float = 1e-6, label: str = "") -> None:
    if abs(a - b) > tol:
        raise AssertionError(f"FAIL [{label}]: {a} != {b} (tol={tol})")


def _assert_true(condition: bool, label: str = "") -> None:
    if not condition:
        raise AssertionError(f"FAIL [{label}]")


# ---------------------------------------------------------------------------
# Self-tests — reproduce Proposition 5 (T-5 §V)
# ---------------------------------------------------------------------------

def test_datong_direction_is_unit_vector() -> None:
    """D-hat is a unit vector."""
    d = datong_direction()
    _assert_close(float(np.linalg.norm(d)), 1.0, label="D-hat is unit vector")
    print("PASS  test_datong_direction_is_unit_vector")


def test_datong_direction_signs() -> None:
    """D-hat is positive on improving dims, negative on D_integrity."""
    d = datong_direction()
    for dim in [DIM_F_AVG, DIM_PHI_T, DIM_AURA_SHI, DIM_CAP_DIST, DIM_COMMONS, DIM_LONG_CYCLE]:
        _assert_true(d[dim] > 0.0, label=f"D-hat[{dim}] > 0")
    _assert_true(d[DIM_D_INTEGRITY] < 0.0, label="D-hat[D_integrity] < 0")
    print("PASS  test_datong_direction_signs")


def test_proposition_5_local_equivalent_datong_divergent() -> None:
    """
    Reproduces Proposition 5 (T-5 §V): two policies with identical local-operator
    effects that project differently onto the Datong direction.

    Policy A (deep personalisation):
      - Identical local gains: F_avg +0.3, Phi_T +0.2, AURA_shi +0.2, D_integrity -0.1
      - Commons-degrading: capability_dist -0.4, commons_health -0.5, long_cycle -0.3

    Policy B (shared-baseline):
      - Identical local gains: same F_avg, Phi_T, AURA_shi, D_integrity
      - Commons-strengthening: capability_dist +0.2, commons_health +0.3, long_cycle +0.2

    Expected: Pi_D(A) < 0 < Pi_D(B); local operators cannot distinguish them.
    """
    d_hat = datong_direction()

    # Policy A: deep personalisation — fragments commons, concentrates capability
    delta_A = np.array([+0.3, +0.2, +0.2, -0.1, -0.4, -0.5, -0.3])

    # Policy B: shared-baseline — same local gains, strengthens commons
    delta_B = np.array([+0.3, +0.2, +0.2, -0.1, +0.2, +0.3, +0.2])

    proj_A = datong_projection(delta_A, d_hat)
    proj_B = datong_projection(delta_B, d_hat)

    # 1. Local operators see the same: F_avg, Phi_T, AURA_shi, D_integrity are identical
    _assert_close(delta_A[DIM_F_AVG], delta_B[DIM_F_AVG], label="F_avg identical (A vs B)")
    _assert_close(delta_A[DIM_PHI_T], delta_B[DIM_PHI_T], label="Phi_T identical (A vs B)")
    _assert_close(delta_A[DIM_AURA_SHI], delta_B[DIM_AURA_SHI], label="AURA_shi identical (A vs B)")
    _assert_close(delta_A[DIM_D_INTEGRITY], delta_B[DIM_D_INTEGRITY], label="D_integrity identical (A vs B)")

    # 2. Datong diverges: A is degrading, B is aligned
    _assert_true(proj_A < 0.0, label="Pi_D(A) < 0 — commons-degrading policy Datong-negative")
    _assert_true(proj_B > 0.0, label="Pi_D(B) > 0 — commons-strengthening policy Datong-positive")
    _assert_true(proj_B > proj_A, label="Pi_D(B) > Pi_D(A)")

    print(
        "PASS  test_proposition_5_local_equivalent_datong_divergent\n"
        f"      Pi_D(Policy A) = {proj_A:+.4f}  [deep personalisation, commons-degrading]\n"
        f"      Pi_D(Policy B) = {proj_B:+.4f}  [shared-baseline, commons-strengthening]\n"
        f"      Local-operator deltas (F_avg, Phi_T, AURA_shi, D_integrity) are identical in both."
    )


def test_datong_coherence_conditions() -> None:
    """Datong coherence requires all three conditions simultaneously."""
    d_hat = datong_direction()

    # Aligned + no floor violations + long-cycle stable — coherent
    aligned_full = np.array([+0.2, +0.1, +0.1, -0.1, +0.1, +0.1, +0.1])
    coherent, diag = is_datong_coherent(aligned_full, d_hat=d_hat)
    _assert_true(coherent, label="aligned_full is Datong-coherent")

    # Aligned on Datong direction BUT long-cycle unstable — not coherent
    aligned_but_lc_degrading = np.array([+0.3, +0.2, +0.2, -0.1, +0.2, +0.3, -0.2])
    coherent2, diag2 = is_datong_coherent(aligned_but_lc_degrading, d_hat=d_hat)
    _assert_true(not diag2["cond3_long_cycle_stable"],
                 label="long-cycle-degrading fails cond3")

    # Equality-collapse: caps F_avg but good on commons (cond2 floor violation)
    equality_collapse = np.array([-0.1, +0.1, +0.1, -0.1, +0.3, +0.2, +0.1])
    coherent3, diag3 = is_datong_coherent(equality_collapse, d_hat=d_hat)
    _assert_true(not diag3["cond2_no_floor_violation"],
                 label="equality-collapse fails cond2")

    print("PASS  test_datong_coherence_conditions")


def test_trajectory_alignment() -> None:
    """Positive trajectory is Datong-aligned arc; negative is drift."""
    positive = [0.3, 0.4, 0.2, 0.5, 0.1]
    negative = [-0.2, -0.4, -0.1, -0.3]
    _assert_true(datong_trajectory(positive) > 0.0, label="positive trajectory")
    _assert_true(datong_trajectory(negative) < 0.0, label="negative trajectory")
    _assert_close(datong_trajectory([]), 0.0, label="empty trajectory")
    print("PASS  test_trajectory_alignment")


def test_neutral_choice() -> None:
    """Zero architectural change produces zero projection — Datong-neutral."""
    delta_zero = np.zeros(N_DIMS)
    proj = datong_projection(delta_zero)
    _assert_close(proj, 0.0, label="zero change -> zero projection")
    print("PASS  test_neutral_choice")


def test_custom_weights() -> None:
    """Custom weights re-scale but preserve D-hat sign structure."""
    weights = [2.0, 1.0, 1.0, 1.5, 3.0, 2.0, 1.0]
    d_hat = datong_direction(weights)
    _assert_close(float(np.linalg.norm(d_hat)), 1.0, label="custom-weighted D-hat is unit")
    _assert_true(d_hat[DIM_D_INTEGRITY] < 0.0, label="integrity-debt still negative with custom weights")
    print("PASS  test_custom_weights")


if __name__ == "__main__":
    test_datong_direction_is_unit_vector()
    test_datong_direction_signs()
    test_proposition_5_local_equivalent_datong_divergent()
    test_datong_coherence_conditions()
    test_trajectory_alignment()
    test_neutral_choice()
    test_custom_weights()
    print("\nAll datong_gradient self-tests passed.")
