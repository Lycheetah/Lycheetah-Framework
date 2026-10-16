"""Loopback-only HTTP receiver used to integration-test StripeWebhookInbox.

This is deliberately a test harness, not a production server. Production routing
should use a supported web framework and official Stripe SDK signature helper,
while preserving the exact raw request body until signature verification.
"""
from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from typing import Iterator

from stripe_webhook_inbox import InboxAction, MAX_WEBHOOK_BODY_BYTES, StripeWebhookInbox


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _handler_for(inbox: StripeWebhookInbox):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format, *args):  # Do not log raw bodies or signature headers.
            return

        def _reply(self, status: int, payload: dict):
            raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("ascii")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            self._reply(405, {"error": "method-not-allowed"})

        def do_POST(self):
            if self.path != "/webhook":
                self._reply(404, {"error": "not-found"})
                return
            if self.headers.get("Transfer-Encoding") is not None:
                self._reply(400, {"error": "transfer-encoding-not-supported-by-test-receiver"})
                return
            lengths = self.headers.get_all("Content-Length", [])
            # Duplicate Content-Length headers are ambiguous framing even when
            # their values agree. Reject rather than rely on parser-specific
            # first/last-header behavior.
            if len(lengths) > 1:
                self._reply(400, {"error": "duplicate-content-length-rejected"})
                return
            value = lengths[0] if lengths else None
            if value is None or not value.isascii() or not value.isdigit():
                self._reply(411, {"error": "content-length-required"})
                return
            length = int(value)
            if length <= 0:
                self._reply(400, {"error": "empty-body"})
                return
            if length > MAX_WEBHOOK_BODY_BYTES:
                self._reply(413, {"error": "payload-too-large"})
                return
            try:
                raw = self.rfile.read(length)
            except OSError:
                self._reply(400, {"error": "body-read-failed"})
                return
            if len(raw) != length:
                self._reply(400, {"error": "body-length-mismatch"})
                return
            signature = self.headers.get("Stripe-Signature", "")
            result = inbox.ingest(raw, signature)
            body = result.to_dict()
            if result.action in {InboxAction.INGESTED, InboxAction.DUPLICATE}:
                self._reply(200, body)
            elif result.reason in {"inbox-durable-write-failed", "inbox-record-authentication-failed"}:
                self._reply(503, body)
            else:
                self._reply(400, body)

    return Handler


@contextmanager
def loopback_receiver(inbox: StripeWebhookInbox) -> Iterator[str]:
    """Run the test receiver on ephemeral 127.0.0.1 only."""
    server = _Server(("127.0.0.1", 0), _handler_for(inbox))
    thread = threading.Thread(target=server.serve_forever, name="stripe-webhook-test-receiver", daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/webhook"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
