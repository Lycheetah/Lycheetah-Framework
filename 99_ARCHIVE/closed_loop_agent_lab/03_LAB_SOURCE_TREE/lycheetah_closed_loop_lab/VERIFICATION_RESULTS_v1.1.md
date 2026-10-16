# Verification results v1.1

Date: 2026-10-16. All results below are local and synthetic unless explicitly stated otherwise.

## Separate suite results

| Suite | Result | Test methods | Mode |
|---|---:|---:|---|
| Legacy lab v0.1–v0.6 | PASS | 66 | Four sub-suites, each in required working directory |
| Crash/recovery v0.7 | PASS | 26 | Separate Python interpreter; multi-process test doubles |
| Trusted catalog v0.8 | PASS | 18 | Independent unittest run |
| Catalog/issuance v0.9 | PASS | 21 | Separate Python interpreter |
| Crash/recovery v0.9 | PASS | 28 | Separate Python interpreter; multi-process test doubles |
| Policy parser fixture | PASS | 7 | Source-equivalent baseline compared with strict candidate |
| **Total** | **PASS_SEPARATE_SUITES** | **166** | Six separate suite invocations, aggregated from per-suite result files |

Run a single suite with `python run_v1_1_verification.py --suite <name>`. Use `python aggregate_v1_1_verification.py` to validate and summarize the completed records; the aggregator does not rerun the tests. Detailed stdout and metadata live in `verification_v1_1/`.

A prior all-in-one verification attempt exceeded the execution window after two suites. That interrupted attempt is not counted. The six later separate invocations all returned exit code zero.

## Expanded parser fixture

The source-equivalent baseline silently stringifies some malformed JSON field values in `TextRule.from_dict`. The expanded matrix covers six invalid JSON value types (`null`, Boolean, integer, float, array, object) across four fields (`id`, `pattern`, `title`, `description`):

- Source-equivalent baseline: **21 / 24 malformed cases accepted**.
- Strict candidate: **24 / 24 malformed cases rejected**.
- Candidate preserves explicit valid strings and defaults in the fixture.

This is source-equivalent micro-experiment evidence, not an upstream package run. The upstream-ready pytest file has 26 pytest cases (24 malformed inputs plus two compatibility cases); it was syntax-compiled here only, not run against `lycheetah.assurance` in a full checkout. The proposed patch has not been applied to GitHub.

## Test-harness integrity correction

A fresh run revealed that previous v0.4/v0.5 token tests could change only unused padding bits in the final unpadded Base64URL character. That can leave the decoded HMAC bytes unchanged. The tests and demo now decode the signature, flip an actual byte, and re-encode. A new regression test verifies that the decoded signature differs. After correction:

- Legacy suite: **66 tests passed**.
- v0.4 demo: tampered-token case denied with `token-authentication-failed`; candidate effect call count zero.

This was a flaw in our test mutation, not a demonstrated weakness in HMAC or a deployed Lycheetah service.

## Upstream boundary

- Inspected source revision: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`.
- `TextRule.from_dict` target blob reported by GitHub: `913006991327ac40bf34e96fce591ca100334ca9`.
- Creating a review branch was rejected by the connected GitHub integration (HTTP 403, resource not accessible by integration). No public repository files or refs were changed.
- GitHub Actions showed 19 check runs on the inspected commit: 3 success, 15 failure, 1 cancelled. Failed jobs exposed no steps and job logs were unavailable; baseline CI cause remains unresolved. The failed baseline checks must not be attributed to this candidate without evidence.

## Not established

No live model, real repository-maintenance task, authenticated reviewer service, production MCP host, remote provider, production sandbox, or deployment was tested. The 166 tests are local reference/harness tests, not measures of real-model safety or capability. No claim of safety superiority or production readiness is supported.
