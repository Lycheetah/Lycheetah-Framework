"""Insert RV18 status notes into the maintained math documents (review 2026-10-22).

Usage: python3 -B apply_rv18_doc_notes.py <framework-root>

Each note is an exact-one insertion after an anchor; the original text stays. Every
anchor is checked before any file is written, and a second run is refused. Measured
values come from repro_batch17.py (check ids in brackets).
"""
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
W = "`FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch17.py`"
TAG = "> **Status note (review 2026-10-22, RV18).** "


def note(body, ids):
    return f"\n{TAG}{body} Witness: {W} ({ids}). The original text above is kept.\n"


THERMO = ("ΔS = −W/T holds for a reversible isothermal process: for an ideal gas, reversible "
          "isothermal compression gives ΔS = −W_on/T exactly. It is not general. In a reversible "
          "adiabatic compression W > 0 and ΔS = 0 (MP17). The qualitative Second Law reading stands; "
          "the equation needs its conditions stated.")

EDITS = {
    "11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md": [
        ("For ψ ∉ H₀, the projection satisfies: ⟨Ao(ψ) − ψ, Ao(ψ)⟩ ≤ 0\n", note(
            "The parenthetical is right: {S ≥ ε} is a superlevel set of a concave S and is convex "
            "(0 of 5000 sampled midpoints left it). H₀ = {S < ε} itself is not convex (3350 of 5000 "
            "midpoints left it), so the projection inequality for convex sets does not apply to a "
            "projection onto H₀. The step needs a convex target or a different argument.", "A3")),
        ("*Partial result:* The linearized system near ψ_inv exhibits dS/dt ≤ 0 provided α + β ≤ 1 − γ·||DΨ||. "
         "This is a local stability result, not global.\n", note(
            "A norm bound on D𝒢 controls its size, not its sign, so it cannot make D𝒢 negative "
            "(semi)definite. α·Ao alone has eigenvalue +α on its range (measured +0.2 at α = 0.2; "
            "control: −I is negative definite). The condition α + β ≤ 1 − γ·||DΨ|| therefore does "
            "not imply dS/dt ≤ 0. Read this partial result as UNVERIFIED.", "A2")),
        ("- Generator: ∇_φ (coherence gradient)\n", note(
            "exp(t·X) is unitary only when the generator X is skew-adjoint, and a gradient field is "
            "not skew-adjoint in general. The implemented ascent step adds dt·∇ and renormalizes: its "
            "output has unit norm, but it does not preserve inner products, so it is not unitary, "
            "and normalized steps do not compose as a one-parameter group.", "A3")),
        ("This confirms the ground state structure.\n", note(
            "The sign is reversed. If ∇²S is negative definite, −α·∇²S is positive definite, so the "
            "eigenvalues of I − α·∇²S are greater than 1, not in (0,1). For binary entropy on "
            "[0.1, 0.9] the smallest is 1.4. The map ψ ↦ ψ − α·∇S descends S and runs away from the "
            "maximum (measured: it reaches p = 1.0; the ascent control converges to 0.5). Near the "
            "simplex boundary the curvature is unbounded (h''(1e−6) ≈ −1e6), so no global constant L "
            "exists. What holds is local. Ascent ψ ↦ ψ + α·∇S has Jacobian I + α·∇²S. On a region "
            "whose curvature is bounded by L (L = 11.11 on [0.1, 0.9]), its eigenvalues lie in (0,1) "
            "for 0 < α < 1/L.", "A1")),
    ],
    "TRUTH_PRESSURE/MASTER_EQUATION.md": [
        ("This proves the master equation structure is correct: the system is stable below threshold "
         "and unstable above it, exactly as truth pressure theory predicts.\n", note(
            "The proof does not hold. The pressure term k₁(Π − Π_th) does not depend on Ψ, so the "
            "linear system has one equilibrium, Ψ* = Ψ_inv + [k₁(Π − Π_th) − k₃I_v + k₄E/E_need]/k₂. "
            "Its eigenvalue is −k₂ for every Π. With k₂ > 0 the system is stable both below and above "
            "Π_th. Crossing Π_th moves the equilibrium but does not change its stability, and Ψ_inv is "
            "the equilibrium only when the forcing sums to zero (for example Π = Π_th with I_v = 0 and "
            "E = 0). The Cauchy–Schwarz step also bounds a term linear in ‖Ψ − Ψ_inv‖ by a quadratic "
            "one, which fails near Ψ_inv. Measured: for 29 values of Π on both sides of Π_th the system "
            "converges to Ψ_inv + k₁(Π − Π_th)/k₂, with slope −k₂.", "A5")),
    ],
    "TRUTH_PRESSURE/PI_THRESHOLD_DERIVATION.md": [
        ("**∴ Π_th ~ √(n) from random matrix theory.**\n", note(
            "The norms in §3.3–3.4 are wrong. G = 11ᵀ/n has operator norm 1, and G = VVᵀ/n with "
            "orthonormal V has norm 1/n, not 1/√n (both measured). The exponent of n therefore comes "
            "from how G is normalized, not from the semicircle law. For a Wigner matrix plus θ·uuᵀ, the "
            "top eigenvalue leaves the bulk edge 2 only when θ > 1, and then sits near θ + 1/θ (the BBP "
            "transition, cited from memory). Measured at N = 1200: θ = 0.5 gives 1.980; θ = 1.5 gives "
            "2.174 against 2.167; θ = 3 gives 3.353 against 3.333. The Hopf bifurcation in §4 needs a "
            "complex-conjugate eigenvalue pair, which a symmetric J cannot have. The √n scaling is a "
            "CONJECTURE here, not a derivation. The corpus also uses seven fixed values of Π_th (0.4, "
            "0.5, 0.6, 0.8, 0.85, 1.2, 1.5) beside the 2√n family. The census is in "
            "`FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH17_FINDINGS_AND_LEDGER.md`.", "A4, A17")),
    ],
    "TRUTH_PRESSURE/PI_DERIVATION.md": [
        ("**Result:** VERIFIED. The formula emerges from Lyapunov stability theory.\n", note(
            "The sympy block above prints strings and checks no inequality, so it verifies nothing. "
            "On the master equation's own dynamics dL/dt < 0 fails for states just below Ψ_inv. Read "
            "this result as UNVERIFIED, and see the note in `MASTER_EQUATION.md` §4.", "A5")),
    ],
    "30_MAPS/FORMAL_SPINE.md": [
        ("> (Mathematical guarantee: demotion only moves blocks downward in the pyramid.)\n", note(
            "The parenthetical contradicts the theorem. If demotion moves blocks downward, a "
            "foundation block can leave K_foundation, and probe MP09 "
            "(`28_DEFENSE/review_2026_10_20/math_probes.py`, re-run unchanged) demotes one. C1 is "
            "refuted as stated unless foundation blocks are excluded from demotion.", "P0")),
        ("> concealed contradictions lower Coh; therefore AURA compliance floors Coh.)\n", note(
            "Disclosure does not floor Coh. In the engine, two fully disclosed universal blocks that "
            "contradict each other give Coh = 0 (control: the same blocks in different domains give "
            "Coh = 1). Concealment hides a contradiction from what Coh measures, so it would raise the "
            "measured Coh. The 0.70 floor does not follow from I₂.", "A15")),
        ("> implies AURA compliance.\n", note(
            "The argument assumes its premise by building compliance into the definition of "
            "intended_action. The shipped score is graded: `compute_sovereignty(0.2, 1)` returns 0.8 "
            "(control: `(0, 1)` returns 1). A passing score therefore does not mean μ_drift = 0, and "
            "any threshold at or below 0.8 admits drift 0.2.", "A6")),
        ("> consistent with the Second Law.\n", note(THERMO, "A12")),
    ],
    "11_MATHEMATICAL_FOUNDATIONS/CASCADE_FORMAL_PROOFS.md": [
        ("H(P_new) ≥ H(P_old)\n```\n", note(
            "A permutation leaves H unchanged, and the joint chain rule H(X,Y) ≥ H(X) is true "
            "(control: 2000 random joints). A cascade, however, adds B_new and renormalizes. Adding a "
            "category and renormalizing can lower H: [0.5, 0.5] → [0.01, 0.01, 0.98] drops from 1 bit "
            "to about 0.16 bits. The statement needs a condition on how mass is reassigned.", "A8")),
        ("(TES(P_new) ≥ 0.70 ∧ VTR(P_new) ≥ 1.0 ∧ PAI(P_new) ≥ 0.80)\n```\n", note(
            "The implication does not hold in general. With the TES and VTR forms this proof uses "
            "(defined in the Batch 17 ledger), the exact conditions are as follows. TES_new ≥ TES_old "
            "iff h(r_new) ≤ H_old/n. The 0.70 floor holds for every compliant old state iff "
            "r_new ≥ 0.9468 (or ≤ 0.0532), a value found by bisection. VTR_new ≥ 1 iff "
            "v_add ≥ r_add − (V − R). A cascade that adds a block outside these bounds breaks the "
            "constraint.", "A9")),
    ],
    "11_MATHEMATICAL_FOUNDATIONS/AGM_POSTULATE_VERIFICATION.md": [
        ("Cascade fires if and only if there are conflicts; absent conflicts, result is pure expansion.\n", note(
            "Conflicts are necessary, not sufficient. The engine also requires the new block's Π to "
            "exceed the old block's by more than 0.3. With old Π = 3.0, a revision at 3.5 fires and "
            "leaves 0 contradictions.", "A13")),
        ("CASCADE therefore achieves **local consistency** around the new block: no universal-regime block\n"
         "contradicts A after revision.\n", note(
            "This fails when the cascade does not fire. A conflicting revision with lower Π (1.6) or "
            "inside the tie band (3.2) does not fire and leaves 1 contradiction.", "A13")),
    ],
    "10_HARMONIA_L6/essentials.md": [
        ("| Tritone | 45:32 | 0.024 | CASCADE event — maximum tension |\n", note(
            "No one formula produces this column. The fifth, fourth and third rows fit "
            "1/(1 + a₁/2 − 1/4) for the continued fraction [1; a₁, …] (.571, .444, .364), but the "
            "unison and octave rows do not. Summing from k = 1 instead gives {1: .667, 2: .5, 3/2: .5, "
            "4/3: .444, 5/4: .4}. For the tritone, 45/32 = [1; 2, 2, 6], and neither reading "
            "reproduces 0.024. The implementation rates the tritone 0.99 (PERFECT). Read the table as "
            "SCAFFOLD until one formula reproduces every row.", "A11")),
        ("*This is a real proof via the fundamental theorem of arithmetic.*\n", note(
            "The general statement is false. (3/2)·(2/3) = 1 closes a cycle with ratios that are not "
            "1, and the distinct superparticular ratios 2/1·3/2·…·8/7 multiply to exactly 8 = 2³. What "
            "the fundamental theorem of arithmetic does prove is narrower: (3/2)^a ≠ 2^b for positive "
            "integers a, b, because 3^a is odd (checked for a ≤ 100). That is the Pythagorean comma. It "
            "does not cover every phase cycle.", "A11")),
    ],
    "11_MATHEMATICAL_FOUNDATIONS/THE_INCOMPLETENESS_PROOF.md": [
        ("Corollary: No honest, consistent, self-measuring framework is complete.\n```\n", note(
            "As written, this conflicts with Gödel's completeness theorem. For first-order F, F ⊨ G "
            "implies F ⊢ G, so no G is true in all models of F yet unprovable. The incompleteness "
            "theorems give a sentence that is true in the standard model, not in all models, and "
            "unprovable. They apply to F that is consistent, recursively axiomatizable and interprets "
            "Robinson arithmetic Q; Rosser's form drops ω-consistency. Conditions (i)–(iii) omit "
            "recursive axiomatizability. True arithmetic Th(ℕ) is consistent and complete, so (i)–(iii) "
            "are not enough. These citations are from memory and were not re-read in this review.", "reasoning; no run")),
    ],
    "07_ANAMNESIS_L0/ANAMNESIS_FROM_ARCHIVE.md": [
        ("5. Since Ω(D) is fixed (independent of agent), the intersection of their knowledge sets is "
         "non-empty in the limit. ∎\n", note(
            "Step 3 fails when Ω(D) has more than one component, because gradient ascent goes to the "
            "maximum of the basin it starts in. With Π = −(x² − 1)², climbers starting at −0.5 and "
            "+0.5 reach −1 and +1 (control: a single well gives one limit). A shared attractor set "
            "does not give a shared limit. The theorem needs a unique global attractor in D, and "
            "Corollary 3.1.1 inherits the same assumption.", "A18")),
    ],
    "07_ANAMNESIS_L0/essentials.md": [
        ("convergence is explained by shared embodiment alone.\n", note(
            "The two statements of the prediction disagree. The paragraph above says equal rates mean "
            "embodied mathematics wins, while item 3 has ANAMNESIS predict TC(abstract) ≈ "
            "TC(embodied). The equal-rates outcome is claimed by both sides, so as written the test "
            "cannot discriminate on it. Fix one mapping before pre-registration.", "reading; no run")),
    ],
    "06_EARNED_LIGHT_L0/essentials.md": [
        ("Consciousness requires local entropy decrease (costs energy globally)\n```\n", note(THERMO, "A12")),
    ],
    "28_DEFENSE/NOVEL_CONTRIBUTIONS.md": [
        ("Proven dimensionally consistent across 7 domains (11_MATHEMATICAL_FOUNDATIONS/DIMENSIONAL_ANALYSIS.md).",
         "Proven dimensionally consistent across 7 domains (TRUTH_PRESSURE/DIMENSIONAL_ANALYSIS.md).", "replace"),
        ("\n### AURA\n", note(
            "The C1 row's own falsifier, \"a valid CASCADE update that loses an invariant\", is met by "
            "probe MP09, which demotes a foundation block (see `30_MAPS/FORMAL_SPINE.md` C1). On the Π "
            "row: normalized E, P and S make Π dimensionless by construction, which is not validation. "
            "No cross-domain dataset is cited for \"Cross-domain validation confirmed\". The Lyapunov "
            "derivation fails (see `TRUTH_PRESSURE/MASTER_EQUATION.md` §4). The dimensional-analysis "
            "path in that row was corrected in this review; the file is in `TRUTH_PRESSURE/`.",
            "P0, A5") + "\n### AURA\n", "replace"),
    ],
    "TRUTH_PRESSURE/DIMENSIONAL_ANALYSIS.md": [
        ("| S | Population effective size stability | S = 1 − (N_t − N_{t−1})² / N_max² (stability index) |\n", note(
            "This row breaks the ranges stated in the summary below. E = (W_trait − W_mean)/W_max is "
            "negative for a below-mean trait, against E ∈ [0, 1]. S = 0 when |N_t − N_{t−1}| = N_max, "
            "against S ∈ (0, 1]. The row needs a clamp or |W_trait − W_mean|, and a bound on the "
            "population step.", "reading; no run")),
    ],
}

texts = {}
for rel, swaps in EDITS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "review 2026-10-22, RV18" not in text, f"{rel}: already applied"
    for old, new, *mode in swaps:
        n = text.count(old)
        assert n == 1, (rel, old[:60], n)
        text = text.replace(old, new if mode == ["replace"] else old + new)
    texts[rel] = text
for rel, text in texts.items():
    (ROOT / rel).write_text(text, encoding="utf-8")
print(f"notes inserted: {sum(len(s) for s in EDITS.values())} swaps in {len(EDITS)} files")
