# Lycheetah Closed-Loop Agent Lab — Current Index v3.7

**Current focus:** anti-rollback for the spent-challenge registry through a fresh external checkpoint quorum, bound to the registry's actual logical SQLite state and exposed through a guarded loopback HTTP interface.

## Latest artifact: Registry External Quorum v3.7

- Adds signed, parent-linked checkpoint records for the actual `challenges`, `request_nonces`, and `clock_state` logical registry state and schema.
- Adds nonce-bound fresh reports from four witness stores, with a 3-of-4 quorum for one tolerated faulty witness.
- Runs every protected mutation through a guarded dispatcher that persists pending intent and only surfaces a success after the state has a current checkpoint quorum.
- Adds a loopback HTTP integration test, eight concurrent HTTP calls, direct DB mutation tests, response-loss recovery, and partial-quorum recovery.
- **37 current focused tests passed; 82 retained v3.6 tests passed in a separate invocation (119 total method runs across the two suites).** The v3.7 source-pin, Python compilation and rollback demo checks passed.

## Downloads

- `lycheetah_registry_external_quorum_v3.7.zip` — standalone v3.7 implementation, docs, tests and logs.
- `lycheetah_closed_loop_agent_lab_v3.7.zip` — complete research history through v3.7.

## Critical limitation

The four witness stores are simulated as separate local SQLite files in this reference package; they are **not independent remote services or administrative trust domains**. If the primary registry, client anchor and all witness stores are rolled back together, the local model accepts the coordinated old state. This is retained as an explicit negative control. Production assurance requires genuinely independent witness services, keys, administrators and backups.

No upstream source was changed, no hosted service was contacted, and the full upstream CI suite was not run. The new local reference wrapper is POSIX-specific (`fcntl.flock`).

See `r27_registry_external_quorum_v3_7/RESULTS_v3.7.md` and `r27_registry_external_quorum_v3_7/THREAT_MODEL_v3.7.md`.
