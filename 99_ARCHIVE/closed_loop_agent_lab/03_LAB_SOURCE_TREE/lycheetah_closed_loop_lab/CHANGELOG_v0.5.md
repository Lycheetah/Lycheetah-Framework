# v0.5 change log — 2026-10-16

- Added read-only host-boundary audit: the inspected Lycheetah Guard MCP component is a decision-receipt service, and outer-host enforcement remains an explicit integration contract.
- Reproduced a callback-selection gap in the local v0.4 reference gate: the approved action digest did not bind the separately supplied dispatch callback.
- Added `authority_boundary_lab_v0_5/authority_gate_v0_5.py`, which dispatches only through a trusted route registry and binds the action to dispatcher identity/version.
- Removed per-call callback and policy-hash overrides. Current policy and time come from trusted host dependencies configured at gate construction.
- Bound approval tokens to a deployment/audience ID; added revocation-before-claim; retained short expiry, HMAC, canonical action snapshot and local one-use nonce claims.
- Added 20 v0.5 tests, including wrong-target, wrong-version, policy-source failure, revocation, gate reconstruction, and eight-way replay.
- Updated `run_all_tests.py` to run the new suite.

Expected full local run: 57 tests total across the existing authored suites plus v0.5. No GitHub repo files were written, no live model was called, and no remote provider or production host was exercised.
