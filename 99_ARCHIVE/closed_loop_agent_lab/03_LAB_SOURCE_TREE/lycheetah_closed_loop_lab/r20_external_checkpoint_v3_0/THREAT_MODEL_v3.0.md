# Threat Model — External Monotonic Checkpoint v3.0

## Threat addressed

A database attacker, storage failure, or unsafe recovery procedure restores a once-valid older SQLite snapshot. Row HMAC verification alone can succeed because the old rows and their MACs are internally consistent. The system needs a freshness reference outside that snapshot.

## Assets and trust domains

1. **Primary DB integrity key:** validates row HMACs on the known inbox, queue, and operation-ledger tables.
2. **Anchor authentication key:** HMAC-authenticates checkpoint records. It must be separate from the primary DB key.
3. **Operator approval key:** signs a short-lived approval for one exact proposed database fingerprint and one exact current checkpoint parent. It must be unavailable to model-driven runtime code.
4. **External monotonic anchor:** authoritative latest sequence and digest chain. Production must protect this in a separate administrative, durability, and rollback domain.

## Invariants enforced by the reference implementation

- A database with invalid row HMACs cannot be checkpointed or marked ready.
- A checkpoint record binds database identity, schema digest, data digest, full logical digest, table counts, parent hash, approval ID/nonce, timestamp, reason code, and anchor key ID.
- The logical hash is recomputed from schema and data hashes; callers cannot pass inconsistent subdigests.
- An approval must be authentic, unexpired, single-use, bound to the exact current parent hash, database identity, and exact proposed logical digest.
- Checkpoint appends use a locked, compare-and-swap sequence/head check; concurrent attempts with the same parent cannot both append.
- Current state differing from the latest checkpoint returns a non-ready result. If it matches an older checkpoint, it is labelled `STALE_SNAPSHOT`; any other same-schema mismatch is `CHECKPOINT_MISMATCH`; schema drift is `SCHEMA_CHANGED`.
- An invalid or incomplete anchor chain returns `ANCHOR_UNVERIFIED` and never `safe_to_continue=true`.

## Recovery policy

Any status other than `MATCH` blocks normal processing. The remedy is not to re-sign rows or blindly publish the current snapshot. Investigate the incident, validate against the provider and external evidence, obtain a new independent change approval for the exact candidate state, then publish a new checkpoint. If state/history may be lost, reconcile before checkpointing.

## Limits and non-claims

- The included `SQLiteReferenceAnchor` proves the protocol mechanics only when the anchor store is preserved independently of the primary DB. It does not resist a coordinated rollback of both local SQLite files.
- HMAC keys can forge records if compromised; HMAC does not encrypt data or prove who a human is unless key custody and issuer authorization are separately controlled.
- Publication is not an atomic distributed transaction between primary SQLite and a remote anchor. The adapter must guarantee durable compare-and-swap; a production connector must handle uncertain append responses by retrieving the authoritative head and reconciling, not by guessing.
- The reference code fingerprints a consistent SQLite logical snapshot; a deployment must serialize all writers and prevent filesystem replacement during checkpointing. It is not a multi-writer cloud database transaction manager.
- This does not establish atomicity with Stripe or another external provider, and it does not certify production security.
