from __future__ import annotations

from contextlib import closing

import hashlib
import hmac
import http.client
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from stripe_webhook_inbox import StripeWebhookInbox
from webhook_http_receiver import loopback_receiver
from test_stripe_webhook_inbox import KEY, SECRET, TS, event_body, _sign


class WebhookHttpReceiverCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "inbox.sqlite")
        self.inbox = StripeWebhookInbox(
            path=self.db_path, integrity_key=KEY,
            endpoint_secrets={"current": SECRET},
            allow_test_clock_override=False,
        )
        self.server_context = loopback_receiver(self.inbox)
        self.url = self.server_context.__enter__()
        self.parsed = urlsplit(self.url)

    def tearDown(self):
        self.server_context.__exit__(None, None, None)
        self.temp.cleanup()

    def current_signature(self, raw):
        timestamp = int(datetime.now(timezone.utc).timestamp())
        return _sign(raw, timestamp=timestamp)

    def request(self, method="POST", path="/webhook", body=None, headers=None):
        conn = http.client.HTTPConnection(self.parsed.hostname, self.parsed.port, timeout=2)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8"))
        finally:
            conn.close()

    def test_valid_signed_http_event_is_durably_ingested(self):
        raw = event_body()
        status, result = self.request(body=raw, headers={"Stripe-Signature": self.current_signature(raw),
                                                          "Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(result["action"], "INGESTED")
        self.assertIsNotNone(self.inbox.get("evt_test_001"))

    def test_duplicate_http_delivery_returns_200_without_second_insert(self):
        raw = event_body()
        headers = {"Stripe-Signature": self.current_signature(raw), "Content-Type": "application/json"}
        first = self.request(body=raw, headers=headers)
        second = self.request(body=raw, headers=headers)
        self.assertEqual(first[0], 200)
        self.assertEqual(second[0], 200)
        self.assertEqual(second[1]["action"], "DUPLICATE")

    def test_tampered_raw_http_body_is_rejected(self):
        raw = event_body()
        signature = self.current_signature(raw)
        changed = raw.replace(b"2500", b"2501", 1)
        status, result = self.request(body=changed, headers={"Stripe-Signature": signature})
        self.assertEqual(status, 400)
        self.assertEqual(result["reason"], "signature-mismatch")

    def test_bad_path_is_not_processed(self):
        raw = event_body()
        status, _ = self.request(path="/webhook/", body=raw,
                                 headers={"Stripe-Signature": self.current_signature(raw)})
        self.assertEqual(status, 404)
        self.assertIsNone(self.inbox.get("evt_test_001"))

    def test_get_is_rejected(self):
        status, result = self.request(method="GET")
        self.assertEqual(status, 405)
        self.assertEqual(result["error"], "method-not-allowed")

    def test_missing_content_length_is_rejected(self):
        conn = http.client.HTTPConnection(self.parsed.hostname, self.parsed.port, timeout=2)
        try:
            conn.putrequest("POST", "/webhook")
            conn.putheader("Stripe-Signature", "t=123,v1=" + "0" * 64)
            conn.endheaders()
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            self.assertEqual(response.status, 411)
            self.assertEqual(data["error"], "content-length-required")
        finally:
            conn.close()

    def test_oversized_declared_content_length_is_rejected_before_read(self):
        from stripe_webhook_inbox import MAX_WEBHOOK_BODY_BYTES
        conn = http.client.HTTPConnection(self.parsed.hostname, self.parsed.port, timeout=2)
        try:
            conn.putrequest("POST", "/webhook")
            conn.putheader("Content-Length", str(MAX_WEBHOOK_BODY_BYTES + 1))
            conn.putheader("Stripe-Signature", "t=123,v1=" + "0" * 64)
            conn.endheaders()
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            self.assertEqual(response.status, 413)
            self.assertEqual(data["error"], "payload-too-large")
        finally:
            conn.close()

    def test_duplicate_content_length_is_rejected(self):
        conn = http.client.HTTPConnection(self.parsed.hostname, self.parsed.port, timeout=2)
        try:
            conn.putrequest("POST", "/webhook")
            conn.putheader("Content-Length", "2")
            conn.putheader("Content-Length", "2")
            conn.putheader("Stripe-Signature", "t=123,v1=" + "0" * 64)
            conn.endheaders()
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            self.assertEqual(response.status, 400)
            self.assertEqual(data["error"], "duplicate-content-length-rejected")
        finally:
            conn.close()

    def test_transfer_encoding_is_rejected(self):
        conn = http.client.HTTPConnection(self.parsed.hostname, self.parsed.port, timeout=2)
        try:
            conn.putrequest("POST", "/webhook")
            conn.putheader("Transfer-Encoding", "chunked")
            conn.putheader("Stripe-Signature", "t=123,v1=" + "0" * 64)
            conn.endheaders()
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            self.assertEqual(response.status, 400)
            self.assertEqual(data["error"], "transfer-encoding-not-supported-by-test-receiver")
        finally:
            conn.close()

    def test_response_does_not_echo_body_or_signature(self):
        raw = event_body()
        status, result = self.request(body=raw,
                                      headers={"Stripe-Signature": "t=" + str(int(datetime.now(timezone.utc).timestamp())) + ",v1=" + "0" * 64})
        self.assertEqual(status, 400)
        encoded = json.dumps(result)
        self.assertNotIn(SECRET, encoded)
        self.assertNotIn(raw.decode(), encoded)


    def test_queue_write_failure_returns_503_and_event_is_not_acked(self):
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute("""CREATE TRIGGER force_queue_failure BEFORE INSERT ON stripe_reconciliation_jobs
                          BEGIN SELECT RAISE(ABORT, 'synthetic queue write failure'); END""")
        raw = event_body()
        status, result = self.request(body=raw, headers={"Stripe-Signature": self.current_signature(raw),
                                                          "Content-Type": "application/json"})
        self.assertEqual(status, 503)
        self.assertEqual(result["reason"], "inbox-durable-write-failed")
        self.assertIsNone(self.inbox.get("evt_test_001"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
