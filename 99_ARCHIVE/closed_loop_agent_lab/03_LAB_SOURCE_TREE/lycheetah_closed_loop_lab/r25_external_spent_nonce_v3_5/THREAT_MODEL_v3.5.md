# Threat Model v3.5 — External Spent-Nonce Registry

## Security property under test

For a challenge registered in a separate, current registry trust domain, a successful freshness decision may consume that challenge at most once—even if an attacker restores the primary verifier's local SQLite ledger to a coherent snapshot taken before consumption.

## Added protections

- Remote create-only registration of nonce + database ID + issue/expiry time + exact policy fingerprint.
- Server-enforced nonce binding and expiry at consumption time.
- Atomic `PENDING -> CONSUMED` under registry database write transaction.
- Client HMAC authentication, timestamp window, durable request-ID anti-replay, signed responses and pinned server key.
- Client validates exact response envelope, status, request ID, nonce, database ID, policy fingerprint, and consumed time.
- Local chain/quorum validation precedes remote consumption. Remote consumption precedes local consumption; after a lost response, an unknown outcome stays fail-closed.

## Tests and counterexamples

- Cross-store snapshot test: restore the pre-consumption primary-ledger snapshot while leaving the registry current; reuse is rejected as already consumed.
- Concurrent requests: eight simultaneous consumers of one nonce yield exactly one accepted result.
- Response lost after remote commit: local row remains pending, but a second use is rejected by the registry.
- Remote service down: verification fails closed and local state is not falsely marked consumed.
- Invalid witness reports do not consume a valid registry nonce.
- Service response tampering, wrong client key, direct registry-row edits, stale expiry, altered challenge policy and disallowed HTTP endpoints fail closed.
- A deliberate negative control restores both primary and registry snapshots. The same challenge becomes reusable because both state stores and their matching keys remain restorable. This is not a passed defence; it documents the remaining trust assumption.

## Out of scope

The remote service and both databases are still run on the same test host in these tests. No multi-cloud administrative boundary, protected hardware monotonic counter, independent cloud account, managed append-only service, or real deployment recovery process is provisioned. Therefore the tests establish cross-store rollback detection under a stated assumption, not universal anti-rollback security.

The HTTP example does not include production TLS termination, authorization operations, service hardening, key management, request rate limiting, deployment monitoring, disaster recovery, or high availability. Deploying it as-is would be unsafe.
