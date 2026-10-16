# Baseline Findings v3.4

## Why the lifecycle wrapper exists

v3.3 fixed caller-constructed freshness summaries and verifies raw, nonce-bound witness reports, but challenge creation and single-use lifecycle remain responsibilities of the consuming application. A fresh nonce prevents replay across *different* challenges; it does not stop the exact same challenge from being accepted twice if the application reuses it or loses durable consumption state.

## v3.2 counterexamples (frozen source)

The corrected local reproduction harness re-executes five previously documented acceptance cases against frozen v3.2 source:

1. Caller-constructed freshness summary accepted as a currentness proof.
2. Distinct witness IDs aliasing the same Ed25519 public key count as distinct votes.
3. Boolean `True` accepted as certificate `sequence=1` after public digest recomputation.
4. Boolean `True` accepted as `max_byzantine=1` after public digest recomputation.
5. Boolean sequence returned by the pluggable guard accepted on the attest path.

All five are recorded as `ACCEPTED_BY_V3_2` in `baseline_v3_2_reproduction.json`. This reaffirms why public hashes and identity labels are not standalone proof of authenticated state.

## New v3.4 result

A durable challenge row is HMAC-authenticated and bound to database ID plus an issue-time policy fingerprint. The successful verification transition is conditionally committed after signature, quorum, chain, nonce and timestamp checks. In the local shared SQLite reference, a concurrent race permits one successful consumption only; normal restarts preserve that consumed state.

## Remaining negative control

The test `test_known_limit_restoring_preconsume_snapshot_allows_replay` proves that restoring the *entire* pre-consumption SQLite snapshot under the same HMAC key restores the challenge to `PENDING`, and the same response can be accepted again. HMAC makes individual edits detectable; it cannot authenticate recency when both the record and its tag are rolled back together.

The counterexample is intentionally retained in the green test suite. It is a requirement for the next integration phase: a separately administered non-rollbackable store must atomically mark the nonce consumed or advance a protected monotonic high-water mark.
