"""Loopback-only end-to-end smoke: signed test event -> queue -> trusted read-only worker."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import hmac
import json
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from operation_ledger import TrustedOperationLedger
from reconciliation_worker import TrustedReconciliationWorker
from stripe_webhook_inbox import StripeWebhookInbox
from webhook_http_receiver import loopback_receiver

SECRET = "whsec_v28_loopback_only_test_secret"
KEY = b"v28-loopback-test-integrity-key-material-32-bytes-min"
OP = "op_v28_smoke_001"
EVENT = "evt_v28_smoke_001"
REFUND = "re_v28_smoke_001"
CHARGE = "ch_v28_smoke_001"
PI = "pi_v28_smoke_001"

class LocalProvider:
    account_scope = "platform"
    livemode = False
    def retrieve_refund(self, refund_id):
        if refund_id != REFUND:
            raise LookupError("unregistered refund id")
        return {
            "object": "refund", "id": REFUND, "status": "succeeded",
            "charge": CHARGE, "payment_intent": PI, "amount": 2500,
            "currency": "usd", "livemode": False,
            "metadata": {"lycheetah_operation_id": OP},
            "description": "not persisted", "client_secret": "not persisted",
        }

def main():
    now = datetime.now(timezone.utc)
    ts = int(now.timestamp())
    event = {
        "id": EVENT, "object": "event", "type": "refund.updated", "created": ts - 2,
        "livemode": False, "data": {"object": {
            "object": "refund", "id": REFUND, "charge": CHARGE, "payment_intent": PI,
            "amount": 2500, "currency": "usd", "status": "pending", "livemode": False,
            "metadata": {"lycheetah_operation_id": OP, "private_note": "must not persist"},
        }},
    }
    raw = json.dumps(event, separators=(",", ":")).encode()
    signature = hmac.new(SECRET.encode(), str(ts).encode() + b"." + raw, hashlib.sha256).hexdigest()
    header = f"t={ts},v1={signature}"
    with tempfile.TemporaryDirectory(prefix="lycheetah-r18-smoke-") as td:
        path = str(Path(td) / "local.sqlite")
        inbox = StripeWebhookInbox(path=path, integrity_key=KEY,
            endpoint_secrets={"test": SECRET}, timestamp_tolerance_seconds=300)
        ledger = TrustedOperationLedger(path=path, integrity_key=KEY)
        ledger.register_operation(operation_id=OP, account_scope="platform", target_type="charge",
            target_id=CHARGE, amount=2500, currency="usd")
        with loopback_receiver(inbox) as url:
            req = Request(url, data=raw, method="POST", headers={
                "Content-Type": "application/json", "Content-Length": str(len(raw)),
                "Stripe-Signature": header,
            })
            with urlopen(req, timeout=5) as response:
                http_status = response.status
                ingest_body = json.loads(response.read().decode())
        worker = TrustedReconciliationWorker(inbox=inbox, ledger=ledger, provider=LocalProvider(),
            worker_id="r18-smoke-worker")
        worker_results = [x.to_dict() for x in worker.run_once(limit=5)]
        ledger_state = ledger.get_operation(OP)["state"]
        queue_state = inbox.get_reconciliation_job(EVENT)["state"]
        result = {
            "http_status": http_status,
            "ingest_action": ingest_body.get("action"),
            "worker_results": worker_results,
            "ledger_state": ledger_state,
            "queue_state": queue_state,
            "hosted_provider_calls": 0,
            "real_refunds_created": 0,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        assert http_status == 200
        assert ingest_body.get("action") == "INGESTED"
        assert worker_results and worker_results[0]["action"] == "RECONCILED"
        assert ledger_state == "PROVIDER_SUCCEEDED"
        assert queue_state == "DONE"

if __name__ == "__main__":
    main()
