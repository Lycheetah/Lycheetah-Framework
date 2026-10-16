# Verification Results v2.0

## Executed locally

Command:

```bash
python -m unittest -v test_r9_baseline_regression.py test_evidence_lease_integration.py
```

Result: **49 test methods passed, 0 failed** (27 v1.9 regression methods + 22 v2.0 methods).

Separate concurrency experiment:

```bash
python run_evidence_race_experiment.py
```

Result: **200 races, 0 invariant violations**. Observed execution on this run: 79 update-first cases (evidence write commits and lease acquisition is denied) and 121 lease-first cases (lease commits and evidence mutation is blocked).

The focused test suite also includes a deterministic 30-round interleaving test alternating update-first and lease-first outcomes.

## How to interpret the inherited baseline

All 27 v1.9 regression methods passed. One is deliberately named `test_external_evidence_can_change_after_dispatch_snapshot`; it passes by demonstrating that the old snapshot-only path can apply the action after the evidence changes. It is a negative-control reproduction of the gap, not evidence that v1.9 closes it.

## Not run / not established

- Full upstream `Lycheetah-Framework` test suite or CI.
- Integration with the actual upstream `FinalityGate`.
- Real payment/deployment provider or genuine conditional-commit API.
- Multi-process kill/restart at the OS level or multi-host race tests.
- Real cross-service lease enforcement, signed lease contract, clock skew handling, key management, or production security review.
- Protection when any evidence mutation path bypasses the lease authority.
- A general recovery/fencing contract for abandoned `IN_FLIGHT` calls in a real provider.

The evidence lease result is a proof of behavior within this local, single-host reference boundary only. Expired unclaimed leases can unlock; a started `IN_FLIGHT` operation remains pinned beyond TTL until the provider outcome is known. This can block subsequent evidence updates after a crashed worker, intentionally preferring safety over availability.
