"""Loopback HTTP smoke for the signed webhook inbox; no hosted Stripe requests."""
from __future__ import annotations
import hashlib
import hmac
import http.client
import json
from datetime import datetime, timezone
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from stripe_webhook_inbox import StripeWebhookInbox
from webhook_http_receiver import loopback_receiver

SECRET = "whsec_local_smoke_secret_only"
INTEGRITY_KEY = b"local-smoke-integrity-key-32-bytes-minimum-00"

def signed(raw: bytes, timestamp: int) -> str:
    message = str(timestamp).encode("ascii") + b"." + raw
    sig = hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"

def post(url: str, raw: bytes, signature: str):
    parsed = urlsplit(url)
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=2)
    try:
        conn.request("POST", parsed.path, body=raw,
                     headers={"Stripe-Signature": signature,
                              "Content-Type": "application/json"})
        response = conn.getresponse()
        return response.status, json.loads(response.read().decode("utf-8"))
    finally:
        conn.close()

now = int(datetime.now(timezone.utc).timestamp())
body = json.dumps({
    "id": "evt_smoke_001", "object": "event", "type": "refund.updated",
    "created": now, "livemode": False,
    "data": {"object": {
        "id": "re_smoke_001", "object": "refund", "charge": "ch_smoke_001",
        "payment_intent": "pi_smoke_001", "amount": 1200, "currency": "usd",
        "status": "succeeded", "livemode": False,
        "metadata": {"lycheetah_operation_id": "op_smoke_001",
                      "extra_private_note": "NEVER_PERSIST_THIS"},
        "description": "PRIVATE_TEST_DESCRIPTION",
    }}
}, separators=(",", ":")).encode("utf-8")

with tempfile.TemporaryDirectory() as td:
    inbox = StripeWebhookInbox(path=str(Path(td) / "inbox.sqlite"),
        integrity_key=INTEGRITY_KEY, endpoint_secrets={"smoke": SECRET})
    with loopback_receiver(inbox) as url:
        first = post(url, body, signed(body, now))
        second = post(url, body, signed(body, now))
    hint = inbox.reconciliation_hint(operation_id="op_smoke_001",
        expected_target="ch_smoke_001", expected_amount=1200, expected_currency="usd")
    with inbox._db() as db:
        row_dump = " ".join(str(row) for row in db.execute("SELECT * FROM stripe_webhook_inbox").fetchall())
    assert first[0] == 200 and first[1]["action"] == "INGESTED"
    assert second[0] == 200 and second[1]["action"] == "DUPLICATE"
    assert hint.action.value == "RETRIEVE_CURRENT_PROVIDER_STATE"
    assert "NEVER_PERSIST_THIS" not in row_dump and "PRIVATE_TEST_DESCRIPTION" not in row_dump
    result = {
        "receiver": "loopback-only test HTTP receiver",
        "first_status": first[0], "first_action": first[1]["action"],
        "duplicate_status": second[0], "duplicate_action": second[1]["action"],
        "reconciliation_action": hint.action.value,
        "refund_id_for_current_state_retrieval": hint.refund_id,
        "sensitive_raw_fields_persisted": False,
        "hosted_stripe_requests": 0,
        "real_refunds": 0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
