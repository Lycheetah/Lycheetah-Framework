# Changelog v4.6

- Fix: pre-authentication rate tokens are charged for all attempts that reach the ingress admission gate, including attempts denied by active-slot or per-peer capacity.
- Fix: canonicalize IPv4-mapped IPv6 peers into the same IPv4 quota identity.
- Fix: use one direct-socket peer canonicalizer for local gateway reservation, shared-store reservation, and local release.
- Hardening: pin the new attempt-based semantics in shared configuration (`schema=3;rate_semantics=attempts-v1`) so v4.5 peers fail closed rather than silently sharing incompatible quota policy.
- Tests: add three shared-store regressions and two gateway regressions.
- Limits: still same-host SQLite; no distributed limiter, kernel-level SYN protection, IPv6 prefix quota, or upstream merge is claimed.
