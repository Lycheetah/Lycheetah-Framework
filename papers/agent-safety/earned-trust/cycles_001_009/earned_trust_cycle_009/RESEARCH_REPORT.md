# Earned Trust Research — Cycle 009

## The Enforced Boundary: from veto to access control

**Study date:** 18 October 2026 · **Status:** synthetic engineering validation only · **Repository writes:** none

### Question

The previous eight cycles tested authorization predicates, stale evidence, governance challenges, audit records, and crash recovery. But an agent can simply call the provider directly if it already possesses usable credentials. This cycle asks whether an untrusted subprocess can reach an effect provider *without* crossing the trusted broker.

### Implemented controls

A root-owned test process hosts (a) a Unix-domain gateway using Linux `SO_PEERCRED` to derive client UID, (b) the existing C008 SQLite approval/dispatch authority, and (c) an HTTP loopback provider requiring HMAC-protected, short-lived capabilities. The agent runs as a real subprocess with UID 65534. The provider also enforces tool `refund.create`, positive integer amount bounded at 100000 cents, action hash, keyed issuer identity, expiry, and one effect per `effect_id` in SQLite. The gateway does not disclose its signing key or capability to the agent.

This creates a real OS-permission test and a real HTTP endpoint, but *does not* separate the trusted gateway and provider into different privilege domains.

### Exact measured observations

- New unit/integration lab: **47/47** Python tests pass with ResourceWarnings treated as errors.
- C008 regression: **46/46** pass in this turn.
- 32 concurrent HTTP attempts with the same correctly signed capability: **one HTTP 201 new effect, thirty-one HTTP 200 idempotent replays**, provider row count one.
- Unprivileged subprocess: local private key file read raises `PermissionError`; direct HTTP POST with unsigned capability returns **401**; authorized Unix gateway request commits one synthetic effect.
- Unauthorized effect ID, changed action, open source challenge, and revoked approval all fail through the agent-facing gateway.
- Independent conventional comparison scoped to the provider's HMAC/expiry/idempotency rules: **15 of 15 authored cases produce the same decision**. The standard baseline is not weaker and this result is not a Lycheetah-specific advantage.

### Counterexamples that must remain visible

| Tested condition | Observed | Interpretation |
|---|---|---|
| Attacker knows trusted gateway signing key | Forged token commits an effect not in authority ledger | Gateway signing key is a critical bearer authority |
| Attacker steals a valid unused capability | Exact action commits once | Bearer capability theft can change *who* triggers the effect; idempotency limits repetitions only |
| Governance challenge after successful dispatch reservation | Provider still commits | The reservation/remote execution seam is not atomic with later local governance updates |
| Trusted eligibility says PASS while scenario's independent truth says false | Provider commits | Signed policy compliance does not verify worldly truth |
| Signer key disabled before delivery | HTTP 401 | Key withdrawal can stop even a previously signed in-flight capability (with availability costs) |
| Provider response lost after commit | Gateway returns UNKNOWN; C008 recover/reconcile via signed receipt | Unknown must not silently become failure or an unsafe retry |

### Observed limitations

The local signer is not attested by a hardware trust root. The lab uses symmetric HMAC, meaning any party with the shared key can forge dispatch capabilities. The provider does not independently attest an actual C008 `SEND_RESERVED` row; it trusts the issuer. The OS/root separation test proves only that uid 65534 could not read a chmod-0600 file inside a root-only directory under the test environment. Host root, network-level interception, endpoint compromise, malicious gateway code, identity enrollment, credential provisioning and real provider behavior remain outside scope. The provider's localhost HTTP channel does not use TLS. This is not a production-ready security system.

### Real framework dependency

The canonical code is [`Lycheetah/Lycheetah-Framework`](https://github.com/Lycheetah/Lycheetah-Framework), whose `master` was inspected earlier at `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`. That commit includes `AssuranceRuntime`, `FinalityGate`, and `PersistentActionGuard`. The native bridge currently raises `ModuleNotFoundError: No module named 'lycheetah'`. No claim is made that C009 executes those classes. The C007 and C008 synthetic authority modules are preserved unchanged, including fixtures and their toy keys.

### Novelty and conventional comparison

Signatures, Unix peer credentials, least privilege, conditional acceptance, idempotency, SQLite transaction serialization and sidecar gateways are well-established approaches. Fifteen matched synthetic provider scenarios produced 100% decision agreement with an independent conventional implementation. The next scientific task is an authenticated original source checkout, threat-model-driven end-to-end integration test, and independent red-team tests involving malicious processes at equivalent privilege levels.

### Cycle 010 research target

**The credential boundary itself:** make the gateway and provider separate constrained services, replace shared HMAC issuer credentials with a verifiable asymmetric capability signer, implement challenge-aware expiry or explicit provider-side epoch checks, and test lost/compromised credentials under process restart. Preserve a matched, equally capable baseline and avoid claiming revocation of already committed external effects.
