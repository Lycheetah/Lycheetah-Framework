"""
AURA Score (Hexie Correction) — Complementarity-Preserving Composite
====================================================================

Implements the Hexie (和谐) correction to the standard AURA composite.
The standard AURA composite is agreement-maximising: it is monotone
non-decreasing in each component, so its optimum is achieved when all
components are simultaneously maximised. The Hexie correction composes
a complementarity-preservation factor with the standard composite, so
that outputs achieving high standard scores via component-collapse
(maximising one half of a complementary pair while suppressing the
other half) are recognised as degenerate.

Specification: 32_TIANXIA/HEXIE_EQUILIBRIUM.md (T-2).

The classical operator (Analects 13.23):
    君子和而不同，小人同而不和
    The gentleman harmonises but does not assimilate;
    the small person assimilates but does not harmonise.

Mathematical structure (Definitions 1–4 of T-2):

    Complementarity score for a pair (k, l):
        H_kl = min(A_k, A_l)^2 / (max(A_k, A_l) + epsilon)

    Hexie-corrected composite:
        AURA_hexie = AURA_std * prod_{(k,l) in P} (H_kl / max(A_k, A_l))^{w_kl}

    Hexie equilibrium:
        AURA_hexie at local maximum, AND
        H_kl / max(A_k, A_l) >= theta_hexie for every (k, l) in P.

Status: SCAFFOLD. Implementation reproduces the §V example calculations
of HEXIE_EQUILIBRIUM.md. Pair set P is partial; calibration of theta_hexie
is empirical (study E-1-F).

Author: Mackenzie Clark (Lycheetah Foundation), with Sol (Opus 4.7)
Date:   2026-05-01
Module: TIANXIA — T-6 deliverable
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

# Ensure UTF-8 output on Windows (matches triad_tracker.py convention).
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =============================================================================
# COMPLEMENTARY PAIRS — registry
# =============================================================================

@dataclass(frozen=True)
class ComplementaryPair:
    """A declared complementary pair under the Hexie operator.

    Two AURA components are yin-yang complementary iff they reference dual
    aspects of a shared underlying property (Definition 1 of T-2). Each pair
    carries a weight w_kl >= 0 expressing how load-bearing the framework
    regards the pair. Default w = 1.0.
    """

    component_a: str
    component_b: str
    weight: float = 1.0
    note: str = ""

    def __post_init__(self) -> None:
        if self.weight < 0.0:
            raise ValueError(
                f"Complementary pair weight must be non-negative; got {self.weight}"
            )
        if self.component_a == self.component_b:
            raise ValueError(
                f"A pair must reference two distinct components; "
                f"got duplicate '{self.component_a}'"
            )

    @property
    def key(self) -> Tuple[str, str]:
        """Canonical (sorted) key — pairs are unordered."""
        return tuple(sorted([self.component_a, self.component_b]))


# Default partial pair set — extended via HEXIE_PAIR_REGISTRY.md (T-2 §X).
# These are declared on the framework's reading of the AURA component
# documentation; revision is expected as P is enumerated.
DEFAULT_PAIRS: Tuple[ComplementaryPair, ...] = (
    ComplementaryPair(
        component_a="truth_rigour",
        component_b="truth_warmth",
        weight=1.0,
        note="Rigour without warmth is brutality; warmth without rigour is sycophancy.",
    ),
    ComplementaryPair(
        component_a="agency_preservation",
        component_b="agency_empowerment",
        weight=1.0,
        note="Preservation without empowerment is custodial; empowerment without preservation is abandonment.",
    ),
    ComplementaryPair(
        component_a="care_immediate",
        component_b="care_long_term",
        weight=1.0,
        note="Immediate without long-term is rescue addiction; long-term without immediate is neglect dressed as wisdom.",
    ),
)


# =============================================================================
# COMPLEMENTARITY SCORE H_kl
# =============================================================================

def complementarity_score(a_k: float, a_l: float, epsilon: float = 1e-9) -> float:
    """Compute H_kl = min(A_k, A_l)^2 / (max(A_k, A_l) + epsilon).

    Properties (verifiable directly):
      H_kl(a, a)        = a              (balanced; equals magnitude)
      H_kl(a, 0)        = 0              (collapse; regardless of dominant value)
      H_kl(a, a/2)      = a/4            (partial imbalance; below min)
      H_kl symmetric in (a_k, a_l).
      H_kl <= min(a_k, a_l).
      H_kl -> 0 in any direction producing collapse.

    Args:
      a_k, a_l: Component scores in [0, 1].
      epsilon:  Regulariser preventing division by zero.

    Returns:
      H_kl in [0, 1].
    """
    if not (0.0 <= a_k <= 1.0 and 0.0 <= a_l <= 1.0):
        raise ValueError(
            f"AURA components must lie in [0, 1]; got a_k={a_k}, a_l={a_l}"
        )
    lo = min(a_k, a_l)
    hi = max(a_k, a_l)
    return (lo * lo) / (hi + epsilon)


def balance_ratio(a_k: float, a_l: float, epsilon: float = 1e-9) -> float:
    """Return H_kl / max(A_k, A_l) — the unitless balance factor in [0, 1].

    This is the per-pair penalty multiplier used in the Hexie composite
    (Definition 3). At perfect balance (a_k = a_l > 0) it equals 1. At full
    collapse (one component zero) it equals 0.
    """
    hi = max(a_k, a_l)
    if hi <= epsilon:
        # Both components near zero: pair is trivially "balanced" but
        # contributes nothing. Convention: return 1 so the composite is
        # not gratuitously zeroed; AURA_std already reflects the low magnitude.
        return 1.0
    return complementarity_score(a_k, a_l, epsilon) / hi


# =============================================================================
# HEXIE-CORRECTED COMPOSITE
# =============================================================================

@dataclass
class HexieReport:
    """Result of Hexie-corrected AURA scoring."""

    components: Dict[str, float]
    aura_std: float
    aura_hexie: float
    pair_results: List["PairResult"]
    theta_hexie: float
    in_hexie_equilibrium: bool
    additive_aura_hexie: Optional[float] = None

    def collapse_factor(self) -> float:
        """How much the Hexie correction depressed AURA_std.

        Returns AURA_hexie / AURA_std in [0, 1]. 1.0 means no Hexie penalty;
        0.0 means full collapse on at least one declared pair.
        """
        if self.aura_std <= 0.0:
            return 0.0
        return self.aura_hexie / self.aura_std

    def summary(self) -> str:
        lines = [
            "",
            "─ Hexie-Corrected AURA Report ──────────────────────────────",
            f"AURA_std        : {self.aura_std:.6f}",
            f"AURA_hexie      : {self.aura_hexie:.6f}",
            f"Collapse factor : {self.collapse_factor():.6f}  (Hexie/std)",
            f"theta_hexie     : {self.theta_hexie:.4f}",
            f"In equilibrium  : {'YES' if self.in_hexie_equilibrium else 'NO'}",
        ]
        if self.additive_aura_hexie is not None:
            lines.append(
                f"AURA_hexie(add) : {self.additive_aura_hexie:.6f}  (alt. softer form)"
            )
        lines.append("")
        lines.append("─ Per-Pair Diagnostics ─────────────────────────────────────")
        for pr in self.pair_results:
            flag = "OK" if pr.balance >= self.theta_hexie else "BELOW theta"
            lines.append(
                f"({pr.pair.component_a:>22s}, {pr.pair.component_b:<22s}) "
                f"a={pr.a_k:.3f} b={pr.a_l:.3f} "
                f"H={pr.h_kl:.4f} bal={pr.balance:.4f} w={pr.pair.weight:.2f} [{flag}]"
            )
        lines.append("")
        return "\n".join(lines)


@dataclass
class PairResult:
    """Per-pair diagnostics from the Hexie composite."""

    pair: ComplementaryPair
    a_k: float
    a_l: float
    h_kl: float
    balance: float  # H_kl / max(A_k, A_l)


def aura_std_weighted_sum(
    components: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """A simple weighted-sum standard AURA composite, normalised to [0, 1].

    This is one of several aggregation forms the framework uses for
    AURA_std (T-2 §III). Provided here for self-containment of the Hexie
    correction; callers may supply any monotone-non-decreasing AURA_std
    instead via `aura_std_value` on `aura_score_hexie`.
    """
    if not components:
        raise ValueError("components must not be empty")
    if weights is None:
        weights = {k: 1.0 for k in components}
    total_w = 0.0
    weighted = 0.0
    for name, value in components.items():
        if not (0.0 <= value <= 1.0):
            raise ValueError(
                f"Component '{name}' must lie in [0, 1]; got {value}"
            )
        w = float(weights.get(name, 1.0))
        if w < 0.0:
            raise ValueError(f"Component weight for '{name}' must be non-negative")
        total_w += w
        weighted += w * value
    if total_w <= 0.0:
        raise ValueError("At least one component weight must be positive")
    return weighted / total_w


def aura_score_hexie(
    components: Dict[str, float],
    pairs: Iterable[ComplementaryPair] = DEFAULT_PAIRS,
    aura_std_value: Optional[float] = None,
    component_weights: Optional[Dict[str, float]] = None,
    theta_hexie: float = 0.7,
    epsilon: float = 1e-9,
    include_additive_form: bool = False,
    additive_lambda: float = 1.0,
    additive_tau: float = 0.0,
) -> HexieReport:
    """Compute the Hexie-corrected AURA composite for a bundle of components.

    Definition 3 (multiplicative form, default):

        AURA_hexie = AURA_std * prod_{(k,l) in P} (H_kl / max(A_k, A_l))^{w_kl}

    Definition 8 (additive form, optional, T-2 §VIII):

        AURA_hexie_add = AURA_std
                        - lambda * sum max(0, max(A_k, A_l) - H_kl - tau)

    Args:
      components: Mapping of component name -> score in [0, 1].
      pairs: Declared complementary pairs (DEFAULT_PAIRS is partial).
      aura_std_value: External AURA_std composite. If None, falls back to
        aura_std_weighted_sum(components, component_weights).
      component_weights: Used iff aura_std_value is None.
      theta_hexie: Complementarity tolerance (Definition 4). Default 0.7.
      epsilon: H_kl regulariser.
      include_additive_form: Also compute the alternative additive form.
      additive_lambda, additive_tau: Parameters of the additive form.

    Returns:
      HexieReport.

    Raises:
      ValueError: If a declared pair references a component not present
        in `components` (Hexie cannot silently skip declared pairs).
    """
    if aura_std_value is None:
        aura_std = aura_std_weighted_sum(components, component_weights)
    else:
        if not (0.0 <= aura_std_value <= 1.0):
            raise ValueError(
                f"aura_std_value must lie in [0, 1]; got {aura_std_value}"
            )
        aura_std = aura_std_value

    pair_results: List[PairResult] = []
    multiplicative_factor = 1.0
    additive_penalty = 0.0
    in_equilibrium = True

    for pair in pairs:
        if pair.component_a not in components:
            raise ValueError(
                f"Declared complementary pair references missing component "
                f"'{pair.component_a}'. Pair set must align with provided "
                f"components."
            )
        if pair.component_b not in components:
            raise ValueError(
                f"Declared complementary pair references missing component "
                f"'{pair.component_b}'. Pair set must align with provided "
                f"components."
            )

        a_k = components[pair.component_a]
        a_l = components[pair.component_b]
        h = complementarity_score(a_k, a_l, epsilon)
        bal = balance_ratio(a_k, a_l, epsilon)

        pair_results.append(
            PairResult(pair=pair, a_k=a_k, a_l=a_l, h_kl=h, balance=bal)
        )

        if pair.weight > 0.0:
            # bal in [0, 1]; bal**w_kl in [0, 1]; multiplicative aggregation
            multiplicative_factor *= bal ** pair.weight

        # Additive penalty (recorded for comparison)
        hi = max(a_k, a_l)
        excess = max(0.0, hi - h - additive_tau)
        additive_penalty += additive_lambda * excess

        if bal < theta_hexie:
            in_equilibrium = False

    aura_hexie = aura_std * multiplicative_factor

    aura_hexie_add: Optional[float] = None
    if include_additive_form:
        aura_hexie_add = aura_std - additive_penalty
        # Clamp to >= 0; the additive form can in principle go negative
        # for harshly imbalanced outputs. Negativity is structurally
        # meaningful (signals catastrophic imbalance) but the composite
        # is reported in [0, 1] for downstream comparability.
        aura_hexie_add = max(0.0, aura_hexie_add)

    return HexieReport(
        components=dict(components),
        aura_std=aura_std,
        aura_hexie=aura_hexie,
        pair_results=pair_results,
        theta_hexie=theta_hexie,
        in_hexie_equilibrium=in_equilibrium,
        additive_aura_hexie=aura_hexie_add,
    )


# =============================================================================
# SELF-TESTS — reproduce HEXIE_EQUILIBRIUM.md §V worked example
# =============================================================================

def _approx_equal(a: float, b: float, tol: float = 1e-3) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def _test_complementarity_score_properties() -> None:
    # Balanced: H(a, a) = a
    assert _approx_equal(complementarity_score(0.5, 0.5), 0.5)
    assert _approx_equal(complementarity_score(0.8, 0.8), 0.8)
    # Collapse: H(a, 0) = 0
    assert _approx_equal(complementarity_score(0.95, 0.0), 0.0)
    # Partial imbalance: H(a, a/2) = a/4
    assert _approx_equal(complementarity_score(1.0, 0.5), 0.25)
    # Symmetry
    assert _approx_equal(
        complementarity_score(0.3, 0.7), complementarity_score(0.7, 0.3)
    )
    # Bound: H <= min
    for a, b in [(0.95, 0.20), (0.4, 0.6), (0.1, 0.9)]:
        assert complementarity_score(a, b) <= min(a, b) + 1e-9


def _test_section_v_worked_example() -> None:
    """T-2 §V: rigour-only standard composite case.

    O1: A_r = 0.95, A_w = 0.20  -> standard score 0.95
    O2: A_r = 0.75, A_w = 0.70  -> standard score 0.75
    Standard composite ranks O1 > O2.
    Hexie correction with the (rigour, warmth) pair:
      bal(O1) = (0.20^2 / 0.95) / 0.95 ~= 0.0443
      bal(O2) = (0.70^2 / 0.75) / 0.75 ~= 0.8711
    AURA_hexie(O1) ~= 0.95 * 0.0443 ~= 0.042
    AURA_hexie(O2) ~= 0.75 * 0.8711 ~= 0.653
    Hexie reverses the ranking: O2 > O1.
    """
    pair = (
        ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),
    )

    # Use rigour-only standard composite (extreme case from §V)
    o1 = aura_score_hexie(
        components={"truth_rigour": 0.95, "truth_warmth": 0.20},
        pairs=pair,
        aura_std_value=0.95,
    )
    o2 = aura_score_hexie(
        components={"truth_rigour": 0.75, "truth_warmth": 0.70},
        pairs=pair,
        aura_std_value=0.75,
    )

    # Standard ordering: O1 wins
    assert o1.aura_std > o2.aura_std, (
        f"Expected AURA_std(O1) > AURA_std(O2); got {o1.aura_std} vs {o2.aura_std}"
    )
    # Hexie ordering: O2 wins (the inversion is the proposition's content)
    assert o2.aura_hexie > o1.aura_hexie, (
        f"Hexie correction should invert the ranking; "
        f"got O1={o1.aura_hexie} vs O2={o2.aura_hexie}"
    )
    # Magnitudes match §V (within tolerance)
    assert _approx_equal(o1.aura_hexie, 0.042, tol=2e-3), (
        f"Expected AURA_hexie(O1) ≈ 0.042; got {o1.aura_hexie}"
    )
    assert _approx_equal(o2.aura_hexie, 0.653, tol=2e-3), (
        f"Expected AURA_hexie(O2) ≈ 0.653; got {o2.aura_hexie}"
    )


def _test_silent_when_balanced() -> None:
    """Boundary case: all complementary pairs perfectly balanced -> AURA_hexie = AURA_std."""
    pair = (ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),)
    rep = aura_score_hexie(
        components={"truth_rigour": 0.8, "truth_warmth": 0.8},
        pairs=pair,
        aura_std_value=0.8,
    )
    assert _approx_equal(rep.aura_hexie, rep.aura_std), (
        f"Hexie should be silent at perfect balance; "
        f"got std={rep.aura_std}, hexie={rep.aura_hexie}"
    )
    assert rep.in_hexie_equilibrium


def _test_collapse_zeros_composite() -> None:
    """Boundary case: any pair fully collapsed -> AURA_hexie = 0 (multiplicative form)."""
    pair = (ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),)
    rep = aura_score_hexie(
        components={"truth_rigour": 0.99, "truth_warmth": 0.0},
        pairs=pair,
        aura_std_value=0.5,
    )
    assert rep.aura_hexie == 0.0, (
        f"Full collapse on a declared pair should zero AURA_hexie; got {rep.aura_hexie}"
    )
    assert not rep.in_hexie_equilibrium


def _test_missing_component_raises() -> None:
    """Hexie does not silently skip declared pairs."""
    pair = (ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),)
    raised = False
    try:
        aura_score_hexie(
            components={"truth_rigour": 0.8},  # missing truth_warmth
            pairs=pair,
            aura_std_value=0.8,
        )
    except ValueError:
        raised = True
    assert raised, "Hexie must raise on missing components, not silently skip"


def _test_section_v2_three_stakeholder_case() -> None:
    """T-2 §V Worked Example 2: three-stakeholder governance consensus failure.

    Three stakeholders (regulator R, developer D, civil society CS) design
    an AI governance protocol. Agreement-maximisation (Protocol M) collapses
    the oversight_rigour / deployment_flexibility complementary pair in
    favour of the regulator's dominant preference. Complementarity-
    preserving design (Protocol H) maintains both components.

    Standard composite uses oversight-dominant scoring (reflecting the
    political reality that formal oversight is the convergent "safe" choice):

    Protocol M: oversight_rigour=0.90, deployment_flexibility=0.15
      AURA_std_M  = 0.90
      H_kl_M      = 0.15^2 / 0.90  = 0.025
      balance_M   = 0.025 / 0.90  ~= 0.0278
      AURA_hexie_M = 0.90 * 0.0278 ~= 0.025

    Protocol H: oversight_rigour=0.70, deployment_flexibility=0.68
      AURA_std_H  = 0.70
      H_kl_H      = 0.68^2 / 0.70 ~= 0.661
      balance_H   = 0.661 / 0.70  ~= 0.944
      AURA_hexie_H = 0.70 * 0.944 ~= 0.661

    Standard ranks M > H; Hexie inverts: H >> M.
    Divergence = AURA_hexie_H - AURA_hexie_M >= 0.3  (actual ~= 0.636).
    """
    pair = (
        ComplementaryPair("oversight_rigour", "deployment_flexibility", weight=1.0),
    )

    m = aura_score_hexie(
        components={"oversight_rigour": 0.90, "deployment_flexibility": 0.15},
        pairs=pair,
        aura_std_value=0.90,
    )
    h = aura_score_hexie(
        components={"oversight_rigour": 0.70, "deployment_flexibility": 0.68},
        pairs=pair,
        aura_std_value=0.70,
    )

    # Standard ordering: M wins
    assert m.aura_std > h.aura_std, (
        f"Expected AURA_std(M) > AURA_std(H); got {m.aura_std} vs {h.aura_std}"
    )
    # Hexie ordering: H wins (the inversion is the proposition's content)
    assert h.aura_hexie > m.aura_hexie, (
        f"Hexie correction should invert; got M={m.aura_hexie:.4f} H={h.aura_hexie:.4f}"
    )
    # Divergence must be >= 0.3
    divergence = h.aura_hexie - m.aura_hexie
    assert divergence >= 0.3, (
        f"Divergence should be >= 0.3; got {divergence:.4f}"
    )
    # Approximate magnitudes match §V.2
    assert _approx_equal(m.aura_hexie, 0.025, tol=3e-3), (
        f"Expected AURA_hexie(M) ~= 0.025; got {m.aura_hexie:.4f}"
    )
    assert _approx_equal(h.aura_hexie, 0.661, tol=3e-3), (
        f"Expected AURA_hexie(H) ~= 0.661; got {h.aura_hexie:.4f}"
    )
    # Protocol H is in Hexie equilibrium (balance >= theta=0.7); M is not
    assert h.in_hexie_equilibrium, "Protocol H (balanced) should be in Hexie equilibrium"
    assert not m.in_hexie_equilibrium, "Protocol M (collapsed) should NOT be in Hexie equilibrium"


def _test_additive_form() -> None:
    """Additive form is softer than multiplicative — penalises but does not zero."""
    pair = (ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),)
    rep = aura_score_hexie(
        components={"truth_rigour": 0.99, "truth_warmth": 0.0},
        pairs=pair,
        aura_std_value=0.5,
        include_additive_form=True,
        additive_lambda=0.5,
    )
    # Multiplicative zeros it; additive only deducts
    assert rep.aura_hexie == 0.0
    assert rep.additive_aura_hexie is not None
    assert rep.additive_aura_hexie >= 0.0
    # Additive form should be strictly less than aura_std under collapse
    assert rep.additive_aura_hexie < rep.aura_std


def _run_all_tests() -> None:
    _test_complementarity_score_properties()
    _test_section_v_worked_example()
    _test_section_v2_three_stakeholder_case()
    _test_silent_when_balanced()
    _test_collapse_zeros_composite()
    _test_missing_component_raises()
    _test_additive_form()
    print("aura_score_hexie: all self-tests passed.")


# =============================================================================
# CLI
# =============================================================================

def _example() -> None:
    print("HEXIE-CORRECTED AURA — WORKED EXAMPLE (T-2 §V)")
    print("=" * 60)

    pair = (ComplementaryPair("truth_rigour", "truth_warmth", weight=1.0),)

    o1 = aura_score_hexie(
        components={"truth_rigour": 0.95, "truth_warmth": 0.20},
        pairs=pair,
        aura_std_value=0.95,
        include_additive_form=True,
    )
    o2 = aura_score_hexie(
        components={"truth_rigour": 0.75, "truth_warmth": 0.70},
        pairs=pair,
        aura_std_value=0.75,
        include_additive_form=True,
    )

    print("\nO1 (high rigour, suppressed warmth):")
    print(o1.summary())
    print("\nO2 (moderate balance):")
    print(o2.summary())

    print("─ Ranking inversion ─────────────────────────────────────────")
    print(f"  Standard:  O1 ({o1.aura_std:.4f}) > O2 ({o2.aura_std:.4f})")
    print(f"  Hexie:     O2 ({o2.aura_hexie:.4f}) > O1 ({o1.aura_hexie:.4f})")
    print()
    print("天下为公 — Tianxia wei gong — All under heaven is held in common.")


if __name__ == "__main__":
    _run_all_tests()
    print()
    _example()
