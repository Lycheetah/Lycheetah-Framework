"""Reference external monotonic checkpoint protocol for the Lycheetah SQLite lab.

This module detects a stale, altered, or uncheckpointed primary database by comparing
its logical contents with the latest record held by a separate monotonic anchor store.
The SQLite anchor adapter is a test/reference implementation, NOT a tamper-proof remote
anchor. Production requires an independently protected append-only/CAS service.
"""
from __future__ import annotations

import base64
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import math
import os
import re
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Protocol

from integrity_key_rotation import (
    REQUIRED_TABLES, _mac_for, _probes, _require_schema,
    KeyRotationError,
)

ANCHOR_TABLE = "anchor_records"
USED_APPROVAL_TABLE = "used_approvals"
MIN_KEY_BYTES = 32


class CheckpointError(ValueError):
    """Checkpoint could not be safely created or verified."""


def _key_ok(key: bytes, name: str) -> None:
    if not isinstance(key, bytes) or len(key) < MIN_KEY_BYTES:
        raise CheckpointError(f"{name} must be at least {MIN_KEY_BYTES} bytes")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str):
        raise CheckpointError("approval timestamp must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise CheckpointError("approval timestamp is invalid") from None
    if parsed.tzinfo is None:
        raise CheckpointError("approval timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def _canon(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _mac(key: bytes, value: Any) -> str:
    return hmac.new(key, _canon(value), hashlib.sha256).hexdigest()


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _typed_sql_value(value: Any) -> dict[str, str | None]:
    if value is None:
        return {"type": "null", "value": None}
    if type(value) is bool:
        # SQLite normally returns bool-like values as int, but distinguish Python-side bool if seen.
        return {"type": "bool", "value": "true" if value else "false"}
    if type(value) is int:
        return {"type": "integer", "value": str(value)}
    if type(value) is float:
        if math.isnan(value):
            token = "nan"
        elif value == float("inf"):
            token = "+inf"
        elif value == float("-inf"):
            token = "-inf"
        else:
            token = value.hex()
        return {"type": "real", "value": token}
    if isinstance(value, str):
        return {"type": "text", "value": value}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"type": "blob-base64", "value": base64.b64encode(bytes(value)).decode("ascii")}
    raise CheckpointError(f"unsupported SQLite value type: {type(value).__name__}")


@dataclass(frozen=True)
class DatabaseSnapshot:
    schema_sha256: str
    data_sha256: str
    logical_sha256: str
    row_counts: Mapping[str, int]
    verified_table_counts: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_sha256": self.schema_sha256,
            "data_sha256": self.data_sha256,
            "logical_sha256": self.logical_sha256,
            "row_counts": dict(sorted(self.row_counts.items())),
            "verified_table_counts": dict(sorted(self.verified_table_counts.items())),
        }


def capture_database_snapshot(path: str | Path, integrity_key: bytes) -> DatabaseSnapshot:
    """Capture a single SQLite read snapshot and verify the three signed Lycheetah tables.

    The generic fingerprint includes all database tables and schema objects (including
    non-Lycheetah tables), while row-HMAC verification applies to the three v2.8 signed
    tables. The caller must stop writers for checkpoint publication; this function alone
    cannot provide an atomic transaction across the primary DB and an external anchor.
    """
    _key_ok(integrity_key, "integrity_key")
    p = Path(path).resolve()
    if not p.is_file():
        raise CheckpointError("primary database must already exist as a file")
    db = None
    try:
        db = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        _require_schema(db)
        probe, _ = _probes(integrity_key)
        verified_counts: dict[str, int] = {}
        for table in REQUIRED_TABLES:
            rows = [dict(row) for row in db.execute(f"SELECT * FROM {_quote_ident(table)} ORDER BY rowid").fetchall()]
            verified_counts[table] = len(rows)
            for row in rows:
                supplied = row.get("row_hmac_sha256")
                expected = _mac_for(table, row, probe, integrity_key)
                if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
                    raise CheckpointError(f"row-integrity-failed:{table}")

        objects = db.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master "
            "WHERE type IN ('table','index','trigger','view') "
            "ORDER BY type,name"
        ).fetchall()
        schema_objects = []
        table_names = []
        for obj in objects:
            record = {"type": obj["type"], "name": obj["name"], "table": obj["tbl_name"], "sql": obj["sql"]}
            schema_objects.append(record)
            if obj["type"] == "table":
                table_names.append(str(obj["name"]))

        table_shapes: dict[str, Any] = {}
        for table in table_names:
            info = db.execute(f"PRAGMA table_info({_quote_ident(table)})").fetchall()
            table_shapes[table] = [
                {"cid": int(row["cid"]), "name": str(row["name"]), "type": str(row["type"] or ""),
                 "notnull": int(row["notnull"]), "default": row["dflt_value"], "pk": int(row["pk"])}
                for row in info
            ]
        schema_digest = _sha({
            "objects": schema_objects,
            "table_shapes": table_shapes,
            "user_version": int(db.execute("PRAGMA user_version").fetchone()[0]),
            "application_id": int(db.execute("PRAGMA application_id").fetchone()[0]),
            "encoding": str(db.execute("PRAGMA encoding").fetchone()[0]),
        })

        table_data: dict[str, list[Any]] = {}
        row_counts: dict[str, int] = {}
        for table in table_names:
            rows = db.execute(f"SELECT * FROM {_quote_ident(table)}").fetchall()
            typed_rows = [[_typed_sql_value(v) for v in tuple(row)] for row in rows]
            typed_rows.sort(key=_canon)
            table_data[table] = typed_rows
            row_counts[table] = len(rows)
        data_digest = _sha(table_data)
        logical_digest = _sha({
            "schema_sha256": schema_digest,
            "data_sha256": data_digest,
            "row_counts": dict(sorted(row_counts.items())),
            "verified_table_counts": dict(sorted(verified_counts.items())),
        })
        db.rollback()
        return DatabaseSnapshot(schema_digest, data_digest, logical_digest, row_counts, verified_counts)
    except CheckpointError:
        if db is not None and db.in_transaction:
            db.rollback()
        raise
    except (sqlite3.Error, KeyRotationError, TypeError, ValueError) as exc:
        if db is not None and db.in_transaction:
            db.rollback()
        raise CheckpointError(f"database-snapshot-refused:{type(exc).__name__}") from None
    finally:
        if db is not None:
            db.close()


@dataclass(frozen=True)
class StateChangeApproval:
    approval_id: str
    nonce: str
    database_id: str
    previous_checkpoint_sha256: str | None
    proposed_logical_sha256: str
    reason_code: str
    issued_at: str
    expires_at: str
    signature_sha256: str

    def body_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "nonce": self.nonce,
            "database_id": self.database_id,
            "previous_checkpoint_sha256": self.previous_checkpoint_sha256,
            "proposed_logical_sha256": self.proposed_logical_sha256,
            "reason_code": self.reason_code,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.body_dict(), "signature_sha256": self.signature_sha256}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StateChangeApproval":
        expected = {"approval_id", "nonce", "database_id", "previous_checkpoint_sha256",
                    "proposed_logical_sha256", "reason_code", "issued_at", "expires_at", "signature_sha256"}
        if not isinstance(data, Mapping) or set(data) != expected:
            raise CheckpointError("approval-file-fields-invalid")
        for name in ("approval_id", "nonce", "database_id", "proposed_logical_sha256", "reason_code", "issued_at", "expires_at", "signature_sha256"):
            if not isinstance(data[name], str):
                raise CheckpointError("approval-file-field-type-invalid")
        if data["previous_checkpoint_sha256"] is not None and not isinstance(data["previous_checkpoint_sha256"], str):
            raise CheckpointError("approval-file-field-type-invalid")
        if not _valid_sha(data["proposed_logical_sha256"]) or not _valid_sha(data["signature_sha256"]):
            raise CheckpointError("approval-file-digest-invalid")
        if data["previous_checkpoint_sha256"] is not None and not _valid_sha(data["previous_checkpoint_sha256"]):
            raise CheckpointError("approval-file-parent-digest-invalid")
        _parse_time(data["issued_at"])
        _parse_time(data["expires_at"])
        return cls(**{name: data[name] for name in expected})

    @classmethod
    def issue(cls, *, operator_key: bytes, approval_id: str, nonce: str, database_id: str,
              previous_checkpoint_sha256: str | None, proposed_logical_sha256: str,
              reason_code: str, issued_at: str, expires_at: str) -> "StateChangeApproval":
        _key_ok(operator_key, "operator_key")
        if not isinstance(approval_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", approval_id):
            raise CheckpointError("approval_id is invalid")
        if not isinstance(nonce, str) or not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", nonce):
            raise CheckpointError("approval nonce must be 16-128 safe characters")
        if not isinstance(database_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", database_id):
            raise CheckpointError("database_id is invalid")
        if not isinstance(reason_code, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._:-]{2,127}", reason_code):
            raise CheckpointError("reason_code must be a sanitized lowercase code")
        if not (previous_checkpoint_sha256 is None or _valid_sha(previous_checkpoint_sha256)):
            raise CheckpointError("previous checkpoint hash is invalid")
        if not _valid_sha(proposed_logical_sha256):
            raise CheckpointError("proposed logical hash is invalid")
        issued = _parse_time(issued_at)
        expires = _parse_time(expires_at)
        if expires <= issued or (expires - issued).total_seconds() > 3600:
            raise CheckpointError("approval lifetime must be positive and no more than one hour")
        body = {
            "approval_id": approval_id, "nonce": nonce, "database_id": database_id,
            "previous_checkpoint_sha256": previous_checkpoint_sha256,
            "proposed_logical_sha256": proposed_logical_sha256, "reason_code": reason_code,
            "issued_at": issued.isoformat().replace("+00:00", "Z"),
            "expires_at": expires.isoformat().replace("+00:00", "Z"),
        }
        return cls(**body, signature_sha256=_mac(operator_key, body))

    def verify(self, *, operator_key: bytes, database_id: str, previous_checkpoint_sha256: str | None,
               proposed_logical_sha256: str, now: datetime | None = None) -> None:
        _key_ok(operator_key, "operator_key")
        expected_body = self.body_dict()
        expected = _mac(operator_key, expected_body)
        if not isinstance(self.signature_sha256, str) or not hmac.compare_digest(self.signature_sha256, expected):
            raise CheckpointError("state-change-approval-signature-invalid")
        if self.database_id != database_id:
            raise CheckpointError("state-change-approval-database-mismatch")
        if self.previous_checkpoint_sha256 != previous_checkpoint_sha256:
            raise CheckpointError("state-change-approval-stale-parent")
        if self.proposed_logical_sha256 != proposed_logical_sha256:
            raise CheckpointError("state-change-approval-snapshot-mismatch")
        issued, expires = _parse_time(self.issued_at), _parse_time(self.expires_at)
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise CheckpointError("verification time must be timezone-aware")
        current = current.astimezone(timezone.utc)
        if issued > current or expires <= current:
            raise CheckpointError("state-change-approval-expired-or-not-yet-valid")
        if (expires - issued).total_seconds() > 3600:
            raise CheckpointError("state-change-approval-lifetime-too-long")
        if not self.approval_id.strip() or not self.nonce.strip() or not self.reason_code.strip():
            raise CheckpointError("state-change-approval-incomplete")


@dataclass(frozen=True)
class CheckpointRecord:
    sequence: int
    database_id: str
    schema_sha256: str
    data_sha256: str
    logical_sha256: str
    row_counts_json: str
    verified_counts_json: str
    approval_id: str
    approval_nonce: str
    reason_code: str
    created_at: str
    previous_record_sha256: str | None
    anchor_key_id: str
    record_sha256: str
    record_hmac_sha256: str

    def body_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence, "database_id": self.database_id,
            "schema_sha256": self.schema_sha256, "data_sha256": self.data_sha256,
            "logical_sha256": self.logical_sha256, "row_counts": json.loads(self.row_counts_json),
            "verified_counts": json.loads(self.verified_counts_json), "approval_id": self.approval_id,
            "approval_nonce": self.approval_nonce, "reason_code": self.reason_code, "created_at": self.created_at,
            "previous_record_sha256": self.previous_record_sha256,
            "anchor_key_id": self.anchor_key_id,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.body_dict(), "record_sha256": self.record_sha256, "record_hmac_sha256": self.record_hmac_sha256}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _validate_snapshot(snapshot: DatabaseSnapshot) -> None:
    if not isinstance(snapshot, DatabaseSnapshot):
        raise CheckpointError("database-snapshot-type-invalid")
    if not all(_valid_sha(v) for v in (snapshot.schema_sha256, snapshot.data_sha256, snapshot.logical_sha256)):
        raise CheckpointError("database-snapshot-digest-invalid")
    expected = _sha({
        "schema_sha256": snapshot.schema_sha256,
        "data_sha256": snapshot.data_sha256,
        "row_counts": dict(sorted(snapshot.row_counts.items())),
        "verified_table_counts": dict(sorted(snapshot.verified_table_counts.items())),
    })
    if not hmac.compare_digest(snapshot.logical_sha256, expected):
        raise CheckpointError("database-snapshot-digest-components-inconsistent")
    for label, counts in (("row_counts", snapshot.row_counts), ("verified_table_counts", snapshot.verified_table_counts)):
        if not isinstance(counts, Mapping):
            raise CheckpointError(f"database-snapshot-{label}-invalid")
        for table, count in counts.items():
            if not isinstance(table, str) or not table or type(count) is not int or count < 0:
                raise CheckpointError(f"database-snapshot-{label}-invalid")


class MonotonicAnchor(Protocol):
    def history(self) -> list[CheckpointRecord]: ...
    def append_checkpoint(self, *, expected_sequence: int, expected_head_sha256: str | None,
                          database_id: str, snapshot: DatabaseSnapshot, approval: StateChangeApproval,
                          operator_key: bytes, now: datetime | None = None) -> CheckpointRecord: ...


class SQLiteReferenceAnchor:
    """Test/reference anchor in a second SQLite file; not a remote/WORM service."""

    def __init__(self, path: str | Path, *, anchor_key: bytes, anchor_key_id: str = "anchor-v1",
                 operator_key: bytes | None = None, allow_test_clock_override: bool = False):
        _key_ok(anchor_key, "anchor_key")
        if operator_key is not None:
            _key_ok(operator_key, "operator_key")
            if hmac.compare_digest(anchor_key, operator_key):
                raise CheckpointError("anchor and operator keys must be independent")
        if not isinstance(anchor_key_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", anchor_key_id):
            raise CheckpointError("anchor_key_id is invalid")
        if type(allow_test_clock_override) is not bool:
            raise CheckpointError("allow_test_clock_override must be a boolean")
        self.path = Path(path).resolve()
        self.anchor_key = anchor_key
        self.anchor_key_id = anchor_key_id
        self.allow_test_clock_override = allow_test_clock_override
        self._init()
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            raise CheckpointError("anchor-store-permissions-could-not-be-restricted") from None

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._db()) as db:
            db.execute(f"CREATE TABLE IF NOT EXISTS {ANCHOR_TABLE} (sequence INTEGER PRIMARY KEY, database_id TEXT NOT NULL, schema_sha256 TEXT NOT NULL, data_sha256 TEXT NOT NULL, logical_sha256 TEXT NOT NULL, row_counts_json TEXT NOT NULL, verified_counts_json TEXT NOT NULL, approval_id TEXT NOT NULL, approval_nonce TEXT NOT NULL, reason_code TEXT NOT NULL, created_at TEXT NOT NULL, previous_record_sha256 TEXT, record_sha256 TEXT NOT NULL UNIQUE, record_hmac_sha256 TEXT NOT NULL, anchor_key_id TEXT NOT NULL)")
            db.execute(f"CREATE TABLE IF NOT EXISTS {USED_APPROVAL_TABLE} (approval_id TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE, record_sha256 TEXT NOT NULL)")
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {ANCHOR_TABLE}_no_update BEFORE UPDATE ON {ANCHOR_TABLE} BEGIN SELECT RAISE(ABORT,'anchor-records-append-only'); END")
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {ANCHOR_TABLE}_no_delete BEFORE DELETE ON {ANCHOR_TABLE} BEGIN SELECT RAISE(ABORT,'anchor-records-append-only'); END")
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {USED_APPROVAL_TABLE}_no_update BEFORE UPDATE ON {USED_APPROVAL_TABLE} BEGIN SELECT RAISE(ABORT,'approval-use-append-only'); END")
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {USED_APPROVAL_TABLE}_no_delete BEFORE DELETE ON {USED_APPROVAL_TABLE} BEGIN SELECT RAISE(ABORT,'approval-use-append-only'); END")
            anchor_columns = {str(r[1]) for r in db.execute(f"PRAGMA table_info({ANCHOR_TABLE})")}
            approval_columns = {str(r[1]) for r in db.execute(f"PRAGMA table_info({USED_APPROVAL_TABLE})")}
            if not {"approval_nonce", "anchor_key_id", "record_hmac_sha256"}.issubset(anchor_columns):
                raise CheckpointError("anchor-schema-incomplete; do not auto-migrate trust anchor")
            if not {"approval_id", "nonce", "record_sha256"}.issubset(approval_columns):
                raise CheckpointError("approval-use-schema-incomplete; do not auto-migrate trust anchor")

    def history(self) -> list[CheckpointRecord]:
        try:
            with closing(self._db()) as db:
                db.execute("BEGIN")
                rows = db.execute(f"SELECT * FROM {ANCHOR_TABLE} ORDER BY sequence").fetchall()
                used_rows = db.execute(f"SELECT approval_id,nonce,record_sha256 FROM {USED_APPROVAL_TABLE}").fetchall()
                db.rollback()
            records = [self._record_from_row(dict(row)) for row in rows]
        except CheckpointError:
            raise
        except (sqlite3.Error, ValueError, TypeError, json.JSONDecodeError):
            raise CheckpointError("anchor-store-unreadable-or-schema-invalid") from None
        previous = None
        database_id = None
        expected_uses = set()
        for expected_seq, record in enumerate(records, start=1):
            if record.sequence != expected_seq:
                raise CheckpointError("anchor-sequence-gap-or-rollback")
            body = record.body_dict()
            if body["previous_record_sha256"] != previous:
                raise CheckpointError("anchor-chain-link-invalid")
            if database_id is None:
                database_id = record.database_id
            elif record.database_id != database_id:
                raise CheckpointError("anchor-database-id-changed")
            if record.anchor_key_id != self.anchor_key_id:
                raise CheckpointError("anchor-key-id-mismatch")
            if not hmac.compare_digest(record.record_sha256, _sha(body)):
                raise CheckpointError("anchor-record-digest-invalid")
            if not hmac.compare_digest(record.record_hmac_sha256, _mac(self.anchor_key, {**body, "record_sha256": record.record_sha256})):
                raise CheckpointError("anchor-record-authentication-invalid")
            if not _valid_sha(record.logical_sha256) or not _valid_sha(record.schema_sha256) or not _valid_sha(record.data_sha256):
                raise CheckpointError("anchor-digest-shape-invalid")
            expected_uses.add((record.approval_id, record.approval_nonce, record.record_sha256))
            previous = record.record_sha256
        observed_uses = {(str(row[0]), str(row[1]), str(row[2])) for row in used_rows}
        if observed_uses != expected_uses or len(used_rows) != len(observed_uses):
            raise CheckpointError("approval-use-index-inconsistent-with-anchor-chain")
        return records

    @staticmethod
    def _record_from_row(row: Mapping[str, Any]) -> CheckpointRecord:
        return CheckpointRecord(
            sequence=int(row["sequence"]), database_id=str(row["database_id"]),
            schema_sha256=str(row["schema_sha256"]), data_sha256=str(row["data_sha256"]),
            logical_sha256=str(row["logical_sha256"]), row_counts_json=str(row["row_counts_json"]),
            verified_counts_json=str(row["verified_counts_json"]), approval_id=str(row["approval_id"]),
            reason_code=str(row["reason_code"]), created_at=str(row["created_at"]),
            approval_nonce=str(row["approval_nonce"]), previous_record_sha256=row["previous_record_sha256"],
            anchor_key_id=str(row["anchor_key_id"]), record_sha256=str(row["record_sha256"]),
            record_hmac_sha256=str(row["record_hmac_sha256"]),
        )

    def append_checkpoint(self, *, expected_sequence: int, expected_head_sha256: str | None,
                          database_id: str, snapshot: DatabaseSnapshot, approval: StateChangeApproval,
                          operator_key: bytes, now: datetime | None = None) -> CheckpointRecord:
        _validate_snapshot(snapshot)
        if now is not None and not self.allow_test_clock_override:
            raise CheckpointError("caller-supplied clock override disabled")
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise CheckpointError("clock must be timezone-aware")
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                rows = db.execute(f"SELECT * FROM {ANCHOR_TABLE} ORDER BY sequence").fetchall()
                records = [self._record_from_row(dict(row)) for row in rows]
                # Validate chain with this locked view, not a stale caller snapshot.
                previous = None
                for i, rec in enumerate(records, start=1):
                    if rec.sequence != i or rec.previous_record_sha256 != previous:
                        raise CheckpointError("anchor-chain-invalid-before-append")
                    body = rec.body_dict()
                    if rec.anchor_key_id != self.anchor_key_id:
                        raise CheckpointError("anchor-key-id-mismatch")
                    if not hmac.compare_digest(rec.record_sha256, _sha(body)) or not hmac.compare_digest(
                        rec.record_hmac_sha256, _mac(self.anchor_key, {**body, "record_sha256": rec.record_sha256})
                    ):
                        raise CheckpointError("anchor-record-authentication-invalid")
                    previous = rec.record_sha256
                expected_uses = {(r.approval_id, r.approval_nonce, r.record_sha256) for r in records}
                used_rows = db.execute(f"SELECT approval_id,nonce,record_sha256 FROM {USED_APPROVAL_TABLE}").fetchall()
                observed_uses = {(str(row[0]), str(row[1]), str(row[2])) for row in used_rows}
                if observed_uses != expected_uses or len(used_rows) != len(observed_uses):
                    raise CheckpointError("approval-use-index-inconsistent-with-anchor-chain")
                latest_seq = records[-1].sequence if records else 0
                latest_hash = records[-1].record_sha256 if records else None
                if latest_seq != expected_sequence or latest_hash != expected_head_sha256:
                    raise CheckpointError("anchor-head-changed-retry-preflight")
                if any(rec.database_id != database_id for rec in records):
                    raise CheckpointError("anchor-database-id-mismatch")
                approval.verify(
                    operator_key=operator_key, database_id=database_id,
                    previous_checkpoint_sha256=latest_hash,
                    proposed_logical_sha256=snapshot.logical_sha256, now=current,
                )
                used = db.execute(f"SELECT 1 FROM {USED_APPROVAL_TABLE} WHERE approval_id=? OR nonce=?",
                                  (approval.approval_id, approval.nonce)).fetchone()
                if used is not None:
                    raise CheckpointError("state-change-approval-already-used")
                body = {
                    "sequence": latest_seq + 1, "database_id": database_id,
                    "schema_sha256": snapshot.schema_sha256, "data_sha256": snapshot.data_sha256,
                    "logical_sha256": snapshot.logical_sha256,
                    "row_counts": dict(sorted(snapshot.row_counts.items())),
                    "verified_counts": dict(sorted(snapshot.verified_table_counts.items())),
                    "approval_id": approval.approval_id, "approval_nonce": approval.nonce,
                    "reason_code": approval.reason_code,
                    "created_at": current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "previous_record_sha256": latest_hash,
                    "anchor_key_id": self.anchor_key_id,
                }
                record_hash = _sha(body)
                row = CheckpointRecord(
                    sequence=body["sequence"], database_id=database_id,
                    schema_sha256=snapshot.schema_sha256, data_sha256=snapshot.data_sha256,
                    logical_sha256=snapshot.logical_sha256,
                    row_counts_json=json.dumps(body["row_counts"], sort_keys=True, separators=(",", ":")),
                    verified_counts_json=json.dumps(body["verified_counts"], sort_keys=True, separators=(",", ":")),
                    approval_id=approval.approval_id, approval_nonce=approval.nonce,
                    reason_code=approval.reason_code, created_at=body["created_at"],
                    previous_record_sha256=latest_hash, anchor_key_id=self.anchor_key_id, record_sha256=record_hash,
                    record_hmac_sha256=_mac(self.anchor_key, {**body, "record_sha256": record_hash}),
                )
                db.execute(
                    f"INSERT INTO {ANCHOR_TABLE}(sequence,database_id,schema_sha256,data_sha256,logical_sha256,row_counts_json,verified_counts_json,approval_id,approval_nonce,reason_code,created_at,previous_record_sha256,record_sha256,record_hmac_sha256,anchor_key_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (row.sequence,row.database_id,row.schema_sha256,row.data_sha256,row.logical_sha256,row.row_counts_json,row.verified_counts_json,row.approval_id,row.approval_nonce,row.reason_code,row.created_at,row.previous_record_sha256,row.record_sha256,row.record_hmac_sha256,self.anchor_key_id),
                )
                db.execute(f"INSERT INTO {USED_APPROVAL_TABLE}(approval_id,nonce,record_sha256) VALUES(?,?,?)",
                           (approval.approval_id, approval.nonce, record_hash))
                db.commit()
                return row
            except Exception:
                db.rollback()
                raise


def publish_checkpoint(primary_path: str | Path, *, database_id: str, integrity_key: bytes,
                       anchor: MonotonicAnchor, approval: StateChangeApproval,
                       operator_key: bytes, now: datetime | None = None) -> CheckpointRecord:
    """Publish a state-bound checkpoint while holding the primary SQLite write lock.

    This is an offline/single-writer procedure. The transaction reserves the primary DB
    against concurrent SQLite writers while the snapshot is fingerprinted and the anchor
    appends using compare-and-swap. The anchor adapter is expected to provide durable CAS.
    If the anchor is unavailable, publication is refused and the database lock is released.
    """
    if not isinstance(database_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", database_id):
        raise CheckpointError("database_id is invalid")
    if not isinstance(operator_key, bytes) or len(operator_key) < MIN_KEY_BYTES:
        raise CheckpointError("operator_key must be at least 32 bytes")
    if hmac.compare_digest(operator_key, integrity_key):
        raise CheckpointError("primary-integrity-and-operator-keys-must-be-independent")
    anchor_key = getattr(anchor, "anchor_key", None)
    if isinstance(anchor_key, bytes) and hmac.compare_digest(anchor_key, integrity_key):
        raise CheckpointError("primary-integrity-and-anchor-keys-must-be-independent")
    if now is not None and not getattr(anchor, "allow_test_clock_override", False):
        raise CheckpointError("caller-supplied clock override disabled")
    path = Path(primary_path).resolve()
    if not path.is_file():
        raise CheckpointError("primary database must already exist as a file")
    lock_db = None
    try:
        lock_db = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        lock_db.execute("PRAGMA busy_timeout=10000")
        lock_db.execute("BEGIN IMMEDIATE")
        # Snapshot read is performed under the writer reservation above; normal SQLite
        # writers cannot slip between fingerprinting and external CAS append.
        snapshot = capture_database_snapshot(path, integrity_key)
        _validate_snapshot(snapshot)
        records = anchor.history()
        latest = records[-1] if records else None
        seq = latest.sequence if latest else 0
        head = latest.record_sha256 if latest else None
        if approval.database_id != database_id:
            raise CheckpointError("state-change-approval-database-mismatch")
        approval.verify(operator_key=operator_key, database_id=database_id,
                        previous_checkpoint_sha256=head, proposed_logical_sha256=snapshot.logical_sha256,
                        now=now)
        record = anchor.append_checkpoint(expected_sequence=seq, expected_head_sha256=head,
                                         database_id=database_id, snapshot=snapshot,
                                         approval=approval, operator_key=operator_key, now=now)
        lock_db.commit()
        # Post-publication verification is a second snapshot. If an out-of-band file
        # replacement or non-SQLite writer changed state, callers receive an error and
        # startup verification will fail closed instead of trusting the publication.
        after = capture_database_snapshot(path, integrity_key)
        if after.logical_sha256 != record.logical_sha256:
            raise CheckpointError("primary-database-changed-during-anchor-publication")
        return record
    except CheckpointError:
        if lock_db is not None and lock_db.in_transaction:
            lock_db.rollback()
        raise
    except sqlite3.Error:
        if lock_db is not None and lock_db.in_transaction:
            lock_db.rollback()
        raise CheckpointError("checkpoint-publication-failed-closed") from None
    finally:
        if lock_db is not None:
            lock_db.close()


def verify_database_against_anchor(primary_path: str | Path, *, database_id: str,
                                   integrity_key: bytes, anchor: MonotonicAnchor) -> dict[str, Any]:
    """Read-only startup gate. Anything but exact latest match requires quarantine/reconcile."""
    try:
        records = anchor.history()
    except CheckpointError:
        return {"status": "ANCHOR_UNVERIFIED", "safe_to_continue": False, "reason": "external-anchor-chain-or-authentication-invalid"}
    if not records:
        return {"status": "NO_ANCHOR", "safe_to_continue": False, "reason": "initial-checkpoint-required"}
    latest = records[-1]
    if latest.database_id != database_id:
        return {"status": "DATABASE_ID_MISMATCH", "safe_to_continue": False, "anchor_sequence": latest.sequence}
    try:
        snapshot = capture_database_snapshot(primary_path, integrity_key)
    except CheckpointError as exc:
        return {"status": "PRIMARY_DATABASE_UNVERIFIED", "safe_to_continue": False, "anchor_sequence": latest.sequence, "reason": str(exc)}
    if snapshot.schema_sha256 != latest.schema_sha256:
        return {"status": "SCHEMA_CHANGED", "safe_to_continue": False, "anchor_sequence": latest.sequence}
    if snapshot.logical_sha256 != latest.logical_sha256:
        previous_match = any(r.logical_sha256 == snapshot.logical_sha256 for r in records[:-1])
        return {"status": "STALE_SNAPSHOT" if previous_match else "CHECKPOINT_MISMATCH",
                "safe_to_continue": False, "anchor_sequence": latest.sequence,
                "matches_older_checkpoint": previous_match,
                "reason": "primary database differs from latest monotonic anchor; quarantine and reconcile"}
    return {"status": "MATCH", "safe_to_continue": True, "anchor_sequence": latest.sequence,
            "logical_sha256": snapshot.logical_sha256, "row_counts": dict(snapshot.row_counts)}
