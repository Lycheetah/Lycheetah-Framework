# Lycheetah mTLS Ingress — Hierarchical IPv6 Prefix Quotas v4.8

## Purpose

v4.7 grouped source addresses by a configurable IPv6 prefix, default `/64`. That blocks address rotation inside one prefix but lets a client use multiple `/64` prefixes to obtain independent per-prefix active slots. v4.8 introduces an **optional** second, broader aggregate cap.

Example test configuration: leaf `/64`, aggregate `/56`, maximum two active connections per `/56`. Sixteen distinct `/64` source buckets inside the same `/56` then share one two-connection aggregate ceiling. A different `/56` has a separate aggregate budget.

The broader cap is intentionally disabled by default. Prefix aggregation is a configurable traffic quota, not an identity or universal network-fairness boundary.

## Verify

```bash
./run_v4.8_tests.sh checks
./run_v4.8_tests.sh ingress
./run_v4.8_tests.sh coordinator
./run_v4.8_tests.sh quorum
./run_v4.8_tests.sh gateway
./run_v4.8_tests.sh all
```

The runner checks source fingerprints, compiles the local Python source, runs the paired v4.7/v4.8 differential probe, and executes the tests. Gateway tests are sharded to preserve process cleanup and reduce stress-case interference. Result logs list the exact counts.

## Configuration

Pass both `ipv6_aggregate_prefix_length` and `max_connections_per_ipv6_aggregate` to `SharedIngressQuotaStore` or `MTLSAnchoredRegistryHTTPServer`. Valid aggregate prefix is less specific than the leaf prefix (for example `/56` over `/64`); the aggregate limit must be a positive integer no larger than the global active cap. Both values must be configured together.

The shared SQLite configuration fingerprint is now schema 5 with `ipv6-prefix-hierarchy-v2` semantics. Old same-boot databases and replicas with differing settings fail closed; no implicit migration is performed.

## Scope limits

Local source-pinned reference artifact only—not upstream CI or production certification. The quota database is shared across same-host workers in the same Linux PID namespace. Application quotas act after TCP accept and do not prevent SYN floods, kernel backlog saturation or link saturation. A reverse proxy changes the direct socket peer; untrusted forwarded headers must never substitute for the socket peer.

No upstream source, branch or PR was changed, and no hosted service was called.
