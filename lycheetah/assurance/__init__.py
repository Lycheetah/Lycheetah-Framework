"""Lycheetah Assurance Runtime public API.

The package is [SCAFFOLD]: useful for evaluation and integration work, not a
certification that an AI system is safe, aligned, truthful, or compliant.
"""

from .in_toto import to_in_toto_statement
from .models import (
    AssuranceEvent,
    ClaimStatus,
    ControlReference,
    Disposition,
    Finding,
    Phase,
    Severity,
    capped_disposition,
    enforcement_cap,
)
from .otel import OTEL_EVENT_NAME, add_receipt_event, otel_event_attributes
from .policy import AssurancePolicy, PolicyError, TextRule, default_policy
from .receipt import (
    AssuranceReceipt,
    LogVerificationReport,
    ReceiptError,
    ReceiptLog,
    VerificationReport,
)
from .runtime import ASSURANCE_VERSION, AssuranceRuntime

__all__ = [
    "ASSURANCE_VERSION",
    "AssuranceEvent",
    "AssurancePolicy",
    "AssuranceReceipt",
    "AssuranceRuntime",
    "ClaimStatus",
    "ControlReference",
    "Disposition",
    "Finding",
    "LogVerificationReport",
    "OTEL_EVENT_NAME",
    "Phase",
    "PolicyError",
    "ReceiptError",
    "ReceiptLog",
    "Severity",
    "TextRule",
    "VerificationReport",
    "add_receipt_event",
    "capped_disposition",
    "default_policy",
    "enforcement_cap",
    "otel_event_attributes",
    "to_in_toto_statement",
]
