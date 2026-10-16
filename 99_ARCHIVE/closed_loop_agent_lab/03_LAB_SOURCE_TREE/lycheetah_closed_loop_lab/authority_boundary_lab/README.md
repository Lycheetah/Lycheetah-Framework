# Consequence Gate — Authority Boundary Lab v0.1

**Status: R0 research prototype. Not integrated into Lycheetah Framework; not production hardened.**

## Question

Can a host-side gate distinguish a trusted, narrowly scoped approval from an agent-supplied claim that approval occurred?

The current Lycheetah assurance code documents `human_approved` as caller-declared state: model-facing integrations must not populate it themselves. That is a valid architectural warning, but it leaves enforcement to the integration. This lab makes the boundary explicit in a runnable reference component.

## Candidate mechanism

- Snapshot the exact consequential action (agent, tool, JSON arguments, scopes, workspace) and hash its canonical representation.
- A host-only approval authority signs a short-lived HMAC token binding the approval to the action digest and current policy digest.
- The gate verifies signature, action, policy, issuance/expiry and token schema.
- A SQLite unique nonce claim prevents sequential/concurrent reuse within the same local database.
- Dispatch receives the canonical snapshot that was actually approved, not a mutable source mapping.
- If dispatch throws, the token stays consumed; the caller must reconcile effect state before authorizing a retry.

## Run

From the parent `lycheetah_closed_loop_lab` directory:

```bash
python -m unittest discover -s authority_boundary_lab -p 'test_*.py' -v
```

Or run all research suites from the project root:

```bash
python run_all_tests.py
```

## What the tests establish

The unit tests demonstrate this local implementation's stated behavior against authored cases: missing/spoofed approval claims do not substitute for a token; action or policy changes invalidate tokens; expired, tampered, replayed or wrong-key tokens are refused; the dispatched action is an immutable snapshot; and exception after consumption does not make the same token reusable.

This is **not** evidence about model-agent performance, reviewer identity verification, malicious code containment, remote provider atomicity, production reliability, or a security review.

## Critical trust boundary

HMAC is authentication only if the signing secret and issuance path are protected. The class cannot prove the human actually clicked approve: the surrounding host must authenticate the reviewer, show the exact operation and scope, and expose issuance only to that trusted workflow. Never give the signing key or `ApprovalAuthority.issue()` capability to the model process.

SQLite consumption is locally atomic, but remote effect execution is not transactional with the nonce claim. A crash can leave the outcome uncertain after the token is consumed. Production needs provider idempotency keys, durable effect receipts, reconciliation, revocation, key rotation, concurrency/restart tests, and independent security review.

## Design relation

This follows conventional least privilege, explicit identity/authorization, separation of duties, and just-in-time authorization rather than claiming novelty for HMAC, token expiry, or replay protection. The research question is whether this boundary can be integrated into Lycheetah's Assurance Runtime and whether it reduces approval-substitution failures without unacceptable friction.
