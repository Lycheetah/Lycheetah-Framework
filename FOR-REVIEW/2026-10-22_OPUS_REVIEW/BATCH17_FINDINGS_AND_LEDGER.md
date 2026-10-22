# Batch 17 — RV18 mathematics: findings and ledger (review 2026-10-22)

Scope: RV18 of `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md`, which covers the mathematical
foundations: `11_MATHEMATICAL_FOUNDATIONS/`, `TRUTH_PRESSURE/`, `30_MAPS/FORMAL_SPINE.md`, the
math sections of the L0/L6 essentials, and `28_DEFENSE/NOVEL_CONTRIBUTIONS.md`. Nothing here is
inherited from the 2026-10-20 review. The 18 probes in `28_DEFENSE/review_2026_10_20/math_probes.py`
were re-run on the current tree (P0), and every claim below has its own counterexample and control.

Witness: `python3 -B repro_batch17.py <root> <scratch> [<baseline-worktree>]` → **ALL CHECKS HELD**.
Every refutation is paired with a control that must pass.

## Findings

Labels: MEASURED means reproduced by `repro_batch17.py` (check id given). DERIVED means reasoned
from named evidence. DID NOT RUN is kept separate.

| # | Claim (where) | Verdict | Evidence |
|---|---|---|---|
| F1 | DG = I − α∇²S has eigenvalues in (0,1) (`MATHEMATICS_FOUNDATIONS.md` §4.4) | **Refuted, sign reversed.** MEASURED | A1: smallest eigenvalue 1.4 on [0.1, 0.9]; descent runs to p = 1.0, ascent control converges to 0.5; h''(1e−6) = −1e6, so no global L |
| F2 | Norm bound makes D𝒢 negative definite (§3 partial result) | **Refuted.** MEASURED | A2: α·Ao has eigenvalue +0.2 at α = 0.2; control −I |
| F3 | Projection inequality onto H₀ = {S < ε} | **Gap.** The parenthetical is true, but H₀ is not convex. MEASURED | A3: 0/5000 vs 3350/5000 midpoint violations |
| F4 | Φ↑ unitary (`MATHEMATICS_FOUNDATIONS.md`, `lamague_reference.py`) | **Refuted.** Normalized, not unitary. MEASURED | A3 |
| F5 | Π_th ~ √n from random matrix theory (`PI_THRESHOLD_DERIVATION.md`) | **Not derived.** The norms are wrong; BBP threshold θ > 1; a symmetric J cannot undergo Hopf. MEASURED | A4: ‖VVᵀ/n‖ = 1/n, ‖11ᵀ/n‖ = 1; Wigner N = 1200: 1.980 / 2.174 (θ+1/θ = 2.167) / 3.353 (3.333) |
| F6 | Master-equation Lyapunov proof: stable below Π_th, unstable above (`MASTER_EQUATION.md` §4) | **Refuted.** One equilibrium Ψ_inv + forcing/k₂, eigenvalue −k₂ for every Π. MEASURED | A5: 29 values of Π on both sides; control Π = Π_th → Ψ_inv |
| F7 | `PI_DERIVATION.md` "Result: VERIFIED" | **Refuted.** The sympy sketch prints strings; dL/dt < 0 fails just below Ψ_inv. MEASURED | A5 |
| F8 | Theorem C1, invariant preservation (`FORMAL_SPINE.md`) | **Refuted by MP09.** The doc's own parenthetical describes the demotion. MEASURED | P0 (MP09 unchanged) |
| F9 | Theorem A1, AURA floors Coh ≥ 0.70 | **Refuted.** Disclosed contradictions give Coh = 0. MEASURED | A15; control: different domains give Coh = 1 |
| F10 | Theorem M2, sovereignty implies compliance | **Circular**, and the score admits drift. MEASURED | A6: `compute_sovereignty(0.2, 1)` = 0.8; control (0, 1) = 1 |
| F11 | ΔS = −W/T general (`FORMAL_SPINE.md` E1, `06_EARNED_LIGHT_L0/essentials.md`) | **True only for reversible isothermal processes.** MEASURED | A12; MP17 adiabatic counterexample |
| F12 | Theorem 2.2: H non-decreasing under cascade (`CASCADE_FORMAL_PROOFS.md`) | **Refuted.** A renormalized added category can lower H. MEASURED | A8; chain-rule control holds on 2000 joints |
| F13 | Theorem 4.1: AURA constraints preserved | **Refuted in general.** Exact conditions below. MEASURED | A9 |
| F14 | AGM: "fires iff conflicts"; "local consistency" | **Refuted.** The Π margin is also required; lower and tie-band revisions leave 1 contradiction. MEASURED | A13 |
| F15 | HARMONIA C(r) table; Theorem 1.1 | **Table has no single formula; theorem false as stated.** MEASURED | A11 |
| F16 | Incompleteness "F ⊨ G ∧ F ⊬ G" | **Conflicts with the completeness theorem.** DERIVED; citations from memory | — |
| F17 | ANAMNESIS Theorem 3.1, convergent discovery | **Refuted.** A double well gives different limits. MEASURED | A18; single-well control |
| F18 | ANAMNESIS falsifier, equal rates | **Non-discriminating as written.** DERIVED from the text | — |
| F19 | `NOVEL_CONTRIBUTIONS.md` CASCADE rows | C1's own falsifier is met; "cross-domain validation confirmed" is unsupported; the cited path was broken (fixed). DERIVED | P0, A5 |
| F20 | `DIMENSIONAL_ANALYSIS.md` biology row | E can be negative and S can be 0, against the stated ranges. DERIVED from the formulas | — |
| F21 | `chrysopoeia_engine.py`: coherence guarantee, Banach | **Guarantee holds only for c ≤ 13/30; Ξ is stochastic.** MEASURED | A10: largest holding value 0.4300, smallest failing 0.4367; control c = 0.05 → 0.15 |
| F22 | `lyapunov_verification.py` statuses | **Four records overclaim** (see the patch below). MEASURED | A16 and the patched run |
| F23 | One Π_th | **No.** The corpus carries 7 fixed values plus the 2√n family. MEASURED | A17 census |

### A9: exact Theorem 4.1 conditions

For the TES and VTR forms used in the proof, adding one block of ratio r_new to n − 1 old blocks
with mean entropy H_old:

- TES_new ≥ TES_old iff h(r_new) ≤ H_old/n.
- The 0.70 floor holds for every compliant old state iff r_new ≥ 0.9468 (or ≤ 0.0532). This value
  comes from bisection.
- VTR_new ≥ 1 iff v_add ≥ r_add − (V − R).

### A11: HARMONIA numbers

- (3/2)^a ≠ 2^b for a in 1..100.
- The fifth, fourth and third rows fit 1/(1 + a₁/2 − 1/4): .571, .444, .364.
- Summing from k = 1 gives {1: .667, 2: .5, 3/2: .5, 4/3: .444, 5/4: .4}.
- 45/32 = [1; 2, 2, 6]. Neither reading reproduces 0.024.

### A17: Π_th census

The census is a regex over the tree, excluding `FOR-REVIEW/`, `_PROPRIETARY/` and `review_2026_10_20/`.

- Genuine values:
  - 0.4 and 0.5 (`tianxia_governance.py`);
  - 0.6 (E1A pre-registration);
  - 0.8 and 1.5 (`PI_DERIVATION.md`);
  - 0.85 (5 files);
  - 1.2 (10 files);
  - the 2√n family (2, 1.79, 5.66, 17.9).
- False positives dropped: "0" (Re(λ) = 0) and "50" (n = 50).
- `TRUTH_PRESSURE_MASTER_SOURCE_2026-08-03.md:130` already admits three values at n = 50.

### Lyapunov script, run in a clean HEAD worktree without sympy

- **sympy is not installed here.** Six of the committed eleven records ran: 5/6 "passing" against
  the committed 11/11. The five sympy records are **DID NOT RUN**, not failed.
- The CASCADE Lyapunov record is `[VERIFIED]`, whose legend says "symbolic proof confirmed by
  sympy", yet it passed with sympy absent. It checks the script's own `cascade_step`, which
  compresses until no contradictions are left, so non-decrease holds by construction there and
  not in the engine.
- The Hessian record reads `{foundation −0.8, theory 0.05, edge 1.2}` from a fixed table and prints
  "CONFIRMED".
- The CHRYSOPOEIA record passes at mean final entropy 1.0931 nats (8-dim, max ln 8 ≈ 2.079) with
  crystallisation 0.4616. Entropy does not go to 0.
- PSI-CONSENSUS: the f = 4 (44%) known-bad case also gives spread 0.0000 and is labelled
  "CONVERGED — weaker than expected", yet the record passes.

## Repairs made in place (maintained files; no test pins them)

- **Status notes** (`apply_rv18_doc_notes.py`): 24 exact-one swaps in 14 files. Every note is
  inserted after its anchor, keeps the original text, and names its check id. A second run is
  refused. One path was fixed (`NOVEL_CONTRIBUTIONS.md` → `TRUTH_PRESSURE/DIMENSIONAL_ANALYSIS.md`).
  The 14 files are:
  - `MATHEMATICS_FOUNDATIONS.md` (4)
  - `MASTER_EQUATION.md`
  - `PI_THRESHOLD_DERIVATION.md`
  - `PI_DERIVATION.md`
  - `FORMAL_SPINE.md` (4)
  - `CASCADE_FORMAL_PROOFS.md` (2)
  - `AGM_POSTULATE_VERIFICATION.md` (2)
  - `10_HARMONIA_L6/essentials.md` (2)
  - `THE_INCOMPLETENESS_PROOF.md`
  - `ANAMNESIS_FROM_ARCHIVE.md`
  - `07_ANAMNESIS_L0/essentials.md`
  - `06_EARNED_LIGHT_L0/essentials.md`
  - `NOVEL_CONTRIBUTIONS.md` (2)
  - `DIMENSIONAL_ANALYSIS.md`
- **Docstrings** (no behaviour change):
  - `12_IMPLEMENTATIONS/core/chrysopoeia_engine.py`: 6 swaps covering the header,
    `_coagulation`, `coagula`, `find_philosophers_stone`, `solve_et_coagula` and the demo status
    lines. The demo was run, and the new lines print.
  - `12_IMPLEMENTATIONS/core/lamague_reference.py`: 1 swap ("not unitary").

## Staged, not applied

**`RV18_lyapunov_honest_status.patch`** (from `stage_rv18_lyapunov_status.py`; 12 exact-one
swaps).

- Checks: applies to HEAD, `cmp` matches, CR bytes 0.
- New statuses `[ASSIGNED]` and `[INCONCLUSIVE]` are added, and neither counts as passing.
  - The Lyapunov condition becomes `[NUMERICAL]`.
  - The Hessian record becomes `[ASSIGNED]`.
  - CHRYSOPOEIA becomes `[FAILED]` unless mean H < 0.01.
  - PSI becomes `[INCONCLUSIVE]` unless the 44% case diverges.
  - The precedence bug in the CHRYSOPOEIA details string is fixed.
- **Witness:** applied in the HEAD worktree and run without sympy.
  - HEAD reports 5/6 passing (VERIFIED 1, NUMERICAL 4, PENDING 1).
  - The patched script reports **2/6** (NUMERICAL 2, ASSIGNED 1, INCONCLUSIVE 1, PENDING 1,
    FAILED 1).
- It is staged because the committed `lyapunov_verification_results.json` was produced with sympy
  and cannot be regenerated faithfully on this machine.

## Stacking note carried from Batch 16

`RV14_04_BNF_GRAMMAR_parser_status.patch` and `RV17_ratio_status_notes.patch` both touch
`03_LAMAGUE_L1/04_BNF_GRAMMAR.md`. Apply RV14 first; the RV17 hunk then applies at offset 5.

## Decisions for Mac

- **G-LYAP:** land the honest-status patch, and/or install sympy and regenerate the results JSON.
  Without sympy, a regenerated JSON would drop the five sympy records.
- **G-PITH:** choose one Π_th truth: a calibrated constant per domain, or the √n conjecture with
  its normalization stated. Then sweep the census.
- **G-MASTER-EQ:** the master equation as written cannot bifurcate at Π_th. Either restate it as an
  equilibrium shift, or add a Π-dependent term to the restoring force so that stability can
  actually change.
- **G-C1:** exclude foundation blocks from demotion (a behaviour change, so it waits for you), or
  retract C1.

## Checks

- `repro_batch17.py`: ALL CHECKS HELD.
- Stage script: patch applies and matches.
- Patched Lyapunov run: as above.
- Full suite after all Batch 17 edits: **1481 passed, 1 skipped, 1 xfailed**, equal to the
  baseline.
- **DID NOT RUN:** the five sympy records; any check on a phone or screen (not applicable).
