from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from contextlib import closing
from http.client import HTTPConnection
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import canonical
from spent_nonce_registry import DOMAIN_REGISTRY_REQUEST, SpentChallengeRegistryService
from registry_checkpoint_quorum import (
    RegistryCheckpointError, RegistryQuorumAnchor, RegistryQuorumUnavailable, verify_head_quorum,
)
from remote_witness_http import RemoteWitnessClient, WitnessHTTPError

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


class RemoteWitnessProcessTests(unittest.TestCase):
    """Share one four-process witness fleet; mutations are append-only across tests."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="lyc-r28-")
        cls.root = Path(cls.tmp.name)
        cls.processes: dict[int, subprocess.Popen] = {}
        cls.ports: dict[int, int] = {}
        cls.configs: dict[int, Path] = {}
        cls.api_keys: dict[int, bytes] = {}
        cls.witness_ids = [f"remote-witness-{i}" for i in range(1, 5)]
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
            }
            cfg_path = cls.root / f"{wid}.config.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            cls.configs[i] = cfg_path
            cls.spawn(i)
            cls.clients.append(RemoteWitnessClient(wid, f"http://127.0.0.1:{cls.ports[i]}",
                                                   cfg["api_key_id"], api, timeout_seconds=1.5))
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
        for i in list(cls.processes):
            try:
                cls.stop_one(i)
            except Exception:
                pass
        cls.tmp.cleanup()

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
        line = proc.stdout.readline()
        if not line:
            err = proc.stderr.read() if proc.stderr else ""
            proc.kill(); proc.wait(timeout=2)
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
        for pipe in (proc.stdout, proc.stderr):
            if pipe:
                try: pipe.close()
                except Exception: pass

    @classmethod
    def restart_one(cls, index: int, *, drop_after_first_attest: bool = False):
        cls.stop_one(index)
        ready = cls.spawn(index, drop_after_first_attest=drop_after_first_attest)
        cfg = json.loads(cls.configs[index].read_text(encoding="utf-8"))
        client = RemoteWitnessClient(cls.witness_ids[index - 1], f"http://127.0.0.1:{ready['port']}",
                                     cfg["api_key_id"], cls.api_keys[index], timeout_seconds=1.5)
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

    def test_four_witnesses_are_distinct_os_processes_and_bootstrap_over_http(self):
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
        bad = RemoteWitnessClient(self.witness_ids[0], f"http://127.0.0.1:{self.ports[1]}",
                                  "anchor-client-1", b"x" * 32, timeout_seconds=1)
        with self.assertRaisesRegex(WitnessHTTPError, "signature-invalid"):
            bad.head_report("C" * 40)

    def test_client_refuses_non_loopback_or_https_downgrade_configuration(self):
        with self.assertRaisesRegex(ValueError, "loopback-http"):
            RemoteWitnessClient("w", "http://0.0.0.0:1234", "key", b"x" * 32)
        with self.assertRaisesRegex(ValueError, "loopback-http"):
            RemoteWitnessClient("w", "https://witness.example", "key", b"x" * 32)

    def test_http_server_process_rejects_unknown_route(self):
        url = f"http://127.0.0.1:{self.ports[1]}/v1/unknown"
        req = Request(url, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1)
        self.assertEqual(err.exception.code, 404)

    def test_noncanonical_request_target_query_is_rejected(self):
        url = f"http://127.0.0.1:{self.ports[1]}/v1/head?unused=1"
        req = Request(url, data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1)
        self.assertEqual(err.exception.code, 400)

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
        sig = hmac.new(client.api_secret, b"lyc-registry-witness-http-rpc-v3.8\n" + canonical(signed), hashlib.sha256).hexdigest()
        tampered = canonical({"challenge_nonce": "E" * 40})
        req = Request(client.base_url + "/v1/head", data=tampered, method="POST", headers={
            "Content-Type": "application/json", "X-Lyc-Witness-Key-Id": client.api_key_id,
            "X-Lyc-Witness-Request-Id": rid, "X-Lyc-Witness-Timestamp-Ms": str(stamp),
            "X-Lyc-Witness-Signature": sig})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=1)
        self.assertEqual(err.exception.code, 401)

    def test_oversized_transport_body_is_rejected_before_reading_body(self):
        # Advertise an oversized body but do not send it; the server must reject
        # from Content-Length without waiting for the body or accepting a huge read.
        with socket.create_connection(("127.0.0.1", self.ports[1]), timeout=2) as sock:
            sock.settimeout(2)
            sock.sendall(("POST /v1/head HTTP/1.1\r\nHost: 127.0.0.1\r\n"
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
