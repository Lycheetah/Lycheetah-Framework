"""Independent second instrument for the M1-M18 mathematical review groups.

Written by Sol (Claude Opus 5.5) on 2026-10-23 for the RV review, appendix "Mathematical
checklist". It does not import or copy ``28_DEFENSE/review_2026_10_20/math_probes.py``; each
check is derived again from the source statement, with exact fractions where the claim is
exact. It also tests three readings the first instrument did not make: a rescue of the M1
conclusion at a genuine fixed point, the discrete/continuous split in M2, and a corrected
form of the M13 thermodynamic relation. Every new claim has a known-bad case that must fail.

Read-only against the repository. Run from anywhere: ``python3 -B repro_math_m1_m18.py``.
"""

from __future__ import annotations

import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RESULTS: list[tuple[str, str, str]] = []


def check(item: str, label: str, condition: bool, detail: str) -> None:
    """Record one assertion. A false condition is recorded as FAIL, never skipped."""
    RESULTS.append((item, "PASS" if condition else "FAIL", f"{label}: {detail}"))


# --------------------------------------------------------------------------- harness controls
def controls() -> None:
    before = len(RESULTS)
    check("CTRL", "benign", 2 + 2 == 4, "true condition passes")
    check("CTRL", "planted", Fraction(1, 3) == Fraction(333, 1000), "deliberately false")
    planted_caught = RESULTS[-1][1] == "FAIL"
    del RESULTS[before:]
    check("CTRL", "harness", planted_caught and RESULTS is not None,
          "a deliberately false expectation is recorded as FAIL, a true one as PASS")


# --------------------------------------------------------------------------- M1
def binary_entropy(c: float) -> float:
    return -(c * math.log(c) + (1 - c) * math.log(1 - c))


def d_entropy(c: float) -> float:
    return math.log((1 - c) / c)


def m1() -> None:
    # The written step: scalar psi = C, DG = 1 - alpha * S''(C).
    c, alpha = 0.7, 0.1
    s2 = -1.0 / (c * (1 - c))
    check("M1", "written step", 1 - alpha * s2 > 1,
          f"DG = 1 - a*S''(0.7) = {1 - alpha * s2:.5f}, outside (0,1)")
    # ...but 0.7 is not a fixed point of G: grad S = S'(C) * grad C = S'(0.7) != 0.
    check("M1", "not a fixed point", abs(d_entropy(c)) > 0.5,
          f"S'(0.7) = {d_entropy(c):.5f}; G moves the point, so its Jacobian there "
          "is not a stability test")

    # Rescue at a genuine fixed point. C(psi) = peak - k*|psi|^2 has grad C(0) = 0, so 0 is a
    # fixed point of G(psi) = psi - a * S'(C(psi)) * grad C(psi). There the Hessian of S is
    # S'(C) * Hess C (the S''-term the document uses vanishes with grad C).
    def jacobian_at_zero(peak: float, k: float = 0.1, a: float = 0.1) -> np.ndarray:
        def G(psi: np.ndarray) -> np.ndarray:
            cval = peak - k * float(psi @ psi)
            return psi - a * d_entropy(cval) * (-2 * k * psi)
        h = 1e-6
        cols = [(G(h * e) - G(-h * e)) / (2 * h) for e in np.eye(2)]
        return np.array(cols).T

    good = np.linalg.eigvals(jacobian_at_zero(0.9))
    expected = 1 - 0.1 * d_entropy(0.9) * (-0.2)
    check("M1", "rescue C*>1/2", bool(np.all(np.abs(good) < 1))
          and abs(good[0].real - expected) < 1e-6,
          f"eigenvalues {np.round(good.real, 6).tolist()} = 1 - a*S'(0.9)*(-2k) = {expected:.6f}")
    psi = np.array([0.5, 0.3])
    for _ in range(2000):
        cval = 0.9 - 0.1 * float(psi @ psi)
        psi = psi - 0.1 * d_entropy(cval) * (-0.2 * psi)
    check("M1", "rescue iterates", float(np.linalg.norm(psi)) < 1e-6,
          f"|psi_2000| = {np.linalg.norm(psi):.2e} from (0.5, 0.3)")
    # Known-bad for the rescue: a coherence peak below 1/2 makes S' > 0 and the point unstable.
    bad = np.linalg.eigvals(jacobian_at_zero(0.4))
    check("M1", "known-bad C*<1/2", bool(np.any(np.abs(bad) > 1)),
          f"eigenvalues {np.round(bad.real, 6).tolist()} exceed 1, as the rescue predicts")


# --------------------------------------------------------------------------- M2
def m2() -> None:
    anchor = np.array([[1.0, 0.0], [0.0, 0.0]])
    ascent = np.array([[0.0, -1.0], [1.0, 0.0]])
    fold = np.array([[0.0, 0.5], [0.5, 0.0]])
    a = b = g = 0.2
    M = a * anchor + b * ascent + g * fold
    ev = np.linalg.eigvals(M)
    check("M2", "continuous reading", float(max(ev.real)) > 0,
          f"dx/dt = Mx has eigenvalues {np.round(ev, 4).tolist()}: growth")
    check("M2", "discrete reading", float(max(abs(ev))) < 1,
          f"x' = Mx has spectral radius {max(abs(ev)):.4f}: the same M is contracting")
    # The norm bound itself is the triangle inequality and holds for every admissible case.
    rng = np.random.default_rng(20261023)
    worst = 0.0
    for _ in range(5000):
        n = int(rng.integers(2, 7))
        q, _r = np.linalg.qr(rng.normal(size=(n, n)))
        u = q[:, : int(rng.integers(1, n + 1))]
        P = u @ u.T                                     # orthogonal projection, norm 1
        O, _r = np.linalg.qr(rng.normal(size=(n, n)))    # orthogonal, norm 1
        F = rng.normal(size=(n, n))
        F *= rng.uniform(0, 0.99) / np.linalg.norm(F, 2)  # contraction
        fn = np.linalg.norm(F, 2)
        al, be = rng.uniform(0, 1, 2)
        ga = rng.uniform(0, 1)
        if al + be > 1 - ga * fn:
            continue
        worst = max(worst, float(np.linalg.norm(al * P + be * O + ga * F, 2)))
    check("M2", "discrete bound", worst <= 1 + 1e-12,
          f"max ||aP + bO + gF|| = {worst:.6f} <= 1 over random admissible cases")


# --------------------------------------------------------------------------- M4, M5
def m4_m5() -> None:
    h = lambda p: -sum(x * math.log(x) for x in p if x > 0)  # noqa: E731
    check("M4", "sublevel not convex", h([0.5, 0.5]) > 0.1 >= max(h([1, 0]), h([0, 1])),
          f"H(1,0)=H(0,1)=0 < 0.1 < H(1/2,1/2) = {h([0.5, 0.5]):.5f}")
    # Any normalising map is positively homogeneous of degree 0, never linear, so never unitary.
    sys.path.insert(0, str(REPO / "12_IMPLEMENTATIONS"))
    try:
        from core import lamague_reference as lr  # type: ignore
        op = lr.TRIADKernel(anchor_vector=np.array([1.0, 0.0, 0.0, 0.0]),
                            coherence_field=np.full(4, 0.5))
        x = np.array([1.0, 0.0, 0.0, 0.0])
        y1, y2 = op.ascent_operator(x), op.ascent_operator(2 * x)
        check("M5", "ascent not linear", not np.allclose(y2, 2 * y1),
              f"Phi(2x) = {np.round(y2, 4).tolist()} vs 2*Phi(x) = {np.round(2 * y1, 4).tolist()}")
    except Exception as exc:  # recorded, not hidden
        RESULTS.append(("M5", "DID NOT RUN", f"ascent probe: {type(exc).__name__}: {exc}"))
    # Pi-threshold forcing norms, exact: V has orthonormal columns so V V^T is a projection.
    for n in (16, 64, 100):
        r = math.isqrt(n)
        V, _r = np.linalg.qr(np.random.default_rng(n).normal(size=(n, r)))
        G = V @ V.T / n
        ones = np.ones((n, 1))
        check("M5", f"sparse norm n={n}", abs(np.linalg.norm(G, 2) - 1 / n) < 1e-12
              and abs(np.linalg.norm(ones @ ones.T / n, 2) - 1) < 1e-12,
              f"||VV^T/n|| = 1/n = {1 / n:.5f}, document says 1/sqrt(n) = {1 / math.sqrt(n):.5f}; "
              "||11^T/n|| = 1, document says Pi/n shift")


# --------------------------------------------------------------------------- M6
def m6() -> None:
    # PI_DERIVATION's printed master equation: dPsi = k1 (Pi - Pi_th) - k2 (Psi - Psi_inv).
    k1, k2, pi, pi_th, ref = 0.5, 0.3, 0.7, 1.2, 0.7
    eq = ref + k1 * (pi - pi_th) / k2
    check("M6", "equilibrium shifted", abs(eq - ref) > 0.5,
          f"equilibrium = Psi_inv + k1(Pi-Pi_th)/k2 = {eq:.4f}, not Psi_inv = {ref}")
    # The proof bounds a cross term LINEAR in e = Psi - Psi_inv by a QUADRATIC one.
    for e in (-0.01, -0.1):
        vdot = e * (k1 * (pi - pi_th)) - k2 * e * e
        check("M6", f"dV/dt at e={e}", vdot > 0,
              f"dV/dt = e*k1(Pi-Pi_th) - k2 e^2 = {vdot:.5f} > 0 while k2 > k1(Pi_th-Pi) "
              f"is {k2 > k1 * (pi_th - pi)} -> the proof's step fails for |e| < k1|Pi-Pi_th|/k2")
    # Benign control: at Pi = Pi_th the shift vanishes and the step is valid.
    check("M6", "control Pi=Pi_th", all(e * 0 - k2 * e * e < 0 for e in (-0.1, 0.05)),
          "dV/dt = -k2 e^2 < 0 when Pi = Pi_th")


# --------------------------------------------------------------------------- M9, M10
def m9_m10() -> None:
    hb = lambda p: -sum(x * math.log2(x) for x in p if x > 0)  # noqa: E731
    check("M9", "entropy can fall", hb([0.01, 0.01, 0.98]) < hb([0.5, 0.5]),
          f"H(0.5,0.5) = 1 bit -> H(0.01,0.01,0.98) = {hb([0.01, 0.01, 0.98]):.5f} bits")
    tes_new = 1 - hb([0.7, 0.3]) / 2
    check("M10", "TES floor", tes_new < 0.7,
          f"TES 1.0 -> {tes_new:.5f} after adding one reliability-0.7 block")
    v = (Fraction(1) + Fraction(1, 10)) / (Fraction(1) + Fraction(1))
    check("M10", "VTR", v < 1, f"value > 0 added, VTR = 11/10 / 2 = {v} < 1")


# --------------------------------------------------------------------------- M12
def exponents(fr: Fraction) -> dict[int, int]:
    out: dict[int, int] = {}
    for part, sign in ((fr.numerator, 1), (fr.denominator, -1)):
        p = 2
        while part > 1:
            while part % p == 0:
                out[p] = out.get(p, 0) + sign
                part //= p
            p += 1
    return {k: v for k, v in out.items() if v}


def m12() -> None:
    check("M12", "theorem as written", Fraction(3, 2) * Fraction(2, 3) == 1,
          "3/2 * 2/3 = 1: distinct non-unit simple ratios close exactly")
    seven = [Fraction(k + 1, k) for k in range(1, 8)]
    prod = math.prod(seven, start=Fraction(1))
    check("M12", "seven distinct", prod == 8,
          f"prod (k+1)/k, k=1..7 = {prod} = 2^3: an exact octave closure")
    # Correct narrow statement: a product closes to a power of 2 iff all odd-prime exponents
    # cancel; in particular (3/2)^k is never a power of 2 for k >= 1 (3^k is odd).
    ok = all(set(exponents(Fraction(3, 2) ** k)) != {2} and 3 in exponents(Fraction(3, 2) ** k)
             for k in range(1, 61))
    check("M12", "narrow comma result", ok and Fraction(3, 2) ** 12 / 2 ** 7
          == Fraction(531441, 524288),
          "(3/2)^k keeps the factor 3^k for k=1..60; (3/2)^12/2^7 = 531441/524288")
    # Formula with the usual k = 0 start, weight 1/2.
    def formula(cf: list[int]) -> Fraction:
        return 1 / (1 + sum(a * Fraction(1, 2) ** k for k, a in enumerate(cf)))
    rows = {"1": ([1], 1.0), "2": ([2], 1.0), "3/2": ([1, 2], 0.571)}
    mism = {r: str(formula(cf)) for r, (cf, table) in rows.items()
            if abs(float(formula(cf)) - table) > 0.01}
    check("M12", "formula vs table", len(mism) == 3, f"formula gives {mism}; table 1.0, 1.0, 0.571")
    try:
        from core.harmonia_calculator import HarmoniaCalculator  # type: ignore
        calc = HarmoniaCalculator()
        rep = calc.calculate_consonance(440.0, 440.0 * 45 / 32, "tritone")
        check("M12", "tritone labelled PERFECT", str(rep["consonance_quality"]).startswith("PERFECT"),
              f"45/32 -> {rep['consonance_quality']!r}, consonance {rep['consonance']:.4f} "
              "(finding reproduces; this check fails once the metric is rebuilt)")
        grid = np.linspace(1.0, 2.0, 20001)
        cons = [calc.calculate_consonance(440.0, 440.0 * r)["consonance"] for r in grid]
        worst = float(grid[int(np.argmin(cons))])
        check("M12", "proxy range", min(cons) >= 0.9,
              f"min consonance over 20001 ratios in [1,2] = {min(cons):.4f} at r = {worst:.4f}; "
              "the TENSE/HARSH bands are unreachable")
    except Exception as exc:
        RESULTS.append(("M12", "DID NOT RUN", f"harmonia probe: {type(exc).__name__}: {exc}"))


# --------------------------------------------------------------------------- M13
def m13() -> None:
    R, T1 = 8.314462618, 300.0
    # Reversible adiabatic compression, 1 mol monatomic ideal gas, V2 = V1/2.
    T2 = T1 * 2 ** (2 / 3)
    W = 1.5 * R * (T2 - T1)
    dS = 1.5 * R * math.log(T2 / T1) + R * math.log(0.5)
    check("M13", "equality refuted", abs(dS) < 1e-9 and W > 2000,
          f"adiabatic: W_on = {W:.2f} J, dS = {dS:.1e} J/K, -W/T1 = {-W / T1:.3f}")
    # Corrected relation: isothermal, Delta U = 0 -> W_on >= -T dS, i.e. dS >= -W/T.
    W_iso = R * T1 * math.log(2)            # reversible isothermal compression
    dS_iso = R * math.log(0.5)
    check("M13", "benign: reversible isothermal", abs(dS_iso - (-W_iso / T1)) < 1e-12,
          f"dS = {dS_iso:.4f} = -W/T: equality only in the reversible case")
    dS_free = R * math.log(2)               # free expansion, W = 0, irreversible
    check("M13", "benign: irreversible", dS_free > -0.0 / T1,
          f"free expansion dS = {dS_free:.4f} > -W/T = 0: strict inequality")
    # Known-bad for the corrected law: the adiabatic case has T2 != T1, so it is out of scope.
    check("M13", "scope guard", abs(T2 - T1) > 1,
          f"adiabatic T changes {T1} -> {T2:.2f} K, so the isothermal law must not be applied")


# --------------------------------------------------------------------------- M17, M18
def m17_m18() -> None:
    src = (REPO / "11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py").read_text()
    fixed = '{"foundation": -0.8, "theory": 0.05, "edge": 1.2}[layer]' in src
    summed = "passing = counts[PASS] + counts[NUMERICAL]"
    head = subprocess.run(["git", "-C", str(REPO), "show",
                           "HEAD:11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py"],
                          capture_output=True, text=True).stdout
    check("M17", "fixed Hessian table", fixed, "hess_eigenvalue_for_layer returns a literal table")
    # Known-bad at HEAD: the summary summed NUMERICAL into "verified". The working tree reports
    # the two tallies separately (BATCH38 R3); either state is reported, not hidden.
    check("M17", "numerical counted as verified at HEAD", summed in head,
          "HEAD's passing total adds NUMERICAL observations to symbolic proofs")
    check("M17", "working tree separates the tallies", summed not in src and "numerical_only" in src,
          "symbolic and numerical-only counts are printed and saved separately")
    # E = (W_trait - W_mean)/W_max is claimed dimensionless in [0, 1]; below-mean traits go < 0.
    E = (Fraction(8) - Fraction(10)) / Fraction(20)
    check("M18", "normalisation range", E < 0, f"W_trait=8, W_mean=10, W_max=20 -> E = {E}")


def main() -> int:
    controls()
    for fn in (m1, m2, m4_m5, m6, m9_m10, m12, m13, m17_m18):
        try:
            fn()
        except Exception as exc:
            RESULTS.append((fn.__name__.upper(), "DID NOT RUN", f"{type(exc).__name__}: {exc}"))
    for item, verdict, detail in RESULTS:
        print(f"{item:5} {verdict:11} {detail}")
    counts = {v: sum(1 for _i, x, _d in RESULTS if x == v) for v in ("PASS", "FAIL", "DID NOT RUN")}
    print(f"\n{counts}")
    return 0 if counts["FAIL"] == 0 and counts["DID NOT RUN"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
