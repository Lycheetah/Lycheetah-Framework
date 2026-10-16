# Research pack manifest — v1.6

## Added directory

`r6_upstream_readiness_v1_6/`

- `policy_type_guard_v1_6.patch` — narrow `TextRule.from_dict` guard against coercing invalid wire types.
- `strict_assurance_wire_types_v1_3.patch` — receipt/finding/control type guards retained from R3.
- `receipt_contract_delta_v1_6.patch` — reject unknown control fields, validate policy SHA-256 field, and reject explicit `cap_reason: null` so the parser does not normalize a noncanonical wire property away.
- `policy.schema.current-snapshot.json`, `receipt.schema.current-snapshot.json` — semantic snapshots of the inspected base schemas, used to preserve a stable old-contract comparison.
- `policy.schema.strict-candidate.json`, `receipt.schema.strict-candidate.json` — candidate schemas.
- `scan_migration_compat.py` — read-only record scanner using the real parser from a clean base checkout and comparing against candidate guards/schemas.
- `fixtures/customer_support_policy.json` — Git-blob-verified copy of the actual public example policy at the inspected source commit.
- `audit_repository_example_policy.py` and `repository_example_policy_results.json` — compatibility check that both current and candidate contracts accept that committed example.
- `tests/test_repository_example_policy_compat.py` — reproducible test for the public example compatibility check.
- `preflight_upstream_integration.py` — exact-blob/source-commit preflight; simulates patch application against temporary copies only.
- `check_patch_context_v1_6.py`, `patch_context_check_v1_6.json` — synthetic context smoke test, explicitly not proof of full-checkout application.
- `tests/test_migration_compat_audit.py` — 12 standalone tests of candidate guard and schema behavior.
- `tests/test_assurance_wire_types.py`, `tests/test_assurance_policy_wire_types.py`, `tests/test_assurance_candidate_schemas.py` — proposed upstream pytest tests; compiled but not run against the full package.
- `UPSTREAM_PROMOTION_CHECKLIST.md` — ordered apply/test/review flow and promotion gates.
- `PROPOSED_PR_DESCRIPTION.md` — draft description only, not submitted.
- `RESULTS_v1.6.md`, `INTEGRATION_STATUS.md`, `CHANGELOG_v1.6.md` — execution facts and limits.

## Measured local results

- R6 standalone compatibility tool: 12 passed.
- Source-hash-verified committed example policy: passed current and candidate contract checks.
- Combined R3–R6 standalone regression suites: 31 test methods passed, 77 subtests passed.
- Candidate schema meta-validation: both Draft 2020-12 schemas passed.
- Synthetic patch contexts: all 3 patches passed.
- `git apply --numstat`: all 3 patches parse.

## Not measured

No full upstream checkout test, true `git apply --check` on a complete checkout, real persisted-record audit, full CI, live model task, deployment, branch, commit or pull request. GitHub branch creation returned HTTP 403 `Resource not accessible by integration`.
