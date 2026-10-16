# Changelog v4.2

- Adds authenticated per-coordinator active-request and request-rate quotas to the bounded mTLS registry gateway.
- Rejects ambiguous certificates that contain multiple allow-listed coordinator URI SANs.
- Adds signed 429 paths, aggregate-only operational reporting, and three identity fairness regression tests.
- Stabilizes outage-fixture cleanup; completed gateway suite runs cleanly.
- Preserves remote witness/quorum history and the v4.1 pre-TLS controls.
- No upstream code changes or hosted service calls.
