# Threat Model v4.9 — One Source Exhausting the Global Attempt Budget

## Asset

Preserve pre-authentication ingress capacity so one source bucket cannot monopolize the gateway's shared connection-attempt budget before other peers can obtain admission.

## Baseline weakness in the local v4.8 model

The shared store has one global token bucket. Each attempt admitted to the quota store consumes a global token before active/per-peer connection decisions. A single high-rate source can therefore spend all global tokens and force unrelated source attempts to be denied by `connection-rate-limit`.

This global ceiling is useful against aggregate load; removing it would be wrong. The weakness is that there is no independent source budget before the shared global bucket.

## v4.9 mitigation

Optional per-canonical-peer and broader IPv6 aggregate token buckets run before the global bucket. If an enabled source tier is exhausted, that request is rejected without spending a global token. Eligible attempts then spend a token from every enabled tier and the global bucket in a single `BEGIN IMMEDIATE` SQLite transaction. Active-limit denials still spend these tokens, preserving the baseline's anti-hammering behavior for requests that pass source-rate checks.

Rate-bucket rows are bounded by `max_rate_buckets`, and stale state is reclaimed only after its idle window. If the store cannot track a new key safely, it fails closed rather than evicting a recently active bucket and resetting its budget.

## Verified local counterexample

The v4.8 global-only fixture admits five attempts from one IPv4 peer, consumes its shared rate bucket, and rejects the next unrelated peer. With v4.9 peer limit two, the same flood admits two, rejects six at the peer tier, and leaves enough global tokens for another peer. A concurrent 32-address IPv6 test with one `/56` aggregate attempt cap observes exactly the configured number of successful admissions.

## Risks and trade-offs

- IPv4 `/32` may represent a household, enterprise, VPN or CGNAT population; an aggressive cap may reject legitimate users.
- IPv6 `/64` and broader aggregate prefixes are network configuration choices, not identity boundaries.
- A malicious client can distribute attempts across multiple independent source prefixes; the global ceiling and edge controls still matter.
- The finite row cap can cause fail-closed denial of new peers during an address-cardinality burst until stale rows are eligible for pruning.
- SQLite is same-host/same-PID-namespace infrastructure; it is not a multi-host global limiter.
- The app sees requests after TCP accept and cannot mitigate SYN floods or saturation upstream of the process.

## Evidence boundary

The result is based on local reference code, a preserved local v4.8 baseline fixture, unittest, and a deterministic differential probe. It is not a public traffic test, upstream CI, or production certification. No upstream branch or source was changed.
