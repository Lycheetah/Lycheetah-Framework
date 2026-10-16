# Authority Boundary Lab v0.5

**Status:** R0 research scaffold. Not wired into Lycheetah Assurance Runtime, not a production authorization service, and not a security certification.

## Why v0.5 exists

A counterexample in v0.4 showed that the gate verified an action token but still accepted an arbitrary execution callback at dispatch time. The callback could represent an operation different from the approved action. The gate was not claiming to authenticate callback semantics, so this was a gap in our local reference design and an important limit on its guarantee.

`authority_gate_v0_5.py` removes the callback from the `execute()` interface. A host-owned dispatch registry resolves a tool name to a target ID and semantic version. The target ID/version are part of the canonical approved action and signed token. The gate obtains the current policy digest and clock via trusted dependencies at construction, rather than accepting a per-call override. Tokens are bound to an audience (deployment identifier), can be revoked before claim, and are single-use in a local SQLite authority store.

## Run

From the lab root:

```bash
python -m unittest -v discover -s authority_boundary_lab_v0_5 -p 'test_*.py'
python authority_boundary_lab_v0_5/reproduce_v0_4_dispatcher_substitution.py
```

Or run every suite from the lab root:

```bash
python run_all_tests.py
```

## Trust assumptions

- The dispatch registry, policy provider, clock provider, signing key, nonce/revocation store, and issuance API are trusted-host components and are not accessible to the model process.
- The host authenticates the reviewer and displays the exact immutable action before issuance. This lab does not implement that UI or authentication flow.
- The host increments dispatcher version when the meaning/implementation of a registered route changes.
- Provider-side idempotency and reconciliation handle timeouts/crashes after a request may have reached the provider.

A Python class boundary alone is not security isolation against hostile code running in the same process. The database transaction protects local nonce consumption, not a transaction spanning a remote provider effect. If a token is consumed and the effect is uncertain, stop and reconcile before making another approval.

The companion `fake_host_adapter.py` exercises a host-shaped flow with an in-memory provider. Its eight tests include post-commit timeout reconciliation and pre-commit uncertainty. See `../HOST_ADAPTER_INTEGRATION_v0.6.md`.

## Included controls

- Canonical immutable action snapshot.
- HMAC signature with minimum key length.
- Action hash, dispatcher identity/version, policy digest, audience, nonce, issue time and expiry binding.
- Trusted policy lookup and trusted clock lookup at use time.
- Unknown tools, stale policy, changed dispatch binding, expired/future tokens, invalid signatures, revoked approvals, and replay rejected.
- Concurrent replay and gate-reconstruction tests against the same local SQLite file.
- One-use token consumed before dispatch; errors require reconciliation, not blind retry.

## What this does not show

It does not show that real agents can or cannot bypass a real host, that a real reviewer is authenticated, that a remote effect happens exactly once, or that the design outperforms conventional controls in production. The `reproduce_v0_4_dispatcher_substitution.py` counterexample records a string in memory and does not execute the named destructive operation.
