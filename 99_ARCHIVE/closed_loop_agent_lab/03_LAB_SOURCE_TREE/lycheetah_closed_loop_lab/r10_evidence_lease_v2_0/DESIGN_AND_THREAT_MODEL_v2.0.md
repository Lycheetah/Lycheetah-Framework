# Evidence Lease Protocol — Design and Threat Model v2.0

## Threat

The v1.9 reference broker reads an evidence snapshot and then calls an effect provider. A separate evidence writer can update or revoke that evidence in the interval between read and effect. Rechecking immediately before the call narrows but does not eliminate this distributed TOCTOU race.

## Proposed protocol

1. The caller supplies a previously issued, authenticated admission witness and exact action.
2. The broker persists authorization and action intent in its local transactional outbox.
3. Immediately before the effect, the adapter requests a lease from the authoritative evidence writer.
4. Within one SQLite `BEGIN IMMEDIATE` transaction, the authority compares current evidence with trusted requirements and (for `EXACT`) admitted evidence, inserts a lease bound to operation ID/action digest/requirements, and attaches all required evidence keys.
5. Before the first provider call, the broker claims the lease as `IN_FLIGHT`. While a lease is `ACTIVE` and unexpired, or in `IN_FLIGHT` regardless of TTL, `put()` refuses to change any protected key. Competing acquisition and evidence writes serialize through SQLite transactions, so one linearizes first. TTL expiry retires an unclaimed lease, but never automatically unlocks an operation that may already be executing.
6. The effect provider verifies lease HMAC, operation ID, action digest and expiry inside its transaction. The token must still be valid when a new provider attempt begins. If it expires between claim and provider validation, a same-operation retry can renew the pinned lease. Once the attempt has entered the provider's effect path, the evidence remains locked until the operation result is resolved. The simulated business effect and idempotency record are inserted atomically in the provider database transaction.
7. On confirmed success, the lease is released. On ambiguous response loss, it remains `IN_FLIGHT` past TTL until retry reconciles the provider's durable idempotency record or an authorized reconciliation path resolves the operation.
8. Before current policy/evidence checks, the broker may read the provider's authoritative idempotency status. A valid committed result only moves the local outbox to `DONE`; it does not authorize a new action. This supports recovery when the original effect committed but its token expired. Evidence remains pinned until this result is confirmed.

## Requirement modes

- `EXACT`: every current evidence record field must equal the record captured at admission (key, version, subject hash, value digest and status).
- `SUBJECT_STATUS`: only the key, required status and configured subject hash must still satisfy the trusted predicate. A new version/value digest can remain acceptable by design. Use this only if the policy intentionally regards a newer passing record for the same subject as equivalent.

A caller cannot supply or downgrade the requirements at dispatch: requirements come from the adapter/broker configuration and the authenticated admission token is checked against its requirement digest.

## Key assumptions

- The authority that issues the lease is the authoritative source for leased evidence and all evidence writes enforce its lock table.
- The HMAC key remains private to trusted components.
- The mock provider checks the lease and commits the mock business effect plus idempotency result inside its own single database transaction.
- The provider's durable lookup API is authenticated and returns a trustworthy operation ID and request digest.
- Clocks are coherent in the local simulation. A real deployment must design for clock skew and enough lease budget, or use a provider-native conditional commit that validates the evidence version at commit.
- The broker/adapter is trusted to claim `IN_FLIGHT` before calling the provider and to release only after authoritative result/reconciliation.
- An abandoned `IN_FLIGHT` lease may remain locked indefinitely; automated release requires a provider status/fencing contract that rules out a late effect.

## What this does not prove

- It does not make independent remote services share one distributed transaction.
- It does not protect evidence changed through a bypass path outside the lease authority.
- It does not guarantee that an arbitrary API honors idempotency keys, preserves them for the retry horizon, or commits them atomically with its business effect.
- It does not establish identity or human authority for the underlying admission witness beyond the separate v1.9 lab model.
- It does not prove security on multiple hosts, clock domains, network partitions, or production databases.
- It does not integrate with the actual upstream Lycheetah `FinalityGate` yet.

## Residual safe behavior

If acquisition fails, the evidence predicate changes, a token is invalid/expired before execution begins, or the adapter cannot establish the expected provider contract, no fresh effect is issued and the local operation enters `RECONCILE`. If an effect might already have committed, do not create a new operation ID: reconcile/retry with the same idempotency key. Do not auto-unlock `IN_FLIGHT` evidence solely because TTL expired: an old provider call might still commit. If authoritative reconciliation cannot prove the operation complete or safely fence a no-effect outcome, retain the lock and escalate to an operator.
