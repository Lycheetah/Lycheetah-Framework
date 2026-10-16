# Lycheetah mTLS Ingress — IPv6 Prefix Quotas v4.7

## Summary

v4.7 extends the v4.6 local reference gateway to accept an explicitly configured numeric IPv4 **or** IPv6 listener address. Native IPv6 socket peers are assigned a configurable prefix bucket (default `/64`) for active-connection quota accounting. IPv4 continues to use exact `/32` identities; IPv4-mapped IPv6 addresses normalize to the same IPv4 identity. The HTTP Host authority formatter now brackets IPv6 literals as required by HTTP authority syntax.

The shared SQLite store pins prefix length and bucket semantics in its configuration fingerprint; same-boot peers with incompatible quota policy fail closed rather than silently sharing a database with different counting semantics.

## Main changes

- `shared_ingress_quota.py`: `canonical_peer_identity()`, default IPv6 `/64` grouping, configurable prefix length from `/32` through `/128`, shared config schema 4 and peer-semantics fingerprint.
- `registry_gateway_mtls.py`: IPv4/IPv6 explicit-address binding, IPv6 prefix buckets in the process-local admission counters, shared prefix configuration, and correctly bracketed IPv6 Host authority validation.
- `test_shared_ingress_quota.py`: rotated IPv6-address, distinct-prefix, configuration mismatch, invalid prefix and existing attempt-budget regressions.
- `test_remote_witness_process.py`: real IPv6 loopback mTLS request, Host authority check, local quota grouping and IPv4-mapped alias behavior.
- `differential_probe_v4.7.py`: runnable comparison against the preserved local v4.6 source fixture.

## Verify

```bash
./run_v4.7_tests.sh all
```

## Scope and limitations

Local reference artifact only—not upstream CI or production certification. IPv6 binding is explicit-address-only: wildcard and scoped link-local IPv6 literals are rejected, and non-loopback binds require explicit opt-in. The listener still charges the global attempt token only after TCP accept and cannot defend against SYN floods or upstream network saturation. Native IPv6 prefix aggregation is a quota heuristic; shared users inside one prefix may share a bucket, and an attacker controlling multiple routed prefixes may still rotate between buckets. A reverse proxy makes the proxy the direct socket peer; do not trust arbitrary forwarded-IP headers as an identity substitute.

The store is local SQLite shared by same-host processes in the same Linux PID namespace. The base code and tests are locally pinned derivatives/fixtures, not asserted byte-identical to upstream. No upstream source, branch or PR was changed, and no hosted service was called.
