# Pack Manifest v4.9

Artifact: Hierarchical Attempt-Rate Quotas for Lycheetah mTLS Ingress
Parent artifact: v4.8 — Hierarchical IPv6 Prefix Quotas
Observed upstream context commit: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`

## Changed components

- `shared_ingress_quota.py`: schema-6 config fingerprint, optional canonical-peer and IPv6-aggregate token buckets, bounded state table, stale bucket pruning, and shared transaction ordering.
- `registry_gateway_mtls.py`: optional configuration pass-through, validation that tiered limits require the shared quota store, and operational snapshot exposure.
- `test_shared_ingress_quota.py`: peer flood isolation, IPv6 leaf/aggregate semantics, invalid config, row-cap behavior, stale-row pruning, a 16-thread rate-limit race, and an aggregate bucket-churn guard.
- `test_remote_witness_process.py`: gateway setting wiring, monitoring and malformed-setting coverage.
- `shared_ingress_quota_v4_8_baseline_fixture.py` and `differential_probe_v4.9.py`: paired experiment comparing the global-only v4.8 local fixture to v4.9.
- `run_v4.9_tests.sh`, `run_gateway_suite_v4.9.py`, `verify_source_pins_v4.9.py`: repeatable test and source-check runner.

## Expected complete suite matrix

- Shared ingress quota: 42 test methods.
- Shared coordinator quota: 13 test methods.
- Registry checkpoint quorum: 38 test methods.
- mTLS gateway/remote witness lifecycle: 60 test methods across 15 isolated shards.
- Total expected: 153 test methods.

The results report and suite logs record the actual final run. Source pins cover the local reference artifact and its documentation; they do not claim byte identity to upstream GitHub source.

## Scope limits

Local reference artifact only; not upstream CI, public Internet load testing or production certification. Peer-prefix rate limits are opt-in and can group legitimate users behind NAT or shared IPv6 allocations. Shared SQLite remains same-host and same-PID-namespace infrastructure. No upstream source, branch, or PR was changed and no hosted service was called.
