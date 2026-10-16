# Pack Manifest v4.7 — Absolute HTTP Deadline Branch

This focused branch builds on the v4.6 gateway's attempt-based ingress quotas. It is an alternative track alongside the v4.7/v4.8 hierarchical IPv6 work, not an upstream merge.

## Contents

- v4.7 local mTLS gateway with absolute HTTP socket deadline.
- Existing gateway, shared quota, quorum and remote-witness dependencies/tests.
- Exact local source pin manifest/checker and runnable suite commands.
- Preserved v4.6 gateway copy plus paired HTTP header slow-drip probe.
- Focused regressions, separate suite logs, and machine-readable results.
- API contract, threat model, baseline comparison, changelog and integration plan.

## Verification

- 24 ingress tests, 13 coordinator tests, 38 checkpoint quorum tests and 56 gateway lifecycle tests passed (131 unique tests).
- 21 source fingerprints and Python compilation passed.
- Paired probe showed v4.6 still holding one active slot at 1.227 seconds while v4.7 had released it at 0.971 seconds during an 80 ms header-byte drip.
- One gateway run emitted its diagnostic stack at 45 seconds while a dispatch awaited fresh quorum evidence, then completed all tests in 56.947 seconds with no errors, failures, or surviving Python threads. This reveals a documented residual: the socket deadline does not preempt in-progress application/quorum work.
- No new TLS handshake delta was measured.
- This is not upstream CI, production certification, or hosted-service verification.
