# Durable Action Outbox — Design and Threat Model (v1.9)

## Main finding

The v1.8 trusted witness prototype consumed a single-use authorization during `finalize()`. If the process died after that transaction but before durably recording the action to execute, the authorization had been spent while no durable action intent existed. Reversing the order is not enough: executing remotely first and then marking the local witness consumed permits a duplicate if the remote effect commits and the acknowledgement is lost.

v1.9 combines local authorization consumption and outbox insertion in one SQLite transaction. A dispatcher reads the durable outbox and calls a cooperating effect provider using `operation_id` as its idempotency key.

## State transitions

Local outbox states:

- `PENDING`: authorized intent committed; no dispatch attempt has begun.
- `IN_FLIGHT`: dispatcher has started a call; remote outcome may be unknown.
- `DONE`: provider returned a result bound to the recorded request digest and local acknowledgement committed.
- `RECONCILE`: automatic safe progress is not supported, or persisted intent failed integrity checks.

The one-use witness registry and outbox insertion use one local transaction. If local commit fails, neither consumption nor the outbox row survives. If the client acknowledgement is lost after commit, the same authenticated witness identifies the pre-existing outbox item and returns its operation ID rather than enqueueing a second one—even after token expiry, for status-recovery only. An expired or stale-policy token cannot create a new outbox item, and dispatch routes the existing operation to reconciliation rather than acting under stale authorization.

## Remote idempotency contract

The reference provider stores the idempotency record and simulated business effect in the same provider-side database transaction. It must:

1. Persist a stable operation key before reporting success.
2. Bind that key to a canonical request digest.
3. Return the stored result for the same key and same request.
4. Reject the same key with a different request digest.
5. Retain key/result records at least as long as a delayed retry can arrive.

If a provider cannot make the deduplication record atomic with the actual business effect, the test provider's guarantees do not transfer. v1.9 refuses to dispatch to a provider that does not declare durable idempotency and moves the operation to `RECONCILE` instead of guessing.

## Fault model tested

- Crash before the local authorization/outbox transaction commits.
- Local commit succeeds but the caller loses the acknowledgement.
- A pending action is recovered after reconstructing the broker object.
- Remote effect and idempotency row commit but the response is lost.
- Worker dies after a remote response but before local `DONE` update.
- Two dispatcher threads race on one operation ID.
- Persisted action JSON is changed without updating its digest.
- Same remote operation ID is reused with a different payload.
- Unsupported non-idempotent provider.

## What is not guaranteed

- There is no general exactly-once transaction across a local database and arbitrary remote system.
- The external evidence provider can change after a passing snapshot is returned and before/after enqueue commit. The included test deliberately demonstrates this residual TOCTOU gap.
- SQLite and the mock provider are local test fixtures, not proof of multi-region, multi-host or real service behavior.
- The reference runtime receipt is synthetic and is not the production `AssuranceRuntime` receipt. The SQLite schema has no production migration or backup/restore protocol; use a fresh research database and design explicit migrations before integrating.
- The signing key and local database are assumed trusted. A deployment must define secret storage/rotation, database access controls, backups, retention, clock policy and audit access.
- A remote provider's idempotency retention window may expire; that must be incorporated in operation expiry and recovery policy.
- This pack does not execute actions or integrate directly into the upstream `FinalityGate`.

## Evidence and external context

The transactional outbox pattern explains why local intent must be committed before a relay sends it, while noting that relays can publish more than once and downstream consumers need idempotency: https://microservices.io/patterns/data/transactional-outbox

AWS Builders' Library describes how idempotent APIs make retry behavior safe and why a request token should preserve meaning across retries: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

SQLite transaction behavior and `BEGIN IMMEDIATE`: https://www.sqlite.org/lang_transaction.html

These sources motivate the standard engineering patterns; they do not validate this specific prototype.
