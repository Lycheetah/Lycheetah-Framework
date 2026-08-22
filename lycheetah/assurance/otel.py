"""Privacy-minimised OpenTelemetry span-event bridge.

Status: [SCAFFOLD]. Attribute names use the Lycheetah namespace; this module does
not claim adoption by OpenTelemetry GenAI semantic conventions.
"""

from __future__ import annotations

from typing import Any, Protocol

from .receipt import AssuranceReceipt, ReceiptError


OTEL_EVENT_NAME = "lycheetah.assurance.decision"


class EventSpan(Protocol):
    """Small structural interface implemented by OpenTelemetry Span objects."""

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
        timestamp: int | None = None,
    ) -> None: ...


def otel_event_attributes(receipt: AssuranceReceipt) -> dict[str, Any]:
    """Return OTel-safe scalar/sequence attributes without raw subject content."""

    verification = receipt.verify()
    if not verification.valid:
        raise ReceiptError(
            "refusing to export an invalid receipt: " + "; ".join(verification.errors)
        )

    finding_ids = tuple(finding.finding_id for finding in receipt.findings)
    effective = tuple(
        finding.effective_disposition.value for finding in receipt.findings
    )
    return {
        "lycheetah.assurance.schema_version": receipt.schema_version,
        "lycheetah.assurance.receipt_id": receipt.receipt_id,
        "lycheetah.assurance.decision": receipt.decision.value,
        "lycheetah.assurance.phase": str(receipt.event.get("phase", "unknown")),
        "lycheetah.assurance.policy.id": str(receipt.policy.get("id", "unknown")),
        "lycheetah.assurance.policy.version": str(
            receipt.policy.get("version", "unknown")
        ),
        "lycheetah.assurance.policy.sha256": str(receipt.policy.get("sha256", "")),
        "lycheetah.assurance.integrity.sha256": receipt.digest,
        "lycheetah.assurance.trace_id": str(
            receipt.lineage.get("trace_id", "unknown")
        ),
        "lycheetah.assurance.replayable": bool(
            receipt.event.get("replayable", False)
        ),
        "lycheetah.assurance.finding.count": len(receipt.findings),
        "lycheetah.assurance.finding.ids": finding_ids,
        "lycheetah.assurance.finding.dispositions": effective,
    }


def add_receipt_event(span: EventSpan, receipt: AssuranceReceipt) -> None:
    """Attach a verified Assurance Receipt summary to an active OTel span."""

    add_event = getattr(span, "add_event", None)
    if not callable(add_event):
        raise TypeError("span must provide add_event(name, attributes=...)")
    add_event(OTEL_EVENT_NAME, attributes=otel_event_attributes(receipt))
