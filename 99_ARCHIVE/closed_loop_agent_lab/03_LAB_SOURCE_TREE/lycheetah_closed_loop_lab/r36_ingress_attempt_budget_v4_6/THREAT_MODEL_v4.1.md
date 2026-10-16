# Threat Model v4.1 — Resource-Bounded mTLS Ingress

## Security objective

Prevent unauthenticated connection floods and slow handshakes/partial-header clients from spawning an unbounded number of gateway request threads or reaching registry mutation before transport identity and request authentication pass.

## New protections

1. Global active connection cap (default 32) applied before TLS handshake / worker thread creation.
2. Per-source-IP active connection cap (default 16).
3. Process-local global token bucket for new TCP connections (default burst 120, refill 2/s).
4. Bounded TCP listen backlog (default 64), TLS handshake timeout (3s), request socket timeout (10s) and inherited 128 KiB request body limit.
5. Rejected pre-handshake connections are closed without attempting to parse or authenticate application data.
6. Admission counters expose counts and configuration only; no IP addresses, request bodies or headers are emitted.

## Adversarial tests

- A held partial-header connection occupies one slot; an additional connection is closed before TLS handshake when configured concurrency is one.
- A separate per-IP cap rejects another connection even when the global cap has spare capacity.
- A one-token burst permits one valid request and rejects the next connection before TLS handshake; registry checkpoint sequence does not change from the rejected connection.
- A 24-client slow-header burst never exceeds a configured four active connections and does not mutate registry state.
- Invalid limits (Boolean where integer is expected, zero/negative limits, NaN timeout and per-IP greater than global) are rejected.
- Existing TLS identity, HMAC, strict framing, response signature, replay and four-witness quorum regressions are retained.

## Residual risks

- A single process-global token bucket can be exhausted by one source, so fairness and multi-tenant rate policy are not solved. Per-peer concurrent limits reduce but do not eliminate this.
- Unique-source distributed floods, slow system resource exhaustion outside the Python worker cap, kernel backlog pressure and TLS CPU saturation are not covered by this local experiment.
- `ThreadingHTTPServer` plus socket timeouts is not a complete production resource-control framework; registry logic and quorum RPCs may occupy a bounded worker for longer than the request's network read timeout.
- Four witness processes and the coordinator still share one host/administrator. This is not independent Byzantine fault tolerance.
- Certificate revocation, CA rotation, secret distribution, production deployment, real network topology and upstream CI are out of scope.

## Failure policy

When the gateway cannot admit a connection, it closes it before authentication. It does not try to make a registry decision or issue an unsigned fallback error. A rejected connection must not change challenge, request-replay or checkpoint state.
