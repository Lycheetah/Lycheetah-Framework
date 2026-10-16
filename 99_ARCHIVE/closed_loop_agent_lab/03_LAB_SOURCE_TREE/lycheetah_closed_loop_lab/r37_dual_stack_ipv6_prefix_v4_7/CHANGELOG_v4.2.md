# Changelog v4.2 — Authenticated Coordinator Fairness

- Added per-authenticated-coordinator active-dispatch limits after the client TLS certificate is verified and mapped to exactly one allow-listed SPIFFE URI SAN.
- Added a per-coordinator request token bucket, separate from the pre-TLS global connection-rate bucket.
- Rejects certificates that contain multiple URI SANs which independently match the configured coordinator allowlist; the gateway no longer picks an arbitrary principal.
- Adds aggregate rejection counters and active-principal counts without exposing URI SANs or request content in operational snapshots.
- Adds integration tests for same-principal concurrency saturation, cross-principal quota isolation, signed 429 responses, ambiguous-identity rejection, and no mutation on ambiguous identity.
- Restores stopped witness subprocesses at the end of the two-witness outage test; this avoids a second unnecessary restart during the subsequent restart-persistence test. The completed 47-test gateway suite then ran cleanly.
- Preserves v4.1 pre-TLS resource bounds, TLS 1.2+, URI-SAN identity pinning, request HMAC, signed response envelope, replay control, multi-process witness and checkpoint quorum tests.
- Limits remain local to one process; no claim of distributed fairness, production DDoS resistance, or cross-host identity quota is made.
- No hosted services called; no upstream source or CI changes.
