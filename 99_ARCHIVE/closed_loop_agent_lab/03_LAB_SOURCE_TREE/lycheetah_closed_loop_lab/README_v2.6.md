# Lycheetah Closed-Loop Agent Lab — v2.6 update

## Latest addition: authenticated Stripe webhook inbox

`r16_webhook_reconciliation_v2_6/` adds a testable signed-webhook inbox and a loopback-only HTTP receiver to the v2.5 refund recovery reference adapter.

**Verification:** 52/52 focused test methods and 254/254 combined retained test methods passed. Python bytecode compilation and local loopback smoke passed. No hosted Stripe request or real refund was made; no upstream Lycheetah source changed.

A verified webhook is never treated as proof of current success. The inbox uses events only to trigger a current authenticated provider retrieval or manual reconciliation. It stores a minimal event summary and HMAC, not raw webhook JSON or arbitrary metadata.

Run focused tests:

```bash
cd r16_webhook_reconciliation_v2_6
python run_webhook_tests_v2_6.py
python run_local_smoke.py
```

Run all retained reference suites from the complete archive root:

```bash
python -m r16_webhook_reconciliation_v2_6.run_complete_tests_v2_6
```

Production integrations should use Stripe's official SDK webhook signature verification and preserve the exact raw request bytes. This reference is not a production server or Stripe conformance certification.
