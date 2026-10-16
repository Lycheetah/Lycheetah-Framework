# API Contract v4.7 — Absolute HTTP Socket Deadline

## Timeouts

- `handshake_timeout_seconds` bounds the TLS handshake through the Python/OpenSSL `do_handshake()` timeout. The paired partial-TLS-record probe found no behavior delta between v4.6 and v4.7.
- `request_timeout_seconds` is the per-I/O inactivity timeout after TLS.
- `request_deadline_seconds` is an absolute wall-clock watchdog for one HTTP exchange. If omitted, it defaults to `1.5 * request_timeout_seconds`. When it expires, the watchdog shuts down the socket even if the request handler is still inside dispatch or response writing.
- The request deadline must be finite and greater than or equal to the inactivity timeout.
- The coordinator quota lease TTL must exceed the request deadline; the shared-ingress quota lease TTL must exceed handshake timeout plus request deadline.

## Expiry behavior and limits

The watchdog bounds slow-drip transport occupancy during request-line/header/body parsing. It also closes the response transport if the clock expires during dispatch. **It does not cancel the Python handler or bound its execution time once dispatch has begun.** The server-side active slot remains reserved until that handler returns, and a client can lose the response while the mutation is still running or commits.

Accordingly, this is not a hard application-execution deadline or a distributed transaction guarantee. Mutations must be idempotent and recoverable, and upstream application operations may need their own cooperative deadline/cancellation and durable reconciliation.

## Threat model

Addressed: a TLS-completed peer trickling HTTP bytes frequently enough to avoid the socket inactivity timeout while retaining a connection/request slot.

Not addressed: kernel SYN floods, application computations that ignore socket closure, long-running business dispatches that occupy a handler after the socket deadline, multi-host quotas, or distributed commit semantics.
