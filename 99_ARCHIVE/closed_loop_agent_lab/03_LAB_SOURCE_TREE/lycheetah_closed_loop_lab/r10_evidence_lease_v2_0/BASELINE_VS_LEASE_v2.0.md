# Baseline vs Evidence Lease — v2.0

## Why another check is not enough

The v1.9 negative-control fixture in `test_r9_baseline_regression.py` deliberately changes external evidence immediately after the broker reads a passing snapshot. The old snapshot-then-effect path still applies the simulated effect. That test passes because it reproduces the vulnerability as expected; it does not mean the baseline is safe.

## What changes in v2.0

The effect adapter asks the evidence authority to issue a version-bound, signed lease immediately before dispatch. The lease is an atomic decision at the authority's SQLite database:

- If an evidence update commits first, the stale exact snapshot no longer matches and no lease is issued. The broker sends no effect and reconciles.
- If the lease commits first, subsequent writes to any required key are refused until the lease is released or expires. The effect provider must verify the lease's HMAC, operation ID, payload digest and expiry at the effect commit boundary.

The broker also queries an authoritative provider idempotency record before rechecking current policy/evidence, allowing a previously committed effect to be acknowledged after a response is lost and evidence later changes. This is only safe when the provider lookup/result record is trustworthy and idempotency is durable.

## Results

- v1.9 regression methods: 27/27 pass, including one explicit open-gap negative control.
- v2.0 new methods: 22/22 pass.
- Shared-SQLite concurrent update-versus-lease race: 200 rounds, zero invariant violations (79 update-first, 121 lease-first on the recorded run).
- Deterministic alternating race fixture: 30 rounds, all expected outcomes.

## Scope boundary

This is not a proof for arbitrary remote services. The simulated evidence source makes all writes use the lease authority, and the simulated effect provider verifies the lease and atomically commits its mock effect plus idempotency record. If an actual evidence system permits out-of-band updates, or an actual action provider does not validate the lease/conditional precondition at its commit boundary, the distributed TOCTOU problem remains. That deployment must retain a review/reconciliation fallback.
