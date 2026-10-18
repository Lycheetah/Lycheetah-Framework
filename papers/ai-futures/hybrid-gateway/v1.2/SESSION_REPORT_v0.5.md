# Cycle 5 research report — Lycheetah Hybrid Gateway v0.5

**Date:** 2026-10-18 (NZ). **Status:** tested local research code. **GitHub:** untouched.

## Problem recovered from v0.4

v0.4's `ContractedHybridPipeline.stage` rejects candidates whose quotes fail exact operator contracts. However it can stage (a) an empty output, (b) one of two expected facts, or (c) duplicate proposals for the same authorized clause. These are different from unauthorized *admissions*: they are omissions and duplicates that should affect completeness decisions before a human review queue.

## New work

- Created `hybrid_gateway/coverage.py`. An `ExtractionPlan` pins the operator-annotated clause fingerprints, source digest and registry snapshot for a single extraction call. The `CoverageAuditor` invokes the adapter exactly once and issues a structured receipt with missing, duplicate, unexpected and supported-unique counts. Bad batches stage zero commit-eligible claims. All statuses are explicitly *pre-admission*.
- Added an optimistic ledger-head check on `commit_one`. Even with trusted review asserted, an audited stage is not committed if another ledger event has occurred since extraction; it must be re-audited. This is not a transaction manager or real authorisation.
- Added an optional `probe_live_model.py` with four fixed fictional documents: two positive, one absent, one with an example-only misleading quote. It uses the existing v0.3 provider adapter and emits privacy-minimised per-case dispositions. It was only tested with injected fixture transports here; **no real model was queried**.
- Preserved the original v0.2–v0.4 modules and historical tests. The single addition to the v0.4 contract registry is a read-only accessor.

## Test and baseline results

- The original **71** tests passed unchanged before v0.5 modifications.
- All **95** tests passed on the final source, including **24 new** tests (19 coverage tests, 4 model-probe fixture tests, 1 eval regression).
- Evaluated **32 author-defined conformance batches**: eight complete, eight missing, eight duplicate, and eight unexpected. The old v0.4 gate staged all 8 missing and all 8 duplicate batches because each supplied claim was valid; v0.5 correctly designated all 16 for review according to the plan. Both accepted the eight complete batches for review and rejected the eight unexpected batches.
- The offline demonstration showed one of two required clauses missing → `REVIEW_MISSING`, no staged candidates, no ledger mutation. Complete re-extraction → `READY_FOR_REVIEW`; missing human approval → `REVIEW`; explicitly approved first claim → `ALLOW`; then another claim from that stale extraction → `REVIEW`, requiring re-audit.

**Epistemic label:** These numbers are repeatable *protocol and regression results* on synthetic author-defined cases. They do not measure neural model quality, user outcomes or independent accuracy. The comparator is deliberately an earlier version of the same system, not a strong research baseline.

## Relevant current research

- `run-llama/ExtractBench` explicitly measures record completeness, missing-null behavior and evidence attribution across different document schemas: https://github.com/run-llama/ExtractBench
- ACL 2026 survey on attribution/citations/quotations examines the lack of uniform evidence metrics: https://github.com/faerber-lab/AttributeCiteQuote
- Abstention is model-specific, not guaranteed by nullable structured output: https://github.com/MVRU/llm-abstention-evals

These works motivate a better independent evaluation; no equivalence to their accuracy or validity is claimed.

## What this enables *today*

A developer can simulate a controlled fact-extraction and review process and reliably tell whether their configured known clauses were omitted, repeated or supplemented with unapproved suggestions. The system also shows *where it cannot proceed* without approval. It is suited to local research and integration prototyping only, not a production customer workflow.

## Remaining blockers

1. Real local or remote model inference on the four probe cases and subsequent held-out documents.
2. Independently annotated, multilingual and exception-heavy extraction corpus; precision, recall, abstention, wrong-field rate and annotation/review time, with no contract-derived ground truth.
3. Canonical CASCADE checkout smoke and calibration study; CASCADE weights must be independently justified, and its contradictions are proxy predicates.
4. Authenticated source-review credentials and operator authority; externalised receipt head; process isolation; database transactions.
5. Batch-safe update semantics and evaluation against stronger retrieval/temporal approaches.
6. Explicit field-granular contracts from policy variants, exceptions and negations; current English grammar is intentionally restrictive.

## Reproduce

```sh
python -m unittest discover -s tests -q
python demo_coverage.py
python run_coverage_eval.py
python probe_live_model.py --model <your-running-local-model-name>
```

Last command requires a real local provider; it was **not** successfully run in this environment.
