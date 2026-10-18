# Failure Museum — Hybrid Gateway v0.5

Failures are not automatically erased by passing the new tests. Each item marks exactly what is demonstrated and what is not.

## F05-01: Valid evidence, omitted clause

Two clauses are authorized. Model returns only one correctly quoted clause. v0.4 stages one and offers no completeness signal. v0.5 reports `REVIEW_MISSING` and offers zero commit-eligible stages. **Fix scope:** operator-plan completeness only. An absent contract cannot be detected.

## F05-02: Duplicate authorized claims

A model outputs the same clause twice with distinct candidate IDs. Both satisfy the v0.4 individual contract. v0.5 flags the duplicate and refuses to stage a partial batch. **Remaining:** this doesn't prevent redundant requests or repeated annotations outside the model response.

## F05-03: Authority still belongs to human annotation

A perfectly aligned output against a mistaken operator-annotated clause can still be wrong. Exact matches do not establish legality, relevance, correctness, or source-author authority. **Open:** independent source authentication, policy hierarchy, and review governance.

## F05-04: Strict grammars sacrifice coverage

Any legitimate unfamiliar paraphrase, exception, negation or multilingual policy may not be represented by `refund_days_v1`, `online_refund_days_v1`, and `loyalty_points_v1`. The safe behavior is review/abstention; this makes annotation and onboarding cost a first-class product metric, not a footnote.

## F05-05: Stale staging is only partly solved

A ledger event after coverage review invalidates the old single-stage approval. This is optimistic conflict detection, not atomic multi-record admission. An approved first claim followed by a blocked second can leave a partial update. **Open:** durable transaction + authenticated batch review.

## F05-06: Real neural model still absent

The `OpenAICompatibleAdapter` has deterministic mock and local HTTP transport coverage, and `probe_live_model.py` can make actual requests. No model weights or live inference service were available here. Zero live-model inference quality measurements exist in this cycle.

## F05-07: Canonical CASCADE still needs a checkout

The optional demo accepts actual `CascadeEngine`/`KnowledgeBlock` classes from an external checkout. No canonical class execution was observed here; v0.3 stub tests and signature-level mapping are not a substitute. No Π calibration was performed.

## F05-08: A deliberately empty plan may be wrong

An operator can select an empty expected clause set. If the model returns no claims, that batch is `READY_FOR_REVIEW`—but only under that operator's explicit choice. **This is not a finding that a real source contains no relevant facts.**

## F05-09: Pass rate can hide the cost

Contract conformance on author-created cases is cheap to score and partly tautological. It does not measure model utility, independent semantic correctness, false-negative discovery in unannotated documents, or annotation time. Hold-outs and operator-time measurement are required before practical claims.

**Museum invariant:** Record the failure's *mechanism*, not just a passing replacement test.
