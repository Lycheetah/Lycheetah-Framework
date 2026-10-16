# Verification Results — v2.2

**Research date:** 2026-10-17

## What ran

- Endpoint-specific Stripe API v1 Refund offline decision suite: **39/39 test methods passed**.
- Preserved v2.0/v2.1 evidence-lease and generic provider-contract suites plus v2.2 suite: **117/117 test methods passed** in one combined invocation.
- Python bytecode compilation passed for the implementation, tests, and scenario runner.
- Scenario runner emitted seven deterministic JSON decisions from fixtures.
- No Stripe credentials were available or used. No Stripe or other provider API calls were made. No payment or refund was created.

## Interpretation

The 39 v2.2 tests verify that the local decision policy follows the documented assumptions encoded in the module: same-key/same-payload retry only within a conservative window, different account or mode and changed payload fail to reconciliation, stored 500 never implies no effect, unique correlation checks target/amount/currency/status, incomplete listing and zero match never imply absence of effect, and failed or canceled matched objects require a newly approved operation.

The aggregate 117 tests also re-run the preserved SQLite lease concurrency, recovery, and generic provider reference suites. They do not represent 117 independent security guarantees and are not a third-party audit.

## Not tested / not claimed

- No Stripe sandbox or live API call; no provider adapter connected to Stripe.
- No validation of account-specific Connect request scoping, webhook ordering/delivery, actual Stripe retention in a particular account, rate limits, or all API versions.
- No proof of strong consistency for refund-list absence; the policy treats no match as inconclusive.
- No provider-side atomic coupling of Lycheetah approval/evidence and Stripe refund commitment.
- No upstream Lycheetah repository changes and no full upstream package CI execution.

## Promotion gate

A real adapter is not ready until it has a sandbox conformance run, durable pre-request operation persistence, tests using Stripe's test mode, webhook/retrieval reconciliation, exact account/mode pinning, API-version pinning, and a human-approved procedure for every ambiguous outcome past the retry cutoff.
