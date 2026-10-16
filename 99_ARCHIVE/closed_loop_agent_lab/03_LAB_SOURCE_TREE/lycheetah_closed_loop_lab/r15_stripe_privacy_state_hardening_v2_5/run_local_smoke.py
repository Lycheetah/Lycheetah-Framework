"""Smoke only the local simulator; never calls Stripe's hosted API."""
from datetime import datetime, timedelta, timezone
import json
import tempfile
from pathlib import Path

from stripe_contract_simulator import StripeContractSimulator
from stripe_test_adapter import Action, DurableOperationStore, StripeTestModeRefundClient

now = datetime.now(timezone.utc)
with tempfile.TemporaryDirectory(prefix="lycheetah-stripe-testmode-") as td:
    store = DurableOperationStore(str(Path(td) / "ops.sqlite"),
                                  integrity_key=b"smoke-test-only-key-do-not-deploy-32bytes")
    with StripeContractSimulator() as provider:
        client = StripeTestModeRefundClient(
            store=store, secret_key="sk_test_local_mock", base_url=provider.url,
            account_scope="platform:acct_demo", api_version="2025-09-30.clover",
            allow_loopback_http=True, allow_test_clock_override=True, timeout_seconds=0.5,
        )
        client.prepare_refund(operation_id="smoke_op_001", idempotency_key="lyc-smoke-key-001",
                              created_at=now, charge="ch_test_smoke", amount=1200,
                              reason="requested_by_customer", expected_currency="usd")
        provider.fail_next("drop_after_commit")
        first = client.dispatch("smoke_op_001", now=now)
        recovered = client.recover("smoke_op_001", now=now + timedelta(seconds=2))
        summary = {
            "test_mode_only": True,
            "provider": "local simulator on loopback",
            "first_action": first.action.value,
            "recovery_action": recovered.action.value,
            "provider_effect_count": provider.effect_count,
            "provider_post_calls": provider.post_calls,
            "persisted_state": store.get("smoke_op_001")["state"],
        }
        print(json.dumps(summary, indent=2))
        assert first.action == Action.RECONCILE
        assert recovered.action == Action.SUCCEEDED
        assert provider.effect_count == 1
