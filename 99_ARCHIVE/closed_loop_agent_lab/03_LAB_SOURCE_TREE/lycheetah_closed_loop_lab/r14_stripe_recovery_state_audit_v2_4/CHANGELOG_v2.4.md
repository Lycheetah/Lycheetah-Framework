# Changelog — v2.4

- Closed the direct-dispatch retry-cutoff bypass for persisted `READY`, `UNKNOWN` and `CONFLICT` operations.
- Added a durable `IN_FLIGHT` state before the first provider POST, so process death during the external call no longer leaves a row that looks never attempted.
- Changed `recover()` so `WAITING` refunds are re-queried and can advance as provider state changes.
- Added preflight GET of the target Charge/PaymentIntent before the first POST. Checks object/ID, explicit test mode, currency, paid/captured or succeeded status, and obvious amount/balance constraints.
- Added `PRECHECK_FAILED` terminal handling for substantive target mismatch; no refund POST is sent and a new reviewed operation is required.
- Added monotonic state protections against downgrading `SUCCEEDED` and terminal `NEW_APPROVAL_REQUIRED` state.
- Hardened target IDs, idempotency key characters, API-version headers, timeout finiteness and official Stripe host port.
- Improved simulator shutdown responsiveness and added instrumentation to assert `IN_FLIGHT` exists before POST.
- Verification: 76 focused tests and 193 retained+focused methods passed; local smoke and Python compilation passed.
- No hosted Stripe calls, real refunds, secrets, or upstream source changes.
- Adversarial privacy review found that HMAC authenticates stored response data but does not conceal it. Provider Charge/PaymentIntent and Refund responses are now reduced to an allow-list of recovery fields; error summaries omit free-text provider messages and URLs. Added persistence-minimization regression tests.
