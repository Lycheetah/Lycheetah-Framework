# Threat Model v4.4 — Shared Pre-TLS Ingress Quotas

## Problem addressed

With process-local caps, multiple gateway replicas each receive their own global active-connection and connection-rate allowance. A same-host process fleet can therefore multiply its unauthenticated ingress budget. v4.4 adds a shared local SQLite authority before TLS begins.

## Adversary and failure scenarios

- A client fans connections across several gateway instances on one host.
- A single peer IP distributes connections across instances to evade per-instance limits.
- Gateways restart while connection-rate tokens should persist in the current OS boot.
- Two processes race to acquire the last global slot.
- The SQLite path is a symlink, parent is writable by group/world, DB fails, or replicas disagree on quotas.
- OS reboot invalidates persisted monotonic timestamps.
- A live handler pauses longer than the lease TTL then resumes after another instance has reclaimed the slot.

## Controls

- Global active leases, per-IP counts, and shared rate token update happen inside a single `BEGIN IMMEDIATE` transaction.
- Reservation happens in the server's `process_request` before request thread creation/TLS handshake; a denial closes the accepted socket.
- Lease renewal uses a background heartbeat; lease release runs when request processing ends.
- Boot ID mismatch clears stale leases/rate state; config mismatch fails closed.
- Database path and parent directory restrictions reduce accidental path redirection and untrusted local modifications.
- Existing local process caps remain enabled as a second layer.

## Residual risk

A lease TTL is not a complete fencing mechanism. If a gateway handler is paused beyond its TTL and later resumes, local SQLite cannot forcibly cancel downstream work or stop the resumed thread. The TTL is required to exceed normal handshake and request socket timeout budgets, but Python socket timeouts do not provide a hard cancellation bound for arbitrary server-side logic. Strong fencing requires downstream participants to validate a monotonic epoch or a different ownership protocol. The feature covers only processes on one host sharing the exact database file. Trusted local admin/process access to the DB remains in the trusted computing base.
