# API Contract v4.2 — Coordinator mTLS Ingress

## Identity

- TLS 1.2 or later is required.
- A trusted client certificate must contain exactly one URI SAN that matches the configured allow-list of `spiffe://` coordinator identities.
- Zero matches returns signed `403 coordinator-identity-invalid`.
- More than one match returns signed `403 coordinator-identity-ambiguous`; no arbitrary principal is selected.

## Resource admission

### Before TLS

1. Global active-connection bound.
2. Direct-peer-IP active-connection bound.
3. Process-local token bucket for new TCP connections.
4. Bounded listen backlog.

Admission rejection closes the socket before TLS handshake or a request worker is created.

### After mTLS identity mapping

The exact selected URI SAN receives a process-local active-dispatch quota and request token bucket. Authenticated quota rejection returns a signed `429` envelope with an explicit error code. Quotas apply after request headers have parsed and before the body/registry dispatch completes. The global connection bound remains the slow-header defense.

## Snapshot

`admission_snapshot()` exposes aggregate active counts, limits, token approximation and rejection counters. It intentionally does not return peer IPs, coordinator URI SANs or request content.

## Explicit non-guarantees

Quotas are per process and reset on restart. They are not distributed fairness, do not reserve a fixed share of underlying registry capacity, and do not replace rate-limiting at a trusted proxy or shared authority. The gateway does not implement certificate revocation checking by itself; production certificate issuance, rotation and revocation remain deployment responsibilities.
