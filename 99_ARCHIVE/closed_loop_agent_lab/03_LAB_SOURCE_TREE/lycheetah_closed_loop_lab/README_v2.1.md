# Lycheetah Closed-Loop Agent Lab v2.1

**Focus:** provider contract conformance, commit-time authorization conditions, idempotency windows, and ambiguity-aware recovery.

## Main deliverables

- `r11_provider_contracts_v2_1/PROVIDER_CONTRACT.md` — minimum semantic provider contract.
- `r11_provider_contracts_v2_1/provider_contract.py` — atomic reference and two negative controls.
- `r11_provider_contracts_v2_1/recovery_policy.py` — explicit recovery decision function.
- `r11_provider_contracts_v2_1/test_provider_contract.py` and `test_recovery_policy.py` — 29 focused tests.
- `r11_provider_contracts_v2_1/model_check.py` — bounded three-event schedule enumeration.
- `r11_provider_contracts_v2_1/DOCUMENTATION_FINDINGS.md` — official Stripe / AWS idempotency semantics and implications.
- `r10_evidence_lease_v2_0/` — preserved previous iteration.

## Verification status

78 local test methods passed across the preserved v2.0 and new v2.1 suites. No external provider API was called. No upstream source was changed and the complete upstream Lycheetah suite was not run.

## Important conclusion

Provider idempotency and authorization-condition freshness are separate guarantees. The same-key retry can protect against duplicate effects, but only provider-enforced commit-time predicates or a documented equivalent can close the stale-evidence window. When key retention, lookup semantics or condition guarantees are unknown, route to reconciliation rather than blindly retry.
