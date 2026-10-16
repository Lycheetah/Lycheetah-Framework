# API Contract v4.8 — Hierarchical IPv6 Ingress Quotas

## Existing leaf bucket

`canonical_peer_identity(peer_ip, ipv6_prefix_length=64)` remains the first-level quota key:

- IPv4 and IPv4-mapped IPv6 addresses normalize to one `ipv4:<address>/32` bucket.
- Native IPv6 addresses map to the configured leaf prefix, default `/64`.
- The input must be a numeric direct socket peer. This helper must never be fed an untrusted forwarded-IP header.

## Optional aggregate bucket

`canonical_peer_aggregate_identity(peer_ip, ipv6_aggregate_prefix_length)` creates an additional bucket for native IPv6 peers only. IPv4 and IPv4-mapped addresses return no aggregate bucket.

`SharedIngressQuotaStore` and `MTLSAnchoredRegistryHTTPServer` accept the paired optional settings:

```python
ipv6_aggregate_prefix_length: int | None = None
max_connections_per_ipv6_aggregate: int | None = None
```

Both values must be set together or both omitted. When enabled:

- `ipv6_aggregate_prefix_length` must be an integer from `/32` through a prefix **less specific than** the leaf prefix (numerically lower than `ipv6_prefix_length`).
- `max_connections_per_ipv6_aggregate` must be a positive integer no larger than the gateway's configured global active-connection ceiling.
- Every native IPv6 lease consumes its leaf bucket and aggregate bucket atomically.
- The aggregate bucket has an independent active-connection ceiling and is accounted/released with the lease.
- The reason `ipv6-aggregate-connection-limit` indicates that the wider configured bucket is full.

The broader cap is disabled by default because no prefix size is universally fair across ISPs, corporate networks, VPNs and multi-tenant hosts. Operators must pick a prefix and limit from deployment measurements. The exact bucket prefix and limit enter the shared-store configuration fingerprint.

## Persistence and replica contract

The shared ingress configuration fingerprint is schema 5 and identifies `peer_semantics=ipv6-prefix-hierarchy-v2`. Any same-boot replica using old schema/semantics or differing aggregate configuration fails closed. There is no implicit migration of existing SQLite databases: operators must perform a reviewed migration or deliberate reinitialization.

A shared `shared_ingress_lease_aggregate` mapping tracks leases using the same transaction as the base lease. The foreign key uses `ON DELETE CASCADE`; normal close, dead-owner reclamation and boot-change cleanup remove aggregate usage together with the lease.

## Explicit limitations

This is a quota key, not a client identity or a complete denial-of-service defence. A broader prefix can group unrelated legitimate clients; a client able to rotate across broader prefixes can still distribute load. TCP SYN/backlog, network-link saturation and upstream edge protection remain outside this application-level limiter.
