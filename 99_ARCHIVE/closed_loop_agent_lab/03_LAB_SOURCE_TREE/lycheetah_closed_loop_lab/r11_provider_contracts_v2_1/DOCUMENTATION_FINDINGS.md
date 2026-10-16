# Documentation findings for provider contracts

**Research date:** 2026-10-17. This is a desk review of official vendor documentation, not live API conformance evidence.

## Stripe

Official source: https://docs.stripe.com/api/idempotent_requests

Stripe documents that it stores a first status code/body for an idempotency key, compares later parameters, and can prune keys once they are at least 24 hours old. The response replay includes errors such as `500`. Validation failures that do not enter endpoint execution, and conflicting concurrent requests that do not initiate execution, are not stored as ordinary endpoint results.

**Implication:** configure an explicitly conservative recovery horizon and never assume a key lasts indefinitely. A still-pending local outbox entry can outlive the provider's key. After the safe window, use authoritative resource lookup or `RECONCILE`; do not blindly resend.

## Amazon EC2

Official source: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html

EC2 documents client tokens for supported API actions, same token/same parameters retry behavior, parameter mismatch errors for differing parameters, and regional versus zonal idempotency depending on the action and request parameters.

**Implication:** key identity must include the provider-documented scope (for example, account, action, region or Availability Zone where relevant). “AWS supports idempotency” is not a sufficiently specific adapter contract.

## Amazon ECS `RunTask`

Official source: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html

ECS documents a 24-hour TTL for `RunTask` client tokens and cluster-scoped idempotency.

**Implication:** a broker recovery schedule that extends beyond that TTL cannot assume provider-side deduplication remains valid. If it cannot authoritatively resolve the operation, it must reconcile rather than retry.

## What these sources do not prove

The idempotency documentation describes repeated-request semantics. It does not, by itself, establish that a condition owned by Lycheetah or another external system is atomically checked at the commit point of a remote side effect. A provider can give strong retry deduplication while still leaving the separate authorization time-of-check/time-of-use race unresolved.
