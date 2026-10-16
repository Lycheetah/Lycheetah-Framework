# Lycheetah Closed-Loop Agent Lab v2.0 — Evidence Leases

**Research status: executable reference prototype. Not production-authorized.**

This iteration directly targets the external evidence time-of-check/time-of-use (TOCTOU) gap demonstrated in v1.9. The protocol adds a short-lived HMAC-authenticated dispatch token issued atomically by a cooperative evidence authority. Before the effect call, the token is claimed as `IN_FLIGHT`; that state pins all associated evidence even after the token's nominal TTL until the provider outcome is confirmed or reconciled. The token is bound to the operation ID, action digest, trusted requirement set, snapshot and expiry.

## Quick start

Use Python 3.11+ and the standard library only:

```bash
python -m unittest -v test_r9_baseline_regression.py test_evidence_lease_integration.py
python run_evidence_race_experiment.py
```

The combined compatibility and focused integration suite contains 49 test methods: 27 inherited v1.9 regression tests and 22 v2.0 tests. The separate concurrency experiment executes 200 two-thread races against a shared SQLite evidence authority.

## Main changes

- `evidence_lease.py`: SQLite evidence authority, authenticated leases, lease-aware mock effect provider and broker adapter.
- `durable_action_broker.py`: copy of the v1.9 lab reference with two v2.0 changes: explicit definitive pre-effect denial handling, and lookup of an already committed provider result before rechecking current evidence/policy.
- `test_evidence_lease_integration.py`: TOCTOU, concurrent SQLite race, lease tampering/expiry, exact vs subject-status semantics, response-loss recovery, process-style recreation, and idempotency tests.
- `test_r9_baseline_regression.py`: preserved v1.9 suite. One test intentionally demonstrates that the old snapshot-then-effect adapter leaves the TOCTOU gap open; it is a positive reproduction of a negative-control condition, not a safety pass.
- `run_evidence_race_experiment.py` and `evidence_race_results_v2_0.json`: 200 actual thread races with shared SQLite transactions.

## Fundamental assumption

The lease protocol works only when the evidence authority is the authoritative writer and all relevant mutations honor its lease state. A signed token alone cannot freeze an external service that does not cooperate. A production effect provider must validate the operation-bound lease at the effect's commit point, and its idempotency record must commit atomically with its own business mutation. If external evidence and the target effect cannot share a transaction or a provider-backed lease/conditional-operation contract, the gap remains and the safe fallback is reconciliation.

## Upstream boundary

The inspected upstream revision remains `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`. The v2.0 files are not applied to the upstream repository. GitHub branch creation previously returned HTTP 403 via the connected integration. No upstream PR, branch, package test run, live provider test, multi-host test, or production security review is claimed.
