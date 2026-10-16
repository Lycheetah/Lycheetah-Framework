# Witness Provenance Audit v1.8

## Executive finding

The inspected source at commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65` computes an `AdmissionWitness` SHA-256 digest over its body. SHA-256 detects body changes only if the expected digest is obtained from a trusted source; it does not authenticate the issuer because anyone who can reconstruct the witness body can compute the digest. In `FinalityGate.finalize`, the witness's own evidence requirements are used for finality-time rechecking, while the gate itself does not have an independently configured required-requirement set. The admission receipt digest is carried in the witness but is not checked against a durable issuance record in the inspected implementation.

This is a **conditional provenance weakness** if an untrusted actor can supply, replace, or modify persisted witness data or select the requirements passed to admission. It is not established as an exploitable production vulnerability in deployments where witness objects never cross a trust boundary and only trusted code selects requirements.

## Source facts

- `AdmissionWitness.verify()` checks `self.digest == sha256_json(self.body_dict())`.
- `AdmissionWitness.from_dict()` reconstructs an object and checks that same digest; it does not verify an issuer MAC/signature.
- `FinalityGate.admit(event, requirements)` receives `requirements` as a parameter and binds evidence for that supplied tuple.
- `FinalityGate.finalize(witness, event)` verifies the public digest, event hash, runtime decision and policy identity; then it rechecks evidence according to requirements inside the witness.
- The gate has no durable one-use ledger for witness identifiers in the inspected code.
- `LYCHEETAH_GUARD_SETUP.md` explicitly labels the Guard integration `[SCAFFOLD]` and says the caller must enforce the returned decision.

Source links:

- [finality.py](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py)
- [test_assurance_finality.py](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/tests/test_assurance_finality.py)
- [Guard setup and integration boundary](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md)

## Source-equivalent reproduction

The v1.7 source-equivalent probe constructs a witness with substituted evidence requirements and a fabricated admission-receipt digest, computes a new public SHA-256 digest, and asks a minimal mirror of the acceptance-relevant source semantics to finalize it. The mirror accepts the new witness. This establishes that the inspected acceptance logic lacks cryptographic provenance under the modeled input boundary; it does not execute the upstream package.

## Defensive reference design

`trusted_witness.py` tests a layered alternative:

1. Requirements are configured inside the trusted gate instance, not selected by callers per witness.
2. The witness body is authenticated using HMAC-SHA256 with a secret that stays inside the trusted service.
3. Issuance is recorded in a SQLite registry protected by the service boundary.
4. Finalization checks the token MAC, issuer registry body hash, exact action digest, policy identity, expiry and evidence.
5. `BEGIN IMMEDIATE` plus a conditional update makes successful witness consumption single-use for concurrent callers sharing the same SQLite database.

The HMAC and registry are intentionally redundant: HMAC authenticates the body, the registry establishes that this gate actually issued it, and the atomic consume operation prevents the same witness being accepted more than once by the registry.

## Test outcomes

The v1.8 reference harness contains 16 test methods, all passing locally. Its concurrency test repeats the two-thread race 25 times and observed exactly one successful consumption in every pair. Additional tests cover genuine issuance, public-hash substitution, another-gate transfer, action substitution, evidence change, expiry, replay, runtime REVIEW, malformed input, policy changes, and reconstruction after object restart.

One test intentionally records an **unresolved limitation**: a separate evidence provider may change immediately after returning its snapshot. The SQLite transaction can serialize witness consumption, but it cannot lock a separate provider or remote effect. The prototype's allow result in that test is an expected demonstration of the architecture's remaining TOCTOU boundary, not a successful security assertion.

## Non-goals and limits

- This does not prove the full upstream package behaves identically to the source-equivalent mirror.
- This does not make a remote side effect atomic with local witness consumption.
- A host with access to the HMAC key or trusted registry can mint or alter authorization state; those are security boundaries and require operating-system/service controls.
- A malicious or stale evidence provider requires its own authenticated provenance and freshness protocol.
- HMAC is shared-secret authentication, not public verifiability or non-repudiation.
- The demo `ToyRuntime` is not a replacement for actual `AssuranceRuntime` verification.
- Production should use a managed secret, key identifier/rotation procedure, durable shared registry, schema/version migration, monitoring and fault-injection tests.

## Upstream status

No upstream code was changed. Branch creation returned HTTP 403 from the connected GitHub integration. The full upstream test suite and CI have not been run.
