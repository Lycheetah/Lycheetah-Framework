# Remote Witness HTTP API Contract v3.8

## Purpose

This local reference adapter exercises the v3.7 checkpoint quorum across four distinct operating-system processes over a real HTTP loopback boundary. It is a process/network-boundary experiment, not a distributed deployment or a claim of independent trust domains.

## Endpoint surface

Every endpoint accepts `POST`, `Content-Type: application/json`, a body no larger than 1 MiB, and requires a fresh authenticated request.

- `/v1/head` — exact body `{ "challenge_nonce": "..." }`; returns the witness's nonce-bound signed head report.
- `/v1/attest` — exact body `{ "checkpoint": { ... } }`; returns the witness's signed vote after its durable append-only checks.
- `/v1/checkpoint` — exact body `{ "sequence": 1 }`; returns the signed checkpoint record if retained, otherwise `null`.

Unknown routes are rejected. Numeric loopback binding is mandatory; arbitrary hostname binding and non-loopback HTTP endpoints are refused by the client/server constructors.

## Request authentication

Headers bind an API key ID, unique request ID, millisecond timestamp, method, path, and exact body SHA-256 into a domain-separated HMAC-SHA256 signature. The server enforces a ±30-second timestamp window and persists consumed `(key_id, request_id)` pairs to a separate SQLite replay ledger before invoking the witness operation. Reused IDs are rejected.

The witness's Ed25519 signature on the returned head or vote is validated by the existing quorum verifier. The API HMAC authenticates the RPC caller to the witness process; it does not replace witness signatures or prove that distinct witness services are independently administered.

## Failure behavior

- Invalid/missing HMAC fields or signature: HTTP 401.
- Replayed API request ID: HTTP 409.
- Unknown endpoint: HTTP 404.
- Oversized request body: HTTP 413 before reading the body.
- Invalid body or unsupported operation: HTTP 400.
- Unexpected server failure: generic HTTP 500 without exception details.
- Unavailable transport or non-200 response: typed client transport error; coordinator decides quorum/availability.
- Redirect following is disabled in the client.

## Security caveats

The server supports HTTP only on loopback. Keys are loaded from local JSON test configuration files, the API replay ledger is local, and all four services share one machine and one administrative boundary. Do not expose this interface to a network or use it as a production trust anchor. Production needs TLS/mTLS, separate hosts/accounts/administrators/keys/backups, hardened secret distribution, monitoring, rate limiting, operator recovery, and independent review.
