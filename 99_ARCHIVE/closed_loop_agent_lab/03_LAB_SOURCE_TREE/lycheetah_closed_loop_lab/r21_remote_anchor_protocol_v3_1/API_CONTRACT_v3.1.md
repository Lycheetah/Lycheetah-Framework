# Remote Monotonic Anchor API Contract v3.1

## Purpose

A source-level reference protocol for submitting a monotonic checkpoint to a separately operated anchor service. The Python implementation in this pack includes an HTTP client, local SQLite-backed service simulator, Ed25519 operator approvals and server responses, compare-and-swap sequence checks, a durable client publish outbox, and recovery after a lost response.

**This is not a production anchor service.** The included service is deliberately local and stores its history in SQLite. It tests the protocol contract, not remote hosting, backup isolation, WORM retention, infrastructure identity or provider-wide availability.

## Endpoints

All paths are relative to the configured anchor base URL. `database_id` and `request_id` are validated identifiers; clients percent-encode path segments.

- `POST /v1/databases/{database_id}/checkpoints` — submit `{request_id, snapshot, approval}`.
- `GET /v1/databases/{database_id}/requests/{request_id}` — authoritative idempotency status lookup.
- `GET /v1/databases/{database_id}/history` — verify and return the full signed append-only sequence.
- `GET /v1/databases/{database_id}/head` — verified latest record or `null`.

## Authentication and authorization are separate

### Client request authentication

Every HTTP request uses HMAC-SHA256 headers bound to method, exact path, timestamp, nonce, and SHA-256 of the request bytes. The service checks a short timestamp window and rejects a reused nonce. The service response signs the exact HTTP status, response body and server key ID with Ed25519. Clients pin an explicit trusted server public key. Redirect following is disabled so signed requests cannot be forwarded to an alternate destination.

The shared request-authentication key identifies an API client; it does **not** authorize a new checkpoint state.

### Operator authorization

The exact state-change approval is signed with Ed25519 by an operator private key kept outside the agent/runtime. It binds the database ID, publish-request ID, expected sequence and parent hash, exact snapshot fingerprint, reason code, issuance and expiration. The service contains only configured operator public keys and rejects expired, untrusted, mismatched or replayed approvals.

### Monotonic append

The service validates the logical snapshot digest itself. Append runs in one SQLite `BEGIN IMMEDIATE` transaction that validates the existing complete history and its request/approval indexes, checks expected sequence/head, consumes the approval ID and nonce, inserts a signed checkpoint, and stores the stable request ID result. Same request ID + same canonical request is idempotent; same ID + different request is a conflict.

## Ambiguous append policy

The client writes the exact proposed request to an HMAC-authenticated SQLite outbox before sending it. When a POST response is lost or fails verification, the publisher queries the authoritative request endpoint. A matching, signed record means committed. An authoritative `NOT_FOUND` permits one retry of the exact request with the exact same request ID. If lookup is unavailable, identity mismatches, or records do not verify, the local operation stays `UNKNOWN`; it does not guess success/failure or mint a new request ID automatically.

An `UNKNOWN` request resumes with status lookup before a new POST. `COMMITTED` and `CONFLICT` outbox records are terminal and cannot be rewritten through the API.

## Production requirements not satisfied by the simulator

A real deployment must supply TLS with strict service identity, an independently protected append-only/compare-and-swap store, durable high-water marks, backup/restore separation, key rotation, access control, rate limiting, observability, retention for replay nonces, and a runbook for uncertain remote commits. Its deployment architecture must also prevent coordinated rollback of the anchor service's own storage. A pair of local SQLite files does not supply that guarantee.
