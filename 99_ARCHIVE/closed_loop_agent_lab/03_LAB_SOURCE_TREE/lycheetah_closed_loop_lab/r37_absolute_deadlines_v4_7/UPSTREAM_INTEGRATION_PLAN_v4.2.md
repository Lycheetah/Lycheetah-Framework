# Upstream Integration Plan v4.2

1. Rebase the gateway change on a clean checkout, preserving upstream files rather than copying the local witness simulation wholesale.
2. Keep v4.1 pre-TLS limits and add post-mTLS principal quotas using the production framework's supported authentication/context API.
3. Decide whether coordinator identity quotas belong at a trusted API gateway, shared distributed limiter, or service layer. Do not rely on in-process dictionaries as a fleet-wide quota.
4. Add authenticated-principal concurrency, rate-isolation, ambiguous-certificate and overload tests to the upstream CI matrix.
5. Measure quota enforcement when requests arrive through the intended proxy/topology, including trusted peer identity derivation and slow-header behavior.
6. Run supported Python-version CI, load and soak tests, TLS certificate rotation/revocation procedures, shutdown/drain tests, and a multi-host quorum outage test.
7. Review privacy of metrics: aggregate counters only by default, with explicit retention/authorization if identity-level audit telemetry is added.

## Repository status

The connected GitHub integration denied branch creation (HTTP 403) in earlier iterations. v4.2 is a local reference change only; no upstream file or CI pipeline was changed.
