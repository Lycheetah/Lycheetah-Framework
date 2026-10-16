# Threat Model v4.8 — IPv6 Prefix Rotation Across Subnets

## Asset and threat

The gateway protects bounded pre-authentication connection slots shared across same-host workers. A client may create many privacy addresses inside one `/64`, or rotate across multiple `/64` subnets in a delegated parent prefix, to obtain more per-peer active slots than intended.

## v4.7 baseline

v4.7 maps native IPv6 peers to a single configured prefix bucket (default `/64`). This stops arbitrary address rotation inside a `/64`; a client that can rotate across distinct `/64` buckets still obtains additional leaf slots, subject only to global active and global connection-attempt budgets.

## v4.8 mitigation

v4.8 adds an optional second-level IPv6 aggregate quota. With leaf `/64`, aggregate `/56`, and an aggregate active limit of two, the third active connection from a third `/64` within that `/56` is denied even though each address has its own leaf bucket. A different `/56` gets a separate aggregate bucket. The leaf and aggregate counters are checked and reserved in the same process-local lock or shared SQLite write transaction.

A local paired differential probe observes three `/64` addresses within one `/56`: v4.7 admits all three under a per-leaf limit of one; v4.8 with aggregate limit two admits the first two and denies the third, while admitting a peer from a different `/56`.

## Fairness and configuration risks

- Aggregate policy is optional and defaults off. `/56` is a test scenario, not a universal operational recommendation.
- Multiple customers may share a prefix, particularly behind an enterprise, hosting provider, VPN or network architecture with nonstandard allocations. Aggregate caps may cause collateral rejection.
- An attacker with multiple parent prefixes can still distribute requests; no finite source-IP prefix quota is a stable authenticated identity.
- IPv4 remains exact `/32`; this does not solve CGNAT fairness or IPv4 source rotation.
- Configuration changes alter accounting semantics. Schema 5 fingerprints all hierarchical settings so same-host replicas with different settings fail closed.
- The database is same-host/same-PID-namespace shared SQLite. It is not a distributed quota coordinator.

## Out of scope

The application attempt budget runs after TCP accept. It does not block SYN floods, stop listen backlog saturation before accept, or protect upstream links from raw traffic volume. Use edge, OS and infrastructure protections in a deployment-specific manner. A trusted proxy also changes the socket peer; arbitrary forwarding headers must not be used as a substitute for authenticated proxy identity.

## Evidence limits

This artifact uses local source derivatives, reference tests, a preserved local v4.7 baseline fixture and a deterministic differential probe. It is not upstream CI, public Internet load testing, penetration testing, or production certification. No upstream code was changed and no hosted service was contacted.
