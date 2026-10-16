# Upstream Integration Plan v4.8

1. Review the optional public API: `ipv6_aggregate_prefix_length` and `max_connections_per_ipv6_aggregate` are paired; leave them disabled by default until a target deployment chooses an explicit policy.
2. Apply changes only on a clean non-default branch after inspecting exact upstream source and current tests. The current local modules are source-pinned derivatives, not asserted byte-identical to upstream.
3. Resolve the database migration strategy before deployment. Schema 5 and hierarchical peer semantics deliberately reject older same-boot database configurations; do not silently alter a live store's counting model.
4. Run unit/model/gateway/quorum regressions on Linux with IPv6 available and in a runner where IPv6 loopback is unavailable; IPv6 integration tests should skip only with an explicit reason.
5. Add deployment-specific load tests using the real edge/load balancer. Measure fairness, false rejection, SQLite write contention and connection-slot distribution for actual delegated prefixes before enabling aggregate limits.
6. Confirm direct socket peer semantics at the real proxy boundary; never accept untrusted `X-Forwarded-For` as the canonical peer.
7. Validate the deployment's network/SYN protection separately; application quotas apply after accept.
8. Run upstream CI and independent review before promotion. No upstream branch/PR was created in this artifact pass due prior GitHub integration HTTP 403.
