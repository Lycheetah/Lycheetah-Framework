# Hybrid Gateway Cycle 9 — signed authority, not a new model

**Date:** 18 October 2026 · **Status:** research prototype · **Lineage:** v0.2–v0.8 preserved.

## Aim and pivot

The planned live-neural / canonical-CASCADE benchmark remains blocked by an unavailable live inference service and trusted on-disk upstream source, and independent annotated documents have not yet been supplied. Rather than manufacture these measurements, Cycle 9 addresses an observed local authorization gap: a boolean `reviewer_approved=True` at the durable commit boundary.

## Implemented

- `hybrid_gateway/authorization.py`: typed short-lived operator-key HMAC permits, one-shot nonces, keyed domain separation, exact batch+plan+source+recording-time+ledger-head binding, bounded TTL.
- `hybrid_gateway/durable.py`: persisted strict mode; enforcement inside the SQLite transaction; nonce consumed atomically with event; persisted random ledger ID; locally verifiable archived MAC/event attachments and fail-closed unknown policy.
- `demo_signed_review.py`: two fictional approved claims are committed as one event in strict mode, bare flag rejected, permit replay blocked, archived approval checked after reopen.
- `tests/test_signed_review.py`: 36 new contract tests. Existing tests kept unchanged.

## Reproduction

```text
python -m unittest discover -s tests -q
Ran 190 tests; OK.

python demo_signed_review.py
No signature: REVIEW
Signed exact batch: ALLOW | claims: 2
Replayed permit: BLOCK
Audit after restart: 1 valid signature/event binding
```

No external effects. This is not production approval infrastructure or independently assessed security. Real review identity, review-time accounting, independent temporal annotations, live-model extraction and canonical CASCADE inference were **not** tested this cycle.

## Defensible result

A strict local SQLite ledger now requires a keyed, batch-specific cryptographic permit in place of a bare boolean, while retaining the original atomic commit and temporal behavior. Under the stated trusted-key/DB assumptions, the associated regression tests pass. No claim of breakthrough AI accuracy, authenticated human consent, new temporal database capability, or hostile code isolation.

## Next experiment

Deploy the signing logic behind a real authenticated human review interface and define a *frozen* external set of evolving policy documents annotated by people who did not author the gateway. Compare end-to-end task success **and** review burden to the temporal SQL/RAG baseline. Canonical CASCADE execution remains optional, read-only and held apart from admission authority.
