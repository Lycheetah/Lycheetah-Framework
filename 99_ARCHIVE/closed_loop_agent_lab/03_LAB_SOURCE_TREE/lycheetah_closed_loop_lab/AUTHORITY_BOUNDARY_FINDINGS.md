# Authority boundary findings — 2026-10-16

## Summary

The next concrete control seam is not another output-quality detector. It is the boundary between an agent's proposal and the trusted host's decision to permit a consequential effect.

The Lycheetah repository's Assurance Runtime does not claim to authenticate a reviewer. In `lycheetah/assurance/runtime.py`, the tool-evaluation logic explicitly says model-facing integrations must not populate `human_approved` themselves. `lycheetah/assurance/finality.py` provides an additive finality scaffold, but its witness integrity is an unkeyed SHA-256 digest and the call remains outside atomic control of a remote provider. The `34_ASSURANCE_RUNTIME/FINALITY_EVIDENCE_REVALIDATION_v0.1.md` handoff itself documents these trust boundaries.

The important distinction is that the repository documents the integration requirement; this local experiment does not establish that the current deployed integration violates it. We have not inspected a deployed host adapter or exercised a real tool provider.

## Local artifact added

`authority_boundary_lab/authority_gate.py` is a reference prototype with:

1. Canonical snapshot of the exact consequential action.
2. HMAC-signed, short-lived approval token binding action digest and policy digest.
3. Expiry and future-issuance checks.
4. A SQLite primary-key nonce claim to prevent reuse of the same token.
5. Dispatch from the same canonical snapshot that was approved.
6. Conservative handling of an executor exception: the token remains consumed and the operator must reconcile the effect before trying again.

The prototype is deliberately additive and is not wired into `AssuranceRuntime` or any production tool path. Test keys are fixtures and must never be used outside the lab.

## Executed checks

- Missing token / a boolean claim alone: denied by candidate.
- Wrong action arguments or tool: denied.
- Changed policy hash: denied.
- Expired or not-yet-valid token: denied.
- Modified token or wrong signing key: denied.
- Sequential replay: second use denied.
- Eight concurrent attempts to reuse one token: exactly one dispatch callback succeeds.
- Mutation of the caller's source dictionary after action construction: dispatched snapshot remains the approved value.
- Executor exception: token remains consumed; retry is denied pending reconciliation.

The full local suite passes 37 tests (13 original harness/sensitivity tests, 10 calibration/correlation tests, and 14 authority-gate tests). These are unit tests on authored reference code, not an independent security assessment.

## Why this is conventional, not a novelty claim

The design follows established principles: explicit identity and authorization, just-in-time least privilege, separation of duties and deny-by-default. NIST's Zero Trust guidance describes authorization around identity, resources and policy context rather than implicit trust, and emphasizes least privilege and periodic/repeated verification. See:

- https://www.nist.gov/publications/zero-trust-architecture
- https://pages.nist.gov/zero-trust-architecture/VolumeB/ZeroTrustTakeaways.html

The possible contribution is a carefully integrated and measured Lycheetah use of these controls around agent actions, not HMAC, tokens, digests, or replay protection as novel techniques.

## Material limitations

- `ApprovalAuthority.issue()` is a trusted API by convention in this scaffold. If the model process can call it or access its secret key, the control fails. Production must isolate and authenticate the approval-issuing path.
- The prototype records a reviewer ID and approval reference but does not verify the reviewer, identity provider, or actual UI confirmation.
- The local SQLite nonce claim is not a distributed replay defense and has not been subjected to process-crash/restart or filesystem-corruption tests.
- Nonce consumption and an external provider effect are not one atomic transaction. If dispatch times out, the effect may or may not have occurred; provider idempotency, durable receipts and reconciliation are required.
- No revocation service, key rotation, provider-bound idempotency, hardened sandbox, production credentials, or independent penetration test is included.
- The demo's comparison baseline intentionally trusts a model-supplied boolean to illustrate a bad integration. It is not a measured claim about the currently deployed Lycheetah system.

## Next engineering gate

Before any integration proposal, inspect the actual host adapter that constructs `AssuranceEvent`, identify exactly who can set `human_approved`, and prove the approval UI and tool dispatcher bind to the same immutable action object. Add an end-to-end test with a fake provider, including concurrent duplicate calls, revoke-before-dispatch, timeout-after-effect, process restart, and explicit wrong-action approval attempts. Only then consider a small disposable dry-run.
