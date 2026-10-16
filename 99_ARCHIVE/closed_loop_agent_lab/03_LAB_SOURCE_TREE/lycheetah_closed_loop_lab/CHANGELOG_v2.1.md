# Changelog — v2.1

## Provider Contract Conformance

- Added reference tests for provider-side atomic condition + side effect + durable idempotency.
- Added negative controls proving a split precheck can execute on stale state and a non-idempotent provider can duplicate effects after a lost response.
- Added a bounded three-event model checker for the authorization TOCTOU interleaving.
- Added explicit provider recovery policy mapping to `ACCEPT_STORED_RESULT`, `RETRY_SAME_KEY`, or `RECONCILE` based on actual observed lookup state and documented API contract fields.
- Reviewed official Stripe, Amazon EC2 and Amazon ECS idempotency docs; no live APIs called.

## Verification

Combined local v2.0 + v2.1 suites passed **78/78 test methods** (49 retained v2.0 methods + 29 v2.1 methods). The artifact is a reference lab, not an upstream or production verification. No Lycheetah repository source was changed.
