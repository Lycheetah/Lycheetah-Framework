# Lycheetah Closed-Loop Agent Lab v2.2 — Stripe Refund Contract

This iteration converts the general provider-recovery work into an endpoint-specific, executable contract for Stripe API v1 refund creation.

- `stripe_refund_recovery.py`: pure offline helper; no provider API traffic and no SDK dependency.
- `test_stripe_refund_recovery.py`: regression suite covering key-window boundaries, account/mode/payload binding, saved 500s, and refund reconciliation.
- `STRIPE_REFUND_CONTRACT_v2.2.md`: documented provider semantics, local conservative policy, residual risks and references.
- `provider_facts.json`: machine-readable documentation-derived facts.
- `results_v2.2.json`: test output digest and scope.

Run:

```bash
python -m unittest -v test_stripe_refund_recovery.py
```

This is not a production Stripe adapter. It intentionally leaves network calls to a later sandbox integration with credentials, and the code never claims that Stripe transactionally validates Lycheetah authorization evidence at commit time. The trusted adapter must construct page envelopes from actual outgoing cursors and returned responses; test fixtures alone do not authenticate provider observations.
