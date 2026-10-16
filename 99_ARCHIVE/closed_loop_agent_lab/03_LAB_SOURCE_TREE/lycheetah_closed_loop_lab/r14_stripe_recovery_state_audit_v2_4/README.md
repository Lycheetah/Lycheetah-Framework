# Lycheetah Closed-Loop Agent Lab — Stripe Recovery State Audit v2.4

**Status:** local reference implementation with adversarial HTTP contract tests. Not an official Stripe SDK, production payment adapter, Stripe-hosted conformance result, or upstream Lycheetah integration.

## This iteration

v2.4 began with a re-audit of v2.3's public operation lifecycle. It fixed three operational gaps and tightened endpoint configuration:

1. `dispatch()` could previously send persisted `READY`, `UNKNOWN`, or `CONFLICT` operations without applying the recovery cutoff itself. The cutoff is now enforced inside the send path, and repeat/recovery states require `recover()`.
2. v2.3 left the row in `READY` during the first HTTP request. A process could die after the provider committed but before local result persistence, making the state look like it had never been sent. v2.4 commits `IN_FLIGHT` before the first refund POST.
3. `recover()` previously returned a stored `WAITING` state indefinitely. It now re-queries refunds and persists a later provider state such as `succeeded`.
4. A currency mismatch was previously detected only after the refund response. v2.4 first retrieves the Charge or PaymentIntent and checks target identity, test mode, currency, payment/capture state, and obvious remaining-balance constraints before the first refund POST.
5. Provider responses are now data-minimized before persistence: only recovery fields and Lycheetah operation correlation are retained, while error messages, PaymentIntent `client_secret`, arbitrary metadata and unrelated provider fields are discarded. HMAC provides integrity, not confidentiality.
6. Endpoint hardening now rejects nonstandard ports on `api.stripe.com`, non-finite timeouts, API-version control characters, whitespace/control characters in idempotency keys, and path-shaped target IDs.

## Files

- `stripe_test_adapter.py` — local HMAC-authenticated SQLite ledger and HTTP adapter.
- `stripe_contract_simulator.py` — loopback-only, deliberately incomplete contract simulator.
- `test_stripe_test_adapter.py` — 76 focused regression/adversarial test methods.
- `run_complete_tests_v2_4.py` — retained R10–R12 tests plus v2.4 suite.
- `run_local_smoke.py` — lost-response-after-commit smoke test against the local simulator only.
- `RECOVERY_STATE_AUDIT_v2.4.md` — findings and design rationale.
- `STRIPE_TESTMODE_HTTP_ADAPTER_v2.4.md` — integration behavior and safety limits.
- `RESULTS_v2.4.md`, `SCENARIO_MATRIX_v2.4.json`, `SOURCE_LOG_v2.4.md` — results, notable scenarios and official documentation references. `combined_tests_v2.4.log` contains the full successful combined output.

Only Python's standard library is required.

## Run

In this directory:

```bash
python -m unittest -v test_stripe_test_adapter.py
python run_local_smoke.py
```

From the parent `lycheetah_closed_loop_lab` directory:

```bash
python r14_stripe_recovery_state_audit_v2_4/run_complete_tests_v2_4.py
```

## Verified locally

- Focused v2.4 suite: **76/76 tests passed**.
- Retained R10–R12 suites plus v2.4: **193/193 test methods passed**.
- Local smoke test: a simulated provider commits, drops the response, then recovery reuses the saved key and returns one simulated effect.
- Python compilation passed.

No hosted Stripe API calls were made, no Stripe secrets were used, no real refund was created, and no upstream Lycheetah source file was changed. The 193 tests are regression cases against project reference implementations and a local simulator, not independent guarantees and not proof of hosted Stripe behavior.

## Non-negotiable limits

- The 23-hour automatic retry cutoff is a conservative project policy, not a Stripe guarantee that an idempotency key remains retained for exactly 23 hours.
- HMAC protects stored rows only while its key remains secret. It does not protect a compromised process or key.
- The preflight retrieves a target snapshot but does not reserve funds or make the later refund request atomic with that snapshot. Stripe remains authoritative for the actual request; the provider contract must be checked in a controlled test account before integration.
- A zero-match refund search is not proof that the refund did not happen; the result remains `RECONCILE`.
- Production use would require real Stripe test-mode conformance, webhook and retrieval strategy, external approval integration, secret management, migration/backup review, monitoring, and independent security review.
