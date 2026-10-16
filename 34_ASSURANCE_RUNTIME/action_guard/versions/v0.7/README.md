# Lycheetah Action Guard v0.7 — independently anchored audit chain

**Status:** research prototype; locally tested, not deployed. **No live GitHub calls are made.**

## Why v0.7 exists

v0.6 persisted approvals and effect states, but its audit table was ordinary mutable data. A database writer could edit an event without a built-in integrity alarm. v0.7 adds a hash-chained audit journal and makes a previously captured audit checkpoint a required precondition for a dispatch claim.

The important addition is not “hashes make the database immutable.” They do not. It is the combination of:

1. Canonical event hashing with each event committing to the previous hash.
2. Whole-chain verification for changed events and gaps.
3. A trusted checkpoint (`event_count`, `last_seq`, `root_hash`) supplied by the caller and retained **outside the database's trust boundary**.
4. Dispatch denial if the checkpoint is missing, or if the current journal no longer contains the same verified prefix.

A saved checkpoint validates a prefix, so legitimate later events do not make it stale. A deleted or rewritten row inside that prefix fails validation. A checkpoint retrieved from the same database *after* suspected tampering is not independent evidence; the production system must preserve checkpoints as they are emitted, e.g. in a separate audit service or immutable store. A writer who can change the database and recompute the chain can fool internal hash validation, but cannot match a previously saved external root without also compromising the external checkpoint.

## Included controls

- SQLite-backed authority epochs, exact-action approvals, effect intents and result state.
- Single-use approval and effect intent, canonical SHA-256 action digest, scope/expiry checks, and distinct approver/executor identity fields.
- `PREPARED → DISPATCHING → SUCCEEDED | FAILED | UNKNOWN`, with pre-dispatch cancellation and no automatic redispatch from `UNKNOWN`.
- Hash-linked audit events, migration of v0.6 audit rows, chain verification and an external checkpoint API.
- **Mandatory external checkpoint at the dispatch boundary** (`claim_dispatch(..., expected_audit_anchor=...)`). Omitting it is denied.
- Synthetic pull-request merge provider with conditional head/base checks and idempotency behavior. This fake provider is a fixture, not evidence of real GitHub semantics.

## Run

Requires Python 3.10+ and only the standard library.

```bash
python3 -m unittest -v test_action_guard_v07.py
python3 run_verification.py
python3 run_synthetic_scenario.py
```

## External checkpoint contract

After preparing an effect, the execution service obtains the checkpoint and writes it to a different trust domain before dispatch:

```python
anchor = guard.audit_anchor()
# REQUIRED IN A REAL SYSTEM: persist `anchor` independently, before dispatch.
claim = guard.claim_dispatch(
    effect_id,
    now,
    trusted_current_action,
    expected_audit_anchor=anchor,
)
```

The code sample illustrates the API, not a secure deployment by itself: in a real deployment the checkpoint returned by `audit_anchor()` must be stored independently and reliably, and later loaded from that trusted store. Calling `audit_anchor()` again from a potentially compromised database does not establish trust. The local test fixture uses an in-memory Python value to simulate the external store.

## Benchmark results

The deterministic verification runner uses no network or provider call:

- 1,000 one-field action mutations across repository, pull request, head SHA, base SHA and merge method: the guarded path accepted **0/1,000**; a deliberately weak tool-only baseline accepted **1,000/1,000**.
- 100 exact-action positive controls: **100/100** accepted.
- 25 concurrency rounds × 8 simultaneous attempts: one winner per round (**25 allowed, 175 denied, zero harness errors**).
- The benchmark's 2,250-event generated audit journal verified cleanly.
- Unit tests include event editing, missing checkpoint, tail truncation, middle deletion, full-chain recomputation by an attacker, v0.6 migration, restart persistence, revocation, uncertain outcome and concurrent use.

These are controlled tests authored with the prototype. The tool-only baseline is deliberately weak, not a mature ACL comparator; results are not an independent security review and do not imply production safety.

## Critical limitations

- No real GitHub API, credential, webhook, repository, or remote effect was touched.
- `approver_id` is data, not authenticated proof of a human's identity. Production requires authenticated approval UI/session and a protected event.
- The external checkpoint is a caller integration requirement; this package does not implement a remote immutable checkpoint service.
- A local database transaction cannot be atomic with a remote API request. Revocation cannot guarantee cancellation after an effect crosses `DISPATCHING`.
- A timeout after transmission remains `UNKNOWN` until reconciled with authoritative provider state. Do not blindly retry.
- Conditional provider enforcement remains essential. GitHub's REST merge endpoint accepts the expected pull-request head `sha` and returns HTTP 409 when the supplied head does not match, but a local pre-read alone cannot close the read/write race.
- v0.6 audit rows are re-hashed during migration. This creates a new integrity baseline; it cannot retroactively prove that legacy rows were untampered before migration.
- No independent audit, formal verification, red-team engagement, multi-host test or production deployment has occurred.
