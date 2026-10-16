# v0.4 change log

- Added `authority_boundary_lab/`: local prototype for host-signed, action-bound, one-use approvals for consequential tool actions.
- Added a deliberately weak boolean-claim baseline demo plus scenarios for missing approval, action substitution, policy drift, expiry, tampering, and replay.
- Added sequential and concurrent replay tests, action snapshot integrity checks, and conservative outcome-uncertainty handling.
- Added `run_all_tests.py` so all test suites run with their expected module paths from a single project-root command. A direct combined unittest import from the root had failed previously because subfolder tests imported sibling modules as top-level names; the harness now runs those suites in their respective working directories.
- Updated the research handoff to emphasize a real host-adapter audit before an actual agent task trial.
- Full combined run: 37 tests passed. No deployed adapter, live agent or remote provider was exercised.
