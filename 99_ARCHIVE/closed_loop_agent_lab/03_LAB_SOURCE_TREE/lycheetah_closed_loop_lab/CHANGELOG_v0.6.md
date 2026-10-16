# v0.6 change log — 2026-10-16

- Added `operation_id` to the canonical, approval-bound intent so a host can reconcile an uncertain external outcome using a stable per-operation identifier.
- Added `fake_host_adapter.py` and eight fake-host/fake-provider integration tests.
- Demonstrated normal approved dispatch, no-approval zero effect, action/policy mismatch, revoke-before-dispatch, concurrent duplicate submission, timeout after provider commit with lookup-based reconciliation, and timeout before commit requiring a stop.
- Updated the combined runner to execute the original suites, v0.4 regression suite and v0.5 gate/host-adapter suites.
- Full combined local run: 65 tests passed. Tests are authored deterministic fixtures; no live model, real payment provider or authenticated human approval system was exercised.
