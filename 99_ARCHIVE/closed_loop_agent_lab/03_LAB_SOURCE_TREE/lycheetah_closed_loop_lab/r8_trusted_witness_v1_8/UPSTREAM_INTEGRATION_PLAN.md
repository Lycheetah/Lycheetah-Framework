# Upstream Integration Plan — Admission Witness v1

## Recommended implementation boundary

Do not paste the standalone prototype directly into `finality.py`. Integrate the contract with the real runtime and trusted host in a non-default branch.

### 1. Move requirements into trusted configuration

- Add a policy-owned dependency/evidence requirement set or a trusted requirement resolver.
- Only trusted orchestration code should choose requirement identifiers/modes/subjects.
- The witness must record the digest of the resolved requirement set and its schema version.
- Finalization must compare the recorded requirement digest and actual structured requirements with the current trusted resolver result.

### 2. Authenticate issuance

- Prefer a server-side, opaque witness ID and durable registry. Persist the exact issued witness/body digest, event digest, policy digest, admission receipt digest, requirement digest, expiry and state.
- If witnesses must be portable between processes, add HMAC authentication with a protected key ID, rotation strategy and strict schema validation.
- Never treat the public SHA-256 digest as issuer authentication.
- During admission, verify the real runtime receipt and confirm it is an ALLOW for the same event and current policy before recording issuance.

### 3. One-use, concurrent-safe finalization

- Use a durable transactional store with conditional state transition `ISSUED -> CONSUMED`.
- Serialize competing finalization attempts or use a compare-and-swap/unique update so exactly one can succeed.
- Fail closed on store failure, malformed records, expired witnesses, policy changes, event substitution or required-evidence drift.
- Add process-restart, multi-worker and simultaneous-finalizer regression tests.

### 4. Resolve the evidence TOCTOU explicitly

The local witness ledger cannot make a separate CI, policy or approval provider immutable. Options:

- version/ETag-bound reads and conditional consume;
- short-lived signed evidence leases from the provider;
- one provider-owned transaction encompassing evidence validation and reservation; or
- acceptance of a documented bounded staleness window, if the threat model permits it.

State explicitly which option is used. A second read alone narrows but does not eliminate the race.

### 5. Couple authorization to the effect lifecycle

- Bind the final authorization to an idempotency key and exact tool payload.
- Persist an intent before dispatch; use a transactional outbox where applicable.
- Use downstream provider idempotency keys if offered.
- Reconcile outcomes after timeout/crash; don't claim exactly-once execution from an authorization witness alone.
- Keep `FinalityGate` separate from the effect broker so each boundary has testable responsibilities.

## Required regression gates

1. Honest valid witness accepted.
2. Forged witness with recomputed public digest rejected.
3. Requirement substitution rejected.
4. Fake admission receipt reference rejected by trusted registry relationship.
5. Action/payload substitution rejected.
6. Policy/version change rejected.
7. Stale, missing, wrong-subject and failed evidence rejected.
8. Expired and previously consumed witnesses rejected.
9. Two concurrent finalizers yield exactly one successful consume.
10. Registry failure is fail-closed.
11. Restart/multi-process persistence behaves as specified.
12. Evidence-provider update race has an explicit test for the chosen consistency protocol.
13. Test effect-broker idempotency and crash/recovery separately from the gate.
14. Run all receipt, model, schema, finality, runtime, execution-cell, MCP integration and package/wheel tests.

## Rollout / compatibility

Treat this as a new witness protocol version. Do not silently reinterpret old unsigned witnesses as authenticated. Either reject old persisted witnesses with a clear migration error, or permit them only under an explicitly named legacy path that is unavailable at production side-effect boundaries. Keep rollback and key rotation instructions separate from source changes.

## External engineering references

- [SQLite transaction control](https://www.sqlite.org/lang_transaction.html) documents that SQLite allows only one simultaneous write transaction and that `BEGIN IMMEDIATE` acquires the write transaction up front. The 25-race local test checks the specific one-use consume pattern used by this prototype; it is not a claim about all database topologies.
- [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) explains why retries around side effects need idempotency tokens and an atomic server-side relationship between the token and the mutation.
- [Microsoft Azure Architecture Center: Transactional Outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos) describes persisting business state and an outgoing event together in one supported local transaction, then relaying the event; delivery can still be at-least-once, so consumers need idempotency.

These patterns support the design direction; they do not validate the Lycheetah prototype or prove its security. The evidence-provider consistency contract and external action broker still need system-specific implementation and tests.
