# Upstream Integration Plan v2.0

## Stage A — adapter boundary

- Introduce an evidence-lease protocol interface alongside the current `EvidenceProvider`; do not replace existing contracts silently.
- Keep `EvidenceRequirement` configuration trusted and versioned. Document each dependency's `EXACT` or `SUBJECT_STATUS` semantics.
- Require the actual evidence system to provide lease/lock/conditional-write semantics. If it cannot, leave that dependency non-finalizable or route it to review/reconciliation.

## Stage B — provider contract

- Define `lookup(operation_id, request_digest)` and `execute(operation_id, request, lease)` semantics.
- Require durable retention of idempotency records beyond the maximum retry/recovery horizon.
- Require operation ID and payload digest binding; key reuse with a different payload must conflict.
- Ensure the remote provider validates the lease/condition at its business-effect commit point, not only before a long-running side effect.
- Keep provider-status lookup authoritative and authenticated; status lookup can only reconcile an existing effect, never authorize a new effect.
- Once the broker records `IN_FLIGHT`, do not unlock evidence automatically at token expiry. Define a provider-side fencing/status contract and an operational procedure for stuck `IN_FLIGHT` records; absent a proof of no-effect and no late request, retain the lock.

## Stage C — tests in a clean upstream branch

- Apply and review changes to `lycheetah/assurance/finality.py`, new lease adapter module, and `tests/test_assurance_finality.py`.
- Run current finality, runtime, receipt, MCP guard, execution cell, package installation and full CI suites.
- Add integration tests for `EXACT` and `SUBJECT_STATUS`, update-vs-lease concurrent threads, provider response loss, response lookup after evidence revocation, key mismatch, lease expiration, process kill/restart and two worker processes.
- Run with a fake provider first; use no real production customer actions during initial validation.

## Stage D — security review and operational readiness

- Threat-model lease key storage/rotation, trusted-host boundary, caller authorization, clock skew and maximum in-flight duration.
- Confirm every evidence mutation/revocation path honors leases or state a narrower guarantee.
- Validate provider-side idempotency atomicity and retention with an integration contract, not only an adapter flag.
- Define stuck `IN_FLIGHT`, expired unclaimed lease and uncertain provider outcomes as explicit reconciliation states. Expired but unclaimed `ACTIVE` leases may expire; started `IN_FLIGHT` operations require result confirmation or a fenced cancellation before unlock.

## Status and boundary

The local v2.0 reference and 49 local test methods pass. A separate 200-round SQLite race experiment reports zero invariant violations. This is not an upstream integration test: the source tree uses the v1.9 research broker copied into this pack and a simulated provider that shares the lease authority's HMAC key. The actual upstream repository remains unchanged; connected GitHub branch creation previously returned HTTP 403. Do not promote until the real repository suite, provider contract and deployment threat review pass.
