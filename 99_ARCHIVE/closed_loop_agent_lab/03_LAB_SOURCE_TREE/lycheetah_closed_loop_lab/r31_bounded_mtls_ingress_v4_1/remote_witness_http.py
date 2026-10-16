"""Process-separated HTTP transport for the v3.7 checkpoint witness.

Reference prototype only. Servers default to numeric loopback IPs and require mutual
TLS (mTLS) plus per-client HMAC. A non-loopback bind requires explicit opt-in and a
specific non-wildcard IPv4 address. Production still needs separately administered
hosts, independent keys/backups, monitoring, and an operational trust design.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import hmac
import ipaddress
import json
import re
import secrets
import socket
import ssl
import sqlite3
import sys
import time
import urllib.parse
import uuid
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from remote_anchor_http import canonical, b64, unb64
from registry_checkpoint_quorum import RegistryCheckpointError, RegistryCheckpointWitness

DOMAIN_RPC = b"lyc-registry-witness-mtls-rpc-v3.9\n"
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


def validate_bind_host(host: str, allow_non_loopback: bool) -> str:
    """Validate a literal IPv4 bind address; reject DNS, wildcard, and implicit exposure."""
    if type(allow_non_loopback) is not bool:
        raise ValueError("witness-allow-non-loopback-must-be-boolean")
    try:
        address = ipaddress.ip_address(host)
    except (ValueError, TypeError) as exc:
        raise ValueError("witness-bind-host-must-be-numeric-ip") from exc
    if address.version != 4:
        raise ValueError("witness-bind-host-must-be-ipv4")
    if address.is_unspecified or address.is_multicast:
        raise ValueError("witness-bind-host-wildcard-or-multicast-forbidden")
    if not address.is_loopback and not allow_non_loopback:
        raise ValueError("witness-non-loopback-bind-requires-explicit-opt-in")
    return str(address)


class _WitnessServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, *, config: Mapping[str, Any], drop_after_first_attest: bool = False):
        required = {"witness_id", "database_path", "storage_key_b64", "private_key_b64",
                    "issuer_key_id", "issuer_public_key_b64", "registry_id", "api_key_id", "api_key_b64",
                    "bind_host", "allow_non_loopback", "tls_server_cert_path", "tls_server_key_path",
                    "tls_client_ca_path", "tls_client_identity_uri"}
        if not isinstance(config, Mapping) or set(config) != required:
            raise ValueError("witness-config-shape-invalid")
        self.config = dict(config)
        host, _ = address
        checked_host = validate_bind_host(host, self.config["allow_non_loopback"])
        if checked_host != self.config["bind_host"]:
            raise ValueError("witness-bind-host-config-mismatch")
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
        self.tls_client_identity_uri = self.config["tls_client_identity_uri"]
        if not isinstance(self.tls_client_identity_uri, str) or not self.tls_client_identity_uri.startswith("spiffe://"):
            raise ValueError("witness-tls-client-identity-invalid")
        self._initialize_replay_db()
        super().__init__(address, _WitnessHandler)
        # TLS is mandatory for this transport revision. Client cert chain validation
        # is completed during the handshake; the handler additionally pins the
        # expected SPIFFE-style URI SAN for the coordinator identity.
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.options |= getattr(ssl, "OP_NO_COMPRESSION", 0)
        ctx.load_cert_chain(self.config["tls_server_cert_path"], self.config["tls_server_key_path"])
        ctx.load_verify_locations(cafile=self.config["tls_client_ca_path"])
        ctx.verify_mode = ssl.CERT_REQUIRED
        # Do not wrap the listening socket itself: SSLSocket.accept() can run a
        # TLS handshake on the accept loop and let one slow client stall the
        # entire service. We wrap each accepted socket without handshaking, then
        # perform the bounded handshake in that request's worker thread.
        self.tls_context = ctx
        self.tls_handshake_timeout_seconds = 3.0
        self.request_timeout_seconds = 10.0

    def handle_error(self, request, client_address):
        # Invalid TLS handshakes and abruptly closed clients are expected on an
        # exposed transport boundary. Do not emit Python tracebacks (which can
        # disclose paths/configuration and can flood a supervisor's stderr pipe).
        # Preserve a minimal event for unexpected failures without exception text.
        exc_type, exc, _tb = sys.exc_info()
        expected = (ssl.SSLError, socket.timeout, ConnectionResetError,
                    ConnectionAbortedError, BrokenPipeError, EOFError)
        if isinstance(exc, expected):
            return
        try:
            name = exc_type.__name__ if exc_type is not None else "UnknownError"
            sys.stderr.write(json.dumps({"event": "witness-handler-error", "type": name}) + "\n")
            sys.stderr.flush()
        except Exception:
            pass

    def get_request(self):
        raw, address = super().get_request()
        try:
            wrapped = self.tls_context.wrap_socket(raw, server_side=True, do_handshake_on_connect=False)
            wrapped.settimeout(self.tls_handshake_timeout_seconds)
            return wrapped, address
        except Exception:
            raw.close()
            raise

    def handle_error(self, request, client_address):
        # Handshake and malformed-connection failures are expected adversarial
        # inputs; never emit stack traces (or key/config details) to stderr.
        return

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
        # TLS client cert chain is verified by OpenSSL; bind the RPC authority to
        # the exact coordinator identity, not merely to any certificate issued by
        # the local test CA.
        try:
            peer = handler.connection.getpeercert()
            san = peer.get("subjectAltName", ()) if isinstance(peer, dict) else ()
            uris = {value for kind, value in san if kind == "URI"}
            if self.tls_client_identity_uri not in uris:
                return False, "witness-rpc-client-identity-invalid"
        except Exception:
            return False, "witness-rpc-client-certificate-missing"
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

    def setup(self):
        # Run the handshake after ThreadingHTTPServer has created the worker
        # thread, with a short timeout so slow clients cannot monopolize accept.
        try:
            self.request.settimeout(self.server.tls_handshake_timeout_seconds)
            self.request.do_handshake()
            self.request.settimeout(self.server.request_timeout_seconds)
        except Exception:
            self.request.close()
            raise
        super().setup()

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
    host = config.get("bind_host")
    server = _WitnessServer((host, port), config=config, drop_after_first_attest=drop_after_first_attest)
    actual_host, actual_port = server.server_address[:2]
    print(json.dumps({"ready": True, "witness_id": server.witness_id, "host": actual_host,
                      "port": actual_port, "pid": __import__("os").getpid()}), flush=True)
    try:
        server.serve_forever(poll_interval=0.05)
    finally:
        server.server_close()


class RemoteWitnessClient:
    """Duck-typed mTLS client for RegistryQuorumAnchor's witness interface."""
    def __init__(self, witness_id: str, base_url: str, api_key_id: str, api_secret: bytes,
                 *, tls_ca_path: str, tls_client_cert_path: str, tls_client_key_path: str,
                 timeout_seconds: float = 1.0, clock_ms=None):
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("remote-witness-client-requires-https")
        try:
            host_ip = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            host_ip = None
        if host_ip is not None and (host_ip.is_unspecified or host_ip.is_multicast):
            raise ValueError("remote-witness-client-host-invalid")
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
            raise ValueError("remote-witness-base-url-invalid")
        if not isinstance(witness_id, str) or not witness_id or not isinstance(api_key_id, str) or not api_key_id:
            raise ValueError("remote-witness-identity-invalid")
        if not isinstance(api_secret, bytes) or len(api_secret) < 32:
            raise ValueError("remote-witness-api-secret-invalid")
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("remote-witness-timeout-invalid")
        if not all(isinstance(v, str) and v for v in (tls_ca_path, tls_client_cert_path, tls_client_key_path)):
            raise ValueError("remote-witness-tls-material-required")
        # Accessing parsed.port forces malformed ports to fail at construction.
        try:
            port = parsed.port
        except ValueError as exc:
            raise ValueError("remote-witness-base-url-port-invalid") from exc
        if port is not None and not (1 <= port <= 65535):
            raise ValueError("remote-witness-base-url-port-invalid")
        self.witness_id, self.base_url = witness_id, f"https://{parsed.netloc}"
        self.api_key_id, self.api_secret = api_key_id, bytes(api_secret)
        self.timeout_seconds = float(timeout_seconds)
        self.clock_ms = clock_ms or (lambda: time.time_ns() // 1_000_000)
        tls = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=tls_ca_path)
        tls.minimum_version = ssl.TLSVersion.TLSv1_2
        tls.options |= getattr(ssl, "OP_NO_COMPRESSION", 0)
        tls.check_hostname = True
        tls.verify_mode = ssl.CERT_REQUIRED
        tls.load_cert_chain(tls_client_cert_path, tls_client_key_path)
        self._tls_context = tls
        # Requests use an explicit HTTPSConnection with Connection: close; this
        # keeps redirect behavior out of the client path and makes socket timeout
        # application visible at the transport boundary.

    def _post(self, path: str, body: Mapping[str, Any], *, request_id: str | None = None) -> Mapping[str, Any]:
        if path not in {"/v1/head", "/v1/attest", "/v1/checkpoint"}:
            raise ValueError("remote-witness-route-invalid")
        raw = canonical(dict(body)); stamp = int(self.clock_ms()); rid = request_id or uuid.uuid4().hex
        sig = _rpc_signature(self.api_secret, "POST", path, stamp, rid, raw)
        headers = {
            "Content-Type": "application/json", "Accept": "application/json", "Connection": "close",
            "X-Lyc-Witness-Key-Id": self.api_key_id, "X-Lyc-Witness-Request-Id": rid,
            "X-Lyc-Witness-Timestamp-Ms": str(stamp), "X-Lyc-Witness-Signature": sig,
        }
        parsed = urllib.parse.urlsplit(self.base_url)
        try:
            port = parsed.port or 443
        except ValueError as exc:
            raise ValueError("remote-witness-base-url-port-invalid") from exc
        conn = http.client.HTTPSConnection(parsed.hostname, port, timeout=self.timeout_seconds,
                                           context=self._tls_context)
        try:
            conn.connect()
            # Apply the timeout to the established TLS socket as well as to the
            # connect operation. Explicit Connection: close prevents ambiguous
            # keep-alive state after dropped/partial responses.
            if conn.sock is not None:
                conn.sock.settimeout(self.timeout_seconds)
            conn.request("POST", path, body=raw, headers=headers)
            response = conn.getresponse()
            raw_resp = response.read(MAX_BODY + 1)
            if len(raw_resp) > MAX_BODY:
                raise WitnessHTTPError(502, "witness-response-too-large")
            try:
                decoded = json.loads(raw_resp)
            except (json.JSONDecodeError, UnicodeDecodeError):
                decoded = None
            if response.status != 200:
                code = decoded.get("error", "witness-http-error") if isinstance(decoded, dict) else "witness-http-error"
                raise WitnessHTTPError(response.status, str(code))
            if not isinstance(decoded, dict) or set(decoded) != {"result"} or not isinstance(decoded["result"], dict):
                raise WitnessHTTPError(502, "witness-response-shape-invalid")
            return decoded["result"]
        except WitnessHTTPError:
            raise
        except (http.client.HTTPException, ssl.SSLError, TimeoutError, ConnectionError, OSError) as exc:
            raise WitnessHTTPError(503, "witness-transport-unavailable") from exc
        finally:
            conn.close()

    def head_report(self, challenge_nonce: str) -> Mapping[str, Any]:
        return self._post("/v1/head", {"challenge_nonce": challenge_nonce})

    def attest(self, checkpoint: Any) -> Mapping[str, Any]:
        body = checkpoint.to_dict() if hasattr(checkpoint, "to_dict") else dict(checkpoint)
        return self._post("/v1/attest", {"checkpoint": body})

    def get_checkpoint(self, sequence: int) -> dict[str, Any] | None:
        result = self._post("/v1/checkpoint", {"sequence": sequence})
        value = result.get("checkpoint")
        return value if isinstance(value, dict) else None


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--drop-after-first-attest", action="store_true")
    args = parser.parse_args()
    serve_from_config(args.config, args.port, args.drop_after_first_attest)


if __name__ == "__main__":
    _main()
