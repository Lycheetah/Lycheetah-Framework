# LYCHEETAH HYBRID GATEWAY v0.6 — Atomic Revision & External-Evaluation Contract

**Research cycle 6 · 18 October 2026 (NZ). Local reproducible prototype, not deployed and not pushed.**

Previous versions are preserved in this archive; **v0.6 fixes the explicitly recorded v0.5 partial multi-claim admission limitation**. Claims remain model proposals until tied to operator-controlled source passages, checked against an extraction plan, and accepted by a trusted caller. No model is given SQL write privileges.

## Reproduce

Python 3.10+; standard library for all new modules and tests:

```bash
python -m unittest discover -s tests -q
python demo_atomic.py
python generate_eval_fixture.py
python run_external_eval.py --gold fixtures/external_eval_example/SELF_AUTHORED_gold.jsonl --predictions fixtures/external_eval_example/SELF_AUTHORED_scripted_guesses.jsonl
```

Cycle 6 result at packaging time: **120 passing tests** (95 inherited + 25 new). The source tests, demo, fixture generator, corpus scoring scripts, and reports are all included. No API key or connection required.

## Changed mechanism: one batch, one commit, one event

**v0.5:** two review-eligible source clauses; `commit_one` admitted the first, advanced the head, then refused the second as stale. Safe refusal, but possible partial policy transition.

**v0.6:**
1. Operator registers immutable `SourceDocument` and trusted `TrustedClause` contracts; expected clauses are pinned in `ExtractionPlan`.
2. `CoverageAuditor` stages *zero* candidates unless the exact expected plan is covered. No model-extracted timestamp, tenant or source authority is trusted.
3. `SQLiteLedger.commit_batch` independently checks every stage, contract fingerprint, plan member, receipt digest and current ledger head **inside `BEGIN IMMEDIATE`**. A separate human-controlled approval boolean is required (but is NOT proof of reviewer identity).
4. `HybridGateway.ingest_batch` first preflights the whole batch on a shadow ledger, resolves supersession dependencies, and writes **one** `BATCH_ADMIT` event. If one member fails, zero members are admitted.
5. The event is inserted into SQLite and committed in a single transaction; failed insertion rolls back. `HybridGateway.restore` replays `BATCH_ADMIT` and refuses changed event hashes or sources.
6. Queries remain bitemporal and preserve prior knowledge-time states. A stale receipt or replay attempt cannot write a second batch.

The SQLite backing is a *conventional* single-file local transaction implementation, not a novel storage system. [SQLite transaction reference](https://www.sqlite.org/lang_transaction.html) · [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html).

### Example output

```text
Partial extraction: REVIEW_MISSING | stages: 0
Cannot commit partial: REVIEW
Complete extraction: READY_FOR_REVIEW
Without reviewer: REVIEW
One batch, two claims: ALLOW
Stale replay: REVIEW
After restart: 1 batch events, 2 claims
Policy answer: 14 evidence receipts: 1
No external actions performed; fixture claims only.
```

## Independent-data evaluation interface (scorer implemented, external study NOT run)

- `hybrid_gateway/evaluation.py` and `run_external_eval.py` accept **separately prepared** ground-truth and prediction JSONL; every case ID must match and a frozen corpus SHA-256 can be required.
- Metrics: claim-level TP/FP/FN, precision/recall/F1, wrong-field/scope errors, document-level exact match, positive-document coverage, missed positive documents, negative-correct-abstention rate and self-reported reviewer minutes.
- The 14-case `fixtures/external_eval_example/` corpus is **self-authored and fictional**, and the "scripted" predictions were handwritten. It is only an instrumentation check. The "all abstain" fixture intentionally earns zero positive recall despite perfect negative abstention.
- Before any external validity claim, source third-party documents, freeze a holdout, obtain independent ground-truth annotation, record disagreements, run a real model on that holdout, and compare against strong baselines on exactly the same split. See `EVALUATION_PROTOCOL_v0.6.md`.

## Source / test map

| Component | Status | Function |
|---|---|---|
| `hybrid_gateway/core.py` | Implemented, tested | In-memory `ingest_batch`, shadow preflight, single batch event, deterministic replay |
| `hybrid_gateway/durable.py` | Implemented, tested | SQLite transaction, strict coverage recheck, stale-head detection, restart recovery |
| `hybrid_gateway/evaluation.py` | Implemented, tested | External-data-ready scoring, no model inference |
| `tests/test_atomic_batch.py` | Implemented, tested | Rollback, altered source, corrupt event, review freshness, competing writers, forced child-process exit |
| `tests/test_external_eval.py` | Implemented, tested | Duplicate predictions, mixed examples, all-abstain penalty, frozen digest, malformed inputs |
| `demo_atomic.py` | Implemented, tested | Offline two-clause operator-authorized batch example |
| `generate_eval_fixture.py` | Implemented, tested | Reproducible tiny *author-created* scoring examples |
| `hybrid_gateway/neural.py` | Prior v0.3 adapter | HTTP fixture-tested; no live model inference result |
| `hybrid_gateway/cascade_bridge.py` | Prior v0.3 diagnostic | Original CASCADE engine execution still unverified in this environment |
| `hybrid_gateway/coverage.py` | Prior v0.5 | Exact operator-plan coverage, no unannotated fact discovery |

## Important boundaries

- **SQLite transaction atomicity is not reviewer authentication**. The `reviewer_approved` flag is provided by a trusted caller; no cryptographic review identity or independent authorized signing system exists.
- **The DB file is trusted local state.** A hash chain plus SQLite is not secure against a privileged actor who rewrites the database and recomputes every digest. An independently protected head is necessary to detect that class of compromise.
- **No tests simulated physical power loss**. The child-process abrupt termination exercises a different failure mode. SQLite's documented guarantees depend on the environment and filesystem.
- **No production side effects or customer data**. There is deliberately no effect executor. A real deployment needs authenticated grants, backup/recovery, operational monitoring, independent authorization, secret hygiene, and a threat model.
- **Performance unmeasured at scale.** Each write replays the event chain; this version does not implement snapshots, compaction, multi-node consensus or a high-volume event bus.
- **Only one database file, one local SQLite transaction.** There is no distributed transaction across a model provider, another service, a cloud document store or an external agent action.
- **Evidence can be authentic but wrong or incomplete.** A flawed trusted contract, missing annotation or biased reviewer can still induce wrong outputs; test real tasks and independent annotations.
- **Canonical CASCADE not run here; no neural model run here.** The new work is storage, authority-bound admission and evaluation methodology, not neural-symbolic intelligence quality.

**Governance sentence:** Models propose; the operator identifies authority; coverage checks the delegated task; review authorizes one atomic local revision; the ledger preserves the history.
