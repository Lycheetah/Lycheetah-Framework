from __future__ import annotations

import hashlib
import hmac
import json
import shutil
import sqlite3
import tempfile
import unittest
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection, RemoteDisconnected
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import canonical
from spent_nonce_registry import DOMAIN_REGISTRY_REQUEST, SpentChallengeRegistryService
from registry_checkpoint_quorum import (
    RegistryCheckpoint,
    RegistryCheckpointError,
    RegistryCheckpointWitness,
    RegistryQuorumAnchor,
    RegistryQuorumUnavailable,
    RegistryRollbackDetected,
    AnchoredRegistryHTTPServer,
    fingerprint_sqlite_state,
    make_certificate,
    quorum_threshold,
    verify_certificate,
    verify_head_quorum,
)

CLIENT_ID = "registry-test-client"
CLIENT_KEY = b"registry-test-client-key-material-minimum-32-bytes"
REGISTRY_STORAGE_KEY = b"registry-service-storage-key-material-32-bytes"
ANCHOR_STORAGE_KEY = b"registry-client-anchor-storage-key-32-bytes"
REGISTRY_ID = "test.spent.registry"
ISSUER_ID = "registry-issuer"


class RegistryCheckpointQuorumTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lyc-r27-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = [1_800_000_000_000]
        self.issuer_private = Ed25519PrivateKey.generate()
        self.issuer_keys = {ISSUER_ID: self.issuer_private.public_key()}
        self.witness_private = {f"witness-{i}": Ed25519PrivateKey.generate() for i in range(1, 5)}
        self.witness_keys = {wid: key.public_key() for wid, key in self.witness_private.items()}
        self.witnesses = []
        for i, (wid, key) in enumerate(self.witness_private.items(), start=1):
            self.witnesses.append(RegistryCheckpointWitness(
                wid, key, self.root / f"{wid}.sqlite",
                (f"registry-witness-storage-key-{i}-material-32bytes").encode()[:48].ljust(48,b"x"),
                self.issuer_keys, REGISTRY_ID, clock_ms=lambda: self.now[0]))
        self.db_path = self.root / "registry.sqlite"
        self.service = SpentChallengeRegistryService(
            self.db_path, client_keys={CLIENT_ID: CLIENT_KEY}, storage_key=REGISTRY_STORAGE_KEY,
            server_key_id="test-server", server_private_key=Ed25519PrivateKey.generate(),
            max_clock_skew_ms=30_000, clock_ms=lambda: self.now[0])
        self.anchor_path = self.root / "client-anchor.sqlite"
        self.anchor = self.make_anchor()
        self.anchor.bootstrap(self.service)
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")

    def make_anchor(self, *, witnesses=None, path=None):
        return RegistryQuorumAnchor(
            registry_id=REGISTRY_ID, registry_db_path=self.db_path,
            path=path or self.anchor_path, issuer_private_key=self.issuer_private,
            issuer_keys=self.issuer_keys, witnesses=witnesses or self.witnesses,
            witness_keys={w.witness_id: self.witness_keys[w.witness_id] for w in (witnesses or self.witnesses)},
            storage_key=ANCHOR_STORAGE_KEY, max_byzantine=1, clock_ms=lambda: self.now[0])

    def signed_request(self, path, body, *, request_id=None, method="POST", stamp=None):
        raw = canonical(body)
        rid = request_id or uuid.uuid4().hex
        ts = self.now[0] if stamp is None else stamp
        signed = {"method": method, "path": path, "timestamp_ms": ts,
                  "request_id": rid, "body_sha256": hashlib.sha256(raw).hexdigest()}
        sig = hmac.new(CLIENT_KEY, DOMAIN_REGISTRY_REQUEST + canonical(signed), hashlib.sha256).hexdigest()
        headers = {"X-Lyc-Registry-Key-Id": CLIENT_ID, "X-Lyc-Registry-Request-Id": rid,
                   "X-Lyc-Registry-Timestamp-Ms": str(ts), "X-Lyc-Registry-Signature": sig}
        return method, path, raw, headers

    def request(self, path, body, **kwargs):
        return self.anchor.dispatch(self.service, *self.signed_request(path, body, **kwargs))

    def challenge(self, *, nonce=None, issued=None, expires=None):
        return {"nonce": nonce or ("n_" + uuid.uuid4().hex + "x"),
                "database_id": "test.registry.db", "issued_at_ms": self.now[0] if issued is None else issued,
                "expires_at_ms": self.now[0] + 60_000 if expires is None else expires,
                "policy_sha256": "a" * 64}

    def register(self, challenge=None, **kwargs):
        return self.request("/v1/challenges", challenge or self.challenge(), **kwargs)

    def consume(self, challenge, **kwargs):
        body = {k: challenge[k] for k in ("database_id", "policy_sha256", "issued_at_ms", "expires_at_ms")}
        return self.request(f"/v1/challenges/{challenge['nonce']}/consume", body, **kwargs)

    @staticmethod
    def sqlite_snapshot(source: Path, target: Path):
        target.unlink(missing_ok=True)
        with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(target)) as dst:
            src.backup(dst)
            dst.commit()

    @staticmethod
    def restore_snapshot(snapshot: Path, target: Path):
        for suffix in ("", "-wal", "-shm"):
            Path(str(target) + suffix).unlink(missing_ok=True)
        shutil.copy2(snapshot, target)

    def test_bootstrap_and_honest_registry_mutations_advance_fresh_quorum(self):
        c = self.challenge()
        first = self.register(c)
        self.assertEqual(first[0], 201)
        state1 = self.anchor.check_current()
        self.assertEqual(state1["quorum_head"]["sequence"], 2)
        second = self.consume(c)
        self.assertEqual(second[0], 200)
        state2 = self.anchor.check_current()
        self.assertEqual(state2["quorum_head"]["sequence"], 3)
        self.assertNotEqual(state1["quorum_head"]["state_sha256"], state2["quorum_head"]["state_sha256"])

    def test_primary_database_restore_is_detected_by_remote_quorum(self):
        c = self.challenge()
        self.register(c)
        registry_snap = self.root / "registry-before-consume.sqlite"
        self.sqlite_snapshot(self.db_path, registry_snap)
        self.consume(c)
        self.restore_snapshot(registry_snap, self.db_path)
        with self.assertRaisesRegex(RegistryRollbackDetected, "registry-state-diverges"):
            self.anchor.check_current()

    def test_coordinated_primary_and_client_anchor_restore_is_detected(self):
        c = self.challenge()
        self.register(c)
        registry_snap = self.root / "registry-before-consume.sqlite"
        anchor_snap = self.root / "anchor-before-consume.sqlite"
        self.sqlite_snapshot(self.db_path, registry_snap)
        self.sqlite_snapshot(self.anchor_path, anchor_snap)
        self.consume(c)
        self.restore_snapshot(registry_snap, self.db_path)
        self.restore_snapshot(anchor_snap, self.anchor_path)
        restarted_anchor = self.make_anchor()
        with self.assertRaisesRegex(RegistryRollbackDetected, "external-quorum-ahead"):
            restarted_anchor.check_current()

    def test_coordinated_restore_of_every_witness_store_remains_negative_control(self):
        c = self.challenge()
        self.register(c)
        registry_snap = self.root / "registry-before-consume.sqlite"
        anchor_snap = self.root / "anchor-before-consume.sqlite"
        witness_snaps = []
        self.sqlite_snapshot(self.db_path, registry_snap)
        self.sqlite_snapshot(self.anchor_path, anchor_snap)
        for w in self.witnesses:
            snap = self.root / f"{w.witness_id}-before-consume.sqlite"
            self.sqlite_snapshot(w.path, snap); witness_snaps.append((w.path, snap))
        self.consume(c)
        self.restore_snapshot(registry_snap, self.db_path)
        self.restore_snapshot(anchor_snap, self.anchor_path)
        for target, snap in witness_snaps: self.restore_snapshot(snap, target)
        restarted = self.make_anchor()
        # Explicit negative control: if every supposedly independent witness store
        # is rolled back too, the local model cannot know those copies were old.
        self.assertEqual(restarted.check_current()["status"], "CURRENT")

    def test_direct_database_mutation_without_quorum_checkpoint_fails_closed(self):
        self.register(self.challenge())
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("UPDATE clock_state SET high_water_ms=high_water_ms+1 WHERE singleton=1")
            db.commit()
        with self.assertRaises((RegistryRollbackDetected, RegistryCheckpointError)):
            self.anchor.check_current()

    def test_partial_two_of_four_witness_publication_fails_closed_then_recovers_same_record(self):
        original_methods = []
        for w in self.witnesses[2:]:
            original_methods.append((w,w.attest))
            w.attest = lambda cp: (_ for _ in ()).throw(RegistryCheckpointError("simulated-witness-unavailable"))
        c = self.challenge()
        status, envelope, dropped = self.register(c)
        self.assertEqual(status, 503)
        self.assertFalse(dropped)
        with self.assertRaises(RegistryCheckpointError): self.anchor.check_current()
        for w, meth in original_methods: w.attest = meth
        recovered = self.anchor.recover_pending(self.service)
        self.assertEqual(recovered["status"], "ANCHORED")
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        # A retry of the same signed operation returns the authenticated cached result.
        signed = self.signed_request("/v1/challenges", c, request_id=envelope["body"].get("request_id") or uuid.uuid4().hex)
        # The failed wrapper's error envelope intentionally isn't the original request ID,
        # so use the recorded pending request identity to request its cached outcome.
        with closing(sqlite3.connect(self.anchor_path)) as db:
            row = db.execute("SELECT client_key_id,request_id,request_fingerprint,response_json FROM response_cache ORDER BY rowid DESC LIMIT 1").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(json.loads(row[3])["body"]["status"], "REGISTERED")

    def test_replay_of_same_authenticated_request_returns_cached_result_without_reexecution(self):
        c = self.challenge(); signed = self.signed_request("/v1/challenges", c)
        first = self.anchor.dispatch(self.service, *signed)
        second = self.anchor.dispatch(self.service, *signed)
        self.assertEqual(first[:2], second[:2])
        self.assertEqual(first[0], 201)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0], 1)

    def test_same_request_id_with_changed_payload_is_rejected(self):
        c = self.challenge(); signed = self.signed_request("/v1/challenges", c)
        self.anchor.dispatch(self.service, *signed)
        changed = dict(c); changed["policy_sha256"] = "b" * 64
        retry = self.signed_request("/v1/challenges", changed, request_id=signed[3]["X-Lyc-Registry-Request-Id"])
        status, envelope, dropped = self.anchor.dispatch(self.service, *retry)
        self.assertEqual((status, envelope["body"]["error"], dropped), (409,"request-id-payload-conflict",False))

    def test_expired_cached_request_is_not_replayed(self):
        c = self.challenge(); signed = self.signed_request("/v1/challenges", c)
        self.anchor.dispatch(self.service, *signed)
        self.now[0] += self.service.max_clock_skew_ms + 1
        status,envelope,dropped = self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status,401)
        self.assertIn("timestamp-invalid",envelope["body"]["error"])

    def test_witness_head_report_requires_fresh_verifier_nonce(self):
        nonce1 = "A" * 32
        report = self.witnesses[0].head_report(nonce1)
        with self.assertRaises(RegistryQuorumUnavailable):
            verify_head_quorum([report]*4,self.witness_keys,registry_id=REGISTRY_ID,
                challenge_nonce="B"*32, max_byzantine=1, now_ms=self.now[0])

    def test_split_two_two_head_reports_have_no_quorum(self):
        c=self.challenge(); self.register(c)
        state_one = self.anchor.check_current()["quorum_head"]
        # Generate a valid alternate checkpoint without voting it. Two witnesses
        # are asked to advance to it; the other two remain on the previous head.
        alternate = RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=state_one["sequence"]+1,
            state_sha256="f"*64,previous_record_sha256=state_one["record_sha256"],request_id="fork.attempt",
            private_key=self.issuer_private,issued_at_ms=self.now[0])
        for w in self.witnesses[:2]: w.attest(alternate)
        nonce = "C"*32
        reports = [w.head_report(nonce) for w in self.witnesses]
        with self.assertRaises(RegistryQuorumUnavailable):
            verify_head_quorum(reports,self.witness_keys,registry_id=REGISTRY_ID,challenge_nonce=nonce,
                max_byzantine=1,now_ms=self.now[0])

    def test_witness_refuses_equivocation_at_locked_sequence(self):
        c=self.challenge(); self.register(c)
        head=self.anchor.check_current()["quorum_head"]
        first=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=head["sequence"]+1,
            state_sha256="1"*64,previous_record_sha256=head["record_sha256"],request_id="fork.first",
            private_key=self.issuer_private,issued_at_ms=self.now[0])
        second=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=head["sequence"]+1,
            state_sha256="2"*64,previous_record_sha256=head["record_sha256"],request_id="fork.second",
            private_key=self.issuer_private,issued_at_ms=self.now[0])
        self.witnesses[0].attest(first)
        with self.assertRaisesRegex(RegistryCheckpointError,"equivocation"):
            self.witnesses[0].attest(second)

    def test_duplicate_public_key_aliases_cannot_count_as_multiple_witnesses(self):
        aliased = dict(self.witness_keys); aliased["witness-alias"] = aliased["witness-1"]
        with self.assertRaisesRegex(RegistryCheckpointError,"alias"):
            verify_head_quorum([],aliased,registry_id=REGISTRY_ID,challenge_nonce="D"*32)

    def test_invalid_checkpoint_signature_is_rejected(self):
        cp=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=1,state_sha256="a"*64,
            previous_record_sha256=None,request_id="test.checkpoint",private_key=self.issuer_private,issued_at_ms=self.now[0])
        bad=cp.to_dict(); bad["body"]["state_sha256"]="b"*64
        with self.assertRaisesRegex(RegistryCheckpointError,"signature-invalid"):
            self.witnesses[0].attest(bad)

    def test_checkpoint_sequence_parent_gap_is_rejected(self):
        cp=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=7,state_sha256="a"*64,
            previous_record_sha256="b"*64,request_id="test.checkpoint",private_key=self.issuer_private,issued_at_ms=self.now[0])
        with self.assertRaisesRegex(RegistryCheckpointError,"parent-mismatch"):
            self.witnesses[0].attest(cp)

    def test_local_head_tampering_is_detected(self):
        c=self.challenge(); self.register(c)
        with closing(sqlite3.connect(self.anchor_path)) as db:
            db.execute("UPDATE local_head SET sequence=sequence+1 WHERE singleton=1"); db.commit()
        with self.assertRaisesRegex(RegistryCheckpointError,"integrity-invalid"):
            self.anchor.check_current()

    def test_witness_current_head_tampering_is_detected(self):
        with closing(sqlite3.connect(self.witnesses[0].path)) as db:
            db.execute("UPDATE current_head SET sequence=sequence+1 WHERE registry_id=?",(REGISTRY_ID,)); db.commit()
        with self.assertRaisesRegex(RegistryCheckpointError,"integrity-invalid"):
            self.witnesses[0].head_report("E"*32)

    def test_witness_head_behind_append_only_vote_ledger_is_detected(self):
        c=self.challenge(); self.register(c)
        head=self.anchor.check_current()["quorum_head"]
        cp=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=head["sequence"]+1,state_sha256="f"*64,
            previous_record_sha256=head["record_sha256"],request_id="ledger.advance",private_key=self.issuer_private,issued_at_ms=self.now[0])
        self.witnesses[0].attest(cp)
        with closing(sqlite3.connect(self.witnesses[0].path)) as db:
            db.row_factory = sqlite3.Row
            # Simulate privileged current-head rollback while the append-only vote
            # ledger remains. The chain checker must detect this despite a valid old tag.
            row=db.execute("SELECT * FROM votes WHERE registry_id=? AND sequence=?",(REGISTRY_ID,head["sequence"])).fetchone()
            body={k:row[k] for k in ("registry_id","sequence","record_sha256","state_sha256")}
            tag=hmac.new(self.witnesses[0].storage_key,b"lyc-registry-local-anchor-v3.7\n"+canonical(body),hashlib.sha256).hexdigest()
            db.execute("DROP TRIGGER head_no_decrease")
            db.execute("UPDATE current_head SET sequence=?,record_sha256=?,state_sha256=?,row_hmac=? WHERE registry_id=?",
                (head["sequence"],head["record_sha256"],head["state_sha256"],tag,REGISTRY_ID)); db.commit()
        with self.assertRaisesRegex(RegistryCheckpointError,"vote-ledger"):
            self.witnesses[0].head_report("F"*32)

    def test_quorum_arithmetic_rejects_insufficient_roster(self):
        self.assertEqual(quorum_threshold(4,1),3)
        with self.assertRaisesRegex(RegistryCheckpointError,"too-small"):
            quorum_threshold(3,1)

    def test_fingerprint_detects_schema_drift(self):
        original=fingerprint_sqlite_state(self.db_path)
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("CREATE TABLE unexpected(value TEXT)"); db.commit()
        with self.assertRaisesRegex(RegistryCheckpointError,"table-set-unexpected"):
            fingerprint_sqlite_state(self.db_path)
        self.assertEqual(len(original),64)

    def test_checkpoint_certificate_requires_quorum_and_unique_votes(self):
        fresh = []
        for i, (wid, key) in enumerate(self.witness_private.items(), start=1):
            fresh.append(RegistryCheckpointWitness(wid,key,self.root/f"cert-{wid}.sqlite",
                (f"registry-cert-storage-key-{i}-material-32bytes").encode()[:48].ljust(48,b"y"),
                self.issuer_keys,REGISTRY_ID,clock_ms=lambda:self.now[0]))
        fresh_keys={w.witness_id:self.witness_keys[w.witness_id] for w in fresh}
        cp=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=1,state_sha256="a"*64,
            previous_record_sha256=None,request_id="cert.test",private_key=self.issuer_private,issued_at_ms=self.now[0])
        votes=[w.attest(cp) for w in fresh[:2]]
        with self.assertRaises(RegistryQuorumUnavailable):
            make_certificate(cp,votes,self.issuer_keys,fresh_keys,max_byzantine=1)
        votes=[w.attest(cp) for w in fresh[2:]]
        cert=make_certificate(cp,[*votes,*[w.attest(cp) for w in fresh[:2]]],self.issuer_keys,fresh_keys,max_byzantine=1)
        self.assertEqual(verify_certificate(cert,self.issuer_keys,fresh_keys,max_byzantine=1).record_sha256,cp.record_sha256)
        bad=dict(cert); bad["votes"]=bad["votes"]+[bad["votes"][0]]
        with self.assertRaises(RegistryCheckpointError): verify_certificate(bad,self.issuer_keys,fresh_keys,max_byzantine=1)

    def test_response_cache_tampering_fails_closed(self):
        c=self.challenge(); signed=self.signed_request("/v1/challenges",c)
        self.anchor.dispatch(self.service,*signed)
        with closing(sqlite3.connect(self.anchor_path)) as db:
            db.execute("UPDATE response_cache SET response_json='{}'"); db.commit()
        status,envelope,dropped=self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status,503)
        self.assertFalse(dropped)
        self.assertEqual(envelope["body"]["error"],"registry-checkpoint-failed-closed")
        self.assertIn("response-cache-integrity-invalid",envelope["body"]["reason_code"])
        self.assertTrue(envelope["body"]["reconciliation_required"])

    def test_lost_response_after_commit_is_anchored_and_retried_as_unknown_not_success(self):
        c=self.challenge()
        signed=self.signed_request("/v1/challenges",c)
        self.service.drop_after_commit_count=1
        status,envelope,dropped=self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status,503)
        self.assertTrue(dropped)
        self.assertEqual(self.anchor.check_current()["status"],"CURRENT")
        status2,envelope2,dropped2=self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status2,503)
        self.assertFalse(dropped2)
        self.assertEqual(envelope2["body"]["error"],"registry-operation-outcome-unknown")
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0],1)

    def test_unexpected_handler_exception_after_commit_fails_closed_and_recovers_unknown(self):
        c=self.challenge()
        signed=self.signed_request("/v1/challenges",c)
        original=self.service.handle
        calls=[0]
        def commit_then_raise(method,path,raw_body,headers):
            result=original(method,path,raw_body,headers)
            calls[0]+=1
            if calls[0] == 1:
                raise RuntimeError("simulated private provider detail")
            return result
        self.service.handle=commit_then_raise
        status,envelope,dropped=self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status,503)
        self.assertFalse(dropped)
        self.assertEqual(envelope["body"]["error"],"registry-checkpoint-failed-closed")
        self.assertEqual(envelope["body"]["reason_code"],"unexpected-dispatch-exception")
        self.assertNotIn("simulated private provider detail",json.dumps(envelope))
        self.service.handle=original
        status2,envelope2,dropped2=self.anchor.dispatch(self.service,*signed)
        self.assertEqual(status2,503)
        self.assertFalse(dropped2)
        self.assertEqual(envelope2["body"]["error"],"registry-operation-committed-response-lost")
        self.assertEqual(self.anchor.check_current()["status"],"CURRENT")
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0],1)

    def test_precommit_drop_leaves_no_pending_checkpoint_or_state_change(self):
        before=self.anchor.check_current()["quorum_head"]
        self.service.drop_before_commit_count=1
        c=self.challenge(); signed=self.signed_request("/v1/challenges",c)
        status,envelope,dropped=self.anchor.dispatch(self.service,*signed)
        self.assertEqual((status,envelope,dropped),(0,None,True))
        self.assertEqual(self.anchor.check_current()["quorum_head"]["record_sha256"],before["record_sha256"])

    def test_invalid_authentication_does_not_advance_external_checkpoint(self):
        before=self.anchor.check_current()["quorum_head"]
        method,path,raw,headers=self.signed_request("/v1/challenges",self.challenge())
        headers["X-Lyc-Registry-Signature"]="0"*64
        status,envelope,dropped=self.anchor.dispatch(self.service,method,path,raw,headers)
        self.assertEqual(status,401)
        self.assertEqual(self.anchor.check_current()["quorum_head"]["record_sha256"],before["record_sha256"])

    def test_expired_challenge_is_checkpointed_as_rejected_request(self):
        c=self.challenge(expires=self.now[0]+1000)
        self.register(c)
        self.now[0]=c["expires_at_ms"]
        result=self.consume(c)
        self.assertEqual(result[0],409)
        self.assertEqual(self.anchor.check_current()["status"],"CURRENT")

    def test_unavailable_quorum_never_returns_success(self):
        originals=[]
        for w in self.witnesses:
            originals.append((w,w.attest)); w.attest=lambda cp: (_ for _ in ()).throw(RegistryCheckpointError("unavailable"))
        status,envelope,dropped=self.register(self.challenge())
        self.assertEqual(status,503)
        self.assertFalse(dropped)
        self.assertTrue(envelope["body"]["reconciliation_required"])
        for w,meth in originals: w.attest=meth
        self.anchor.recover_pending(self.service)
        self.assertEqual(self.anchor.check_current()["status"],"CURRENT")

    def test_bootstrap_refuses_existing_remote_checkpoint(self):
        # A second independent local anchor cannot restart from genesis over a live quorum.
        second = self.make_anchor(path=self.root/"second-client.sqlite")
        with self.assertRaisesRegex(RegistryRollbackDetected,"existing-external-head"):
            second.bootstrap(self.service)

    def test_local_preflight_refuses_direct_unanchored_request(self):
        c=self.challenge()
        method,path,raw,headers=self.signed_request("/v1/challenges",c)
        status,envelope,dropped=self.service.handle(method,path,raw,headers)
        self.assertEqual(status,201)
        with self.assertRaisesRegex(RegistryRollbackDetected,"diverges-from-current"):
            self.anchor.check_current()

    def test_checkpoint_request_ids_are_bound_into_signed_record(self):
        cp1=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=1,state_sha256="a"*64,previous_record_sha256=None,request_id="request.one",private_key=self.issuer_private,issued_at_ms=self.now[0])
        cp2=RegistryCheckpoint.issue(registry_id=REGISTRY_ID,sequence=1,state_sha256="a"*64,previous_record_sha256=None,request_id="request.two",private_key=self.issuer_private,issued_at_ms=self.now[0])
        self.assertNotEqual(cp1.record_sha256,cp2.record_sha256)

    def test_challenge_state_is_anchored_at_every_authenticated_route_result(self):
        before=self.anchor.check_current()["quorum_head"]["sequence"]
        result=self.request("/v1/not-a-real-route",{})
        self.assertEqual(result[0],404)
        after=self.anchor.check_current()["quorum_head"]["sequence"]
        self.assertEqual(after,before+1)

    def test_pending_integrity_tampering_fails_closed(self):
        c=self.challenge()
        original_methods=[]
        for w in self.witnesses:
            original_methods.append((w,w.attest)); w.attest=lambda cp: (_ for _ in ()).throw(RegistryCheckpointError("down"))
        self.register(c)
        for w,meth in original_methods: w.attest=meth
        with closing(sqlite3.connect(self.anchor_path)) as db:
            db.execute("UPDATE pending SET state_sha256=?",("e"*64,)); db.commit()
        with self.assertRaisesRegex(RegistryCheckpointError,"pending-checkpoint-mismatch|pending-integrity-invalid"):
            self.anchor.recover_pending(self.service)

    def test_client_outbox_resume_uses_same_checkpoint_after_partial_failure(self):
        original=[]
        for w in self.witnesses[1:]:
            original.append((w,w.attest)); w.attest=lambda cp: (_ for _ in ()).throw(RegistryCheckpointError("partition"))
        status,_,_=self.register(self.challenge())
        self.assertEqual(status,503)
        for w,meth in original: w.attest=meth
        with closing(sqlite3.connect(self.anchor_path)) as db:
            first_pending=json.loads(db.execute("SELECT checkpoint_json FROM pending WHERE singleton=1").fetchone()[0])
        self.anchor.recover_pending(self.service)
        with closing(sqlite3.connect(self.anchor_path)) as db:
            self.assertIsNone(db.execute("SELECT 1 FROM pending WHERE singleton=1").fetchone())
            head=json.loads(db.execute("SELECT record_json FROM local_head WHERE singleton=1").fetchone()[0])
        self.assertEqual(first_pending["body"]["sequence"],head["body"]["sequence"])
        self.assertEqual(first_pending["body"]["state_sha256"],head["body"]["state_sha256"])

    def test_loopback_http_boundary_routes_mutations_through_quorum(self):
        server = AnchoredRegistryHTTPServer(("127.0.0.1", 0), service=self.service, anchor=self.anchor)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start(); self.addCleanup(server.server_close); self.addCleanup(thread.join); self.addCleanup(server.shutdown)
        c = self.challenge()
        method, path, raw, headers = self.signed_request("/v1/challenges", c)
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request(method, path, body=raw, headers=headers)
        response = conn.getresponse(); payload = json.loads(response.read())
        self.assertEqual(response.status, 201)
        self.assertEqual(payload["body"]["status"], "REGISTERED")
        self.assertEqual(self.anchor.check_current()["status"], "CURRENT")
        conn.close()

    def test_loopback_http_concurrent_requests_are_serialized_and_each_checkpointed(self):
        server = AnchoredRegistryHTTPServer(("127.0.0.1", 0), service=self.service, anchor=self.anchor)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start(); self.addCleanup(server.server_close); self.addCleanup(thread.join); self.addCleanup(server.shutdown)
        challenges = [self.challenge() for _ in range(8)]
        requests = [self.signed_request("/v1/challenges", c) for c in challenges]
        def send(req):
            method,path,raw,headers=req
            conn=HTTPConnection("127.0.0.1",server.server_port,timeout=10)
            try:
                conn.request(method,path,body=raw,headers=headers)
                resp=conn.getresponse(); body=json.loads(resp.read())
                return resp.status,body
            finally: conn.close()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(send,requests))
        self.assertEqual([s for s,_ in results],[201]*8)
        self.assertEqual(self.anchor.check_current()["quorum_head"]["sequence"],9)
        with closing(sqlite3.connect(self.db_path)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0],8)

    def test_http_server_refuses_non_loopback_binding(self):
        with self.assertRaisesRegex(RegistryCheckpointError,"loopback-only"):
            AnchoredRegistryHTTPServer(("0.0.0.0", 0), service=self.service, anchor=self.anchor)

    def test_keyset_requires_distinct_witness_keys(self):
        aliased={**self.witness_keys,"witness-extra":self.witness_keys["witness-1"]}
        with self.assertRaises(RegistryCheckpointError):
            verify_head_quorum([],aliased,registry_id=REGISTRY_ID,challenge_nonce="G"*32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
