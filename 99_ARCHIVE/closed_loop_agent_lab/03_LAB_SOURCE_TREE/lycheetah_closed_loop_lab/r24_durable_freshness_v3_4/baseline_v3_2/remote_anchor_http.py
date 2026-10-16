"""v3.1 reference protocol for an authenticated remote monotonic checkpoint anchor.

This module is a local protocol simulator/client, not a production remote service.
It demonstrates signed operator approvals, client-authenticated requests, signed
service responses, CAS appends, request idempotency, and recovery from lost replies.
Requires `cryptography` for Ed25519 signatures.
"""
from __future__ import annotations

import base64
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

MIN_KEY_BYTES = 32
DOMAIN_APPROVAL = b"lycheetah-remote-anchor-operator-approval-v3.1\n"
DOMAIN_RECORD = b"lycheetah-remote-anchor-record-v3.1\n"
DOMAIN_RESPONSE = b"lycheetah-remote-anchor-response-v3.1\n"
VALID_REASON = re.compile(r"^[a-z0-9][a-z0-9._:-]{2,127}$")
VALID_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
VALID_REQ = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


class AnchorProtocolError(ValueError):
    pass


class AnchorTransportError(AnchorProtocolError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_json(value: Any) -> str:
    return sha256(canonical(value))


def b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def unb64(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, TypeError):
        raise AnchorProtocolError("invalid-base64") from None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise AnchorProtocolError("timestamp-must-be-timezone-aware")
    return dt.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise AnchorProtocolError("timestamp-invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AnchorProtocolError("timestamp-invalid") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AnchorProtocolError("timestamp-must-include-timezone")
    return parsed.astimezone(timezone.utc)


def public_bytes(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def private_bytes(key: Ed25519PrivateKey) -> bytes:
    return key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())


def validate_snapshot(s: Mapping[str, Any]) -> dict[str, Any]:
    required = {"schema_sha256", "data_sha256", "logical_sha256", "row_counts", "verified_table_counts"}
    if not isinstance(s, Mapping) or set(s) != required:
        raise AnchorProtocolError("snapshot-fields-invalid")
    for field in ("schema_sha256", "data_sha256", "logical_sha256"):
        if not isinstance(s[field], str) or not HEX64.fullmatch(s[field]):
            raise AnchorProtocolError("snapshot-digest-invalid")
    counts: dict[str, dict[str, int]] = {}
    for name in ("row_counts", "verified_table_counts"):
        value = s[name]
        if not isinstance(value, Mapping):
            raise AnchorProtocolError("snapshot-counts-invalid")
        normalized: dict[str, int] = {}
        for table, count in value.items():
            if not isinstance(table, str) or not table or type(count) is not int or count < 0:
                raise AnchorProtocolError("snapshot-counts-invalid")
            normalized[table] = count
        counts[name] = dict(sorted(normalized.items()))
    body = {"schema_sha256": s["schema_sha256"], "data_sha256": s["data_sha256"],
            "row_counts": counts["row_counts"], "verified_table_counts": counts["verified_table_counts"]}
    if not hmac.compare_digest(s["logical_sha256"], sha_json(body)):
        raise AnchorProtocolError("snapshot-logical-digest-inconsistent")
    return {"schema_sha256": s["schema_sha256"], "data_sha256": s["data_sha256"],
            "logical_sha256": s["logical_sha256"], "row_counts": counts["row_counts"],
            "verified_table_counts": counts["verified_table_counts"]}


def make_snapshot(schema_sha: str, data_sha: str, row_counts: Mapping[str, int], verified_counts: Mapping[str, int]) -> dict[str, Any]:
    body = {"schema_sha256": schema_sha, "data_sha256": data_sha,
            "row_counts": dict(sorted(row_counts.items())),
            "verified_table_counts": dict(sorted(verified_counts.items()))}
    return {**body, "logical_sha256": sha_json(body)}


@dataclass(frozen=True)
class OperatorApproval:
    approval_id: str
    nonce: str
    signer_key_id: str
    request_id: str
    database_id: str
    expected_sequence: int
    expected_head_sha256: str | None
    snapshot: Mapping[str, Any]
    reason_code: str
    issued_at: str
    expires_at: str
    signature_b64: str

    def body_dict(self) -> dict[str, Any]:
        return {"approval_id": self.approval_id, "nonce": self.nonce, "signer_key_id": self.signer_key_id,
                "request_id": self.request_id, "database_id": self.database_id,
                "expected_sequence": self.expected_sequence, "expected_head_sha256": self.expected_head_sha256,
                "snapshot": dict(self.snapshot), "reason_code": self.reason_code,
                "issued_at": self.issued_at, "expires_at": self.expires_at}

    def to_dict(self) -> dict[str, Any]:
        return {**self.body_dict(), "signature_b64": self.signature_b64}

    @classmethod
    def issue(cls, *, private_key: Ed25519PrivateKey, signer_key_id: str, approval_id: str,
              nonce: str, request_id: str, database_id: str, expected_sequence: int,
              expected_head_sha256: str | None, snapshot: Mapping[str, Any], reason_code: str,
              issued_at: datetime | None = None, expires_at: datetime | None = None) -> "OperatorApproval":
        snap = validate_snapshot(snapshot)
        now = issued_at or utc_now()
        exp = expires_at or (now + timedelta(minutes=10))
        if not VALID_ID.fullmatch(approval_id) or not VALID_ID.fullmatch(database_id) or not VALID_ID.fullmatch(signer_key_id):
            raise AnchorProtocolError("approval-identifier-invalid")
        if not VALID_REQ.fullmatch(nonce) or not VALID_REQ.fullmatch(request_id):
            raise AnchorProtocolError("approval-nonce-or-request-id-invalid")
        if type(expected_sequence) is not int or expected_sequence < 0:
            raise AnchorProtocolError("approval-parent-sequence-invalid")
        if expected_head_sha256 is not None and not HEX64.fullmatch(expected_head_sha256):
            raise AnchorProtocolError("approval-parent-hash-invalid")
        if (expected_sequence == 0) != (expected_head_sha256 is None):
            raise AnchorProtocolError("approval-parent-state-inconsistent")
        if not VALID_REASON.fullmatch(reason_code):
            raise AnchorProtocolError("approval-reason-invalid")
        if exp <= now or exp - now > timedelta(minutes=15):
            raise AnchorProtocolError("approval-lifetime-invalid")
        body = {"approval_id": approval_id, "nonce": nonce, "signer_key_id": signer_key_id,
                "request_id": request_id, "database_id": database_id,
                "expected_sequence": expected_sequence, "expected_head_sha256": expected_head_sha256,
                "snapshot": snap, "reason_code": reason_code, "issued_at": iso(now), "expires_at": iso(exp)}
        if not isinstance(private_key, Ed25519PrivateKey):
            raise AnchorProtocolError("operator-private-key-invalid")
        sig = private_key.sign(DOMAIN_APPROVAL + canonical(body))
        return cls(**body, signature_b64=b64(sig))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OperatorApproval":
        fields = {"approval_id", "nonce", "signer_key_id", "request_id", "database_id", "expected_sequence",
                  "expected_head_sha256", "snapshot", "reason_code", "issued_at", "expires_at", "signature_b64"}
        if not isinstance(data, Mapping) or set(data) != fields:
            raise AnchorProtocolError("approval-fields-invalid")
        if not all(isinstance(data[k], str) for k in fields - {"expected_sequence", "expected_head_sha256", "snapshot"}):
            raise AnchorProtocolError("approval-field-type-invalid")
        if type(data["expected_sequence"]) is not int or (data["expected_head_sha256"] is not None and not isinstance(data["expected_head_sha256"], str)):
            raise AnchorProtocolError("approval-field-type-invalid")
        return cls(**{k: (validate_snapshot(data[k]) if k == "snapshot" else data[k]) for k in fields})



@dataclass(frozen=True)
class AnchorRecord:
    body: Mapping[str, Any]
    record_sha256: str
    server_key_id: str
    signature_b64: str

    def to_dict(self) -> dict[str, Any]:
        return {"body": dict(self.body), "record_sha256": self.record_sha256,
                "server_key_id": self.server_key_id, "signature_b64": self.signature_b64}


def verify_record(record: Mapping[str, Any], server_keys: Mapping[str, Ed25519PublicKey], *, expected_previous: str | None = None,
                  expected_sequence: int | None = None, expected_database_id: str | None = None) -> AnchorRecord:
    if not isinstance(record, Mapping) or set(record) != {"body", "record_sha256", "server_key_id", "signature_b64"}:
        raise AnchorProtocolError("anchor-record-envelope-invalid")
    body = record["body"]
    if not isinstance(body, Mapping):
        raise AnchorProtocolError("anchor-record-body-invalid")
    rec_hash = record["record_sha256"]
    key_id = record["server_key_id"]
    signature = record["signature_b64"]
    if not isinstance(rec_hash, str) or not HEX64.fullmatch(rec_hash) or not isinstance(key_id, str) or not isinstance(signature, str):
        raise AnchorProtocolError("anchor-record-envelope-invalid")
    required_body = {"sequence", "database_id", "schema_sha256", "data_sha256", "logical_sha256",
                     "row_counts", "verified_table_counts", "approval_id", "approval_nonce",
                     "reason_code", "created_at", "previous_record_sha256", "request_id",
                     "request_sha256", "server_key_id"}
    if set(body) != required_body:
        raise AnchorProtocolError("anchor-record-body-fields-invalid")
    if type(body["sequence"]) is not int or body["sequence"] < 1:
        raise AnchorProtocolError("anchor-record-sequence-invalid")
    if not all(isinstance(body[k], str) and VALID_ID.fullmatch(body[k]) for k in
               ("database_id", "approval_id", "server_key_id")):
        raise AnchorProtocolError("anchor-record-identifier-invalid")
    if not isinstance(body["reason_code"], str) or not VALID_REASON.fullmatch(body["reason_code"]):
        raise AnchorProtocolError("anchor-record-reason-invalid")
    if body["server_key_id"] != key_id:
        raise AnchorProtocolError("anchor-record-key-id-mismatch")
    if not isinstance(body["approval_nonce"], str) or not VALID_REQ.fullmatch(body["approval_nonce"]):
        raise AnchorProtocolError("anchor-record-approval-nonce-invalid")
    if not isinstance(body["request_id"], str) or not VALID_REQ.fullmatch(body["request_id"]):
        raise AnchorProtocolError("anchor-record-request-id-invalid")
    if not isinstance(body["request_sha256"], str) or not HEX64.fullmatch(body["request_sha256"]):
        raise AnchorProtocolError("anchor-record-request-digest-invalid")
    validate_snapshot({k: body[k] for k in ("schema_sha256", "data_sha256", "logical_sha256", "row_counts", "verified_table_counts")})
    parse_time(body["created_at"])
    previous = body["previous_record_sha256"]
    if previous is not None and (not isinstance(previous, str) or not HEX64.fullmatch(previous)):
        raise AnchorProtocolError("anchor-record-parent-hash-invalid")
    if (body["sequence"] == 1) != (previous is None):
        raise AnchorProtocolError("anchor-record-sequence-parent-inconsistent")
    if not hmac.compare_digest(rec_hash, sha_json(body)):
        raise AnchorProtocolError("anchor-record-digest-invalid")
    key = server_keys.get(key_id)
    if key is None:
        raise AnchorProtocolError("anchor-server-key-untrusted")
    try:
        key.verify(unb64(signature), DOMAIN_RECORD + canonical({"body": dict(body), "record_sha256": rec_hash, "server_key_id": key_id}))
    except InvalidSignature:
        raise AnchorProtocolError("anchor-record-signature-invalid") from None
    if expected_previous is not None or expected_sequence is not None:
        if body.get("previous_record_sha256") != expected_previous:
            raise AnchorProtocolError("anchor-record-parent-mismatch")
        if body.get("sequence") != expected_sequence:
            raise AnchorProtocolError("anchor-record-sequence-mismatch")
    if expected_database_id is not None and body.get("database_id") != expected_database_id:
        raise AnchorProtocolError("anchor-record-database-mismatch")
    return AnchorRecord(dict(body), rec_hash, key_id, signature)


@dataclass(frozen=True)
class ServiceResponse:
    http_status: int
    body: Mapping[str, Any]
    server_key_id: str
    signature_b64: str

    def unsigned(self) -> dict[str, Any]:
        return {"http_status": self.http_status, "body": dict(self.body), "server_key_id": self.server_key_id}

    def to_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "signature_b64": self.signature_b64}


class RemoteAnchorService:
    """SQLite-backed local simulation of a remote CAS anchor API."""
    def __init__(self, path: str | Path, *, api_keys: Mapping[str, bytes], operator_keys: Mapping[str, Ed25519PublicKey],
                 server_key_id: str, server_private_key: Ed25519PrivateKey, max_clock_skew_seconds: int = 90):
        self.path = Path(path).resolve()
        self.api_keys = dict(api_keys)
        self.operator_keys = dict(operator_keys)
        if not isinstance(server_private_key, Ed25519PrivateKey):
            raise AnchorProtocolError("anchor-server-private-key-invalid")
        if any(not isinstance(k, str) or not VALID_ID.fullmatch(k) or not isinstance(v, Ed25519PublicKey)
               for k, v in self.operator_keys.items()):
            raise AnchorProtocolError("operator-public-key-registry-invalid")
        self.server_key_id = server_key_id
        self.server_private_key = server_private_key
        self.server_keys = {server_key_id: server_private_key.public_key()}
        self.max_clock_skew_seconds = max_clock_skew_seconds
        if not VALID_ID.fullmatch(server_key_id):
            raise AnchorProtocolError("server-key-id-invalid")
        for key_id, key in self.api_keys.items():
            if not VALID_ID.fullmatch(key_id) or not isinstance(key, bytes) or len(key) < MIN_KEY_BYTES:
                raise AnchorProtocolError("client-api-key-invalid")
        self.drop_before_count = 0
        self.drop_after_commit_count = 0
        self.fail_lookup_count = 0
        self.mutate_response_count = 0
        self._init_db()

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _init_db(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._db()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS auth_nonces (key_id TEXT NOT NULL, nonce TEXT NOT NULL, created_at INTEGER NOT NULL, PRIMARY KEY(key_id,nonce))")
            db.execute("CREATE TABLE IF NOT EXISTS approvals_used (database_id TEXT NOT NULL, approval_id TEXT NOT NULL, nonce TEXT NOT NULL, request_id TEXT NOT NULL, PRIMARY KEY(database_id,approval_id), UNIQUE(database_id,nonce))")
            db.execute("CREATE TABLE IF NOT EXISTS checkpoints (database_id TEXT NOT NULL, sequence INTEGER NOT NULL, record_json TEXT NOT NULL, record_sha256 TEXT NOT NULL, request_id TEXT NOT NULL, request_sha256 TEXT NOT NULL, PRIMARY KEY(database_id,sequence), UNIQUE(database_id,record_sha256), UNIQUE(database_id,request_id))")
            db.execute("CREATE TABLE IF NOT EXISTS requests (database_id TEXT NOT NULL, request_id TEXT NOT NULL, request_sha256 TEXT NOT NULL, record_json TEXT NOT NULL, created_at INTEGER NOT NULL, PRIMARY KEY(database_id,request_id))")
            db.execute("CREATE TRIGGER IF NOT EXISTS checkpoints_no_update BEFORE UPDATE ON checkpoints BEGIN SELECT RAISE(ABORT,'checkpoint-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS checkpoints_no_delete BEFORE DELETE ON checkpoints BEGIN SELECT RAISE(ABORT,'checkpoint-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS approvals_no_update BEFORE UPDATE ON approvals_used BEGIN SELECT RAISE(ABORT,'approval-use-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS approvals_no_delete BEFORE DELETE ON approvals_used BEGIN SELECT RAISE(ABORT,'approval-use-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS checkpoints_no_update BEFORE UPDATE ON checkpoints BEGIN SELECT RAISE(ABORT,'checkpoint-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS checkpoints_no_delete BEFORE DELETE ON checkpoints BEGIN SELECT RAISE(ABORT,'checkpoint-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS requests_no_update BEFORE UPDATE ON requests BEGIN SELECT RAISE(ABORT,'request-record-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS requests_no_delete BEFORE DELETE ON requests BEGIN SELECT RAISE(ABORT,'request-record-append-only'); END")

    def _read_verified_history(self, db: sqlite3.Connection, database_id: str) -> list[dict[str, Any]]:
        rows = db.execute("SELECT sequence,record_json,record_sha256,request_id,request_sha256 FROM checkpoints WHERE database_id=? ORDER BY sequence", (database_id,)).fetchall()
        records: list[dict[str, Any]] = []
        previous = None
        for expected_seq, row in enumerate(rows, start=1):
            try:
                record = json.loads(row["record_json"])
            except (TypeError, json.JSONDecodeError):
                raise ApiError(503, "anchor-record-storage-invalid") from None
            try:
                verified = verify_record(record, self.server_keys, expected_previous=previous,
                                         expected_sequence=expected_seq, expected_database_id=database_id)
            except AnchorProtocolError as exc:
                raise ApiError(503, "anchor-chain-unverified:" + str(exc)) from None
            if (int(row["sequence"]) != expected_seq or row["record_sha256"] != verified.record_sha256
                or row["request_id"] != verified.body["request_id"]
                or row["request_sha256"] != verified.body["request_sha256"]):
                raise ApiError(503, "anchor-record-index-mismatch")
            request = db.execute("SELECT request_sha256,record_json FROM requests WHERE database_id=? AND request_id=?",
                                 (database_id, verified.body["request_id"])).fetchone()
            if request is None or request["request_sha256"] != verified.body["request_sha256"] or request["record_json"] != canonical(record).decode("utf-8"):
                raise ApiError(503, "anchor-request-index-mismatch")
            previous = verified.record_sha256
            records.append(verified.to_dict())
        used_rows = db.execute("SELECT approval_id,nonce,request_id FROM approvals_used WHERE database_id=?", (database_id,)).fetchall()
        expected_uses = {(r["body"]["approval_id"], r["body"]["approval_nonce"], r["body"]["request_id"]) for r in records}
        observed_uses = {(str(r["approval_id"]), str(r["nonce"]), str(r["request_id"])) for r in used_rows}
        if observed_uses != expected_uses or len(used_rows) != len(observed_uses):
            raise ApiError(503, "anchor-approval-index-mismatch")
        all_requests = db.execute("SELECT request_id,request_sha256,record_json FROM requests WHERE database_id=?", (database_id,)).fetchall()
        expected_requests = {(r["body"]["request_id"], r["body"]["request_sha256"], canonical(r).decode("utf-8")) for r in records}
        observed_requests = {(str(r["request_id"]), str(r["request_sha256"]), str(r["record_json"])) for r in all_requests}
        if observed_requests != expected_requests or len(all_requests) != len(observed_requests):
            raise ApiError(503, "anchor-request-index-has-orphan-or-missing-record")
        return records

    def _sign_response(self, status: int, body: Mapping[str, Any]) -> dict[str, Any]:
        unsigned = {"http_status": status, "body": dict(body), "server_key_id": self.server_key_id}
        sig = self.server_private_key.sign(DOMAIN_RESPONSE + canonical(unsigned))
        response = {**unsigned, "signature_b64": b64(sig)}
        if self.mutate_response_count:
            self.mutate_response_count -= 1
            response["body"] = {**response["body"], "tampered_by_fault_injector": True}
        return response

    def _authenticate(self, db: sqlite3.Connection, method: str, path: str, body: bytes, headers: Mapping[str, str]) -> None:
        normalized_headers = {str(k).lower(): v for k, v in headers.items()}
        key_id = normalized_headers.get("x-anchor-key-id", "")
        timestamp = normalized_headers.get("x-anchor-timestamp", "")
        nonce = normalized_headers.get("x-anchor-nonce", "")
        supplied = normalized_headers.get("x-anchor-signature", "")
        key = self.api_keys.get(key_id)
        if key is None or not re.fullmatch(r"[0-9]{10,13}", timestamp) or not VALID_REQ.fullmatch(nonce):
            raise ApiError(401, "client-authentication-invalid")
        try:
            stamp = int(timestamp)
            if len(timestamp) == 13:
                stamp //= 1000
        except ValueError:
            raise ApiError(401, "client-authentication-invalid") from None
        if abs(int(time.time()) - stamp) > self.max_clock_skew_seconds:
            raise ApiError(401, "client-authentication-expired")
        canonical_request = {"method": method, "path": path, "timestamp": timestamp,
                             "nonce": nonce, "body_sha256": sha256(body)}
        expected = hmac.new(key, canonical(canonical_request), hashlib.sha256).hexdigest()
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, expected):
            raise ApiError(401, "client-authentication-invalid")
        now_seconds = int(time.time())
        exists = db.execute("SELECT 1 FROM auth_nonces WHERE key_id=? AND nonce=?", (key_id, nonce)).fetchone()
        if exists:
            raise ApiError(401, "client-request-replay")
        db.execute("INSERT INTO auth_nonces(key_id,nonce,created_at) VALUES(?,?,?)", (key_id, nonce, now_seconds))
        # Requests older than the accepted timestamp window cannot be replayed; keep a
        # small additional margin for clock skew and concurrent request handling.
        db.execute("DELETE FROM auth_nonces WHERE created_at < ?", (now_seconds - (2 * self.max_clock_skew_seconds + 60),))

    def handle(self, method: str, path: str, body_bytes: bytes, headers: Mapping[str, str]) -> tuple[int, dict[str, Any] | None, bool]:
        """Return (HTTP status, signed response, drop_connection)."""
        if self.drop_before_count and method == "POST" and path.startswith("/v1/databases/"):
            self.drop_before_count -= 1
            return 0, None, True
        if self.fail_lookup_count and method == "GET" and "/requests/" in path:
            self.fail_lookup_count -= 1
            return 503, self._sign_response(503, {"error": "fault-injected-status-unavailable"}), False
        db = None
        drop_after = False
        response_body: dict[str, Any]
        status = 200
        try:
            db = self._db()
            db.execute("BEGIN IMMEDIATE")
            self._authenticate(db, method, path, body_bytes, headers)
            parts = [unquote(p) for p in urlparse(path).path.split("/") if p]
            if len(parts) < 3 or parts[0:2] != ["v1", "databases"]:
                raise ApiError(404, "route-not-found")
            database_id = parts[2]
            if not VALID_ID.fullmatch(database_id):
                raise ApiError(400, "database-id-invalid")
            if method == "POST" and parts[3:] == ["checkpoints"]:
                req = json.loads(body_bytes.decode("utf-8"))
                response_body, status = self._append(db, database_id, req)
                if status == 200 and self.drop_after_commit_count:
                    self.drop_after_commit_count -= 1
                    drop_after = True
            elif method == "GET" and len(parts) == 5 and parts[3] == "requests":
                if len(parts[4]) > 128 or not VALID_REQ.fullmatch(parts[4]):
                    raise ApiError(400, "request-id-invalid")
                records = self._read_verified_history(db, database_id)
                row = db.execute("SELECT request_sha256,record_json FROM requests WHERE database_id=? AND request_id=?",
                                 (database_id, parts[4])).fetchone()
                if row is None:
                    response_body, status = {"status": "NOT_FOUND", "database_id": database_id, "request_id": parts[4]}, 200
                else:
                    rec = json.loads(row["record_json"])
                    if not any(r["record_sha256"] == rec.get("record_sha256") for r in records):
                        raise ApiError(503, "anchor-request-not-in-verified-history")
                    response_body, status = {"status": "FOUND", "database_id": database_id, "request_id": parts[4],
                                             "request_sha256": row["request_sha256"], "record": rec}, 200
            elif method == "GET" and parts[3:] == ["history"]:
                records = self._read_verified_history(db, database_id)
                response_body, status = {"database_id": database_id, "records": records}, 200
            elif method == "GET" and parts[3:] == ["head"]:
                records = self._read_verified_history(db, database_id)
                response_body, status = {"database_id": database_id, "record": records[-1] if records else None}, 200
            else:
                raise ApiError(404, "route-not-found")
            db.commit()
        except ApiError as exc:
            if db is not None and db.in_transaction:
                # Commit an authenticated nonce even for authenticated route conflicts.
                if exc.status in (400, 404, 409, 422):
                    db.commit()
                else:
                    db.rollback()
            response_body, status = {"error": exc.code}, exc.status
        except (sqlite3.Error, ValueError, UnicodeError, json.JSONDecodeError):
            if db is not None and db.in_transaction:
                db.rollback()
            response_body, status = {"error": "anchor-internal-error"}, 500
        finally:
            if db is not None:
                db.close()
        response = self._sign_response(status, response_body)
        return status, response, drop_after

    def _append(self, db: sqlite3.Connection, database_id: str, req: Any) -> tuple[dict[str, Any], int]:
        fields = {"request_id", "snapshot", "approval"}
        if not isinstance(req, Mapping) or set(req) != fields:
            raise ApiError(400, "append-request-fields-invalid")
        request_id = req["request_id"]
        if not isinstance(request_id, str) or not VALID_REQ.fullmatch(request_id):
            raise ApiError(400, "request-id-invalid")
        try:
            snap = validate_snapshot(req["snapshot"])
            approval = OperatorApproval.from_dict(req["approval"])
        except AnchorProtocolError as exc:
            raise ApiError(422, str(exc)) from None
        request_sha = sha_json({"request_id": request_id, "snapshot": snap, "approval": approval.to_dict()})
        # Never return an idempotent replay from the request index until the full
        # append-only chain and all cross-index relationships have verified.
        records = self._read_verified_history(db, database_id)
        prior = db.execute("SELECT request_sha256,record_json FROM requests WHERE database_id=? AND request_id=?",
                           (database_id, request_id)).fetchone()
        if prior is not None:
            if not hmac.compare_digest(prior["request_sha256"], request_sha):
                return {"error": "request-id-reused-with-different-content", "status": "CONFLICT"}, 409
            rec = json.loads(prior["record_json"])
            if not any(r["record_sha256"] == rec.get("record_sha256") for r in records):
                raise ApiError(503, "anchor-request-not-in-verified-history")
            return {"status": "COMMITTED", "request_id": request_id, "request_sha256": request_sha,
                    "record": rec, "idempotent_replay": True}, 200
        if approval.request_id != request_id or approval.database_id != database_id or dict(approval.snapshot) != snap:
            raise ApiError(422, "approval-does-not-bind-request")
        if not VALID_ID.fullmatch(database_id):
            raise ApiError(400, "database-id-invalid")
        public_key = self.operator_keys.get(approval.signer_key_id)
        if public_key is None:
            raise ApiError(422, "operator-signer-untrusted")
        try:
            public_key.verify(unb64(approval.signature_b64), DOMAIN_APPROVAL + canonical(approval.body_dict()))
        except (InvalidSignature, AnchorProtocolError):
            raise ApiError(422, "operator-approval-signature-invalid") from None
        now = utc_now()
        try:
            issued, expires = parse_time(approval.issued_at), parse_time(approval.expires_at)
        except AnchorProtocolError as exc:
            raise ApiError(422, str(exc)) from None
        if issued > now or expires <= now or expires - issued > timedelta(minutes=15):
            raise ApiError(422, "operator-approval-expired-or-not-yet-valid")
        if not VALID_REASON.fullmatch(approval.reason_code):
            raise ApiError(422, "approval-reason-invalid")
        row = db.execute("SELECT sequence,record_sha256 FROM checkpoints WHERE database_id=? ORDER BY sequence DESC LIMIT 1", (database_id,)).fetchone()
        current_seq = int(row["sequence"]) if row else 0
        current_head = str(row["record_sha256"]) if row else None
        if current_seq != len(records) or (records and current_head != records[-1]["record_sha256"]):
            raise ApiError(503, "anchor-head-index-inconsistent")
        if approval.expected_sequence != current_seq or approval.expected_head_sha256 != current_head:
            return {"status": "CONFLICT", "error": "anchor-head-changed", "current_sequence": current_seq,
                    "current_head_sha256": current_head}, 409
        try:
            db.execute("INSERT INTO approvals_used(database_id,approval_id,nonce,request_id) VALUES(?,?,?,?)",
                       (database_id, approval.approval_id, approval.nonce, request_id))
        except sqlite3.IntegrityError:
            return {"status": "CONFLICT", "error": "approval-replayed", "request_id": request_id}, 409
        current_time = iso(now)
        record_body = {"sequence": current_seq + 1, "database_id": database_id,
                       **snap, "approval_id": approval.approval_id, "approval_nonce": approval.nonce,
                       "reason_code": approval.reason_code, "created_at": current_time,
                       "previous_record_sha256": current_head, "request_id": request_id,
                       "request_sha256": request_sha, "server_key_id": self.server_key_id}
        record_sha = sha_json(record_body)
        sig = self.server_private_key.sign(DOMAIN_RECORD + canonical({"body": record_body, "record_sha256": record_sha,
                                                                      "server_key_id": self.server_key_id}))
        rec = {"body": record_body, "record_sha256": record_sha, "server_key_id": self.server_key_id, "signature_b64": b64(sig)}
        rec_json = canonical(rec).decode("utf-8")
        db.execute("INSERT INTO checkpoints(database_id,sequence,record_json,record_sha256,request_id,request_sha256) VALUES(?,?,?,?,?,?)",
                   (database_id, current_seq + 1, rec_json, record_sha, request_id, request_sha))
        db.execute("INSERT INTO requests(database_id,request_id,request_sha256,record_json,created_at) VALUES(?,?,?,?,?)",
                   (database_id, request_id, request_sha, rec_json, int(time.time())))
        return {"status": "COMMITTED", "request_id": request_id, "request_sha256": request_sha,
                "record": rec, "idempotent_replay": False}, 200


class ApiError(Exception):
    def __init__(self, status: int, code: str):
        self.status = status
        self.code = code
        super().__init__(code)


class AnchorHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], service: RemoteAnchorService):
        self.service = service
        super().__init__(address, AnchorRequestHandler)


class AnchorRequestHandler(BaseHTTPRequestHandler):
    server: AnchorHTTPServer
    protocol_version = "HTTP/1.1"

    def log_message(self, *_: Any) -> None:
        return

    def _dispatch(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = -1
        if content_length < 0 or content_length > 1_000_000:
            response = self.server.service._sign_response(413, {"error": "request-body-size-invalid"})
            payload = canonical(response)
            self.send_response(413)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            self.close_connection = True
            return
        raw = self.rfile.read(content_length) if self.command == "POST" else b""
        headers = {k: v for k, v in self.headers.items()}
        status, response, drop = self.server.service.handle(self.command, self.path, raw, headers)
        if drop:
            self.close_connection = True
            try:
                self.connection.shutdown(2)
            except OSError:
                pass
            self.connection.close()
            return
        payload = canonical(response or {})
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.close_connection = True

    do_GET = _dispatch
    do_POST = _dispatch


class _NoRedirectHandler(HTTPRedirectHandler):
    """Never forward a signed anchor request to a redirect target."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class RemoteAnchorClient:
    def __init__(self, base_url: str, *, client_key_id: str, client_key: bytes,
                 server_keys: Mapping[str, Ed25519PublicKey], server_key_id: str,
                 timeout_seconds: float = 2.0, allow_http_loopback: bool = False):
        parsed = urlparse(base_url)
        loopback = parsed.hostname in {"127.0.0.1", "::1", "localhost"}
        if parsed.scheme != "https" and not (allow_http_loopback and parsed.scheme == "http" and loopback):
            raise AnchorProtocolError("anchor-url-must-use-https-unless-explicit-loopback-test")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise AnchorProtocolError("anchor-url-components-invalid")
        if not VALID_ID.fullmatch(client_key_id) or not isinstance(client_key, bytes) or len(client_key) < MIN_KEY_BYTES:
            raise AnchorProtocolError("anchor-client-key-invalid")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise AnchorProtocolError("anchor-timeout-invalid")
        if any(not isinstance(k, str) or not VALID_ID.fullmatch(k) or not isinstance(v, Ed25519PublicKey)
               for k, v in server_keys.items()):
            raise AnchorProtocolError("anchor-server-key-registry-invalid")
        if server_key_id not in server_keys:
            raise AnchorProtocolError("anchor-server-key-untrusted")
        self.base_url = base_url.rstrip("/")
        self.client_key_id = client_key_id
        self.client_key = client_key
        self.server_keys = dict(server_keys)
        self.server_key_id = server_key_id
        self.timeout_seconds = timeout_seconds
        self._opener = build_opener(_NoRedirectHandler())

    def _request(self, method: str, path: str, body_obj: Mapping[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        body = canonical(dict(body_obj)) if body_obj is not None else b""
        timestamp = str(int(time.time()))
        nonce = b64(os.urandom(18)).rstrip("=").replace("+", "-").replace("/", "_")
        req_auth = {"method": method, "path": path, "timestamp": timestamp, "nonce": nonce, "body_sha256": sha256(body)}
        signature = hmac.new(self.client_key, canonical(req_auth), hashlib.sha256).hexdigest()
        headers = {"Accept": "application/json", "X-Anchor-Key-Id": self.client_key_id,
                   "X-Anchor-Timestamp": timestamp, "X-Anchor-Nonce": nonce,
                   "X-Anchor-Signature": signature}
        if body_obj is not None:
            headers["Content-Type"] = "application/json"
        req = Request(self.base_url + path, data=body if body_obj is not None else None, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=self.timeout_seconds) as response:
                status = response.status
                raw = response.read(1_000_001)
        except HTTPError as exc:
            status = exc.code
            try:
                raw = exc.read(1_000_001)
            finally:
                exc.close()
        except (URLError, TimeoutError, OSError, ConnectionError) as exc:
            raise AnchorTransportError(f"anchor-transport-uncertain:{type(exc).__name__}") from None
        if len(raw) > 1_000_000:
            raise AnchorProtocolError("anchor-response-too-large")
        try:
            outer = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            raise AnchorProtocolError("anchor-response-invalid-json") from None
        expected_fields = {"http_status", "body", "server_key_id", "signature_b64"}
        if not isinstance(outer, Mapping) or set(outer) != expected_fields or type(outer.get("http_status")) is not int or not isinstance(outer.get("body"), Mapping):
            raise AnchorProtocolError("anchor-response-shape-invalid")
        if outer["http_status"] != status or outer["server_key_id"] != self.server_key_id:
            raise AnchorProtocolError("anchor-response-status-or-key-mismatch")
        key = self.server_keys.get(outer["server_key_id"])
        if key is None:
            raise AnchorProtocolError("anchor-server-key-untrusted")
        unsigned = {"http_status": outer["http_status"], "body": dict(outer["body"]), "server_key_id": outer["server_key_id"]}
        try:
            key.verify(unb64(outer["signature_b64"]), DOMAIN_RESPONSE + canonical(unsigned))
        except InvalidSignature:
            raise AnchorProtocolError("anchor-response-signature-invalid") from None
        return status, dict(outer["body"])

    def publish(self, database_id: str, request_body: Mapping[str, Any]) -> tuple[int, dict[str, Any]]:
        return self._request("POST", f"/v1/databases/{quote(database_id, safe='')}/checkpoints", request_body)

    def request_status(self, database_id: str, request_id: str) -> tuple[int, dict[str, Any]]:
        return self._request("GET", f"/v1/databases/{quote(database_id, safe='')}/requests/{quote(request_id, safe='')}")

    def history(self, database_id: str) -> tuple[int, dict[str, Any]]:
        status, payload = self._request("GET", f"/v1/databases/{quote(database_id, safe='')}/history")
        if status != 200 or payload.get("database_id") != database_id or not isinstance(payload.get("records"), list):
            raise AnchorProtocolError("anchor-history-response-invalid")
        previous = None
        for sequence, record in enumerate(payload["records"], start=1):
            verified = verify_record(record, self.server_keys, expected_previous=previous,
                                     expected_sequence=sequence, expected_database_id=database_id)
            previous = verified.record_sha256
        return status, payload


@dataclass(frozen=True)
class PendingRequest:
    request_id: str
    database_id: str
    snapshot: Mapping[str, Any]
    approval: Mapping[str, Any]
    request_sha256: str
    state: str
    response_json: str | None


class PublishOutbox:
    """Authenticated persistent client outbox. Stores only the proposed snapshot and approval."""
    FIELDS = ("request_id", "database_id", "request_json", "request_sha256", "state", "response_json", "updated_at")

    def __init__(self, path: str | Path, *, integrity_key: bytes):
        if not isinstance(integrity_key, bytes) or len(integrity_key) < MIN_KEY_BYTES:
            raise AnchorProtocolError("outbox-integrity-key-too-short")
        self.path = Path(path).resolve()
        self.integrity_key = integrity_key
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._db()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS publish_outbox (request_id TEXT PRIMARY KEY, database_id TEXT NOT NULL, request_json TEXT NOT NULL, request_sha256 TEXT NOT NULL, state TEXT NOT NULL, response_json TEXT, updated_at INTEGER NOT NULL, row_hmac_sha256 TEXT NOT NULL)")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            raise AnchorProtocolError("outbox-permissions-could-not-be-restricted") from None

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _mac(self, row: Mapping[str, Any]) -> str:
        body = {field: row[field] for field in self.FIELDS}
        return hmac.new(self.integrity_key, b"lycheetah-remote-publish-outbox-v3.1\n" + canonical(body), hashlib.sha256).hexdigest()

    def prepare(self, request_id: str, database_id: str, snapshot: Mapping[str, Any], approval: Mapping[str, Any]) -> PendingRequest:
        if not isinstance(request_id, str) or not VALID_REQ.fullmatch(request_id):
            raise AnchorProtocolError("outbox-request-id-invalid")
        if not isinstance(database_id, str) or not VALID_ID.fullmatch(database_id):
            raise AnchorProtocolError("outbox-database-id-invalid")
        snap = validate_snapshot(snapshot)
        approval_obj = OperatorApproval.from_dict(approval)
        if approval_obj.request_id != request_id or approval_obj.database_id != database_id or dict(approval_obj.snapshot) != snap:
            raise AnchorProtocolError("outbox-approval-does-not-bind-request")
        body = {"request_id": request_id, "snapshot": snap, "approval": approval_obj.to_dict()}
        body_json = canonical(body).decode("utf-8")
        body_sha = sha_json(body)
        now = int(time.time())
        row = {"request_id": request_id, "database_id": database_id, "request_json": body_json,
               "request_sha256": body_sha, "state": "PENDING", "response_json": None, "updated_at": now}
        row["row_hmac_sha256"] = self._mac(row)
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM publish_outbox WHERE request_id=?", (request_id,)).fetchone()
            if old is not None:
                self._verify_row(dict(old))
                if old["request_sha256"] != body_sha or old["database_id"] != database_id:
                    db.rollback()
                    raise AnchorProtocolError("outbox-request-id-reused-with-different-content")
                db.commit()
                return self.load(request_id)
            db.execute("INSERT INTO publish_outbox(request_id,database_id,request_json,request_sha256,state,response_json,updated_at,row_hmac_sha256) VALUES(?,?,?,?,?,?,?,?)",
                       (row["request_id"], row["database_id"], row["request_json"], row["request_sha256"], row["state"], row["response_json"], row["updated_at"], row["row_hmac_sha256"]))
            db.commit()
        return self.load(request_id)

    def _verify_row(self, row: Mapping[str, Any]) -> None:
        if row.get("state") not in {"PENDING", "UNKNOWN", "COMMITTED", "CONFLICT"}:
            raise AnchorProtocolError("outbox-state-invalid")
        if not hmac.compare_digest(str(row.get("row_hmac_sha256", "")), self._mac(row)):
            raise AnchorProtocolError("outbox-row-authentication-failed")
        try:
            body = json.loads(row["request_json"])
        except (json.JSONDecodeError, TypeError):
            raise AnchorProtocolError("outbox-request-json-invalid") from None
        if not isinstance(body, Mapping) or sha_json(body) != row["request_sha256"] or body.get("request_id") != row["request_id"]:
            raise AnchorProtocolError("outbox-request-digest-invalid")

    def load(self, request_id: str) -> PendingRequest:
        with closing(self._db()) as db:
            row = db.execute("SELECT * FROM publish_outbox WHERE request_id=?", (request_id,)).fetchone()
        if row is None:
            raise AnchorProtocolError("outbox-request-not-found")
        raw = dict(row)
        self._verify_row(raw)
        body = json.loads(raw["request_json"])
        return PendingRequest(request_id=raw["request_id"], database_id=raw["database_id"], snapshot=body["snapshot"],
                              approval=body["approval"], request_sha256=raw["request_sha256"], state=raw["state"],
                              response_json=raw["response_json"])

    def set_state(self, request_id: str, state: str, response: Mapping[str, Any] | None = None) -> PendingRequest:
        if state not in {"PENDING", "UNKNOWN", "COMMITTED", "CONFLICT"}:
            raise AnchorProtocolError("outbox-state-invalid")
        with closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            raw = db.execute("SELECT * FROM publish_outbox WHERE request_id=?", (request_id,)).fetchone()
            if raw is None:
                db.rollback()
                raise AnchorProtocolError("outbox-request-not-found")
            row = dict(raw)
            self._verify_row(row)
            if row["state"] in {"COMMITTED", "CONFLICT"}:
                db.rollback()
                if state != row["state"]:
                    raise AnchorProtocolError("outbox-terminal-state-cannot-change")
                raise AnchorProtocolError("outbox-terminal-state-cannot-be-rewritten")
            response_json = canonical(dict(response)).decode("utf-8") if response is not None else row["response_json"]
            changed = {**row, "state": state, "response_json": response_json, "updated_at": int(time.time())}
            changed["row_hmac_sha256"] = self._mac(changed)
            db.execute("UPDATE publish_outbox SET state=?,response_json=?,updated_at=?,row_hmac_sha256=? WHERE request_id=?",
                       (changed["state"], changed["response_json"], changed["updated_at"], changed["row_hmac_sha256"], request_id))
            db.commit()
        return self.load(request_id)


class RemoteAnchorPublisher:
    """Publishes a durable outbox request; uncertainty never silently becomes failure."""
    def __init__(self, client: RemoteAnchorClient, outbox: PublishOutbox):
        self.client = client
        self.outbox = outbox

    def publish_or_resume(self, request_id: str) -> PendingRequest:
        pending = self.outbox.load(request_id)
        if pending.state in {"COMMITTED", "CONFLICT"}:
            return pending
        body = {"request_id": pending.request_id, "snapshot": dict(pending.snapshot), "approval": dict(pending.approval)}
        # Verify exact persisted request before any HTTP operation.
        if sha_json(body) != pending.request_sha256:
            raise AnchorProtocolError("outbox-payload-no-longer-matches-authenticated-digest")
        if pending.state == "UNKNOWN":
            return self._resolve_uncertain(pending, body)
        try:
            status, payload = self.client.publish(pending.database_id, body)
            return self._consume_post_result(pending, status, payload)
        except (AnchorTransportError, AnchorProtocolError):
            return self._resolve_uncertain(pending, body)

    def _consume_post_result(self, pending: PendingRequest, status: int, payload: Mapping[str, Any]) -> PendingRequest:
        if status == 200 and payload.get("status") == "COMMITTED":
            self._verify_published_record(pending, payload)
            return self.outbox.set_state(pending.request_id, "COMMITTED", payload)
        if status == 409 or payload.get("status") == "CONFLICT":
            return self.outbox.set_state(pending.request_id, "CONFLICT", payload)
        if status >= 500:
            return self._resolve_uncertain(pending, {"request_id": pending.request_id, "snapshot": dict(pending.snapshot), "approval": dict(pending.approval)})
        return self.outbox.set_state(pending.request_id, "CONFLICT", {"status": "REFUSED", "http_status": status, **dict(payload)})

    def _resolve_uncertain(self, pending: PendingRequest, body: Mapping[str, Any]) -> PendingRequest:
        try:
            status, result = self.client.request_status(pending.database_id, pending.request_id)
        except (AnchorTransportError, AnchorProtocolError):
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "authoritative-request-lookup-unavailable"})
        if status != 200:
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "request-lookup-nonauthoritative"})
        if result.get("database_id") != pending.database_id or result.get("request_id") != pending.request_id:
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "request-lookup-identity-mismatch"})
        if result.get("status") == "FOUND":
            if result.get("request_sha256") != pending.request_sha256:
                return self.outbox.set_state(pending.request_id, "CONFLICT", {"status": "CONFLICT", "reason": "remote-request-payload-digest-mismatch"})
            record = result.get("record")
            try:
                self._verify_record_for_pending(pending, record)
            except AnchorProtocolError:
                return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "found-record-failed-verification"})
            return self.outbox.set_state(pending.request_id, "COMMITTED", {"status": "COMMITTED", "request_id": pending.request_id,
                                                                             "request_sha256": pending.request_sha256, "record": record,
                                                                             "recovered_by": "authoritative-request-lookup"})
        if result.get("status") != "NOT_FOUND":
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "request-lookup-status-invalid"})
        # An authoritative not-found can still race with a just-arriving append; retry only
        # the exact persisted body under the same idempotency key, once.
        try:
            status2, result2 = self.client.publish(pending.database_id, body)
        except (AnchorTransportError, AnchorProtocolError):
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "retry-result-unknown"})
        try:
            return self._consume_post_result_no_recursion(pending, status2, result2)
        except AnchorProtocolError:
            return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "retry-response-failed-verification"})

    def _consume_post_result_no_recursion(self, pending: PendingRequest, status: int, payload: Mapping[str, Any]) -> PendingRequest:
        if status == 200 and payload.get("status") == "COMMITTED":
            self._verify_published_record(pending, payload)
            return self.outbox.set_state(pending.request_id, "COMMITTED", payload)
        if status == 409 or payload.get("status") == "CONFLICT":
            return self.outbox.set_state(pending.request_id, "CONFLICT", payload)
        return self.outbox.set_state(pending.request_id, "UNKNOWN", {"status": "UNKNOWN", "reason": "retry-did-not-establish-commit", "http_status": status})

    def _verify_published_record(self, pending: PendingRequest, payload: Mapping[str, Any]) -> None:
        if payload.get("request_id") != pending.request_id or payload.get("request_sha256") != pending.request_sha256:
            raise AnchorProtocolError("publish-response-request-binding-invalid")
        self._verify_record_for_pending(pending, payload.get("record"))

    def _verify_record_for_pending(self, pending: PendingRequest, record: Any) -> AnchorRecord:
        if not isinstance(record, Mapping):
            raise AnchorProtocolError("publish-record-missing")
        approval = OperatorApproval.from_dict(pending.approval)
        parent = approval.expected_head_sha256
        sequence = approval.expected_sequence + 1
        verified = verify_record(record, self.client.server_keys, expected_previous=parent,
                                 expected_sequence=sequence, expected_database_id=pending.database_id)
        body = verified.body
        if body.get("request_id") != pending.request_id or body.get("request_sha256") != pending.request_sha256:
            raise AnchorProtocolError("anchor-record-request-binding-invalid")
        if body.get("logical_sha256") != pending.snapshot.get("logical_sha256"):
            raise AnchorProtocolError("anchor-record-snapshot-binding-invalid")
        if body.get("approval_id") != approval.approval_id or body.get("approval_nonce") != approval.nonce:
            raise AnchorProtocolError("anchor-record-approval-binding-invalid")
        return verified


def make_service_handler(server: AnchorHTTPServer) -> None:
    """No-op compatibility marker; HTTPServer installs AnchorRequestHandler automatically."""
    return None
