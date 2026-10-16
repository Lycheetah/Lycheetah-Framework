# Runbook: Stuck `IN_FLIGHT` Action

## Safety rule

**Never clear an `IN_FLIGHT` evidence lease solely because its token TTL expired or its worker disappeared.** The provider may have accepted the request and can still commit or return a result late. The lease remains pinned to prevent evidence revocation from racing a late effect.

## Resolution sequence

1. Identify the exact `operation_id`, canonical action digest, witness ID, evidence keys and policy digest. Preserve logs and the outbox row; do not generate a new operation ID for a retry.
2. Query the authenticated effect provider's durable idempotency/status endpoint using that same operation ID and action digest.
3. If the provider reports a committed result, verify the provider result's operation ID and request digest, persist the local outbox as `DONE`, then release the lease. The status query must not create a new effect.
4. If the provider reports no result, do not infer that the action never happened unless its contract also guarantees no in-flight/late operation remains and fences any later request for that operation ID. With such a contract, record the authoritative no-effect/fenced outcome, route the action to reconciliation, and release only via the reviewed recovery path.
5. If the provider cannot authoritatively distinguish `COMMITTED`, `NOT_COMMITTED_AND_FENCED`, and `UNKNOWN`, leave the lease pinned and route to a human operator for provider-specific reconciliation. Depending on the business operation, investigate and reconcile or compensate before authorizing any new attempt.
6. Record the final outcome, source of evidence, operator/automation identity, provider request key and any compensation in the audit log.

## Why the fallback is intentionally strict

The SQLite prototype can keep its own evidence updates and lease state consistent, but it cannot invent a distributed transaction with a third-party provider. If the provider lacks durable idempotency and authoritative status/fencing, automatic unlock or a new action ID could cause a duplicate or stale effect. The safe response is operational reconciliation, not a fabricated guarantee.
