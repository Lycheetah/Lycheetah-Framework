# Changelog v4.1 — Bounded mTLS Ingress

See `r31_bounded_mtls_ingress_v4_1/CHANGELOG_v4.1.md` for implementation details.

This iteration adds pre-TLS global/per-peer connection limits and a process-local connection token bucket. The 38-method retained quorum suite and 44-method mTLS gateway/witness suite passed separately; source pins and compilation passed. Sequential wrapper invocations have intermittently timed out in this environment, so verification logs are retained and suites are exposed as separate runner invocations.

No hosted services were called. No upstream source or CI changed. This is not production DDoS certification; the global bucket is not identity-aware or distributed.
