# Batch 20 — RV21 Truth Pressure forge, cybernetics and Tianxia operators

Reviewer: Sol (Claude Opus 5.5, xhigh) · 2026-10-22 · branch `review/full-framework-2026-10-20` at `d7ae0ad`, working tree only, nothing committed.
No "reviewed" label was inherited. Every bundle was run from a `git archive HEAD` copy in scratch, never in place.

## Coverage (what was actually read and run)

| Surface | Coverage |
|---|---|
| `TRUTH_PRESSURE/FORGE_2026-08-02/` (9 zips, `SHA256_MANIFEST.txt`) and `FORGE_2026-08-02_EXPANDED/` (9 bundles) | Every zip member compared byte for byte with the expanded tree, both directions; forge manifest and all 7 per-bundle `SHA256_MANIFEST.json` verified (C1) |
| v0.1 `truth_pressure/engine.py` | Gate code read; 33 tests and benchmark 16/16 re-run; rounding probed (C8) |
| v0.2, v0.3, v0.5, v0.6 TS packs | Verify scripts re-run: 24/24, 24/24, 14/14, 11/11 |
| v0.7 Shadow Evidence Console | `shadow-analysis.ts` gates, `shadow-store-core.ts` counters, both verify scripts read and run; patched copy run (C3) |
| v0.4 Measurement Pack | `analyze_annotations.py` read in full; run on synthetic filled packets (C4); README, pre-registration and blinding key read |
| v0.8 Live Source Collector | 421 lines read; run on a scratch fixture only (C5). Never run on a real repository: it writes inside its target |
| SOURCE_AUDIT_PASS_1 v0.1 | Sources matched against private app commit d8c8a12 (read-only `git show`) |
| `TRUTH_PRESSURE/MASTER_EQUATION.md` | §4–§6 read against the Batch 17 and 18 findings |
| `34_CYBERNETICS/` | `loop_audit.py`, `--self-test`, `variety_demo.py` run (C7); `tests/test_cybernetics.py` + `tests/test_tianxia_operators.py` 35 passed |
| `32_TIANXIA/` | `REN_ZHENG_OPERATOR.md`, `implementations/ren_zheng.py`, `hexie_five_fold.py` (H₅ line), `operator_audit.py` (run), `civilisational_governance_benchmark.py` (run), `WORKED_EXAMPLES_v0.3.md` read; `28_DEFENSE/CLAIM_STATUS_LEDGER.md:186` read |
| `99_ARCHIVE/closed_loop_agent_lab` | Collection only: 677 collected, **71 collection errors**. Outside `testpaths`. DID NOT RUN as a suite; carried to the archive RV |

## Findings

Labels: MEASURED = reproduced by `repro_batch20.py` (9/9 PASS). DERIVED = read from code or text.

**F1 — v0.7's disagreement gate passes on zero evidence. MEASURED (C3). Severity: medium; the bundle is dormant.**
`GATE-DISAGREEMENT-REVIEW` is `PASS` when `triggerDisagreements === 0`. A dataset with no trigger-comparable record has zero disagreements, so it passes. The bundle's own test `100 clean records can meet the engineering gate` builds records whose helper never yields `'AGREE'`, so it enshrines the vacuous pass: 100 records, 0 comparable, `ENGINEERING_GATE_MET`. The recorded `reports/SYNTHETIC_REPORT.md` carries a hand-added disclaimer that the analyzer does not emit. Staged patch: the gate passes only after agreement has been observed. The witness: the new check **fails against HEAD source** (AssertionError) and passes on the patched bundle, which then passes 12/12 review checks and 11/11 bridge checks.

**F2 — v0.4's analyzer accepts one rater's packet as several raters. MEASURED (C4). Severity: high for the measurement program once ratings exist; no ratings have been collected.**
`load_ratings` assigns a rater index per file and never checks which packet a file is. Passing `RATER_A` three times gives every case three "independent" ratings, and alpha reports **1.0, 1.0, 1.0**. Patched: refused with `Rater packet A supplied twice`.

**F3 — v0.4 reports perfect agreement for ratings with no variation. MEASURED (C4).** `interval_alpha` returns 1.0 when both disagreement terms are zero. Alpha is 0/0 there, undefined. The pack's own pre-registration says high agreement from uniformly low-information ratings is not sufficient, and its analyzer reports exactly that case as 1.0. Patched: `null`. Control: on independent synthetic raters, HEAD and the patched analyzer both give α = 0.769 / 0.854 / 0.751 (E/P/S), equal to an independently written Krippendorff interval alpha to 1e-12. The formula itself is correct for complete data.

**F4 — v0.8's collector copies pasted secrets and tells the user it collected none. MEASURED (C5). Severity: high if run; it is built for upload.**
Exclusion is by file and directory name only. Files are selected by content (Truth Pressure identifiers) or by an always-include list (`app.config.ts`, `app.json`, `package.json`, …). There is no content scan. On a fixture with a runtime-built `sk-` key in `app.config.ts` and a Google-style key in `lib/score.ts`, HEAD copied both into the extract and printed "No .env, keys, databases, logs, dependencies, builds, or user data were collected." The output's README says to compress it and upload it. Controls: `.env` was excluded by name in both versions; a benign `lib/view.ts` was collected in both. Patched: both files withheld and named in stdout and the receipt; the final message now says the scan is pattern-based and cannot prove absence. The collector also records `git status --porcelain` and writes `_truth-pressure-live-source-extract` inside its target (deleting any previous one). Run it only on a copy.

**F5 — Tianxia's R(s) has two definitions. MEASURED (C6).**
- `REN_ZHENG_OPERATOR.md:93` and `ren_zheng.py` define R(s) = (W + V + F)/3, with F = force *restraint*, θ_r = 0.618.
- `WORKED_EXAMPLES_v0.3.md` and `28_DEFENSE/CLAIM_STATUS_LEDGER.md:186` use 0.4W + 0.4V − 0.2F, with F = force *component*, θ_r = 0.60.
- The classification flips. Example 2 is "marginally below" (0.59) on paper and **0.80, Wang-eligible** under the operator. Example 4 is 0.75, eligible. Examples 1 and 3 fail under both.

**F6 — The worked examples do not follow their own arithmetic. MEASURED (C6), with the H₅ definition DERIVED from `hexie_five_fold.py:57` (plain mean of five components).**
- Example 4 prints R = 0.52 where its formula gives 0.54.
- Example 4's H₅ components average **0.542**, while the text prints 0.64 "just below" the 0.65 threshold and concludes "Conditional PASS".
- Example 2's components average **0.624**, below threshold, while the text prints 0.72 "above threshold".
- Example 1's table parsed to 4 numeric rows (mean 0.36 against a printed 0.32). It is not adjudicated, because one row did not parse as a number.

**F7 — `MASTER_EQUATION.md` §5–§6 still assert a proof that fails. DERIVED.** The §6 table says "Equation structure ACTIVE — proven in §4" and "Stability proof ACTIVE — Lyapunov verified", and it closes with "structure is proven". The §4 proof was refuted in Batch 17 (F6), and an RV18 note was added there. §5.2 rests k₁ on the +40.3% Monte Carlo, whose accounts are inconsistent (Batch 18 F2), and asserts that the run "implicitly encodes k₁ ≈ 1.0" without derivation. The §6 activation route fits k₁–k₄ to `cascade_engine.py`'s own simulation, which is self-calibration. Dated notes were added at §5 and §6; the original text is kept.

**F8 — v0.1 gates compare rounded values. MEASURED (C8). Severity: low.** Support is rounded to 6 dp before the `minimum_support` test, so a raw 0.5499996 clears 0.55. The delta margin is rounded the same way. Recorded only.

**F9 — Tianxia's benchmark baseline is hand-authored. DERIVED.** `civilisational_governance_benchmark.py` labels itself SCAFFOLD. Its `Tianxia_Aligned_Baseline` scenario is written to score well, so it cannot serve as evidence for the operators. `operator_audit.py` is honest ("measures internal decision geometry ONLY") and shows threshold sensitivity, e.g. H₅ ≥ 0.65 covers 35.0% of the input space and R ≥ 0.618 covers 24.9%.

**F10 — Cybernetics is clean at this boundary. MEASURED (C7).** 10/10 loops match the map, with 6 closed, which agrees with the README's "6 of 10". The self-test catches 7/7 mutations. The audit prints its own limit ("a feedback path in code, not that it regulates the right thing"). The census reads 797 files, up from 794 at the start of the batch because of this batch's three new Python files. `variety_demo.py` is a synthetic illustration of Ashby's law, labelled as such.

**F11 — The forge mirror was unpinned. MEASURED (C1, C2).** All 9 zips are byte-identical to the expanded tree, and every manifest verifies today, but no test held the two copies together. New test `tests/test_truth_pressure_forge_mirrors.py`. It fails when one expanded byte or one zip byte is flipped on a scratch copy.

## Writes (all uncommitted)

| Path | Change | Kind |
|---|---|---|
| `tests/test_truth_pressure_forge_mirrors.py` | Pins zip ↔ expanded bytes both ways and the forge SHA-256 manifest | NEW |
| `TRUTH_PRESSURE/MASTER_EQUATION.md` | Dated RV21 status notes at §5 and §6; original text kept | note only |
| `32_TIANXIA/WORKED_EXAMPLES_v0.3.md` | Dated RV21 notes at the top (two R(s) definitions) and after Example 4 (arithmetic); original text kept | note only |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv21_patches.py` | Generator: exact-one swaps on `git show HEAD:` bytes, `diff -ruN`, applied to a HEAD copy and compared | NEW |
| `FOR-REVIEW/…/RV21_v07_disagreement_gate.patch` | F1 (2 files, +21 −6) | STAGED, not applied |
| `FOR-REVIEW/…/RV21_v04_analyzer_integrity.patch` | F2 + F3 (+22 −5) | STAGED, not applied |
| `FOR-REVIEW/…/RV21_v08_collector_content_scan.patch` | F4 (+31 −2) | STAGED, not applied |
| `FOR-REVIEW/…/repro_batch20.py` | Witness script C1–C9 | NEW |
| this ledger | | NEW |

Not touched: every frozen bundle, every zip and manifest, `28_DEFENSE/CLAIM_STATUS_LEDGER.md` (committed canon, see G-REN-ZHENG-ONE-DEFINITION), `REN_ZHENG_OPERATOR.md`, `ren_zheng.py`. No test key literal was written to the repository: C5 assembles its key strings at runtime and writes them only to scratch.

## Verification

- `python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch20.py <root> <scratch>` → **9/9 PASS** (see the run at the foot of this batch's chat receipt).
- C3 is a fail-on-HEAD witness: the new v0.7 check fails against HEAD source and passes when patched. C2 is a mutation witness for the new repository test. C4 and C5 each carry a control that behaves identically before and after the patch.
- Full suite, run once at the end of the batch: see the chat receipt (expected baseline 1495 + 2 new).

## Decisions for Mac

- **G-FORGE-REMINT.** Applying any staged patch changes a frozen bundle. Its `SHA256_MANIFEST.json`, its zip and the forge `SHA256_MANIFEST.txt` must then be re-minted together, and the new mirror test will refuse a half-done re-mint. Sol's call: **one re-mint covering whichever patches you accept**, with a dated line in each bundle README naming the review.
- **G-TP-ANNOTATION-INTEGRITY** (F2, F3). Sol's call: **apply now.** This is the only one with a deadline. The pre-registration's no-moving-target rule binds once the first packet is opened. After that, the analyzer can't change without breaking the pre-registration.
- **G-TP-COLLECTOR-SECRETS** (F4). Sol's call: **apply before any future run, and do not run v0.8 until then.** A pattern scan narrows the risk but does not close it. The patched message says so.
- **G-TP-SHADOW-GATE** (F1). Sol's call: **apply at the re-mint**. Until then, don't cite the recorded `ENGINEERING_GATE_MET` as a gate result.
- **G-REN-ZHENG-ONE-DEFINITION** (F5, F6). Sol's call: **the implemented operator is canonical** (it is tested and audited, and its bounds were hardened on 2026-08-08). The worked examples should be recomputed under it. The `CLAIM_STATUS_LEDGER.md:186` line is Zenodo-linked canon, so its correction is yours: a dated correction line, not a rewrite.
- **G-MASTER-EQ-STATUS** (F7). Rewrite the §6 rows to UNVERIFIED, or keep the dated notes. Sol's call: **keep the notes** until the Batch 17/18 decision on the equation itself, then rewrite once.
