# LYCHEETAH HYBRID GATEWAY v0.5 — Coverage Before Commitment

**Research cycle 5 · 18 October 2026 · offline-first · research prototype · not deployed / not pushed to GitHub.**

**Core finding:** A strict quotation or clause-authority gate is **not** a completeness check. v0.4 could stage `[]` or one fully supported claim even when an operator expected two different clauses to be recovered. v0.5 introduces an opt-in coverage protocol that reports **omitted**, **duplicated**, and **unexpected** candidates separately and does not stage any part of an incomplete batch.

The v0.2 bitemporal ledger, v0.3 HTTP adapter and CASCADE diagnostic, and v0.4 exact-clause contracts remain. Nothing here asserts model consciousness, novel continual learning, trained alignment, secure identity, unbounded natural-language understanding, or deployment-readiness.

## Reproduce

Requires Python 3.10+; all main tests and offline probes use the Python standard library. The optional canonical CASCADE smoke requires a separate official Lycheetah checkout and NumPy.

```bash
cd lycheetah_hybrid_architecture_v0_5
python -m unittest discover -s tests -q
python demo_coverage.py
python run_coverage_eval.py
python demo_contracts.py
python run_contract_eval.py --output results/contract_eval_v0.4.json
```

**Latest verified package:** 95/95 deterministic unit tests (71 inherited, 24 new). Run the actual commands rather than treating this line as an independent security attestation.

## Four-step v0.5 architecture

1. A **trusted operator** registers immutable source text and annotates exact authoritative clauses with subject/predicate/scope/effective window (v0.4 contracts).
2. An operator establishes an **extraction plan**, selecting expected clause fingerprints for one model call. It can intentionally expect zero values, but then the operator accepts the responsibility for deciding that the relevant value is absent.
3. An **untrusted model** proposes structured claims. The coverage auditor matches them against the selected plan and reports `REVIEW_MISSING`, `REVIEW_DUPLICATE`, `REVIEW_UNEXPECTED`, or `REVIEW_MIXED`. No staged candidate survives a failed batch. A correctly complete batch is only `READY_FOR_REVIEW`.
4. The caller separately supplies **human approval**. An optimistic ledger-head check refuses to commit if the ledger has advanced since audit. There is still no authenticated identity or transaction manager: one claim is committed at a time, and multiple claims require re-auditing after each admission.

A system that wants automatic discovery across a document still needs a reliable discovery procedure. **This gate only measures completeness against the operator's selected annotated clauses**, not all facts implicitly present in the source.

## Evaluation — contract conformance only

`python run_coverage_eval.py` exercises 32 authored synthetic batches (8 in each family):

| Family | v0.4 stage accepted | v0.5 review-ready |
|---|---:|---:|
| Complete/selected plan | 8/8 | 8/8 |
| Missing required claim | 8/8 | 0/8 |
| Duplicate authorized claim | 8/8 | 0/8 |
| Extra unsupported or out-of-plan claim | 0/8 | 0/8 |

These are NOT independently annotated real documents, nor actual model outputs. In particular, the v0.5 labels are defined using the same operator plan as the gate, so scores demonstrate implemented invariants, not independent accuracy. Both systems still require reviewer authorization before admission.

## Optional neural probe (not run with a real model in this cycle)

```bash
# Run on your own machine with an already-running OpenAI-compatible local model:
python probe_live_model.py --model qwen2.5:7b

# Or configure a remote OpenAI-compatible HTTPS endpoint *explicitly*:
# LYCHEETAH_MODEL_API_KEY=... python probe_live_model.py --model ... --base-url https://provider.example/v1 --allow-remote-https
```

The probe sends **four embedded, fictional documents** to the chosen model and checks structured output against pre-annotated clause expectations: two have a current refund rule, one contains no refund rule, one contains an example-only refund statement. It logs only a model label, case identifiers, counts, and dispositions. It does not log source bodies or model completions. It never admits a claim.

This runtime had **no working Ollama endpoint, no installed local model weights, and no configured model for actual inference**. The probe was tested with an injected, deterministic fixture transport. Its metrics are **not** a live-model evaluation. The chosen provider may not support the requested JSON schema; errors are counted as failures, not secretly coerced into abstentions.

## Optional original CASCADE smoke — still not exercised

```bash
python demo_cascade_canonical.py --framework-root ../Lycheetah-Framework
```

The bridge accepts `CascadeEngine` and `KnowledgeBlock` constructors from the independently installed original `12_IMPLEMENTATIONS/core/cascade_engine.py`. It is read-only and refuses to invent Π weights. The original engine wasn't installed in this build environment, so a tested canonical import/invocation **remains pending**. This optional diagnostic MUST NOT override ledger facts or grant execution permission.

## Source map

- `hybrid_gateway/core.py`: unchanged v0.2 source-anchored, bitemporal ledger.
- `hybrid_gateway/neural.py`: unchanged v0.3 OpenAI-compatible extraction adapter.
- `hybrid_gateway/contracts.py`: v0.4 contracts plus a read-only `contracts_for_source` accessor.
- **`hybrid_gateway/coverage.py`**: new typed extraction plan, coverage receipt, pending review stages, stale-head check.
- **`probe_live_model.py`**: provider-backed optional four-document instrument with fixture-injected tests.
- **`run_coverage_eval.py`** / **`demo_coverage.py`**: reproducible coverage regression and no-side-effect demonstration.
- `tests/test_coverage.py`, `tests/test_live_probe.py`, `tests/test_coverage_eval.py`: new checks.
- `SESSION_REPORT_v0.5.md`, `FAILURE_MUSEUM_v0.5.md`, `RESEARCH_HANDOFF_v0.5.md`: analysis, known failures, next agent directions.
- `README_v0.4.md`, earlier session reports and Failure Museums: source lineage preserved.

## Important safety and research boundaries

- **The annotations are a prerequisite, not verified truth.** An incorrect operator plan yields incorrect coverage conclusions. Unmarked facts do not appear in missing-count metrics.
- **Not semantic entailment or production LLM extraction.** Grammar support remains narrow; natural paraphrases and footnotes can require manual review.
- **Not a security boundary against a hostile Python process.** In-memory objects, digest receipts, approval booleans and ledger state require external identity, key storage, durable transactions and effect execution controls.
- **Not transactionally atomic.** Multi-clause updates are not all-or-nothing. Re-audit after each single admission; adding a real durable batch transaction is the next engineering target.
- **Not independently benchmarked.** Measure model completeness, correct abstention, annotation cost and human review load on held-out independently labelled documents before any product or research claim.

**Design principle:** The neural model may propose. The operator chooses authority. The ledger preserves temporal evidence. The gate measures whether this exact delegated task was completely accounted for, not whether the world is fully understood.
