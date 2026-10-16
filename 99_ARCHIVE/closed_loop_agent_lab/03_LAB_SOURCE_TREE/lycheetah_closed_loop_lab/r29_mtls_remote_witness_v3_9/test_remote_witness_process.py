from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import socket
import ssl
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
import ipaddress
import threading
from queue import Queue, Empty
from collections import deque
import unittest
import uuid
from contextlib import closing
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

from remote_anchor_http import canonical
from spent_nonce_registry import DOMAIN_REGISTRY_REQUEST, SpentChallengeRegistryService
from registry_checkpoint_quorum import (
    RegistryCheckpointError, RegistryQuorumAnchor, RegistryQuorumUnavailable, verify_head_quorum,
)
from remote_witness_http import RemoteWitnessClient, WitnessHTTPError, validate_bind_host

ROOT = Path(__file__).resolve().parent
CLIENT_ID = "remote-process-test-client"
CLIENT_KEY = b"remote-process-client-secret-material-over-32-bytes"
REGISTRY_STORAGE_KEY = b"remote-process-registry-storage-key-material-32bytes"
ANCHOR_STORAGE_KEY = b"remote-process-anchor-storage-key-material-32bytes"
REGISTRY_ID = "test.spent.registry"
ISSUER_ID = "test.registry.issuer"


def raw_private(key):
    return key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())


def raw_public(key):
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def enc(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")



COORDINATOR_URI = "spiffe://lycheetah.local/coordinator"

def _write_key(path: Path, key):
    path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    path.chmod(0o600)

def _make_test_ca(root: Path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Lycheetah Test Transport CA")])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=2)).not_valid_after(now + timedelta(days=3))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()), critical=False)
        .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
            key_encipherment=True, data_encipherment=False, key_agreement=False,
            key_cert_sign=True, crl_sign=True, encipher_only=None, decipher_only=None), critical=True)
        .sign(key, __import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256()))
    cert_path, key_path = root / "test-ca.pem", root / "test-ca-key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    _write_key(key_path, key)
    return key, cert, cert_path, key_path

def _issue_leaf(root: Path, ca_key, ca_cert, *, name: str, san, server: bool):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    now = datetime.now(timezone.utc)
    eku = ExtendedKeyUsageOID.SERVER_AUTH if server else ExtendedKeyUsageOID.CLIENT_AUTH
    builder = (x509.CertificateBuilder().subject_name(subject).issuer_name(ca_cert.subject)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=2)).not_valid_after(now + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([eku]), critical=True)
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False))
    cert = builder.sign(ca_key, __import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256())
    cert_path, key_path = root / f"{name.replace('/', '_')}.pem", root / f"{name.replace('/', '_')}-key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    _write_key(key_path, key)
    return cert, cert_path, key_path

class RemoteWitnessProcessTests(unittest.TestCase):
    """Share one four-process witness fleet; mutations are append-only across tests."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="lyc-r28-")
        cls.root = Path(cls.tmp.name)
        cls.processes: dict[int, subprocess.Popen] = {}
        cls.process_stderr_tails = {}
        cls.process_stderr_threads = {}
        cls.ports: dict[int, int] = {}
        cls.addClassCleanup(cls._cleanup_all_processes)
        cls.configs: dict[int, Path] = {}
        cls.api_keys: dict[int, bytes] = {}
        cls.witness_ids = [f"remote-witness-{i}" for i in range(1, 5)]
        cls.bind_hosts = [f"127.0.0.{i}" for i in range(1, 5)]
        ca_key, ca_cert, cls.tls_ca_path, cls.tls_ca_key_path = _make_test_ca(cls.root)
        cls.client_identity_uri = COORDINATOR_URI
        _, cls.tls_client_cert_path, cls.tls_client_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="lycheetah-coordinator",
            san=[x509.UniformResourceIdentifier(COORDINATOR_URI)], server=False)
        _, cls.tls_wrong_identity_cert_path, cls.tls_wrong_identity_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="other-coordinator",
            san=[x509.UniformResourceIdentifier("spiffe://other.local/coordinator")], server=False)
        cls.server_cert_paths = {}
        cls.server_key_paths = {}
        for i, host in enumerate(cls.bind_hosts, 1):
            _, cert_path, key_path = _issue_leaf(
                cls.root, ca_key, ca_cert, name=f"witness-server-{i}",
                san=[x509.IPAddress(ipaddress.ip_address(host))], server=True)
            cls.server_cert_paths[i] = cert_path
            cls.server_key_paths[i] = key_path
        cls.client_tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(cls.tls_ca_path))
        cls.client_tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
        cls.client_tls_context.load_cert_chain(str(cls.tls_client_cert_path), str(cls.tls_client_key_path))
        cls.issuer_private = Ed25519PrivateKey.generate()
        cls.issuer_keys = {ISSUER_ID: cls.issuer_private.public_key()}
        cls.witness_private = {wid: Ed25519PrivateKey.generate() for wid in cls.witness_ids}
        cls.witness_keys = {wid: key.public_key() for wid, key in cls.witness_private.items()}
        cls.clients = []
        for i, wid in enumerate(cls.witness_ids, 1):
            api = secrets.token_bytes(32)
            cls.api_keys[i] = api
            cfg = {
                "witness_id": wid,
                "database_path": str(cls.root / f"{wid}.sqlite"),
                "storage_key_b64": enc(secrets.token_bytes(32)),
                "private_key_b64": enc(raw_private(cls.witness_private[wid])),
                "issuer_key_id": ISSUER_ID,
                "issuer_public_key_b64": enc(raw_public(cls.issuer_private.public_key())),
                "registry_id": REGISTRY_ID,
                "api_key_id": f"anchor-client-{i}",
                "api_key_b64": enc(api),
                "bind_host": cls.bind_hosts[i - 1],
                "allow_non_loopback": False,
                "tls_server_cert_path": str(cls.server_cert_paths[i]),
                "tls_server_key_path": str(cls.server_key_paths[i]),
                "tls_client_ca_path": str(cls.tls_ca_path),
                "tls_client_identity_uri": cls.client_identity_uri,
            }
            cfg_path = cls.root / f"{wid}.config.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            cls.configs[i] = cfg_path
            cls.spawn(i)
            cls.clients.append(RemoteWitnessClient(wid, f"https://{cls.bind_hosts[i - 1]}:{cls.ports[i]}",
                cfg["api_key_id"], api, tls_ca_path=str(cls.tls_ca_path),
                tls_client_cert_path=str(cls.tls_client_cert_path),
                tls_client_key_path=str(cls.tls_client_key_path), timeout_seconds=1.5))
        cls.db_path = cls.root / "registry.sqlite"
        cls.service = SpentChallengeRegistryService(
            cls.db_path, client_keys={CLIENT_ID: CLIENT_KEY}, storage_key=REGISTRY_STORAGE_KEY,
            server_key_id="test-registry-server", server_private_key=Ed25519PrivateKey.generate())
        cls.anchor_path = cls.root / "client-anchor.sqlite"
        cls.anchor = RegistryQuorumAnchor(
            registry_id=REGISTRY_ID, registry_db_path=cls.db_path, path=cls.anchor_path,
            issuer_private_key=cls.issuer_private, issuer_keys=cls.issuer_keys,
            witnesses=cls.clients, witness_keys=cls.witness_keys,
            storage_key=ANCHOR_STORAGE_KEY, max_byzantine=1)
        cls.anchor.bootstrap(cls.service)
        if cls.anchor.check_current()["status"] != "CURRENT":
            raise RuntimeError("remote witness bootstrap did not reach CURRENT")

    @classmethod
    def tearDownClass(cls):
        # addClassCleanup below is also run when setUpClass fails partway through.
        pass

    @classmethod
    def _cleanup_all_processes(cls):
        for i in list(getattr(cls, "processes", {})):
            try:
                cls.stop_one(i)
            except Exception:
                pass
        tmp = getattr(cls, "tmp", None)
        if tmp is not None:
            try:
                tmp.cleanup()
            except Exception:
                pass

    @classmethod
    def spawn(cls, index: int, *, drop_after_first_attest: bool = False):
        old = cls.processes.get(index)
        if old is not None and old.poll() is None:
            raise AssertionError("cannot start second witness process for same roster slot")
        cmd = [sys.executable, str(ROOT / "remote_witness_http.py"),
               "--config", str(cls.configs[index]), "--port", "0"]
        if drop_after_first_attest:
            cmd.append("--drop-after-first-attest")
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, bufsize=1)
        # Drain stderr continuously. Failed TLS handshakes are expected adversarial
        # inputs; leaving stderr unread can fill the OS pipe and stall the child.
        stderr_tail = deque(maxlen=80)
        cls.process_stderr_tails[index] = stderr_tail
        def _drain_stderr():
            try:
                for err_line in proc.stderr:
                    stderr_tail.append(err_line)
            except Exception:
                return
        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True,
                                         name=f"witness-{index}-stderr-drain")
        cls.process_stderr_threads[index] = stderr_thread
        stderr_thread.start()
        # Never block the entire harness forever if a child fails before writing
        # its readiness record. This makes restart races observable and cleanup-safe.
        line_queue: Queue[str] = Queue(maxsize=1)
        def _read_ready_line():
            try:
                line_queue.put(proc.stdout.readline() if proc.stdout else "")
            except Exception:
                try: line_queue.put("")
                except Exception: pass
        threading.Thread(target=_read_ready_line, daemon=True).start()
        try:
            line = line_queue.get(timeout=15.0)
        except Empty:
            proc.terminate()
            try:
                proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=1.0)
            err = "".join(stderr_tail)
            raise RuntimeError(f"witness {index} readiness timeout after 15 seconds: {err}")
        if not line:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=1.0)
            err = "".join(stderr_tail)
            raise RuntimeError(f"witness {index} failed to start: {err}")
        ready = json.loads(line)
        if ready.get("ready") is not True or ready.get("witness_id") != cls.witness_ids[index - 1]:
            proc.terminate(); proc.wait(timeout=2)
            raise RuntimeError(f"invalid witness readiness record: {ready!r}")
        cls.processes[index] = proc
        cls.ports[index] = int(ready["port"])
        return ready

    @classmethod
    def stop_one(cls, index: int):
        proc = cls.processes[index]
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=2)
        if proc.stdout:
            try: proc.stdout.close()
            except Exception: pass
        thread = getattr(cls, "process_stderr_threads", {}).get(index)
        if thread is not None:
            thread.join(timeout=0.25)
        if proc.stderr:
            try: proc.stderr.close()
            except Exception: pass

    @classmethod
    def restart_one(cls, index: int, *, drop_after_first_attest: bool = False):
        cls.stop_one(index)
        ready = cls.spawn(index, drop_after_first_attest=drop_after_first_attest)
        cfg = json.loads(cls.configs[index].read_text(encoding="utf-8"))
        client = RemoteWitnessClient(cls.witness_ids[index - 1], f"https://{cls.bind_hosts[index - 1]}:{ready['port']}",
            cfg["api_key_id"], cls.api_keys[index], tls_ca_path=str(cls.tls_ca_path),
            tls_client_cert_path=str(cls.tls_client_cert_path), tls_client_key_path=str(cls.tls_client_key_path),
            timeout_seconds=1.5)
        cls.clients[index - 1] = client
        cls.anchor.witnesses = tuple(cls.clients)
        return client

    def setUp(self):
        # Previous tests may have stopped a service; relaunch it against the same
        # persistent witness database and swap only its transport client.
        for index in range(1, 5):
            if self.processes[index].poll() is not None:
                self.restart_one(index)
        for i, client in enumerate(self.clients):
            client.witness_id = self.witness_ids[i]

    def signed_request(self, path, body, *, request_id=None, method="POST", stamp=None):
        raw = canonical(body)
        rid = request_id or uuid.uuid4().hex
        ts = time.time_ns() // 1_000_000 if stamp is None else stamp
        signed = {"method": method, "path": path, "timestamp_ms": ts,
                  "request_id": rid, "body_sha256": hashlib.sha256(raw).hexdigest()}
        sig = hmac.new(CLIENT_KEY, DOMAIN_REGISTRY_REQUEST + canonical(signed), hashlib.sha256).hexdigest()
        headers = {"X-Lyc-Registry-Key-Id": CLIENT_ID, "X-Lyc-Registry-Request-Id": rid,
                   "X-Lyc-Registry-Timestamp-Ms": str(ts), "X-Lyc-Registry-Signature": sig}
        return method, path, raw, headers

    def call_registry(self, path, body, *, request_id=None):
        return self.anchor.dispatch(self.service, *self.signed_request(path, body, request_id=request_id))

    def challenge(self):
        now = time.time_ns() // 1_000_000
        return {"nonce": "n_" + uuid.uuid4().hex + "x", "database_id": "test.registry.db",
                "issued_at_ms": now, "expires_at_ms": now + 60_000, "policy_sha256": "a" * 64}

    def test_four_witnesses_are_distinct_os_processes_and_bootstrap_over_mtls(self):
        pids = [p.pid for p in self.processes.values()]
        self.assertEqual(len(set(pids)), 4)
        self.assertNotIn(os.getpid(), pids)
        head = self.anchor.current_quorum_head()
        self.assertGreaterEqual(head["sequence"], 1)
        self.assertEqual(len(head["witness_ids"]), 4)

    def test_mutation_and_checkpoint_pass_through_four_remote_http_processes(self):
        before = self.anchor.current_quorum_head()["sequence"]
        result = self.call_registry("/v1/challenges", self.challenge())
        self.assertEqual(result[0], 201)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before + 1)

    def test_one_remote_witness_down_is_tolerated(self):
        self.stop_one(1)
        result = self.call_registry("/v1/challenges", self.challenge())
        self.assertEqual(result[0], 201)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        self.assertEqual(self.anchor.current_quorum_head()["threshold"], 3)

    def test_two_remote_witnesses_down_fail_closed_without_mutation(self):
        self.stop_one(1); self.stop_one(2)
        with closing(sqlite3.connect(self.db_path)) as db:
            before = db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
        status, envelope, dropped = self.call_registry("/v1/challenges", self.challenge())
        with closing(sqlite3.connect(self.db_path)) as db:
            after = db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
        self.assertEqual(status, 503)
        self.assertTrue(envelope["body"].get("reconciliation_required"))
        self.assertEqual(before, after)

    def test_witness_process_restart_preserves_append_only_head(self):
        before = self.anchor.current_quorum_head()
        old_pid = self.processes[2].pid
        client = self.restart_one(2)
        self.assertNotEqual(self.processes[2].pid, old_pid)
        report = client.head_report("A" * 40)
        self.assertEqual(report["body"]["sequence"], before["sequence"])
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")

    def test_dropped_attest_response_after_witness_commit_recovers(self):
        before = self.anchor.current_quorum_head()["sequence"]
        self.restart_one(1, drop_after_first_attest=True)
        result = self.call_registry("/v1/challenges", self.challenge())
        self.assertEqual(result[0], 201)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before + 1)

    def test_duplicate_transport_request_id_is_rejected_before_reexecution(self):
        client = self.clients[0]
        body = {"challenge_nonce": "B" * 40}
        rid = "R" * 32
        first = client._post("/v1/head", body, request_id=rid)
        self.assertIn("body", first)
        with self.assertRaisesRegex(WitnessHTTPError, "replay-detected"):
            client._post("/v1/head", body, request_id=rid)

    def test_wrong_client_secret_cannot_request_head(self):
        bad = RemoteWitnessClient(self.witness_ids[0], f"https://{self.bind_hosts[0]}:{self.ports[1]}",
            "anchor-client-1", b"x" * 32, tls_ca_path=str(self.tls_ca_path),
            tls_client_cert_path=str(self.tls_client_cert_path), tls_client_key_path=str(self.tls_client_key_path),
            timeout_seconds=1)
        with self.assertRaisesRegex(WitnessHTTPError, "signature-invalid"):
            bad.head_report("C" * 40)

    def test_client_refuses_http_downgrade_and_unspecified_host(self):
        common = dict(tls_ca_path=str(self.tls_ca_path),
            tls_client_cert_path=str(self.tls_client_cert_path), tls_client_key_path=str(self.tls_client_key_path))
        with self.assertRaisesRegex(ValueError, "host-invalid"):
            RemoteWitnessClient("w", "https://0.0.0.0:1234", "key", b"x" * 32, **common)
        with self.assertRaisesRegex(ValueError, "requires-https"):
            RemoteWitnessClient("w", "http://127.0.0.1:1234", "key", b"x" * 32, **common)

    def test_client_supports_explicit_https_dns_endpoint_configuration(self):
        client = RemoteWitnessClient("witness-prod", "https://witness.example:9443", "key", b"x" * 32,
            tls_ca_path=str(self.tls_ca_path), tls_client_cert_path=str(self.tls_client_cert_path),
            tls_client_key_path=str(self.tls_client_key_path))
        self.assertEqual(client.base_url, "https://witness.example:9443")

    def test_server_bind_requires_explicit_nonloopback_opt_in_and_rejects_wildcard(self):
        self.assertEqual(validate_bind_host("127.0.0.9", False), "127.0.0.9")
        with self.assertRaisesRegex(ValueError, "explicit-opt-in"):
            validate_bind_host("192.0.2.9", False)
        self.assertEqual(validate_bind_host("192.0.2.9", True), "192.0.2.9")
        with self.assertRaisesRegex(ValueError, "wildcard-or-multicast"):
            validate_bind_host("0.0.0.0", True)
        with self.assertRaisesRegex(ValueError, "numeric-ip"):
            validate_bind_host("witness.example", True)

    def test_https_server_rejects_unknown_route(self):
        url = f"{self.clients[0].base_url}/v1/unknown"
        req = Request(url, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1, context=self.client_tls_context)
        self.assertEqual(err.exception.code, 404)

    def test_cleartext_http_cannot_speak_to_mtls_listener(self):
        # The listening socket is wrapped in TLS: a plain HTTP request is not
        # interpreted as an API request or allowed to reach application handlers.
        with socket.create_connection((self.bind_hosts[0], self.ports[1]), timeout=2) as sock:
            sock.settimeout(2)
            try:
                sock.sendall(b"POST /v1/head HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 2\r\n\r\n{}")
                response = sock.recv(512)
            except OSError:
                response = b""
        self.assertFalse(response.startswith(b"HTTP/1.1 200"))
        self.assertFalse(response.startswith(b"HTTP/1.1 401"))

    def test_noncanonical_request_target_query_is_rejected(self):
        url = f"{self.clients[0].base_url}/v1/head?unused=1"
        req = Request(url, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1, context=self.client_tls_context)
        self.assertEqual(err.exception.code, 400)

    def test_slow_tls_handshake_does_not_block_other_witness_requests(self):
        # Connect but deliberately do not start TLS. The server should handle
        # this handshake in a worker with a timeout while continuing to serve
        # other clients from the accept loop.
        slow = socket.create_connection((self.bind_hosts[0], self.ports[1]), timeout=2)
        try:
            time.sleep(0.05)
            started = time.monotonic()
            result = self.clients[0].head_report("SLOW" + uuid.uuid4().hex)
            elapsed = time.monotonic() - started
            self.assertIn("body", result)
            self.assertLess(elapsed, 2.0, f"slow handshake delayed valid request: {elapsed:.3f}s")
        finally:
            slow.close()

    def test_mtls_rejects_client_without_certificate(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(self.tls_ca_path))
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        req = Request(f"{self.clients[0].base_url}/v1/head", data=canonical({"challenge_nonce": "M" * 40}),
                      method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(Exception):
            urlopen(req, timeout=1, context=context)

    def test_mtls_rejects_wrong_coordinator_uri_even_when_ca_trusts_certificate(self):
        bad = RemoteWitnessClient(self.witness_ids[0], self.clients[0].base_url,
            self.clients[0].api_key_id, self.api_keys[1], tls_ca_path=str(self.tls_ca_path),
            tls_client_cert_path=str(self.tls_wrong_identity_cert_path),
            tls_client_key_path=str(self.tls_wrong_identity_key_path), timeout_seconds=1)
        with self.assertRaisesRegex(WitnessHTTPError, "client-identity-invalid"):
            bad.head_report("N" * 40)

    def test_client_timeout_bounds_a_tls_peer_that_never_sends_response_headers(self):
        # Isolate the client timeout with an mTLS peer that accepts a complete
        # request but deliberately never sends an HTTP status line or headers.
        class StallServer(ThreadingHTTPServer):
            daemon_threads = True
            allow_reuse_address = True
            def __init__(self, address, context):
                self.context = context
                super().__init__(address, StallHandler)
            def get_request(self):
                raw, addr = super().get_request()
                return self.context.wrap_socket(raw, server_side=True, do_handshake_on_connect=False), addr
            def handle_error(self, request, client_address):
                return
        class StallHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"
            def setup(self):
                self.request.settimeout(2)
                self.request.do_handshake()
                self.request.settimeout(5)
                super().setup()
            def log_message(self, *_args):
                return
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                if length:
                    self.rfile.read(length)
                time.sleep(2.0)  # Intentionally omit the HTTP response entirely.

        tls_server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls_server.minimum_version = ssl.TLSVersion.TLSv1_2
        tls_server.load_cert_chain(str(self.server_cert_paths[4]), str(self.server_key_paths[4]))
        tls_server.load_verify_locations(cafile=str(self.tls_ca_path))
        tls_server.verify_mode = ssl.CERT_REQUIRED
        server = StallServer((self.bind_hosts[3], 0), tls_server)
        thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
        thread.start()
        client = RemoteWitnessClient("stall-peer", f"https://{self.bind_hosts[3]}:{server.server_address[1]}",
            "stall-key", b"z" * 32, tls_ca_path=str(self.tls_ca_path),
            tls_client_cert_path=str(self.tls_client_cert_path), tls_client_key_path=str(self.tls_client_key_path),
            timeout_seconds=0.4)
        started = time.monotonic()
        try:
            with self.assertRaisesRegex(WitnessHTTPError, "transport-unavailable"):
                client.head_report("TIMEOUT" + uuid.uuid4().hex)
            elapsed = time.monotonic() - started
            self.assertLess(elapsed, 1.5, f"transport timeout was not bounded: {elapsed:.3f}s")
        finally:
            server.shutdown()
            server.server_close()

    def test_tls_server_certificate_is_bound_to_each_loopback_host(self):
        mismatched = RemoteWitnessClient(self.witness_ids[1], f"https://{self.bind_hosts[0]}:{self.ports[2]}",
            "anchor-client-2", self.api_keys[2], tls_ca_path=str(self.tls_ca_path),
            tls_client_cert_path=str(self.tls_client_cert_path), tls_client_key_path=str(self.tls_client_key_path),
            timeout_seconds=1)
        with self.assertRaisesRegex(WitnessHTTPError, "transport-unavailable"):
            mismatched.head_report("O" * 40)

    def test_authenticated_but_malformed_head_nonce_is_rejected_by_witness(self):
        with self.assertRaises(WitnessHTTPError) as err:
            self.clients[0].head_report("bad")
        self.assertEqual(err.exception.status, 400)

    def test_transport_request_body_is_bound_to_hmac(self):
        client = self.clients[0]
        stamp = time.time_ns() // 1_000_000
        rid = "T" * 32
        body = canonical({"challenge_nonce": "D" * 40})
        signed = {"method": "POST", "path": "/v1/head", "timestamp_ms": stamp,
                  "request_id": rid, "body_sha256": hashlib.sha256(body).hexdigest()}
        sig = hmac.new(client.api_secret, b"lyc-registry-witness-mtls-rpc-v3.9\n" + canonical(signed), hashlib.sha256).hexdigest()
        tampered = canonical({"challenge_nonce": "E" * 40})
        req = Request(client.base_url + "/v1/head", data=tampered, method="POST", headers={
            "Content-Type": "application/json", "X-Lyc-Witness-Key-Id": client.api_key_id,
            "X-Lyc-Witness-Request-Id": rid, "X-Lyc-Witness-Timestamp-Ms": str(stamp),
            "X-Lyc-Witness-Signature": sig})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1, context=self.client_tls_context)
        self.assertEqual(err.exception.code, 401)

    def test_oversized_transport_body_is_rejected_before_reading_body(self):
        # Advertise an oversized body but do not send it; the server must reject
        # from Content-Length without waiting for the body or accepting a huge read.
        with socket.create_connection((self.bind_hosts[1], self.ports[2]), timeout=2) as tcp:
            with self.client_tls_context.wrap_socket(tcp, server_hostname=self.bind_hosts[1]) as sock:
                sock.settimeout(2)
                sock.sendall((f"POST /v1/head HTTP/1.1\r\nHost: {self.bind_hosts[1]}\r\n"
                              "Content-Type: application/json\r\nContent-Length: 1048577\r\n"
                              "Connection: close\r\n\r\n").encode("ascii"))
                response = b""
                while b"\r\n\r\n" not in response:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
        self.assertTrue(response.startswith(b"HTTP/1.1 413 "), response[:200])

    def test_checkpoint_fetch_survives_process_restart(self):
        client = self.clients[3]
        checkpoint = client.get_checkpoint(1)
        self.assertIsNotNone(checkpoint)
        self.restart_one(4)
        checkpoint_after = self.clients[3].get_checkpoint(1)
        self.assertEqual(checkpoint, checkpoint_after)

    def test_fresh_nonce_head_reports_are_signed_by_remote_witnesses(self):
        nonce = "F" * 40
        for client in self.clients:
            report = client.head_report(nonce)
            self.assertEqual(report["body"]["challenge_nonce"], nonce)
            self.assertEqual(report["body"]["witness_id"], client.witness_id)

    def test_repeated_signed_reports_cannot_be_counted_as_distinct_witnesses(self):
        nonce = "G" * 40
        first = self.clients[0].head_report(nonce)
        second = self.clients[1].head_report(nonce)
        with self.assertRaises(RegistryQuorumUnavailable):
            verify_head_quorum([first, second, first, second], self.witness_keys,
                               registry_id=REGISTRY_ID, challenge_nonce=nonce)


if __name__ == "__main__":
    unittest.main(verbosity=2)
