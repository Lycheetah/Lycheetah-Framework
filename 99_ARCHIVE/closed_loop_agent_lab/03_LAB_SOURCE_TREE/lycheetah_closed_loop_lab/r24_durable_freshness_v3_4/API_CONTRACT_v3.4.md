# API Contract v3.4 — Durable Freshness Challenges

## Construction

```python
verifier = DurableFreshnessVerifier(
    ledger_path,
    anchor_keys,
    witness_keys,
    integrity_key=secret_from_protected_key_storage,
    max_byzantine=1,
    max_clock_skew_seconds=60,
    challenge_ttl_seconds=120,
)
challenge = verifier.issue(database_id)
```

The integrity key must be at least 32 bytes. Anchor and witness registries are validated on construction and copied into the verifier. Do not load them from a verification request. The challenge policy fingerprint includes the current protocol version, raw Ed25519 public-key bytes and IDs, fault budget, clock-skew window and TTL.

The caller sends `challenge.nonce` to configured witnesses and gathers signed `fresh-head` reports. Then:

```python
heads = verifier.verify_and_consume(certificates, reports, challenge)
```

The method reads the authoritative ledger row; the `issued_at_ms` and `expires_at_ms` values in a caller-created/reconstructed envelope are display metadata, not trusted proof. It verifies the complete certificate chain and raw nonce-bound reports using v3.3 functions, then consumes the persisted challenge within a conditional write transaction. Only one competing successful call can consume a challenge. Failed report verification leaves it pending until expiry to allow collection/retry of correct reports.

## Error semantics

- `challenge-not-issued-by-this-verifier`: nonce absent from this ledger.
- `challenge-already-consumed`: nonce was successfully used previously.
- `challenge-expired`: TTL passed at initial check or before atomic consumption.
- `challenge-database-mismatch`: challenge envelope/ledger are for another database.
- `challenge-policy-changed`: protocol, trusted key roster, fault budget, clock-skew window, or TTL differs from issue-time policy.
- `challenge-ledger-integrity-invalid`: stored row doesn't authenticate under the configured integrity key.
- `challenge-ledger-schema-incompatible`: local table's column contract differs from this version.

Underlying signed-chain/quorum failures raise `WitnessProtocolError` from the retained verifier; they do not consume a challenge.

## One-time use and crash behavior

Consumption is durable before the method returns. If the process crashes after commit but before the caller receives the return value, the same nonce is not accepted again; the caller must request a new challenge. This is a safe-availability tradeoff, not an idempotent response cache.

## Trust assumptions and non-guarantees

- The HMAC key remains protected and consistent across verifier restarts.
- The local SQLite file and backups are not rollback-protected. Restoring a pre-consumption snapshot also restores the pending state and re-enables replay. A production implementation MUST use a separately administered non-rollbackable spent-challenge/high-water store or remote monotonic CAS.
- Wall-clock accuracy is required for expiry and signed-report timestamp checking; a backwards clock adjustment can affect expiry semantics. Production expiry should rely on a trusted clock/service and monotonic stored state.
- Different public keys do not guarantee independent administrators, hosts or control domains.
- This protocol is an experimental Lycheetah design, not a certified consensus algorithm or RFC 9162 implementation.
