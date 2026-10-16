# Threat Model v4.7 — Slow-Drip HTTP Deadline Enforcement

## Adversary

A TLS-completed peer sends partial HTTP request-line, header, or body bytes at intervals smaller than the socket inactivity timeout. The peer may possess a client certificate but still fail application principal authorization; the deadline is a resource bound, not an identity control.

## Previous behavior

The inherited gateway relied on socket inactivity timeout while `BaseHTTPRequestHandler` parsed the request line and headers using buffered reads. A peer could trickle partial HTTP bytes within the idle timeout and keep a slot active well beyond one idle interval. In a paired local probe, v4.6 still had its connection active after about 1.2–1.5 seconds of drip input.

## v4.7 control

A daemon watchdog enforces a wall-clock socket deadline for each HTTP exchange. In the latest paired probe v4.6 had one active slot at 1.227 seconds; v4.7 had released it at 0.971 seconds. The existing Python/OpenSSL handshake timeout remains unchanged; the tested partial TLS record was already bounded by v4.6.

## Tests

- Paired local v4.6/v4.7 slow-drip header probe.
- mTLS peer trickles an HTTP request-header line within the inactivity timeout; v4.7 closes it and no registry mutation occurs.
- mTLS peer trickles an incomplete body within the inactivity timeout; v4.7 closes it and no registry mutation occurs.
- Retained partial-TLS-record control proves existing handshake timeout behavior without claiming a v4.7 delta.
- Retained quota, coordinator, quorum, and gateway lifecycle suites pass locally.

## Limits

- Timer closure interrupts socket I/O but cannot preempt arbitrary Python application code. It does not bound a handler's CPU/remote-RPC wait once dispatch has begun, and an already-started side effect may complete after the client loses its response.
- Application operations need idempotency and durable reconciliation.
- Rate-limit budget begins after TCP accept; this does not stop SYN floods.
- SQLite quota scope is same-host / same PID namespace.
- This is a local reference artifact, not an upstream merge or deployed production service.
