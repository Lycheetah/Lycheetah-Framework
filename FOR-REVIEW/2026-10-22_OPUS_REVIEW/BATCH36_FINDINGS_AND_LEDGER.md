# BATCH 36 — RV37 · Four reproduced leads (Outbox, ResearchPipeline, TitleReceipt, Hexie)

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

The checklist named four leads for this workstream. Each one was located in source, reproduced with a known-bad input that should fail, and checked against a benign control. All four are real defects. Maintained files are repaired in place. Frozen or canonical files get a staged patch that has not been applied.

## Coverage, stated honestly

- **Read whole:**
  - `32_TIANXIA/implementations/hexie_five_fold.py` and `FIVE_FOLD_HEXIE_COMPOSITE.md` §IV.
  - `14_MYSTERY_SCHOOL/implementations/research_pipeline.py`.
  - `14_MYSTERY_SCHOOL/IDENTITY_AND_RETURN/source/title_receipt.schema.json`, its `examples.json`, and the receipt and state sections of `TITLE_SYSTEM_SPEC.md`.
  - In `03_atomic_resource_authority_finality_v0_9/`: the `commit` path of `atomic_finality.py`, `OutboxRelay.deliver`, the scripted cases in `benchmark.py`, and `atomic_worker.py`.
  - `Action` in `frontier-controls/research_support.py`.
- **Read in part (DERIVED from code, not probed):** the commit and outbox path of `04_dependency_scoped_evidence_finality_v1_0/evidence_finality.py`, lines 527, 543 and 647–649.
- **Not edited (mirrors named in the ledger only):** `14_MYSTERY_SCHOOL` `GETTING_STARTED.md`, `QUICK_REFERENCE.md:120,220` and `MYSTERY_SCHOOL_COMPLETE.md:131-140`.
- **DID NOT RUN:**
  - The full Python suite. Only the two focused test files were run.
  - The v1.0 benchmark.
  - Any regeneration of the v0.9 `reports/report.json` or its checksum files in the repository. The benchmark was run only on scratch copies.

## Findings

| # | Status | Finding |
|---|---|---|
| L1 | MEASURED | **The v0.9 atomic-finality outbox does not bind its payload to the admitted Action.** `commit(effect_id, action, payload)` checks the Action's hash against the reservation, then writes the separate, free-form `payload` into the outbox. `OutboxRelay.deliver` sends `payload_json`, never the Action. **Known-bad** (scratch DBs): admit job 1, then commit with a job-999 payload. The result is `COMMITTED`; the outbox `action_hash` still equals the admitted hash; the relay reports `SETTLED`; **the provider executes the job-999 payload**. **Control:** case 11's action substitution still returns `DENY action-substitution` with no outbox row. So the gate guards the label, not the effect. |
| L1b | DERIVED (code) | The same pattern (an Action checked, a separate payload stored and relayed) appears in v1.0 `evidence_finality.py:527,543,647-649`. Not probed. |
| L1c | MEASURED | **The benchmark could not see L1.** All 11 scripted cases pass on the vulnerable gate, because no case sends a payload that differs from the Action. Its race, thread, process and trace results do not touch the outbox payload. |
| L2 | MEASURED | **A single study could reach FOUNDATION.** A single HIGH-rated study with d=0.16, n=200 and p=.04 gives Π=1.600, which is FOUNDATION. That holds when the study is an RCT, and equally when it is a CASE_STUDY. With one study, consistency is 1.0, `study_type` is not used in Π, and the noise floor is 0.1. d=0.15 gives Π=1.4999999999999998, which is MIDDLE: a float edge, not a reasoned line. |
| L2b | MEASURED | **Π is non-monotonic in evidence.** d=0.16 plus an *equal* replication keeps Π=1.600 (FOUNDATION). d=0.16 plus a *stronger* replication (d=0.30) **lowers** Π to 1.324 (MIDDLE). Consistency is computed from the range of effect sizes, so a larger confirming effect is scored as disagreement. The RV37 repair does not fix this. It is G-RV37-4. |
| L2c | MEASURED | **The example data is mislabelled.** The module header says "real research" while the data is tagged "real-ish". Khoury (2015) is entered with year 2014. Balban (2023) is entered with year 2020. "Joyce & Herbison (2015) Cochrane Review" is typed RCT, though a Cochrane review is a systematic review. The citations themselves were not checked against the literature here (UNVERIFIED). |
| L2d | MEASURED | **The thresholds are duplicated in prose.** `QUICK_REFERENCE.md:120,220` carries its own inline threshold logic, and `MYSTERY_SCHOOL_COMPLETE.md:131-140` asserts "Shadow work Π ≈ 1.7". Neither is generated from the code. |
| L3 | MEASURED | **The title-receipt schema accepts receipts that the spec forbids.** Under Draft 2020-12, three receipts validate with 0 errors: an EARNED receipt with `bearer_choice: false` and no gate, evidence or witness; an EARNED receipt with witness `NONE` and null gate and evidence; and a TRANSMUTED receipt with `bearer_choice: false`. The spec says EARNED means "a defined School gate has been passed". The state machine says "AI may propose a TRANSMUTED name but cannot accept it for the bearer". **Control:** the unknown state `MASTER` gives 1 error. No validator in the folder checks receipts (`validator.py` and `return_validator.py` do not), so the schema is the only guard. |
| L4 | MEASURED | **Hexie's "greatest marginal improvement" claim is false under its own formula.** H₅ = (I+C+E+O+S)/5 is linear, so +0.05 on any component moves H₅ by exactly +0.0100 (∂H₅/∂k = 1/5). The binding constraint is also not unique: with I=E=0.5, `components.index(min)` returns the first in order (innovation). The spec's inequality line and its "minimal H₅ improvement" sentence do not follow. A min or geometric-mean aggregate (∂G/∂k = G/(5k)) would make the claim true. |

## Repairs (working tree)

**Maintained files, edited in place.** Backups are in the session scratchpad under `rv37_bak/`.

1. **`32_TIANXIA/implementations/hexie_five_fold.py`**
   - The `binding_constraint` docstring now says what the code does: "the lowest-scoring component (ties resolve in I, C, E, O, S order)".
   - A dated RV37 review note covers equal 1/5 marginals, headroom (1−k), and the concave alternatives.
   - A new self-test, `test_marginal_effect_is_equal_under_linear_average`, is wired into `run_all_tests`.
2. **`32_TIANXIA/FIVE_FOLD_HEXIE_COMPOSITE.md`**
   - A dated RV37 note under the §IV heading.
   - The formal inequality line and the "minimal H₅ improvement" sentence are struck through with dated reasons, not deleted.
   - The note cites the witness `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_rv37.py`.
3. **`tests/test_tianxia_operators.py`**: appended `test_hexie_marginal_gain_is_equal_across_components`.
4. **`14_MYSTERY_SCHOOL/implementations/research_pipeline.py`**
   - A module review note.
   - A comment at the consistency line describing L2b.
   - A new class attribute `FOUNDATION_DESIGNS = (RCT, META_ANALYSIS, SYSTEMATIC_REVIEW)`.
   - `get_layer_recommendation` now caps at MIDDLE unless there are **at least two studies and at least one controlled design**. Π itself is unchanged.
5. **`tests/test_research_pipeline_layers.py`** (new), with three tests:
   - a single HIGH study is capped at MIDDLE;
   - uncontrolled designs are capped at MIDDLE;
   - the CBT example still reaches FOUNDATION.

**Staged patches, not applied:**

6. **`RV37_OUTBOX_PAYLOAD_BINDING.patch`** covers v0.9, which is frozen by `SOURCE_SHA256SUMS.json` and `SHA256SUMS.json`.
   - **`atomic_finality.py`:** `commit` now denies `payload-substitution` before any outbox write unless `payload == action.arguments`. The deny is audited, like the existing deny paths.
   - **`benchmark.py`:** its 12 commit call sites now pass `X.arguments`.
   - **`benchmark.py`:** a new scripted case, `payload-substitution-denied-before-outbox`.
   - **Checks:** `git apply --check` returns 0, and 55 lines change.
   - **`atomic_worker.py` is unchanged.** Its payload `{"job": i}` equals its Action's `arguments={"job": i}`.
   - **Applying it** also requires regenerating `reports/report.json` and both checksum files. That is a freeze decision (G-RV37-1).
7. **`RV37_TITLE_RECEIPT_SCHEMA.patch`** is for a canonical schema, the receipt grammar in TITLE_SYSTEM_SPEC §15.
   - It adds a `$comment` and an `allOf` of `if`/`then` rules:
     - **EARNED:** requires a non-empty `gate_id` and `evidence_uri`, a `witness_type` of ARTIFACT, PEER, SYSTEM or REVIEWER, and `bearer_choice` true.
     - **WITNESSED:** requires a non-empty `evidence_uri` and an outside witness.
     - **TRANSMUTED:** requires `bearer_choice` true.
   - `git apply --check` returns 0.
8. **Witness scripts** (repo-relative paths, no home paths):
   - `repro_rv37.py` (L2, L3, L4).
   - `repro_rv37_outbox.py` (L1). Its usage is `<empty scratch dir> [gate dir]`, and it writes only to the scratch dir.

## Witnesses

| Witness | Result |
|---|---|
| Outbox probe, live gate | `COMMITTED`, relay `SETTLED`, provider executed `job-999`. The control is `DENY action-substitution` with no outbox row. |
| Outbox probe, patched copy | `DENY payload-substitution`, no outbox row, nothing relayed. The control is unchanged. |
| v0.9 benchmark, original (scratch) | Scripted 11/11; races 64 with 0 violations; threads 5/16 and processes 6/20 with 0 errors; traces 259/259 |
| v0.9 benchmark, patched (scratch) | Scripted 12/12; everything else is identical |
| **Mutation:** the new benchmark run against the **unpatched** gate | 11/12. Only `payload-substitution-denied-before-outbox` fails, so the new case can fail. |
| Schema, before and after the patch (12 cases: 7 that must be rejected, 5 that must be accepted, including both `examples.json` receipts) | Before: 6/12 correct, and all 6 that should be rejected are accepted. After: 12/12 correct. The patched schema passes `check_schema`. The live schema is byte-identical to the original. |
| `pytest tests/test_research_pipeline_layers.py tests/test_tianxia_operators.py` | 27 passed |
| `hexie_five_fold.py` self-test | all passed, including the new marginal test |
| **Mutation:** the RP cap removed (a scratch copy swapped into the test module) | 2 of the 3 tests fail. The CBT control still passes, as it should. |
| **Mutation:** unequal Hexie weights `0.4·I + 0.15·(C+E+O+S)` (scratch copy) | the new test fails; the live file passes |
| `ruff` (venv) on the 4 edited Python files | all checks passed |
| `tools/verify-links.py` | 0 dead outside the archive (22 inside `99_ARCHIVE`, unchanged) |

Every mutation in this batch ran on a scratch copy. No live file was altered to test.

## G-items for Mac

- **G-RV37-1 (the security one):** apply `RV37_OUTBOX_PAYLOAD_BINDING.patch`, then regenerate the v0.9 report and both checksum files, and record that the freeze was reopened for a security fix. **Sol: apply it.** A finality gate that authorises one action and executes another is the failure the paper exists to prevent. Then extend the same binding to v1.0 (L1b), which needs its own probe first. Anywhere the paper or its README claims "no unauthorised effect", that claim should carry a dated note until the fix lands.
- **G-RV37-2:** apply `RV37_TITLE_RECEIPT_SCHEMA.patch`. One sub-question is yours alone: must `bearer_choice` be true for EARNED? Sol says yes. A title the bearer did not choose to carry is a label, not a receipt. If you say no, delete that one `const`.
- **G-RV37-3:** the Hexie aggregate. Option (a): keep the linear average and live without the binding-constraint claim. That is what the struck spec now says. Option (b): move to a geometric mean or a min, which makes "improve the weakest first" true by construction. **Sol: (b), geometric.** It keeps every component visible, and the claim was the reason for the composite.
- **G-RV37-4:** redesign Π consistency (L2b). Replace the range-based score with one that rewards agreement in sign and direction, so a stronger replication cannot demote a practice. Until then, the RV37 structural cap is a guard, not a cure.
- **G-RV37-5:** fix the example-data labels (L2c), and either generate `QUICK_REFERENCE.md`'s thresholds from the code or point them at it (L2d). Both are mechanical once you say go.
