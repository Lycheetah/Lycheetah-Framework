# Lycheetah Shared Ingress Quota v4.6

## Summary

v4.6 changes the pre-authentication connection budget from a successful-reservation counter into an **attempt budget**. Every accepted TCP connection reaching the admission gate spends a global rate token before active/per-peer quotas are checked. This prevents requests rejected by a saturated active slot or per-peer limit from hammering those paths without consuming the shared rate budget.

The peer canonicalizer now maps IPv4-mapped IPv6 forms to the same IPv4 identity (`192.0.2.44` and `::ffff:192.0.2.44`). The gateway's process-local quota and shared ingress store use the same canonical identity for reservation and release.

## Why it matters

The v4.5 baseline could accept one connection with a two-token bucket, reject arbitrarily many subsequent requests with `active-connection-limit` without spending the remaining token, then accept another after the slot freed. v4.6 charges the over-limit attempt; later attempts return `connection-rate-limit` until refill. The same principle applies to per-IP denials.

## Files

- `shared_ingress_quota.py`: shared SQLite store, now pins `rate_semantics=attempts-v1` and logical schema 3 in shared configuration; mismatched replicas fail closed.
- `registry_gateway_mtls.py`: direct peer canonicalization and matching local attempt-budget semantics.
- `test_shared_ingress_quota.py`: adversarial regressions for active-limit debits, per-IP-limit debits, and IPv4-mapped IPv6 canonicalization.
- `test_remote_witness_process.py`: gateway-level attempt budget and canonical peer regressions.
- `run_v4.6_tests.sh`: reproducible test runner.

## Verify

```bash
./run_v4.6_tests.sh all
```

## Scope and limitations

This is a local reference artifact using Linux `/proc` and a trusted same-host SQLite file. It is not upstream repository CI or production certification. The gateway in this revision binds a numeric IPv4 listener, so the IPv4-mapped form regression exercises the generic quota store and the shared canonicalization helper rather than demonstrating a remotely reachable bypass on the current IPv4-only listener. Prefix-based IPv6 rate limiting is not implemented. No hosted services were called and no upstream code was changed.
