# Threat Model v4.6 — Attempt-Based Ingress Quotas

## Adversary and objective

An unauthenticated network client can repeatedly establish TCP connections and send no valid TLS/client identity. The adversary attempts to consume CPU, thread scheduling, SQLite admission work, or active connection slots before mTLS identity is known.

## v4.5 weakness reproduced

In v4.5, the active-slot and per-peer checks ran before global rate-token debit. With `max_active_connections=1` and a bucket capacity of two: (1) one connection reserves the slot and spends one token; (2) an additional connection is denied by active capacity but spends no token; (3) further active-limit denials also spend no token; (4) after the active slot releases, another request can be accepted using the preserved token.

The same ordering applied to per-IP quota rejections. This made the rate limit an admitted-success counter, not an attempt budget.

## v4.6 changes

- Debit the token before active and per-peer capacity checks in both the shared store and the gateway's process-local admission layer.
- Normalize IPv4-mapped IPv6 addresses to the IPv4 identity in the shared store and gateway local peer accounting.
- Bind semantics into the shared configuration string so a v4.5/v4.6 mix fails closed on the same boot.

## Expected property

For any request reaching the application admission gate, the global attempt token bucket is charged unless it is already empty. A request rejected by active/per-peer capacity therefore cannot leave budget available for a later request that was not charged.

## Out of scope

- SYN flood and traffic rejected before the application's process_request handler.
- Multi-host/distributed quotas or malicious local DB modification.
- IPv6 privacy-address rotation across a prefix. This revision does not implement prefix aggregation.
- Upstream source modification or deployment certification.
