# Lycheetah External Monotonic Checkpoint v3.0

**Purpose:** detect a restored stale SQLite snapshot, an uncheckpointed valid state change, or schema/data drift in the Lycheetah webhook inbox, reconciliation queue, operation ledger, and any other tables in the same database.

The local database's row HMACs protect signed rows against edits by parties without the primary integrity key. They do not prove freshness: a previously valid database backup still contains valid HMACs. v3.0 binds the logical database state to a separate monotonically appended checkpoint chain and requires an operator-HMAC-authenticated approval to publish a new state.

## Contents

- `external_checkpoint.py` — logical snapshot fingerprinting, strict approval checks, a `MonotonicAnchor` protocol, a SQLite reference adapter, checkpoint publication, and a fail-closed startup gate.
- `external_checkpoint_cli.py` — fingerprint, verify, and approval-gated publish modes. Secrets are read from environment variables, never command-line arguments.
- `test_external_checkpoint.py` — adversarial regression suite, including stale snapshot restoration, anchor-record tamper detection, operator approval binding, and competing checkpoint CAS writes.
- `operation_ledger.py`, `stripe_webhook_inbox.py`, `integrity_key_rotation.py` — source-pinned test dependencies copied from the v2.9 reference pack.
- `RESULTS_v3.0.md`, `THREAT_MODEL_v3.0.md`, `SOURCE_PIN_v3.0.json` — findings, assumptions, limitations, and observed source revision.

## Run focused tests

```bash
python -W error::ResourceWarning -m unittest -v test_external_checkpoint.py
```

Python standard library only.

## CLI modes

- `--mode fingerprint`: verify the three known authenticated tables, then return a logical fingerprint of the entire SQLite database. No checkpoint is written.
- `--mode verify`: compare the current primary database to the latest independently stored checkpoint. Exit 0 only for `MATCH`; exit 3 for a fail-closed mismatch; exit 2 for an invalid invocation or unusable secret/store.
- `--mode publish`: requires a short-lived, operator-HMAC-signed approval JSON bound to the database ID, previous checkpoint hash, and exact proposed logical database hash. This must be issued by a trusted change-approval process separate from the agent/runtime.

Example verification (key bytes supplied as base64 through a secret manager, never on the command line):

```bash
export LYC_PRIMARY_INTEGRITY_KEY_B64='...'
export LYC_EXTERNAL_ANCHOR_KEY_B64='...'
python external_checkpoint_cli.py --mode verify \
  --database /secure/operations.sqlite \
  --database-id lycheetah.operations.main \
  --anchor-database /separate-protected-store/anchor.sqlite \
  --anchor-key-id ops-anchor-v1
```

## Important deployment boundary

`SQLiteReferenceAnchor` is a **test/reference store**, not a genuinely remote anti-rollback service. The primary and anchor SQLite files must be in separate protection/backup domains. If an attacker can restore both files to the same earlier valid pair, this local reference adapter cannot know that a later history once existed. Production must implement `MonotonicAnchor` using an independently controlled, append-only/compare-and-swap store with a non-rollbackable high-water mark (for example, a remote service with write-once audit retention). Do not describe a pair of local SQLite files as protection against a full-host rollback.

This version is an offline recovery/maintenance checkpoint tool, not an automatic per-transaction publisher. Normal service writes after a checkpoint intentionally cause `CHECKPOINT_MISMATCH` until a new trusted checkpoint is approved and published. Do not install it as a startup gate for a continuously changing database without a transactionally coupled checkpoint outbox and an independently authorized automatic publisher.

Checkpoint publication is an offline/single-writer maintenance procedure. It reserves the primary SQLite writer lock while taking the snapshot and appending the external checkpoint; the caller must still prevent filesystem-level replacement and non-SQLite writers. No remote Stripe APIs are called, no real refunds are created, and this research artifact does not modify the upstream Lycheetah repository.
