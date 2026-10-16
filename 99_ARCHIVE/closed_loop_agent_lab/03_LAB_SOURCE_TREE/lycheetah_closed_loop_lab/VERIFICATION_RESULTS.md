# Verification Results — v0.9 pack

## Current iteration

Command:

```bash
python -S run_v0_9_tests.py
```

Result: **49 tests passed**, across two separately launched Python interpreter test suites:

- Catalog/issuance integration: 21 tests passed in 2.272 seconds.
- Separate-process crash/recovery: 28 tests passed in 23.735 seconds.
- The test log is saved at `test_output_v0_9.txt`.

A direct provider-boundary test mutates the durable policy body while retaining the old digest and confirms the fake provider rejects the operation with `policy-catalog-binding-rejected` before it opens the provider effects database. A separate host-side test checks the same malformed stored policy before claiming dispatch. The actual execution paths, including crash injection and provider recovery, remain local fixtures.

## Older recorded suites retained

- v0.1-v0.6 legacy suites: 65 tests passed in their separate runner.
- v0.7 crash/recovery: 26 tests passed independently.
- v0.8 catalog stamping: 17 tests passed independently (the prior script's printed expected count was stale and is corrected to 17).

These are separate invocations and not one aggregate run. One `unittest discover` attempt spanning both v0.9 modules timed out; the standalone test for the last case passed, and the intended two-suite runner then passed. Do not claim a single combined discovery pass.

## Scope

Tests use authored deterministic input cases and local SQLite fake services. No live AI model, authenticated approval UI, real MCP host dispatch, real payment/provider service, production secret, or public GitHub mutation was exercised. Results show reference code behavior only.
