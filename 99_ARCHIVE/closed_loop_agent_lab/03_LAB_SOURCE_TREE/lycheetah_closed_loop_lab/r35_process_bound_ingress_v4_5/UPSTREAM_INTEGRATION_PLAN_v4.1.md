# Upstream Integration Plan v4.1

1. Rebase the gateway on a fresh upstream checkout without copying reference-only registry/witness files as if they were upstream source.
2. Preserve v4.0 transport/HMAC/quorum tests and add pre-handshake concurrency/rate limits using the production server/framework primitives.
3. Decide a deployment rate-control model: per authenticated coordinator identity at a trusted proxy, plus network-level global caps. Do not present the process-local token bucket as the production rate-limiting design.
4. Add OS-level limits, slow-header tests, bounded TLS handshakes, graceful shutdown and connection metrics without logging secret request material.
5. Run supported Python-version CI and a bounded load profile across a staged multi-host topology, including certificate rotation/revocation and quorum outage.
6. Conduct code review and ensure all changes are on a non-default branch. No claim of production readiness before upstream tests and deployment gates pass.

## Repository status

The GitHub integration has returned HTTP 403 for branch creation in earlier iterations. v4.1 is a local reference change only; no upstream file or CI pipeline was modified.
