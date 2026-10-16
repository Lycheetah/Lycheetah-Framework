# Changelog v4.1 — Bounded mTLS Ingress

- Added a pre-TLS admission gate so unauthenticated connections cannot create an unbounded number of request worker threads.
- Added configurable global active-connection limit, direct-peer active limit, process-local token bucket for new connections, and bounded listen backlog.
- Added strict validation for limit values and timeouts; booleans are rejected where positive integers are required.
- Added an admission snapshot exposing aggregate counters only; no peer IP or request data is emitted.
- Added tests for active-slot rejection, per-IP rejection, global burst limit, 24-client slow-header burst, invalid config and unchanged registry state under rejected connections.
- Retained v4.0 mTLS, URI-SAN, HMAC, response-signature, framing, replay, remote witness and quorum suites.
- Explicitly documents global-bucket fairness/DoS limits and need for upstream identity-aware rate control.
- No hosted services called; no upstream source or CI changes.
