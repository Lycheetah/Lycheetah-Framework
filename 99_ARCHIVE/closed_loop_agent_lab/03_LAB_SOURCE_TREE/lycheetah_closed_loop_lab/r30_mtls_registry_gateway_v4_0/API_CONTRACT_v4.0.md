# Lycheetah mTLS Registry Gateway API Contract v4.0

## Scope

v4.0 closes one specific gap in the v3.9 research harness: the coordinator-facing `SpentChallengeRegistryService` / `RegistryQuorumAnchor` HTTP boundary now has a separate mTLS-capable server implementation. It supplements rather than replaces the existing signed request/response and quorum mechanisms.

This is a local reference server class, not a ready-to-deploy production daemon. The end-to-end tests use one host, a temporary test CA, four witness subprocesses, and a temporary SQLite state directory.

## Transport requirements

- TLS 1.2 or later.
- Server certificate chain and hostname/IP SAN must validate in clients.
- Client certificate is required by the TLS handshake and must chain to the configured client CA.
- After chain validation, the application pins the coordinator identity against an explicit allowlist of URI SANs such as `spiffe://lycheetah.local/coordinator`.
- The coordinator also must supply the existing registry HMAC request authentication. mTLS does not replace method/path/timestamp/request-ID/body-digest authentication.
- Redirects are not followed by the test client path. Cleartext HTTP does not reach the request handler.
- Default bind behavior is numeric IPv4 loopback. Non-loopback binding requires an explicit constructor opt-in and rejects wildcard/reserved addresses. Independent-host deployment is not validated by this pack.

## HTTP request profile

Only `POST` is accepted. Current supported route forms are:

- `/v1/challenges`
- `/v1/challenges/{nonce}/consume`

Requirements:

- Exactly one Host header matching the configured listener address and port.
- Exactly one `Content-Type: application/json` header.
- Exactly one non-negative decimal Content-Length, maximum 128 KiB.
- `Transfer-Encoding` is not supported.
- Duplicate/missing Content-Length, unknown routes, wrong method, oversized bodies and wrong coordinator URI SAN are rejected before registry dispatch.
- Registry request HMAC remains responsible for request identity, timestamp skew, payload binding and replay semantics.

## Responses

Application responses use the existing signed registry envelope (`http_status`, `body`, `server_key_id`, `request_id`, `signature_b64`). Clients must verify both the HTTP status and Ed25519 response signature. Successful responses and authenticated semantic errors must bind to the outstanding request ID. On request-authentication failures the existing dispatcher may deliberately return `invalid-request-id` rather than reflecting an untrusted asserted identifier.

## Operational limits

- No CRL/OCSP revocation, live CA rotation, certificate issuance service, rate limiting, bounded global worker pool, or production secret manager.
- URI SAN checking uses certificate information supplied by Python's TLS stack after certificate-chain validation; deployment profiles must define the exact SAN format and rotation rules.
- Four witness processes and the gateway share the same host and administrator in the test suite. This is transport separation, not independent trust domains.
- The local coordinator ingress is mTLS-enabled only in this v4.0 test/reference composition; the upstream repository was not modified.
