# BATCH 35 — RV36 · Audit the auditors and their receipts

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

**Standing caveat (from the checklist, and true of this batch).** This is one AI reviewer checking another AI reviewer's receipts. Agreement between them is not independent scientific validation, and nothing below upgrades any author claim.

## Coverage, stated honestly

- **Read whole:**
  - `28_DEFENSE/review_2026_10_20/README.md`.
  - The harness, receipt and audit sections of `math_probes.py` (lines 60–135 and 505–700), plus probes MP04, MP05, MP12 and MP13 in full.
  - The source lines behind MP01, MP04 and MP12.
  - `CLAIMS.schema.json`, `tools/verify-claims.py` `check_register`, and the head of `tests/test_claims_register.py`.
- **Parsed structurally, then recomputed:** all 13 JSON receipts in `review_2026_10_20/`, `DEFENSE_INDEX.json`, `CLAIMS.json`, and the 10-19 intake manifest.
- **Executed:**
  - `math_probes.py` in a detached baseline worktree, plus two negative controls.
  - `pytest --collect-only` at two named commits.
  - Schema validation with five negative controls.
  - `tools/verify_research_intake.py`, `tools/verify-claims.py` and `tools/verify-links.py`.
  - Each worktree was removed afterwards.
- **NOT read in this batch:** the 28_DEFENSE prose documents themselves (FAILURE_MUSEUM, CLAIM_STATUS_LEDGER, DOWNGRADE_REGISTER, OBJECTIONS_REGISTRY and the rest), and `FULL_FRAMEWORK_REVIEW_2026-10-20.md` whole. Their pointers and counts were checked, not their arguments.
- **DID NOT RUN:**
  - The full suite at the baseline commit; only collection was run.
  - The current `run_chorus.py` against empty agents.
  - Any regeneration of the receipts that have no producer.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED | **The mathematical receipt reproduces exactly.** In a detached `6ba483a` worktree, `math_probes.py` returns 18 of 18 REPRODUCED. Every probe's values, the 36 source receipts, the summary, the controls and the script SHA-256 are identical to the committed `math-probes.json`. `claim-evidence-audit.json` is identical except for its timestamp. **Negative controls:** a one-line append to a pinned source in the scratch worktree raises `A cited source differs from reviewed commit`, and running at the current HEAD raises `The checkout no longer has the reviewed commit`. Each of the 18 probes carries between 1 and 6 assertions, so no verdict is a bare label. |
| F2 | MEASURED + DERIVED | **Classifications challenged; three hold.** <br>- **MP04:** `MATHEMATICS_FOUNDATIONS.md:318` applies the projection inequality "for a projection onto a convex set" to H₀ = {S < ε}. A strict sublevel set of a concave function is not convex in general, and the probe's two vertices with their midpoint show it. <br>- **MP12:** `CASCADE_FORMAL_PROOFS.md:415–421` derives `Value_created ≥ Resources_consumed` from two increases being non-negative. That is a non sequitur, and the countermodel is correct. <br>- **MP01:** the displayed `‖T‖ < 1·1·1` chain is the one the probe breaks. <br>The other 15 were not re-derived by hand; their reproduction is F1. |
| F3 | MEASURED | **All 32 dated source notices preserve the original body.** For every file, `before_sha256` is the baseline blob, `after_sha256` is the HEAD blob, and a line diff from baseline to HEAD deletes 0 lines. 15 of the 32 now differ in the working tree because of this review's own dated notes, which are disclosed in their batches. |
| F4 | MEASURED | **`verification.json`'s suite count is not reproducible from any named state.** It says `collected 999, passed 997` against `baseline_commit 6ba483a`. Collection gives **981** at `6ba483a` and **1058** at `cf6ff23`, the commit that added the receipt. The 999 belongs to an uncommitted intermediate working tree. The count may well have been true when it was taken, but nothing in the repository can witness it. |
| F5 | DERIVED (code) | **One control in the claims audit is a label, not a test.** `resolver_controls: {"existing_register_detected": true, "known_missing_sentinel_detected": true}` is written as literals (`math_probes.py:602`). The underlying assertions check that `CLAIMS.json` is a file and that a sentinel path does **not** exist. The sentinel is never passed through the classifier, so nothing shows that the resolver would label a missing path `MISSING_EVIDENCE`. The pinned totals (37 missing, 24 all-missing) do bind the result, and that is the real control. |
| F6 | MEASURED | **Only 2 of the 13 receipts have a committed generator** (`math-probes.json` and `claim-evidence-audit.json`). The other 11 are hand- or agent-written, including their booleans (`notice_hashes_match`, `all_current_hashes_match`, `missing_folder_negative_control_detected`, `statements_and_author_statuses_unchanged`). **Recomputed here and holding:** <br>- notices (F3); <br>- `coverage.json` counts of 4822 files, 50 directories and 35 root files; <br>- `folder-coverage.json`: 606 of 606 folders equal the snapshot tree `e3971f1`, with 4837 files; <br>- `evidence-path-repairs.json`: all 71 statements and statuses unchanged against the baseline, and 23 missing references with 16 all-missing claims reproduced on the current tree; <br>- `claim-assessments.json`: its register hash equals `CLAIMS.json` at HEAD; <br>- `deeper-reproductions.json`: the 3 source hashes equal baseline, HEAD and the working tree; <br>- `lint-baseline-comparison.json`: 46 findings in 6 files, which agrees with BATCH32 F4. |
| F7 | MEASURED | **`folder-coverage.json` is honest about its depth.** 583 of 606 folders are `CENSUS_ONLY_THIS_PASS`, 18 are `SOURCE_TARGETED` (each of them names its read files), and 5 are ZIP metadata only. "Every folder listed" is not "every folder reviewed", and the README says so. |
| F8 | MEASURED | **Two receipts describe HEAD, not this review's working tree.** <br>- `oct19-preservation.json`: 225 of 225 at HEAD, but 223 of 225 in the working tree. The two changed files are this review's dated notes: `VALIDATION_AND_LIMITATIONS.md` (RV22, BATCH21 F2) and the sovereign-choice README (RV30, BATCH29). Both are already disclosed, and `tools/verify_research_intake.py` passes (2563 files). G-INTAKE-1019-RECORD still stands. <br>- `swarm-hardening.json`: its 7 source hashes equal HEAD. They do not equal `cf6ff23`, its pre-repair baseline, which is consistent. 5 of the 7 now differ in the working tree because of RV33's repairs (policy normalization, gateway, shield, demo, bundle test). |
| F9 | MEASURED (source), UNVERIFIED (runtime) | **`chorus-probe.json` is a pre-repair witness.** With nine `None` agents and zero files, it recorded `OPERATIONAL`, 9 `✅ ONLINE` and `framework_coherence 1.0`. At HEAD, `run_chorus.py:104,141,143` emits `SCAFFOLD` and `None` for those fields. The current behaviour on empty agents was not run. |
| F10 | MEASURED | **`DEFENSE_INDEX.json` lists two documents that have never existed.** D-X `AI_READER_TEST_LOG.md` and D-XI `DEFENSE_AUDIT.md` are absent from the tree and from all of git history (`git log --diff-filter=D` is empty and `git ls-files` has no match). The other 17 entries, including every part of the compound entries, resolve. The index is canonical, so the fix is staged, not applied. |
| F11 | MEASURED | **The claims schema and gate accepted a duplicated `claim_id`.** The schema enforces the `status_normalized` enum (negative control: 1 error), required fields, and the boolean type of `load_bearing`. But `claim_id: "xx"` and a duplicated id both validate with 0 errors, and `check_register` accepted the duplicate too, because counts survive duplication. All 71 current ids are unique and match `^[A-Z]+-[0-9]{3}$`. |

**Retracted inside this batch.** My first recount reported 3 `descendant_files` mismatches in `folder-coverage.json`. **RETRACTED:** git C-quotes non-ASCII paths in `ls-tree --name-only`, so my own prefix count missed them. `ls-tree` per folder confirms the receipt's numbers (for example, 24 in `26_FOR_AI`).

## Repairs (working tree)

1. **`tools/verify-claims.py` `check_register`** (maintained): it now reports any `claim_id` that appears more than once. (2 lines; the earlier RV30 `BASELINE` edit in the same file is unchanged.)
2. **`tests/test_claims_register.py`**: a new test, `test_register_check_fails_on_a_duplicate_claim_id`, which works on a tmp copy of the register and its mirrors.
3. **`28_DEFENSE/review_2026_10_20/README.md`**: an appended, dated second-reviewer note summarising F1, F3, F4, F5, F6 and F8. All JSON receipts are byte-for-byte untouched.
4. **Staged, not applied: `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV36_DEFENSE_INDEX_PRESENCE.patch`.** It adds a `presence_2026_10_22: "NOT PRESENT …"` field to D-X and D-XI (+2 lines). The patched JSON parses, and `git apply --check` returns 0.

Backups are in `$S/rv36_bak/`.

## Witnesses

| Witness | Result |
|---|---|
| `math_probes.py` on the baseline worktree | 18/18, identical to the receipt (F1) |
| Pinned-source mutation (scratch worktree) | refused, as it should be |
| Run at HEAD | refused, as it should be |
| `pytest --collect-only` at `6ba483a` / `cf6ff23` | 981 / 1058; the receipt says 999 |
| `tests/test_claims_register.py` on the tree | 3 passed |
| Mutation: duplicate check removed | the new test fails (1 failed, 2 passed); restored and `cmp` identical |
| `tools/verify-claims.py` | rc 0 |
| `ruff` on both edited Python files (clean venv ruff) | all checks passed |
| `tools/verify-links.py` | 0 dead outside the archive |
| `tools/verify_research_intake.py` | rc 0, 2563 files |

**Disclosure.** The duplicate-check mutation was applied to the **live** `tools/verify-claims.py` and then restored, byte-identical by `cmp`. That breaks the standing rule against corrupting live source to test, the same slip disclosed in BATCH32. The correct form is to load a mutated scratch copy through `spec_from_file_location`. The next mutation witness will do that.

## G-items for Mac

- **G-RV36-1:** apply `RV36_DEFENSE_INDEX_PRESENCE.patch`, or write the two promised documents (D-X AI reader test log, D-XI defense audit). **Sol: apply the patch.** An index that names absent documents is exactly what an outside reader catches first.
- **G-RV36-2:** add `"pattern": "^[A-Z]+-[0-9]{3}$"` to `claim_id` in `CLAIMS.schema.json`. All 71 ids already comply. It is a canonical schema, so this needs your word.
- **G-RV36-3:** the 999 count in `verification.json` (F4). Either leave the receipt as issued with the README note (done), or have a future run re-mint it at a named commit. **Sol: leave it, with the note.** Re-minting a historical receipt rewrites history.
- **G-RV36-4 (standing rule for future reviews):** every committed receipt should come with its producer script, or say plainly that it has none. 11 of 13 here cannot be regenerated. It was luck, not design, that they recomputed correctly.
- **G-RV36-5:** independent validation. The whole 28_DEFENSE / review apparatus is self-review plus AI review. The only thing that changes that status is a human outside reviewer or a submitted paper. That is your call and your network; no gate here can stand in for it.
