# Threat Model — Registry External Quorum v3.7

## Protected asset

The integrity and freshness of spent-challenge registry state, especially one-use challenge and request-nonce records, as observed by a client before accepting a new protected mutation.

## Adversary capabilities considered in tests

- Restore the registry's SQLite database to an earlier snapshot.
- Restore registry and client-anchor databases together.
- Modify logical registry rows without a matching checkpoint.
- Modify client head, pending intent, response cache, or witness current-head metadata directly in SQLite.
- Submit stale, replayed, incorrectly signed, altered-payload, or duplicate-request-ID requests.
- Corrupt or omit witness votes, present equivocation or split heads, or reuse public keys under multiple witness IDs.
- Drop service responses before or after a state mutation commits.
- Submit requests concurrently through the loopback HTTP boundary.
- Restore every witness database as well as registry and client state (negative control).

## Mitigations modeled

- Client HMAC signatures bind key ID, timestamp, request ID, method, path and body digest.
- Logical state fingerprinting includes the expected tables and schema objects.
- Signed checkpoints form a parent-linked sequence; strict parsing and signature checks reject malformed values.
- Unique witness public keys, nonce-bound signed head reports, freshness checks, and a 3-of-4 certificate quorum resist one faulty witness and split quorums within the configured model.
- Authenticated local rows, schema checks, outbox recovery, file-lock serialization, and signed fail-closed responses guard local operations.

## Explicitly out of scope / not proven

- Four witnesses in local memory/local SQLite are not four independent failure or administrative domains.
- No protection is claimed if all witness stores/keys/administrators/backups are rolled back or compromised together; this is an intentional negative control.
- OS root, process memory access, private-key theft, or compromise of issuer plus all trusted witness keys are not resisted by the local prototype.
- SQLite correctness on a single host does not prove a distributed transaction or consensus protocol under network partitions.
- Upstream application behavior, deployment packaging, real network security, service availability, and external-provider integration have not been audited by this experiment.
- This is not a cryptographic proof or production security certification.

## Operational rule

All protected operations must enter through the guarded dispatcher. Direct writes to the registry DB are outside the contract; the next preflight should detect state divergence and stop. Production requires separately deployed witness services with independent credentials/storage, operational key rotation, backup/restore protocol, authenticated transport, rate limits, monitoring, and externally witnessed recovery.
