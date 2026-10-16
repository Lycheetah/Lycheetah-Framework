# Upstream Integration Plan v3.8

No branch or upstream file has been changed.

1. Preserve the current upstream base commit and verify source fingerprints before applying any changes.
2. Keep the HTTP witness client behind an experimental feature flag; preserve the current direct reference implementation until parity is demonstrated.
3. Introduce a transport protocol type for `head_report`, `attest`, and `get_checkpoint` rather than relying on ad hoc duck typing long term.
4. Run the existing registry, nonce, clock, policy, schema, package-install, CLI and all retained v3.7 tests.
5. Add a subprocess transport matrix: one node down, two down, server restart, lost response after commit, replayed RPC, invalid HMAC, clock skew, wrong witness identity, and corrupt response payload.
6. Build a dedicated witness-service package with TLS/mTLS, per-client authorization, external secret management, process supervision, health checks, rate limits and schema migrations.
7. Deploy witnesses to separate failure/admin domains and exercise backup restoration of one store, two stores, client anchor, registry store, and all but one trust domain.
8. Define operator procedures for quorum loss, stale witness recovery, key rotation, and coordinated rollback before real data is entrusted to it.

## Promotion gate

Promotion requires full upstream CI, packaging and cross-platform tests, external service integration tests, an independently reviewed trust-domain design, verified secrets/backup independence, and reproducible rollback/equivocation exercises. The current localhost process prototype satisfies none of the independent-deployment requirements by itself.
