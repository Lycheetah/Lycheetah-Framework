# Pack Manifest v4.8

Artifact: Hierarchical IPv6 Prefix Quotas for Lycheetah mTLS Ingress
Parent: v4.7
Observed upstream default-branch commit used as source context: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`

New/updated primary files:
- `shared_ingress_quota.py`: optional aggregate bucket helper, schema-5 fingerprint, atomic aggregate lease mapping, cleanup, and snapshot counter.
- `registry_gateway_mtls.py`: optional process-local aggregate quota and wiring into shared SQLite store.
- `test_shared_ingress_quota.py`: cross-/64 aggregate tests, concurrency, mismatch, invalid settings, dead-owner cascade.
- `test_remote_witness_process.py`: gateway-process local quota, shared-store integration and invalid-configuration regressions.
- `shared_ingress_quota_v4_7_baseline_fixture.py`: preserved prior local behavior.
- `differential_probe_v4.8.py`: paired v4.7/v4.8 experiment.
- `run_gateway_suite_v4.8.py`, `run_v4.8_tests.sh`, and source pin manifest/verifier.

Retained runtime modules and test suites are included so the entire local gateway/quorum regression can run standalone. Historical logs and superseded documentation are not embedded in this iteration directory; the complete lab archive includes prior iterations separately.

Not production certification, not upstream CI, and not a claim that local source files are byte-identical to upstream. No upstream code, branch or PR was changed; no hosted service was called.
