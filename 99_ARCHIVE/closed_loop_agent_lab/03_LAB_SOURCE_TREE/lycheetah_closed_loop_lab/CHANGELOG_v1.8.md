# Changelog — v1.8

## Trusted admission witness prototype

- Took the v1.7 source-equivalent witness provenance finding into a standalone defensive prototype.
- Added HMAC-authenticated witness bodies and an issuance registry backed by SQLite.
- Moved evidence requirement selection into trusted gate configuration.
- Added exact action/policy binding, expiry, malformed-token rejection and durable one-use consumption.
- Added 16 local unittest methods, including 25 concurrent two-caller finalization races; exactly one use succeeds per trial.
- Included an intentional external evidence provider TOCTOU demonstration, documenting that a local witness transaction cannot atomically lock a separate provider or remote effect.
- Repeated the v1.7 source-equivalent baseline probe: altered witness with a recomputed public digest is accepted by the source-equivalent mirror, while the hardened prototype rejects the same class of public-hash substitution.

## Limits retained

- Standalone prototype uses `ToyRuntime`; it is not connected to the real AssuranceRuntime or FinalityGate.
- No repository branch or PR was created and no upstream code was changed.
- No full upstream tests or CI were run.
- Not production ready; effect dispatch, remote idempotency, provider-side versioned leases/transactions, key rotation and multi-host deployment need a real integration.
