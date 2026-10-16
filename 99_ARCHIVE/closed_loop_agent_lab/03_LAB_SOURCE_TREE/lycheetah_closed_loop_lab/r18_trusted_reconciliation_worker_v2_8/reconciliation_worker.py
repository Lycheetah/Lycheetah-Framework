"""Trusted current-state worker for the Lycheetah Stripe refund inbox (v2.8).

The worker is read-only against Stripe. It never creates or retries a refund.
Webhook status only queues reconciliation; provider GET data is validated,
minimized, and committed to the authenticated operation ledger before queue
acknowledgment. The matching inbox code enforces this invariant in the queue API.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Mapping, Protocol
from pathlib import Path

from operation_ledger import TrustedOperationLedger, OperationLedgerError, OperationLedgerIntegrityError
from stripe_webhook_inbox import (
    ReconciliationQueueError,
    StripeWebhookInbox,
)


class TransientProviderReadError(OSError):
    """A provider read failed in a way that can be safely retried as a GET."""


class ProviderNotFoundError(TransientProviderReadError):
    """The correlated refund may not yet be visible; never infer non-execution."""


class ProviderContractError(ValueError):
    """The provider adapter contract is incomplete or malformed."""


class ReadOnlyRefundProvider(Protocol):
    account_scope: str
    livemode: bool

    def retrieve_refund(self, refund_id: str) -> Mapping[str, Any]:
        """Retrieve current provider state; MUST perform no financial side effect."""


@dataclass(frozen=True)
class WorkerResult:
    event_id: str
    operation_id: str | None
    action: str
    reason: str
    ledger_state: str | None = None
    refund_status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "operation_id": self.operation_id,
            "action": self.action,
            "reason": self.reason,
            "ledger_state": self.ledger_state,
            "refund_status": self.refund_status,
        }


_TERMINAL = {"PROVIDER_SUCCEEDED", "PROVIDER_FAILED", "PROVIDER_CANCELED"}
_ALLOWED_STATUS = {"pending", "requires_action", "succeeded", "failed", "canceled"}


class TrustedReconciliationWorker:
    """Reconcile claimed inbox jobs to authenticated operation state.

    The provider object must be a trusted client already pinned to one account
    scope and test mode. The worker never trusts webhook `refund_status`.
    """
    def __init__(self, *, inbox: StripeWebhookInbox,
                 ledger: TrustedOperationLedger,
                 provider: ReadOnlyRefundProvider,
                 worker_id: str,
                 retry_after_seconds: int = 60):
        if not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", worker_id or ""):
            raise ValueError("worker_id is invalid")
        if type(retry_after_seconds) is not int or not 1 <= retry_after_seconds <= 86400:
            raise ValueError("retry_after_seconds is invalid")
        if Path(inbox.path).resolve() != Path(ledger.path).resolve():
            raise ValueError("inbox and operation ledger must share one SQLite database for DONE guard")
        if not hasattr(provider, "retrieve_refund") or not callable(provider.retrieve_refund):
            raise TypeError("provider must implement retrieve_refund(refund_id)")
        if not hasattr(provider, "account_scope") or not hasattr(provider, "livemode"):
            raise TypeError("provider must declare fixed account_scope and livemode")
        self.inbox = inbox
        self.ledger = ledger
        self.provider = provider
        self.worker_id = worker_id
        self.retry_after_seconds = retry_after_seconds

    def run_once(self, *, limit: int = 10, lease_seconds: int = 120,
                 now: datetime | None = None) -> list[WorkerResult]:
        kwargs: dict[str, Any] = {"worker_id": self.worker_id, "limit": limit,
                                  "lease_seconds": lease_seconds}
        if now is not None:
            kwargs["now"] = now
        claims = self.inbox.claim_reconciliation_jobs(**kwargs)
        return [self.process_claimed(job, now=now) for job in claims]

    def process_claimed(self, job: Mapping[str, Any], *,
                        now: datetime | None = None) -> WorkerResult:
        """Process one queue claim. No caller-supplied status is accepted."""
        if not isinstance(job, Mapping):
            raise TypeError("job must be a mapping")
        event_id = job.get("event_id")
        operation_id = job.get("operation_id")
        if not isinstance(event_id, str) or not re.fullmatch(r"evt_[A-Za-z0-9_]+", event_id):
            raise ValueError("job event_id is invalid")
        if not isinstance(job.get("claim_token"), str):
            raise ValueError("job claim token is missing")
        if not isinstance(operation_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", operation_id):
            return self._finish(job, "MANUAL", "missing-operation-correlation", now=now)

        try:
            op = self.ledger.get_operation(operation_id)
        except OperationLedgerIntegrityError:
            return self._finish(job, "MANUAL", "operation-ledger-authentication-failed", now=now)
        if op is None:
            return self._finish(job, "MANUAL", "operation-ledger-record-missing", now=now)

        expected_event_account = None if op["account_scope"] == "platform" else op["account_scope"]
        if (
            job.get("event_account") != expected_event_account
            or job.get("amount") != op["expected_amount"]
            or job.get("currency") != op["expected_currency"]
            or self._job_target(job, op) is False
        ):
            try:
                op = self.ledger.mark_manual(operation_id, "webhook-operation-binding-mismatch", now=now)
            except OperationLedgerError:
                pass
            return self._finish(job, "MANUAL", "webhook-operation-binding-mismatch", now=now,
                                ledger_state=(op or {}).get("state"))

        # Account/mode are properties of the configured provider client, not values
        # supplied by a webhook or worker call. Fail closed before any provider read.
        if self.provider.account_scope != op["account_scope"] or self.provider.livemode is not False:
            op = self.ledger.mark_manual(operation_id, "provider-client-scope-mismatch", now=now)
            return self._finish(job, "MANUAL", "provider-client-scope-mismatch", now=now,
                                ledger_state=op["state"])

        try:
            snapshot = self.provider.retrieve_refund(job["refund_id"])
        except ProviderNotFoundError:
            return self._finish(job, "RETRY", "provider-refund-not-yet-visible", now=now)
        except TransientProviderReadError:
            return self._finish(job, "RETRY", "provider-read-transient-failure", now=now)
        except Exception:
            # Never copy an exception message into durable logs; SDK errors can
            # contain request material. Unknown adapter failures route to manual.
            op = self.ledger.mark_manual(operation_id, "provider-adapter-contract-error", now=now)
            return self._finish(job, "MANUAL", "provider-adapter-contract-error", now=now,
                                ledger_state=op["state"])

        valid, reason = self._validate_snapshot(snapshot, job=job, op=op, operation_id=operation_id)
        if not valid:
            op = self.ledger.mark_manual(operation_id, reason, now=now)
            return self._finish(job, "MANUAL", reason, now=now,
                                ledger_state=op["state"], refund_status=snapshot.get("status") if isinstance(snapshot, Mapping) and isinstance(snapshot.get("status"), str) else None)

        op = self.ledger.record_provider_observation(
            operation_id=operation_id, event_id=event_id, snapshot={
                "id": snapshot.get("id"),
                "status": snapshot.get("status"),
                "charge": snapshot.get("charge"),
                "payment_intent": snapshot.get("payment_intent"),
                "amount": snapshot.get("amount"),
                "currency": snapshot.get("currency"),
                "livemode": snapshot.get("livemode"),
                "metadata_operation_id": snapshot["metadata"]["lycheetah_operation_id"],
            }, now=now)

        if op["state"] in _TERMINAL:
            # Only the queue API's ledger guard allows this transition to DONE.
            return self._finish(job, "RECONCILED", "terminal-provider-state-recorded", now=now,
                                ledger_state=op["state"], refund_status=op["refund_status"])
        if op["state"] == "WAITING_PROVIDER":
            return self._finish(job, "RETRY", "refund-still-pending", now=now,
                                ledger_state=op["state"], refund_status=op["refund_status"])
        return self._finish(job, "MANUAL", op.get("manual_reason") or "provider-state-requires-review",
                            now=now, ledger_state=op["state"], refund_status=op.get("refund_status"))

    @staticmethod
    def _job_target(job: Mapping[str, Any], op: Mapping[str, Any]) -> bool:
        if op["target_type"] == "charge":
            return job.get("charge") == op["target_id"]
        if op["target_type"] == "payment_intent":
            return job.get("payment_intent") == op["target_id"]
        return False

    @staticmethod
    def _validate_snapshot(snapshot: Any, *, job: Mapping[str, Any],
                           op: Mapping[str, Any], operation_id: str) -> tuple[bool, str]:
        if not isinstance(snapshot, Mapping) or snapshot.get("object") != "refund":
            return False, "provider-object-type-invalid"
        if snapshot.get("id") != job.get("refund_id"):
            return False, "provider-refund-id-mismatch"
        if type(snapshot.get("livemode")) is not bool or snapshot.get("livemode") is not False:
            return False, "provider-livemode-mismatch"
        status = snapshot.get("status")
        if not isinstance(status, str) or status not in _ALLOWED_STATUS:
            return False, "provider-status-unknown"
        metadata = snapshot.get("metadata")
        if not isinstance(metadata, Mapping) or metadata.get("lycheetah_operation_id") != operation_id:
            return False, "provider-operation-correlation-mismatch"
        target = snapshot.get(op["target_type"])
        if target != op["target_id"]:
            return False, "provider-target-mismatch"
        if type(snapshot.get("amount")) is not int or snapshot.get("amount") != op["expected_amount"]:
            return False, "provider-amount-mismatch"
        if snapshot.get("currency") != op["expected_currency"]:
            return False, "provider-currency-mismatch"
        return True, "provider-snapshot-contract-valid"

    def _finish(self, job: Mapping[str, Any], disposition: str, reason: str, *,
                now: datetime | None = None, ledger_state: str | None = None,
                refund_status: str | None = None) -> WorkerResult:
        kwargs: dict[str, Any] = {
            "event_id": job["event_id"], "worker_id": self.worker_id,
            "claim_token": job["claim_token"], "disposition": disposition,
            "reason_code": reason,
        }
        if disposition == "RETRY":
            kwargs["retry_after_seconds"] = self.retry_after_seconds
        if now is not None:
            kwargs["now"] = now
        try:
            result = self.inbox.finish_reconciliation_job(**kwargs)
        except ReconciliationQueueError as exc:
            # Ledger update may already be durable. If the lease expired before
            # ack, let the lease be reclaimed; GET reconciliation is idempotent.
            if "lease-expired" in str(exc) or "claim-mismatch" in str(exc):
                return WorkerResult(job["event_id"], job.get("operation_id"), "ACK_PENDING",
                                    "queue-lease-no-longer-valid", ledger_state, refund_status)
            raise
        action = {"DONE": "RECONCILED", "PENDING": "RETRY", "MANUAL": "MANUAL"}.get(result.state, result.state)
        return WorkerResult(job["event_id"], job.get("operation_id"), action, reason,
                            ledger_state, refund_status)
