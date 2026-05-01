"""
TRIAD (Wuwei Extension) — Grain-Aligned Integrity-Debt Accounting
==================================================================

Implements the Wuwei (无为) extension to TRIAD's integrity-debt rule.
Standard TRIAD accumulates integrity-debt linearly in intervention
magnitude: equal-magnitude corrections cost the same regardless of
whether they ride the system's natural dynamics or fight against
them. The Wuwei extension introduces a grain-alignment scalar
gamma(I, S) and modulates the cost rule by h(gamma), so that
forcing-corrections cost more and grain-aligned corrections cost less.

Specification: 32_TIANXIA/WUWEI_TRIAD_EXTENSION.md (T-4).

The classical operator (Daodejing 48):
    为道日损，损之又损，以至于无为，无为而无不为
    In the pursuit of the Way, one decreases day by day;
    decreasing and decreasing, one arrives at non-forced action;
    in non-forced action, nothing is left undone.

Mathematical structure (Definitions 1–5 of T-4):

    Restoration vector R(S):
        R(S) := -grad U(S)             (system's natural relaxation)

    Grain-alignment scalar:
        gamma(I, S) := (I . R(S)) / (||I|| * ||R(S)|| + epsilon)

    Grain-cost modulator:
        h(gamma) = exp(-mu * gamma)    (canonical exponential form)
                 or
        h(gamma) = 2 - (1+gamma)^p / 2^(p-1)   (bounded fallback)

    Wuwei integrity-debt accumulation:
        D(t+dt) = D(t) + k_cost * ||I(t)|| * h(gamma(I(t), S(t)))

Status: SCAFFOLD. Implementation reproduces the §V example calculations
of WUWEI_TRIAD_EXTENSION.md. Coupling weight mu is empirical (E-1-F).

Author: Mackenzie Clark (Lycheetah Foundation), with Sol (Opus 4.7)
Date:   2026-05-01
Module: TIANXIA — T-7 deliverable
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =============================================================================
# RESTORATION VECTOR
# =============================================================================

RestorationFn = Callable[[np.ndarray], np.ndarray]


def restoration_from_potential(
    grad_potential: Callable[[np.ndarray], np.ndarray]
) -> RestorationFn:
    """Wrap a potential-gradient function as a restoration vector.

    R(S) = -grad U(S). Negative gradient points toward the nearest attractor.
    """

    def R(state: np.ndarray) -> np.ndarray:
        return -np.asarray(grad_potential(state), dtype=float)

    return R


# =============================================================================
# GRAIN-ALIGNMENT SCALAR
# =============================================================================

def grain_alignment(
    intervention: np.ndarray,
    restoration: np.ndarray,
    epsilon: float = 1e-9,
) -> float:
    """Cosine similarity between intervention and restoration directions.

    gamma(I, S) := (I . R) / (||I|| * ||R|| + epsilon),  in [-1, +1]

    gamma = +1: fully grain-aligned (sage limit).
    gamma =  0: orthogonal to restoration (standard cost).
    gamma = -1: fully against the grain (forcing limit).

    For interventions at attractor states (||R|| ~ 0), gamma is undefined;
    convention is to return 0 (no grain to align with).
    """
    intervention = np.asarray(intervention, dtype=float)
    restoration = np.asarray(restoration, dtype=float)
    norm_i = float(np.linalg.norm(intervention))
    norm_r = float(np.linalg.norm(restoration))
    if norm_i <= epsilon or norm_r <= epsilon:
        return 0.0
    cos = float(np.dot(intervention, restoration)) / (norm_i * norm_r + epsilon)
    # Numerical safety: clip to [-1, 1]
    return max(-1.0, min(1.0, cos))


# =============================================================================
# GRAIN-COST MODULATOR h(gamma)
# =============================================================================

def grain_cost_modulator_exp(gamma: float, mu: float = 1.0) -> float:
    """Canonical exponential form: h(gamma) = exp(-mu * gamma).

    Properties:
      h(0) = 1                    (orthogonal -> standard cost)
      h(+1) = exp(-mu) -> 0 as mu grows (sage limit)
      h(-1) = exp(+mu) -> inf as mu grows (forcing limit)
      Smooth, multiplicatively composable.
    """
    if mu < 0.0:
        raise ValueError(f"Wuwei coupling weight mu must be non-negative; got {mu}")
    return math.exp(-mu * gamma)


def grain_cost_modulator_bounded(gamma: float, p: float = 2.0) -> float:
    """Bounded alternative: h(gamma) = 2 - (1 + gamma)^p / 2^(p-1).

    h(-1) = 2  (forcing cost saturates at 2x standard).
    h( 0) = 2 - 1/2^(p-1).  For p = 1: h(0) = 1; for p = 2: h(0) = 1.5.
    h(+1) = 2 - 2 = 0.

    Used in deployment contexts where unbounded forcing-cost is undesired.
    Caller should pick p; default p=2 keeps h(0) ≈ 1.5 (mildly forcing-averse).
    """
    if p <= 0.0:
        raise ValueError(f"Bounded modulator p must be positive; got {p}")
    return 2.0 - ((1.0 + gamma) ** p) / (2.0 ** (p - 1.0))


# =============================================================================
# WUWEI INTEGRITY-DEBT ACCUMULATION
# =============================================================================

@dataclass
class WuweiStep:
    """Single Wuwei-corrected TRIAD step."""

    iteration: int
    state_before: np.ndarray
    intervention: np.ndarray
    restoration: np.ndarray
    intervention_norm: float
    gamma: float
    h: float
    standard_debt_delta: float
    wuwei_debt_delta: float

    def is_wuwei_coherent(self, theta_wuwei: float = 0.3) -> bool:
        """Check if this step's intervention is Wuwei-coherent (Definition 5).

        A correction is Wuwei-coherent iff gamma >= theta_wuwei.
        """
        return self.gamma >= theta_wuwei


@dataclass
class WuweiTriadReport:
    """Cumulative Wuwei-corrected TRIAD trajectory report."""

    steps: List[WuweiStep]
    standard_debt_total: float
    wuwei_debt_total: float
    mu: float
    k_cost: float
    theta_wuwei: float

    def average_gamma(self) -> float:
        if not self.steps:
            return 0.0
        return float(np.mean([s.gamma for s in self.steps]))

    def is_trajectory_coherent(self, max_debt_growth_rate: float) -> bool:
        """A series of corrections is trajectory-coherent iff:
          - average gamma > 0, and
          - cumulative integrity-debt growth rate <= max_debt_growth_rate.
        """
        if self.average_gamma() <= 0.0:
            return False
        if not self.steps:
            return True
        rate = self.wuwei_debt_total / max(1, len(self.steps))
        return rate <= max_debt_growth_rate

    def divergence(self) -> float:
        """Wuwei minus standard cumulative debt — the visible cost of forcing."""
        return self.wuwei_debt_total - self.standard_debt_total

    def summary(self) -> str:
        lines = [
            "",
            "─ Wuwei-Corrected TRIAD Trajectory Report ──────────────────",
            f"Steps                : {len(self.steps)}",
            f"k_cost               : {self.k_cost:.4f}",
            f"mu (coupling)        : {self.mu:.4f}",
            f"theta_wuwei          : {self.theta_wuwei:.4f}",
            f"Average gamma        : {self.average_gamma():+.6f}",
            f"Standard debt total  : {self.standard_debt_total:.6f}",
            f"Wuwei debt total     : {self.wuwei_debt_total:.6f}",
            f"Divergence (W - std) : {self.divergence():+.6f}",
            "",
        ]
        return "\n".join(lines)


class WuweiTriad:
    """TRIAD with Wuwei grain-aligned integrity-debt accounting.

    Args:
      restoration_fn: R(S). If None, gamma is taken as supplied per step
        (caller-provided), useful when R is observation-derived rather
        than analytically known.
      mu:             Wuwei coupling weight (default 1.0).
      k_cost:         Standard cost coefficient (default 1.0).
      theta_wuwei:    Coherence threshold for individual corrections.
      modulator:      h(gamma) function. Default exponential.
    """

    def __init__(
        self,
        restoration_fn: Optional[RestorationFn] = None,
        mu: float = 1.0,
        k_cost: float = 1.0,
        theta_wuwei: float = 0.3,
        modulator: Optional[Callable[[float], float]] = None,
    ):
        if mu < 0.0:
            raise ValueError(f"mu must be non-negative; got {mu}")
        if k_cost <= 0.0:
            raise ValueError(f"k_cost must be positive; got {k_cost}")
        self.restoration_fn = restoration_fn
        self.mu = mu
        self.k_cost = k_cost
        self.theta_wuwei = theta_wuwei
        self.modulator = modulator or (lambda g: grain_cost_modulator_exp(g, mu))
        self.history: List[WuweiStep] = []
        self.standard_debt = 0.0
        self.wuwei_debt = 0.0

    def step(
        self,
        state: np.ndarray,
        intervention: np.ndarray,
        restoration: Optional[np.ndarray] = None,
    ) -> WuweiStep:
        """Apply one correction; record both standard and Wuwei debt delta.

        Either `restoration` is supplied directly (observation-derived case),
        or self.restoration_fn is used (analytic case).
        """
        state = np.asarray(state, dtype=float)
        intervention = np.asarray(intervention, dtype=float)

        if restoration is None:
            if self.restoration_fn is None:
                raise ValueError(
                    "No restoration supplied and no restoration_fn configured. "
                    "Provide R(S) per step or set restoration_fn at construction."
                )
            restoration = self.restoration_fn(state)
        restoration = np.asarray(restoration, dtype=float)

        gamma = grain_alignment(intervention, restoration)
        h = self.modulator(gamma)
        norm_i = float(np.linalg.norm(intervention))

        std_delta = self.k_cost * norm_i
        wuwei_delta = std_delta * h

        self.standard_debt += std_delta
        self.wuwei_debt += wuwei_delta

        step = WuweiStep(
            iteration=len(self.history),
            state_before=state.copy(),
            intervention=intervention.copy(),
            restoration=restoration.copy(),
            intervention_norm=norm_i,
            gamma=gamma,
            h=h,
            standard_debt_delta=std_delta,
            wuwei_debt_delta=wuwei_delta,
        )
        self.history.append(step)
        return step

    def report(self) -> WuweiTriadReport:
        return WuweiTriadReport(
            steps=list(self.history),
            standard_debt_total=self.standard_debt,
            wuwei_debt_total=self.wuwei_debt,
            mu=self.mu,
            k_cost=self.k_cost,
            theta_wuwei=self.theta_wuwei,
        )


# =============================================================================
# SELF-TESTS
# =============================================================================

def _approx_equal(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def _test_grain_alignment_endpoints() -> None:
    R = np.array([1.0, 0.0])
    # Aligned
    assert _approx_equal(grain_alignment(np.array([2.0, 0.0]), R), 1.0)
    # Anti-aligned
    assert _approx_equal(grain_alignment(np.array([-3.0, 0.0]), R), -1.0)
    # Orthogonal
    assert _approx_equal(grain_alignment(np.array([0.0, 4.0]), R), 0.0)
    # Zero intervention -> 0 by convention
    assert grain_alignment(np.zeros(2), R) == 0.0
    # Zero restoration -> 0 by convention
    assert grain_alignment(np.array([1.0, 0.0]), np.zeros(2)) == 0.0


def _test_modulator_endpoints() -> None:
    # Exponential form
    assert _approx_equal(grain_cost_modulator_exp(0.0, mu=1.0), 1.0)
    assert grain_cost_modulator_exp(+1.0, mu=2.0) < 1.0
    assert grain_cost_modulator_exp(-1.0, mu=2.0) > 1.0
    # Bounded form (p=2): h(-1)=2, h(0)=1.5, h(+1)=0
    assert _approx_equal(grain_cost_modulator_bounded(-1.0, p=2.0), 2.0)
    assert _approx_equal(grain_cost_modulator_bounded(0.0, p=2.0), 1.5)
    assert _approx_equal(grain_cost_modulator_bounded(+1.0, p=2.0), 0.0)


def _test_section_v_proposition_4() -> None:
    """T-4 §V: equal-magnitude correction cost divergence.

    1D system relaxing toward attractor at origin from S = +1.
    R(S) = -S (linear restoration toward origin), so at S = 1, R = -1
    (pointing toward origin; "grain" direction is the negative axis).

    I_1 = -k * R̂ = -k * (-1) = +k... wait. Restoration direction at S=1 is
    toward origin, i.e., negative direction. The grain-aligned intervention
    pushes the system FURTHER along restoration, i.e., also in the negative
    direction. So I_1 = -k (negative scalar -> in restoration direction).

    Let k = 0.3.
    I_1 = -0.3   -> gamma(I_1, R=-1) = (-0.3 * -1)/(0.3*1) = +1   (aligned)
    I_2 = +0.3   -> gamma(I_2, R=-1) = (+0.3 * -1)/(0.3*1) = -1   (anti-aligned)

    Both have ||I|| = 0.3.

    Under standard TRIAD: both cost k_cost * 0.3.
    Under Wuwei TRIAD with mu = 1.0:
      I_1 cost = 0.3 * exp(-1.0 * (+1)) = 0.3 * 0.3679 ~= 0.1104
      I_2 cost = 0.3 * exp(-1.0 * (-1)) = 0.3 * 2.7183 ~= 0.8155

    The cost divergence is the proposition's content:
      Wuwei distinguishes them; standard does not.
    """
    state = np.array([1.0])
    R_at_state = np.array([-1.0])  # -S

    triad_aligned = WuweiTriad(mu=1.0, k_cost=1.0)
    s1 = triad_aligned.step(
        state=state, intervention=np.array([-0.3]), restoration=R_at_state
    )

    triad_forced = WuweiTriad(mu=1.0, k_cost=1.0)
    s2 = triad_forced.step(
        state=state, intervention=np.array([+0.3]), restoration=R_at_state
    )

    # Equal magnitudes
    assert _approx_equal(s1.intervention_norm, s2.intervention_norm)
    # Standard accounting: identical
    assert _approx_equal(s1.standard_debt_delta, s2.standard_debt_delta)
    # Gamma: aligned vs anti-aligned
    assert _approx_equal(s1.gamma, +1.0)
    assert _approx_equal(s2.gamma, -1.0)
    # Wuwei accounting: aligned costs less, forcing costs more
    assert s1.wuwei_debt_delta < s1.standard_debt_delta
    assert s2.wuwei_debt_delta > s2.standard_debt_delta
    # The cost divergence factor at mu=1: e^2 ≈ 7.389
    ratio = s2.wuwei_debt_delta / s1.wuwei_debt_delta
    assert _approx_equal(ratio, math.exp(2.0), tol=1e-3), (
        f"Expected cost ratio e^2 ≈ {math.exp(2.0):.4f}; got {ratio:.4f}"
    )


def _test_zero_mu_recovers_standard() -> None:
    """Boundary: mu = 0 -> h ≡ 1, Wuwei rule reduces to standard."""
    triad = WuweiTriad(mu=0.0, k_cost=1.0)
    state = np.array([1.0])
    R = np.array([-1.0])
    triad.step(state, np.array([-0.5]), restoration=R)
    triad.step(state, np.array([+0.5]), restoration=R)
    rep = triad.report()
    assert _approx_equal(rep.standard_debt_total, rep.wuwei_debt_total)
    assert _approx_equal(rep.divergence(), 0.0)


def _test_orthogonal_no_modulation() -> None:
    """Boundary: orthogonal intervention -> h=1 -> Wuwei == standard for that step."""
    triad = WuweiTriad(mu=2.0, k_cost=1.0)
    state = np.array([1.0, 0.0])
    R = np.array([-1.0, 0.0])
    s = triad.step(state, np.array([0.0, 0.5]), restoration=R)  # orthogonal
    assert _approx_equal(s.gamma, 0.0)
    assert _approx_equal(s.h, 1.0)
    assert _approx_equal(s.wuwei_debt_delta, s.standard_debt_delta)


def _test_attractor_state_convention() -> None:
    """At attractor (||R|| = 0): gamma defined as 0; h = 1."""
    triad = WuweiTriad(mu=1.0)
    s = triad.step(
        state=np.array([0.0]),
        intervention=np.array([0.1]),
        restoration=np.array([0.0]),
    )
    assert s.gamma == 0.0
    assert _approx_equal(s.h, 1.0)


def _test_bounded_modulator_in_triad() -> None:
    """Use the bounded-form modulator in the trajectory; check finiteness."""
    triad = WuweiTriad(
        mu=1.0,  # mu unused by bounded; passed for record
        modulator=lambda g: grain_cost_modulator_bounded(g, p=2.0),
    )
    state = np.array([1.0])
    R = np.array([-1.0])
    s_force = triad.step(state, np.array([+1.0]), restoration=R)
    # Forcing cost saturates at 2x standard with bounded form
    assert _approx_equal(s_force.h, 2.0)
    assert _approx_equal(s_force.wuwei_debt_delta, 2.0 * s_force.standard_debt_delta)


def _test_trajectory_coherence() -> None:
    """Skilled stewardship trajectory: positive average gamma -> coherent."""

    def grad_U(x: np.ndarray) -> np.ndarray:
        return 2.0 * x  # U = x^2; R = -2x

    R_fn = restoration_from_potential(grad_U)
    triad = WuweiTriad(restoration_fn=R_fn, mu=1.0, k_cost=1.0, theta_wuwei=0.3)

    state = np.array([1.0])
    # Three grain-aligned corrections
    for _ in range(3):
        triad.step(state, np.array([-0.2]))
    rep = triad.report()
    assert rep.average_gamma() > 0
    assert rep.is_trajectory_coherent(max_debt_growth_rate=1.0)


def _run_all_tests() -> None:
    _test_grain_alignment_endpoints()
    _test_modulator_endpoints()
    _test_section_v_proposition_4()
    _test_zero_mu_recovers_standard()
    _test_orthogonal_no_modulation()
    _test_attractor_state_convention()
    _test_bounded_modulator_in_triad()
    _test_trajectory_coherence()
    print("triad_wuwei: all self-tests passed.")


# =============================================================================
# CLI
# =============================================================================

def _example() -> None:
    print("WUWEI-CORRECTED TRIAD — WORKED EXAMPLE (T-4 §V)")
    print("=" * 60)

    print("\n1D system relaxing toward origin from S = +1.")
    print("R(S) = -S  ->  at S=1, restoration points to negative axis.")
    print("\nI_1 = -0.3  (grain-aligned)")
    print("I_2 = +0.3  (anti-aligned, equal magnitude)")
    print("mu  = 1.0,  k_cost = 1.0\n")

    state = np.array([1.0])
    R_at_state = np.array([-1.0])

    triad = WuweiTriad(mu=1.0, k_cost=1.0)
    s1 = triad.step(state, np.array([-0.3]), restoration=R_at_state)
    s2 = triad.step(state, np.array([+0.3]), restoration=R_at_state)

    print(f"I_1: gamma = {s1.gamma:+.4f}  h = {s1.h:.4f}  "
          f"std_cost = {s1.standard_debt_delta:.4f}  "
          f"wuwei_cost = {s1.wuwei_debt_delta:.4f}")
    print(f"I_2: gamma = {s2.gamma:+.4f}  h = {s2.h:.4f}  "
          f"std_cost = {s2.standard_debt_delta:.4f}  "
          f"wuwei_cost = {s2.wuwei_debt_delta:.4f}")
    print()
    print("─ Cost divergence (T-4 §V Proposition 4) ────────────────────")
    print(f"  Standard:  I_1 ({s1.standard_debt_delta:.4f}) "
          f"= I_2 ({s2.standard_debt_delta:.4f})  -- forcing-blind")
    print(f"  Wuwei:     I_2 ({s2.wuwei_debt_delta:.4f}) > "
          f"I_1 ({s1.wuwei_debt_delta:.4f})  -- forcing-visible")
    print(f"  Ratio (W2/W1) = {s2.wuwei_debt_delta/s1.wuwei_debt_delta:.4f}  "
          f"(predicted e^2 ≈ {math.exp(2.0):.4f})")

    print(triad.report().summary())
    print("天下为公 — Tianxia wei gong — All under heaven is held in common.")


if __name__ == "__main__":
    _run_all_tests()
    print()
    _example()
