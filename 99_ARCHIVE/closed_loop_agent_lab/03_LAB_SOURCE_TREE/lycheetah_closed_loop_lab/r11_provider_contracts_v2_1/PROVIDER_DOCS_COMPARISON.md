# Public provider semantics reviewed for v2.1

Research date: 2026-10-17. These are documentation findings, not live API test results.

## Stripe idempotent requests

Official documentation: https://docs.stripe.com/api/idempotent_requests

Stripe documents storing the first status code and response body for an idempotency key, replaying subsequent requests with the same key, and comparing request parameters. It also states keys can be removed once they are at least 24 hours old; after pruning, reusing a key can create a new request. Results are saved after endpoint execution begins; parameter-validation failures and concurrent conflicts that do not initiate execution are not saved as normal idempotent results.

**Implication for Lycheetah:** the recovery horizon cannot be inferred from “Stripe supports idempotency.” Persist provider and endpoint-specific rules; do not blindly retry an unresolved operation beyond the documented key retention envelope. If the state is ambiguous, use an authoritative resource lookup or reconcile.

## Amazon EC2 client-token idempotency

Official documentation: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html

AWS EC2 documents per-action client-token support, same-token/same-parameters retry behavior, and `IdempotentParameterMismatch` when parameters differ. Scope can be regional or zonal depending on the operation and request parameters; it is not safe to assume every token is globally unique across all regions/zones in the same way.

**Implication for Lycheetah:** canonicalize the exact endpoint/action, account, region/zone, and payload into the adapter's operation identity. Verify the scope for the precise operation rather than describing AWS as having one universal idempotency contract.

## Amazon ECS RunTask as a concrete TTL example

Official documentation: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html

AWS ECS documents `RunTask` client-token idempotency, a 24-hour TTL, and a conflict when the same token is reused with different parameters. The scope is cluster-specific.

**Implication for Lycheetah:** provider TTLs are hard constraints. A persisted local outbox may live longer than the provider's dedupe key; after TTL expiry, a blind retry can create a second operation. The safe state is `RECONCILE` unless a reliable lookup proves whether the original operation exists.

## Key distinction

These documented idempotency semantics primarily handle repeated requests. They do not by themselves prove that a separate evidence predicate is checked atomically at the moment a side effect commits. For Lycheetah, treat these as two independent axes:

1. **Retry/effect deduplication:** same logical request does not apply the effect twice within the provider's key scope and retention window.
2. **Authorization freshness:** required evidence/policy predicate is enforced at the effect's linearization point, or the provider has an equivalent explicit reservation/version condition.

A provider can satisfy (1) while failing (2). That is the main finding of the v2.1 two-provider comparison.
