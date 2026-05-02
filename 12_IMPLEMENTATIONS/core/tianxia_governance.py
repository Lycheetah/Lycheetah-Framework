"""
tianxia_governance.py — T-1 TIANXIA Operator Implementation
Tianxia (天下) flourishing-coherence extension to CASCADE multi-agent governance.

Classical source: Zhou-dynasty governance thought; Zhao Tingyang,
  The Tianxia System (2005, English 2021)
Framework mapping: CASCADE multi-agent master equation — adds k5 * grad_Phi_T term
Spec: CODEX_AURA_PRIME/32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md (T-1)
Status: [SCAFFOLD] — k5 unfit; Proposition 1 verified on simulation only; E-1-F pending.
Negative space: does NOT score real governments. Does NOT claim Tianxia dynamics
  are always stable. k5 is domain-specific [SCAFFOLD]. Inputs are
  framework-internal simulation variables.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Core types  (T-1 §IV)
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    """Per-agent CASCADE state."""
    psi: float                  # knowledge state
    E: float                    # energy available, >= 0
    E_need: float               # energy required, > 0
    violations: float           # integrity violations (normalised [0,1])
    externality_cost: float = 0.0  # cost imposed by this agent on others


@dataclass
class FlourishingParams:
    """Weights for F_i (T-1 §IV Def 1). Default equal weighting."""
    alpha: float = 1.0   # psi weight
    beta: float = 1.0    # (1 - violations) weight
    gamma: float = 1.0   # E/E_need weight
    delta: float = 1.0   # externality cost weight


@dataclass
class CascadeCoeffs:
    """k1..k4 Westphalian coefficients + k5 Tianxia coupling."""
    k1: float = 0.5    # truth-pressure gain
    k2: float = 0.3    # reversion to invariant
    k3: float = 0.4    # integrity-violation penalty
    k4: float = 0.6    # energy-term gain
    k5: float = 0.0    # Tianxia coupling weight; 0 = pure Westphalian
    Pi_th: float = 0.5
    Psi_inv: float = 0.0


# ---------------------------------------------------------------------------
# Flourishing and coupling  (T-1 §IV Defs 1–3)
# ---------------------------------------------------------------------------

def flourishing(
    agent: AgentState,
    params: FlourishingParams = FlourishingParams(),
) -> float:
    """
    F_i = alpha*psi + beta*(1-violations) + gamma*(E/E_need) - delta*c_i  (Def 1)
    """
    return (params.alpha * agent.psi
            + params.beta * (1.0 - agent.violations)
            + params.gamma * (agent.E / agent.E_need)
            - params.delta * agent.externality_cost)


def coherence_coeff_numerical(
    agent_i: AgentState,
    agent_j: AgentState,
    delta_F_j: float,
    delta_F_i_response: float,
) -> float:
    """
    C_ij = dF_i / dF_j  (Def 2) — supplied numerically.

    In general this requires a perturbation experiment or analytical derivation
    from the coupling structure. Callers provide the measured dF_i / dF_j ratio.

    Positive: mutualistic; Negative: extractive; Zero: independent.
    """
    if abs(delta_F_j) < 1e-12:
        return 0.0
    return delta_F_i_response / delta_F_j


def tianxia_potential(c_matrix: list[list[float]]) -> float:
    """
    Phi_T = sum_{i != j} C_ij  (Def 3)

    c_matrix[i][j] = C_ij for all i != j.
    Positive: net mutualistic. Negative: net extractive.
    """
    n = len(c_matrix)
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i != j:
                total += c_matrix[i][j]
    return total


# ---------------------------------------------------------------------------
# Dynamics  (T-1 §IV Definition 4)
# ---------------------------------------------------------------------------

def westphalian_dpsi(
    agent: AgentState,
    Pi_i: float,
    coeffs: CascadeCoeffs,
) -> float:
    """dPsi_i/dt — Westphalian CASCADE (k5 = 0)."""
    return (coeffs.k1 * (Pi_i - coeffs.Pi_th)
            - coeffs.k2 * (agent.psi - coeffs.Psi_inv)
            - coeffs.k3 * agent.violations
            + coeffs.k4 * (agent.E / agent.E_need))


def tianxia_term(grad_phi_T: float, coeffs: CascadeCoeffs) -> float:
    """k5 * grad_Phi_T — Tianxia coupling contribution to dPsi_i/dt."""
    return coeffs.k5 * grad_phi_T


# ---------------------------------------------------------------------------
# Extractive scenario for Proposition 1  (T-1 §V)
#
# Model: Agent 1's psi growth imposes quadratic externality on Agent 2.
#   F_1(psi_1) = alpha * psi_1  (direct, energy fixed)
#   F_2(psi_1, psi_2) = alpha * psi_2 - delta * k_ext * psi_1^2
#
# Coupling:
#   C_21 = dF_2/dF_1 = (-2*delta*k_ext*psi_1) / alpha  — grows more negative with psi_1
#   C_12 = 0  (Agent 1 independent of Agent 2's flourishing)
#
# Phi_T = C_21 + C_12 = -2*delta*k_ext*psi_1/alpha
# grad_Phi_T w.r.t. psi_1 = -2*delta*k_ext/alpha  (constant negative)
#
# Westphalian eq: 0 = k4*E_1/E_need - k2*psi_1  → psi_1_eq = k4*E1/(k2*E_need)
# Tianxia eq: 0 = k4*E_1/E_need + k5*grad_Phi_T - k2*psi_1
#   psi_1_eq_TX = (k4*E1/E_need + k5*grad_Phi_T) / k2  < psi_1_eq  when grad < 0
# ---------------------------------------------------------------------------

def extractive_grad_phi_T(
    k_ext: float,
    params: FlourishingParams = FlourishingParams(),
) -> float:
    """
    Analytical grad_Phi_T w.r.t. psi_1 for the quadratic-externality scenario.

    dPhi_T/d_psi_1 = -2 * delta * k_ext / alpha

    Negative: increasing Agent 1's psi always deepens the extraction.
    """
    return -2.0 * params.delta * k_ext / params.alpha


def simulate_extractive(
    psi1_init: float,
    psi2_init: float,
    coeffs: CascadeCoeffs,
    k_ext: float = 0.5,
    Pi_1: float = 0.6,
    Pi_2: float = 0.5,
    E1: float = 1.0,
    E2: float = 1.0,
    dt: float = 0.05,
    steps: int = 300,
    params: FlourishingParams = FlourishingParams(),
) -> dict:
    """
    Forward-Euler simulation of the two-agent quadratic-externality scenario.

    Westphalian dynamics (k5=0) converge to extractive equilibrium.
    Tianxia dynamics (k5>0) are moderated by the negative grad_Phi_T term.
    """
    grad = extractive_grad_phi_T(k_ext, params)

    psi1, psi2 = psi1_init, psi2_init
    history = {"psi1": [psi1], "psi2": [psi2]}

    for _ in range(steps):
        a1 = AgentState(psi=psi1, E=E1, E_need=1.0, violations=0.0)
        a2 = AgentState(psi=psi2, E=E2, E_need=1.0, violations=0.0)

        dPsi1 = (westphalian_dpsi(a1, Pi_1, coeffs)
                 + tianxia_term(grad, coeffs))
        dPsi2 = westphalian_dpsi(a2, Pi_2, coeffs)

        psi1 = psi1 + dt * dPsi1
        psi2 = psi2 + dt * dPsi2
        history["psi1"].append(psi1)
        history["psi2"].append(psi2)

    history["psi1_final"] = psi1
    history["psi2_final"] = psi2

    # Phi_T at final state: C_21 = -2*delta*k_ext*psi1/alpha
    C21_final = (-2.0 * params.delta * k_ext * psi1) / params.alpha
    history["phi_T_final"] = C21_final  # C12 = 0

    return history


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

def _assert_close(a: float, b: float, tol: float = 1e-4, label: str = "") -> None:
    if abs(a - b) > tol:
        raise AssertionError(f"FAIL [{label}]: {a} != {b} (tol={tol})")


def _assert_true(condition: bool, label: str = "") -> None:
    if not condition:
        raise AssertionError(f"FAIL [{label}]")


# ---------------------------------------------------------------------------
# Self-tests — reproduce Proposition 1 (T-1 §V)
# ---------------------------------------------------------------------------

def test_flourishing_measure() -> None:
    """F_i is higher for a healthy agent than a degraded one."""
    healthy = AgentState(psi=1.0, E=1.0, E_need=1.0, violations=0.0, externality_cost=0.0)
    degraded = AgentState(psi=0.5, E=0.5, E_need=1.0, violations=0.3, externality_cost=0.2)
    p = FlourishingParams()
    _assert_true(flourishing(healthy, p) > flourishing(degraded, p),
                 label="healthy > degraded flourishing")
    print("PASS  test_flourishing_measure")


def test_grad_phi_T_negative_in_extraction() -> None:
    """grad_Phi_T w.r.t. psi_1 is strictly negative in the extractive scenario."""
    grad = extractive_grad_phi_T(k_ext=0.5)
    _assert_true(grad < 0.0, label="grad_phi_T < 0 (deepening extraction)")
    print("PASS  test_grad_phi_T_negative_in_extraction")


def test_tianxia_term_opposes_extraction() -> None:
    """k5 * grad_Phi_T < 0 opposes Agent 1's psi rise when k5 > 0."""
    c = CascadeCoeffs(k5=1.0)
    grad = extractive_grad_phi_T(k_ext=0.5)
    _assert_true(tianxia_term(grad, c) < 0.0, label="Tianxia term < 0 (opposing extraction)")
    _assert_close(tianxia_term(grad, CascadeCoeffs(k5=0.0)), 0.0,
                  label="k5=0 -> Tianxia term = 0")
    print("PASS  test_tianxia_term_opposes_extraction")


def test_phi_T_negative_at_westphalian_equilibrium() -> None:
    """
    At the Westphalian equilibrium Phi_T < 0: net extraction is the stable outcome.

    Westphalian eq (k2*psi_1 = k4*E1/E_need): psi_1_eq = k4*E1/(k2*E_need)
    Phi_T_W = -2*delta*k_ext * psi_1_eq / alpha
    """
    coeffs = CascadeCoeffs(k4=0.8, k2=0.3, k5=0.0)
    k_ext = 0.5
    params = FlourishingParams()
    psi1_eq = coeffs.k4 * 1.0 / (coeffs.k2 * 1.0)  # E1=E_need=1
    phi_T_W = -2.0 * params.delta * k_ext * psi1_eq / params.alpha
    _assert_true(phi_T_W < 0.0, label="Phi_T < 0 at Westphalian equilibrium")
    print("PASS  test_phi_T_negative_at_westphalian_equilibrium")


def test_proposition_1_westphalian_vs_tianxia() -> None:
    """
    Proposition 1 (T-1 §V): same initial conditions, zero violations in both;
    Westphalian dynamics reach extractive equilibrium (Phi_T < 0);
    Tianxia dynamics (k5 > 0) reach different equilibrium with higher Phi_T.

    Critical: both agents have violations=0, so the Westphalian k3 term cannot
    distinguish them. The Tianxia term is the load-bearing difference.
    """
    # Westphalian (k5=0)
    c_west = CascadeCoeffs(k1=0.2, k2=0.3, k3=0.4, k4=0.8, k5=0.0, Pi_th=0.4, Psi_inv=0.0)
    h_west = simulate_extractive(0.0, 0.0, c_west, k_ext=0.5, steps=300)

    # Tianxia (k5=1.5) — coupling weight comparable to Westphalian terms
    c_tx = CascadeCoeffs(k1=0.2, k2=0.3, k3=0.4, k4=0.8, k5=1.5, Pi_th=0.4, Psi_inv=0.0)
    h_tx = simulate_extractive(0.0, 0.0, c_tx, k_ext=0.5, steps=300)

    # 1. Westphalian: higher psi_1 (less moderation) → more extraction → Phi_T lower
    _assert_true(h_west["psi1_final"] > h_tx["psi1_final"],
                 label="psi1_westphalian > psi1_tianxia (Tianxia moderates Agent 1)")

    # 2. Tianxia Phi_T is higher (less extractive equilibrium)
    _assert_true(h_tx["phi_T_final"] > h_west["phi_T_final"],
                 label="Phi_T_tianxia > Phi_T_westphalian")

    # 3. Westphalian Phi_T at equilibrium is negative (net extraction)
    _assert_true(h_west["phi_T_final"] < 0.0,
                 label="Phi_T_westphalian < 0 (extractive equilibrium)")

    print(
        "PASS  test_proposition_1_westphalian_vs_tianxia\n"
        f"      Westphalian: psi1_final={h_west['psi1_final']:.4f}  "
        f"Phi_T_final={h_west['phi_T_final']:.4f}\n"
        f"      Tianxia:     psi1_final={h_tx['psi1_final']:.4f}  "
        f"Phi_T_final={h_tx['phi_T_final']:.4f}\n"
        "      Both had violations=0 throughout: Tianxia term is load-bearing."
    )


def test_k5_scaling() -> None:
    """Higher k5 produces more moderation of psi_1 at equilibrium (Prediction P-3)."""
    configs = [
        CascadeCoeffs(k1=0.2, k2=0.3, k3=0.4, k4=0.8, k5=k5_val)
        for k5_val in [0.0, 0.5, 1.5, 3.0]
    ]
    finals = [simulate_extractive(0.0, 0.0, c, k_ext=0.5, steps=300)["psi1_final"]
              for c in configs]

    for i in range(1, len(finals)):
        _assert_true(finals[i] < finals[i - 1],
                     label=f"psi1 decreases as k5 increases (k5 index {i})")
    print("PASS  test_k5_scaling")


if __name__ == "__main__":
    test_flourishing_measure()
    test_grad_phi_T_negative_in_extraction()
    test_tianxia_term_opposes_extraction()
    test_phi_T_negative_at_westphalian_equilibrium()
    test_proposition_1_westphalian_vs_tianxia()
    test_k5_scaling()
    print("\nAll tianxia_governance self-tests passed.")
