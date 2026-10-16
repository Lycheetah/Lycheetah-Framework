# Lycheetah Remote Monotonic Anchor Protocol v3.1

This package advances the Lycheetah assurance line from local checkpoint simulation to an **HTTP-level protocol reference** for publishing database-state checkpoints to a separate anchor service.

## What is included

- Ed25519 operator approvals binding the exact snapshot, database identity, stable request ID, expected sequence/head, reason, and validity window.
- HMAC-authenticated HTTP client requests with timestamp, nonce, body digest, and replay checks.
- Ed25519-signed checkpoint records and responses, verified against an explicitly pinned server public key.
- Compare-and-swap append and a server-side idempotency/request-result index.
- A durable HMAC-authenticated client outbox with `PENDING`, `UNKNOWN`, `COMMITTED`, and `CONFLICT` states.
- Ambiguous-response recovery through authoritative request lookup. The client never silently generates a new request ID to escape uncertainty.
- Refusal to follow redirects with authenticated requests; explicit loopback-only HTTP test opt-in; HTTPS required otherwise.
- Historical v3.0 checkpoint components and tests, kept together at the exact matching revisions for regression verification.

## Run the tests

Requires Python 3.11+ and `cryptography` (see `requirements.txt`). From this directory:

```bash
python -m pip install -r requirements.txt
./run_v3_1_tests.sh
```

The run script invokes four independent test groups to keep the existing checkpoint suite separate from the HTTP transport tests. The recorded runs in `test_logs/` show:

| Group | Tests | Result |
|---|---:|---|
| Existing v3.0 checkpoint suite | 33 | PASS |
| Remote HTTP protocol group 1 | 14 | PASS |
| Remote HTTP protocol group 2 | 14 | PASS |
| Remote HTTP protocol group 3 | 13 | PASS |
| **Total** | **74** | **PASS** |

The 41 protocol tests are divided across groups purely to make each run independently inspectable. `RESULTS_v3.1.md` records the exact scope and boundaries.

## Security boundary

**This is a reference protocol and local simulator, not a production remote anchor.** The service uses SQLite and a local HTTP server for tests. It does not provide production WORM storage, independently administered backup/restore protection, production TLS identity provisioning, remote high-water-mark isolation, enterprise key custody, or a deployed service. A sufficiently privileged attacker who can roll back the anchor database, its key material, and every external copy can still defeat local history assumptions. Coordinated rollback is not solved by a second SQLite file.

The design addresses ambiguous HTTP outcomes and request idempotency under the stated reference contract. It does not make the primary database and remote anchor a distributed atomic transaction, and it does not bind a Stripe refund to a checkpoint. No hosted Stripe calls or real refunds were performed.

## Upstream boundary

Observed upstream repository: https://github.com/Lycheetah/Lycheetah-Framework

Pinned upstream `master` remained at commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65` at the time of this pass. This artifact is an exploratory integration candidate, not a drop-in replacement for the existing `MonotonicAnchor`. No upstream branch, source change, pull request, or CI run was created.
