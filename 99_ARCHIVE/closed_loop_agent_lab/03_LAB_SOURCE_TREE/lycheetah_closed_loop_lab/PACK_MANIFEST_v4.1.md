# Closed-Loop Agent Lab Manifest v4.1

Current focus: resource-bounded coordinator mTLS ingress, preserving the remote witness quorum, HMAC request authentication, signed responses, replay detection and append-only checkpoints.

Current iteration: `r31_bounded_mtls_ingress_v4_1/`.

- 8 source/reference file fingerprints passed.
- Python compilation passed.
- 38 retained quorum tests passed.
- 44 remote witness/gateway tests passed in a separate invocation.
- 24 concurrent stalled-header clients stayed under the configured four-connection limit in the dedicated burst test; no mutation occurred from those incomplete requests.
- Combined unique test methods: 82.
- No hosted calls, upstream source changes or upstream CI.

Limitations: one host/operator, local test certificates, process-local rate limiting, no distributed DDoS or production CA lifecycle validation. The one-shot sequential runner was intermittent in this environment; logs from completed individual suite runs are preserved.
