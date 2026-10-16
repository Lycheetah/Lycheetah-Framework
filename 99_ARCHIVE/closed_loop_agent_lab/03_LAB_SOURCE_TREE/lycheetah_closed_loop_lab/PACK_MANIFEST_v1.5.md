# Research pack manifest — v1.5

The v1.5 pack retains the prior closed-loop agent, authority-gate, crash-recovery, and receipt-schema work and adds `r5_policy_contract_v1_5/`.

## R5 contents

- `POLICY_CONTRACT_AUDIT_v1.5.md` — findings, limits, proposed resolution and promotion gates.
- `policy.schema.json` — readable reconstruction of inspected current schema.
- `policy.schema.strict-candidate.json` — candidate schema changes.
- `policy_contract_parity.py` — source-equivalent current parser and 20-case differential matrix.
- `results.json` — complete machine-readable matrix and summary.
- `test_policy_contract_parity.py` — 5 local tests.
- `PROPOSED_PARSER_CHANGE.md` — narrow source-level change proposal.
- `PROPOSED_UPSTREAM_TESTS_v1.5.py` — tests intended for a clean upstream package checkout; not run upstream here.
- `VERIFICATION_RESULTS_v1.5.md` — executed versus unexecuted checks.

## Result summary

The current source-equivalent parser/schema acceptance comparison agreed on 7 of 20 deliberately selected cases. The candidate schema plus proposed strict-type parser model agreed on 17 of 20. The remaining three mismatches concern parser-specific semantic validation (invalid regex, duplicate rule IDs) and numerical integer representation (`20.0`), which require explicit treatment rather than pretending standard JSON Schema duplicates all parser behavior.

All reported results are fixture-level. There was no full upstream checkout, package test, CI run, production deployment, or repository write.
