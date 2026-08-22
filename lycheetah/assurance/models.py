"""Typed public models for the Lycheetah Assurance Runtime."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

from .jsonutil import jsonable


class Phase(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    TOOL = "tool"


class Disposition(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class ClaimStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SCAFFOLD = "SCAFFOLD"
    CONJECTURE = "CONJECTURE"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


DISPOSITION_ORDER = {
    Disposition.ALLOW: 0,
    Disposition.REVIEW: 1,
    Disposition.BLOCK: 2,
}


def strongest(dispositions: Sequence[Disposition]) -> Disposition:
    return max(dispositions, key=DISPOSITION_ORDER.get, default=Disposition.ALLOW)


def enforcement_cap(status: ClaimStatus, deterministic: bool) -> Disposition:
    if status == ClaimStatus.CONJECTURE:
        return Disposition.ALLOW
    if status == ClaimStatus.SCAFFOLD or not deterministic:
        return Disposition.REVIEW
    return Disposition.BLOCK


def capped_disposition(
    requested: Disposition,
    status: ClaimStatus,
    deterministic: bool,
) -> tuple[Disposition, Optional[str]]:
    cap = enforcement_cap(status, deterministic)
    if DISPOSITION_ORDER[requested] <= DISPOSITION_ORDER[cap]:
        return requested, None
    effective = cap
    reason = (
        f"requested {requested.value} capped at {effective.value}: "
        f"status={status.value}, deterministic={str(deterministic).lower()}"
    )
    return effective, reason


@dataclass(frozen=True)
class ControlReference:
    framework: str
    control_id: str
    title: str
    url: str = ""

    def to_dict(self) -> dict[str, str]:
        out = {
            "framework": self.framework,
            "control_id": self.control_id,
            "title": self.title,
        }
        if self.url:
            out["url"] = self.url
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ControlReference":
        return cls(
            framework=str(data["framework"]),
            control_id=str(data["control_id"]),
            title=str(data["title"]),
            url=str(data.get("url", "")),
        )


@dataclass(frozen=True)
class Finding:
    finding_id: str
    title: str
    description: str
    severity: Severity
    requested_disposition: Disposition
    effective_disposition: Disposition
    claim_status: ClaimStatus
    deterministic: bool
    evaluator: str
    confidence: float = 1.0
    status_basis: str = ""
    evidence: tuple[str, ...] = ()
    controls: tuple[ControlReference, ...] = ()
    cap_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", self.finding_id):
            raise ValueError(f"invalid finding_id: {self.finding_id!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("finding confidence must be in [0, 1]")

    @classmethod
    def create(
        cls,
        *,
        finding_id: str,
        title: str,
        description: str,
        severity: Severity,
        requested_disposition: Disposition,
        claim_status: ClaimStatus,
        deterministic: bool,
        evaluator: str,
        confidence: float = 1.0,
        status_basis: str = "",
        evidence: Sequence[str] = (),
        controls: Sequence[ControlReference] = (),
    ) -> "Finding":
        effective, reason = capped_disposition(
            requested_disposition, claim_status, deterministic
        )
        return cls(
            finding_id=finding_id,
            title=title,
            description=description,
            severity=severity,
            requested_disposition=requested_disposition,
            effective_disposition=effective,
            claim_status=claim_status,
            deterministic=deterministic,
            evaluator=evaluator,
            confidence=confidence,
            status_basis=status_basis,
            evidence=tuple(evidence),
            controls=tuple(controls),
            cap_reason=reason,
        )

    def with_evidence(self, evidence: Sequence[str]) -> "Finding":
        return replace(self, evidence=tuple(evidence))

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.finding_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "requested_disposition": self.requested_disposition.value,
            "effective_disposition": self.effective_disposition.value,
            "claim_status": self.claim_status.value,
            "deterministic": self.deterministic,
            "evaluator": self.evaluator,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "controls": [control.to_dict() for control in self.controls],
        }
        if self.status_basis:
            out["status_basis"] = self.status_basis
        if self.cap_reason:
            out["cap_reason"] = self.cap_reason
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Finding":
        required = {
            "id",
            "title",
            "description",
            "severity",
            "requested_disposition",
            "effective_disposition",
            "claim_status",
            "deterministic",
            "evaluator",
            "confidence",
            "evidence",
            "controls",
        }
        allowed = required | {"status_basis", "cap_reason"}
        missing = sorted(required.difference(data))
        unknown = sorted(set(data).difference(allowed))
        if missing:
            raise ValueError(f"finding missing required fields: {', '.join(missing)}")
        if unknown:
            raise ValueError(f"finding contains unknown fields: {', '.join(unknown)}")
        if type(data.get("deterministic")) is not bool:
            raise ValueError("finding deterministic must be a boolean")
        if not isinstance(data["evidence"], list) or not isinstance(data["controls"], list):
            raise ValueError("finding evidence and controls must be arrays")
        if data.get("cap_reason") is not None and not isinstance(data["cap_reason"], str):
            raise ValueError("finding cap_reason must be a string or null")
        return cls(
            finding_id=str(data["id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            severity=Severity(data["severity"]),
            requested_disposition=Disposition(data["requested_disposition"]),
            effective_disposition=Disposition(data["effective_disposition"]),
            claim_status=ClaimStatus(data["claim_status"]),
            deterministic=data["deterministic"],
            evaluator=str(data["evaluator"]),
            confidence=float(data.get("confidence", 1.0)),
            status_basis=str(data.get("status_basis", "")),
            evidence=tuple(str(item) for item in data.get("evidence", [])),
            controls=tuple(
                ControlReference.from_dict(item) for item in data.get("controls", [])
            ),
            cap_reason=data.get("cap_reason"),
        )


@dataclass(frozen=True)
class AssuranceEvent:
    phase: Phase
    content: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: Optional[str] = None
    tool_arguments: Mapping[str, Any] = field(default_factory=dict)
    scopes: tuple[str, ...] = ()
    side_effect: bool = False
    human_approved: Optional[bool] = None
    context: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", Phase(self.phase))
        if self.content is not None and not isinstance(self.content, str):
            raise TypeError("event content must be text when supplied")
        if self.tool_name is not None and not isinstance(self.tool_name, str):
            raise TypeError("tool_name must be text when supplied")
        if not isinstance(self.tool_arguments, Mapping):
            raise TypeError("tool_arguments must be an object")
        if not isinstance(self.context, Mapping) or not isinstance(self.metadata, Mapping):
            raise TypeError("event context and metadata must be objects")
        if isinstance(self.scopes, (str, bytes)):
            raise TypeError("event scopes must be an iterable of strings")
        if type(self.side_effect) is not bool:
            raise TypeError("side_effect must be a boolean")
        if self.human_approved is not None and type(self.human_approved) is not bool:
            raise TypeError("human_approved must be a boolean or null")
        object.__setattr__(self, "tool_arguments", jsonable(self.tool_arguments))
        object.__setattr__(self, "context", jsonable(self.context))
        object.__setattr__(self, "metadata", jsonable(self.metadata))
        if any(not isinstance(scope, str) or not scope for scope in self.scopes):
            raise TypeError("event scopes must contain non-empty strings")
        object.__setattr__(self, "scopes", tuple(self.scopes))
        if not isinstance(self.event_id, str) or not isinstance(self.trace_id, str):
            raise TypeError("event_id and trace_id must be strings")
        if not self.event_id.strip() or not self.trace_id.strip():
            raise ValueError("event_id and trace_id must be non-empty")
        if self.phase == Phase.TOOL:
            if self.content is not None:
                raise ValueError("tool event content must be null; use tool_arguments")
        elif (
            self.tool_name is not None
            or self.tool_arguments
            or self.scopes
            or self.side_effect
            or self.human_approved is not None
        ):
            raise ValueError("input/output events cannot contain tool-only fields")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AssuranceEvent":
        if not isinstance(data, Mapping):
            raise TypeError("event must be an object")
        allowed = {
            "phase",
            "content",
            "event_id",
            "trace_id",
            "tool_name",
            "tool_arguments",
            "scopes",
            "side_effect",
            "human_approved",
            "context",
            "metadata",
        }
        unknown = sorted(str(key) for key in data if key not in allowed)
        if "phase" not in data:
            raise ValueError("event requires phase")
        if unknown:
            raise ValueError("event contains unknown fields: " + ", ".join(unknown))
        if not isinstance(data["phase"], str):
            raise TypeError("event phase must be a string")
        for name in ("event_id", "trace_id"):
            if name in data and not isinstance(data[name], str):
                raise TypeError(f"event {name} must be a string")
        scopes = data.get("scopes", [])
        if not isinstance(scopes, (list, tuple)):
            raise TypeError("event scopes must be an array")
        side_effect = data.get("side_effect", False)
        if type(side_effect) is not bool:
            raise TypeError("event side_effect must be a boolean")
        human_approved = data.get("human_approved")
        if human_approved is not None and type(human_approved) is not bool:
            raise TypeError("event human_approved must be a boolean or null")
        return cls(
            phase=Phase(data["phase"]),
            content=data.get("content"),
            event_id=data.get("event_id", str(uuid.uuid4())),
            trace_id=data.get("trace_id", str(uuid.uuid4())),
            tool_name=data.get("tool_name"),
            tool_arguments=data.get("tool_arguments", {}),
            scopes=tuple(scopes),
            side_effect=side_effect,
            human_approved=human_approved,
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
        )
