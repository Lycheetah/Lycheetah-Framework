# Changelog v3.4 — Durable Freshness Challenge Lifecycle

- Added `DurableFreshnessVerifier`, which persists nonce issuance and binds each challenge to a database ID and a frozen verification-policy fingerprint.
- The policy fingerprint covers protocol version, anchor key IDs/public-key bytes, witness IDs/public-key bytes, Byzantine fault budget, freshness report clock-skew limit, and challenge TTL. A pending challenge is rejected if this policy configuration changes.
- HMAC-authenticated each persisted challenge row, including pending/consumed state and consumption time.
- Made successful challenge use atomic with a conditional SQLite transaction after full signed-chain and fresh-head verification; concurrent calls permit one successful consume.
- Added explicit schema-shape rejection for incompatible pre-existing tables.
- Added lifecycle tests for restart persistence, same-challenge replay, 8-way concurrent verification, wrong database envelope, forged nonce, expiry before and after chain verification, invalid reports, wrong HMAC key, direct row tampering, policy/roster change, collision retries, and incompatible schema.
- Added a rollback negative control: restoring a valid pre-consumption SQLite snapshot under the same integrity key permits replay. This is retained as evidence that the reference ledger is not anti-rollback.
- Corrected a malformed module docstring in the copied v3.3 baseline-reproduction harness and re-executed all five frozen v3.2 acceptance reproductions.
- 56 tests passed in the combined v3.3 + v3.4 test invocation; includes one intentional expected-acceptance negative control that documents the snapshot-rollback limitation.
- No upstream branch, pull request, hosted API call, or production source modification.
