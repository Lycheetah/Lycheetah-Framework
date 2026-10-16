"""Process-separated HTTP transport for the v3.7 checkpoint witness.

Reference prototype only. Servers intentionally bind to numeric loopback IPs and use
HTTP + per-client HMAC so the transport can be tested without a TLS deployment.
For non-loopback production deployments use authenticated TLS/mTLS, external key
management, independent administrators/backups, and an operational trust design.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import ipaddress
import json
import re
import secrets
import socket
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from remote_anchor_http import canonical, b64, unb64
from registry_checkpoint_quorum import RegistryCheckpointError, RegistryCheckpointWitness

DOMAIN_RPC = b"lyc-registry-witness-http-rpc-v3.8\n"
REQ_ID_RE = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
HEX64_RE = re.compile(r"^[a-f0-9]{64}$")
MAX_BODY = 1_048_576
DEFAULT_SKEW_MS = 30_000


class WitnessHTTPError(RuntimeError):
    def __init__(self, status: int, code: str):
        self.status = int(status)
        self.code = str(code)
        super().__init__(f"witness-http-{self.status}:{self.code}")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _rpc_signature(secret: bytes, method: str, path: str, stamp: int, rid: str, raw: bytes) -> str:
    signed = {"method": method, "path": path, "timestamp_ms": stamp,
              "request_id": rid, "body_sha256": _sha(raw)}
    return hmac.new(secret, DOMAIN_RPC + canonical(signed), hashlib.sha256).hexdigest()


def _numeric_loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class _WitnessServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, *, config: Mapping[str, Any], drop_after_first_attest: bool = False):
        host, _ = address
        if not _numeric_loopback(host):
            raise ValueError("witness-http-server-loopback-only")
        required = {"witness_id", "database_path", "storage_key_b64", "private_key_b64",
                    "issuer_key_id", "issuer_public_key_b64", "registry_id", "api_key_id", "api_key_b64"}
        if not isinstance(config, Mapping) or set(config) != required:
            raise ValueError("witness-config-shape-invalid")
        self.config = dict(config)
        self.witness_id = self.config["witness_id"]
        self.api_key_id = self.config["api_key_id"]
        self.api_secret = unb64(self.config["api_key_b64"])
        if len(self.api_secret) < 32:
            raise ValueError("witness-api-key-too-short")
        private = Ed25519PrivateKey.from_private_bytes(unb64(self.config["private_key_b64"]))
        issuer_public = Ed25519PublicKey.from_public_bytes(unb64(self.config["issuer_public_key_b64"]))
        self.witness = RegistryCheckpointWitness(
            self.witness_id, private, self.config["database_path"],
            unb64(self.config["storage_key_b64"]),
            {self.config["issuer_key_id"]: issuer_public}, self.config["registry_id"])
        self.replay_path = str(self.config["database_path"]) + ".rpc-replay.sqlite"
        self.max_skew_ms = DEFAULT_SKEW_MS
        self.drop_after_first_attest = bool(drop_after_first_attest)
        self._initialize_replay_db()
        super().__init__(address, _WitnessHandler)

    def _initialize_replay_db(self):
        with closing(sqlite3.connect(self.replay_path, timeout=10)) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("CREATE TABLE IF NOT EXISTS api_replay (key_id TEXT NOT NULL, request_id TEXT NOT NULL, timestamp_ms INTEGER NOT NULL, PRIMARY KEY(key_id, request_id))")
            cols = [(r[1], r[2].upper(), int(r[5])) for r in db.execute("PRAGMA table_info(api_replay)")]
            if cols != [("key_id", "TEXT", 1), ("request_id", "TEXT", 2), ("timestamp_ms", "INTEGER", 0)]:
                raise ValueError("witness-api-replay-schema-incompatible")
            db.commit()

    def _authorize_request(self, handler: BaseHTTPRequestHandler, path: str, raw: bytes) -> tuple[bool, str]:
        headers = handler.headers
        kid = headers.get("X-Lyc-Witness-Key-Id", "")
        rid = headers.get("X-Lyc-Witness-Request-Id", "")
        ts_raw = headers.get("X-Lyc-Witness-Timestamp-Ms", "")
        sig = headers.get("X-Lyc-Witness-Signature", "")
        if kid != self.api_key_id or not REQ_ID_RE.fullmatch(rid) or not ts_raw.isdigit() or not HEX64_RE.fullmatch(sig):
            return False, "witness-rpc-auth-fields-invalid"
        stamp = int(ts_raw)
        now = time.time_ns() // 1_000_000
        if abs(now - stamp) > self.max_skew_ms:
            return False, "witness-rpc-timestamp-stale"
        expected = _rpc_signature(self.api_secret, handler.command, path, stamp, rid, raw)
        if not hmac.compare_digest(expected, sig):
            return False, "witness-rpc-signature-invalid"
        # Persist anti-replay consumption before invoking the witness. An ambiguous
        # client response must be retried with a fresh transport request ID.
        try:
            with closing(sqlite3.connect(self.replay_path, timeout=10, isolation_level=None)) as db:
                db.execute("PRAGMA busy_timeout=10000")
                db.execute("BEGIN IMMEDIATE")
                db.execute("DELETE FROM api_replay WHERE timestamp_ms < ?", (now - 4 * self.max_skew_ms,))
                db.execute("INSERT INTO api_replay(key_id,request_id,timestamp_ms) VALUES(?,?,?)", (kid, rid, stamp))
                db.commit()
        except sqlite3.IntegrityError:
            return False, "witness-rpc-replay-detected"
        except sqlite3.Error:
            return False, "witness-rpc-replay-ledger-unavailable"
        return True, "ok"


class _WitnessHandler(BaseHTTPRequestHandler):
    server: _WitnessServer
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        return

    def _send(self, status: int, body: Mapping[str, Any]):
        raw = canonical(dict(body))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        target = urllib.parse.urlsplit(self.path)
        # Query strings are intentionally unsupported. Reject rather than signing
        # only the path component while silently ignoring extra request-target data.
        if target.query or target.fragment or target.path != self.path:
            self._send(400, {"error": "witness-request-target-noncanonical"}); return
        path = target.path
        if path not in {"/v1/head", "/v1/attest", "/v1/checkpoint"}:
            self._send(404, {"error": "witness-route-not-found"}); return
        if self.headers.get("Transfer-Encoding") is not None:
            self._send(400, {"error": "witness-transfer-encoding-unsupported"}); return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self._send(415, {"error": "witness-content-type-invalid"}); return
        n = self.headers.get("Content-Length", "")
        if not n.isdigit() or int(n) < 0 or int(n) > MAX_BODY:
            self._send(413, {"error": "witness-body-size-invalid"}); return
        raw = self.rfile.read(int(n))
        if len(raw) != int(n):
            self._send(400, {"error": "witness-body-truncated"}); return
        ok, why = self.server._authorize_request(self, path, raw)
        if not ok:
            status = 409 if why == "witness-rpc-replay-detected" else 401
            self._send(status, {"error": why}); return
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("witness-request-body-not-object")
            if path == "/v1/head":
                if set(data) != {"challenge_nonce"}:
                    raise ValueError("witness-head-request-invalid")
                result = self.server.witness.head_report(data["challenge_nonce"])
            elif path == "/v1/attest":
                if set(data) != {"checkpoint"}:
                    raise ValueError("witness-attest-request-invalid")
                result = self.server.witness.attest(data["checkpoint"])
            else:
                if set(data) != {"sequence"} or type(data["sequence"]) is not int or data["sequence"] < 1:
                    raise ValueError("witness-checkpoint-request-invalid")
                result = {"checkpoint": self.server.witness.get_checkpoint(data["sequence"])}
        except (ValueError, TypeError, RegistryCheckpointError, json.JSONDecodeError) as exc:
            # Return stable error classes, not exception details or key material.
            code = str(exc) if isinstance(exc, ValueError) else "witness-request-rejected"
            code = re.sub(r"[^a-zA-Z0-9._:-]", "-", code)[:96] or "witness-request-rejected"
            self._send(400, {"error": code}); return
        except Exception:
            self._send(500, {"error": "witness-internal-error"}); return
        if path == "/v1/attest" and self.server.drop_after_first_attest:
            self.server.drop_after_first_attest = False
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.connection.close()
            except OSError:
                pass
            return
        self._send(200, {"result": result})


def serve_from_config(config_path: str, port: int, drop_after_first_attest: bool = False):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    server = _WitnessServer(("127.0.0.1", port), config=config, drop_after_first_attest=drop_after_first_attest)
    actual_host, actual_port = server.server_address[:2]
    print(json.dumps({"ready": True, "witness_id": server.witness_id, "host": actual_host,
                      "port": actual_port, "pid": __import__("os").getpid()}), flush=True)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()


class RemoteWitnessClient:
    """Duck-typed client for RegistryQuorumAnchor's witness interface."""
    def __init__(self, witness_id: str, base_url: str, api_key_id: str, api_secret: bytes,
                 *, timeout_seconds: float = 1.0, clock_ms=None):
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme != "http" or not parsed.hostname or not _numeric_loopback(parsed.hostname):
            raise ValueError("remote-witness-client-requires-loopback-http")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("remote-witness-base-url-invalid")
        if not isinstance(witness_id, str) or not witness_id or not isinstance(api_key_id, str) or not api_key_id:
            raise ValueError("remote-witness-identity-invalid")
        if not isinstance(api_secret, bytes) or len(api_secret) < 32:
            raise ValueError("remote-witness-api-secret-invalid")
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("remote-witness-timeout-invalid")
        self.witness_id, self.base_url = witness_id, f"http://{parsed.netloc}"
        self.api_key_id, self.api_secret = api_key_id, bytes(api_secret)
        self.timeout_seconds = float(timeout_seconds)
        self.clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)
        # Disallow redirects; otherwise signed witness requests could be sent to
        # an unintended server after an HTTP redirect.
        self._opener = urllib.request.build_opener(_NoRedirect())

    def _post(self, path: str, body: Mapping[str, Any], *, request_id: str | None = None) -> Mapping[str, Any]:
        if path not in {"/v1/head", "/v1/attest", "/v1/checkpoint"}:
            raise ValueError("remote-witness-route-invalid")
        raw = canonical(dict(body)); stamp = int(self.clock_ms()); rid = request_id or uuid.uuid4().hex
        sig = _rpc_signature(self.api_secret, "POST", path, stamp, rid, raw)
        req = urllib.request.Request(self.base_url + path, data=raw, method="POST", headers={
            "Content-Type": "application/json", "Accept": "application/json",
            "X-Lyc-Witness-Key-Id": self.api_key_id, "X-Lyc-Witness-Request-Id": rid,
            "X-Lyc-Witness-Timestamp-Ms": str(stamp), "X-Lyc-Witness-Signature": sig,
        })
        try:
            response = self._opener.open(req, timeout=self.timeout_seconds)
            with response:
                raw_resp = response.read(MAX_BODY + 1)
                if len(raw_resp) > MAX_BODY:
                    raise WitnessHTTPError(502, "witness-response-too-large")
                if response.status != 200:
                    raise WitnessHTTPError(response.status, "witness-http-status-unexpected")
        except urllib.error.HTTPError as exc:
            try:
                payload = json.loads(exc.read(MAX_BODY + 1))
                code = payload.get("error", "witness-http-error") if isinstance(payload, dict) else "witness-http-error"
            except Exception:
                code = "witness-http-error"
            raise WitnessHTTPError(exc.code, str(code)) from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            raise WitnessHTTPError(503, "witness-transport-unavailable") from exc
        try:
            decoded = json.loads(raw_resp)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise WitnessHTTPError(502, "witness-response-invalid-json") from exc
        if not isinstance(decoded, dict) or set(decoded) != {"result"} or not isinstance(decoded["result"], dict):
            raise WitnessHTTPError(502, "witness-response-shape-invalid")
        return decoded["result"]

    def head_report(self, challenge_nonce: str) -> Mapping[str, Any]:
        return self._post("/v1/head", {"challenge_nonce": challenge_nonce})

    def attest(self, checkpoint: Any) -> Mapping[str, Any]:
        body = checkpoint.to_dict() if hasattr(checkpoint, "to_dict") else dict(checkpoint)
        return self._post("/v1/attest", {"checkpoint": body})

    def get_checkpoint(self, sequence: int) -> dict[str, Any] | None:
        result = self._post("/v1/checkpoint", {"sequence": sequence})
        value = result.get("checkpoint")
        return value if isinstance(value, dict) else None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--drop-after-first-attest", action="store_true")
    args = parser.parse_args()
    serve_from_config(args.config, args.port, args.drop_after_first_attest)


if __name__ == "__main__":
    _main()
