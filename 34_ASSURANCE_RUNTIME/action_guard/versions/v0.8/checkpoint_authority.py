"""Lycheetah v0.8 signed external checkpoint authority.

A separate HTTP service and SQLite file store monotonically advancing signed
checkpoints for one or more audit journals. The service's Ed25519 private key
never leaves this process. Clients must pin/provision the public key separately.
Research prototype: production should use managed key custody, service identity,
TLS, backups, independent monitoring, and a separately administered host/account.
"""
from __future__ import annotations

import base64
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

FORMAT = "lycheetah-signed-checkpoint-v1"
CHECKPOINT_GENESIS = sha256(b"lycheetah-checkpoint-authority-genesis-v1").hexdigest()
MAX_BODY = 65_536


def canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _envelope_hash(envelope: dict[str, Any]) -> str:
    body = {k: v for k, v in envelope.items() if k != "envelope_hash"}
    return sha256(canonical_json(body)).hexdigest()


def _signing_payload(envelope: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in envelope.items() if k not in ("signature", "envelope_hash")}


def verify_envelope(envelope: dict[str, Any], public_key_bytes: bytes,
                    expected_journal_id: str | None = None) -> bool:
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
    """Monotonic signed checkpoint store, intended to run in a separate process."""

    def __init__(self, db_path: str | Path, private_key_path: str | Path):
        self.db_path = str(db_path)
        self.key_path = Path(private_key_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self._key_lock = threading.Lock()
        self._private_key = self._load_or_create_private_key()
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS checkpoint_history (
                    journal_id TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    event_count INTEGER NOT NULL,
                    last_seq INTEGER,
                    root_hash TEXT NOT NULL,
                    envelope_json TEXT NOT NULL,
                    envelope_hash TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    PRIMARY KEY(journal_id, generation),
                    UNIQUE(journal_id, envelope_hash)
                );
                CREATE INDEX IF NOT EXISTS checkpoint_latest_idx
                    ON checkpoint_history(journal_id, generation DESC);
            """)

    def _load_or_create_private_key(self) -> Ed25519PrivateKey:
        with self._key_lock:
            if self.key_path.exists():
                key = serialization.load_pem_private_key(self.key_path.read_bytes(), password=None)
                if not isinstance(key, Ed25519PrivateKey):
                    raise CheckpointError("checkpoint_signing_key_wrong_type")
                try:
                    os.chmod(self.key_path, 0o600)
                except OSError:
                    pass
                return key
            key = Ed25519PrivateKey.generate()
            pem = key.private_bytes(serialization.Encoding.PEM,
                                    serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption())
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = os.open(self.key_path, flags, 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(pem)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.chmod(self.key_path, 0o600)
            except OSError:
                pass
            return key

    def public_key_bytes(self) -> bytes:
        return self._private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10, isolation_level=None, factory=_ClosingConnection)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    @staticmethod
    def _validate_anchor(anchor: dict[str, Any]) -> tuple[int, int | None, str]:
        if not isinstance(anchor, dict):
            raise CheckpointError("anchor_must_be_object")
        try:
            count = anchor["event_count"]
            last_seq = anchor["last_seq"]
            root_hash = anchor["root_hash"]
        except KeyError as exc:
            raise CheckpointError("anchor_missing_field") from exc
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise CheckpointError("invalid_event_count")
        if count == 0 and last_seq is not None:
            raise CheckpointError("empty_anchor_last_seq_must_be_null")
        if count > 0 and (isinstance(last_seq, bool) or not isinstance(last_seq, int) or last_seq != count):
            raise CheckpointError("invalid_last_seq")
        if not isinstance(root_hash, str) or len(root_hash) != 64:
            raise CheckpointError("invalid_root_hash")
        try:
            int(root_hash, 16)
        except ValueError as exc:
            raise CheckpointError("invalid_root_hash") from exc
        # Do not accept arbitrary extra fields that might be interpreted differently by clients.
        if set(anchor) != {"event_count", "last_seq", "root_hash"}:
            raise CheckpointError("unexpected_anchor_field")
        return count, last_seq, root_hash

    @staticmethod
    def _verify_extension(events: list[dict[str, Any]], prior_count: int,
                          prior_last_seq: int | None, prior_root: str,
                          proposed_anchor: dict[str, Any]) -> None:
        if not isinstance(events, list) or len(events) > 256:
            raise CheckpointError("invalid_event_batch")
        expected_seq = 1 if prior_last_seq is None else prior_last_seq + 1
        root = prior_root
        required = {"seq", "at", "actor", "approval_id", "effect_id", "event", "reason",
                    "details_json", "prev_hash", "event_hash"}
        for event in events:
            if not isinstance(event, dict) or set(event) != required:
                raise CheckpointError("invalid_audit_event_shape")
            seq = event["seq"]
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
                canonical_details = json.dumps(details_value, sort_keys=True, separators=(",", ":"),
                                               ensure_ascii=False, allow_nan=False)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise CheckpointError("invalid_audit_details_json") from exc
            if canonical_details != event["details_json"]:
                raise CheckpointError("noncanonical_audit_details_json")
            payload = {
                "seq": seq, "at": event["at"], "actor": event["actor"],
                "approval_id": event["approval_id"], "effect_id": event["effect_id"],
                "event": event["event"], "reason": event["reason"],
                "details_json": event["details_json"], "prev_hash": event["prev_hash"],
                "format": "lycheetah-action-guard-audit-event-v1",
            }
            computed = sha256(canonical_json(payload)).hexdigest()
            if event["event_hash"] != computed:
                raise CheckpointError("audit_event_hash_mismatch")
            root = computed
            expected_seq += 1
        expected_count = prior_count + len(events)
        expected_last_seq = None if expected_count == 0 else expected_count
        if (proposed_anchor["event_count"] != expected_count
                or proposed_anchor["last_seq"] != expected_last_seq
                or proposed_anchor["root_hash"] != root):
            raise CheckpointError("proposed_anchor_does_not_match_verified_extension")

    def latest(self, journal_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT envelope_json FROM checkpoint_history WHERE journal_id=? ORDER BY generation DESC LIMIT 1", (journal_id,)).fetchone()
        return json.loads(row["envelope_json"]) if row else None

    def store(self, journal_id: str, anchor: dict[str, Any], events: list[dict[str, Any]], *, issued_at: int | None = None) -> dict[str, Any]:
        if not isinstance(journal_id, str) or not journal_id or len(journal_id) > 200 or "\x00" in journal_id:
            raise CheckpointError("invalid_journal_id")
        count, last_seq, root_hash = self._validate_anchor(anchor)
        if not isinstance(events, list):
            raise CheckpointError("events_must_be_list")
        now = int(time.time()) if issued_at is None else int(issued_at)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM checkpoint_history WHERE journal_id=? ORDER BY generation DESC LIMIT 1", (journal_id,)).fetchone()
            if row is not None:
                previous = json.loads(row["envelope_json"])
                if (not verify_envelope(previous, self.public_key_bytes(), journal_id)
                        or int(row["generation"]) != previous.get("generation")
                        or int(row["event_count"]) != previous.get("event_count")
                        or row["last_seq"] != previous.get("last_seq")
                        or row["root_hash"] != previous.get("root_hash")
                        or row["envelope_hash"] != previous.get("envelope_hash")):
                    db.execute("ROLLBACK")
                    raise CheckpointError("checkpoint_store_integrity_failure")
                old_count = int(previous["event_count"])
                if count < old_count:
                    db.execute("ROLLBACK")
                    raise CheckpointConflict("checkpoint_rollback_rejected")
                if count == old_count:
                    if root_hash == previous["root_hash"] and last_seq == previous["last_seq"]:
                        db.execute("COMMIT")
                        return previous  # idempotent retry after lost response
                    db.execute("ROLLBACK")
                    raise CheckpointConflict("same_sequence_different_root_rejected")
                generation = int(previous["generation"]) + 1
                previous_hash = str(previous["envelope_hash"])
                prior_count = old_count
                prior_last_seq = previous["last_seq"]
                prior_root = str(previous["root_hash"])
            else:
                generation = 1
                previous_hash = CHECKPOINT_GENESIS
                prior_count, prior_last_seq, prior_root = 0, None, sha256(b"lycheetah-action-guard-audit-chain-v1").hexdigest()
            self._verify_extension(events, prior_count, prior_last_seq, prior_root,
                                   {"event_count": count, "last_seq": last_seq, "root_hash": root_hash})
            envelope: dict[str, Any] = {
                "format": FORMAT,
                "journal_id": journal_id,
                "generation": generation,
                "event_count": count,
                "last_seq": last_seq,
                "root_hash": root_hash,
                "previous_envelope_hash": previous_hash,
                "issued_at": now,
            }
            signature = self._private_key.sign(canonical_json(envelope))
            envelope["signature"] = base64.b64encode(signature).decode("ascii")
            envelope["envelope_hash"] = _envelope_hash(envelope)
            db.execute("INSERT INTO checkpoint_history(journal_id,generation,event_count,last_seq,root_hash,envelope_json,envelope_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
                       (journal_id, generation, count, last_seq, root_hash,
                        json.dumps(envelope, sort_keys=True, separators=(",", ":")),
                        envelope["envelope_hash"], now))
            db.execute("COMMIT")
            return envelope


class CheckpointHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(store: CheckpointStore, bearer_token: str,
                host: str = "127.0.0.1", port: int = 0) -> CheckpointHTTPServer:
    """Build a loopback-only JSON server, to be fronted by a TLS proxy if remote."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("bind_to_loopback_only_and_use_a_tls_proxy")
    if not bearer_token or len(bearer_token) < 24:
        raise ValueError("bearer token must be at least 24 characters")

    class Handler(BaseHTTPRequestHandler):
        server_version = "LycheetahCheckpoint/0.8"
        sys_version = ""

        def log_message(self, _format: str, *args: Any) -> None:
            # Avoid logging Authorization headers or payload contents.
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
                self._json(401, {"error": "unauthorized"}); return
            journal_id = self._journal_id()
            if journal_id is None:
                self._json(404, {"error": "not_found"}); return
            envelope = store.latest(journal_id)
            if envelope is None:
                self._json(404, {"error": "checkpoint_not_found"}); return
            self._json(200, {"checkpoint": envelope})

        def do_POST(self) -> None:
            if not self._authorized():
                self._json(401, {"error": "unauthorized"}); return
            journal_id = self._journal_id()
            if journal_id is None:
                self._json(404, {"error": "not_found"}); return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 1 or size > MAX_BODY:
                    self._json(413, {"error": "invalid_body_size"}); return
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict) or set(body) != {"anchor", "events"}:
                    self._json(400, {"error": "invalid_request"}); return
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
    """Minimal authenticated client; verifies every receipt against a pinned key."""
    def __init__(self, base_url: str, bearer_token: str, pinned_public_key: bytes, timeout: float = 2.0):
        parsed = urlparse(base_url)
        is_loopback_http = parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1")
        if not is_loopback_http and parsed.scheme != "https":
            raise ValueError("non-loopback clients require HTTPS")
        if parsed.username or parsed.password or not parsed.hostname:
            raise ValueError("invalid_checkpoint_service_url")
        self.base_url = base_url.rstrip("/")
        self.token = bearer_token
        self.public_key = pinned_public_key
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        wire = canonical_json(payload) if payload is not None else None
        req = Request(self.base_url + path, data=wire, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        try:
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read(MAX_BODY + 1))
        except HTTPError as exc:
            body = exc.read(2000).decode("utf-8", "replace")
            try: code = json.loads(body).get("error", f"http_{exc.code}")
            except Exception: code = f"http_{exc.code}"
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
        if not isinstance(envelope, dict) or not verify_envelope(envelope, self.public_key, journal_id):
            raise CheckpointError("invalid_checkpoint_signature_or_identity")
        return envelope

    def publish(self, journal_id: str, anchor: dict[str, Any],
                events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        path = "/v1/checkpoints/" + quote(journal_id, safe="")
        response = self._request("POST", path, {"anchor": anchor, "events": events or []})
        envelope = response.get("checkpoint")
        if not isinstance(envelope, dict) or not verify_envelope(envelope, self.public_key, journal_id):
            raise CheckpointError("invalid_checkpoint_signature_or_identity")
        if {k: envelope.get(k) for k in ("event_count", "last_seq", "root_hash")} != anchor:
            raise CheckpointError("checkpoint_anchor_mismatch")
        return envelope


if __name__ == "__main__":
    import argparse
    import signal

    parser = argparse.ArgumentParser(description="Lycheetah v0.8 signed checkpoint authority")
    parser.add_argument("--db", default="./checkpoint-service/checkpoints.sqlite3")
    parser.add_argument("--key", default="./checkpoint-service/ed25519-private.pem")
    parser.add_argument("--public-key-out", default="./checkpoint-service/ed25519-public.raw")
    parser.add_argument("--host", default="127.0.0.1", help="Keep loopback unless deployed behind authenticated TLS proxy")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--token-env", default="LYCHEETAH_CHECKPOINT_TOKEN")
    args = parser.parse_args()
    token = os.environ.get(args.token_env, "")
    if len(token) < 24:
        raise SystemExit(f"Set {args.token_env} to a high-entropy secret of at least 24 characters")
    store = CheckpointStore(args.db, args.key)
    public_out = Path(args.public_key_out)
    public_out.parent.mkdir(parents=True, exist_ok=True)
    public_out.write_bytes(store.public_key_bytes())
    try:
        os.chmod(public_out, 0o644)
    except OSError:
        pass
    server = make_server(store, token, args.host, args.port)
    print(f"Checkpoint authority listening on {args.host}:{args.port}; public key written to {public_out}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
