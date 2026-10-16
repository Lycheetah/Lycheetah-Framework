# Lycheetah mTLS Gateway v4.7 — Absolute HTTP Socket Deadline

This branch adds an absolute wall-clock **socket deadline for HTTP exchanges** to the v4.6 attempt-based ingress quota design. Its measured contribution is narrow: a client that trickles an HTTP request line/header/body below the inactivity timeout no longer holds the connection slot indefinitely just by keeping bytes arriving.

## Run

```bash
./run_v4.7_tests.sh checks
./run_v4.7_tests.sh ingress
./run_v4.7_tests.sh coordinator
./run_v4.7_tests.sh quorum
./run_v4.7_tests.sh gateway
```

Run suite groups sequentially. The gateway group starts four local witness processes and tests shared append-only state.

## Timeout contract

- `handshake_timeout_seconds`: the existing Python/OpenSSL TLS handshake timeout; no new handshake improvement is claimed.
- `request_timeout_seconds`: per-I/O inactivity timeout.
- `request_deadline_seconds`: absolute socket deadline, defaulting to `1.5 * request_timeout_seconds`.
- Coordinator quota lease TTL must exceed the request deadline; shared-ingress quota lease TTL must exceed handshake plus request deadline.

## What it does not promise

The watchdog closes the transport socket. It cannot preempt a Python handler already waiting inside application or quorum logic, nor does it undo an effect that has already begun. A slow dispatch can outlive the socket deadline, and a client may lose the response while the mutation still completes. Durable idempotency, cooperative application deadlines and reconciliation remain necessary.

This is a local reference branch, separate from the v4.8 hierarchical IPv6 aggregate-quota work. No upstream source was changed, no PR was opened, and no hosted service was called.
