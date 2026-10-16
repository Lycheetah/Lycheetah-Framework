# API Contract v4.9 — Hierarchical Attempt-Rate Quotas

## New optional store settings

- `max_new_connections_per_peer_per_minute`: optional positive integer no larger than the global attempt-rate capacity. The key is the existing canonical peer quota bucket, not a verified person or device.
- `max_new_connections_per_ipv6_aggregate_per_minute`: optional positive integer no larger than global capacity. Requires the existing `ipv6_aggregate_prefix_length` + `max_connections_per_ipv6_aggregate` configuration pair.
- `rate_bucket_idle_ttl_seconds`: finite number of at least 60 seconds. A bucket can be deleted after this idle window because its full refill period has elapsed under the per-minute token model.
- `max_rate_buckets`: positive integer cap on peer and aggregate attempt-rate rows together.

The gateway options are `max_new_connections_per_peer_per_minute`, `max_new_connections_per_ipv6_aggregate_per_minute`, `ingress_rate_bucket_idle_ttl_seconds`, and `max_ingress_rate_buckets`. The two tiered caps require `shared_ingress_quota_db_path`; otherwise construction fails closed.

## Admission ordering

1. Canonicalize the numeric direct socket peer; do not trust forwarding headers.
2. Begin a shared SQLite write transaction and verify pinned configuration.
3. Refill/check enabled peer and IPv6 aggregate rate buckets.
4. If a tiered bucket is exhausted, persist only existing bucket refill metadata and reject; do not spend a global token or insert new bucket rows for this denied request.
5. Check/refill the global rate bucket. If depleted, reject without spending tiered tokens or creating missing rows.
6. Consume global and all configured tiered tokens atomically.
7. Apply global active, leaf active and aggregate active ceilings; active-limit denials still consume the rate tokens as in the prior attempt semantics.
8. Insert a connection lease and aggregate mapping in the same transaction.

## Failure and state bounds

- Configuration mismatch, store errors, or PID-identity mismatch fail closed.
- If the attempt-bucket row cap remains full after stale-row cleanup, a new bucket key is rejected with `attempt-bucket-capacity`.
- Replica configuration fingerprints move to schema 6 / `hierarchical-attempts-v1`. There is no implicit migration of schema-5 databases.
- Snapshot output includes only bucket counts and configured cap values; it does not expose source addresses.

## Non-guarantees

Rate limits after TCP accept do not protect the kernel accept backlog or upstream network. Prefix-based rate controls are heuristics, can have collateral effects for shared IPs, and are bypassable by distribution across independent prefixes. The global budget remains necessary to bound the aggregate admitted attempt rate.
