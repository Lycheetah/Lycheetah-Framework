# Lycheetah Integrity-Key Rotation v2.9 — Design & Threat Model

## Problem

The v2.8 inbox, queue, and operation ledger authenticate persisted rows with one externally supplied integrity key. Replacing that key without re-signing data makes otherwise intact rows fail verification; changing the key in the environment alone is therefore unsafe. Key rotation is explicitly an operational concern, and an untested migration could corrupt the trusted recovery state.

## Decision

Implement an **offline, single-transaction re-signing utility** for the exact v2.8 row formats instead of adding an untested key-ID migration to runtime code. The utility:

1. requires a database file and distinct old/new keys, each at least 32 bytes;
2. validates the old key against every row in each of the three tables before backup;
3. makes a consistent SQLite API backup and restricts its file mode to `0600` where supported;
4. obtains `BEGIN EXCLUSIVE`, compares the live logical database fingerprint with the backup fingerprint, and revalidates all rows;
5. re-signs only the `row_hmac_sha256` fields under the new key, preserving operation states, claims, raw-payload hashes, provider observations and event identity;
6. verifies all new MACs while still in the transaction, commits once, and independently verifies the new-key database;
7. prints only status, counts, backup path and database file digests.

Each record type uses its existing v2.8 MAC method so that the new key is compatible with the current v2.8 runtime after it is configured with that key. This is key replacement, not a format change. The operation-ledger HMAC keeps its existing domain prefix. The inbox and queue currently use their existing canonical field projections and no explicit MAC-version identifier.

## Threats mitigated by this utility

- accidental key replacement without re-signing stored rows;
- wrong old key, malformed schema, or any pre-existing invalid row causing partial migration;
- same-key no-op mistaken for rotation;
- target backup overwritten accidentally;
- re-sign failure halfway through leaving mixed-key rows;
- changes to database content between consistent backup and exclusive transaction (detected by logical fingerprint);
- raw integrity-key values appearing in command-line args or output, assuming secret-manager environment injection is configured correctly.

## Threats not mitigated

- online/running writer or deployment orchestration errors beyond the SQLite transaction and logical-fingerprint guard;
- compromise of either integrity key, process memory, host, filesystem administrator, or SQLite library;
- deletion, whole-database rollback to an older valid snapshot, or malicious restoration of the pre-rotation backup;
- confidentiality of database or backup contents;
- stale backup retention, key manager compromise, unsecure environment injection, or logs outside this script;
- rolling rotation across multiple databases or multiple replicas;
- incompatible future schema versions or a future change to row MAC projections without a matching migration;
- correctness of Stripe payment/refund operations or upstream Lycheetah authorization semantics.

## Model boundaries

The tests seed all three row tables via the v2.8 source modules, rotate a disposable database, and read the resulting state through the v2.8 implementation. No hosted Stripe API is called. This validates local format compatibility, atomicity at the SQLite transaction boundary, backup usability, and refusal behavior. It does not establish production readiness.

## Promotion gate

Before upstream integration: full source checkout; clean non-default branch; exact source pin; review how the deployed HMAC key is injected; confirm whether all production state is in this one database; run the project suite and CI; rehearse backup/restore in a disposable environment; require security review of key storage and rollback operations. Online multi-key rotation should be a separate design if downtime is unacceptable.
