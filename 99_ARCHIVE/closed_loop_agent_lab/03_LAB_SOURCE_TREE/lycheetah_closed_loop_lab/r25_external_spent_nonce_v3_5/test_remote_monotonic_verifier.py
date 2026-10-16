from __future__ import annotations
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
import time
import unittest
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import DOMAIN_RECORD, canonical, b64, make_snapshot, sha_json, iso, utc_now
from checkpoint_witness_quorum import CheckpointWitness, SQLiteCASGuard, create_certificate
from durable_freshness_verifier import ChallengeLifecycleError, DurableFreshnessVerifier
from spent_nonce_registry import (
    SpentChallengeRegistryService, SpentChallengeRegistryClient, RegistryRejected,
    RegistryProtocolError, RegistryTransportError, serve_in_thread,
)
from remote_monotonic_verifier import RemoteMonotonicFreshnessVerifier

DBID = "lycheetah.external-registry.integration"
ANCHOR_ID = "primary.anchor.v1"
INTEGRITY_KEY = b"local-test-integrity-key-material-32bytes+"
CLIENT_KEY = b"registry-client-key-material-at-least-32-bytes"
STORAGE_KEY = b"registry-independent-storage-key-32-bytes-long"
SERVER_ID = "spent-registry.v1"


def make_record(anchor_private):
    snap = make_snapshot("a"*64, "b"*64, {"events":1}, {"signed":1})
    body = {"sequence":1,"database_id":DBID,**snap,
        "approval_id":"approval_"+uuid.uuid4().hex,
        "approval_nonce":"nonce_"+uuid.uuid4().hex,
        "reason_code":"approved.freshness.test","created_at":iso(utc_now()),
        "previous_record_sha256":None,"request_id":"req_"+uuid.uuid4().hex,
        "request_sha256":"c"*64,"server_key_id":ANCHOR_ID}
    digest = sha_json(body)
    signature = anchor_private.sign(DOMAIN_RECORD + canonical({"body":body,"record_sha256":digest,"server_key_id":ANCHOR_ID}))
    return {"body":body,"record_sha256":digest,"server_key_id":ANCHOR_ID,"signature_b64":b64(signature)}


class RemoteMonotonicVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-remote-spent-nonce-")
        self.root = Path(self.tmp.name)
        self.anchor_private = Ed25519PrivateKey.generate()
        self.anchor_keys = {ANCHOR_ID:self.anchor_private.public_key()}
        self.witness_private = {f"witness-{i}":Ed25519PrivateKey.generate() for i in range(1,5)}
        self.witness_public = {kid:key.public_key() for kid,key in self.witness_private.items()}
        self.record = make_record(self.anchor_private)
        self.witnesses = {
            kid: CheckpointWitness(kid,key,self.root/f"{kid}-votes.sqlite",
                SQLiteCASGuard(self.root/f"{kid}-guard.sqlite"),self.anchor_keys)
            for kid,key in self.witness_private.items()
        }
        votes = [w.attest(self.record) for w in self.witnesses.values()]
        self.certificate = create_certificate(self.record,votes,self.anchor_keys,self.witness_public)
        self.local_path = self.root/"primary-ledger.sqlite"
        self.registry_path = self.root/"registry-ledger.sqlite"
        self.local = DurableFreshnessVerifier(self.local_path,self.anchor_keys,self.witness_public,integrity_key=INTEGRITY_KEY)
        self.server_private = Ed25519PrivateKey.generate()
        self.service = SpentChallengeRegistryService(self.registry_path,
            client_keys={"client-v1":CLIENT_KEY},storage_key=STORAGE_KEY,
            server_key_id=SERVER_ID,server_private_key=self.server_private)
        self._start_server()
        self.wrapper = RemoteMonotonicFreshnessVerifier(self.local,self.client)

    def _start_server(self):
        self.server,self.thread = serve_in_thread(self.service)
        host,port = self.server.server_address
        self.client = SpentChallengeRegistryClient(f"http://{host}:{port}",
            client_key_id="client-v1",client_key=CLIENT_KEY,
            server_keys={SERVER_ID:self.server_private.public_key()},server_key_id=SERVER_ID,
            allow_http_loopback=True)

    def _stop_server(self):
        if getattr(self,"server",None):
            self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=3)
            self.server = None

    def tearDown(self):
        self._stop_server()
        self.tmp.cleanup()

    def issue_reports(self, wrapper=None):
        wrapper = wrapper or self.wrapper
        challenge = wrapper.issue(DBID)
        reports = [w.report_head(DBID,challenge.nonce) for w in self.witnesses.values()]
        return challenge,reports

    def snapshot(self,path,name):
        target = self.root/name
        with closing(sqlite3.connect(path)) as source, closing(sqlite3.connect(target)) as dst:
            source.backup(dst)
        return target

    def restore_db(self,path,snapshot):
        for suffix in ("-wal","-shm"):
            Path(str(path)+suffix).unlink(missing_ok=True)
        shutil.copy2(snapshot,path)

    def test_valid_chain_consumes_local_and_remote_nonce(self):
        challenge,reports = self.issue_reports()
        heads = self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        self.assertEqual(heads[-1].record_sha256,self.record["record_sha256"])
        with self.assertRaisesRegex(ChallengeLifecycleError,"already-consumed"):
            self.wrapper.verify_and_consume([self.certificate],reports,challenge)

    def test_primary_ledger_snapshot_rollback_is_rejected_by_remote_spent_nonce(self):
        challenge,reports = self.issue_reports()
        old = self.snapshot(self.local_path,"primary-before-consume.sqlite")
        self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        self.restore_db(self.local_path,old)
        restarted_local = DurableFreshnessVerifier(self.local_path,self.anchor_keys,self.witness_public,integrity_key=INTEGRITY_KEY)
        restarted_wrapper = RemoteMonotonicFreshnessVerifier(restarted_local,self.client)
        with self.assertRaisesRegex(RegistryRejected,"already-consumed"):
            restarted_wrapper.verify_and_consume([self.certificate],reports,challenge)

    def test_lost_remote_consume_response_burns_nonce_and_fails_closed(self):
        challenge,reports = self.issue_reports()
        self.service.drop_after_commit_count = 1
        with self.assertRaises(RegistryTransportError):
            self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        # Remote transaction committed, response disappeared. The local challenge
        # is still pending, but the external registry blocks a second acceptance.
        self.assertEqual(self.local._load_pending(challenge.nonce,database_id=DBID)["state"],"PENDING")
        with self.assertRaisesRegex(RegistryRejected,"already-consumed"):
            self.wrapper.verify_and_consume([self.certificate],reports,challenge)

    def test_bad_witness_reports_do_not_spend_remote_nonce(self):
        challenge,reports = self.issue_reports()
        forged=[dict(r) for r in reports]
        forged[0]["signature_b64"]="A"*88
        with self.assertRaises(Exception):
            self.wrapper.verify_and_consume([self.certificate],forged,challenge)
        heads=self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        self.assertEqual(heads[-1].record_sha256,self.record["record_sha256"])

    def test_expired_challenge_is_denied_by_registry(self):
        # Freeze the primary verifier's clock for the test so its local expiry
        # check still passes, while the independent registry's real clock advances.
        frozen_now = time.time_ns() // 1_000_000
        short_local = DurableFreshnessVerifier(self.local_path,self.anchor_keys,self.witness_public,
            integrity_key=INTEGRITY_KEY,challenge_ttl_seconds=1,clock_ms=lambda:frozen_now)
        wrapper = RemoteMonotonicFreshnessVerifier(short_local,self.client)
        challenge,reports = self.issue_reports(wrapper)
        time.sleep(1.1)
        with self.assertRaisesRegex(RegistryRejected,"expired"):
            wrapper.verify_and_consume([self.certificate],reports,challenge)

    def test_wrong_envelope_policy_does_not_consume_nonce(self):
        challenge,reports=self.issue_reports()
        forged=replace(challenge,policy_sha256="f"*64)
        with self.assertRaisesRegex(ChallengeLifecycleError,"binding-mismatch"):
            self.wrapper.verify_and_consume([self.certificate],reports,forged)
        self.wrapper.verify_and_consume([self.certificate],reports,challenge)

    def test_concurrent_remote_consumers_accept_exactly_one(self):
        challenge,reports=self.issue_reports()
        count=8; barrier=threading.Barrier(count); outcomes=[]; lock=threading.Lock()
        def worker():
            local=DurableFreshnessVerifier(self.local_path,self.anchor_keys,self.witness_public,integrity_key=INTEGRITY_KEY)
            wrapper=RemoteMonotonicFreshnessVerifier(local,self.client)
            barrier.wait(timeout=5)
            try:
                wrapper.verify_and_consume([self.certificate],reports,challenge); result="accepted"
            except (ChallengeLifecycleError,RegistryProtocolError) as exc:
                result="rejected:"+str(exc)
            except Exception as exc:
                result="unexpected:"+type(exc).__name__+":"+str(exc)
            with lock: outcomes.append(result)
        threads=[threading.Thread(target=worker) for _ in range(count)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=10)
        self.assertTrue(all(not t.is_alive() for t in threads),outcomes)
        self.assertEqual(outcomes.count("accepted"),1,outcomes)
        self.assertEqual(sum(v.startswith("rejected:") for v in outcomes),count-1,outcomes)
        self.assertFalse(any(v.startswith("unexpected:") for v in outcomes),outcomes)

    def test_remote_unavailable_fails_closed_without_consuming_local_state(self):
        challenge,reports=self.issue_reports()
        self._stop_server()
        with self.assertRaises(RegistryTransportError):
            self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        self.assertEqual(self.local._load_pending(challenge.nonce,database_id=DBID)["state"],"PENDING")

    def test_registry_key_is_required(self):
        bad=SpentChallengeRegistryClient(self.client.base_url,client_key_id="client-v1",
            client_key=b"wrong-client-key-material-that-is-32-bytes!!",
            server_keys={SERVER_ID:self.server_private.public_key()},server_key_id=SERVER_ID,
            allow_http_loopback=True)
        challenge,reports=self.issue_reports()
        with self.assertRaises(RegistryRejected):
            bad.consume(challenge)

    def test_untrusted_or_non_loopback_http_endpoint_is_rejected(self):
        with self.assertRaisesRegex(RegistryProtocolError,"https"):
            SpentChallengeRegistryClient("http://example.com",client_key_id="client-v1",
                client_key=CLIENT_KEY,server_keys={SERVER_ID:self.server_private.public_key()},
                server_key_id=SERVER_ID)

    def test_tampered_signed_server_response_is_rejected(self):
        original = self.service._sign
        def tamper_after_sign(status, body, request_id):
            envelope = original(status, body, request_id)
            envelope["body"] = {**envelope["body"], "forged_field": True}
            return envelope
        self.service._sign = tamper_after_sign
        with self.assertRaisesRegex(RegistryProtocolError, "response-signature-invalid"):
            self.wrapper.issue(DBID)

    def test_registry_row_tampering_fails_closed(self):
        challenge, _ = self.issue_reports()
        with closing(sqlite3.connect(self.registry_path)) as db:
            db.execute("UPDATE challenges SET state='CONSUMED',consumed_at_ms=? WHERE nonce=?",
                       (int(time.time()*1000), challenge.nonce))
            db.commit()
        with self.assertRaisesRegex(RegistryRejected, "unavailable-or-invalid"):
            self.client.consume(challenge)

    def test_registration_response_lost_before_commit_returns_no_challenge(self):
        self.service.drop_before_commit_count = 1
        with self.assertRaises(RegistryTransportError):
            self.wrapper.issue(DBID)
        # The challenge created in the primary ledger is not returned. A new issue
        # uses a new nonce; a caller is never told that uncertain registration worked.
        challenge, reports = self.issue_reports()
        heads = self.wrapper.verify_and_consume([self.certificate], reports, challenge)
        self.assertEqual(heads[-1].record_sha256, self.record["record_sha256"])

    def test_registration_response_lost_after_commit_returns_no_challenge(self):
        self.service.drop_after_commit_count = 1
        with self.assertRaises(RegistryTransportError):
            self.wrapper.issue(DBID)
        # The external registry may contain an orphan pending nonce, but the caller
        # never receives it. A distinct challenge can be issued and used normally.
        challenge, reports = self.issue_reports()
        heads = self.wrapper.verify_and_consume([self.certificate], reports, challenge)
        self.assertEqual(heads[-1].record_sha256, self.record["record_sha256"])

    def test_primary_and_registry_restore_together_replays_negative_control(self):
        """Negative control: both trust domains rolled back defeat this reference protocol."""
        challenge,reports=self.issue_reports()
        local_old=self.snapshot(self.local_path,"primary-before-both-rollback.sqlite")
        reg_old=self.snapshot(self.registry_path,"registry-before-both-rollback.sqlite")
        self.wrapper.verify_and_consume([self.certificate],reports,challenge)
        self._stop_server()
        self.restore_db(self.local_path,local_old)
        self.restore_db(self.registry_path,reg_old)
        self._start_server()
        local=DurableFreshnessVerifier(self.local_path,self.anchor_keys,self.witness_public,integrity_key=INTEGRITY_KEY)
        wrapper=RemoteMonotonicFreshnessVerifier(local,self.client)
        # Expected acceptance shows why the remote registry must be separately
        # administered and itself protected from old backup restore.
        heads=wrapper.verify_and_consume([self.certificate],reports,challenge)
        self.assertEqual(heads[-1].record_sha256,self.record["record_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
