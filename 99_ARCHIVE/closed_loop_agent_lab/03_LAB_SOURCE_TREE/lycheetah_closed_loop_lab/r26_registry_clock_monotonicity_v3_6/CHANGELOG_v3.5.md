# Changelog v3.5 — External Spent-Nonce Registry

- Added a client-authenticated HTTP registry for challenge registration and atomic one-use consumption.
- Added request timestamp/id anti-replay, pinned Ed25519 response signatures, bounded bodies, redirect refusal, strict challenge binding and a separate registry-side row HMAC.
- Composed remote spent-nonce consumption with the retained local signed-chain/quorum verifier. Remote consumption occurs before local consumption so a lost response or crash is fail-closed.
- Added a snapshot test proving a pre-consumption primary-ledger restore is rejected while the remote registry remains current.
- Added a deliberate negative control proving coordinated rollback of both databases still permits replay; the registry itself needs independent anti-rollback operations.
- Added 15 registry integration tests. Combined retained suite: 71 passing test methods in one invocation; five v3.2 baseline counterexamples reproduced.
- No hosted services, real refunds, upstream source changes or upstream CI claims.
