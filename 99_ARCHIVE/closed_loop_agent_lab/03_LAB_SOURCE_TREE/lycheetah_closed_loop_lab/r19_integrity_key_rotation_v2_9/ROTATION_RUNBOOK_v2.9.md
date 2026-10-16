# Offline Integrity-Key Rotation Runbook v2.9

## Scope

This utility rotates the **local SQLite row-authentication key** used by the v2.8 reference webhook inbox, reconciliation queue, and operation ledger. It does **not** rotate Stripe API credentials (`sk_test_...`), Stripe webhook signing secrets (`whsec_...`), or keys used by any other component.

The reference implementation supports **offline whole-database rotation**, not online dual-key verification or a rolling fleet rotation. All services that read or write the database must be stopped for the procedure. It expects the three authenticated tables to be present in one SQLite file:

- `stripe_webhook_inbox`
- `stripe_reconciliation_jobs`
- `lycheetah_refund_operation_ledger`

## Preconditions

1. Stop webhook receivers, workers, cron jobs, admin tasks, and any other database readers/writers that might change state. The script re-checks after taking a consistent backup, but that check is defense in depth, not a substitute for maintenance mode.
2. Take and test the normal deployment backup procedure. Ensure protected storage capacity and filesystem permissions.
3. Retrieve both old and new integrity keys from the approved secret manager. Each must be at least 32 bytes and must differ. This script accepts base64-encoded key bytes through environment variables so the actual values are not command-line arguments. Do not `echo` them, paste them into logs, or commit them.
4. Verify you have an operator-approved recovery plan. The utility's generated backup remains signed under the old key and contains operational metadata; store it with restrictive permissions and retention.
5. Pin the Python runtime and review the exact script copy before running it. This standalone artifact is a reference utility, not a signed release binary.

## Verify first (read-only)

Set `LYCHEETAH_OLD_INTEGRITY_KEY_B64` from the secret manager and run:

```bash
python integrity_key_rotation.py --database /secure/path/operations.sqlite --verify-only
```

A successful result reports row counts only. Any missing table, wrong key, or invalid row HMAC refuses to proceed. Do not bypass a verification failure or regenerate HMACs for rows that did not verify.

## Rotate

Inject the old and new integrity keys through the deployment secret manager as:

- `LYCHEETAH_OLD_INTEGRITY_KEY_B64`
- `LYCHEETAH_NEW_INTEGRITY_KEY_B64`

Then run with a **new, non-existing** protected backup path:

```bash
python integrity_key_rotation.py \
  --database /secure/path/operations.sqlite \
  --backup /secure/backups/operations.pre-key-rotation.sqlite
```

The utility verifies all rows with the old key, creates a consistent SQLite backup with owner-only permissions, acquires an exclusive write transaction, checks that the live database still matches the backup's logical contents, verifies again, re-signs every row across all three tables, verifies every new MAC before commit, and then independently verifies the committed database with the new key.

It outputs counts and database SHA-256 file digests, never key material. A refusal is a stop condition, not a request to force the migration.

## Restart and verification

1. Update the service's integrity-key configuration to the new key and start one read-only verifier/health check first.
2. Run `--verify-only` using the new key; it should report the same table counts as the rotation result.
3. Run inbox duplicate/replay and worker read-only smoke checks with the new key. Confirm no old-key-only process remains before resuming webhook ingestion.
4. Resume writers only after all services that share the database use the new key.
5. Keep the old key secured only as long as required to read the encrypted/controlled pre-rotation backup under policy. Destroy it according to key-management policy once restore requirements are satisfied.

## Rollback and crash handling

- Before the SQLite commit, a process failure should roll back the re-signing transaction. The backup remains a verified old-key snapshot.
- If the command returns a refusal, keep services stopped, preserve the database and backup, investigate, and verify again. Do not delete or rewrite rows to make the check pass.
- If rotation committed but startup with the new key fails **and no post-rotation writes have occurred**, the pre-rotation database backup can be restored with the old key under an approved recovery procedure.
- If any writes occurred after rotation, restoring the old snapshot may lose new operations. Prefer an offline reverse rotation from the new key back to the old key with a new protected backup, after validating the current database; involve the incident/recovery owner.
- HMAC protects record integrity against a party without the key. It does not make the database confidential, detect deletion or whole-database rollback, or protect against an attacker who has the key.

## Explicit limitations

- No online key IDs or dual-key read path are implemented. The database has one active row-authentication key at a time.
- The procedure requires downtime and all three tables to share a single SQLite database.
- The tool does not prove that all live processes have stopped; this is an operator responsibility.
- SQLite/filesystem backup semantics and WAL-mode behavior must be tested in the actual deployment. The logical fingerprint guard detects a content change between backup and exclusive transaction, but not malicious storage below SQLite or an attacker with the active key.
- The current Lycheetah upstream source was not changed by this research artifact. Integration should begin only on a clean branch with project-owner review and the full upstream test suite.
