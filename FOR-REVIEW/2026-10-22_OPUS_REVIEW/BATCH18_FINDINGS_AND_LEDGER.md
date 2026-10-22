# Batch 18 — RV19 claims register: findings and ledger (review 2026-10-22)

Scope: RV19 of `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md`, the canonical claims register
`28_DEFENSE/CLAIMS.json` (71 claims, 107 evidence references), its schema, the 2026-10-20 review in
`28_DEFENSE/review_2026_10_20/`, and the documents the empirical CASCADE claims rest on:
`TRUTH_PRESSURE/EMPIRICAL_RESULTS.md`, `28_DEFENSE/TESTABILITY_MANIFEST.md`,
`papers/LYCHEETAH_SYNTHESIS_v0.1.md`, `11_MATHEMATICAL_FOUNDATIONS/cascade_simulation.py` and its
stored run. Nothing here is inherited from the 2026-10-20 review: each of its 71 classifications was
checked against this review's own witnesses where they exist (overlay below).

Witness: `python3 -B repro_batch18.py <root> <scratch>` → **Batch 18: ALL PASS** (20 checks). Every
refutation is paired with a control that must pass. It runs entirely in scratch copies and removes them.

## Findings

Labels: MEASURED means reproduced by `repro_batch18.py` (check id given). DERIVED means reasoned from
named evidence. DID NOT RUN is kept separate.

| # | Claim (where) | Verdict | Evidence |
|---|---|---|---|
| F1 | A pre-registered 200-trial experiment with all materials "available"; "The empirical results are verifiable." (`TRUTH_PRESSURE/EMPIRICAL_RESULTS.md`, "Document status: ACTIVE", added in 4898d15) | **No artifact exists in the repository → UNVERIFIED.** `50_belief_corpus.json`, `annotator_labels.csv`, `trial_results_200.csv`, `analysis.py` and `trial_config.json` are in neither the tree nor any commit; `cascade_engine.py` has 744 lines and no `compute_coherence()` (cited "line ~847") or `compute_forgetting()` ("line ~912"). This review does not claim the trials were never run, only that nothing in the repository lets anyone check them. MEASURED | B3; control: the same search finds `cascade_simulation_results.json` |
| F2 | +40.3%, d = 2.84 | **Three accounts, none consistent with another or with itself.** (a) EMPIRICAL_RESULTS: 0.529→0.742 is +40.3%, but its SDs 0.063/0.058 give pooled d 3.52 (Glass 3.67); d = 2.84 needs a pooled SD of 0.075. Its t(198) = 24.7 is consistent (24.9). (b) CAS-009 and TESTABILITY_MANIFEST: 0.58→0.93 over 10 replications × 3 conditions is **+60.3%**, not 40.3%. (c) SYNTHESIS v0.1:130: the same 0.58/0.93 with SDs 0.04/0.09 gives d **5.03**. MEASURED | B4 |
| F3 | CAS-010: +110% coherence on five historical paradigm shifts | **CASCADE ties the additive baseline in every trial of every domain** (both 1.0; stored t = 0, p = 1, d = 0). The +110% is over a static baseline that never updates. Each domain's 200 trials are identical deterministic copies (zero variance; stored t = inf), so the p-values do not count independent samples. 0.47→1.0 is +112.8%; 110.05% is the mean of the per-domain percentages [115.38, 115.38, 90.91, 114.29, 114.29]. The run itself reproduces exactly. MEASURED | B4, B5, B6 |
| F4 | `cascade_simulation.py` verdict `if mean_pct >= claimed*0.8: "[CONFIRMED]"` | **Overshoot counted as confirmation.** 110.05% against a claimed 40.3% (2.7×) printed [CONFIRMED], and the 40.3% belongs to a different experiment (F2). **Fixed in place**: a pure `classify_status()` confirms only within ±20% of the claim and only with a gain over the additive baseline; the paradigm run now reports `[NO GAIN OVER ADDITIVE]` with a museum line saying why. The stored JSON is kept as the frozen counterexample. MEASURED | B6 (HEAD: [CONFIRMED]), B7 (repaired: gain +0.0000, [NO GAIN OVER ADDITIVE]) |
| F5 | CAS-011: −95.2% catastrophic forgetting | **Two accounts from different numbers, neither with data.** Register and SYNTHESIS: 0.42→0.02. EMPIRICAL_RESULTS: 1.00%→0.048%. Both give 95.2%. MEASURED | B3, B4 |
| F6 | TESTABILITY_MANIFEST code path `01_CASCADE_L4/implementations/cascade_synthetic_experiment.py` (CAS-009, CAS-011) | **Has never existed in the repository.** The protocol cannot be run. MEASURED | B3 |
| F7 | Register evidence paths | **23 of 107 references are dead, in 23 claims** (16 claims have every reference dead). Recon recorded `01_CASCADE_L4/implementations/` as resolving but silent: **corrected**, it is dead and is three of the 23. A staged patch repoints 20 claims to where each claim is actually stated (line-checked) and drops two dead duplicates; three `TC_CATALOG.md` references stay declared missing. 23 → 3. MEASURED | B1; control: a planted dead reference is counted |
| F8 | Silent pointers | `CLAUDE.md` has not contained the EWM table, Two-Point Protocol or PGF since the reforge (3980262); they live in `AGENTS.md` and `THE_SOL_PROTOCOL.md` (HAR-004, XFW-005, XFW-006). `29_GOVERNANCE/EMPIRICAL_INVENTORY.md` states none of the CAS-009..011 numbers. Neither LYV-001 pointer states "11/11"; only SYNTHESIS v0.1:136 does. `MATHEMATICS_FOUNDATIONS.md` lacks "Conjecture C5" (CAS-008); FORMAL_SPINE:227 states it. MEASURED (B2 for CLAUDE.md, with 6cfccf2 as control); the rest asserted by `stage_rv19_claims_pointers.py` |
| F9 | ANA-003 TC(π, 4), ANA-004 TC(symmetry, 4) | **The count 4 is stated nowhere that resolves.** The only resolving statement, `30_MAPS/FORMAL_SPINE.md:439`, says TC(π, ≥3) and TC(symmetry_groups, ≥3). The remaining mentions are PROVENANCE_INDEX (pointing at the missing TC_CATALOG) and ASCII art in VISUAL_ATLAS:501–511. DERIVED from the files |
| F10 | AUR-009 provenance | PROVENANCE_INDEX cites `AURA_THEOREMS.md` lines 215–220, which do not exist. The claim is stated, as pending, at `30_MAPS/CODEX_DISTILLATION.md:536`. DERIVED; the line check is in the generator |
| F11 | `tests/test_claims_register.py` | Checks only that claim counts agree across mirrors; nothing checked that a reference resolves. **New test** `tests/test_claims_evidence_pointers.py` (below). MEASURED | B8 |
| F12 | 2026-10-20 classifications (`claim-assessments.json`) | **No disagreements.** 8 agree with this review's RV18 witnesses, 9 are sharpened (CAS-009/010/011, LYV-001, HAR-004, XFW-005/006, ANA-003/004), and 54 were not re-audited here and say so. For CAS-009..011 the 10-20 review wrote "the full experiment runner was not rerun". This review reran the one that exists (CAS-010) and found that the other two have none. DERIVED | `RV19_claim_review_overlay.json` |

### The +40.3% mirror census (DERIVED, grep on the tree)

27 files carry 40.3%: `03_LAMAGUE_L1` ×2, `11_MATHEMATICAL_FOUNDATIONS/cascade_simulation.py`,
`15_PERSONAL_VAULT` ×2, `26_FOR_AI/DEAR_AI.md`, `28_DEFENSE/` (C1_AUDIT_REPORT, C1_REFORGE_RECON,
CLAIMS.json, NOVEL_CONTRIBUTIONS, REFORGE_REGISTER, SCOPE_BOUNDARY, SCOPE_DECLARATION,
TESTABILITY_MANIFEST), `papers/` SYNTHESIS v0.1 and v0.2, and `TRUTH_PRESSURE/` (00_INDEX,
EMPIRICAL_RESULTS, FABLE_REVIEW_PROMPT, FORGE_2026-08-02 ×2, IP_PROVENANCE, MASTER_EQUATION, CANON,
MASTER_SOURCE 08-03 and 08-07, THEORY). `README.md`, `llms.txt` and `FIVE_MINUTE_BRIEF` no longer
carry 40.3%, 110% or 95.2%. Notes went only into the two documents that present the figures as
replicable evidence (EMPIRICAL_RESULTS, TESTABILITY_MANIFEST). The other 25 mirrors are decision
G-EMPIRICAL: a note on each mirror would patch reflections rather than the source.

## Writes

**In place (maintained or unpinned):**

- `11_MATHEMATICAL_FOUNDATIONS/cascade_simulation.py`: `classify_status()`, per-domain `additive`,
  `gain_over_additive` printed and saved, and the museum line for a tie. Running the script still
  overwrites its stored JSON, as it did before; this review never ran it in the repository.
- `TRUTH_PRESSURE/EMPIRICAL_RESULTS.md`: an UNVERIFIED status note under the header and a pointer
  note after the §6 materials list. Original text kept. Applied by `apply_rv19_doc_notes.py`, which
  asserts every fact it states before writing.
- `28_DEFENSE/TESTABILITY_MANIFEST.md`: status notes on CAS-009, CAS-010 and CAS-011. Original entries kept.
- `tests/test_claims_evidence_pointers.py` (new, 11 tests): the dead-reference ratchet (⊆ the 23
  known dead) plus a planted-reference control; the EMPIRICAL_RESULTS note and the absence of its
  materials; the verdict table (7 cases); and the stored run as a frozen counterexample, which must
  tie additive, keep its stored [CONFIRMED], and be refused by the repaired verdict.
  **B8: on HEAD, 9 fail and 2 pass (the ratchet and its control). Repaired: 11 pass. With the
  pointer patch applied: 11 pass. Mutating one stored additive value fails exactly the fact pin.**

**Staged (canon, not applied):**

- `RV19_claims_pointer_repairs.patch` + `RV19_claims_pointer_repairs.json`, from
  `stage_rv19_claims_pointers.py`. 24 claims change `evidence_path` only; statements and author
  statuses are byte-for-byte the same after parsing. Missing references go from 23 to 3, and total
  references from 107 to 106. Register sha256 9d8e76dc… → 8b9daf4a…. The patch applies to HEAD and
  matches, with no CR bytes.
  **Applying it stales the `register_sha256` pin in `28_DEFENSE/review_2026_10_20/claim-assessments.json`.**
  The record carries a caution: a pointer to where a claim is stated is not evidence for it.
- `RV19_claim_review_overlay.json` (71 rows): author status, 10-20 classification, this review's
  verdict, witnesses, and the state of every reference on HEAD and after the patch.

**Scripts:** `apply_rv19_doc_notes.py`, `stage_rv19_claims_pointers.py`, `build_rv19_overlay.py`, `repro_batch18.py`.

Unchanged: `28_DEFENSE/CLAIMS.json`, `cascade_simulation_results.json` (frozen counterexample),
everything under `28_DEFENSE/review_2026_10_20/`.

## Verification

- `repro_batch18.py` → ALL PASS (B1–B8, 20 checks; the scratch copies are removed by the script).
- Focused: `tests/test_claims_evidence_pointers.py` 11 passed.
- Full suite, run once: **1492 passed, 1 skipped, 1 xfailed** (baseline 1481 + 11 new). The run also
  reported 1 warning. This review has not attributed it; the new test file alone emits none.
- DID NOT RUN: the F(2, 27) = 318.4 ANOVA in SYNTHESIS v0.1:130 cannot be checked without the
  control condition's mean. No independent statistics package recomputed d; the formulas are
  standard (pooled SD with equal n) and are written out in B4.

## Decisions for Mac

- **G-RV19-POINTERS**: apply `RV19_claims_pointer_repairs.patch` to CLAIMS.json? If yes, re-pin
  or annotate the 10-20 `claim-assessments.json` sha (it would otherwise point at a superseded register).
- **G-EMPIRICAL**: what EMPIRICAL_RESULTS becomes. Options: (a) produce the materials; (b) set its
  status to UNVERIFIED or RETRACTED and point the 25 mirrors at that one ruling; (c) keep the notes as they stand.
- **G-CAS-STATUS**: the author statuses of CAS-009/011 (ACTIVE; no runner exists) and the wording of
  CAS-010 (honest form: "beats a no-update baseline; ties additive update on these five encodings").
- **G-TC-COUNT**: ANA-003/004 say 4; the only resolving statement says ≥3. Which is the claim?
