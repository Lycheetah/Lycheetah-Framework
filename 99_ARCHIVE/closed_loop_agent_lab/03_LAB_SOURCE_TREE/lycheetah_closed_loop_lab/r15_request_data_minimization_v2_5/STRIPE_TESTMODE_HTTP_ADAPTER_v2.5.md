# Stripe Test-Mode HTTP Adapter — v2.5

This standalone reference adapter exercises a refund creation/recovery loop against a loopback HTTP contract simulator. It is not an officially supported Stripe SDK, a payment product, or a production-certified integration.

## v2.5 changes

1. **Request metadata minimisation:** arbitrary caller-supplied metadata is rejected before persistence. The adapter only sends `lycheetah_operation_id`, which is used to correlate a potential refund during reconciliation.
2. **Owner-only local ledger:** the SQLite operation database is opened as a regular file and restricted to owner read/write (`0600`) on POSIX. Symlink database paths and the per-connection `:memory:` option are rejected. HMAC still provides integrity only, not confidentiality.
3. **Preserved v2.4 protections:** response allow-listing; no provider error prose; durable `IN_FLIGHT` marker; explicit test-mode marker validation; account/API-version/request fingerprint binding; redirect rejection; official-host TLS/port restrictions; idempotency cutoff; cursor validation; reconciliation on ambiguity.

## Install and run

Requires Python 3.13+ and standard library only.

```bash
python -m unittest -v test_stripe_test_adapter.py
python run_complete_tests_v2_5.py
python run_local_smoke.py
```

The full regression runner expects the retained `r10_evidence_lease_v2_0`, `r11_provider_contracts_v2_1` and `r12_stripe_refund_contract_v2_2` folders, included in the complete lab archive. The focused test module and local simulator run independently from this directory.

## Default guardrails

- Only a syntactically shaped `sk_test_` key is accepted; a syntactic key check is not authentication to Stripe.
- Default HTTPS host is `api.stripe.com`; custom HTTPS hosts require explicit opt-in.
- Plain HTTP is permitted only to a loopback simulator with explicit opt-in.
- Redirects are not followed.
- HTTP interactions are disabled in tests to hosted Stripe; all runs in this pack use local loopback simulation.
- Caller metadata is intentionally unsupported to prevent unnecessary values being persisted in the replayable SQLite payload.
- A local 23-hour cutoff is a conservative policy, not a Stripe retention SLA.

## Known limitations

- No hosted Stripe test-mode conformance was run; no real refunds were created.
- Local Charge/PaymentIntent preflight is a snapshot, not atomic reservation of refundable balance.
- HMAC does not encrypt the database and does not protect against a compromised process or key.
- Target IDs, amount, idempotency key, and operation state remain in the protected local ledger for recovery.
- The simulator does not fully model Stripe's backend semantics, timing or failure modes.
- This code has not been integrated into the upstream Lycheetah Framework or run against its full package CI.
