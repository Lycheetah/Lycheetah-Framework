# Changelog v4.9

- Added optional shared per-peer attempt token buckets using the canonical leaf peer key.
- Added optional native-IPv6 aggregate attempt buckets keyed by the configured wider prefix.
- Enforced the rate hierarchy atomically with the global rate bucket and active-slot reservation in one SQLite write transaction.
- Ensured attempts denied by a peer or aggregate attempt bucket do not consume global tokens or create unnecessary new bucket rows.
- Added a configured hard cap and idle-expiry pruning for per-source rate state; new state fails closed when the cap remains full.
- Pinned the new configuration/semantics in schema 6 and fail closed across mixed old/new configurations; no implicit DB migration.
- Wired optional settings through the mTLS gateway, only when shared ingress storage is enabled.
- Added baseline-v4.8 vs v4.9 differential probe, validation cases, state-cap tests, same-leaf normalization, aggregate shared-cap concurrency, and gateway wiring coverage.
