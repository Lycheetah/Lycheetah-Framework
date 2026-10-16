# Changelog — v1.6

## R6 upstream readiness and migration compatibility

- Consolidated R3/R4 receipt-wire fixes with R5 policy text-rule type guards into a sequence of source patches and candidate schemas.
- Added a source-pinned, non-mutating preflight that simulates the patch sequence in a temporary copy and syntax-compiles modified files.
- Added a read-only policy/receipt compatibility inventory that must run against the untouched base checkout before applying stricter schemas/parsers.
- Added regression cases for explicit-null `cap_reason`, unknown control properties and `policy.sha256` format.
- Corrected integration order: first inspect persisted records, then apply parser/schema updates and run tests.
- Local R3–R6 test suites: 31 methods passed, 77 subtests passed. Synthetic patch-context check: 3/3. Candidate schemas pass Draft 2020-12 meta-validation.
- No upstream branch, commit, PR, full package test, CI result, or production claim. Branch creation was blocked by GitHub integration HTTP 403.
