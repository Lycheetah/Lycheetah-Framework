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
from http.client import HTTPConnection, HTTPSConnection
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
from spent_nonce_registry import DOMAIN_REGISTRY_REQUEST, DOMAIN_REGISTRY_RESPONSE, SpentChallengeRegistryService
from registry_checkpoint_quorum import (
    RegistryCheckpointError, RegistryQuorumAnchor, RegistryQuorumUnavailable, verify_head_quorum,
)
from remote_witness_http import RemoteWitnessClient, WitnessHTTPError, validate_bind_host
from registry_gateway_mtls import MTLSAnchoredRegistryHTTPServer, _numeric_ipv4_bind

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
COORDINATOR_URI_2 = "spiffe://lycheetah.local/coordinator-secondary"

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
        cls.tls_ca_key = ca_key
        cls.client_identity_uri = COORDINATOR_URI
        _, cls.tls_client_cert_path, cls.tls_client_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="lycheetah-coordinator",
            san=[x509.UniformResourceIdentifier(COORDINATOR_URI)], server=False)
        _, cls.tls_wrong_identity_cert_path, cls.tls_wrong_identity_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="other-coordinator",
            san=[x509.UniformResourceIdentifier("spiffe://other.local/coordinator")], server=False)
        _, cls.tls_second_identity_cert_path, cls.tls_second_identity_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="lycheetah-secondary-coordinator",
            san=[x509.UniformResourceIdentifier(COORDINATOR_URI_2)], server=False)
        _, cls.tls_multi_identity_cert_path, cls.tls_multi_identity_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="lycheetah-multi-coordinator",
            san=[x509.UniformResourceIdentifier(COORDINATOR_URI),
                 x509.UniformResourceIdentifier(COORDINATOR_URI_2)], server=False)
        cls.server_cert_paths = {}
        cls.server_key_paths = {}
        for i, host in enumerate(cls.bind_hosts, 1):
            _, cert_path, key_path = _issue_leaf(
                cls.root, ca_key, ca_cert, name=f"witness-server-{i}",
                san=[x509.IPAddress(ipaddress.ip_address(host))], server=True)
            cls.server_cert_paths[i] = cert_path
            cls.server_key_paths[i] = key_path
        _, cls.gateway_server_cert_path, cls.gateway_server_key_path = _issue_leaf(
            cls.root, ca_key, ca_cert, name="registry-gateway",
            san=[x509.IPAddress(ipaddress.ip_address("127.0.0.1"))], server=True)
        cls.client_tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(cls.tls_ca_path))
        cls.client_tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
        cls.client_tls_context.load_cert_chain(str(cls.tls_client_cert_path), str(cls.tls_client_key_path))
        cls.client2_tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(cls.tls_ca_path))
        cls.client2_tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
        cls.client2_tls_context.load_cert_chain(str(cls.tls_second_identity_cert_path), str(cls.tls_second_identity_key_path))
        cls.client_multi_identity_tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(cls.tls_ca_path))
        cls.client_multi_identity_tls_context.minimum_version = ssl.TLSVersion.TLSv1_2
        cls.client_multi_identity_tls_context.load_cert_chain(str(cls.tls_multi_identity_cert_path), str(cls.tls_multi_identity_key_path))
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
        cls.gateway_host = "127.0.0.1"
        cls.gateway_server = MTLSAnchoredRegistryHTTPServer(
            (cls.gateway_host, 0), service=cls.service, anchor=cls.anchor,
            server_cert_path=str(cls.gateway_server_cert_path),
            server_key_path=str(cls.gateway_server_key_path),
            client_ca_path=str(cls.tls_ca_path),
            allowed_coordinator_uri_sans=(COORDINATOR_URI,), allow_nonloopback=False)
        cls.gateway_thread = threading.Thread(
            target=cls.gateway_server.serve_forever, daemon=True, name="registry-gateway-mtls")
        cls.gateway_thread.start()
        cls.addClassCleanup(cls._cleanup_gateway)

    @classmethod
    def tearDownClass(cls):
        # addClassCleanup below is also run when setUpClass fails partway through.
        pass

    @classmethod
    def _cleanup_gateway(cls):
        server = getattr(cls, "gateway_server", None)
        if server is not None:
            try:
                server.shutdown()
            except Exception:
                pass
            try:
                server.server_close()
            except Exception:
                pass
        thread = getattr(cls, "gateway_thread", None)
        if thread is not None:
            thread.join(timeout=1.0)

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
        # Track the child immediately so class cleanup can reclaim it even when
        # startup/readiness fails partway through.
        cls.processes[index] = proc
        # Never block the entire harness forever if a child fails before writing
        # its readiness record. Allow a slower CI worker more headroom than v3.9.
        line_queue: Queue[str] = Queue(maxsize=1)
        def _read_ready_line():
            try:
                line_queue.put(proc.stdout.readline() if proc.stdout else "")
            except Exception:
                try: line_queue.put("")
                except Exception: pass
        threading.Thread(target=_read_ready_line, daemon=True).start()
        try:
            line = line_queue.get(timeout=30.0)
        except Empty:
            try:
                proc.terminate()
            except OSError:
                pass
            try:
                proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except OSError:
                    pass
                try:
                    proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    pass  # cleanup reports the still-live PID without masking the startup fault
            err = "".join(stderr_tail)
            raise RuntimeError(f"witness {index} readiness timeout after 30 seconds: {err}")
        if not line:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    try: proc.kill()
                    except OSError: pass
                    try: proc.wait(timeout=5.0)
                    except subprocess.TimeoutExpired: pass
                except OSError:
                    pass
            err = "".join(stderr_tail)
            raise RuntimeError(f"witness {index} failed to start: {err}")
        ready = json.loads(line)
        if ready.get("ready") is not True or ready.get("witness_id") != cls.witness_ids[index - 1]:
            proc.terminate(); proc.wait(timeout=2)
            raise RuntimeError(f"invalid witness readiness record: {ready!r}")
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

    def call_gateway(self, path, body, *, request_id=None, context=None, host=None,
                     raw_override=None, headers_override=None, method="POST", server=None):
        _, signed_path, raw, headers = self.signed_request(path, body, request_id=request_id, method=method)
        if raw_override is not None:
            raw = raw_override
        headers = dict(headers)
        headers.update({"Content-Type": "application/json", "Connection": "close"})
        if headers_override:
            headers.update(headers_override)
        active_server = server or self.gateway_server
        connection = HTTPSConnection(host or active_server.server_address[0], active_server.server_address[1],
                                     timeout=2.0, context=context or self.client_tls_context)
        try:
            connection.request(method, signed_path, body=raw, headers=headers)
            response = connection.getresponse()
            response_raw = response.read(128 * 1024 + 1)
            if len(response_raw) > 128 * 1024:
                raise AssertionError("gateway response exceeded test bound")
            try:
                decoded = json.loads(response_raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                decoded = None
            # Every application response—including signed error envelopes—must
            # bind to this request ID and verify against the registry signing key.
            if isinstance(decoded, dict) and "signature_b64" in decoded:
                expected_fields = {"http_status", "body", "server_key_id", "request_id", "signature_b64"}
                if set(decoded) != expected_fields or decoded.get("http_status") != response.status:
                    raise AssertionError("registry gateway response envelope invalid")
                # Success and authenticated semantic errors bind to the caller's
                # request ID. For failed request authentication, the dispatcher
                # deliberately returns a generic invalid-request-id to avoid
                # reflecting an untrusted asserted identity.
                supplied_rid = headers.get("X-Lyc-Registry-Request-Id")
                if decoded.get("request_id") != supplied_rid and not (
                    response.status == 401 and decoded.get("request_id") == "invalid-request-id"
                ):
                    raise AssertionError("registry gateway response request binding invalid")
                unsigned = {k: decoded[k] for k in ("http_status", "body", "server_key_id", "request_id")}
                signature = base64.b64decode(decoded["signature_b64"], validate=True)
                self.service.server_private_key.public_key().verify(
                    signature, DOMAIN_REGISTRY_RESPONSE + canonical(unsigned))
            return response.status, decoded
        finally:
            connection.close()

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
        try:
            with closing(sqlite3.connect(self.db_path)) as db:
                before = db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
            status, envelope, dropped = self.call_registry("/v1/challenges", self.challenge())
            with closing(sqlite3.connect(self.db_path)) as db:
                after = db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]
            self.assertEqual(status, 503)
            self.assertTrue(envelope["body"].get("reconciliation_required"))
            self.assertEqual(before, after)
        finally:
            # Restore shared fixture services at the end of this test so the next
            # test doesn't need to restart two processes in its setup phase.
            # This avoids an unnecessary extra restart cycle in constrained CI.
            for index in (1, 2):
                if self.processes[index].poll() is not None:
                    self.restart_one(index)

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

    # v4.1: coordinator-facing ingress now includes bounded pre-TLS admission.
    def test_registry_gateway_bind_requires_explicit_nonloopback_opt_in(self):
        self.assertEqual(_numeric_ipv4_bind("127.0.0.9", False), "127.0.0.9")
        with self.assertRaisesRegex(ValueError, "nonloopback-bind-requires-opt-in"):
            _numeric_ipv4_bind("10.20.30.40", False)
        self.assertEqual(_numeric_ipv4_bind("10.20.30.40", True), "10.20.30.40")
        with self.assertRaisesRegex(ValueError, "wildcard-or-reserved"):
            _numeric_ipv4_bind("0.0.0.0", True)
        with self.assertRaisesRegex(ValueError, "numeric-ipv4"):
            _numeric_ipv4_bind("gateway.example", True)
        with self.assertRaisesRegex(ValueError, "must-be-ipv4"):
            _numeric_ipv4_bind("::1", True)

    def test_registry_gateway_accepts_pinned_coordinator_and_anchors_mutation(self):
        before = self.anchor.current_quorum_head()["sequence"]
        status, response = self.call_gateway("/v1/challenges", self.challenge())
        self.assertEqual(status, 201, response)
        self.assertEqual(response.get("http_status"), 201)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before + 1)

    def test_registry_gateway_signed_response_binds_status_body_and_request_id(self):
        status, response = self.call_gateway("/v1/challenges", self.challenge())
        self.assertEqual(status, 201, response)
        self.assertEqual(response["http_status"], status)
        self.assertIn("request_id", response)
        unsigned = {k: response[k] for k in ("http_status", "body", "server_key_id", "request_id")}
        signature = base64.b64decode(response["signature_b64"], validate=True)
        self.service.server_private_key.public_key().verify(
            signature, DOMAIN_REGISTRY_RESPONSE + canonical(unsigned))
        unsigned["http_status"] = 403
        with self.assertRaises(Exception):
            self.service.server_private_key.public_key().verify(
                signature, DOMAIN_REGISTRY_RESPONSE + canonical(unsigned))

    def test_registry_gateway_rejects_missing_client_certificate(self):
        no_client_cert = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(self.tls_ca_path))
        no_client_cert.minimum_version = ssl.TLSVersion.TLSv1_2
        with self.assertRaises((ssl.SSLError, OSError, TimeoutError, ConnectionError)):
            self.call_gateway("/v1/challenges", self.challenge(), context=no_client_cert)

    def test_registry_gateway_rejects_wrong_uri_san_even_when_ca_trusts_client(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=str(self.tls_ca_path))
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(str(self.tls_wrong_identity_cert_path), str(self.tls_wrong_identity_key_path))
        before = self.anchor.current_quorum_head()["sequence"]
        status, response = self.call_gateway("/v1/challenges", self.challenge(), context=context)
        self.assertEqual(status, 403, response)
        self.assertEqual(response["body"]["error"], "coordinator-identity-invalid")
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)

    def test_registry_gateway_rejects_server_hostname_mismatch(self):
        before = self.anchor.current_quorum_head()["sequence"]
        with self.assertRaises((ssl.SSLError, OSError, TimeoutError, ConnectionError)):
            self.call_gateway("/v1/challenges", self.challenge(), host="localhost")
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)

    def test_registry_gateway_rejects_cleartext_http(self):
        with socket.create_connection((self.gateway_host, self.gateway_server.server_address[1]), timeout=2) as sock:
            sock.settimeout(2)
            try:
                sock.sendall(b"POST /v1/challenges HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Length: 2\r\n\r\n{}")
                response = sock.recv(512)
            except OSError:
                response = b""
        self.assertFalse(response.startswith(b"HTTP/1.1 200"))
        self.assertFalse(response.startswith(b"HTTP/1.1 401"))

    def test_registry_gateway_rejects_body_tampering_before_mutation(self):
        body = self.challenge()
        tampered = {**body, "nonce": "n_" + uuid.uuid4().hex + "x"}
        status, response = self.call_gateway("/v1/challenges", body, raw_override=canonical(tampered))
        self.assertEqual(status, 401, response)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")

    def test_registry_gateway_rejects_wrong_hmac_key(self):
        body = self.challenge()
        _, _, raw, headers = self.signed_request("/v1/challenges", body)
        # A plausible-shaped but incorrect MAC must not reach the registry mutation.
        status, response = self.call_gateway(
            "/v1/challenges", body, headers_override={"X-Lyc-Registry-Signature": "0" * 64})
        self.assertEqual(status, 401, response)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")

    def test_registry_gateway_duplicate_request_returns_cached_result_without_second_mutation(self):
        body = self.challenge()
        request_id = "gateway-replay-00000001"
        before = self.anchor.current_quorum_head()["sequence"]
        first_status, first = self.call_gateway("/v1/challenges", body, request_id=request_id)
        after_first = self.anchor.current_quorum_head()["sequence"]
        second_status, second = self.call_gateway("/v1/challenges", body, request_id=request_id)
        self.assertEqual(first_status, 201, first)
        self.assertEqual(second_status, 201, second)
        self.assertEqual(first, second)
        self.assertEqual(after_first, before + 1)
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], after_first)

    def test_registry_gateway_changed_payload_with_reused_request_id_is_conflict(self):
        request_id = "gateway-conflict-00001"
        status1, _ = self.call_gateway("/v1/challenges", self.challenge(), request_id=request_id)
        status2, response2 = self.call_gateway("/v1/challenges", self.challenge(), request_id=request_id)
        self.assertEqual(status1, 201)
        self.assertEqual(status2, 409, response2)
        self.assertEqual(response2["body"]["error"], "request-id-payload-conflict")

    def test_registry_gateway_rejects_non_post_method(self):
        before = self.anchor.current_quorum_head()["sequence"]
        status, response = self.call_gateway("/v1/challenges", self.challenge(), method="GET")
        self.assertEqual(status, 405, response)
        self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)

    def test_registry_gateway_rejects_duplicate_content_length(self):
        # Raw HTTPS request allows exercising malformed framing that clients normally hide.
        raw_sock = socket.create_connection((self.gateway_host, self.gateway_server.server_address[1]), timeout=2)
        try:
            tls_sock = self.client_tls_context.wrap_socket(raw_sock, server_hostname=self.gateway_host)
            tls_sock.settimeout(2)
            tls_sock.sendall((f"POST /v1/challenges HTTP/1.1\r\nHost: {self.gateway_host}:{self.gateway_server.server_address[1]}\r\n"
                              "Content-Type: application/json\r\nContent-Length: 2\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}").encode("ascii"))
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = tls_sock.recv(2048)
                if not chunk:
                    break
                data += chunk
        finally:
            try: tls_sock.close()
            except Exception: raw_sock.close()
        self.assertTrue(data.startswith(b"HTTP/1.1 400"), data[:200])

    def test_registry_gateway_oversized_body_rejected_before_read(self):
        with socket.create_connection((self.gateway_host, self.gateway_server.server_address[1]), timeout=2) as tcp:
            with self.client_tls_context.wrap_socket(tcp, server_hostname=self.gateway_host) as sock:
                sock.settimeout(2)
                sock.sendall((f"POST /v1/challenges HTTP/1.1\r\nHost: {self.gateway_host}:{self.gateway_server.server_address[1]}\r\n"
                              "Content-Type: application/json\r\nContent-Length: 131073\r\nConnection: close\r\n\r\n").encode("ascii"))
                response = b""
                while b"\r\n\r\n" not in response:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
        self.assertTrue(response.startswith(b"HTTP/1.1 413"), response[:200])



    # v4.1: bound pre-authentication connection resources before TLS handshake.
    def _make_limited_gateway(self, *, max_active=32, per_ip=16, per_minute=120,
                              request_timeout=1.0, coordinators=(COORDINATOR_URI,),
                              max_active_per_coordinator=8, per_coordinator_per_minute=60):
        return MTLSAnchoredRegistryHTTPServer(
            ("127.0.0.1", 0), service=self.service, anchor=self.anchor,
            server_cert_path=str(self.gateway_server_cert_path),
            server_key_path=str(self.gateway_server_key_path),
            client_ca_path=str(self.tls_ca_path),
            allowed_coordinator_uri_sans=coordinators,
            allow_nonloopback=False,
            request_timeout_seconds=request_timeout,
            max_concurrent_connections=max_active,
            max_connections_per_ip=per_ip,
            max_new_connections_per_minute=per_minute,
            max_active_requests_per_coordinator=max_active_per_coordinator,
            max_requests_per_coordinator_per_minute=per_coordinator_per_minute,
            request_queue_size=8,
        )

    def _start_temporary_gateway(self, server):
        thread = threading.Thread(target=server.serve_forever, daemon=True,
                                  name="bounded-registry-gateway-test")
        thread.start()
        return thread

    def _stop_temporary_gateway(self, server, thread):
        try:
            server.shutdown()
        finally:
            server.server_close()
            thread.join(timeout=2.0)

    def test_registry_gateway_active_connection_limit_closes_excess_before_tls(self):
        server = self._make_limited_gateway(max_active=1, per_ip=1, per_minute=600,
                                            request_timeout=0.6)
        thread = self._start_temporary_gateway(server)
        first = None
        before = self.anchor.current_quorum_head()["sequence"]
        try:
            raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            first = self.client_tls_context.wrap_socket(raw, server_hostname="127.0.0.1")
            first.settimeout(2)
            first.sendall(b"POST /v1/challenges HTTP/1.1\r\n")
            deadline = time.monotonic() + 1.0
            while server.admission_snapshot()["active_connections"] != 1 and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertEqual(server.admission_snapshot()["active_connections"], 1)

            second_raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            try:
                with self.assertRaises((ssl.SSLError, OSError, TimeoutError, ConnectionError)):
                    self.client_tls_context.wrap_socket(second_raw, server_hostname="127.0.0.1")
            finally:
                try:
                    second_raw.close()
                except OSError:
                    pass
            snap = server.admission_snapshot()
            self.assertEqual(snap["active_connections"], 1)
            self.assertGreaterEqual(snap["rejections"]["active-connection-limit"], 1)
            self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)
        finally:
            if first is not None:
                first.close()
            deadline = time.monotonic() + 2.0
            while server.admission_snapshot()["active_connections"] and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertEqual(server.admission_snapshot()["active_connections"], 0)
            status, response = self.call_gateway("/v1/challenges", self.challenge(), server=server)
            self.assertEqual(status, 201, response)
            self._stop_temporary_gateway(server, thread)

    def test_registry_gateway_burst_never_exceeds_global_active_bound(self):
        server = self._make_limited_gateway(max_active=4, per_ip=4, per_minute=600,
                                            request_timeout=0.9)
        thread = self._start_temporary_gateway(server)
        start = threading.Event()
        workers = []
        sockets = []
        sockets_lock = threading.Lock()
        before = self.anchor.current_quorum_head()["sequence"]

        def stalled_peer():
            sock = None
            try:
                if not start.wait(2.0):
                    return
                raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
                sock = self.client_tls_context.wrap_socket(raw, server_hostname="127.0.0.1")
                sock.settimeout(1.5)
                sock.sendall(b"POST /v1/challenges HTTP/1.1\r\n")
                with sockets_lock:
                    sockets.append(sock)
                time.sleep(0.25)
            except (ssl.SSLError, OSError, TimeoutError, ConnectionError):
                pass  # admission control intentionally closes excess peers pre-handshake
            finally:
                if sock is not None:
                    try:
                        sock.close()
                    except OSError:
                        pass

        try:
            for _ in range(24):
                worker = threading.Thread(target=stalled_peer, daemon=True)
                worker.start()
                workers.append(worker)
            start.set()
            peak = 0
            deadline = time.monotonic() + 4.0
            while time.monotonic() < deadline and any(w.is_alive() for w in workers):
                peak = max(peak, int(server.admission_snapshot()["active_connections"]))
                time.sleep(0.002)
            for worker in workers:
                worker.join(timeout=1.0)
            peak = max(peak, int(server.admission_snapshot()["active_connections"]))
            self.assertTrue(all(not worker.is_alive() for worker in workers))
            self.assertLessEqual(peak, 4)
            snap = server.admission_snapshot()
            rejected = sum(snap["rejections"].values())
            self.assertGreater(rejected, 0)
            self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)
        finally:
            start.set()
            for worker in workers:
                worker.join(timeout=1.0)
            for sock in sockets:
                try:
                    sock.close()
                except OSError:
                    pass
            self._stop_temporary_gateway(server, thread)

    def test_registry_gateway_per_ip_limit_is_enforced_separately(self):
        server = self._make_limited_gateway(max_active=2, per_ip=1, per_minute=600,
                                            request_timeout=0.6)
        thread = self._start_temporary_gateway(server)
        first = None
        try:
            raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            first = self.client_tls_context.wrap_socket(raw, server_hostname="127.0.0.1")
            first.settimeout(2)
            first.sendall(b"POST /v1/challenges HTTP/1.1\r\n")
            deadline = time.monotonic() + 1.0
            while server.admission_snapshot()["active_connections"] != 1 and time.monotonic() < deadline:
                time.sleep(0.005)
            second_raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            try:
                with self.assertRaises((ssl.SSLError, OSError, TimeoutError, ConnectionError)):
                    self.client_tls_context.wrap_socket(second_raw, server_hostname="127.0.0.1")
            finally:
                second_raw.close()
            snap = server.admission_snapshot()
            self.assertEqual(snap["active_connections"], 1)
            self.assertGreaterEqual(snap["rejections"]["per-ip-connection-limit"], 1)
        finally:
            if first is not None:
                first.close()
            deadline = time.monotonic() + 2.0
            while server.admission_snapshot()["active_connections"] and time.monotonic() < deadline:
                time.sleep(0.01)
            self._stop_temporary_gateway(server, thread)

    def test_registry_gateway_global_connection_rate_limit_precedes_tls(self):
        server = self._make_limited_gateway(max_active=4, per_ip=4, per_minute=1,
                                            request_timeout=1.0)
        thread = self._start_temporary_gateway(server)
        try:
            status, response = self.call_gateway("/v1/challenges", self.challenge(), server=server)
            self.assertEqual(status, 201, response)
            before = self.anchor.current_quorum_head()["sequence"]
            raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            try:
                with self.assertRaises((ssl.SSLError, OSError, TimeoutError, ConnectionError)):
                    self.client_tls_context.wrap_socket(raw, server_hostname="127.0.0.1")
            finally:
                raw.close()
            snap = server.admission_snapshot()
            self.assertGreaterEqual(snap["rejections"]["connection-rate-limit"], 1)
            self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)
        finally:
            self._stop_temporary_gateway(server, thread)

    def test_registry_gateway_rejects_invalid_admission_limits(self):
        base = {
            "service": self.service, "anchor": self.anchor,
            "server_cert_path": str(self.gateway_server_cert_path),
            "server_key_path": str(self.gateway_server_key_path),
            "client_ca_path": str(self.tls_ca_path),
            "allowed_coordinator_uri_sans": (COORDINATOR_URI,),
        }
        for kwargs in (
            {"max_concurrent_connections": True},
            {"max_connections_per_ip": 0},
            {"max_new_connections_per_minute": 0},
            {"max_active_requests_per_coordinator": True},
            {"max_requests_per_coordinator_per_minute": 0},
            {"request_queue_size": -1},
            {"max_concurrent_connections": 2, "max_connections_per_ip": 3},
            {"request_timeout_seconds": float("nan")},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    MTLSAnchoredRegistryHTTPServer(("127.0.0.1", 0), **base, **kwargs)


    # v4.2: authenticated identity quotas protect admitted work after mTLS.
    def test_one_coordinator_cannot_monopolize_authenticated_dispatch_slots(self):
        server = self._make_limited_gateway(
            max_active=4, per_ip=4, per_minute=600, request_timeout=1.3,
            coordinators=(COORDINATOR_URI, COORDINATOR_URI_2),
            max_active_per_coordinator=1, per_coordinator_per_minute=600)
        thread = self._start_temporary_gateway(server)
        stalled = None
        before = self.anchor.current_quorum_head()["sequence"]
        try:
            raw = socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=2)
            stalled = self.client_tls_context.wrap_socket(raw, server_hostname="127.0.0.1")
            stalled.settimeout(2)
            stalled.sendall((f"POST /v1/challenges HTTP/1.1\r\nHost: 127.0.0.1:{server.server_address[1]}\r\n"
                "X-Lyc-Registry-Request-Id: stalled-coordinator-0001\r\n"
                "Content-Type: application/json\r\nContent-Length: 1000\r\nConnection: close\r\n\r\n{}").encode())
            deadline = time.monotonic() + 1.0
            while server.admission_snapshot()["active_coordinator_count"] < 1 and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertEqual(server.admission_snapshot()["active_coordinator_count"], 1)

            # Same principal is bounded even though global and per-IP slots remain.
            status, response = self.call_gateway("/v1/challenges", self.challenge(), server=server)
            self.assertEqual(status, 429, response)
            self.assertEqual(response["body"]["error"], "coordinator-active-request-limit")

            # A separate explicitly allow-listed coordinator has independent quota.
            status2, response2 = self.call_gateway(
                "/v1/challenges", self.challenge(), context=self.client2_tls_context, server=server)
            self.assertEqual(status2, 201, response2)
            snap = server.admission_snapshot()
            self.assertGreaterEqual(snap["rejections"]["coordinator-active-request-limit"], 1)
            # Snapshot exports counts only, never principal identifiers.
            self.assertNotIn(COORDINATOR_URI, json.dumps(snap))
            self.assertNotIn(COORDINATOR_URI_2, json.dumps(snap))
        finally:
            if stalled is not None:
                stalled.close()
            deadline = time.monotonic() + 2.0
            while server.admission_snapshot()["active_connections"] and time.monotonic() < deadline:
                time.sleep(0.01)
            self._stop_temporary_gateway(server, thread)
        self.assertGreater(self.anchor.current_quorum_head()["sequence"], before)

    def test_per_coordinator_request_rate_is_independent_and_signed(self):
        server = self._make_limited_gateway(
            max_active=4, per_ip=4, per_minute=600, request_timeout=1.0,
            coordinators=(COORDINATOR_URI, COORDINATOR_URI_2),
            max_active_per_coordinator=4, per_coordinator_per_minute=1)
        thread = self._start_temporary_gateway(server)
        try:
            first_status, first = self.call_gateway("/v1/challenges", self.challenge(), server=server)
            self.assertEqual(first_status, 201, first)
            same_status, same = self.call_gateway("/v1/challenges", self.challenge(), server=server)
            self.assertEqual(same_status, 429, same)
            self.assertEqual(same["body"]["error"], "coordinator-request-rate-limit")
            other_status, other = self.call_gateway(
                "/v1/challenges", self.challenge(), context=self.client2_tls_context, server=server)
            self.assertEqual(other_status, 201, other)
            self.assertGreaterEqual(server.admission_snapshot()["rejections"]["coordinator-request-rate-limit"], 1)
        finally:
            self._stop_temporary_gateway(server, thread)

    def test_certificate_with_two_allowlisted_uri_sans_is_rejected_as_ambiguous(self):
        server = self._make_limited_gateway(
            max_active=4, per_ip=4, per_minute=600,
            coordinators=(COORDINATOR_URI, COORDINATOR_URI_2))
        thread = self._start_temporary_gateway(server)
        before = self.anchor.current_quorum_head()["sequence"]
        try:
            status, response = self.call_gateway(
                "/v1/challenges", self.challenge(),
                context=self.client_multi_identity_tls_context, server=server)
            self.assertEqual(status, 403, response)
            self.assertEqual(response["body"]["error"], "coordinator-identity-ambiguous")
            self.assertEqual(self.anchor.current_quorum_head()["sequence"], before)
            self.assertGreaterEqual(server.admission_snapshot()["rejections"]["coordinator-identity-ambiguous"], 1)
        finally:
            self._stop_temporary_gateway(server, thread)


if __name__ == "__main__":
    unittest.main(verbosity=2)
