# Changelog — v2.4

- Closed direct-dispatch bypasses around persisted operation retry cutoffs.
- Persists `IN_FLIGHT` before the first refund POST and actively rechecks `WAITING` operations.
- Retrieves and checks Charge/PaymentIntent identity, test-mode marker, currency and relevant payment/amount fields before creating a refund.
- Tightens idempotency key, target path, API version, host port and finite-timeout validation.
- Minimizes persisted provider responses: allow-listed recovery fields only; no PaymentIntent `client_secret`, arbitrary metadata, provider error prose or URLs.
- Adds regressions for local ledger tampering, lifecycle monotonicity, recovery, preflight and storage minimization.
- Verification: 76 focused tests and 193 combined retained+focused methods passed; local loopback smoke and Python compilation passed.
- No hosted Stripe API calls, real refunds, real credentials, upstream source changes or full upstream CI run.
