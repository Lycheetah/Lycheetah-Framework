# BATCH 38 — Mathematical checklist M1–M18

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-23 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

The source is the checklist's mathematical section (M1–M18). Each item maps to the 2026-10-20 findings table (`28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md`, "Mathematical findings", probes MP01–MP18). RV36 (BATCH35) already reproduced all 18 probes byte-exactly from `math-probes.json`. This batch does not repeat that work. It is an **independent re-derivation**: a fresh instrument that does not import `math_probes.py`. Where a finding could be narrowed to a true theorem, the batch also looks for the corrected form.

## Coverage, stated honestly

- **Re-derived independently** by `repro_math_m1_m18.py` (stdlib + numpy, relative paths, read-only): M1, M2, M4, M5, M6, M9, M10, M12, M13, M17, M18.
- **Read-confirmed only** against the RV36 byte-exact reproduction and the RV18 status notes (BATCH17): M3, M7, M8, M11, M14, M15, M16. They were not re-derived here.
- **Read:** the RV18 status notes in `MATHEMATICS_FOUNDATIONS.md`, `30_MAPS/FORMAL_SPINE.md`, Harmonia and Earned Light `essentials.md`, and `MASTER_EQUATION.md`; the `barlow_dissonance` code path; `lyapunov_verification.py`; the eight affected `CLAIMS.json` rows; and the RV19 claim overlay.
- **DID NOT RUN:** `ruff` (the venv was lost in the reboot) and sympy-backed symbolic checks (sympy is absent, so the Lyapunov suite marks one claim PENDING).

## Instrument

`repro_math_m1_m18.py` prints one line per check and a tally. It exits non-zero on any FAIL.

- **Harness control:** a planted false expectation is caught as FAIL inside the harness.
- **First run:** M12 FAIL and M5 DID NOT RUN. The M5 TRIAD kernel needed constructor arguments (fixed). The M12 failure was a real defect in the repository, described below; the check now asserts that the defect reproduces and carries a full sweep.
- **Final run:** `{'PASS': 35, 'FAIL': 0, 'DID NOT RUN': 0}`, exit 0. The earlier tally of 34 changed when the R3 repair turned the single M17 check into two: one confirms that HEAD still sums NUMERICAL into "passing", the other that the working tree separates them. The first post-R3 run reported the old M17 check as FAIL, because it looked for the pre-repair pattern. The check was rewritten, not the repair undone.

## Per-item status

| M | 10-20 finding | This review | Status |
|---|---|---|---|
| M1 | TRIAD Jacobian sign | Reproduces: written step 1.47619; the MP01 point is not a fixed point (S′(0.7) = −0.8473). **New: the conclusion survives at a genuine coherence peak above ½** (see N1). | MEASURED + DERIVED |
| M2 | Generator bound | Reproduces: eigenvalues 0.1 ± 0.1414i. **New: as a discrete map the bound is a valid non-expansion** (see N2). | MEASURED + DERIVED |
| M3 | Actual tracker | Read-confirmed (RV36, RV18 notes; `triad_tracker.py` docstring already carries the Banach caveat) | not re-derived |
| M4 | Convexity / unitarity | Sublevel set not convex: zero-entropy endpoints, maximum-entropy midpoint | MEASURED |
| M5 | √n threshold | ‖VVᵀ/n‖ = 1/n for n = 16, 64, 100; ‖11ᵀ/n‖ = 1; the implemented ascent is not linear | MEASURED |
| M6 | Master equation | Equilibrium shifted to −0.1333; dV/dt > 0 at e = −0.01 and −0.1; control at Π = Π_th behaves | MEASURED |
| M7 | Sovereignty ⇒ AURA | Read-confirmed (RV36; RV19 overlay "agree") | not re-derived |
| M8 | Foundation preservation | Read-confirmed (RV36) | not re-derived |
| M9 | Information preservation | Shannon entropy can fall when outcomes are added | MEASURED |
| M10 | AURA metric preservation | TES falls below the floor; VTR = 0.55 < 1 with positive value | MEASURED |
| M11 | Chrysopoeia | Read-confirmed (RV36; `chrysopoeia_engine.py` already notes c ≤ 13/30 and Banach SCAFFOLD) | not re-derived |
| M12 | Harmonia | Narrow comma holds; telescoping product = 8; formula vs table mismatch {1: 1/2, 2: 1/3, 3/2: 1/3}. **New: the implemented consonance proxy cannot discriminate** (see N4). | MEASURED |
| M13 | Thermodynamics | Adiabatic counterexample reproduces. **New: corrected law stated and witnessed** (see N3). | MEASURED + DERIVED |
| M14 | AGM | Read-confirmed (RV36) | not re-derived |
| M15 | Incompleteness | Read-confirmed (RV36; RV18 note) | not re-derived |
| M16 | Anamnesis | Read-confirmed (RV36) | not re-derived |
| M17 | "11/11 verified" | Hessian table is a literal; NUMERICAL is summed into "passing". **Today's run: 1/6 symbolic, 4/6 numerical only, 1/6 PENDING, 0 failed.** Output wording repaired (R3). The instrument checks both states: HEAD sums, the working tree separates. | MEASURED |
| M18 | Novelty / normalisation | W_trait=8, W_mean=10, W_max=20 gives E = −1/10, outside [0, 1] | MEASURED |

## New findings beyond the 2026-10-20 probes

- **N1 — M1 rescue (DERIVED, numeric witness).** For S = h(C(ψ)), a fixed point of the ascent needs ∇C = 0 whenever C ≠ ½. There ∇²S = h′(C)·∇²C. For C > ½, h′ < 0, so a coherence peak gives ∇²S ⪰ 0 and DG = I − α∇²S has eigenvalues in (0, 1] for small α.
  - Witness: a peak of 0.9 gives eigenvalues 0.956056, and the iterates converge to 5.9e−40.
  - Known-bad: a peak of 0.4 gives 1.008109.
  - MP01's point (C = 0.7, ∇C ≠ 0) is not a fixed point, which is why the printed inference fails there. RV18 already stated the ascent rescue; the fixed-point argument is new.
- **N2 — M2 discrete form (DERIVED, sampled witness).** ‖D𝒢‖ ≤ α + β + γ‖DΨ‖ is a valid non-expansion bound for the map ψ ↦ 𝒢(ψ). It holds when ‖DAo‖ ≤ 1 and ‖DΦ↑‖ ≤ 1; the normalised ascent does not guarantee the second. It says nothing about continuous time.
  - Witness: the same matrix has spectral radius 0.1732 as a map, and real part +0.1 as a flow.
  - Sampled admissible cases: the largest norm was 0.991138, always ≤ 1.
- **N3 — M13 corrected law (DERIVED from the Second Law, witnessed).** At constant T, W ≥ ΔF. With ΔU = 0 this gives ΔS ≥ −W/T, with equality only for reversible processes.
  - Benign controls: reversible isothermal (equality) and free expansion (strict).
  - Scope guard: the adiabatic case changes T, so the bound does not apply there.
  - The bits-to-J/K bridge (k_B ln 2) is still unstated in the source.
- **N4 — M12 Harmonia proxy cannot discriminate (MEASURED).** `barlow_dissonance` measures the log2 distance to the nearest p/q with q ≤ 12. It does no prime factorisation.
  - Minimum consonance over 20,001 ratios in [1, 2] is **0.9196, at r = 1.0409**.
  - The 45/32 tritone scores 0.9904 and is labelled **"PERFECT (highly consonant)"**.
  - The existing tests pass for the wrong reason: every ratio passes.

## Repairs (working tree)

Backups are in the session scratchpad under `m_bak/`.

- **R1:** `12_IMPLEMENTATIONS/core/harmonia_calculator.py` (CRLF preserved). The `barlow_dissonance` docstring now separates the specification from what the code computes and states the measured non-discrimination. No behaviour change, because the metric redesign is Mac's (G-M-2).
- **R2:** `tests/test_harmonia_calculator.py`, new class `TestConsonanceDiscrimination`, with a strict-xfail test `test_tritone_is_not_perfect`. It will turn into an XPASS failure the day the metric starts discriminating, which forces the marker to be removed.
- **R3:** `11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification.py`.
  - The summary now prints symbolic and numerical-only tallies separately instead of a summed "verified or numerically confirmed" figure.
  - The JSON report carries `symbolic` and `numerical_only` in place of `passing`. No code reads that key; the tracked `lyapunov_verification_results.json` is unchanged.
  - Disclosure: the first edit left the `passing` reference in the JSON block, so a run raised NameError after printing the summary and before writing anything. The bug was caught on the first run and fixed. The witness run then used a scratch copy and exited 0.
- **R4:** `12_IMPLEMENTATIONS/core/earned_light_calculator.py`. The module header changes `ΔS = −W/T` to `ΔS ≥ −W/T`, with scope (isothermal, ΔU = 0, equality only when reversible).
- **R5:** dated review addenda, each placed after the existing RV18 note, original text kept:
  - N1 and N2 in `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md`;
  - N3 in `30_MAPS/FORMAL_SPINE.md` and `06_EARNED_LIGHT_L0/essentials.md`.
- **R6:** new `repro_math_m1_m18.py` (this folder).

**No CLAIMS.json patch was staged.** RV19 already carries every affected row in `RV19_claim_review_overlay.json` (author status kept, 10-20 classification, this review's verdict). A second status patch would create a parallel truth. This batch's sharpenings are recorded here for the next overlay rebuild:

- ELI-003: the corrected inequality (N3).
- HAR-002: the narrow result holds, and the implementation proxy cannot discriminate (N4).
- LYV-001: today's tally is 1/6 symbolic, without sympy.
- TRI-006 / LYV-002: the discrete non-expansion form (N2) is the honest Banach-adjacent statement. Contraction is still not shown in general.

## Witnesses

| Witness | Result |
|---|---|
| `repro_math_m1_m18.py` (with harness control and known-bad cases) | 35 PASS, 0 FAIL, 0 DID NOT RUN, exit 0 |
| Harmonia tests | 24 passed, 1 xfailed (strict) |
| Doc and claims gates after the addenda (`-k spine/claim/doc/...`) | 77 passed, 1 skipped |
| Focused `-k earned/lyapunov/harmonia/claim` after R3 and R4 | 101 passed, 1 skipped, 1 xfailed |
| `lyapunov_verification.py`, scratch copy, after the repair | exit 0; summary 1 / 4 / 1 / 0; JSON written with the new keys |
| `ruff` | DID NOT RUN |
| Full suite | not rerun for this batch. It runs once, alone, at the end of the review. |

## G-items for Mac

- **G-M-1 — claim statuses.** MIC-003, ELI-003, CAS-003 (counterexample or mismatch) and LYV-001 (unsupported) are still ACTIVE. The ruling stays with you, through the existing G-RV19 overlay. Options: (a) keep ACTIVE with the overlay as the visible dissent; (b) move them to SCAFFOLD and restate ELI-003 as N3; (c) RETRACTED for MIC-003 only. Sol leans to (b), because each claim has a true narrower successor except MIC-003, whose successor needs the compliant-intention premise put back in.
- **G-M-2 — Harmonia metric.** Implement the prime-factor specification, recalibrate the tests, and lift the strict xfail. This one is yours because it changes the numbers every Harmonia output reports.
- **G-M-3 — "11/11" mirrors.** `papers/LYCHEETAH_SYNTHESIS_v0.1` and the other mirrors still say 11/11. Point them at the R3 tally, or at the RV19 note. Some "11/11" hits are unrelated (frontier controls), so the sweep needs reading, not a global replace.
- **G-M-4 — promoting N1–N3 into the theorem text.** The addenda sit beside the original statements as review notes. Do you want them written into the theorems as the corrected statements?
