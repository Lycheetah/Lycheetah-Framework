# Batch 19 — RV20 Cellular sheaf and factorial experiment

Reviewer: Sol (Claude Opus 5.5, xhigh) · 2026-10-22 · branch `review/full-framework-2026-10-20` at `d7ae0ad`, working tree only, nothing committed.
No "reviewed" label was inherited. The prior critique (`TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/SHEAF_KNOWLEDGE_REVIEW.md`, Caelorynth, 18 Oct) was re-tested point by point below.

## Coverage (what was actually read and run)

| Surface | Coverage |
|---|---|
| `12_IMPLEMENTATIONS/core/sheaf_cohomology_factorial.py` (1223 lines at HEAD) | Read in full: `_svd_parts`, `CellularSheaf`, `paradigm_stalk_vector`, `SheafCascadeEngine`, `simulate_orthogonal` (window, drain, work coupling), `compute_yates_factorial_effects`, `run_sheaf_and_factorial_study` |
| `tests/test_sheaf_cohomology_factorial.py` (382 lines at HEAD) | Read in full; extended (3 tests) |
| `lycheetah/consensus/arena.py` `sheaf_cohomology_report` (lines 322–368) and the class head (140–240) | Read; measured in C8 |
| GLASS_TRANSITION: `SHEAF_KNOWLEDGE_REVIEW.md`, `TOPOLOGICAL_RESULTS.md`, `README.md` | Read |
| GLASS_TRANSITION recorded data (`results.*`, `load_aware.*`, `topological_recorded.json`) | **Not re-derived here.** None of it is output of the sheaf factorial; there is **no recorded run of the 2×2×2 factorial anywhere in the repo** (MEASURED: only the module, its tests, two READMEs, the review and the arena reference it) |
| `CHANGELOG.md:425` consensus entry | Read |

Coverage limit, said plainly: the eight factorial cells were exercised from code at the module's defaults (4 topologies × seeds (0,1) × loads (1,3), 8 concepts, 48 proposals). No larger run was made, and no recorded run exists to audit.

## Findings

Labels: MEASURED = reproduced by `repro_batch19.py` (15/15 PASS). DERIVED = read from the code.

**F1 — work_coupled does not pay the work a lookahead completion performs. MEASURED. Severity: high for any causal reading of the duration factor.**
`simulate_orthogonal` estimates work by a probe clone at service start, schedules the completion from that estimate, and then the live engine adjudicates against the store as it stands at completion. Under lookahead, the store has grown in between.
- `lookahead/all_domains/work_coupled`: 94/532 jobs differ, net **+233,001 unpaid work units**, worst run ratio actual/paid **8.67** (diamond_cycle, seed 0, load 3: paid 2627, actual 22771).
- `lookahead/domain_isolated/work_coupled`: 63/553 differ, net +3,104; run ratios 0.98–1.05.
- Control: both snapshot cells give **0/509 and 0/564**. The probe clone is faithful when the visible set is frozen, so the mismatch is the timing mode, not a cloning bug.
- Consequence: in the two lookahead work_coupled cells, the "duration" main effect, every interaction involving duration, and the cascade drain and *g* numbers are computed under unpaid work. Because unpaid work is unevenly spread (some jobs are overpaid, down to −2294), work coupling also changes effective utilisation. The duration factor is therefore partly confounded with load (DERIVED).
- This upgrades Caelorynth's point 3 ("a missing invariant, not a measured failure count") to a measured failure count.

**F2 — the Euler–Poincaré check cannot fail. MEASURED.** `dim C⁰ − dim C¹ = dim H⁰ − dim H¹` holds by dimension counting for *any* rank value. When the rank was forced to 1 on the 6-concept diamond_cycle sheaf, the certificate claimed dim H⁰ = 11, and EP still held. The true rank 10 gives dim H⁰ = 2, and EP also holds. Tests that assert EP therefore assert arithmetic, not the SVD. (The rank itself *is* independently pinned by the existing fixed-direction and scale-fixture tests, so the gap is in the wording, not the coverage.)

**F3 — the experiment's "obstruction" is parent-label inequality, and other labels collide. MEASURED.**
- For labels a/b (the only ones the experiment generates), up to 4 parents: obstructed ⇔ the parent labels differ, for every multiset. Under identity maps on basis vectors the sheaf certificate is an exact restatement of `len(set(labels)) > 1`.
- `paradigm_stalk_vector` hashes any other label. At d=2, `c → a`'s basis vector. Over labels a–d with k ≤ 3 parents, **30 distinct-label parent sets are reported consistent**. At d=1 everything except a maps to −1.
- So the linear algebra adds no information beyond the labels in this experiment, and for an input outside {a, b} it can hide a real disagreement.

**F4 — `has_discordant_parent`'s coboundary-energy condition is redundant. MEASURED.** Over all 16 obstructed a/b stars with k ∈ {2, 3}, it never vetoed (0/16). Under identity maps, a nonzero relative obstruction implies a nonzero coboundary for any child value.

**F5 — `parents_v3` docstring contradicted the code. MEASURED.** The docstring said k ≥ 4 depends on (k−3, k−2); the code gives `parents(4) = (2, 3)`, i.e. (k−2, k−1). Docstring repaired.

**F6 — `service_before_horizon` was computed and dropped. DERIVED.** The counter existed but was never returned, unlike the sibling modules' `service_completions_in_window`. It is now returned under that name.

**F7 — censoring and windows. DERIVED.**
- `mean_g` and backlog are time-averaged over [0.2·horizon, last arrival].
- `mean_work`, and so `loaded_to_calibrated_work` and the work-ratio effects, pool **in-window and drain** completions.
- The two families of metric are therefore measured over different job sets. The drain is run to completion (not censored), and its duration is reported. Labelled as a design note, not a defect.

**F8 — sample size and uncertainty. DERIVED.** The effects are computed at the highest load only, from 8 rows per cell (4 topologies × 2 seeds). No interval, standard error or replicate spread is reported. The cascade−FIFO difference pairs rows by `zip` in loop order, not by `trace_sha256`. That is correct today, because the loops are aligned, but nothing checks it. Matched traces across cells (common random numbers) are good design and are kept.

**F9 — Yates algebra is correct. MEASURED (control).** All seven effects plus the mean equal twice the corresponding OLS coefficient on a ±1 design.

**F10 — FIFO is structurally immune to timing and scope. DERIVED, already in the prior review.** Only cascade rows can carry the timing and queue effects. FIFO is a baseline for *g*, not for the factor structure.

**F11 — `max(1, engine.work)` floor. DERIVED.** Zero-work jobs are paid one unit of service. These appear as overpaid in the new receipts, which is correct accounting, not a fault.

**F12 — ConsensusArena's H¹ is topology only. MEASURED.**
- `sheaf_cohomology_report` builds an identity-map sheaf on the healthy-agent graph. `cohomology_certificate()` reads no agent state.
- Three agreeing agents and three opposed agents on the same triangle both report **dim H⁰ = 2, dim H¹ = 2**. Only the Dirichlet energy differs (0.0 vs 8.0).
- `CHANGELOG.md:425` advertises "H^1(G, F) sheaf cohomology obstruction detection". As implemented, the dim-H¹ number detects cycles in the mesh, not disagreement.
- The same CHANGELOG line says "33% Byzantine quarantine", while the class docstring says quarantine "does not detect Byzantine agents". That is a lead for the consensus RV; it is not adjudicated here.

### Prior critique reassessed (SHEAF_KNOWLEDGE_REVIEW.md)

| Point | Status now |
|---|---|
| 1 fixed-subspace counterexample | Repaired in code before this batch; pinned by the existing reflection test. Confirmed passing. |
| 2 cutoff mismatch | Repaired (one shared cutoff in `_svd_parts`); pinned by the 1e12 scale fixture. The fixture now reports H¹ = 1 while the exact value is 0, labelled `SVD_CUTOFF`. That is honest truncation, as the checklist warns: a floating-point certificate is not exact algebra. |
| 3 lookahead work mismatch | **Confirmed and now measured** (F1), with per-job receipts in the output. |
| 4 local residual = parent variance, hash collisions | **Confirmed** (F3), with a collision pinned by test. |

A green diagnostic in this module is not causal proof. F1 and F3 together mean the factorial's current outputs cannot be read as "sheaf consistency causes the glass transition": the gate is label inequality, and one factor runs on unpaid work.

## Writes (all uncommitted)

| Path | Change | Kind |
|---|---|---|
| `12_IMPLEMENTATIONS/core/sheaf_cohomology_factorial.py` | Per-job paid-work receipts (`receipt_jobs`, `receipt_actual_work`, `receipt_paid_work`, `receipt_jobs_underpaid`, `receipt_unpaid_work`, `receipt_jobs_overpaid`, `receipt_overpaid_work`), `service_rule`, `service_completions_in_window`; per-cell `cascade_jobs_underpaid`, `cascade_jobs`, `cascade_unpaid_work` in the factorial summary; docstrings corrected (EP tautology, `parents_v3`, label hashing, redundant condition, estimated-work-at-start) | ADAPTER (exposes existing truth); no behaviour of the simulation changed |
| `tests/test_sheaf_cohomology_factorial.py` | +3 tests: receipt contract with snapshot control, per-cell receipts in summary, hashed-label collision pin | NEW |
| `lycheetah/consensus/arena.py` | `sheaf_cohomology_report` docstring states that dims are topology only and that the energy measures disagreement | docstring only |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch19.py` | Witness script C1–C9 | NEW |
| this ledger | | NEW |

Not touched: `SHEAF_KNOWLEDGE_REVIEW.md` (Caelorynth-authored; this ledger carries the reassessment), `CHANGELOG.md` (historical entry; see G-CONSENSUS-H1).

## Verification

- `python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch19.py <root> <scratch>` → **15/15 PASS**, run against the working tree, a HEAD extract and a mutant, all in scratch:
  - C1 measured on both HEAD and the tree (the finding predates the edit);
  - C2 the new receipts count exactly the underpaid jobs an external probe counts (85/85, 58/58, 0/0, 0/0);
  - C9 the two receipt tests **fail on HEAD source and pass on the tree**, and the receipt pin **fails under mutation** (`receipt_jobs_underpaid` forced to 0).
- The collision pin passes on HEAD and on the tree by design: it pins documented existing behaviour.
- `tests/test_sheaf_cohomology_factorial.py`: 21 passed. Consensus tests (3 files): 42 passed.
- Full suite, run once: **1495 passed, 1 skipped, 1 xfailed, 1 warning** (baseline 1492 + 3 new; warning unchanged and still unattributed).

## Decisions for Mac

- **G-PAID-WORK.** Either (a) make lookahead + work_coupled pay actual work (incremental service: extend the completion when the live adjudication exceeds the estimate), or (b) keep the mechanism and rename the rule `estimated_work_at_start` everywhere it is reported. That label already appears in `service_rule`. Sol's call: **(a)**. A factor called "work coupled" that leaves 8.67× of the work unpaid is measuring the wrong thing, and (b) only names the flaw.
- **G-SHEAF-ENCODING.** Reject labels outside {a, b} (or give every label a distinct basis vector, with d ≥ the label count) instead of hashing. Sol's call: **reject**. Collisions turn real disagreement into "consistent", silently.
- **G-CONSENSUS-H1.** Amend `CHANGELOG.md:425` with a dated correction line (H¹ here counts mesh cycles; disagreement is the Dirichlet energy), or leave the history as written and let the docstring carry the truth. Sol's call: **dated correction line**, not a rewrite.
- **G-FACTORIAL-RECORD.** Record one factorial run with receipts into GLASS_TRANSITION, or leave the module as an unrecorded instrument. Sol's call: **after G-PAID-WORK** — recording now would enshrine F1.
