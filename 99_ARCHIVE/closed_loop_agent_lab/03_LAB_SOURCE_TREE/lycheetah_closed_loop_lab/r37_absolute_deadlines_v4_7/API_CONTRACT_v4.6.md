# API Contract v4.6 — Ingress Attempt Budget

## `SharedIngressQuotaStore.reserve(peer_ip)`

- Validates a literal IP address and canonicalizes IPv4-mapped IPv6 addresses to their IPv4 identity.
- Under one `BEGIN IMMEDIATE` transaction, prepares state and debits the global connection-attempt token bucket **before** checking active global/per-peer capacity.
- Therefore attempts rejected because active or per-peer capacity is exhausted still spend a token.
- If no token is available, returns `connection-rate-limit` without attempting an active reservation.
- On a successful admission, persists the owner-bound lease as before.
- Returns `(lease, None)` on success; `(None, reason)` on quota denial.

## Gateway local admission

- Uses a canonical direct socket peer; no forwarded header participates in pre-TLS identity.
- Debits the local rate bucket before active and per-peer checks.
- Uses the same identity form for reserve and release, so IPv4 and IPv4-mapped IPv6 strings cannot become distinct local buckets.

## Configuration compatibility

The shared-store config includes `schema=3` and `rate_semantics=attempts-v1`. A same-boot store using a different config fails closed. No implicit database migration is performed. Operators should coordinate the version change rather than mixing v4.5 and v4.6 processes against one database.

## Scope

Rate is charged when the TCP connection has been accepted and reaches application `process_request`, not at SYN time. A kernel firewall, load balancer or network-level DDoS filter is still needed for floods that never reach this process. The DB and parent directory remain trusted same-host infrastructure.
