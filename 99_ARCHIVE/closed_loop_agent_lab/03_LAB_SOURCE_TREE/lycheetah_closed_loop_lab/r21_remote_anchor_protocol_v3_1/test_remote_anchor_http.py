import base64
from contextlib import closing
from datetime import timedelta
import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from remote_anchor_http import (
    AnchorHTTPServer, AnchorProtocolError, AnchorTransportError, OperatorApproval,
    PublishOutbox, RemoteAnchorClient, RemoteAnchorPublisher, RemoteAnchorService,
    canonical, make_snapshot, sha256, utc_now, verify_record,
)


CLIENT_KEY = b"client-key-v31-" + b"c" * 32
OUTBOX_KEY = b"outbox-key-v31-" + b"o" * 32
DATABASE_ID = "lycheetah.operations.main"
CLIENT_KEY_ID = "worker-api-v1"
SERVER_KEY_ID = "anchor-signer-v1"
OPERATOR_KEY_ID = "operations-approval-v1"


def request_id() -> str:
    return "req_" + uuid.uuid4().hex


def nonce() -> str:
    return "nonce_" + uuid.uuid4().hex


class RemoteAnchorHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lyc-anchor-v31-")
        self.root = Path(self.tmp.name)
        self.operator_private = Ed25519PrivateKey.generate()
        self.server_private = Ed25519PrivateKey.generate()
        self.service_db = self.root / "anchor.sqlite"
        self.outbox_db = self.root / "outbox.sqlite"
        self.service = RemoteAnchorService(
            self.service_db,
            api_keys={CLIENT_KEY_ID: CLIENT_KEY},
            operator_keys={OPERATOR_KEY_ID: self.operator_private.public_key()},
            server_key_id=SERVER_KEY_ID,
            server_private_key=self.server_private,
        )
        self.httpd = AnchorHTTPServer(("127.0.0.1", 0), self.service)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.client = RemoteAnchorClient(
            self.base_url, client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
            server_keys={SERVER_KEY_ID: self.server_private.public_key()},
            server_key_id=SERVER_KEY_ID, allow_http_loopback=True,
        )
        self.outbox = PublishOutbox(self.outbox_db, integrity_key=OUTBOX_KEY)
        self.publisher = RemoteAnchorPublisher(self.client, self.outbox)
        self.snapshot = make_snapshot("a" * 64, "b" * 64, {"events": 2, "operations": 1}, {"signed": 3})

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=3)
        self.tmp.cleanup()

    def issue(self, *, rid=None, snapshot=None, seq=0, head=None, issued_at=None, expires_at=None, signer_key_id=OPERATOR_KEY_ID):
        rid = rid or request_id()
        return rid, OperatorApproval.issue(
            private_key=self.operator_private, signer_key_id=signer_key_id,
            approval_id="approval_" + uuid.uuid4().hex,
            nonce=nonce(), request_id=rid, database_id=DATABASE_ID,
            expected_sequence=seq, expected_head_sha256=head,
            snapshot=snapshot or self.snapshot, reason_code="approved.state.change",
            issued_at=issued_at, expires_at=expires_at,
        )

    def prepare(self, *, rid=None, snapshot=None, seq=0, head=None, issued_at=None, expires_at=None, signer_key_id=OPERATOR_KEY_ID, outbox=None):
        rid, approval = self.issue(rid=rid, snapshot=snapshot, seq=seq, head=head,
                                   issued_at=issued_at, expires_at=expires_at, signer_key_id=signer_key_id)
        (outbox or self.outbox).prepare(rid, DATABASE_ID, snapshot or self.snapshot, approval.to_dict())
        return rid, approval

    def test_happy_path_publishes_one_signed_record(self):
        rid, _ = self.prepare()
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        status, history = self.client.history(DATABASE_ID)
        self.assertEqual(status, 200)
        self.assertEqual(len(history["records"]), 1)
        verified = verify_record(history["records"][0], self.client.server_keys,
                                 expected_previous=None, expected_sequence=1,
                                 expected_database_id=DATABASE_ID)
        self.assertEqual(verified.body["request_id"], rid)

    def test_lost_response_after_commit_is_reconciled_by_request_lookup(self):
        rid, _ = self.prepare()
        self.service.drop_after_commit_count = 1
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        self.assertIn("authoritative-request-lookup", result.response_json)
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_lost_response_before_commit_retries_same_request_id(self):
        rid, _ = self.prepare()
        self.service.drop_before_count = 1
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_ambiguous_post_and_unavailable_lookup_remains_unknown_then_recovers(self):
        rid, _ = self.prepare()
        self.service.drop_before_count = 1
        self.service.fail_lookup_count = 1
        first = self.publisher.publish_or_resume(rid)
        self.assertEqual(first.state, "UNKNOWN")
        second = self.publisher.publish_or_resume(rid)
        self.assertEqual(second.state, "COMMITTED")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_lost_commit_and_unavailable_lookup_then_resend_same_key_is_idempotent(self):
        rid, _ = self.prepare()
        self.service.drop_after_commit_count = 1
        self.service.fail_lookup_count = 1
        first = self.publisher.publish_or_resume(rid)
        self.assertEqual(first.state, "UNKNOWN")
        second = self.publisher.publish_or_resume(rid)
        self.assertEqual(second.state, "COMMITTED")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_unknown_resumption_queries_status_before_any_new_post(self):
        rid, _ = self.prepare()
        self.service.drop_before_count = 1
        self.service.fail_lookup_count = 1
        self.assertEqual(self.publisher.publish_or_resume(rid).state, "UNKNOWN")
        # If status lookup is still unavailable, resume remains UNKNOWN and does not POST.
        self.service.fail_lookup_count = 1
        second = self.publisher.publish_or_resume(rid)
        self.assertEqual(second.state, "UNKNOWN")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 0)
        # Once lookup works and says NOT_FOUND, the stable request can be safely retried.
        third = self.publisher.publish_or_resume(rid)
        self.assertEqual(third.state, "COMMITTED")

    def test_remote_service_restart_recovers_committed_append_from_durable_request_index(self):
        rid, _ = self.prepare()
        self.service.drop_after_commit_count = 1
        self.service.fail_lookup_count = 1
        self.assertEqual(self.publisher.publish_or_resume(rid).state, "UNKNOWN")
        old_httpd = self.httpd
        old_httpd.shutdown()
        old_httpd.server_close()
        self.thread.join(timeout=3)
        # Re-open the same durable service database with the same pinned server key.
        self.service = RemoteAnchorService(
            self.service_db, api_keys={CLIENT_KEY_ID: CLIENT_KEY},
            operator_keys={OPERATOR_KEY_ID: self.operator_private.public_key()},
            server_key_id=SERVER_KEY_ID, server_private_key=self.server_private,
        )
        self.httpd = AnchorHTTPServer(("127.0.0.1", 0), self.service)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.client = RemoteAnchorClient(
            self.base_url, client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
            server_keys={SERVER_KEY_ID: self.server_private.public_key()},
            server_key_id=SERVER_KEY_ID, allow_http_loopback=True,
        )
        self.publisher = RemoteAnchorPublisher(self.client, PublishOutbox(self.outbox_db, integrity_key=OUTBOX_KEY))
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_same_request_and_same_body_replays_exact_original_record(self):
        rid, _ = self.prepare()
        pending = self.outbox.load(rid)
        body = {"request_id": rid, "snapshot": dict(pending.snapshot), "approval": dict(pending.approval)}
        first_status, first = self.client.publish(DATABASE_ID, body)
        second_status, second = self.client.publish(DATABASE_ID, body)
        self.assertEqual((first_status, second_status), (200, 200))
        self.assertEqual(first["record"], second["record"])
        self.assertTrue(second["idempotent_replay"])

    def test_same_request_id_with_changed_body_is_conflict(self):
        rid, _ = self.prepare()
        pending = self.outbox.load(rid)
        self.publisher.publish_or_resume(rid)
        changed = make_snapshot("c" * 64, "d" * 64, {"events": 2}, {"signed": 1})
        _, approval = self.issue(rid=rid, snapshot=changed, seq=0, head=None)
        status, response = self.client.publish(DATABASE_ID, {"request_id": rid, "snapshot": changed, "approval": approval.to_dict()})
        self.assertEqual(status, 409)
        self.assertEqual(response["status"], "CONFLICT")

    def test_stale_parent_is_conflict_and_not_silently_rebased(self):
        rid1, _ = self.prepare()
        rid2, _ = self.prepare()
        self.assertEqual(self.publisher.publish_or_resume(rid1).state, "COMMITTED")
        conflict = self.publisher.publish_or_resume(rid2)
        self.assertEqual(conflict.state, "CONFLICT")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_expired_operator_approval_is_refused(self):
        now = utc_now()
        rid, _ = self.prepare(issued_at=now - timedelta(minutes=20), expires_at=now - timedelta(minutes=10))
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "CONFLICT")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 0)

    def test_untrusted_operator_key_id_is_refused(self):
        rid, _ = self.prepare(signer_key_id="not-trusted-v1")
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "CONFLICT")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 0)

    def test_modified_approval_signature_is_refused(self):
        rid, approval = self.issue()
        tampered = approval.to_dict()
        tampered["reason_code"] = "another.approval"
        self.outbox.prepare(rid, DATABASE_ID, self.snapshot, tampered)
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "CONFLICT")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 0)

    def test_malformed_approval_signature_encoding_is_refused_as_client_error(self):
        rid, approval = self.issue()
        tampered = approval.to_dict()
        tampered["signature_b64"] = "not!!base64"
        self.outbox.prepare(rid, DATABASE_ID, self.snapshot, tampered)
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "CONFLICT")
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 0)

    def test_database_identity_is_bound_by_approval(self):
        rid, approval = self.issue()
        with self.assertRaises(AnchorProtocolError):
            self.outbox.prepare(rid, "other.database.id", self.snapshot, approval.to_dict())
        # The signed approval is also rejected by the service if submitted under a different path.
        status, response = self.client.publish(
            "other.database.id",
            {"request_id": rid, "snapshot": self.snapshot, "approval": approval.to_dict()},
        )
        self.assertEqual(status, 422)
        self.assertEqual(response["error"], "approval-does-not-bind-request")

    def test_changed_snapshot_cannot_be_submitted_under_existing_approval(self):
        rid, approval = self.issue()
        changed = make_snapshot("c" * 64, "d" * 64, {"events": 99}, {"signed": 1})
        with self.assertRaises(AnchorProtocolError):
            self.outbox.prepare(rid, DATABASE_ID, changed, approval.to_dict())

    def test_response_body_tampering_is_detected_then_resolved_by_lookup(self):
        rid, _ = self.prepare()
        self.service.mutate_response_count = 1
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        self.assertIn("authoritative-request-lookup", result.response_json)

    def test_untrusted_server_public_key_is_refused_at_client_creation(self):
        with self.assertRaises(AnchorProtocolError):
            RemoteAnchorClient(self.base_url, client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
                               server_keys={}, server_key_id=SERVER_KEY_ID, allow_http_loopback=True)

    def test_non_loopback_plain_http_is_refused(self):
        with self.assertRaises(AnchorProtocolError):
            RemoteAnchorClient("http://example.com", client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
                               server_keys={SERVER_KEY_ID: self.server_private.public_key()},
                               server_key_id=SERVER_KEY_ID, allow_http_loopback=True)

    def test_http_loopback_must_be_explicitly_enabled(self):
        with self.assertRaises(AnchorProtocolError):
            RemoteAnchorClient(self.base_url, client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
                               server_keys={SERVER_KEY_ID: self.server_private.public_key()},
                               server_key_id=SERVER_KEY_ID)

    def test_client_does_not_follow_redirect_with_authenticated_request(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        sink_hits = []
        class Sink(BaseHTTPRequestHandler):
            def do_GET(self):
                sink_hits.append(self.path)
                payload = b"ok"
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *_):
                return
        sink = ThreadingHTTPServer(("127.0.0.1", 0), Sink)
        sink_thread = threading.Thread(target=sink.serve_forever, daemon=True)
        sink_thread.start()
        sink_url = f"http://127.0.0.1:{sink.server_address[1]}/sink"
        class Redirector(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", sink_url)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
            def log_message(self, *_):
                return
        redirector = ThreadingHTTPServer(("127.0.0.1", 0), Redirector)
        redirect_thread = threading.Thread(target=redirector.serve_forever, daemon=True)
        redirect_thread.start()
        try:
            redirected_client = RemoteAnchorClient(
                f"http://127.0.0.1:{redirector.server_address[1]}",
                client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
                server_keys={SERVER_KEY_ID: self.server_private.public_key()},
                server_key_id=SERVER_KEY_ID, allow_http_loopback=True,
            )
            with self.assertRaises(AnchorProtocolError):
                redirected_client.history(DATABASE_ID)
            self.assertEqual(sink_hits, [])
        finally:
            redirector.shutdown(); redirector.server_close(); redirect_thread.join(timeout=2)
            sink.shutdown(); sink.server_close(); sink_thread.join(timeout=2)

    def test_outbox_row_tampering_is_detected(self):
        rid, _ = self.prepare()
        with closing(sqlite3.connect(self.outbox_db)) as db:
            db.execute("UPDATE publish_outbox SET state='COMMITTED' WHERE request_id=?", (rid,))
            db.commit()
        with self.assertRaises(AnchorProtocolError):
            self.outbox.load(rid)

    def test_outbox_survives_reopen_and_can_resume(self):
        rid, _ = self.prepare()
        reopened = PublishOutbox(self.outbox_db, integrity_key=OUTBOX_KEY)
        result = RemoteAnchorPublisher(self.client, reopened).publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")

    def test_outbox_request_id_cannot_be_reused_with_new_content(self):
        rid, _ = self.prepare()
        changed = make_snapshot("e" * 64, "f" * 64, {"events": 1}, {"signed": 1})
        _, approval = self.issue(rid=rid, snapshot=changed)
        with self.assertRaises(AnchorProtocolError):
            self.outbox.prepare(rid, DATABASE_ID, changed, approval.to_dict())

    def test_committed_outbox_state_is_terminal(self):
        rid, _ = self.prepare()
        self.publisher.publish_or_resume(rid)
        with self.assertRaises(AnchorProtocolError):
            self.outbox.set_state(rid, "UNKNOWN")

    def test_committed_outbox_response_cannot_be_rewritten_in_terminal_state(self):
        rid, _ = self.prepare()
        self.publisher.publish_or_resume(rid)
        with self.assertRaises(AnchorProtocolError):
            self.outbox.set_state(rid, "COMMITTED", {"status": "fabricated"})

    def test_conflict_outbox_state_is_terminal(self):
        rid, _ = self.prepare(issued_at=utc_now() - timedelta(minutes=20), expires_at=utc_now() - timedelta(minutes=10))
        self.publisher.publish_or_resume(rid)
        with self.assertRaises(AnchorProtocolError):
            self.outbox.set_state(rid, "PENDING")

    def test_header_authentication_is_case_insensitive_at_http_boundary(self):
        path = f"/v1/databases/{DATABASE_ID}/history"
        timestamp = str(int(time.time()))
        request_nonce = nonce()
        body = b""
        signed = {"method": "GET", "path": path, "timestamp": timestamp,
                  "nonce": request_nonce, "body_sha256": sha256(body)}
        sig = hmac.new(CLIENT_KEY, canonical(signed), hashlib.sha256).hexdigest()
        headers = {"x-anchor-key-id": CLIENT_KEY_ID, "x-anchor-timestamp": timestamp,
                   "x-anchor-nonce": request_nonce, "x-anchor-signature": sig}
        status, response, drop = self.service.handle("GET", path, body, headers)
        self.assertFalse(drop)
        self.assertEqual(status, 200)
        self.assertIsNotNone(response)

    def test_auth_request_nonce_replay_is_rejected(self):
        path = f"/v1/databases/{DATABASE_ID}/history"
        timestamp = str(int(time.time()))
        request_nonce = nonce()
        signed = {"method": "GET", "path": path, "timestamp": timestamp,
                  "nonce": request_nonce, "body_sha256": sha256(b"")}
        headers = {"X-Anchor-Key-Id": CLIENT_KEY_ID, "X-Anchor-Timestamp": timestamp,
                   "X-Anchor-Nonce": request_nonce,
                   "X-Anchor-Signature": hmac.new(CLIENT_KEY, canonical(signed), hashlib.sha256).hexdigest()}
        status1, _, _ = self.service.handle("GET", path, b"", headers)
        status2, response2, _ = self.service.handle("GET", path, b"", headers)
        self.assertEqual(status1, 200)
        self.assertEqual(status2, 401)
        self.assertEqual(response2["body"]["error"], "client-request-replay")

    def test_history_verification_rejects_record_body_mutation(self):
        rid, _ = self.prepare()
        self.publisher.publish_or_resume(rid)
        with closing(sqlite3.connect(self.service_db)) as db:
            db.execute("DROP TRIGGER checkpoints_no_update")
            row = db.execute("SELECT record_json FROM checkpoints WHERE database_id=?", (DATABASE_ID,)).fetchone()
            value = json.loads(row[0])
            value["body"]["reason_code"] = "mutated.reason"
            db.execute("UPDATE checkpoints SET record_json=? WHERE database_id=?", (json.dumps(value), DATABASE_ID))
            db.commit()
        with self.assertRaises(AnchorProtocolError):
            self.client.history(DATABASE_ID)

    def test_append_refuses_to_extend_tampered_existing_history(self):
        rid, _ = self.prepare()
        self.publisher.publish_or_resume(rid)
        with closing(sqlite3.connect(self.service_db)) as db:
            db.execute("DROP TRIGGER checkpoints_no_update")
            row = db.execute("SELECT record_json FROM checkpoints WHERE database_id=?", (DATABASE_ID,)).fetchone()
            value = json.loads(row[0])
            value["body"]["reason_code"] = "mutated.reason"
            db.execute("UPDATE checkpoints SET record_json=? WHERE database_id=?", (json.dumps(value), DATABASE_ID))
            db.commit()
        rid2, _ = self.prepare(seq=1, head="0" * 64)
        result = self.publisher.publish_or_resume(rid2)
        self.assertNotEqual(result.state, "COMMITTED")

    def test_orphaned_idempotency_index_cannot_masquerade_as_committed(self):
        rid, _ = self.prepare()
        self.assertEqual(self.publisher.publish_or_resume(rid).state, "COMMITTED")
        pending = self.outbox.load(rid)
        body = {"request_id": rid, "snapshot": dict(pending.snapshot), "approval": dict(pending.approval)}
        # Simulate out-of-band storage corruption that removes the chain row but leaves
        # the idempotency/request index. Replay must validate the entire chain first.
        with closing(sqlite3.connect(self.service_db)) as db:
            db.execute("DROP TRIGGER checkpoints_no_delete")
            db.execute("DROP TRIGGER approvals_no_delete")
            db.execute("DELETE FROM checkpoints WHERE database_id=? AND request_id=?", (DATABASE_ID, rid))
            db.execute("DELETE FROM approvals_used WHERE database_id=?", (DATABASE_ID,))
            db.commit()
        status, response = self.client.publish(DATABASE_ID, body)
        self.assertEqual(status, 503)
        self.assertEqual(response["error"], "anchor-request-index-has-orphan-or-missing-record")

    def test_concurrent_competing_cas_appends_have_one_winner(self):
        rid1, _ = self.prepare()
        rid2, _ = self.prepare()
        results = []
        barrier = threading.Barrier(2)
        def run(rid):
            barrier.wait()
            results.append(self.publisher.publish_or_resume(rid).state)
        a = threading.Thread(target=run, args=(rid1,))
        b = threading.Thread(target=run, args=(rid2,))
        a.start(); b.start(); a.join(timeout=10); b.join(timeout=10)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertCountEqual(results, ["COMMITTED", "CONFLICT"])
        self.assertEqual(len(self.client.history(DATABASE_ID)[1]["records"]), 1)

    def test_bad_service_request_auth_is_denied(self):
        path = f"/v1/databases/{DATABASE_ID}/history"
        status, response, drop = self.service.handle("GET", path, b"", {})
        self.assertFalse(drop)
        self.assertEqual(status, 401)
        self.assertEqual(response["body"]["error"], "client-authentication-invalid")

    def test_service_history_and_request_results_are_signed(self):
        rid, _ = self.prepare()
        result = self.publisher.publish_or_resume(rid)
        self.assertEqual(result.state, "COMMITTED")
        status, req_status = self.client.request_status(DATABASE_ID, rid)
        self.assertEqual(status, 200)
        self.assertEqual(req_status["status"], "FOUND")
        self.assertEqual(req_status["request_sha256"], self.outbox.load(rid).request_sha256)

    def test_bad_database_id_is_refused_by_outbox(self):
        rid, approval = self.issue()
        with self.assertRaises(AnchorProtocolError):
            self.outbox.prepare(rid, "bad database id!", self.snapshot, approval.to_dict())

    def test_logical_snapshot_digest_must_bind_components(self):
        bad = {**self.snapshot, "logical_sha256": "0" * 64}
        rid, approval = self.issue(snapshot=self.snapshot)
        with self.assertRaises(AnchorProtocolError):
            self.outbox.prepare(rid, DATABASE_ID, bad, approval.to_dict())

    def test_no_anchor_history_is_empty_and_signed(self):
        status, payload = self.client.history(DATABASE_ID)
        self.assertEqual(status, 200)
        self.assertEqual(payload["records"], [])

    def test_http_server_rejects_oversized_body_before_json_parse(self):
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_address[1], timeout=3)
        try:
            conn.putrequest("POST", f"/v1/databases/{DATABASE_ID}/checkpoints")
            conn.putheader("Content-Length", "1000001")
            conn.putheader("Content-Type", "application/json")
            conn.endheaders()  # Deliberately declare a large body without transmitting it.
            response = conn.getresponse()
            self.assertEqual(response.status, 413)
            outer = json.loads(response.read().decode("utf-8"))
            self.assertEqual(outer["body"]["error"], "request-body-size-invalid")
        finally:
            conn.close()

    def test_service_rejects_invalid_public_key_registry(self):
        with self.assertRaises(AnchorProtocolError):
            RemoteAnchorService(self.root / "bad-service.sqlite", api_keys={CLIENT_KEY_ID: CLIENT_KEY},
                                operator_keys={OPERATOR_KEY_ID: b"not-a-public-key"},
                                server_key_id=SERVER_KEY_ID, server_private_key=self.server_private)

    def test_client_rejects_nonpositive_timeout(self):
        with self.assertRaises(AnchorProtocolError):
            RemoteAnchorClient(self.base_url, client_key_id=CLIENT_KEY_ID, client_key=CLIENT_KEY,
                               server_keys={SERVER_KEY_ID: self.server_private.public_key()},
                               server_key_id=SERVER_KEY_ID, timeout_seconds=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
