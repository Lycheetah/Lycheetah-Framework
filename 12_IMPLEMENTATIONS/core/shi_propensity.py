"""
shi_propensity.py — T-3 TIANXIA Operator Implementation
Shi (势) as a propensity-field reformulation of AURA scoring.

Classical source: Sun Tzu, Sunzi Bingfa ch.5; François Jullien,
  The Propensity of Things: Toward a History of Efficacy in China (1995)
Framework mapping: AURA context-sensitivity layer
  AURA_shi(O, C) = AURA_hexie(O, C) × g(σ(O,C), ‖Σ(C)‖)
Spec: CODEX_AURA_PRIME/32_TIANXIA/SHI_PROPENSITY_FIELD.md (T-3)
Status: [SCAFFOLD] — formal structure declared; propensity-field
  estimation per deployment context pending empirical operationalisation.
Negative space: does NOT score real governments or predict policy outcomes.
  Inputs are framework-internal state variables.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Context space  (T-3 §IV Definition 1)
# ---------------------------------------------------------------------------

@dataclass
class ShiContext:
    """
    A point in context-space ℂ — six illustrative coordinates from T-3 §IV Def 1.

    All values ∈ [0, 1]:
      stakes            0=low ↔ 1=high
      reversibility     0=irreversible ↔ 1=undoable
      user_expertise    0=novice ↔ 1=expert
      register          0=casual ↔ 1=formal
      temporal_horizon  0=immediate ↔ 1=generational
      action_readiness  0=deliberating ↔ 1=poised

    Callers may omit unused dimensions; defaults to 0.5 (neutral).
    """
    stakes: float = 0.5
    reversibility: float = 0.5
    user_expertise: float = 0.5
    register: float = 0.5
    temporal_horizon: float = 0.5
    action_readiness: float = 0.5

    def to_array(self) -> np.ndarray:
        return np.array([
            self.stakes,
            self.reversibility,
            self.user_expertise,
            self.register,
            self.temporal_horizon,
            self.action_readiness,
        ], dtype=float)

    @property
    def dim(self) -> int:
        return 6


# ---------------------------------------------------------------------------
# Core Shi functions  (T-3 §IV Definitions 2–5)
# ---------------------------------------------------------------------------

def propensity_field(
    context: ShiContext,
    propensity_vector: Sequence[float],
) -> np.ndarray:
    """
    Σ(C) — the propensity field at context C.  (Def 2)

    In live deployment Σ is estimated from trajectory data or domain expertise.
    Here it is supplied explicitly so tests are reproducible.

    Negative space: does NOT derive Σ analytically — takes the caller's estimate
    and enforces shape consistency with the context-space dimensionality.
    """
    sigma = np.asarray(propensity_vector, dtype=float)
    if sigma.shape != (context.dim,):
        raise ValueError(
            f"propensity_vector must have length {context.dim} "
            f"(context-space dimensionality); got {sigma.shape}"
        )
    return sigma


def intervention_vector(
    output_effect: Sequence[float],
    context: ShiContext,
) -> np.ndarray:
    """
    Δ_O(C) — marginal effect of output O on context C above intrinsic dynamics.  (Def 3)

    Negative space: does NOT estimate Δ_O from output text — the caller
    supplies it from domain annotation or estimation.
    """
    delta = np.asarray(output_effect, dtype=float)
    if delta.shape != (context.dim,):
        raise ValueError(
            f"output_effect must have length {context.dim}; got {delta.shape}"
        )
    return delta


def shi_alignment_score(
    delta_O: np.ndarray,
    sigma_C: np.ndarray,
    epsilon: float = 1e-9,
) -> float:
    """
    σ(O, C) = cosine similarity of intervention with propensity.  (Def 4)

    Range: [−1, 1]
      +1  output rides the propensity   (maximum grain-alignment)
       0  output orthogonal to propensity (neutral)
      −1  output forces against propensity (maximum forcing-cost)

    Convention: returns 0.0 when ‖Δ_O‖ ≈ 0 (negligible intervention).
    """
    norm_delta = np.linalg.norm(delta_O)
    norm_sigma = np.linalg.norm(sigma_C)
    if norm_delta < epsilon or norm_sigma < epsilon:
        return 0.0
    return float(np.dot(delta_O, sigma_C) / (norm_delta * norm_sigma + epsilon))


def propensity_strength(sigma_C: np.ndarray) -> float:
    """‖Σ(C)‖ — magnitude of the propensity at context C."""
    return float(np.linalg.norm(sigma_C))


def shi_modulator(
    sigma: float,
    norm_sigma: float,
    lambda_shi: float = 1.0,
    sigma_ref: float = 1.0,
) -> float:
    """
    g(σ, ‖Σ‖) = exp(λ_shi × σ × tanh(‖Σ‖ / Σ_ref))   (Def 5)

    Structural requirements verified by test_modulator_structural_requirements:
      g(0, ‖Σ‖) = 1       neutral alignment → no modulation
      g(1, ‖Σ‖) > 1       aligned riding → reward
      g(−1,‖Σ‖) < 1       forcing → penalty
      g(σ, 0)   = 1       absent propensity → no modulation
      monotone non-decreasing in σ for fixed ‖Σ‖

    λ_shi and Σ_ref are calibration parameters [SCAFFOLD].
    """
    return math.exp(lambda_shi * sigma * math.tanh(norm_sigma / sigma_ref))


def aura_shi(
    aura_hexie: float,
    sigma: float,
    norm_sigma: float,
    lambda_shi: float = 1.0,
    sigma_ref: float = 1.0,
) -> float:
    """
    AURA_shi(O, C) = AURA_hexie(O, C) × g(σ, ‖Σ‖)   (Def 5)

    Shi-corrected composite. Rewards grain-aligned outputs in strong-propensity
    contexts; penalises forcing actions.
    """
    return aura_hexie * shi_modulator(sigma, norm_sigma, lambda_shi, sigma_ref)


def trajectory_alignment(sigmas: Sequence[float]) -> float:
    """
    Time-average of σ(O_t, C_t) across a multi-turn trajectory.  (Def 6)

    > 0  Shi-aligned trajectory
    = 0  neutral
    < 0  drift-inducing trajectory

    A sequence of individually high-scoring outputs that collectively push
    context toward a degraded region will have negative trajectory_alignment
    even when per-snapshot AURA scores are positive.
    """
    if not sigmas:
        return 0.0
    return float(sum(sigmas) / len(sigmas))


# ---------------------------------------------------------------------------
# Convenience composite
# ---------------------------------------------------------------------------

@dataclass
class ShiEvaluation:
    """Complete Shi evaluation for one (output, context) pair."""
    context: ShiContext
    propensity: np.ndarray
    intervention: np.ndarray
    sigma: float
    norm_sigma: float
    modulator: float
    aura_hexie_input: float
    aura_shi_output: float


def evaluate(
    context: ShiContext,
    propensity_vector: Sequence[float],
    output_effect: Sequence[float],
    aura_hexie: float,
    lambda_shi: float = 1.0,
    sigma_ref: float = 1.0,
) -> ShiEvaluation:
    """Single-call interface for a complete Shi evaluation."""
    sigma_C = propensity_field(context, propensity_vector)
    delta_O = intervention_vector(output_effect, context)
    sig = shi_alignment_score(delta_O, sigma_C)
    ns = propensity_strength(sigma_C)
    g = shi_modulator(sig, ns, lambda_shi, sigma_ref)
    return ShiEvaluation(
        context=context,
        propensity=sigma_C,
        intervention=delta_O,
        sigma=sig,
        norm_sigma=ns,
        modulator=g,
        aura_hexie_input=aura_hexie,
        aura_shi_output=aura_hexie * g,
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
# Self-tests
# ---------------------------------------------------------------------------

def test_modulator_structural_requirements() -> None:
    """g satisfies the four structural requirements from T-3 §IV Def 5."""
    _assert_close(shi_modulator(0.0, 1.0), 1.0,
                  label="g(0,‖Σ‖=1)=1")
    _assert_close(shi_modulator(0.0, 5.0), 1.0,
                  label="g(0,‖Σ‖=5)=1")
    _assert_true(shi_modulator(1.0, 1.0) > 1.0,
                 label="g(+1,‖Σ‖>0)>1 — riding rewarded")
    _assert_true(shi_modulator(-1.0, 1.0) < 1.0,
                 label="g(−1,‖Σ‖>0)<1 — forcing penalised")
    _assert_close(shi_modulator(1.0, 0.0), 1.0, tol=1e-9,
                  label="g(+1,‖Σ‖=0)=1 — absent propensity")
    _assert_close(shi_modulator(-1.0, 0.0), 1.0, tol=1e-9,
                  label="g(−1,‖Σ‖=0)=1 — absent propensity")
    _assert_true(
        shi_modulator(0.5, 1.0) < shi_modulator(1.0, 1.0),
        label="g monotone non-decreasing in σ"
    )
    print("PASS  test_modulator_structural_requirements")


def test_proposition_3_context_divergence() -> None:
    """
    Reproduces Proposition 3 (T-3 §V): identical output O, different contexts
    C1/C2, Shi-corrected scores diverge; Hexie scores do not.

    Scenario (§V Sketch):
      O  — directive "submit now"; pushes context toward action.
      C1 — user poised at apex of preparation; Σ(C1) points toward action.
      C2 — user mid-deliberation; Σ(C2) points toward continued reflection.

    Context-space: 6-dim. Intervention and propensity vectors live in the
    action_readiness dimension (dim 5) for clarity.
    """
    C1 = ShiContext(
        stakes=0.5, reversibility=0.7, user_expertise=0.8,
        register=0.5, temporal_horizon=0.3, action_readiness=0.9,
    )
    sigma_C1 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.8]   # pointing toward action

    C2 = ShiContext(
        stakes=0.5, reversibility=0.7, user_expertise=0.8,
        register=0.5, temporal_horizon=0.3, action_readiness=0.2,
    )
    sigma_C2 = [0.0, 0.0, 0.0, 0.0, 0.0, -0.6]  # pointing toward reflection

    delta_O = [0.0, 0.0, 0.0, 0.0, 0.0, 0.7]     # same output, pushes toward action

    aura_hexie_val = 0.75  # content-blind score — identical for O in both contexts

    ev1 = evaluate(C1, sigma_C1, delta_O, aura_hexie_val)
    ev2 = evaluate(C2, sigma_C2, delta_O, aura_hexie_val)

    # 1. AURA_hexie is equal — context-blind scoring sees the same output
    _assert_close(ev1.aura_hexie_input, ev2.aura_hexie_input,
                  label="AURA_hexie(O,C1) = AURA_hexie(O,C2)")

    # 2. Propensities differ
    _assert_true(
        np.linalg.norm(ev1.propensity - ev2.propensity) > 0.1,
        label="‖Σ(C1) − Σ(C2)‖ > 0"
    )

    # 3. σ(O,C1) > 0 — aligned: directive rides the poised propensity
    _assert_true(ev1.sigma > 0.0, label="σ(O,C1) > 0  (aligned)")

    # 4. σ(O,C2) < 0 — forcing: directive against the reflecting propensity
    _assert_true(ev2.sigma < 0.0, label="σ(O,C2) < 0  (forcing)")

    # 5. AURA_shi diverges — C1 scores higher
    _assert_true(
        ev1.aura_shi_output > ev2.aura_shi_output,
        label="AURA_shi(O,C1) > AURA_shi(O,C2)"
    )

    print(
        "PASS  test_proposition_3_context_divergence\n"
        f"      sigma(O,C1) = {ev1.sigma:+.4f}   AURA_shi(O,C1) = {ev1.aura_shi_output:.4f}\n"
        f"      sigma(O,C2) = {ev2.sigma:+.4f}   AURA_shi(O,C2) = {ev2.aura_shi_output:.4f}\n"
        f"      AURA_hexie (both) = {aura_hexie_val:.4f}  "
        f"delta_AURA_shi = {ev1.aura_shi_output - ev2.aura_shi_output:.4f}"
    )


def test_neutral_intervention() -> None:
    """Zero-magnitude intervention → σ=0, g=1, AURA_shi=AURA_hexie."""
    ctx = ShiContext()
    ev = evaluate(
        ctx,
        propensity_vector=[0.0, 0.0, 0.0, 0.0, 0.0, 0.5],
        output_effect=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        aura_hexie=0.8,
    )
    _assert_close(ev.sigma, 0.0, label="σ=0 for zero intervention")
    _assert_close(ev.modulator, 1.0, label="g=1 for σ=0")
    _assert_close(ev.aura_shi_output, 0.8, label="AURA_shi=AURA_hexie neutral")
    print("PASS  test_neutral_intervention")


def test_absent_propensity() -> None:
    """Zero propensity → g=1 regardless of σ; Shi is silent."""
    ctx = ShiContext(action_readiness=0.5)
    ev = evaluate(
        ctx,
        propensity_vector=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        output_effect=[0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        aura_hexie=0.7,
    )
    _assert_close(ev.sigma, 0.0, label="σ=0 absent propensity")
    _assert_close(ev.modulator, 1.0, label="g=1 absent propensity")
    _assert_close(ev.aura_shi_output, 0.7, label="AURA_shi=AURA_hexie absent propensity")
    print("PASS  test_absent_propensity")


def test_trajectory_alignment() -> None:
    """Trajectory alignment: positive-mean aligned, negative-mean not."""
    _assert_true(trajectory_alignment([0.3, 0.5, 0.7, 0.4, 0.6]) > 0.0,
                 label="positive trajectory aligned")
    _assert_true(trajectory_alignment([-0.4, -0.1, -0.6, -0.2]) < 0.0,
                 label="negative trajectory not aligned")
    _assert_close(trajectory_alignment([0.5, -0.5, 0.3, -0.3]), 0.0, tol=1e-9,
                  label="neutral trajectory")
    print("PASS  test_trajectory_alignment")


def test_forcing_penalty_scales_with_propensity_strength() -> None:
    """
    Proposition 4 (T-3 §VI P-4): Shi-modulation magnitude scales with ‖Σ‖.
    Weak propensity → small correction; strong propensity → larger correction.
    """
    sigma_fixed = -1.0  # fully forcing

    g_weak = shi_modulator(sigma_fixed, norm_sigma=0.1)
    g_medium = shi_modulator(sigma_fixed, norm_sigma=1.0)
    g_strong = shi_modulator(sigma_fixed, norm_sigma=5.0)

    # All penalise (< 1), but penalty grows with ‖Σ‖
    _assert_true(g_weak < 1.0, label="weak propensity: forcing still penalised")
    _assert_true(g_weak > g_medium, label="penalty stronger at medium ‖Σ‖")
    _assert_true(g_medium > g_strong, label="penalty stronger at high ‖Σ‖")
    print("PASS  test_forcing_penalty_scales_with_propensity_strength")


if __name__ == "__main__":
    test_modulator_structural_requirements()
    test_proposition_3_context_divergence()
    test_neutral_intervention()
    test_absent_propensity()
    test_trajectory_alignment()
    test_forcing_penalty_scales_with_propensity_strength()
    print("\nAll shi_propensity self-tests passed.")
