# Lycheetah Admission Witness Provenance Audit — v1.7

**Status:** Source-inspected finding plus source-equivalent reproduction. Not an upstream execution, deployed exploit, or production security claim.

## Executive finding

The inspected `FinalityGate` acceptance path verifies that an `AdmissionWitness`'s SHA-256 digest matches its own body, then checks event identity, current runtime decision, policy fingerprint, and the evidence claims contained in the witness. The inspected `AdmissionWitness.issue()` computes that digest using public canonical JSON hashing, and `verify()` recomputes the same hash. There is no keyed authenticator, gate-issued witness registry, nonce, or consumed-witness state in the inspected witness structure.

Therefore, if an attacker can supply or modify a serialized witness that is accepted by `finalize`, the bare SHA-256 digest does not establish provenance. An editor can modify the evidence requirement (or `admission_receipt_sha256`) and recompute the public digest. Because finality evaluates the evidence requirements from the witness itself and does not resolve them from a trusted policy/configuration source, a substituted requirement can pass if the evidence provider contains a record satisfying it.

The local source-equivalent reproduction demonstrates the acceptance logic under that explicit threat model. **It does not prove a deployed exploit.** If the application guarantees that only a trusted in-process caller can pass objects directly from `admit` to `finalize`, and witnesses cannot be loaded from attacker-writable persistence or RPC inputs, external forgery is not established by this finding. The upstream module is explicitly marked `[SCAFFOLD]` and disclaims production atomicity.

## Inspected upstream source

Repository: `Lycheetah/Lycheetah-Framework`

Commit inspected: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`

Source: [`lycheetah/assurance/finality.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py)

Blob SHA reported by GitHub Contents API: `dd97733d45c2261863d24a2a00800baf59fc8bac`

Relevant behavior, paraphrased from that source:

1. `AdmissionWitness.issue()` serializes event hash, policy identity/version/hash, admission receipt digest and bound evidence into a body, then sets `digest = sha256_json(body)`.
2. `AdmissionWitness.verify()` only compares its stored digest with a fresh `sha256_json(body_dict())` calculation.
3. `AdmissionWitness.from_dict()` calls `verify()` after constructing the witness. As hashing is unkeyed, this detects un-rehashed changes but does not authenticate who created the witness.
4. `FinalityGate.finalize()` checks non-empty evidence, witness digest, event digest, current runtime outcome, and policy identity. It fetches current evidence for the requirement objects *inside the witness*.
5. The finality path does not verify that `admission_receipt_sha256` refers to an issued admission receipt, nor that the witness came from a trusted `admit()` call. The checked-out module also does not have a witness identifier or consumed-witness store.
6. The public `admit(event, requirements)` API accepts requirements as an argument. If this list is not supplied from trusted policy/configuration, witness authentication alone would not make the requirement set authoritative.

Existing upstream tests detect simple tampering where the digest is not recomputed, action substitution, policy changes, and empty-evidence witnesses. They do not appear to test a fully re-hashed witness whose requirement set has been changed.

## Reproduction result

`witness_provenance_probe.py` mirrors only the source acceptance semantics needed for this hypothesis and uses Lycheetah's canonical JSON profile (`sort_keys=True`, compact separators, UTF-8). It constructs an honest witness and a forged witness with:

- the same event digest;
- the same current policy identity/version/hash;
- a replacement evidence requirement pointing to another record in the provider;
- an arbitrary admission-receipt digest; and
- a newly computed, internally consistent public SHA-256 digest.

Observed source-equivalent result: both honest and forged witness accepted. The strict illustrative reference path accepts an HMAC-authenticated configured witness, rejects modified witness data, and rejects replay of the same witness identifier after consumption.

Local tests: **5/5 passed**. These are tests of the source-equivalent acceptance model and a proposed reference defense, not the upstream package.

## Risk classification

**Conditional provenance / requirement-binding gap.** It becomes security-relevant when a persisted witness, RPC message, queue item, user input, plugin result, or other attacker-modifiable representation can reach `finalize`. Severity depends on who can modify that representation and whether witness requirements are expected to encode trusted release gates.

It is not a SHA-256 cryptographic break. The problem is using a public digest as if it proved origin and authoritativeness.

The missing requirement binding is distinct from integrity: even a perfectly authenticated witness can be unsafe if a less-trusted caller was permitted to choose weaker required evidence before `admit` issued it.

## Proposed change

### Preferred design: authoritative admission ledger + opaque one-use reference

1. Have a trusted policy/release configuration resolver define required evidence. Do not accept the authoritative requirement set from an untrusted model, plugin or caller.
2. On successful admission, persist a canonical record containing a random witness ID, event digest, policy digest, receipt digest, exact requirement-set digest, evidence records, issuance time and expiry.
3. Return only an opaque witness ID to callers that do not need the contents. Keep the ledger authoritative.
4. At finality, fetch the record by ID; verify the event and current policy; revalidate the configured evidence requirements; enforce expiry; atomically reserve/consume the witness once.
5. Make finalization and action intent durable/idempotent. A process-local set is only a demonstration; it does not provide cross-process replay protection or atomic remote side effects.

### Alternative: authenticated serialized witness

For designs that genuinely need serialized witnesses across a trust boundary, HMAC-sign the canonical body with a secret held only by the issuing service, and maintain a replay/consumption store. Bind the signature to the full requirement-set identity and trusted admission receipt. Do not expose the HMAC key or a signing tool to model-visible inputs. HMAC alone does not prevent replay, and signature alone does not make caller-selected requirements authoritative.

## Validation plan before upstream integration

- Add an upstream regression: modify a valid witness's evidence list, recompute its public SHA-256 digest, and assert finality rejects it when external/untrusted witness ingress is supported.
- Add a forged `admission_receipt_sha256` test and require the ID to resolve to a real trusted ledger record or authenticated receipt.
- Test requirement-set substitution and require trusted configuration to win.
- Test duplicate finalization, two concurrent finalizations, expiry, restart, and storage recovery.
- Run the actual complete `tests/test_assurance_finality.py`, receipt/runtime tests, package build, installed-wheel tests, and CI against a clean checkout.
- Test provider-side idempotency and crash windows separately. `FinalityGate` alone cannot make remote side effects atomic.

## Limitations

- GitHub repository write/branch creation was attempted through the connected integration and returned HTTP 403 (`Resource not accessible by integration`). Container DNS to `github.com` also failed, preventing a clean checkout.
- No upstream source or tests were modified.
- The probe is deliberately a small source-equivalent model—not dynamic execution of `finality.py` itself.
- The proposed defense in the probe is illustrative, process-local, and not production ready.
