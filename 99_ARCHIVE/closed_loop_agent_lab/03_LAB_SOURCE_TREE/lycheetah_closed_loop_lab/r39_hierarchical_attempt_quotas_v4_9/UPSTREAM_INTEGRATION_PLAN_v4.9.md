# Upstream Integration Plan v4.9

1. Review the new optional settings and their operational effects with the target deployment; leave peer and aggregate attempt caps disabled until measured.
2. Apply only to a clean non-default branch after a fresh full checkout and source review. The local code is a source-pinned derivative, not asserted byte-identical to upstream.
3. Confirm configuration migration: schema-6 fingerprint `hierarchical-attempts-v1` intentionally fails closed when a same-boot DB or replica still uses schema 5. Plan a backup, explicit reset/migration and rollback procedure.
4. Run all store, coordinator, checkpoint quorum and gateway lifecycle tests in upstream CI; include Python/Linux versions actually deployed.
5. Run load tests with real IPv4/NAT populations, IPv6 privacy-address rotation within `/64`, multiple `/64`s within the configured aggregate, and unrelated aggregates. Measure false rejection and SQLite write contention.
6. Use a deployment-specific policy for prefix sizes and cap values. Do not treat IP prefixes as authenticated identities or assume a `/56` or `/64` has universal ownership semantics.
7. Keep edge/OS/SYN flood controls; this rate limiter operates after accept.
8. Independent review and upstream CI are required before production. No upstream file, branch or PR was changed in this artifact pass due the previously observed GitHub integration HTTP 403.
