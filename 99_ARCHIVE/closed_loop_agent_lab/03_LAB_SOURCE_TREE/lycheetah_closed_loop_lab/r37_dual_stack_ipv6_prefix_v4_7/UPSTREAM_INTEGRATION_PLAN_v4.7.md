# Upstream Integration Plan v4.7

1. Apply the changes on a clean non-default branch after confirming the exact base commit and unchanged working tree.
2. Review the public API choice: whether `max_connections_per_ip` should be deprecated in favor of `max_connections_per_peer_bucket`, keeping backwards compatibility in the initial release.
3. Add schema/configuration migration notes. Existing shared-ingress databases use a different semantic fingerprint and should fail closed until operators deliberately reinitialize or migrate them; do not silently reinterpret live rows.
4. Run the full existing model/gateway/quorum suite on Linux with IPv6 loopback available and in an IPv6-disabled runner, where the integration test should be explicitly skipped.
5. Add deployment tests for IPv6 behind the actual load balancer/reverse proxy. Verify the direct peer semantics and never accept unauthenticated `X-Forwarded-For` as the quota key.
6. Load test IPv4 and IPv6 listeners through the intended edge stack, including one source `/64` with many privacy addresses and many independent prefixes. Measure unfair sharing, rejection rates, DB write latency and kernel backlog behavior.
7. Establish OS/network-layer SYN protections separately; application connection quotas do not cover pre-accept traffic.
8. Run upstream CI and review before merging. No branch/PR was created in this research pass because GitHub branch creation previously returned HTTP 403.
