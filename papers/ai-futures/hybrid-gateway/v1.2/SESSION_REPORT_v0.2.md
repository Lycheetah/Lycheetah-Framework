# Cycle 2 field report — Lycheetah Hybrid Gateway v0.2

**Date:** 18 October 2026

## Decision

Prioritize a **provider-neutral, reversible, evidence-carrying policy-memory spine**, before any LLM weight editing. Keep existing CASCADE theory as lineage and future integration target without claiming this checkpoint executes CASCADE itself.

## Newly created in this cycle

1. `hybrid_gateway/core.py`: immutable claim/source dataclasses; two UTC clocks; operator-registry evidence binding; optional exact-grammar domain validation; review gate; explicit version/withdrawal graph and conflict abstention; per-result citations; head-anchored hash-chain verification and replay; effect boundary kept non-executing.
2. `demo.py`: deterministic mock model extracts two fictional policy versions; both require review; query answers differ by effective and known times.
3. `tests/`: **42 passing tests**, including a deliberately reproducible false-semantic-grounding failure under the loose mode and prevention in strict mode.
4. `fixtures/synthetic_eval_cases.json` and `run_eval.py`: **22 authored cases** and two source-matched conventional retrieval reference algorithms, emitting each per-case result into JSON.
5. `README.md`, `RESEARCH_HANDOFF_v0.2.md`, `FAILURE_MUSEUM_v0.2.md`, `RESEARCH_REFERENCES.md`: source trace and honestly bounded status.

## Measured locally, not independent

| Engine | Outcome correct / all | Primary failure mode |
|---|---:|---|
| B0 newest known document | 8/22 | wrong effective date, collisions, retractions |
| B1 bitemporal newest applicable | 13/22 | unresolved conflicting documents and approved withdrawal |
| H1 explicit bitemporal ledger | 22/22 | none of the hand-authored targets; separately exposed semantic misbinding in loose mode |

This measures conformity to our own cases, not true task generalization. It is not a benchmark of foundation models, neural extractors, CASCADE, model editing, or commercially deployed RAG.

## Most consequential finding

**A verified source hash and a perfectly accurate quote do not prove the *relationship* claimed.** A loyalty points sentence can be misread as a refunds sentence with a valid citation. Stronger predicate-aware validation reduced this *specific* error by returning `REVIEW`, but its grammar is too narrow for real customer policies. Improving claim entailment/claim-review is the highest-priority follow-up.

## Current maturity

- Stage 0 prior-source inspection: partial, key GitHub documents reviewed; full dependency graph not audited.
- Stage 1 runnable bounded demonstration: **complete for offline fixture**.
- Stage 2 internal baseline probe: **completed only for synthetic authored cases**; independent evaluation still outstanding.
- Stage 3 live business pilot: **not started**.
- Stage 4 neural weight editing: **not started**.

**No repository changed remotely. No live customer data, hosted models, effects, signatures or production claims.**
