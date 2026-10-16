# Lycheetah Integrity-Key Rotation v2.9

A reference utility to rotate the single local integrity key used by the v2.8 authenticated webhook inbox, reconciliation queue, and operation ledger. It validates all records, creates a protected consistent backup, revalidates after taking an exclusive transaction, re-signs the three table families atomically, then checks the new key.

## Run tests

```bash
python -W error::ResourceWarning -m unittest -v test_integrity_key_rotation.py
```

## Verify a database without mutation

Set `LYCHEETAH_OLD_INTEGRITY_KEY_B64` through your secret manager, then:

```bash
python integrity_key_rotation.py --database /secure/path/operations.sqlite --verify-only
```

## Rotate offline

Stop all DB readers/writers and use base64-encoded key bytes from the secret manager in `LYCHEETAH_OLD_INTEGRITY_KEY_B64` and `LYCHEETAH_NEW_INTEGRITY_KEY_B64`:

```bash
python integrity_key_rotation.py \
  --database /secure/path/operations.sqlite \
  --backup /secure/backups/operations.pre-rotation.sqlite
```

Read `ROTATION_RUNBOOK_v2.9.md` before running any real database. This is not online rotation: all services using the DB must be stopped and restarted with the new key together. The script only covers local HMAC integrity keys—not Stripe API keys or webhook signing secrets. It is a reference tool, not an approved production migration without review and rehearsal.
