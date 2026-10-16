"""Offline, atomic whole-database HMAC-key rotation for Lycheetah v2.8 stores.

This utility intentionally rotates the shared key for all three authenticated
SQLite tables in one transaction. It is not online/rolling key rotation.
Stop every writer/worker before invoking it. A mode-0600 SQLite backup is made
first; the database is fully verified with the old key before any HMAC is changed.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import closing
import base64
import hashlib
import hmac
import os
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from operation_ledger import LEDGER_FIELDS, LEDGER_TABLE, operation_row_mac
from stripe_webhook_inbox import StripeWebhookInbox

INBOX_TABLE = "stripe_webhook_inbox"
QUEUE_TABLE = "stripe_reconciliation_jobs"
REQUIRED_TABLES = (INBOX_TABLE, QUEUE_TABLE, LEDGER_TABLE)

INBOX_REQUIRED = {
    "event_id", "event_type", "event_created", "event_account", "refund_id",
    "charge", "payment_intent", "amount", "currency", "refund_status",
    "operation_id", "livemode", "payload_sha256", "signature_timestamp",
    "signing_secret_label", "received_at", "row_hmac_sha256",
}
QUEUE_REQUIRED = {
    "event_id", "operation_id", "refund_id", "event_account", "charge",
    "payment_intent", "amount", "currency", "state", "attempts",
    "available_at", "claimed_by", "claim_token_sha256", "lease_until",
    "last_error_code", "created_at", "updated_at", "row_hmac_sha256",
}
LEDGER_REQUIRED = set(LEDGER_FIELDS) | {"row_hmac_sha256"}


class KeyRotationError(ValueError):
    """Key rotation refused; source DB was not modified by this invocation."""


@dataclass(frozen=True)
class RotationResult:
    inbox_rows: int
    queue_rows: int
    operation_rows: int
    backup_path: str
    source_sha256_before: str
    source_sha256_after: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "ROTATED",
            "inbox_rows": self.inbox_rows,
            "queue_rows": self.queue_rows,
            "operation_rows": self.operation_rows,
            "backup_path": self.backup_path,
            "source_sha256_before": self.source_sha256_before,
            "source_sha256_after": self.source_sha256_after,
        }


def _validate_key(key: bytes, name: str) -> None:
    if not isinstance(key, bytes) or len(key) < 32:
        raise KeyRotationError(f"{name} must be at least 32 bytes")


def _connect(path: str | Path, *, readonly: bool = False) -> sqlite3.Connection:
    p = Path(path).resolve()
    if readonly:
        db = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True, timeout=10)
    else:
        db = sqlite3.connect(str(p), timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    if not readonly:
        db.execute("PRAGMA synchronous=FULL")
    return db


def _table_columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {str(r[1]) for r in db.execute(f"PRAGMA table_info({table})").fetchall()}


def _require_schema(db: sqlite3.Connection) -> None:
    existing = {str(r[0]) for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    missing_tables = [name for name in REQUIRED_TABLES if name not in existing]
    if missing_tables:
        raise KeyRotationError("required authenticated tables missing: " + ",".join(missing_tables))
    for table, needed in ((INBOX_TABLE, INBOX_REQUIRED), (QUEUE_TABLE, QUEUE_REQUIRED),
                          (LEDGER_TABLE, LEDGER_REQUIRED)):
        missing = needed - _table_columns(db, table)
        if missing:
            raise KeyRotationError(f"schema incomplete for {table}: {','.join(sorted(missing))}")


def _probes(key: bytes) -> tuple[Any, Any]:
    inbox_probe = object.__new__(StripeWebhookInbox)
    inbox_probe.integrity_key = key
    return inbox_probe, None


def _rows(db: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return [dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()]


def _logical_fingerprint(db: sqlite3.Connection) -> str:
    """Fingerprint authenticated-table contents, independent of SQLite file layout."""
    body: dict[str, Any] = {}
    for table in REQUIRED_TABLES:
        columns = [str(r[1]) for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
        body[table] = {"columns": columns, "rows": _rows(db, table)}
    encoded = __import__("json").dumps(
        body, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mac_for(table: str, row: Mapping[str, Any], inbox_probe: Any, key: bytes) -> str:
    if table == INBOX_TABLE:
        return inbox_probe._mac(row)
    if table == QUEUE_TABLE:
        return inbox_probe._job_mac(row)
    return operation_row_mac(key, row)


def verify_database(path: str | Path, key: bytes) -> dict[str, int]:
    """Verify every authenticated row without changing the database."""
    _validate_key(key, "integrity key")
    inbox_probe, _ = _probes(key)
    counts: dict[str, int] = {}
    db = _connect(path, readonly=True)
    try:
        _require_schema(db)
        for table in REQUIRED_TABLES:
            rows = _rows(db, table)
            for row in rows:
                expected = _mac_for(table, row, inbox_probe, key)
                supplied = row.get("row_hmac_sha256")
                if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
                    raise KeyRotationError(f"integrity verification failed for {table}; no rows rotated")
            counts[table] = len(rows)
    except sqlite3.Error:
        raise KeyRotationError("database verification failed; no rows rotated") from None
    finally:
        db.close()
    return counts


def _snapshot_backup(source: Path, backup: Path) -> None:
    if source.resolve() == backup.resolve():
        raise KeyRotationError("backup path must differ from source database")
    if backup.exists():
        raise KeyRotationError("backup path already exists; refusing to overwrite")
    backup.parent.mkdir(parents=True, exist_ok=True)
    src = None
    dest = None
    try:
        src = _connect(source, readonly=True)
        dest = sqlite3.connect(str(backup))
        src.backup(dest)
        dest.commit()
        os.chmod(backup, 0o600)
    except Exception:
        try:
            backup.unlink(missing_ok=True)
        except OSError:
            pass
        raise KeyRotationError("database backup failed; source was not modified") from None
    finally:
        if dest is not None:
            dest.close()
        if src is not None:
            src.close()


def rotate_integrity_key(path: str | Path, *, old_key: bytes, new_key: bytes,
                         backup_path: str | Path) -> RotationResult:
    """Re-sign all authenticated rows under ``new_key`` atomically.

    This is an offline whole-database rotation. Stop webhook receivers, workers,
    and all other DB writers first. The backup remains signed with old_key.
    """
    _validate_key(old_key, "old_key")
    _validate_key(new_key, "new_key")
    if hmac.compare_digest(old_key, new_key):
        raise KeyRotationError("new key must differ from old key")

    source = Path(path).resolve()
    backup = Path(backup_path).resolve()
    if not source.is_file():
        raise KeyRotationError("source database must already exist as a file")

    # Validate before creating a backup, so a wrong key or corrupted row does not
    # cause a misleading 'rotation backup' to be emitted.
    counts_before = verify_database(source, old_key)
    source_digest_before = _file_sha256(source)
    _snapshot_backup(source, backup)
    backup_conn = _connect(backup, readonly=True)
    try:
        _require_schema(backup_conn)
        backup_fingerprint = _logical_fingerprint(backup_conn)
    finally:
        backup_conn.close()

    inbox_old, _ = _probes(old_key)
    inbox_new, _ = _probes(new_key)
    counts: dict[str, int] = {}
    db = _connect(source)
    try:
        db.execute("BEGIN EXCLUSIVE")
        _require_schema(db)
        # Compare logical content against the consistent backup after acquiring
        # the write lock. If a writer changed even a same-count row during the
        # backup/lock window, do not rotate from a stale recovery point.
        if _logical_fingerprint(db) != backup_fingerprint:
            raise KeyRotationError("database changed after backup; rotation aborted")
        # Reverify after obtaining the write lock. No changes are made until
        # every row in all three tables has validated with the old key.
        table_rows = {table: _rows(db, table) for table in REQUIRED_TABLES}
        for table, rows in table_rows.items():
            for row in rows:
                expected = _mac_for(table, row, inbox_old, old_key)
                supplied = row.get("row_hmac_sha256")
                if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
                    raise KeyRotationError(f"integrity verification failed for {table}; rotation aborted")
            counts[table] = len(rows)
        if counts != counts_before:
            raise KeyRotationError("database row counts changed since preflight; rotation aborted")

        # Re-sign each record in a single SQLite transaction.
        for table, rows in table_rows.items():
            pk = "operation_id" if table == LEDGER_TABLE else "event_id"
            for row in rows:
                new_mac = _mac_for(table, row, inbox_new, new_key)
                db.execute(f"UPDATE {table} SET row_hmac_sha256=? WHERE {pk}=?",
                           (new_mac, row[pk]))

        # Verify all new MACs before commit so a malformed row or coding error
        # rolls back the entire rotation rather than leaving a mixed-key DB.
        for table in REQUIRED_TABLES:
            for row in _rows(db, table):
                expected = _mac_for(table, row, inbox_new, new_key)
                if not hmac.compare_digest(str(row.get("row_hmac_sha256", "")), expected):
                    raise KeyRotationError(f"post-rotation verification failed for {table}; rotation aborted")
        db.commit()
    except KeyRotationError:
        if db.in_transaction:
            db.rollback()
        raise
    except Exception:
        if db.in_transaction:
            db.rollback()
        raise KeyRotationError("rotation failed; transaction rolled back if not committed") from None
    finally:
        db.close()

    # Independent post-commit verification. If this fails, the backup is retained
    # for recovery, and callers must not restart the service with an assumed key.
    post_counts = verify_database(source, new_key)
    if post_counts != counts:
        raise KeyRotationError("post-commit row counts differ; retain backup and investigate")
    source_digest_after = _file_sha256(source)
    # Rows may be empty (or SQLite may use WAL mode), so a changed main-file hash
    # is informative but not used as the correctness criterion. Row MACs and counts
    # were independently checked above.
    return RotationResult(counts[INBOX_TABLE], counts[QUEUE_TABLE], counts[LEDGER_TABLE],
                          str(backup), source_digest_before, source_digest_after)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_key_from_env(name: str) -> bytes:
    value = os.environ.get(name)
    if not value:
        raise KeyRotationError(f"required environment variable {name} is missing")
    try:
        key = base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error):
        raise KeyRotationError(f"environment variable {name} must contain base64 key bytes") from None
    _validate_key(key, name)
    return key


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Offline, all-table integrity-key rotation for the Lycheetah v2.8 SQLite reference stores."
    )
    parser.add_argument("--database", required=True, help="existing SQLite database path")
    parser.add_argument("--backup", help="new, protected backup path required for rotation")
    parser.add_argument("--old-key-env", default="LYCHEETAH_OLD_INTEGRITY_KEY_B64")
    parser.add_argument("--new-key-env", default="LYCHEETAH_NEW_INTEGRITY_KEY_B64")
    parser.add_argument("--verify-only", action="store_true", help="verify all rows under old key without mutation")
    args = parser.parse_args(argv)
    try:
        old_key = decode_key_from_env(args.old_key_env)
        if args.verify_only:
            counts = verify_database(args.database, old_key)
            print(json.dumps({"status": "VERIFIED", "rows": counts}, sort_keys=True))
            return 0
        if not args.backup:
            parser.error("--backup is required unless --verify-only is set")
        new_key = decode_key_from_env(args.new_key_env)
        result = rotate_integrity_key(
            args.database, old_key=old_key, new_key=new_key, backup_path=args.backup
        )
        print(json.dumps(result.to_dict(), sort_keys=True))
        return 0
    except KeyRotationError as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
