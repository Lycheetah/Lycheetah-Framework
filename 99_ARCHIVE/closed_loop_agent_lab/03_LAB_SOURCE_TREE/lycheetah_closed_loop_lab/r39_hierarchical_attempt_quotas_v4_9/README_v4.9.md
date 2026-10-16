# Lycheetah mTLS Ingress — Hierarchical Attempt-Rate Quotas v4.9

## Summary

v4.8 added optional aggregate IPv6 active-connection quotas across many leaf `/64` buckets. v4.9 adds **optional hierarchical attempt-rate buckets** so a single noisy source bucket cannot consume the entire shared global rate budget before an unrelated source gets a chance.

The attempt-rate hierarchy is:

1. Optional canonical peer bucket: IPv4 `/32` or configured IPv6 leaf prefix (default `/64`).
2. Optional native-IPv6 aggregate bucket when the existing wider IPv6 prefix configuration is enabled.
3. Existing shared global attempt budget.
4. Existing global, leaf-peer, and optional aggregate active-connection ceilings.

All enabled rate buckets and the global bucket are refilled/consumed in one SQLite write transaction. Attempts denied by a peer/aggregate bucket do **not** consume a global token; requests that pass these tiers consume a global token before active-slot checks, preserving the prior active-denial semantics.

## Focused differential result

A preserved local v4.8 implementation and the v4.9 code are run with a global rate budget of five attempts/minute. One IPv4 peer makes eight rapid attempts, then an unrelated peer tries once:

- v4.8 global-only baseline: the noisy peer consumes all five global tokens; the unrelated peer is rejected.
- v4.9 with a peer cap of two: two noisy-peer attempts pass and six are rejected by its own bucket; the unrelated peer is accepted; the post-admission snapshot shows about two global tokens remaining (minor refill affects the fractional value).

See `differential_probe_v4.9.json` for machine-readable output. This is a deterministic local store experiment, not a network load test.

## Configuration

`SharedIngressQuotaStore` accepts the optional settings:

```python
max_new_connections_per_peer_per_minute: int | None = None
max_new_connections_per_ipv6_aggregate_per_minute: int | None = None
rate_bucket_idle_ttl_seconds: float = 600.0
max_rate_buckets: int = 50000
```

The aggregate attempt-rate cap requires the wider IPv6 aggregate prefix to be enabled. Both attempt caps are disabled by default to avoid silently imposing a new traffic policy. The ingress gateway exposes these settings only with `shared_ingress_quota_db_path` configured; the shared SQLite store provides same-host cross-process agreement.

Attempt-rate bucket state is bounded. Stale rows are pruned when a new bucket needs space; if a new bucket would exceed `max_rate_buckets`, the request fails closed with `attempt-bucket-capacity`. Choose the bound from real traffic cardinality and monitor the aggregate bucket count.

## Verify

```bash
./run_v4.9_tests.sh checks
./run_v4.9_tests.sh ingress
./run_v4.9_tests.sh coordinator
./run_v4.9_tests.sh quorum
./run_v4.9_tests.sh gateway
./run_v4.9_tests.sh all
```

The runner validates local artifact fingerprints, compiles Python sources, runs the v4.8/v4.9 differential, and executes the full test matrix including gateway lifecycle shards.

## Scope and limits

- IP prefixes are quota keys, not authenticated identity. IPv4 `/32` can group NAT/CGNAT users; IPv6 prefix policy can group unrelated clients.
- Peer and aggregate rate caps are opt-in and require deployment-specific fairness and false-rejection testing.
- The global shared quota and peer buckets are SQLite-based for same-host workers in the same Linux PID namespace, not a distributed quota service.
- The application limiter runs after TCP accept. It does not stop SYN floods, saturate-link attacks, or replace edge/OS network controls.
- Local source hashes pin this artifact, not exact byte identity with upstream. No upstream branch, source, or PR was changed; no hosted service was called.
