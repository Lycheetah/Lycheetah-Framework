# Upstream Integration Plan v3.9

## Promotion gates

1. Run this reference pack's source pin and separate regression invocations.
2. Integrate TLS context creation behind an explicit transport configuration boundary; do not silently change existing default host deployments.
3. Define production CA trust, URI identity namespace, certificate rotation/revocation, time synchronization, and secret delivery before enabling network hosts.
4. Add bounded concurrency, rate limiting, structured redacted audit logs, and TLS/HTTP telemetry.
5. Test actual certificates and service DNS on independently administered staging hosts. Verify the server cert SAN and client identity mapping for every witness.
6. Exercise process restarts, response-loss recovery, slow TLS clients, one-/two-witness outages, and backup restoration on those staging hosts.
7. Run the full upstream package test suite and CI; compare against a recorded clean baseline.
8. Promote only after review by a second engineer/security reviewer. Do not merge just because the local test harness passes.

## Scope discipline

The current reference directory is additive and derived from the v3.8 research pack. It is not an upstream patch and has not changed `Lycheetah-Framework`. Production mTLS is a separate deployment capability, not by itself an independent trust domain or an anti-rollback guarantee.
