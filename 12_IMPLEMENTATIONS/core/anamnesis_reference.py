"""
ANAMNESIS reference scaffold — ONLY behaviors fixed by the shelf specs.

Status: REFERENCE / SCAFFOLD
  - Implements concrete, testable fragments cited from
    07_ANAMNESIS_L0/ANAMNESIS_FROM_ARCHIVE.md and README.md.
  - Does NOT invent TC scoring, Scale(S) numerics, R_min/C_min, or Π on M.
  - See MISSING_SPEC below (fuller engine blocked until Mac defines TC/Scale/Π).

Author: Mackenzie Clark (spec) · reference module 2026-09-24
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Set, Tuple


# =============================================================================
# MISSING-SPEC — Mac must define before a fuller engine is honest
# =============================================================================

MISSING_SPEC: List[str] = [
    "TC score formula: inputs (discovery records), aggregation, and statistical tolerance "
    "for TC(abstract)≈TC(embodied) (essentials.md §'The test, stated as a falsifier' steps 1–4).",
    "Scale(S): numeric scale function on structures for Visible(A,t) "
    "(ANAMNESIS_FROM_ARCHIVE.md Def 3.3) — only the inequality form is specified.",
    "R_min / C_min thresholds in Theorem 3.1 (Convergent Discovery).",
    "Truth-pressure Π on abstract structure space M, and ∇Π dynamics dK/dt ∝ ∇Π(K) "
    "(Theorem 3.1 proof sketch) — no computable Π(S) given for arbitrary S∈M.",
    "Domain(A) membership test and attractor set Ω(D) construction (Theorem 3.1).",
    "Structure(D, depth) operator for Depth-Universality Theorem 3.3.",
    "Embodied vs abstract categorization taxonomy binding to Lakoff/Núñez "
    "(essentials.md battleground table) as machine-checkable labels.",
    "Empirical discovery-record schema for the TC program (catalog format).",
]


# =============================================================================
# Corollary 3.3.1 — φ fixed point of x ↦ 1 + 1/x
# Source: ANAMNESIS_FROM_ARCHIVE.md Corollary 3.3.1
# =============================================================================

PHI: float = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV: float = PHI - 1.0  # = 1/φ ≈ 0.6180339887


def phi_map(x: float) -> float:
    """The map cited for φ: x ↦ 1 + 1/x (Corollary 3.3.1)."""
    if x == 0.0:
        raise ZeroDivisionError("phi_map undefined at x=0")
    return 1.0 + 1.0 / x


def is_phi_fixed_point(x: float, tol: float = 1e-12) -> bool:
    """True iff x is a fixed point of phi_map within tol.

    Spec: ANAMNESIS_FROM_ARCHIVE.md Corollary 3.3.1 —
    'φ is the unique fixed point of the map x → 1 + 1/x' (for x>0).
    """
    return abs(phi_map(x) - x) <= tol


def verify_phi_identities(tol: float = 1e-12) -> Dict[str, bool]:
    """Check closed-form φ identities used as framework constants.

    Spec anchors:
      - Corollary 3.3.1 (fixed point)
      - README.md: 'φ⁻¹ ≈ 0.618'
    """
    return {
        "fixed_point": is_phi_fixed_point(PHI, tol=tol),
        "phi_inv_matches": abs(PHI_INV - 1.0 / PHI) <= tol,
        "phi_inv_approx_0618": abs(PHI_INV - 0.618) < 5e-4,
        # Negative root of x=1+1/x is 1-φ = -1/φ; also a fixed point algebraically,
        # but Corollary 3.3.1's "unique" claim is for the positive fixed point used
        # as the framework constant — we only assert positivity here.
        "phi_positive": PHI > 0.0,
    }


# =============================================================================
# Heptagon constant — README.md / COMPLETE cross-ref
# =============================================================================

HEPTAGON_COS: float = math.cos(math.pi / 7.0)


def heptagon_constant() -> float:
    """cos(π/7) ≈ 0.9010 — cited in 07_ANAMNESIS_L0/README.md as framework evidence.

    Spec: README.md lines on φ⁻¹ and cos(π/7) appearing in framework dynamics.
    """
    return HEPTAGON_COS


# =============================================================================
# Definition 3.2 — Agent state structure (representation only)
# Source: ANAMNESIS_FROM_ARCHIVE.md Definition 3.2
# =============================================================================

@dataclass(frozen=True)
class Structure:
    """A named element of M with an externally supplied scale.

    Scale is NOT derived here — Def 3.3 requires Scale(S) but does not define
    how to compute it. Callers must provide scale (MISSING-SPEC if omitted).
    """

    name: str
    scale: float

    def __post_init__(self):
        if self.scale <= 0:
            raise ValueError("Scale(S) must be positive when supplied")


@dataclass
class AgentState:
    """Finite explorer A(t) = {K(t), R(t), C(t)} — Def 3.2.

    Spec: ANAMNESIS_FROM_ARCHIVE.md Definition 3.2.
    K holds structure names recognized so far.
    """

    knowledge: Set[str] = field(default_factory=set)
    resolution: float = 1.0
    capacity: float = 1.0

    def __post_init__(self):
        if self.resolution <= 0 or self.capacity <= 0:
            raise ValueError("R(t) and C(t) must be finite and positive (Def 3.2)")
        if len(self.knowledge) > self.capacity + 1e-9:
            # Soft guard: capacity bounds how many structures can be held
            raise ValueError("K(t) exceeds capacity C(t) (Def 3.2 finiteness)")


# =============================================================================
# Definition 3.3 / Theorem 3.2 — visibility & discovery-as-resolution-increase
# =============================================================================

def visible(agent: AgentState, structures: Iterable[Structure]) -> FrozenSet[str]:
    """Visible(A,t) = {S ∈ M : Scale(S) > 1/R(A,t)} — Def 3.3.

    Spec: ANAMNESIS_FROM_ARCHIVE.md Definition 3.3.
    Requires caller-supplied Scale on each Structure (not invented here).
    """
    threshold = 1.0 / agent.resolution
    return frozenset(s.name for s in structures if s.scale > threshold)


def discovery_event(
    agent_before: AgentState,
    agent_after: AgentState,
    structure_name: str,
    structures: Iterable[Structure],
) -> bool:
    """Discovery(A,S,t) ⟺ S∉Visible(t-1) ∧ S∈Visible(t) — Theorem 3.2.

    Spec: ANAMNESIS_FROM_ARCHIVE.md Theorem 3.2.
    """
    structs = list(structures)
    return (
        structure_name not in visible(agent_before, structs)
        and structure_name in visible(agent_after, structs)
    )


# =============================================================================
# Definition 3.4 — Anamnesis operator 𝔸 (structural properties only)
# =============================================================================

def anamnesis_recognize(agent: AgentState, structure_name: str) -> AgentState:
    """𝔸(A, S): K' = K ∪ {S}, R' ≥ R — Def 3.4.

    Spec: ANAMNESIS_FROM_ARCHIVE.md Definition 3.4 (monotonicity, idempotence).
    Does not invent the phenomenology of recognition or automatic R-increase
    magnitude — R is left unchanged unless caller raises it (Property 4 only
    requires R' ≥ R, satisfied by equality).
    """
    if len(agent.knowledge) >= agent.capacity and structure_name not in agent.knowledge:
        raise ValueError("Cannot recognize: at capacity C(t) (Def 3.2)")
    new_k = set(agent.knowledge)
    new_k.add(structure_name)
    return AgentState(
        knowledge=new_k,
        resolution=agent.resolution,
        capacity=agent.capacity,
    )


def anamnesis_idempotent(agent: AgentState, structure_name: str) -> bool:
    """Property 3: 𝔸(𝔸(A,S),S) = 𝔸(A,S) — Def 3.4."""
    once = anamnesis_recognize(agent, structure_name)
    twice = anamnesis_recognize(once, structure_name)
    return once.knowledge == twice.knowledge and once.resolution == twice.resolution


def anamnesis_commutative(
    agent: AgentState, s1: str, s2: str
) -> bool:
    """Property 2: order of recognition does not affect final K — Def 3.4.

    Requires capacity ≥ |K| + 2 for a fair check when both are new.
    """
    a12 = anamnesis_recognize(anamnesis_recognize(agent, s1), s2)
    a21 = anamnesis_recognize(anamnesis_recognize(agent, s2), s1)
    return a12.knowledge == a21.knowledge
