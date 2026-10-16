# API Contract v3.2 — Checkpoint Witness Quorum

## Primary record

Input is an existing v3.1 primary anchor record envelope. `CheckpointWitness.attest(record)` calls `verify_record` against the configured primary anchor key registry before issuing any vote.

## Witness vote

The signed witness statement contains exactly:

- protocol version
- witness ID
- database ID
- sequence number
- primary record SHA-256
- previous primary record SHA-256
- logical database SHA-256
- primary anchor server key ID

Signature domain: `lycheetah-checkpoint-witness-v3.2\n`. The witness key must be pinned by the verifier. Votes from duplicate or untrusted witness IDs do not count.

## Witness sequence rule

For database `D`, a witness can attest genesis only at sequence 1 with no parent. Every subsequent head must have sequence `current + 1` and parent hash equal to the guard's current record hash. Repeated requests for the current identical head return the same stored vote. A conflicting head at a locked sequence is rejected.

The local vote ledger is not treated as the monotonic trust root. The external guard's sequence/hash must agree before a stored vote is reissued. If a crash occurs after guard advance but before local vote persistence, the same head can be re-signed deterministically; a different head cannot advance from the guard's now-current value.

## Quorum certificate

`create_certificate()` requires unique votes over the exact verified primary head, a pinned roster, and a quorum calculated from the verifier's configured Byzantine-fault budget. The certificate contains the anchor record, sorted votes, roster digest and a canonical certificate digest.

`verify_certificate()` checks a single certificate's primary signature, roster, vote signatures, quorum threshold, head binding and certificate digest. A single non-genesis certificate is not a full history proof. Use `verify_certificate_chain()` to verify a contiguous chain beginning at genesis (or implement an equivalent check from a previously pinned trusted head).

## Freshness

The client creates a high-entropy challenge with `new_freshness_challenge()` and asks each witness for `report_head(database_id, challenge_nonce)`. `verify_fresh_head_quorum()` validates unique witness IDs, trusted signatures, challenge equality, signed timestamps and a quorum reporting the same head. `verify_current_chain()` refuses a chain whose tip is not equal to that nonce-fresh quorum head.

Freshness depends on the verifier's clock and the operational independence of witnesses/guards. A nonce blocks replay of old reports, but does not compensate for a witness signing key compromise or a compromised non-monotonic guard.

## Equivocation evidence

`find_equivocation(cert_a, cert_b, ...)` only succeeds for two independently verifiable quorum certificates with different primary record hashes at the same database sequence. The returned output includes each overlapping witness's two signed votes. This is evidence of double-signing under the pinned identity; it is not, by itself, a response/incident-handling system.
