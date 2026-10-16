# Results v3.3

## Focused suite

- Command: `./run_v3_3_tests.sh`
- Result: **37 test methods passed**; current-chain demo passed.
- Log: `focused_tests_v3.3.log` and `demo_output_v3.3.log`.
- Includes 6 new tests beyond v3.2's 31 focused tests.

## Frozen baseline counterexamples

- Command: `python reproduce_v3_2_findings.py`
- Result: **5 baseline acceptance cases reproduced**; output is `baseline_v3_2_reproduction.json`.
- This is a local before/after comparison against the frozen v3.2 module copy, not an upstream security assessment.

## Retained historical regression

- v3.1 external checkpoint group: 33 passed.
- v3.1 HTTP group 1: 14 passed.
- v3.1 HTTP group 2: 14 passed (rerun separately after an earlier combined shell invocation stalled; the isolated run exited 0).
- v3.1 HTTP group 3: 13 passed.
- Aggregate: **111 passing test methods across five separate test-process invocations** (37 current + 74 retained). This is not one monolithic run and not upstream CI.

## Claims deliberately not made

- Not upstream CI; no full checkout build or public branch was created.
- No production anchor/Stripe API calls and no real refunds.
- Distinct signing keys do not ensure organizational or infrastructure independence.
- The SQLite monotonic guard is a local test adapter, not a non-rollbackable production CAS.
