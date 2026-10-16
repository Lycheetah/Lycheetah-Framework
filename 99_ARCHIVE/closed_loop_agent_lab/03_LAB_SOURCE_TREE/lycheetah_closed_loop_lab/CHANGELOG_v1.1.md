# v1.1 — upstream-ready parser fix and CI baseline audit

- Added an upstream-style pytest file that covers null, Boolean, integer, float, array and object values for `id`, `pattern`, `title` and `description` through `AssurancePolicy.from_dict` (24 malformed cases), plus preservation of explicit strings and defaults.
- Added a non-mutating preflight script: checks a named non-default branch, clean worktree, exact target blob SHA and `git apply --check` before giving exact apply/test commands.
- Recorded the read-only GitHub integration's 403 rejection of branch creation; no upstream repository mutation took place.
- Recorded the inspected base commit's 19 GitHub Actions checks: 3 success, 15 failure, 1 cancelled, but failed job step lists were empty and logs unavailable. Baseline CI cause remains unresolved.
- Kept the finding bounded: a strictness defect in parser input handling, not a confirmed production security bypass.

- Fixed false-negative Base64URL signature-tampering tests in v0.4/v0.5 and demo: now flip a decoded signature byte; added a test that asserts the decoded bytes differ.
- Expanded the policy parser probe from 20 to 24 cases: source-equivalent baseline accepted 21; strict candidate rejected all 24.
- Added one regression test validating test-mutation semantics; v0.1-v0.6 suite count is now 66, while all 6 separate suites report 166 methods passed.
- Corrected the v0.8 runner label from 17 tests to the 18 that actually run.
