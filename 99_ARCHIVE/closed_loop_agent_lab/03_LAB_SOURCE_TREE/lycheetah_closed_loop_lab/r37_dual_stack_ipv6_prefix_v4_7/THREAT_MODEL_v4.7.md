# Threat Model v4.7 — Native IPv6 Peer Rotation

## Target

An unauthenticated network client reaches the mTLS gateway over IPv6 and rotates its source address within a delegated subnet, for example SLAAC/privacy addresses under one `/64`, in an attempt to multiply the active-connection quota formerly associated with one exact IPv6 address.

## Baseline weakness

The preserved v4.6 store keys native IPv6 leases by exact compressed address. Two distinct addresses in the same `/64` therefore appear to be different quota identities and can each obtain a slot under a per-IP limit of one.

## v4.7 control

- Native IPv6 peers map to the configured network prefix, default `/64`.
- Exact IPv4 and IPv4-mapped IPv6 forms share an IPv4 `/32` identity.
- The gateway's process-local and shared SQLite quotas use the same canonical bucket.
- Prefix length and semantics are pinned into the store's shared configuration so replicas with divergent policies fail closed.
- The gateway can bind an explicit IPv6 loopback or non-loopback address, preserving the explicit opt-in for non-loopback exposure.
- IPv6 Host authorities are bracketed before exact Host-header comparison; the real IPv6 mTLS request is a regression case.

## Trade-offs

- Clients sharing an IPv6 `/64` share a per-peer active bucket. That can penalize multi-tenant networks or enterprise clients.
- Aggregation by `/64` does not stop attackers who can rotate across multiple routed prefixes. Changing the prefix size changes the operational fairness/security trade-off and should be pinned consistently across replicas.
- IPv4 still uses exact `/32` per-peer quotas; CGNAT clients may share one bucket, and IPv4 address rotation has different characteristics.
- A trusted reverse proxy becomes the direct socket peer. Forwarded client-IP data is usable only with an explicit proxy trust boundary and authentication/transport protection; untrusted headers must never influence this key.

## Remaining DoS boundaries

The application attempt budget runs after TCP accept. It does not count SYN packets, stop SYN floods, constrain the kernel listen backlog before accept, or defend upstream links/firewalls from traffic-volume attacks. Production needs network-edge controls appropriate to deployment (for example a managed load balancer, firewall/rate-control rules and OS TCP backlog/SYN protections) plus monitoring and capacity testing.

## Verification scope

Tests cover deterministic IPv4/IPv4-mapped identity, native IPv6 prefix grouping, same-host SQLite semantics, explicit IPv6 listener binding and a local mTLS request. They are not a public Internet load test, cloud deployment test, or production DoS certification.
