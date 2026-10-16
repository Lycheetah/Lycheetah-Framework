"""External spent-challenge registry reference protocol (v3.5).

The SQLite service below is a local HTTP simulator for an independently
administered monotonic registry. It demonstrates cross-store rollback detection
when the verifier's primary ledger is restored but this registry remains current.
It is NOT itself rollback-proof if its own database/backups can also be restored.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
import time
import uuid
from contextlib import closing
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from remote_anchor_http import canonical, b64, unb64

DOMAIN_REGISTRY_REQUEST = b"lycheetah-spent-challenge-request-v3.6\n"
DOMAIN_REGISTRY_RESPONSE = b"lycheetah-spent-challenge-response-v3.6\n"
DOMAIN_REGISTRY_CLOCK = b"lyc-registry-clock-state-v3.6\n"
MIN_KEY_BYTES = 32
VALID_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
VALID_NONCE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
MAX_REQUEST_BYTES = 128 * 1024
MAX_RESPONSE_BYTES = 128 * 1024
MAX_CHALLENGE_TTL_MS = 60 * 60 * 1000


class RegistryProtocolError(ValueError):
    pass


class RegistryTransportError(RegistryProtocolError):
    pass


class RegistryRejected(RegistryProtocolError):
    pass


class RegistryClockError(RegistryProtocolError):
    """The service clock regressed or its authenticated high-water mark is invalid."""
    pass


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha_json(value: Any) -> str:
    return _sha256(canonical(value))


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _validate_challenge(body: Mapping[str, Any]) -> dict[str, Any]:
    fields = {"nonce", "database_id", "issued_at_ms", "expires_at_ms", "policy_sha256"}
    if not isinstance(body, Mapping) or set(body) != fields:
        raise RegistryProtocolError("challenge-fields-invalid")
    if not isinstance(body["nonce"], str) or not VALID_NONCE.fullmatch(body["nonce"]):
        raise RegistryProtocolError("challenge-nonce-invalid")
    if not isinstance(body["database_id"], str) or not VALID_ID.fullmatch(body["database_id"]):
        raise RegistryProtocolError("challenge-database-id-invalid")
    if type(body["issued_at_ms"]) is not int or type(body["expires_at_ms"]) is not int:
        raise RegistryProtocolError("challenge-time-type-invalid")
    if body["issued_at_ms"] < 0 or body["expires_at_ms"] <= body["issued_at_ms"]:
        raise RegistryProtocolError("challenge-time-range-invalid")
    if body["expires_at_ms"] - body["issued_at_ms"] > MAX_CHALLENGE_TTL_MS:
        raise RegistryProtocolError("challenge-ttl-exceeds-registry-limit")
    if not isinstance(body["policy_sha256"], str) or not HEX64.fullmatch(body["policy_sha256"]):
        raise RegistryProtocolError("challenge-policy-digest-invalid")
    return dict(body)


@dataclass(frozen=True)
class RegistryReceipt:
    http_status: int
    body: Mapping[str, Any]
    server_key_id: str
    request_id: str
    signature_b64: str

    def unsigned(self) -> dict[str, Any]:
        return {"http_status": self.http_status, "body": dict(self.body),
                "server_key_id": self.server_key_id, "request_id": self.request_id}

    def to_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "signature_b64": self.signature_b64}


class SpentChallengeRegistryService:
    """HTTP service model with atomic register/consume in its own SQLite store."""
    def __init__(self, path: str | Path, *, client_keys: Mapping[str, bytes], storage_key: bytes,
                 server_key_id: str, server_private_key: Ed25519PrivateKey,
                 max_clock_skew_ms: int = 30_000, clock_ms=None):
        if not isinstance(storage_key, bytes) or len(storage_key) < MIN_KEY_BYTES:
            raise RegistryProtocolError("registry-storage-key-invalid")
        if not VALID_ID.fullmatch(server_key_id) or not isinstance(server_private_key, Ed25519PrivateKey):
            raise RegistryProtocolError("registry-server-key-invalid")
        if type(max_clock_skew_ms) is not int or not 1_000 <= max_clock_skew_ms <= 300_000:
            raise RegistryProtocolError("registry-clock-skew-invalid")
        for kid, key in client_keys.items():
            if not VALID_ID.fullmatch(kid) or not isinstance(key, bytes) or len(key) < MIN_KEY_BYTES:
                raise RegistryProtocolError("registry-client-key-invalid")
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.client_keys = dict(client_keys)
        self.storage_key = bytes(storage_key)
        self.server_key_id = server_key_id
        self.server_private_key = server_private_key
        self.max_clock_skew_ms = max_clock_skew_ms
        self.clock_ms = clock_ms or _now_ms
        self.drop_before_commit_count = 0
        self.drop_after_commit_count = 0
        self._init_db()

    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _init_db(self):
        with closing(self._db()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS challenges(
                nonce TEXT PRIMARY KEY, database_id TEXT NOT NULL,
                issued_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL,
                policy_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PENDING','CONSUMED')),
                consumed_at_ms INTEGER, row_hmac TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS request_nonces(
                key_id TEXT NOT NULL, request_id TEXT NOT NULL, timestamp_ms INTEGER NOT NULL,
                PRIMARY KEY(key_id,request_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS clock_state(
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                high_water_ms INTEGER NOT NULL,
                prune_before_ms INTEGER NOT NULL,
                replay_window_ms INTEGER NOT NULL,
                row_hmac TEXT NOT NULL)""")
            clock_expected = [
                ("singleton", "INTEGER", 0, 1),
                ("high_water_ms", "INTEGER", 1, 0),
                ("prune_before_ms", "INTEGER", 1, 0),
                ("replay_window_ms", "INTEGER", 1, 0),
                ("row_hmac", "TEXT", 1, 0),
            ]
            clock_actual = [(r["name"], r["type"].upper(), r["notnull"], r["pk"])
                            for r in db.execute("PRAGMA table_info(clock_state)").fetchall()]
            if clock_actual != clock_expected:
                raise RegistryProtocolError("registry-clock-schema-incompatible")
            request_nonce_expected = [
                ("key_id", "TEXT", 1, 1),
                ("request_id", "TEXT", 1, 2),
                ("timestamp_ms", "INTEGER", 1, 0),
            ]
            request_nonce_actual = [(r["name"], r["type"].upper(), r["notnull"], r["pk"])
                                    for r in db.execute("PRAGMA table_info(request_nonces)").fetchall()]
            if request_nonce_actual != request_nonce_expected:
                raise RegistryProtocolError("registry-request-nonce-schema-incompatible")
            expected = [
                ("nonce", "TEXT", 0, 1), ("database_id", "TEXT", 1, 0),
                ("issued_at_ms", "INTEGER", 1, 0), ("expires_at_ms", "INTEGER", 1, 0),
                ("policy_sha256", "TEXT", 1, 0), ("state", "TEXT", 1, 0),
                ("consumed_at_ms", "INTEGER", 0, 0), ("row_hmac", "TEXT", 1, 0),
            ]
            actual = [(r["name"], r["type"].upper(), r["notnull"], r["pk"])
                      for r in db.execute("PRAGMA table_info(challenges)").fetchall()]
            if actual != expected:
                raise RegistryProtocolError("registry-schema-incompatible")
            db.execute("CREATE TRIGGER IF NOT EXISTS challenges_no_delete BEFORE DELETE ON challenges BEGIN SELECT RAISE(ABORT,'registry-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS challenges_no_update_unless_transition BEFORE UPDATE ON challenges WHEN NOT (OLD.state='PENDING' AND NEW.state='CONSUMED' AND OLD.nonce=NEW.nonce AND OLD.database_id=NEW.database_id AND OLD.issued_at_ms=NEW.issued_at_ms AND OLD.expires_at_ms=NEW.expires_at_ms AND OLD.policy_sha256=NEW.policy_sha256) BEGIN SELECT RAISE(ABORT,'registry-invalid-transition'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS clock_state_no_delete BEFORE DELETE ON clock_state BEGIN SELECT RAISE(ABORT,'registry-clock-state-append-only'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS clock_state_no_decrease BEFORE UPDATE ON clock_state WHEN OLD.singleton != NEW.singleton OR NEW.high_water_ms < OLD.high_water_ms OR NEW.prune_before_ms < OLD.prune_before_ms OR NEW.replay_window_ms != OLD.replay_window_ms BEGIN SELECT RAISE(ABORT,'registry-clock-must-not-decrease-or-reconfigure'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS request_nonces_no_update BEFORE UPDATE ON request_nonces BEGIN SELECT RAISE(ABORT,'registry-request-nonce-immutable'); END")
            db.execute("CREATE TRIGGER IF NOT EXISTS request_nonces_no_delete_recent BEFORE DELETE ON request_nonces WHEN OLD.timestamp_ms >= COALESCE((SELECT prune_before_ms FROM clock_state WHERE singleton=1),9223372036854775807) BEGIN SELECT RAISE(ABORT,'registry-request-nonce-still-live'); END")
            db.commit()

    @staticmethod
    def _row_body(row: Mapping[str, Any]) -> dict[str, Any]:
        return {name: row[name] for name in ("nonce", "database_id", "issued_at_ms", "expires_at_ms", "policy_sha256", "state", "consumed_at_ms")}

    def _row_tag(self, row: Mapping[str, Any]) -> str:
        return hmac.new(self.storage_key, b"lyc-registry-row-v3.5\n" + canonical(self._row_body(row)), hashlib.sha256).hexdigest()

    def _clock_tag(self, singleton: int, high_water_ms: int, prune_before_ms: int, replay_window_ms: int) -> str:
        body = {
            "singleton": singleton,
            "high_water_ms": high_water_ms,
            "prune_before_ms": prune_before_ms,
            "replay_window_ms": replay_window_ms,
        }
        return hmac.new(self.storage_key, DOMAIN_REGISTRY_CLOCK + canonical(body), hashlib.sha256).hexdigest()

    def _check_clock(self, db: sqlite3.Connection, now_ms: int) -> dict[str, int] | None:
        """Validate persisted monotonic time and the fixed request replay window."""
        if type(now_ms) is not int or now_ms < 0:
            raise RegistryClockError("registry-clock-invalid")
        row = db.execute("SELECT singleton,high_water_ms,prune_before_ms,replay_window_ms,row_hmac FROM clock_state WHERE singleton=1").fetchone()
        if row is None:
            return None
        if set(row.keys()) != {"singleton", "high_water_ms", "prune_before_ms", "replay_window_ms", "row_hmac"}:
            raise RegistryClockError("registry-clock-state-shape-invalid")
        for name in ("singleton", "high_water_ms", "prune_before_ms", "replay_window_ms"):
            if type(row[name]) is not int:
                raise RegistryClockError("registry-clock-state-invalid")
        if row["singleton"] != 1 or row["high_water_ms"] < 0 or row["replay_window_ms"] <= 0:
            raise RegistryClockError("registry-clock-state-invalid")
        if row["prune_before_ms"] != row["high_water_ms"] - row["replay_window_ms"]:
            raise RegistryClockError("registry-clock-prune-floor-invalid")
        expected = self._clock_tag(row["singleton"], row["high_water_ms"], row["prune_before_ms"], row["replay_window_ms"])
        if not isinstance(row["row_hmac"], str) or not HEX64.fullmatch(row["row_hmac"]) or not hmac.compare_digest(expected, row["row_hmac"]):
            raise RegistryClockError("registry-clock-state-integrity-invalid")
        if row["replay_window_ms"] != self.max_clock_skew_ms:
            raise RegistryClockError("registry-clock-window-config-changed")
        if now_ms < row["high_water_ms"]:
            raise RegistryClockError("registry-clock-rollback")
        return {
            "high_water_ms": row["high_water_ms"],
            "prune_before_ms": row["prune_before_ms"],
            "replay_window_ms": row["replay_window_ms"],
            "singleton": row["singleton"],
        }

    def _advance_clock(self, db: sqlite3.Connection, now_ms: int, previous: Mapping[str, int] | None) -> None:
        """Advance the authenticated wall-clock floor and safely expire request IDs."""
        prune_before_ms = now_ms - self.max_clock_skew_ms
        if previous is None:
            tag = self._clock_tag(1, now_ms, prune_before_ms, self.max_clock_skew_ms)
            db.execute(
                "INSERT INTO clock_state(singleton,high_water_ms,prune_before_ms,replay_window_ms,row_hmac) VALUES(1,?,?,?,?)",
                (now_ms, prune_before_ms, self.max_clock_skew_ms, tag),
            )
        elif now_ms > previous["high_water_ms"]:
            tag = self._clock_tag(1, now_ms, prune_before_ms, previous["replay_window_ms"])
            cur = db.execute(
                "UPDATE clock_state SET high_water_ms=?,prune_before_ms=?,row_hmac=? WHERE singleton=1 AND high_water_ms=? AND prune_before_ms=? AND row_hmac=?",
                (now_ms, prune_before_ms, tag, previous["high_water_ms"], previous["prune_before_ms"], self._clock_tag(1, previous["high_water_ms"], previous["prune_before_ms"], previous["replay_window_ms"])),
            )
            if cur.rowcount != 1:
                raise RegistryClockError("registry-clock-advance-race")
        # The database trigger forbids deleting request IDs still inside the current
        # replay window. The HMAC-bound prune floor and non-decreasing clock ensure
        # deleted IDs can no longer pass timestamp validation, absent whole-store rollback.
        db.execute("DELETE FROM request_nonces WHERE timestamp_ms < ?", (prune_before_ms,))

    def _validate_row(self, row: Mapping[str, Any]) -> None:
        if set(row.keys()) != {"nonce", "database_id", "issued_at_ms", "expires_at_ms", "policy_sha256", "state", "consumed_at_ms", "row_hmac"}:
            raise RegistryProtocolError("registry-row-shape-invalid")
        _validate_challenge({k: row[k] for k in ("nonce", "database_id", "issued_at_ms", "expires_at_ms", "policy_sha256")})
        if row["state"] not in {"PENDING", "CONSUMED"}:
            raise RegistryProtocolError("registry-row-state-invalid")
        if row["state"] == "PENDING" and row["consumed_at_ms"] is not None:
            raise RegistryProtocolError("registry-row-state-time-invalid")
        if row["state"] == "CONSUMED" and type(row["consumed_at_ms"]) is not int:
            raise RegistryProtocolError("registry-row-state-time-invalid")
        if not isinstance(row["row_hmac"], str) or not HEX64.fullmatch(row["row_hmac"]):
            raise RegistryProtocolError("registry-row-auth-invalid")
        if not hmac.compare_digest(self._row_tag(row), row["row_hmac"]):
            raise RegistryProtocolError("registry-row-integrity-invalid")

    def _sign(self, status: int, body: Mapping[str, Any], request_id: str) -> dict[str, Any]:
        unsigned = {"http_status": status, "body": dict(body), "server_key_id": self.server_key_id, "request_id": request_id}
        sig = self.server_private_key.sign(DOMAIN_REGISTRY_RESPONSE + canonical(unsigned))
        return {**unsigned, "signature_b64": b64(sig)}

    def _auth(self, method: str, path: str, raw_body: bytes, headers: Mapping[str, str], db: sqlite3.Connection, *, now_ms: int | None = None) -> tuple[str, str]:
        h = {str(k).lower(): v for k, v in headers.items()}
        kid, rid, stamp, supplied = (h.get("x-lyc-registry-key-id", ""), h.get("x-lyc-registry-request-id", ""),
                                    h.get("x-lyc-registry-timestamp-ms", ""), h.get("x-lyc-registry-signature", ""))
        key = self.client_keys.get(kid)
        if key is None or not VALID_ID.fullmatch(kid) or not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", rid) or not re.fullmatch(r"[0-9]{10,16}", stamp):
            raise RegistryProtocolError("client-auth-fields-invalid")
        ts = int(stamp)
        now = self.clock_ms() if now_ms is None else now_ms
        if type(now) is not int or abs(now-ts) > self.max_clock_skew_ms:
            raise RegistryProtocolError("client-auth-timestamp-invalid")
        body_hash = _sha256(raw_body)
        signed = {"method": method, "path": path, "timestamp_ms": ts, "request_id": rid, "body_sha256": body_hash}
        expected = hmac.new(key, DOMAIN_REGISTRY_REQUEST + canonical(signed), hashlib.sha256).hexdigest()
        if not isinstance(supplied, str) or not hmac.compare_digest(expected, supplied):
            raise RegistryProtocolError("client-auth-signature-invalid")
        exists = db.execute("SELECT 1 FROM request_nonces WHERE key_id=? AND request_id=?", (kid, rid)).fetchone()
        if exists:
            raise RegistryProtocolError("client-request-replay")
        db.execute("INSERT INTO request_nonces(key_id,request_id,timestamp_ms) VALUES(?,?,?)", (kid,rid,ts))
        return rid, kid

    def handle(self, method: str, path: str, raw_body: bytes, headers: Mapping[str, str]) -> tuple[int, dict[str, Any] | None, bool]:
        if not isinstance(raw_body, bytes) or len(raw_body) > MAX_REQUEST_BYTES:
            rid = headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")
            return 413, self._sign(413, {"error":"request-body-too-large"}, rid), False
        try:
            obj = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            if not isinstance(obj, dict):
                raise RegistryProtocolError("request-body-must-be-object")
        except (UnicodeDecodeError, json.JSONDecodeError):
            obj = None
        try:
            with closing(self._db()) as db:
                db.execute("BEGIN IMMEDIATE")
                # Sample time only after acquiring the write transaction. Otherwise
                # a slower request could sample earlier, wait behind a newer request,
                # and be misclassified as wall-clock rollback.
                now = self.clock_ms()
                if type(now) is not int or now < 0:
                    db.rollback()
                    return 503, self._sign(503, {"error":"registry-clock-invalid"}, headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")), False
                try:
                    previous_clock = self._check_clock(db, now)
                except RegistryClockError as exc:
                    db.rollback()
                    return 503, self._sign(503, {"error":str(exc)}, headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")), False
                try:
                    rid, _ = self._auth(method, path, raw_body, headers, db, now_ms=now)
                except RegistryProtocolError as exc:
                    db.rollback()
                    return 401, self._sign(401, {"error":str(exc)}, headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")), False
                try:
                    self._advance_clock(db, now, previous_clock)
                except RegistryClockError as exc:
                    db.rollback()
                    return 503, self._sign(503, {"error":str(exc)}, rid), False
                if self.drop_before_commit_count:
                    self.drop_before_commit_count -= 1
                    db.rollback()
                    return 0, None, True
                status, body = self._route(method, path, obj, db, now_ms=now)
                db.commit()
                signed = self._sign(status, body, rid)
                if self.drop_after_commit_count:
                    self.drop_after_commit_count -= 1
                    return 0, None, True
                return status, signed, False
        except (sqlite3.Error, RegistryProtocolError, ValueError, KeyError) as exc:
            return 503, self._sign(503, {"error":"registry-unavailable-or-invalid"}, headers.get("X-Lyc-Registry-Request-Id", "invalid-request-id")), False

    def _route(self, method: str, path: str, obj: Any, db: sqlite3.Connection, *, now_ms: int | None = None) -> tuple[int, dict[str, Any]]:
        if obj is None:
            return 400, {"error":"invalid-json"}
        if method == "POST" and path == "/v1/challenges":
            body = _validate_challenge(obj)
            now = self.clock_ms() if now_ms is None else now_ms
            if body["issued_at_ms"] > now + self.max_clock_skew_ms or body["expires_at_ms"] <= now:
                return 422, {"error":"challenge-time-invalid"}
            pending = {**body, "state":"PENDING", "consumed_at_ms":None}
            tag = self._row_tag(pending)
            try:
                db.execute("INSERT INTO challenges(nonce,database_id,issued_at_ms,expires_at_ms,policy_sha256,state,consumed_at_ms,row_hmac) VALUES(?,?,?,?,?,'PENDING',NULL,?)",
                           (body["nonce"], body["database_id"], body["issued_at_ms"], body["expires_at_ms"], body["policy_sha256"], tag))
            except sqlite3.IntegrityError:
                return 409, {"error":"challenge-nonce-already-registered"}
            return 201, {"status":"REGISTERED", "nonce":body["nonce"], "database_id":body["database_id"], "policy_sha256":body["policy_sha256"], "expires_at_ms":body["expires_at_ms"]}
        match = re.fullmatch(r"/v1/challenges/([A-Za-z0-9_-]{16,128})/consume", path)
        if method == "POST" and match:
            nonce = unquote(match.group(1))
            if set(obj) != {"database_id", "policy_sha256", "issued_at_ms", "expires_at_ms"}:
                return 400, {"error":"consume-fields-invalid"}
            row0 = db.execute("SELECT * FROM challenges WHERE nonce=?", (nonce,)).fetchone()
            if row0 is None:
                return 404, {"error":"challenge-not-registered"}
            row = dict(row0)
            self._validate_row(row)
            if (obj["database_id"] != row["database_id"] or obj["policy_sha256"] != row["policy_sha256"] or
                obj["issued_at_ms"] != row["issued_at_ms"] or obj["expires_at_ms"] != row["expires_at_ms"]):
                return 409, {"error":"challenge-binding-mismatch"}
            now = self.clock_ms() if now_ms is None else now_ms
            if type(now) is not int or now < 0:
                return 503, {"error":"registry-clock-invalid"}
            if now < row["issued_at_ms"]:
                return 409, {"error":"challenge-not-yet-valid"}
            if now >= row["expires_at_ms"]:
                return 409, {"error":"challenge-expired"}
            if row["state"] != "PENDING":
                return 409, {"error":"challenge-already-consumed"}
            updated = {**self._row_body(row), "state":"CONSUMED", "consumed_at_ms":now}
            tag = self._row_tag(updated)
            cur = db.execute("UPDATE challenges SET state='CONSUMED',consumed_at_ms=?,row_hmac=? WHERE nonce=? AND state='PENDING' AND row_hmac=?",
                             (now, tag, nonce, row["row_hmac"]))
            if cur.rowcount != 1:
                return 409, {"error":"challenge-consume-race-lost"}
            return 200, {"status":"CONSUMED", "nonce":nonce, "database_id":row["database_id"],
                         "policy_sha256":row["policy_sha256"], "consumed_at_ms":now}
        return 404, {"error":"route-not-found"}


class RegistryHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    def __init__(self, address, service: SpentChallengeRegistryService):
        self.service = service
        super().__init__(address, RegistryRequestHandler)


class RegistryRequestHandler(BaseHTTPRequestHandler):
    server: RegistryHTTPServer
    protocol_version = "HTTP/1.1"
    def log_message(self, *_):
        return
    def _dispatch(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_REQUEST_BYTES:
            status, envelope, drop = 413, self.server.service._sign(413,{"error":"request-body-too-large"},self.headers.get("X-Lyc-Registry-Request-Id","invalid-request-id")),False
        else:
            raw = self.rfile.read(length) if self.command == "POST" else b""
            status, envelope, drop = self.server.service.handle(self.command, self.path, raw, dict(self.headers.items()))
        if drop or envelope is None:
            self.close_connection = True
            try: self.connection.shutdown(2)
            except OSError: pass
            self.connection.close()
            return
        payload = canonical(envelope)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.close_connection = True
    do_GET = _dispatch
    do_POST = _dispatch


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SpentChallengeRegistryClient:
    """Authenticated HTTPS client. HTTP is permitted only for explicit loopback tests."""
    def __init__(self, base_url: str, *, client_key_id: str, client_key: bytes,
                 server_keys: Mapping[str, Ed25519PublicKey], server_key_id: str,
                 timeout_seconds: float = 2.0, allow_http_loopback: bool = False, clock_ms=None):
        parsed = urlparse(base_url)
        loopback = parsed.hostname in {"127.0.0.1", "::1", "localhost"}
        if parsed.scheme != "https" and not (allow_http_loopback and parsed.scheme == "http" and loopback):
            raise RegistryProtocolError("registry-url-must-use-https-unless-loopback-test")
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {"", "/"}:
            raise RegistryProtocolError("registry-url-components-invalid")
        if not VALID_ID.fullmatch(client_key_id) or not isinstance(client_key, bytes) or len(client_key) < MIN_KEY_BYTES:
            raise RegistryProtocolError("registry-client-key-invalid")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds,(int,float)) or timeout_seconds <= 0 or timeout_seconds > 30:
            raise RegistryProtocolError("registry-timeout-invalid")
        if not isinstance(server_keys, Mapping) or server_key_id not in server_keys or any(not VALID_ID.fullmatch(k) or not isinstance(v,Ed25519PublicKey) for k,v in server_keys.items()):
            raise RegistryProtocolError("registry-server-key-untrusted")
        self.base_url = base_url.rstrip("/")
        self.client_key_id, self.client_key = client_key_id, bytes(client_key)
        self.server_keys, self.server_key_id = dict(server_keys), server_key_id
        self.timeout_seconds = float(timeout_seconds)
        self.clock_ms = clock_ms or _now_ms
        self.opener = build_opener(_NoRedirect())

    def _request(self, method: str, path: str, body: Mapping[str, Any]) -> dict[str, Any]:
        raw = canonical(dict(body))
        rid = uuid.uuid4().hex
        stamp = str(self.clock_ms())
        signed = {"method":method,"path":path,"timestamp_ms":int(stamp),"request_id":rid,"body_sha256":_sha256(raw)}
        sig = hmac.new(self.client_key, DOMAIN_REGISTRY_REQUEST + canonical(signed), hashlib.sha256).hexdigest()
        req = Request(self.base_url + path, data=raw if method == "POST" else None, method=method,
                      headers={"Content-Type":"application/json","Accept":"application/json",
                               "X-Lyc-Registry-Key-Id":self.client_key_id,"X-Lyc-Registry-Request-Id":rid,
                               "X-Lyc-Registry-Timestamp-Ms":stamp,"X-Lyc-Registry-Signature":sig})
        try:
            with self.opener.open(req, timeout=self.timeout_seconds) as resp:
                status = resp.status
                payload = resp.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            status = exc.code
            try: payload = exc.read(MAX_RESPONSE_BYTES + 1)
            finally: exc.close()
        except (URLError, TimeoutError, OSError) as exc:
            raise RegistryTransportError("registry-transport-failed; outcome-may-be-ambiguous") from None
        if len(payload) > MAX_RESPONSE_BYTES:
            raise RegistryProtocolError("registry-response-too-large")
        try: envelope = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RegistryProtocolError("registry-response-json-invalid") from None
        fields = {"http_status","body","server_key_id","request_id","signature_b64"}
        if not isinstance(envelope,dict) or set(envelope) != fields or envelope["http_status"] != status or envelope["request_id"] != rid or envelope["server_key_id"] != self.server_key_id or not isinstance(envelope["body"],dict) or not isinstance(envelope["signature_b64"],str):
            raise RegistryProtocolError("registry-response-envelope-invalid")
        unsigned = {k:envelope[k] for k in ("http_status","body","server_key_id","request_id")}
        try:
            self.server_keys[self.server_key_id].verify(unb64(envelope["signature_b64"]), DOMAIN_REGISTRY_RESPONSE + canonical(unsigned))
        except (InvalidSignature, ValueError, TypeError):
            raise RegistryProtocolError("registry-response-signature-invalid") from None
        if status < 200 or status >= 300:
            code = envelope["body"].get("error", "registry-rejected")
            raise RegistryRejected(str(code))
        return dict(envelope["body"])

    @staticmethod
    def _challenge_body(challenge) -> dict[str, Any]:
        body = {"nonce":challenge.nonce,"database_id":challenge.database_id,
                "issued_at_ms":challenge.issued_at_ms,"expires_at_ms":challenge.expires_at_ms,
                "policy_sha256":challenge.policy_sha256}
        return _validate_challenge(body)

    def register(self, challenge) -> Mapping[str, Any]:
        result = self._request("POST", "/v1/challenges", self._challenge_body(challenge))
        if result.get("status") != "REGISTERED" or result.get("nonce") != challenge.nonce or result.get("database_id") != challenge.database_id or result.get("policy_sha256") != challenge.policy_sha256 or result.get("expires_at_ms") != challenge.expires_at_ms:
            raise RegistryProtocolError("registry-registration-response-mismatch")
        return result

    def consume(self, challenge) -> Mapping[str, Any]:
        body = self._challenge_body(challenge)
        path = "/v1/challenges/" + quote(challenge.nonce,safe="") + "/consume"
        result = self._request("POST", path, {k:body[k] for k in ("database_id","policy_sha256","issued_at_ms","expires_at_ms")})
        consumed_at = result.get("consumed_at_ms")
        if (result.get("status") != "CONSUMED" or result.get("nonce") != challenge.nonce
                or result.get("database_id") != challenge.database_id
                or result.get("policy_sha256") != challenge.policy_sha256
                or type(consumed_at) is not int
                or not challenge.issued_at_ms <= consumed_at < challenge.expires_at_ms):
            raise RegistryProtocolError("registry-consume-response-mismatch")
        return result


def serve_in_thread(service: SpentChallengeRegistryService, host: str = "127.0.0.1", port: int = 0):
    """Test helper. Production needs TLS termination, service isolation and operations."""
    import threading
    server = RegistryHTTPServer((host, port), service)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
