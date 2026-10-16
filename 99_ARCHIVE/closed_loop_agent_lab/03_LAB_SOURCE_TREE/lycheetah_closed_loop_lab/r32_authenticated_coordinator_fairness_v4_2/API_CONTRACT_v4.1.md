# Lycheetah mTLS Registry Gateway API Contract v4.1 — Bounded Admission

## Scope

v4.1 retains the v4.0 mTLS coordinator ingress, URI-SAN allowlisting, HMAC request authentication, signed responses and quorum-guarded registry dispatcher. It adds bounded connection admission before TLS handshake.

This is an executable local reference implementation, not a production daemon.

## Admission defaults

- Maximum simultaneously admitted connections: **32**.
- Maximum active connections from one observed TCP peer IP: **16**.
- Global process-local connection token bucket: **120 new connections per minute**, with an initial burst capacity of 120 and continuous refill at 2 tokens/second.
- Listen backlog: **64**.
- TLS handshake timeout: **3 seconds**.
- Request socket timeout: **10 seconds**.
- HTTP body limit: **128 KiB** (inherited from v4.0).

Admission is reserved in the server's accept path before a per-connection worker thread is created and before the TLS handshake. If any limit is exhausted, the server closes the connection without an HTTP response; no TLS identity or HTTP request can be trusted yet. Slots are released in the worker's `finally` path after the request handler ends.

## HTTP/API behavior retained

The only exposed request methods/routes remain POST to `/v1/challenges` and `/v1/challenges/{nonce}/consume`. TLS 1.2+ and required client cert validation remain in force, followed by exact coordinator URI-SAN allowlisting. Existing HMAC authentication and signed response envelope checks are unchanged.

## Operational limits

- The connection token bucket is process-local and global, not distributed. A single peer can consume its burst; it does not provide fairness among authenticated identities.
- Per-IP limits use the direct socket peer address. Proxy-forwarded IP headers are not trusted or parsed.
- This is not DDoS protection against distributed sources. Use an upstream load balancer/firewall with connection quotas, an identity-aware rate limiter and network controls in production.
- Resource tests run on one host with ephemeral test certificates and four local witness processes. Independent hosts/admins, production CA rotation/revocation, global worker quotas, OS resource limits and upstream CI remain unvalidated.
