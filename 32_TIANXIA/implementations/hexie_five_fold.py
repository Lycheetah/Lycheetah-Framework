"""
hexie_five_fold.py — Five-Fold Hexie Composite Operator
TIANXIA v0.3 — W-13

Implements H_5(s) = (I + C + E + O + S) / 5 from FIVE_FOLD_HEXIE_COMPOSITE.md (W-8).

Five components:
  I — Innovation-coherence (革, gé): capacity for constructive transformation
  C — Coordination-coherence (和, hé): inter-agent harmonisation quality [base Hexie]
  E — Ecological-coherence (天人合一): alignment with natural constraints
  O — Openness-coherence (通, tōng): information flow and connectivity
  S — Sharing-coherence (共, gòng): equitable distribution of governance benefits

Self-tests verify component independence, composite ordering, and binding-constraint diagnosis.

Classical source: Analects 13.23, Daodejing ch. 8, Liji Liyun.
Claim status: [SCAFFOLD] — equal weights 1/5 pending E-1-H calibration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HexieState:
    """Five-component governance state for Hexie evaluation."""
    innovation: float   # I(s) — 革 — reform capacity
    coordination: float # C(s) — 和 — stakeholder harmonisation (base Hexie H(s))
    ecological: float   # E(s) — 天人合一 — ecological budget alignment
    openness: float     # O(s) — 通 — information permeability
    sharing: float      # S(s) — 共 — equitable benefit distribution
    label: str = ""

    def __post_init__(self):
        for name, val in [
            ("innovation", self.innovation),
            ("coordination", self.coordination),
            ("ecological", self.ecological),
            ("openness", self.openness),
            ("sharing", self.sharing),
        ]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")


def hexie_five_fold(state: HexieState) -> tuple:
    """
    Returns (I, C, E, O, S, H_5) — the five components and composite score.

    H_5(s) = (I + C + E + O + S) / 5
    """
    I = state.innovation
    C = state.coordination
    E = state.ecological
    O = state.openness
    S = state.sharing
    H5 = (I + C + E + O + S) / 5.0
    return (
        round(I, 4),
        round(C, 4),
        round(E, 4),
        round(O, 4),
        round(S, 4),
        round(H5, 4),
    )


_COMPONENT_NAMES = {
    0: "innovation (革)",
    1: "coordination (和)",
    2: "ecological (天人合一)",
    3: "openness (通)",
    4: "sharing (共)",
}


def binding_constraint(state: HexieState) -> str:
    """
    Proposition H5-1: The binding constraint is the lowest-scoring component.
    Returns the name of the component whose improvement yields the greatest marginal H_5 increase.
    """
    components = [
        state.innovation,
        state.coordination,
        state.ecological,
        state.openness,
        state.sharing,
    ]
    idx = components.index(min(components))
    return _COMPONENT_NAMES[idx]


def hexie_report(state: HexieState, threshold: float = 0.65) -> dict:
    """Full diagnostic report including binding constraint and fragility flags."""
    I, C, E, O, S, H5 = hexie_five_fold(state)
    bc = binding_constraint(state)

    # Fragility flags from NEOCONFUCIAN_HEXIE_EXTENSION — structural/dispositional brittle
    # Here approximated: if coordination (structure) and innovation (disposition) diverge widely
    struct_disp_gap = abs(state.coordination - state.innovation)
    fragility_flag = None
    if struct_disp_gap > 0.35:
        if state.coordination > state.innovation:
            fragility_flag = "structurally_brittle (high coord, low innovation — agents unmotivated)"
        else:
            fragility_flag = "dispositionally_brittle (high innovation, low coord — structure misaligned)"

    return {
        "label": state.label,
        "I_innovation": I,
        "C_coordination": C,
        "E_ecological": E,
        "O_openness": O,
        "S_sharing": S,
        "H5": H5,
        "threshold": threshold,
        "hexie_pass": H5 >= threshold,
        "binding_constraint": bc if H5 < threshold else None,
        "fragility_flag": fragility_flag,
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _assert_close(a: float, b: float, tol: float = 0.001, msg: str = "") -> None:
    assert abs(a - b) < tol, f"Expected {b} ± {tol}, got {a}. {msg}"


def test_composite_arithmetic():
    """Verify H5 computation is correct for reference states."""
    g_a = HexieState(0.28, 0.72, 0.81, 0.76, 0.69, "G_A_innovation_constrained")
    _, _, _, _, _, h5 = hexie_five_fold(g_a)
    _assert_close(h5, (0.28 + 0.72 + 0.81 + 0.76 + 0.69) / 5, msg="G_A H5")

    g_b = HexieState(0.74, 0.72, 0.19, 0.78, 0.71, "G_B_ecological_constrained")
    _, _, _, _, _, h5_b = hexie_five_fold(g_b)
    _assert_close(h5_b, (0.74 + 0.72 + 0.19 + 0.78 + 0.71) / 5, msg="G_B H5")

    g_c = HexieState(0.77, 0.72, 0.75, 0.81, 0.14, "G_C_sharing_constrained")
    _, _, _, _, _, h5_c = hexie_five_fold(g_c)
    _assert_close(h5_c, (0.77 + 0.72 + 0.75 + 0.81 + 0.14) / 5, msg="G_C H5")

    print("  PASS: test_composite_arithmetic")


def test_component_independence():
    """
    Verify components are functionally independent:
    identical base Hexie score (C) but different composite H5 across all three states.
    """
    g_a = HexieState(0.28, 0.72, 0.81, 0.76, 0.69, "G_A")
    g_b = HexieState(0.74, 0.72, 0.19, 0.78, 0.71, "G_B")
    g_c = HexieState(0.77, 0.72, 0.75, 0.81, 0.14, "G_C")

    # All have identical coordination (base Hexie) = 0.72
    assert g_a.coordination == g_b.coordination == g_c.coordination == 0.72, \
        "All states should have identical coordination component"

    # But different H5
    _, _, _, _, _, h5_a = hexie_five_fold(g_a)
    _, _, _, _, _, h5_b = hexie_five_fold(g_b)
    _, _, _, _, _, h5_c = hexie_five_fold(g_c)
    assert h5_a != h5_b != h5_c, "H5 should differ across states with identical base Hexie"

    print(f"  PASS: test_component_independence")
    print(f"    Identical base Hexie (C=0.72), but H5: G_A={h5_a:.3f}, G_B={h5_b:.3f}, G_C={h5_c:.3f}")


def test_binding_constraint_identification():
    """Proposition H5-1: binding constraint is the lowest-scoring component."""
    g_a = HexieState(0.28, 0.72, 0.81, 0.76, 0.69, "G_A")
    g_b = HexieState(0.74, 0.72, 0.19, 0.78, 0.71, "G_B")
    g_c = HexieState(0.77, 0.72, 0.75, 0.81, 0.14, "G_C")

    bc_a = binding_constraint(g_a)
    bc_b = binding_constraint(g_b)
    bc_c = binding_constraint(g_c)

    assert "innovation" in bc_a, f"G_A binding should be innovation, got {bc_a}"
    assert "ecological" in bc_b, f"G_B binding should be ecological, got {bc_b}"
    assert "sharing" in bc_c, f"G_C binding should be sharing, got {bc_c}"

    print(f"  PASS: test_binding_constraint_identification")
    print(f"    G_A binding: {bc_a}")
    print(f"    G_B binding: {bc_b}")
    print(f"    G_C binding: {bc_c}")


def test_composite_ordering():
    """States with same base Hexie produce different H5 ordering — composite ordering holds."""
    g_a = HexieState(0.28, 0.72, 0.81, 0.76, 0.69, "G_A")
    g_b = HexieState(0.74, 0.72, 0.19, 0.78, 0.71, "G_B")
    g_c = HexieState(0.77, 0.72, 0.75, 0.81, 0.14, "G_C")

    _, _, _, _, _, h5_a = hexie_five_fold(g_a)
    _, _, _, _, _, h5_b = hexie_five_fold(g_b)
    _, _, _, _, _, h5_c = hexie_five_fold(g_c)

    # G_A > G_C > G_B from worked example
    assert h5_a > h5_c > h5_b, \
        f"Composite ordering should be G_A > G_C > G_B, got {h5_a:.3f} > {h5_c:.3f} > {h5_b:.3f}"

    print(f"  PASS: test_composite_ordering: G_A({h5_a:.3f}) > G_C({h5_c:.3f}) > G_B({h5_b:.3f})")


def test_fragility_flags():
    """Fragility flags fire when structure-disposition gap is large."""
    # Structurally brittle: high coordination, low innovation
    structurally_brittle = HexieState(0.20, 0.85, 0.70, 0.72, 0.68, "StructBrittle")
    report = hexie_report(structurally_brittle)
    assert report["fragility_flag"] is not None, "Should flag structurally brittle"
    assert "structurally" in report["fragility_flag"]

    # No flag when gap is small
    balanced = HexieState(0.72, 0.72, 0.72, 0.72, 0.72, "Balanced")
    report_b = hexie_report(balanced)
    assert report_b["fragility_flag"] is None, "Balanced state should have no fragility flag"

    print("  PASS: test_fragility_flags")


def test_invalid_input():
    try:
        HexieState(1.1, 0.5, 0.5, 0.5, 0.5)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("  PASS: test_invalid_input")


def run_all_tests():
    print("hexie_five_fold.py — self-tests")
    test_composite_arithmetic()
    test_component_independence()
    test_binding_constraint_identification()
    test_composite_ordering()
    test_fragility_flags()
    test_invalid_input()
    print("All tests passed. [SCAFFOLD — equal weights 1/5 pending E-1-H calibration]")


if __name__ == "__main__":
    run_all_tests()
