# Lycheetah Stripe Request Privacy Audit v2.5

This iteration narrows what the Stripe refund reference adapter will persist or send as metadata and hardens local SQLite file permissions. It is a research/test artifact, not a production payment integration.

- See `PRIVACY_DATA_MINIMIZATION_AUDIT_v2.5.md` for the finding and threat boundary.
- See `stripe_test_adapter.py` for the reference implementation.
- See `test_stripe_test_adapter.py` for 81 focused test methods.
- See `RESULTS_v2.5.md` for test counts and limitations.

Quick start:

```bash
python -m unittest -v test_stripe_test_adapter.py
python run_complete_tests_v2_5.py
python run_local_smoke.py
```

No hosted Stripe API calls are made by these tests. The adapter rejects arbitrary caller-supplied metadata because it persists the exact outgoing request for recovery and does not need unrelated business/customer values in that payload. Callers that need business metadata should store it separately under their own data-governance rules, not extend this recovery ledger implicitly.
