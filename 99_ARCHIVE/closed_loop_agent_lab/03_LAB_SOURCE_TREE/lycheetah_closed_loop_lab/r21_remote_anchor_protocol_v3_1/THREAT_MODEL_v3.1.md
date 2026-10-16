# Threat Model v3.1 — Remote Anchor Protocol

## Threats addressed in the reference protocol

- Lost HTTP response after the server commits a checkpoint.
- Duplicate/replayed API request nonce inside the accepted timestamp window.
- Reuse of a publish-request ID with changed content.
- Two checkpoint publishers race using the same prior sequence/head.
- Forged or modified operator approval, including an unknown signing key.
- Forged or modified server response/record.
- Restored/tampered service history indexes that disagree with signatures, parent links, request results or approval-use rows.
- Local outbox row edits and attempts to rewrite terminal states.
- Authenticated requests redirected to a different URL.
- Oversized inbound request body.

## Principal invariants

1. Operator authorization is a detached Ed25519 signature and binds the full logical snapshot plus exact parent checkpoint and stable request ID.
2. Every append uses a serialized transaction and exact compare-and-swap against sequence and head.
3. The service verifies full existing history before replaying an old request or extending the chain.
4. The request result table, checkpoint sequence and approval-use index must exactly agree with the signed history.
5. Server responses and checkpoint records must verify against an explicitly pinned Ed25519 public key.
6. An ambiguous result stays `UNKNOWN` until an authoritative status lookup or exact same-ID retry establishes the result.
7. Request payloads and status responses are bound to the same database ID and request ID.
8. Terminal local outbox states cannot be modified through the public state transition API.

## Trust domains

- Agent/worker carries a client API credential and an outbox integrity key. It must not hold the operator signing private key.
- Operator approval process holds the Ed25519 private key and signs one exact change.
- Anchor service has configured operator public keys, API-client HMAC keys, and its own record/response signing private key.
- Client pins the service public key separately.

## Out of scope / not proven

- The reference server's SQLite database is not a real remote monotonic/WORM anchor. An attacker with full access to that database can remove triggers, alter storage or roll back the database file; signature checks expose ordinary edits, but coordinated full-store rollback cannot be detected without a trusted external high-water mark.
- Key custody, person-level operator identity, approval UI, signer revocation, remote service availability, TLS certificate setup, distributed database behavior and production deployment isolation are not implemented here.
- The protocol does not make primary-database state and remote anchor append a distributed atomic transaction. It makes uncertain outcomes discoverable and retriable under a stable ID.
- It does not bind a remote Stripe refund to the checkpoint; no Stripe API calls or refunds were performed.
