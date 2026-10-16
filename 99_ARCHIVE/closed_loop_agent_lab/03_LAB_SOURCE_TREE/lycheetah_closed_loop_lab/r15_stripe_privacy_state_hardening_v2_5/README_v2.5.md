# Stripe Privacy & State Hardening v2.5

A standard-library-only reference adapter and loopback simulator. See `RECOVERY_STATE_AUDIT_v2.5.md` for the threat model, exact test claims, and remaining limitations.

## Standalone quick verification

Run these from this directory:

```bash
python -m unittest -v test_stripe_test_adapter.py
python run_local_smoke.py
```

Focused suite: 85/85 test methods passed. The combined 202-test runner is in the complete research archive, because it imports retained R10–R12 suites outside this standalone package.

## Safety note

This is not an official Stripe SDK or a production payment processor. HMAC protects record integrity but does not encrypt the SQLite database. Local preflight checks are not atomic with Stripe's remote refund commit. The default constructor refuses caller-supplied per-call timestamps; a test-only clock override is an explicit opt-in. No hosted Stripe calls have been made with this artifact.
