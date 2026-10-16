# Remote Witness API Contract v3.9 — TLS/mTLS

## Purpose and status

This version carries the v3.8 remote-witness RPC through a real TLS 1.2+ connection with mutual TLS, while retaining request HMAC authentication, durable transport replay protection, and Ed25519 signatures on witness evidence. It is a local reference prototype, not a production deployment.

## Transport identity

- HTTPS is mandatory in `RemoteWitnessClient`; plain HTTP downgrade is refused.
- Client contexts require a trusted CA, hostname verification, and a client certificate/key pair.
- Server contexts require a trusted client certificate. In addition, each witness checks for the exact configured coordinator URI SAN (`spiffe://...`) before validating HMAC RPC authentication.
- Test server certificates include a SAN for the actual loopback IP being used, so a certificate issued for one witness address cannot be substituted at another address without hostname verification failing.
- TLS minimum version is 1.2. Redirects are disabled.
- TLS handshake work happens in a request worker with a 3-second timeout; post-handshake requests have a 10-second socket timeout. This prevents one incomplete handshake from blocking the accept loop. Concurrency is not globally rate-limited in this reference server.

## Bind policy

By default, witness services bind to a numeric IPv4 loopback address. Non-loopback binding requires `allow_non_loopback: true`, a literal, specific IPv4 address, and a valid mTLS configuration. Wildcard addresses such as `0.0.0.0`, multicast addresses, DNS names in the bind field, and IPv6 are rejected. The client can use a DNS hostname for an HTTPS endpoint; standard certificate-chain and hostname validation applies at connection time.

## Application request authentication

The request HMAC binds method, canonical path, timestamp, unique request ID, and exact body SHA-256 under the `lyc-registry-witness-mtls-rpc-v3.9` domain string. Timestamp freshness is checked against a ±30-second default window; `(key_id, request_id)` values are durably consumed before an operation runs. Reusing the same request ID is rejected. An ambiguous response must be retried with a new transport request ID after determining the underlying operation's idempotency behavior.

The transport HMAC authenticates RPC use but does not replace witness Ed25519 signatures. The coordinator verifies the signatures and distinct identities in the existing quorum code.

## Routes

All routes use `POST`, `Content-Type: application/json`, an exact JSON object shape, and a maximum body of 1 MiB:

- `/v1/head`: `{ "challenge_nonce": "..." }`
- `/v1/attest`: `{ "checkpoint": { ... } }`
- `/v1/checkpoint`: `{ "sequence": 1 }`

Unknown routes, query strings, transfer encoding, malformed bodies, stale or invalid signatures, and replayed request IDs are rejected.

## Configuration additions

Witness config now includes `bind_host`, `allow_non_loopback`, `tls_server_cert_path`, `tls_server_key_path`, `tls_client_ca_path`, and `tls_client_identity_uri`. Client construction requires `tls_ca_path`, `tls_client_cert_path`, and `tls_client_key_path`.

## Security limits

- The tests generate an ephemeral local CA and certificates; these are test materials, not production credentials.
- Certificate revocation, online status checking, CA rotation workflow, remote secrets distribution, service rate limits, and incident response are not implemented.
- All tests use four processes on one host. They do not establish independent machines, administrators, backups, or key custody.
- The inherited coordinator-facing registry HTTP facade remains a separate loopback-only local test component; v3.9 specifically upgrades witness RPC transport.
- Upstream source and CI remain unchanged/unrun.
