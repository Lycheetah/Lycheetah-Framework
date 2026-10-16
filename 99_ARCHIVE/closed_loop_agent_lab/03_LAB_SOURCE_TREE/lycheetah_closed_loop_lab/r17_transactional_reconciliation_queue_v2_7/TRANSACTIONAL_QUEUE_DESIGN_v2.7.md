# Transactional Reconciliation Queue — Design and Threat Model v2.7

## Trust boundary

The receiver verifies the signature against the exact raw request bytes, parses a bounded event shape, checks test-mode and configured platform/Connect account scope, and derives a minimal record. The record is authenticated with an HMAC key held outside the database.

A single SQLite transaction then:
1. checks whether the event ID already exists;
2. rejects the same ID with a different signed payload digest;
3. inserts the minimal inbox record;
4. inserts one minimal queue job (or a sticky manual-reconciliation job if no valid operation ID is present).

If either insert fails, the transaction rolls back both. The HTTP wrapper maps durable-write failures to `503`, allowing delivery retry; a duplicate accepted event receives `200` without creating a second job.

## Queue state machine

```text
PENDING --claim--> CLAIMED --trusted current-state record saved--> DONE
   ^                   | 
   |                   +-- transient read failure --> PENDING (delayed)
   |                   +-- explicit ambiguity --> MANUAL
   +------ expired lease / attempts below limit

CLAIMED --expired lease at max attempts--> MANUAL
PENDING --missing correlation / account mismatch--> MANUAL
```

`DONE` is a work-queue statement only. It does not mean the refund is successful. Current provider state and the operation ledger remain authoritative for business status.

## Concurrency properties tested

- Two concurrent ingesters for the same event ID produce one inbox row and one job.
- Two workers concurrently claiming one ready job produce one claim.
- Fifty repeated two-worker claim races produced one claim for each distinct event.
- Claim token plaintext is returned once and only its digest is stored.
- A wrong worker, wrong token, expired lease, consumed lease or mismatched account cannot acknowledge work.
- An expired lease can be reclaimed; an old token becomes invalid.
- Retry delays defer work; repeated failure reaches `MANUAL` at the maximum attempt count.
- Queue-row tampering is detected before read/claim.
- An inbox insert failure or queue insert failure rolls back the paired write.

## Migration

On initialization, v2.7 creates the additive queue table and backfills missing jobs for legacy inbox rows. Each legacy inbox row must pass its existing HMAC check before a job is generated. The migration uses the original `received_at` timestamp for queue age. Existing job states are not overwritten. If a legacy row cannot be authenticated or parsed, initialization fails closed and asks for explicit migration/recovery.

This migration does not reconstruct historical worker progress that was never represented in the old inbox. It intentionally creates pending reconciliation work for correlated accepted events and manual work for uncorrelated events. Operators must review large backfills before using this on production data.

## Assumptions and limits

- SQLite is a single durable authority for inbox + queue on one host/filesystem. Multi-host use requires a shared transactional database or a formally equivalent queue store.
- Workers authenticate with their own secure runtime channel. This reference validates worker identifiers and one-use claim capabilities, but does not establish an enterprise identity system.
- A worker must perform current-provider retrieval and durable operation-ledger update idempotently before calling `finish_reconciliation_job(..., disposition="RECONCILED")`.
- A crash after operation-ledger update but before queue acknowledgement causes repeated read/reconcile work; that is intended to be safe.
- HMAC authenticates rows but does not encrypt them, and cannot by itself detect deletion/rollback of the entire database. A production design may require backup integrity, append-only external checkpoints or monotonic counters.
- The queue is for reconciliation reads. It must never use a webhook's `refund_status` to generate a financial side effect or mark the business operation successful.
- Signature verification and the loopback server are reference-only. Use Stripe's official SDK verifier and a production HTTP framework in a deployment.
