"""Lycheetah signed external checkpoint authority.

A separate service and SQLite store monotonically advancing signed checkpoints for
one or more audit journals using Ed25519 signatures.
"""
from __future__ import annotations

import base64
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import ProxyHandler, Request, build_opener

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

FORMAT = "lycheetah-signed-checkpoint-v1"
CHECKPOINT_GENESIS = sha256(b"lycheetah-checkpoint-authority-genesis-v1").hexdigest()
MAX_BODY = 65_536


def canonical_json(value: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 encoded canonical JSON bytes."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def _envelope_hash(envelope: dict[str, Any]) -> str:
    body = {k: v for k, v in envelope.items() if k != "envelope_hash"}
    return sha256(canonical_json(body)).hexdigest()


def _signing_payload(envelope: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in envelope.items() if k not in ("signature", "envelope_hash")}


def verify_envelope(
    envelope: dict[str, Any],
    public_key_bytes: bytes,
    expected_journal_id: str | None = None,
) -> bool:
    """Verify signature, envelope digest, format, and optionally journal identity."""
    try:
        if envelope.get("format") != FORMAT:
            return False
        if expected_journal_id is not None and envelope.get("journal_id") != expected_journal_id:
            return False
        if envelope.get("envelope_hash") != _envelope_hash(envelope):
            return False
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature = base64.b64decode(envelope["signature"], validate=True)
        public_key.verify(signature, canonical_json(_signing_payload(envelope)))
        return True
    except Exception:
        return False


class CheckpointError(RuntimeError):
    pass


class CheckpointConflict(CheckpointError):
    pass


class _ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


class CheckpointStore:
    """Monotonic signed checkpoint store, designed for out-of-process authority."""

    def __init__(self, db_path: str | Path, private_key_path: str | Path):
        self.db_path = str(db_path)
        self.key_path = Path(private_key_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self._key_lock = threading.Lock()
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS checkpoint_history (
                    generation INTEGER PRIMARY KEY AUTOINCREMENT,
                    journal_id TEXT NOT NULL,
                    event_count INTEGER NOT NULL,
                    last_seq INTEGER,
                    root_hash TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    envelope_hash TEXT NOT NULL,
                    envelope_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS checkpoint_journal_idx
                    ON checkpoint_history(journal_id, generation DESC);
            """)
        self._ensure_private_key()

    def _connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(
            self.db_path, timeout=15, isolation_level=None, factory=_ClosingConnection
        )
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("PRAGMA busy_timeout=15000")
        return c

    def _ensure_private_key(self) -> None:
        with self._key_lock:
            if not self.key_path.exists():
                key = Ed25519PrivateKey.generate()
                pem = key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                tmp = self.key_path.with_name(
                    f"{self.key_path.name}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
                )
                fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                try:
                    with open(fd, "wb") as f:
                        f.write(pem)
                    os.replace(tmp, self.key_path)
                finally:
                    if tmp.exists():
                        try:
                            tmp.unlink()
                        except OSError:
                            pass
            try:
                self.key_path.chmod(0o600)
            except OSError:
                pass

    def _load_private_key(self) -> Ed25519PrivateKey:
        with self._key_lock:
            pem = self.key_path.read_bytes()
            key = serialization.load_pem_private_key(pem, password=None)
            if not isinstance(key, Ed25519PrivateKey):
                raise RuntimeError("checkpoint key is not an Ed25519 private key")
            return key

    def public_key_bytes(self) -> bytes:
        return self._load_private_key().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @staticmethod
    def _validate_anchor(anchor: dict[str, Any]) -> tuple[int, int | None, str]:
        if not isinstance(anchor, dict):
            raise CheckpointError("anchor_must_be_dict")
        count = anchor.get("event_count")
        last_seq = anchor.get("last_seq")
        root = anchor.get("root_hash")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise CheckpointError("invalid_event_count")
        if count == 0:
            if last_seq is not None:
                raise CheckpointError("zero_event_count_requires_null_last_seq")
            if root != CHECKPOINT_GENESIS:
                from .action_guard import AUDIT_GENESIS

                if root != AUDIT_GENESIS:
                    raise CheckpointError("zero_event_count_requires_genesis_root")
        else:
            if isinstance(last_seq, bool) or not isinstance(last_seq, int) or last_seq != count:
                raise CheckpointError("invalid_last_seq")
            if not isinstance(root, str) or len(root) != 64:
                raise CheckpointError("invalid_root_hash")
        return count, last_seq, root

    @classmethod
    def _verify_extension(
        cls,
        prior_anchor: dict[str, Any] | None,
        proposed_anchor: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> None:
        prior_count = 0 if prior_anchor is None else prior_anchor["event_count"]
        prior_seq = None if prior_anchor is None else prior_anchor["last_seq"]
        from .action_guard import AUDIT_GENESIS

        prior_root = (
            AUDIT_GENESIS
            if prior_anchor is None
            else prior_anchor.get("root_hash", AUDIT_GENESIS)
        )
        if prior_root == CHECKPOINT_GENESIS:
            prior_root = AUDIT_GENESIS

        expected_seq = 1 if prior_seq is None else prior_seq + 1
        root = prior_root
        for event in events:
            if not isinstance(event, dict):
                raise CheckpointError("audit_event_must_be_dict")
            seq = event.get("seq")
            if isinstance(seq, bool) or not isinstance(seq, int) or seq != expected_seq:
                raise CheckpointError("audit_event_sequence_gap")
            if event["prev_hash"] != root:
                raise CheckpointError("audit_event_previous_hash_mismatch")
            if isinstance(event["at"], bool) or not isinstance(event["at"], int):
                raise CheckpointError("invalid_audit_timestamp")
            for name in ("actor", "event", "reason", "details_json", "prev_hash", "event_hash"):
                if not isinstance(event[name], str):
                    raise CheckpointError("invalid_audit_event_field")
            for name in ("approval_id", "effect_id"):
                if event[name] is not None and not isinstance(event[name], str):
                    raise CheckpointError("invalid_audit_reference")
            try:
                details_value = json.loads(event["details_json"])
                canonical_details = json.dumps(
                    details_value,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise CheckpointError("invalid_audit_details_json") from exc
            if canonical_details != event["details_json"]:
                raise CheckpointError("noncanonical_audit_details_json")
            payload = {
                "seq": seq,
                "at": event["at"],
                "actor": event["actor"],
                "approval_id": event["approval_id"],
                "effect_id": event["effect_id"],
                "event": event["event"],
                "reason": event["reason"],
                "details_json": event["details_json"],
                "prev_hash": event["prev_hash"],
                "format": "lycheetah-action-guard-audit-event-v1",
            }
            computed = sha256(canonical_json(payload)).hexdigest()
            if event["event_hash"] != computed:
                raise CheckpointError("audit_event_hash_mismatch")
            root = computed
            expected_seq += 1
        expected_count = prior_count + len(events)
        expected_last_seq = None if expected_count == 0 else expected_count
        if (
            proposed_anchor["event_count"] != expected_count
            or proposed_anchor["last_seq"] != expected_last_seq
            or proposed_anchor["root_hash"] != root
        ):
            raise CheckpointError("proposed_anchor_does_not_match_verified_extension")

    def latest(self, journal_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT envelope_json FROM checkpoint_history WHERE journal_id=? "
                "ORDER BY generation DESC LIMIT 1",
                (journal_id,),
            ).fetchone()
        return json.loads(row["envelope_json"]) if row else None

    def store(
        self,
        journal_id: str,
        anchor: dict[str, Any],
        events: list[dict[str, Any]],
        *,
        issued_at: int | None = None,
    ) -> dict[str, Any]:
        if (
            not isinstance(journal_id, str)
            or not journal_id
            or len(journal_id) > 200
            or "\x00" in journal_id
        ):
            raise CheckpointError("invalid_journal_id")
        count, last_seq, root_hash = self._validate_anchor(anchor)
        if not isinstance(events, list):
            raise CheckpointError("events_must_be_list")
        now = int(time.time()) if issued_at is None else int(issued_at)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM checkpoint_history WHERE journal_id=? ORDER BY generation DESC LIMIT 1",
                (journal_id,),
            ).fetchone()
            if row is not None:
                previous = json.loads(row["envelope_json"])
                if (
                    not verify_envelope(previous, self.public_key_bytes(), journal_id)
                    or int(row["generation"]) != previous.get("generation")
                    or int(row["event_count"]) != previous.get("event_count")
                    or row["last_seq"] != previous.get("last_seq")
                    or row["root_hash"] != previous.get("root_hash")
                    or row["envelope_hash"] != previous.get("envelope_hash")
                ):
                    db.execute("ROLLBACK")
                    raise CheckpointError("checkpoint_store_integrity_failure")
                old_count = int(previous["event_count"])
                if count < old_count:
                    db.execute("ROLLBACK")
                    raise CheckpointConflict("checkpoint_rollback_rejected")
                if count == old_count:
                    if root_hash == previous["root_hash"] and last_seq == previous["last_seq"]:
                        db.execute("COMMIT")
                        return previous
                    db.execute("ROLLBACK")
                    raise CheckpointConflict("same_count_fork_rejected")
                prior_anchor = {
                    "event_count": old_count,
                    "last_seq": previous["last_seq"],
                    "root_hash": previous["root_hash"],
                }
            else:
                prior_anchor = None
            proposed_anchor = {"event_count": count, "last_seq": last_seq, "root_hash": root_hash}
            self._verify_extension(prior_anchor, proposed_anchor, events)
            cur = db.execute(
                "INSERT INTO checkpoint_history(journal_id,event_count,last_seq,root_hash,issued_at,envelope_hash,envelope_json) "
                "VALUES(?,?,?,?,?,?,?)",
                (journal_id, count, last_seq, root_hash, now, "", ""),
            )
            generation = int(cur.lastrowid)
            envelope_core = {
                "format": FORMAT,
                "generation": generation,
                "journal_id": journal_id,
                "event_count": count,
                "last_seq": last_seq,
                "root_hash": root_hash,
                "issued_at": now,
            }
            priv = self._load_private_key()
            sig = priv.sign(canonical_json(envelope_core))
            signed_envelope = dict(envelope_core)
            signed_envelope["signature"] = base64.b64encode(sig).decode("ascii")
            signed_envelope["envelope_hash"] = _envelope_hash(signed_envelope)
            envelope_json = json.dumps(
                signed_envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            db.execute(
                "UPDATE checkpoint_history SET envelope_hash=?,envelope_json=? WHERE generation=?",
                (signed_envelope["envelope_hash"], envelope_json, generation),
            )
            db.execute("COMMIT")
            return signed_envelope


class CheckpointHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(
    store: CheckpointStore,
    bearer_token: str,
    host: str = "127.0.0.1",
    port: int = 0,
) -> CheckpointHTTPServer:
    """Build a loopback-only JSON server for signed checkpoint receipts."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("bind_to_loopback_only_and_use_a_tls_proxy")
    if not bearer_token or len(bearer_token) < 24:
        raise ValueError("bearer token must be at least 24 characters")

    class Handler(BaseHTTPRequestHandler):
        server_version = "LycheetahCheckpoint/1.0"
        sys_version = ""

        def log_message(self, _format: str, *args: Any) -> None:
            return

        def _json(self, code: int, obj: dict[str, Any]) -> None:
            wire = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(wire)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(wire)

        def _authorized(self) -> bool:
            header = self.headers.get("Authorization", "")
            return hmac.compare_digest(header, "Bearer " + bearer_token)

        def _journal_id(self) -> str | None:
            parts = urlparse(self.path).path.split("/")
            if len(parts) == 4 and parts[1:3] == ["v1", "checkpoints"]:
                return unquote(parts[3])
            return None

        def do_GET(self) -> None:
            if urlparse(self.path).path == "/health":
                self._json(200, {"status": "ok", "service": "lycheetah-checkpoint-authority"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            journal_id = self._journal_id()
            if journal_id is None:
                self._json(404, {"error": "not_found"})
                return
            envelope = store.latest(journal_id)
            if envelope is None:
                self._json(404, {"error": "checkpoint_not_found"})
                return
            self._json(200, {"checkpoint": envelope})

        def do_POST(self) -> None:
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            journal_id = self._journal_id()
            if journal_id is None:
                self._json(404, {"error": "not_found"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 1 or size > MAX_BODY:
                    self._json(413, {"error": "invalid_body_size"})
                    return
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict) or set(body) != {"anchor", "events"}:
                    self._json(400, {"error": "invalid_request"})
                    return
                envelope = store.store(journal_id, body["anchor"], body["events"])
                self._json(200, {"checkpoint": envelope})
            except CheckpointConflict as exc:
                self._json(409, {"error": str(exc)})
            except (CheckpointError, ValueError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
            except Exception:
                self._json(500, {"error": "internal_error"})

    return CheckpointHTTPServer((host, port), Handler)


class CheckpointHTTPClient:
    """Authenticated client for the checkpoint authority; verifies against a pinned public key."""

    def __init__(
        self,
        base_url: str,
        bearer_token: str,
        pinned_public_key: bytes,
        timeout: float = 3.0,
    ):
        parsed = urlparse(base_url)
        is_loopback = parsed.hostname in ("127.0.0.1", "localhost", "::1")
        if not is_loopback and parsed.scheme != "https":
            raise ValueError("non-loopback clients require HTTPS")
        if parsed.username or parsed.password or not parsed.hostname:
            raise ValueError("invalid_checkpoint_service_url")
        self.base_url = base_url.rstrip("/")
        self.token = bearer_token
        self.public_key = pinned_public_key
        self.timeout = timeout
        # For loopback IPC, bypass ambient http_proxy/https_proxy settings
        if is_loopback:
            self._opener = build_opener(ProxyHandler({}))
        else:
            self._opener = build_opener()

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        wire = canonical_json(payload) if payload is not None else None
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        req = Request(self.base_url + path, data=wire, method=method, headers=headers)
        try:
            with self._opener.open(req, timeout=self.timeout) as response:
                data = json.loads(response.read(MAX_BODY + 1))
        except HTTPError as exc:
            body = exc.read(2000).decode("utf-8", "replace")
            try:
                code = json.loads(body).get("error", f"http_{exc.code}")
            except Exception:
                code = f"http_{exc.code}"
            raise CheckpointError(str(code)) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise CheckpointError("checkpoint_service_unavailable") from exc
        if not isinstance(data, dict):
            raise CheckpointError("invalid_service_response")
        return data

    def get_latest(self, journal_id: str) -> dict[str, Any] | None:
        path = "/v1/checkpoints/" + quote(journal_id, safe="")
        try:
            response = self._request("GET", path)
        except CheckpointError as exc:
            if str(exc) == "checkpoint_not_found":
                return None
            raise
        envelope = response.get("checkpoint")
        if not isinstance(envelope, dict):
            raise CheckpointError("malformed_checkpoint_response")
        if not verify_envelope(envelope, self.public_key, journal_id):
            raise CheckpointError("checkpoint_signature_invalid")
        return envelope

    def publish(
        self, journal_id: str, anchor: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        path = "/v1/checkpoints/" + quote(journal_id, safe="")
        response = self._request("POST", path, {"anchor": anchor, "events": events})
        envelope = response.get("checkpoint")
        if not isinstance(envelope, dict):
            raise CheckpointError("malformed_checkpoint_response")
        if not verify_envelope(envelope, self.public_key, journal_id):
            raise CheckpointError("checkpoint_signature_invalid")
        return envelope
