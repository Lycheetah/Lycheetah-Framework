# Threat Model v4.0 — End-to-End mTLS Registry Ingress

## Security objective

Ensure a coordinator-facing registry request must traverse authenticated encrypted transport, must originate from a specifically authorized coordinator certificate identity, and must also satisfy the existing HMAC/replay and checkpoint-quorum controls before it mutates registry state.

## Threats tested

1. Client has no certificate, despite trusting the server CA.
2. Client cert chains to the same CA but contains a different URI SAN.
3. Client connects using the wrong server hostname.
4. Caller attempts cleartext HTTP.
5. Valid body is changed after HMAC signature construction.
6. Wrong request HMAC.
7. Same request ID and same payload is replayed; response is cached and mutation is not repeated.
8. Same request ID is reused with a changed payload; request is rejected as conflict.
9. Non-POST method, duplicate Content-Length, oversized body, and wrong HTTP framing.
10. Valid authorized request travels through the TLS gateway and four mTLS witness subprocesses and returns an anchored result.
11. Application response signature is verified and shown to bind status/body/server-key/request-ID.

## Defence layers

- TLS verifies certificates and protects transport confidentiality/integrity.
- Application URI-SAN allowlisting restricts an otherwise CA-trusted client to the configured coordinator identity.
- HMAC binds method/path/timestamp/request ID/body digest and persists replay consumption.
- Existing RegistryQuorumAnchor / remote witness layers supply Ed25519 witness evidence, quorum rules, anti-rollback checks and durable checkpointing.
- The response envelope is signed independently of transport and must be verified by callers.

## Explicitly out of scope

- Independent hosts, administrators, storage operators or key custodians. The four witness processes and registry share one machine in the tests.
- Production CA governance, certificate revocation, rotation and compromise recovery.
- Distributed rate limiting, connection quotas, worker-pool bounds, denial-of-service testing or network fault testing across hosts.
- Byzantine compromise of the coordinator with its valid client certificate, HMAC key and registry signing permissions.
- Strong anti-rollback under a privileged attacker who can restore all local databases and key material together. The existing external-quorum negative control remains.
- Real deployments, live provider systems or upstream GitHub modifications.

## Failure policy

Unknown transport identity, signature, request shape or quorum state must fail closed. A rejected transport request must not advance registry or checkpoint state. The test suite asserts state/quorum status remains unchanged for invalid-client, HMAC and framing cases.
