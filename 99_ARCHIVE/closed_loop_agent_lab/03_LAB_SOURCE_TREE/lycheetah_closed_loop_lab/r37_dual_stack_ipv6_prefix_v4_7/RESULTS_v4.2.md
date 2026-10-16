# Verification Results v4.2 — Authenticated Coordinator Fairness

## Final local verification

- Source pin check: **PASS**, 8 reference-file SHA-256 pins.
- Python compilation: **PASS**.
- Retained checkpoint quorum suite: **PASS**, 38 tests.
- Remote witness / mTLS gateway integration suite: **PASS**, 47 tests in 32.274 seconds.
- Total across separate invocations: **85 test methods passed**.
- Archive CRC: pending archive-build step.
- Hosted service calls: **0**.
- Upstream repository or CI modified: **No**.

## v4.2-specific checks

1. With coordinator A occupying its one allowed dispatch slot, a second request from A gets a signed 429 without registry mutation from that request.
2. Coordinator B has an independent quota and can successfully perform a request while A is at its active-request limit.
3. Per-coordinator request-rate tokens are separate; exhausting A's token does not exhaust B's.
4. A certificate that contains two URI SANs both on the allow-list is rejected with signed `403 coordinator-identity-ambiguous` before registry mutation.
5. Operational snapshots expose aggregate counts only and do not emit either coordinator URI SAN.
6. Invalid coordinator quota values, including Boolean-as-integer, zero and negative values, are rejected at construction.

## Harness reliability note

An earlier full gateway invocation timed out in the inherited subprocess restart path. Inspection showed that the two-witness outage test left stopped subprocesses for the next test's setup to restart, then the explicit restart test restarted one of them again. The test now restores stopped witness processes in its own `finally` block. The subsequent completed 47-test gateway invocation passed. This is recorded as a test-fixture stabilization, not a runtime security finding.

## Boundaries

The implementation and all tests are local reference-harness code. Four witness subprocesses and the gateway share one host/operator, test certificates are ephemeral, and no live or hosted service was contacted. The URI-SAN quotas are process-local and begin only after HTTP headers parse. Distributed quotas, production CA policy, OS resource limits, multi-host conditions and upstream CI remain unverified.
