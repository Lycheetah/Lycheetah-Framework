# Pack Manifest — Lycheetah Closed-Loop Agent Lab v2.5

The complete archive retains prior evidence-lease, provider-contract, refund-recovery and HTTP-adapter experiments, and adds `r15_stripe_privacy_state_hardening_v2_5/`.

## Current artifact

- `stripe_test_adapter.py`: strict request metadata/payload contract, bounded response reads, atomic local dispatch claim, full state-transition guard and test-only per-call clock override.
- `stripe_contract_simulator.py`: local loopback-only simulator with lost-response, oversized-response and other fault injections.
- `test_stripe_test_adapter.py`: 85 focused test methods.
- `run_complete_tests_v2_5.py`: all retained R10-R12 regression suites plus the R15 suite.
- `RECOVERY_STATE_AUDIT_v2.5.md`, `PROVIDER_CONTRACT_SOURCES_v2.5.md`, `RESULTS_v2.5.md` explain design, official provider contract sources and evidence boundaries.

## Verified

- 85 / 85 focused tests passed.
- 202 / 202 combined tests passed.
- Local smoke passed; one simulated provider effect across two POST attempts after a dropped response.
- Python compilation passed.

## Not claimed

No live API calls, no real refunds, no actual Stripe credentials, no upstream modifications, no hosted Stripe conformance and no full upstream Lycheetah CI run. This remains a local reference implementation requiring independent review and explicit promotion gates.
