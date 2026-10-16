# Threat Model v3.4 — Durable Freshness Challenge Lifecycle

## Target property

For a single issued freshness challenge, under the same durable and trusted verifier state, at most one concurrent verification call returns a successful current chain. Challenges are bound to one database ID and one verification-policy configuration. Replayed signed reports from a prior challenge fail nonce matching; a successfully consumed challenge fails on subsequent use, including after a process restart.

## Adversary capabilities considered

- Submit arbitrary/caller-constructed `FreshnessChallenge` envelopes.
- Reuse a previously valid challenge and signed reports.
- Submit malformed or stale fresh-head reports.
- Race multiple verifier instances against the same SQLite ledger.
- Change the verifier's roster/fault-budget configuration between issuance and verification.
- Modify individual local ledger rows without possessing the HMAC key.
- Open a pre-existing incompatible schema.

## Defences in this version

- Random nonce issuance via the underlying v3.3 `new_freshness_challenge()` function; shape enforced at issue time.
- Persisted nonce lookup; caller envelope's times are never trusted.
- HMAC on the canonical challenge row including lifecycle state.
- Policy fingerprint tied to protocol version, key IDs and raw Ed25519 public keys, Byzantine budget, clock-skew limit, and challenge TTL.
- Schema validation and fail-closed row type/shape/HMAC validation.
- Full v3.3 verification of chain continuity and fresh signed witness reports before state transition.
- `BEGIN IMMEDIATE` and conditional `UPDATE ... WHERE state='PENDING' AND row_hmac=?`, so concurrent calls serialize and exactly one can consume the row.
- Expiry checked before verification and again inside the final transaction, immediately before consumption.

## Executed local tests

The combined source-local unit suite reports 55 passing test methods, including one deliberately affirmative negative control for the snapshot rollback limitation. Test coverage includes concurrent attempts from eight threads, restarts, expiry at both checks, row HMAC tampering, wrong HMAC keys, changed witness roster and fault budget, bad reports, forged nonce, wrong database ID, and schema mismatch. Five historical v3.2 baseline acceptances were re-run against the frozen baseline.

## Deliberate residual finding: whole-ledger rollback

The `test_known_limit_restoring_preconsume_snapshot_allows_replay` test backs up the SQLite file while a challenge is pending, consumes it, restores the earlier snapshot, and verifies that the same signed reports can be accepted again. This happens because the old row and its HMAC are both valid under the same key. Row authentication detects local edits but cannot prove recency after the whole store is rolled back.

This test must not be described as a defence passing. It is a counterexample intentionally retained in the green test suite so the limitation stays visible.

## Required production control

Move nonce consumption into an independently administered, non-rollbackable store that provides atomic create/consume or compare-and-swap keyed by nonce. It should have different credential administration and backup/restore controls from the verifier host. Bind the stored policy fingerprint and expiry there. Protect its recovery procedure against old snapshots; test real failover/restore. If that invariant cannot be supplied, the system must describe freshness as process-local/best-effort and must not claim cross-restore replay resistance.

## Out of scope / not demonstrated

- No real independent witness operators/hosts/cloud accounts were provisioned.
- No production monotonic CAS or remote nonce registry exists in this pack.
- SQLite `synchronous=FULL` and transaction semantics protect local transaction durability under SQLite's documented assumptions, not against privileged snapshot restore or lying storage/hardware. See https://www.sqlite.org/pragma.html and https://www.sqlite.org/wal.html.
- The protocol is not RFC 9162 compliant and makes no claims about data truth or semantic safety. RFC 9162 separately discusses conflicting log views: https://www.rfc-editor.org/rfc/rfc9162.html#section-11.3.
- No upstream source modifications, hosted anchor APIs or real refund actions.
