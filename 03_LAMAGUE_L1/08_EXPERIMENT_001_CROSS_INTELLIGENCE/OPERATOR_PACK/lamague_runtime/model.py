from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
import uuid


class AuditOutcome(str, Enum):
    VALID = "VALID"
    EXPAND = "EXPAND"
    REPAIR = "REPAIR"
    ISOLATE = "ISOLATE"
    REJECT = "REJECT"


class Lifecycle(str, Enum):
    VOID = "VOID"
    GLOW = "GLOW"
    FORGED = "FORGED"
    ROOT = "ROOT"
    ASH = "ASH"


class CompressionMode(str, Enum):
    COMPRESS = "Z_DOWN"
    EXPAND = "Z_UP"
    HOLD = "HOLD"


class IdentityStatus(str, Enum):
    CONTINUATION = "CONTINUATION"
    DESCENDANT = "DESCENDANT"
    FORK = "FORK"
    IMPOSTOR = "IMPOSTOR"
    DEAD = "DEAD"


@dataclass
class DissentRecord:
    parties: list[str]
    positions: dict[str, str]
    unknown_type: str = "disagreement"
    protected_boundaries: list[str] = field(default_factory=list)
    status: str = "UNRESOLVED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValueEntry:
    source: str
    recipient: str
    kind: str
    amount: float = 0.0
    unit: str = "relative"
    declared: bool = True
    consent: str = ""
    affected_parties: list[str] = field(default_factory=list)
    reversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompressionDecision:
    mode: CompressionMode
    reasons: list[str]
    decoder_confidence: float
    risk_level: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "reasons": self.reasons,
            "decoder_confidence": self.decoder_confidence,
            "risk_level": self.risk_level,
        }


@dataclass
class ContextCapsule:
    domain: str = "unspecified"
    participants: list[str] = field(default_factory=list)
    affected_parties: list[str] = field(default_factory=list)
    purpose: str = ""
    claim: str = ""
    evidence: list[str] = field(default_factory=list)
    evidence_score: float = 0.0
    certainty: float = 0.0
    unknowns: list[str] = field(default_factory=list)
    authority: list[str] = field(default_factory=list)
    consent: dict[str, str] = field(default_factory=dict)
    boundaries: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    value_created: list[str] = field(default_factory=list)
    costs: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    consequence_horizon: str = ""
    recovery: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    risk_level: str = "low"
    irreversible: bool = False
    execute_requested: bool = False
    registry_version: str = "0.2"
    decoder_confidence: float = 1.0
    shared_context: bool = True
    dissent: list[dict[str, Any]] = field(default_factory=list)
    value_ledger: list[dict[str, Any]] = field(default_factory=list)
    parent_semantic_hash: str = ""
    claimed_identity: str = ""
    migration_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ASTNode:
    operation: str
    operation_name: str
    input_types: list[str]
    output_type: str
    arguments: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    provenance: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    authority: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    value_flow: dict[str, Any] = field(default_factory=dict)
    consequence_horizon: str = ""
    recovery: list[str] = field(default_factory=list)
    version: str = "0.2"
    node_id: str = field(default_factory=lambda: f"node-{uuid.uuid4().hex[:12]}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProgramAST:
    source: str
    nodes: list[ASTNode]
    context: ContextCapsule
    expanded_from: list[str] = field(default_factory=list)
    version: str = "0.2"
    program_id: str = field(default_factory=lambda: f"program-{uuid.uuid4().hex[:12]}")

    @property
    def operation_path(self) -> list[str]:
        return [node.operation for node in self.nodes]

    def to_dict(self) -> dict[str, Any]:
        return {
            "program_id": self.program_id,
            "version": self.version,
            "source": self.source,
            "expanded_from": self.expanded_from,
            "operation_path": self.operation_path,
            "context": self.context.to_dict(),
            "nodes": [node.to_dict() for node in self.nodes],
        }


@dataclass
class AuditFinding:
    gate: str
    outcome: AuditOutcome
    code: str
    message: str
    repair: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["outcome"] = self.outcome.value
        return d


@dataclass
class AuditReport:
    outcome: AuditOutcome
    findings: list[AuditFinding]
    gates: dict[str, AuditOutcome]

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "gates": {k: v.value for k, v in self.gates.items()},
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass
class ExecutionResult:
    executed: bool
    state: dict[str, Any]
    audit: AuditReport
    trace: list[dict[str, Any]]
    explanation: str = ""
    semantic_hash: str = ""
    compression: CompressionDecision | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "executed": self.executed,
            "state": self.state,
            "audit": self.audit.to_dict(),
            "trace": self.trace,
            "explanation": self.explanation,
            "semantic_hash": self.semantic_hash,
            "compression": self.compression.to_dict() if self.compression else None,
        }
