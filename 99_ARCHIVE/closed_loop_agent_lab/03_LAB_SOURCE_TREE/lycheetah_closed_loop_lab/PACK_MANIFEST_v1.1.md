# Pack manifest — v1.1

## Current focus

- `TEST_HARNESS_FINDING_v1.1.md` — Base64URL padding-bit test error and correction.
- `CHANGELOG_v1.1.md` — changes in this iteration.
- `VERIFICATION_RESULTS_v1.1.md` and `verification_v1_1.json` — six isolated suite outcomes and aggregation.
- `run_v1_1_verification.py` — runs one named suite at a time with a per-suite timeout.
- `aggregate_v1_1_verification.py` — aggregates completed, per-suite JSON result files without rerunning tests.
- `verification_v1_1/` — stdout logs and machine-readable outcome for each of the six suite invocations.

## R2 parser microtask

- `r2_policy_parser_audit/R2_REPORT.md` — finding and bounded result.
- `r2_policy_parser_audit/task_contract.md` — frozen type contract.
- `r2_policy_parser_audit/proposed_patches/strict_text_rule_parser.patch` — proposed minimal source patch.
- `r2_policy_parser_audit/proposed_patches/test_assurance_policy_text_rule_types.py` — upstream-ready pytest regression tests; not run against a full upstream checkout in this environment.
- `scripts/verify_upstream_patch.py` — non-mutating preflight requiring a matching source blob and a clean named non-default branch.
- `UPSTREAM_INTEGRATION_STATUS_v1.1.md` — GitHub write gate and baseline Actions status.

## Retained earlier research

All earlier v0.1–v1.0 lab files are retained. Key directories: `authority_boundary_lab/`, `authority_boundary_lab_v0_5/`, `authority_boundary_lab_v0_7/`, `authority_boundary_lab_v0_8/`, `authority_boundary_lab_v0_9/`, `observer_probe_v0_3/`, and `r2_policy_parser_audit/`.

## Evidence summary

- 166 test methods passed across six completed local suite invocations.
- 24 malformed policy-parser probes: baseline accepts 21; strict candidate rejects 24.
- The upstream parser patch remains proposed, not committed.
- No public GitHub branch, issue, pull request or file was created or modified.
- No live model or production deployment was tested.
