# R6 results — v1.6 upstream readiness

## Local execution

- Standalone compatibility/audit tests: **12 passed**.
- Repository example-policy compatibility test: **1 passed**; the fixture's Git blob matches the exact public repository file at the inspected base, and both current/candidate schemas plus the source-equivalent parser models accept it.
- Combined R3–R6 standalone regression suites after this addition: **31 passed, 77 subtests passed**.
- All three patch files parse with `git apply --numstat`.
- Both candidate schemas parse as JSON and pass JSON Schema Draft 2020-12 meta-validation.
- Python syntax compilation passed for the compatibility scanner, preflight, and proposed tests.
- ZIP integrity is checked separately at pack creation.

## What was actually tested

The 12 local tests validate strict wire-guard functions plus representative candidate policy/receipt schema acceptance and rejection. The earlier R3–R5 local fixture suites were rerun and passed. These tests run on the artifact's standalone test harnesses, not in the complete upstream package.

The new preflight is designed to test all patches sequentially against a *temporary copy* of source files from a real, exact-base checkout, then syntax-compile changed Python modules. It was not executable here because the checkout was unavailable. Its successful operation is not claimed.

## Current repo-write limitation

The GitHub repository metadata query showed push permissions; however direct creation of a non-default branch returned HTTP 403 `Resource not accessible by integration`. No branch, commit, PR, schema replacement, or upstream test run happened.

## Promotion gate

Run `preflight_upstream_integration.py` and `scan_migration_compat.py` against a clean checkout at the exact base before patching. Review every `needs_review` record. Then apply the patches, replace schema files, copy new tests, run the specified and full test suites, and compare against a known-green baseline. This pack alone is not release evidence.
