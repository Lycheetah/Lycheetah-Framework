# Threat Model v3.9 — mTLS Remote Witness Transport

## Security question

Does a remote witness RPC require authenticated encrypted transport and a specific coordinator client identity, while preserving the existing witness signature/quorum checks and fail-closed behavior?

## New controls

- TLS 1.2+ on every witness RPC connection; plain HTTP cannot reach the HTTP handler.
- Server certificate chain and hostname/IP SAN verified by the client.
- Client certificate chain required by the server, plus exact coordinator URI-SAN allowlist check.
- HMAC RPC authentication still binds method/path/time/request ID/body digest.
- Duplicate request IDs remain durably rejected; witness reports/votes still rely on Ed25519 signatures.
- Per-accepted-connection TLS handshake occurs in a worker thread with a short timeout, so a socket that never starts TLS does not block the accept loop.
- Non-loopback bind requires explicit opt-in and a specific numeric IPv4 address; wildcard binds are refused.

## Adversary scenarios exercised

- No client certificate.
- CA-trusted client certificate with the wrong coordinator URI SAN.
- Server certificate/name mismatch across two witness addresses.
- Attempted cleartext HTTP against the TLS listener.
- Slow client that connects but does not begin a TLS handshake while a valid client sends a request.
- Wrong HMAC secret, body tampering, replayed request ID, stale/malformed request, oversized body, unknown route, noncanonical target.
- Witness process restart, dropped response after durable vote, one-witness outage and two-witness outage.

## Still not established

- Four subprocesses share one host and one operator/OS administrator; root access can alter processes, databases, config, keys, or certificates.
- TLS CA and coordinator client certificate are locally generated in tests. There is no production CA lifecycle, revocation, independent secret management, bounded worker pool, or request rate limiting.
- Binding to a non-loopback IPv4 is supported only with explicit configuration; it has not been tested against remote hosts or an internet-facing network.
- The inherited registry facade uses its own local loopback HTTP harness. This work does not convert every endpoint in the larger lab to TLS.
- A privileged coordinated restoration of all state stores remains the previously documented anti-rollback negative control.
- No hosted service was contacted, no upstream code changed, and no formal verification/certification is claimed.
