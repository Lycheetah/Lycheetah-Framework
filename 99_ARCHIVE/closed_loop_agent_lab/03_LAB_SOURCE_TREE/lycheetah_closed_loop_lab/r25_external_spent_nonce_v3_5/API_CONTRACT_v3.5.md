# API Contract v3.5 — External Spent-Challenge Registry

## Purpose

v3.4 demonstrated that an HMAC-authenticated local challenge ledger can be rolled back to a prior valid snapshot. v3.5 composes the local quorum verifier with an independently administered HTTP spent-nonce registry. The registry's atomic `PENDING -> CONSUMED` transition becomes the monotonic authority for one-time use.

## Components

- `DurableFreshnessVerifier`: retained v3.4 local signed-chain and quorum verification.
- `SpentChallengeRegistryService`: local HTTP simulator with a separate SQLite file, service storage HMAC key, client HMAC authentication, anti-replay request IDs, and Ed25519-signed responses.
- `SpentChallengeRegistryClient`: HTTPS-only except explicit loopback tests; no redirects; bounded request/response sizes; pinned response signing key; validates signed response bindings.
- `RemoteMonotonicFreshnessVerifier`: registers a challenge remotely at issuance; verifies the full chain locally; consumes the remote nonce; then consumes the local row.

## Sequence

1. The local verifier issues a challenge and persists the exact database ID, nonce, issue/expiry times and policy fingerprint.
2. The client registers that tuple with the external registry. The challenge is returned to the caller only after a valid signed registration response.
3. Witnesses issue signed fresh-head reports bound to the nonce. The local verifier checks chain continuity and witness quorum.
4. The external registry atomically checks the registered tuple, expiration and pending state, then changes `PENDING` to `CONSUMED`.
5. The local verifier rechecks and consumes its local row. If local commit fails after remote consume, the challenge remains spent remotely; a new challenge is required.

## Registry routes

### `POST /v1/challenges`
Exact JSON keys: `nonce`, `database_id`, `issued_at_ms`, `expires_at_ms`, `policy_sha256`. Registration is create-only; duplicate nonces return conflict. Challenge lifetime is bounded to one hour at the registry boundary.

### `POST /v1/challenges/{nonce}/consume`
Exact JSON keys: `database_id`, `policy_sha256`, `issued_at_ms`, `expires_at_ms`. All values must match the registered row. A valid pending row is consumed once by one SQLite write transaction. Unknown, mismatched, expired, already-consumed or tampered rows fail closed.

## Authentication

Client requests are authenticated by HMAC-SHA256 over domain-separated canonical JSON containing method, path, timestamp, unique request ID and exact body digest. The registry accepts a bounded timestamp window and rejects reused `(key_id, request_id)` values. The registry signs every response—including errors—with a pinned Ed25519 key over HTTP status, response body, server key ID and request ID. Client-side request IDs are one-use, so a lost response is an ambiguous outcome: do not replay the same signed request blindly; request a fresh challenge after checking service state through an operational recovery procedure.

## Crash and failure semantics

- Registry rejects / unavailable before consumption: do not accept the freshness result.
- Registry commits consumption but response is lost: the challenge is burned; request a new challenge. Do not infer success from a retry.
- Registry commits consumption but local consume fails: the challenge is burned remotely; this sacrifices availability to preserve one-use semantics.
- Primary-ledger snapshot rollback only: replay is denied while registry state remains current.
- Registry rollback, or coordinated rollback of both trust domains: outside the protection of this prototype; the negative control demonstrates replay can return.

## Trust assumptions

The production registry must be administered independently from the primary verifier, hold separate credentials/keys, authenticate clients, keep its spent set monotonic through failover and backup restoration, and expose auditable atomic compare-and-swap semantics. The included service uses SQLite on the same test host and is a protocol simulator—not a production non-rollbackable service.
