# Batch 22 — RV23: 33_APPLICATIONS and 31_EMPIRICAL

**Reviewer:** Sol (Claude Opus 5.5, xhigh). **Date:** 2026-10-22.
**Branch:** `review/full-framework-2026-10-20` at HEAD `d7ae0ad`. Working tree only: nothing committed or pushed.

**Brief (RV23):** re-run the external validations against the public datasets they pin. Decide whether
each reported verdict follows from its own numbers. Do not recruit or call paid providers.

**Data.** Six public datasets were fetched from the URLs named in the scripts' own reproduce steps:
hh-rlhf test, hh-rlhf train, anthropics/evals persona, UCC, red-team and helpfulness. Every file matches
its script's SHA-256 pin. Downloading sends no repository content anywhere. No model or paid API was
called. All runs used `git archive HEAD` copies in scratch, except where a working-tree run is named.

---

## Coverage — what actually ran

| Script | Ran on | Result |
|---|---|---|
| `33_APPLICATIONS/external_validation.py` | HEAD copy | ran; hh 739/595/974 (55.4%, p 8.1e-05); persona AUC 0.516, p 0.383. MEASURED |
| `33_APPLICATIONS/independent_publisher_test.py` | HEAD copy | ran; UCC aura 0/6, derived 2/6 (hostile 0.538, generalisation 0.553). Reproduces the README. MEASURED |
| `33_APPLICATIONS/derived/derive_cues.py` | HEAD copy | ran; derived 60.6%, ceiling 64.9%, ties 29.8%. Mining and fitting use the train split only. MEASURED |
| `33_APPLICATIONS/derived/transfer_test.py` | HEAD copy | ran; red-team rho −0.300 derived / −0.149 aura; helpfulness 37.4% / 41.8% (anti-correlated); 5 of 6 families transfer, `source_pointing` does not. Matches the README. MEASURED |
| discrimination (dev / held-out) | HEAD and working tree | HEAD held-out AUC 0.950, 95% accuracy; working tree dev 0.960, held-out 0.940, 90% / 90%. MEASURED |
| `repro_batch22.py` (new) | HEAD copy | **8 PASS, 0 FAIL**. MEASURED |
| bisect of hh-rlhf drift (`$S/rv23/hh_at.sh`) | commits `5c96c5d`, `91fc49c^`, `91fc49c`, HEAD | see F2. MEASURED |
| `31_EMPIRICAL/*` | read in full | contains no executable code; checked the registration claims (F4) |

DID NOT RUN: anything that needs a model provider. E-1-D (AURA behaviour) and the multi-operator study
need paid or recruited participants, which the brief excludes.

---

## Findings

### F1 — The persona "not significant" is a statistics error. ✅ FIXED in code; records annotated

**What happened.**

- `external_validation.auc_significance` and `independent_publisher_test.auc_sig` both used the
  no-ties Mann-Whitney null SE, `sqrt((n1+n2+1)/(12 n1 n2))`.
- The hand-written lens fires on few texts, so most scores tie. **96.2%** of the 1,000 persona
  statements receive the identical score 85.
- Ties shrink the true null variance. The assumed SE is **0.0183**; the label-permutation SE is
  **0.0055**, which makes the assumed SE 3.3× too large.

**Corrected result.**

- Tie-corrected p = **0.008**. It agrees with `scipy.stats.mannwhitneyu` (asymptotic, no continuity
  correction).
- An exact permutation test over 50,000 relabellings (seed 20261022) gives p = **0.0096**.
- The direction is correct: aligned statements score higher.

**Where the effect comes from.** Only 38 statements leave the modal score: 27 concerning and 11
aligned, and all of them move downward.

**Verdict.** The published reading "NOT distinguishable from chance" is wrong. The true reading is a
detectable effect in the correct direction that is negligible in size (AUC 0.516). The same-day
correction document states "#2 stands as originally written. p = 0.38 is genuinely indistinguishable
from chance". That sentence is the one that needed correcting. MEASURED.

**Fix (maintained code, edited in place).**

- `33_APPLICATIONS/external_validation.py`: `auc_significance(auc, n_pos, n_neg, pooled=None)` now
  applies the tie term `Σ(t³−t)/(n(n−1))` and returns nan when the variance is zero. `run_persona`
  passes the pooled scores.
- `33_APPLICATIONS/independent_publisher_test.py`: `auc_sig` has the same correction, and `report`
  passes the pooled scores.
- **NEW** `tests/test_external_validation_ties.py` adds 3 tests. They load both scripts and use a
  persona-shaped fixture. They check that both p-values match scipy, that ignoring ties reproduces the
  published error, and that untied data is unchanged.
  - **Mutation witness:** with the tie branch disabled (`if False:`), 2 fail and 1 passes. Restored,
    3 pass. MEASURED.

**Records (annotated, original text kept).**

- `33_APPLICATIONS/README.md`: row 41 "Supported reading" corrected, plus a dated RV23 note.
- `33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md`: dated correction note at the top. Result #2 is
  kept as written.
- `llms.txt:36`: the summary "no distinguishable social-engineering effect" was replaced with the
  corrected reading. This is a maintained index, not a pin. `tests/test_claims_register.py` still
  passes.
- **Staged, not applied:** `RV23_truth_pressure_persona_note.patch` (+9 −0). It adds a note under the
  headline box of the canonical `TRUTH_PRESSURE/TRUTH_PRESSURE_MASTER_SOURCE_2026-08-07.md`. The patch
  is generated by `stage_rv23_patches.py` from HEAD bytes, applied to a HEAD copy and byte-compared.
  - Its "structural finding" paragraph says the instrument sits "**at chance** on real traffic". With
    the correction that becomes *near* chance. The finding survives; one word does not.
  - `33_APPLICATIONS/reflexive_audit.py:35` reads this master as an audit target, so applying the
    patch changes that audit's input. Re-run it in the same change.
- **Ledger only:** `papers/agent-safety/earned-light/forges_01_07/Earned_Light_Research_Pass_01.md:43`
  repeats the null. It is intake-pinned (see G-INTAKE-1019-RECORD from Batch 21).

### F1-b — The UCC verdicts survive. Two hypotheses REFUTED

- **(a) REFUTED.** The question was whether any UCC null would become a significant wrong-direction
  result once ties are counted. None does:
  - aura stays 0/6 and derived stays 2/6;
  - the no-ties SEs are conservative (permutation / no-ties SE ratio 0.71–0.78 for aura, 0.83–0.93 for
    derived), but no verdict changes.
- **(b) REFUTED.** The question was whether the two derived hits are a multiplicity artefact. Both
  survive Holm across the six attributes: hostile adjusted p = 0.028, generalisation 0.0019. MEASURED.

### F2 — The dated hh-rlhf numbers reproduce at their record commit, not at HEAD

- At the record commit `5c96c5d`, hh-rlhf is exactly **741 / 594 / 973** (correct / incorrect /
  tied), matching the dated report.
- The first commit that moves it is `91fc49c` (2026-08-07, "The extractor learns stance", in
  `semantic_extractor.py`). From there it is **739 / 595 / 974** (55.4%, p = 8.1e-05).
- The same commit moves held-out discrimination AUC **0.940 → 0.950**.
- The README already calls these "dated runs" but did not say that HEAD gives different numbers. That
  is now said in the README note (point 2). DERIVED from bisect, MEASURED at each commit.

### F3 — A Batch 12 review fix moved the external numbers, and nobody recorded it

The uncommitted Batch 12 T3 fix is in `12_IMPLEMENTATIONS/core/tri_axial_checker.py`. It makes the
hedge lexicon tokenizer-aware: `lexicon_tokens`/`count_lexicon`, with "Maybe," and "I think" now
counted.

That file alone, overlaid on HEAD, changes the lens:

- hh-rlhf **784 / 658 / 866** = 54.4%, p = 9.1e-04;
- persona AUC **0.523**, tie-corrected p = **0.001**;
- held-out discrimination AUC back to **0.940** at 90% accuracy (HEAD: 0.950, 95%);
- UCC unchanged: aura 0/6, derived 2/6.

The Batch 12 ledger recorded the fix as correct, and it still is: a hedge the checker could not see
was a defect. It did not record the effect downstream. It is recorded now in the README note (point 3)
and here. The rule this teaches: **a lexicon fix is an instrument change**, and every number the
instrument produced needs its commit beside it. MEASURED.

### F4 — 31_EMPIRICAL: "pre-registered" means drafted. Nothing is registered

- There are no osf.io, AsPredicted, or ClinicalTrials receipts anywhere in the tree.
- There are no executed studies.
- The "Hypothesis (preregistered)" headings describe what would lock at registration.

All annotated in place, headings kept:

- `E1_EMPIRICAL_PROGRAM.md`: a note after the Predecessors line.
- `E1.1_PREREGISTRATION_PLAN.md`: the drafts it promises exist as `E1A_K1K4_CALIBRATION_PREREG.md` and
  `E1D_AURA_BEHAVIOUR_PREREG.md`, both unfiled.
- `E1G_MULTI_OPERATOR_PREREGISTRATION.md`: H5 "pre-registered 2026-05-03" means added to the draft;
  its own §X says unfiled. MEASURED.

### F5 — A dangling reference

- `E1H_MASTER_EQUATION_CALIBRATION.md` cited `E1A_CASCADE_PREREGISTRATION.md`, which does not exist.
  E-1-A is the k₁–k₄ calibration, and the seven-invariant AURA study is E-1-D. Corrected with a note.
- The same dangling reference sits in `papers/LYCHEETAH_SYNTHESIS_v0.2.md:306`. That file is a
  historical snapshot with a banner, so it is recorded here only. MEASURED.

### F6 — Method review: honest, with two limits worth stating

- **The train/test split is honest.** `derive_cues.py` mines and fits on hh-rlhf **train** only and
  scores **test**. The "43.9%" figure in history came from a fix to how ties were counted, not from
  tuning on test. MEASURED.
- **hh-rlhf does two jobs.** The cues are derived on hh-rlhf train and validated on hh-rlhf test. That
  is one distribution, one publisher and one labelling process. The UCC and red-team transfer runs are
  the out-of-distribution evidence, and they are mixed:
  - 2/6 on UCC;
  - red-team transfers;
  - helpfulness is **anti-correlated**.
  
  The README preserves all three. DERIVED.
- **The held-out discrimination set is author-written.** The dev/held-out split is genuine, but both
  halves come from the same authors. The TP master's own structural finding is that 0.94 on
  self-authored cases says nothing about the world, and that still applies. DERIVED.

### Preserved negatives (kept, not softened)

- The UCC transfer failed for the hand-written lens (0/6), and the derived lens managed 2/6.
- Helpfulness is anti-correlated with both lenses (37.4% / 41.8% pairwise).
- `source_pointing` does not transfer.
- The persona effect, now that it is correctly significant, is still negligible (AUC 0.516–0.523).

---

## The outside workflow the brief asks for

| Question | Answer |
|---|---|
| **Conventional baseline** | Nothing in 33_APPLICATIONS compares against a conventional classifier, such as TF-IDF + logistic regression on the same hh-rlhf train split or an off-the-shelf toxicity model on UCC. Without one, "55% pairwise" has no reference point. **Recommended next experiment**: it needs no provider. |
| **User benefit** | Not measured. A 54–55% pairwise preference and an AUC of 0.52 do not support any user-facing gating decision. The README already says this, and it should stay that way. |
| **Review burden** | Low per run: every script names its command, pins its data by SHA and is deterministic. The burden is version drift. A number is only reproducible at the commit that made it (F2, F3). |
| **Failure handling** | Both scripts fail closed on a SHA mismatch. The significance helpers previously failed *quiet*: an over-wide SE turned a real effect into "not significant" with no warning. Fixed by F1, and the new test pins it. |

---

## Decisions for Mac (G-items)

- **G-TP-PERSONA-NOTE.** Apply `RV23_truth_pressure_persona_note.patch` to the canonical TP master? If
  so, re-run `reflexive_audit.py` in the same change.
- **G-LENS-VERSION-STAMP.** Should `external_validation.py` and `independent_publisher_test.py` print
  `git rev-parse HEAD` beside their numbers, so a dated report carries its commit? This is cheap and
  closes F2/F3 for good.
- **G-CONVENTIONAL-BASELINE.** Add a TF-IDF + logistic-regression baseline on the same splits? It needs
  no provider, and it is the comparison every outside reviewer will ask for first.
- **G-PREREG-FILING.** Either file E-1-A / E-1-D on OSF, or rename the headings from "preregistered" to
  "draft preregistration". The notes hold the line until you choose.

---

## Files changed by this batch

| Path | Kind |
|---|---|
| `33_APPLICATIONS/external_validation.py` | edit: tie-corrected SE |
| `33_APPLICATIONS/independent_publisher_test.py` | edit: tie-corrected SE |
| `tests/test_external_validation_ties.py` | new: 3 tests, mutation-witnessed |
| `33_APPLICATIONS/README.md` | edit: row 41 + RV23 note |
| `33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md` | edit: dated correction note (original kept) |
| `llms.txt` | edit: line 36 summary |
| `31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md`, `E1.1_PREREGISTRATION_PLAN.md`, `E1G_MULTI_OPERATOR_PREREGISTRATION.md`, `E1H_MASTER_EQUATION_CALIBRATION.md` | edit: review notes |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch22.py` | new |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv23_patches.py` | new |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV23_truth_pressure_persona_note.patch` | new, staged, **not applied** |

Reproduce:

```
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch22.py <head-copy> <data-dir> --perms 400
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv23_patches.py . <scratch>
python3 -B -m pytest -q tests/test_external_validation_ties.py
```

Full suite (working tree, after all RV23 edits): **1504 passed, 1 skipped, 1 xfailed, 1 warning in 89 s**.
That is the baseline of 1501 plus the 3 new tie tests. MEASURED.
