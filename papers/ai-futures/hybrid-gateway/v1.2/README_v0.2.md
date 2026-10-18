# Lycheetah Hybrid Intelligence — executable checkpoint v0.2

**Date:** 2026-10-18 · **Status:** local research prototype, *not deployed* · **Remote GitHub status:** no branch created or pushed by this work.

**Research question:** Can a provider-neutral evidence ledger improve responses to versioned business-policy questions by enforcing **what was effective when**, **what we knew when**, **who/what supports the claim**, and **what changes were explicitly authorized**? This package implements a narrow test of that composition. The neural component is **mocked**; CASCADE integration is **proposed, not active**. It is not a full live neuro-symbolic architecture.

## What works in this package

- Source registry with immutable per-ID body digests and tenant scope.
- Candidate adapter contract: a model *may propose* claims, never grant its own review/authority.
- Two clocks: **valid time** and **recorded (knowledge) time**, normalized to UTC.
- Human-review parameter on admission and withdrawal (trusted-caller API; **not** authenticated identity).
- Scope-indexed append-only claims, explicit supersessions, withdrawals, conflicts, and abstentions.
- Evidence quote must occur in the registered document; optional **domain-specific validator** can check the quote-to-field mapping for a narrow refund-window grammar.
- Source citations, recorded time, effective interval, and source hashes returned with answers.
- Append-only hash-chained event log, export, integrity checking, and deterministic restore given a **pinned external head** and original registered sources.
- No tool dispatch method; attempted side effects always return `REVIEW`.

## Run in 3 commands

Requires **Python 3.10+**, standard library only.

```bash
cd lycheetah_hybrid_architecture
python demo.py
python -m unittest discover -s tests -v
python run_eval.py
```

The evaluation also writes `results/synthetic_evaluation_v0.2.json`.

## Internal results

| Variant | Correct response/abstention on 22 hand-authored fictional cases |
|---|---:|
| B0 — latest admitted document, tenant/scope isolated | 8/22 |
| B1 — bitemporal retrieval, most recent effective document | 13/22 |
| H1 — version ledger, explicit supersession/withdrawal/dispute | 22/22 |

All three only cite sources present in the fixture registry (empty citations on legitimate abstentions are counted as satisfying the citation requirement). **This is deliberately an internal, author-designed, feature-focused smoke test**, not independent evidence that this beats strong modern RAG or commercial systems. H1 functionality overlaps established temporal and version-aware retrieval research. No statistical significance claim is appropriate. Scores are not measurements on a live LLM.

## Concrete outcomes

- A policy effective February 1 but discovered February 10 yields **14** when querying as the system knew on February 5, but **21** when querying the effective February 5 rule using knowledge available on February 20.
- Conflicting accepted documents with no explicit precedence cause **ABSTAIN_CONFLICT**, not silent priority by model confidence.
- An explicitly approved withdrawal of the 21-day revision causes the older 14-day revision to become applicable again when its interval is still valid.
- A second tenant or scope never borrows a policy from another tenant or scope.
- A proposal by a mock neural provider is `REVIEW` until trusted-caller approval; a tool proposal has **no executable effect path**.

All policies, dates and merchants are fictional fixtures.

## The critical distinction from CASCADE

Existing [`CASCADE`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/core/cascade_engine.py) is the **lineage and intended interoperability target**, not a dependency imported or proven effective by this checkpoint. Its `contradicts` check equates same-domain / different-paradigm / universal with contradiction; our policy record cannot use that heuristic without false conflicts across time and scope. **The v0.2 ledger implements a separately testable symbolic revision contract**. Later integration should send only scoped, temporally eligible, properly reviewed candidates to CASCADE diagnostics; truth-pressure weights cannot be invented just to generate outputs.

Existing [`34_ASSURANCE_RUNTIME`](https://github.com/Lycheetah/Lycheetah-Framework/tree/master/34_ASSURANCE_RUNTIME) and Action Guard are similarly intended enforcement integrations. This package stops before side effects; it does not claim those runtime modules are wired in.

## Key limitations

1. The default lexical quote check can accept a **semantically wrong relation** even if the cited words exist in a source. `tests/test_known_failure.py` reproduces this failure. The optional `refund_window_quote_validator` prevents that specific known case but only understands one exact sentence grammar; other domains need verified extractors or human semantic review.
2. `reviewer_approved=True` is not cryptographically authenticated, and source registration is operator-trusted. This is not an access-control or identity solution.
3. The hash chain detects record changes **relative to a separately retained head digest**. Without a trusted head/key/append-only store it is not tamper-proof or evidence of who authored a record. The in-process dictionaries remain mutable.
4. Registered documents may contain malicious instructions. They are inert in this offline ledger, but future real-model integrations must treat them as untrusted data, not instructions.
5. No actual neural API, semantic NLI, production RAG system, vector index, DB, trained model, ROME/MEMIT, authentication, human reviewer UI, release binary, or deployed pilot is included.
6. Baselines are simple reference algorithms, **not VersionRAG or a strong production RAG comparator**. Outcomes are not blind-labeled.
7. A restored chain is only as trustworthy as its externally retained pinned head, source registry, and trusted clock. Ingested records can include sensitive business content in a real application; **use fictitious data here**.

## Package layout

- `HYBRID_INTELLIGENCE_RESEARCH_CHARTER_v0.1.md` — original charter, preserved.
- `hybrid_gateway/core.py` — narrow symbolic claim/event API.
- `hybrid_gateway/__init__.py` — public exports.
- `tests/` — executable contract and deliberate limitation tests.
- `fixtures/synthetic_eval_cases.json` — full scenario definitions and expected outcomes.
- `run_eval.py` — deterministic three-way comparison.
- `demo.py` — chronological human-review and query demonstration.
- `results/synthetic_evaluation_v0.2.json` — per-case results including mistakes.
- `FAILURE_MUSEUM_v0.2.md`, `RESEARCH_HANDOFF_v0.2.md`, `RESEARCH_REFERENCES.md` — limitation, integration and literature notes.

**Working principle:** No apologies for creating. No claims beyond the evidence.
