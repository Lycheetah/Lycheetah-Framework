"""Lycheetah Assurance Runtime public API.

The package is [SCAFFOLD]: useful for evaluation and integration work, not a
certification that an AI system is safe, aligned, truthful, or compliant.
"""

from .evaluation import (
    EVALUATION_SCHEMA_VERSION,
    EvaluationCase,
    EvaluationCorpus,
    EvaluationError,
    EvaluationGate,
    EvaluationReport,
    evaluate_corpus,
)
from .execution_cell import (
    EXECUTION_CELL_VERSION,
    CellAvailability,
    ExecutionCell,
    ExecutionCellResult,
    ExecutionCellSpec,
)
from .finality import (
    FINALITY_VERSION,
    AdmissionResult,
    AdmissionWitness,
    BoundEvidence,
    EvidenceMode,
    EvidenceRecord,
    EvidenceRequirement,
    FinalityGate,
    FinalityResult,
    MappingEvidenceStore,
)
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
from .regression import (
    REGRESSION_SCHEMA_VERSION,
    RegressionGate,
    RegressionReport,
    compare_evaluations,
)
from .runtime import ASSURANCE_VERSION, AssuranceRuntime

__all__ = [
    "ASSURANCE_VERSION",
    "EVALUATION_SCHEMA_VERSION",
    "EXECUTION_CELL_VERSION",
    "FINALITY_VERSION",
    "OTEL_EVENT_NAME",
    "REGRESSION_SCHEMA_VERSION",
    "AdmissionResult",
    "AdmissionWitness",
    "AssuranceEvent",
    "AssurancePolicy",
    "AssuranceReceipt",
    "AssuranceRuntime",
    "BoundEvidence",
    "CellAvailability",
    "ClaimStatus",
    "ControlReference",
    "Disposition",
    "EvaluationCase",
    "EvaluationCorpus",
    "EvaluationError",
    "EvaluationGate",
    "EvaluationReport",
    "EvidenceMode",
    "EvidenceRecord",
    "EvidenceRequirement",
    "ExecutionCell",
    "ExecutionCellResult",
    "ExecutionCellSpec",
    "FinalityGate",
    "FinalityResult",
    "Finding",
    "LogVerificationReport",
    "MappingEvidenceStore",
    "Phase",
    "PolicyError",
    "ReceiptError",
    "ReceiptLog",
    "RegressionGate",
    "RegressionReport",
    "Severity",
    "TextRule",
    "VerificationReport",
    "add_receipt_event",
    "capped_disposition",
    "compare_evaluations",
    "default_policy",
    "enforcement_cap",
    "evaluate_corpus",
    "otel_event_attributes",
    "to_in_toto_statement",
]
