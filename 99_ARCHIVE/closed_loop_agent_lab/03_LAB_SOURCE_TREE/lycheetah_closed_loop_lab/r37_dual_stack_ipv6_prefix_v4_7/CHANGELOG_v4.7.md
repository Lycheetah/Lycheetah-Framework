# Changelog v4.7

- Added configurable native IPv6 prefix quota identities (default `/64`) while preserving exact IPv4 `/32` identities and mapped-IPv4 normalization.
- Pinned prefix semantics and configured prefix length into the shared SQLite configuration fingerprint (schema 4) to make mixed-policy replicas fail closed.
- Extended explicit listener binding to IPv6 addresses, with wildcard/scoped link-local rejection and opt-in for non-loopback exposure.
- Fixed IPv6 Host authority formatting: HTTP authorities bracket IPv6 literals.
- Added a real IPv6-loopback mTLS gateway request test, prefix quota regression cases, preserved-v4.6 differential probe and deployment threat model.
- Full result count and limitations are recorded in `RESULTS_v4.7.md`.
