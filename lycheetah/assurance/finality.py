"""Dispatch/finality-time evidence revalidation for Assurance Runtime.

Status: [SCAFFOLD].

This module is additive. It does not turn :class:`AssuranceRuntime` into an
effect broker and it does not claim to make a remote provider atomic with a
local policy decision.

The caller:
1. evaluates/admit a tool event through ``FinalityGate.admit``;
2. persists the returned witness if the result is ALLOW;
3. immediately before creating irreversible external execution intent, calls
   ``FinalityGate.finalize`` with the same exact event and witness;
4. proceeds only when ``ready`` is true.

Gate-owned failures route to REVIEW because this feature remains SCAFFOLD.
A BLOCK is propagated only when the underlying current Assurance Runtime returns
BLOCK at admission/finality.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from .jsonutil import jsonable, sha256_json
from .models import AssuranceEvent, Disposition, Phase

FINALITY_VERSION = "0.1.0"


class EvidenceMode(str, Enum):
    EXACT = "EXACT"
    SUBJECT_STATUS = "SUBJECT_STATUS"


@dataclass(frozen=True)
class EvidenceRecord:
    key: str
    version: str
    subject_hash: str
    value_digest: str
    status: str

    def __post_init__(self) -> None:
        for name in ("key", "version", "subject_hash", "value_digest", "status"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "version": self.version,
            "subject_hash": self.subject_hash,
            "value_digest": self.value_digest,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> EvidenceRecord:
        required = {"key", "version", "subject_hash", "value_digest", "status"}
        if set(data) != required:
            raise ValueError("evidence record has missing or unknown fields")
        return cls(**{name: data[name] for name in required})


class EvidenceProvider(Protocol):
    def get_evidence(self, key: str) -> EvidenceRecord | None:
        """Return the current authoritative record for ``key``."""


@dataclass(frozen=True)
class EvidenceRequirement:
    key: str
    mode: EvidenceMode = EvidenceMode.SUBJECT_STATUS
    required_status: str = "PASS"
    required_subject_hash: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("evidence requirement key must be non-empty")
        object.__setattr__(self, "mode", EvidenceMode(self.mode))
        if not isinstance(self.required_status, str) or not self.required_status:
            raise ValueError("required_status must be non-empty")
        if self.required_subject_hash is not None and (
            not isinstance(self.required_subject_hash, str) or not self.required_subject_hash
        ):
            raise ValueError("required_subject_hash must be non-empty when supplied")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "mode": self.mode.value,
            "required_status": self.required_status,
            "required_subject_hash": self.required_subject_hash,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> EvidenceRequirement:
        required = {"key", "mode", "required_status", "required_subject_hash"}
        if set(data) != required:
            raise ValueError("evidence requirement has missing or unknown fields")
        return cls(
            key=data["key"],
            mode=EvidenceMode(data["mode"]),
            required_status=data["required_status"],
            required_subject_hash=data["required_subject_hash"],
        )


@dataclass(frozen=True)
class BoundEvidence:
    requirement: EvidenceRequirement
    admitted: EvidenceRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement": self.requirement.to_dict(),
            "admitted": self.admitted.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BoundEvidence:
        if set(data) != {"requirement", "admitted"}:
            raise ValueError("bound evidence has missing or unknown fields")
        return cls(
            EvidenceRequirement.from_dict(data["requirement"]),
            EvidenceRecord.from_dict(data["admitted"]),
        )


@dataclass(frozen=True)
class AdmissionWitness:
    event_sha256: str
    policy_id: str
    policy_version: str
    policy_sha256: str
    admission_receipt_sha256: str
    evidence: tuple[BoundEvidence, ...]
    digest: str

    @classmethod
    def issue(
        cls,
        *,
        event_sha256: str,
        policy_id: str,
        policy_version: str,
        policy_sha256: str,
        admission_receipt_sha256: str,
        evidence: Iterable[BoundEvidence],
    ) -> AdmissionWitness:
        items = tuple(evidence)
        body = {
            "schema_version": "0.1",
            "finality_version": FINALITY_VERSION,
            "event_sha256": event_sha256,
            "policy_id": policy_id,
            "policy_version": policy_version,
            "policy_sha256": policy_sha256,
            "admission_receipt_sha256": admission_receipt_sha256,
            "evidence": [item.to_dict() for item in items],
        }
        return cls(
            event_sha256=event_sha256,
            policy_id=policy_id,
            policy_version=policy_version,
            policy_sha256=policy_sha256,
            admission_receipt_sha256=admission_receipt_sha256,
            evidence=items,
            digest=sha256_json(body),
        )

    def body_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "finality_version": FINALITY_VERSION,
            "event_sha256": self.event_sha256,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "policy_sha256": self.policy_sha256,
            "admission_receipt_sha256": self.admission_receipt_sha256,
            "evidence": [item.to_dict() for item in self.evidence],
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.body_dict(), "integrity": {"algorithm": "sha256", "digest": self.digest}}

    def verify(self) -> bool:
        return self.digest == sha256_json(self.body_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AdmissionWitness:
        required = {
            "schema_version",
            "finality_version",
            "event_sha256",
            "policy_id",
            "policy_version",
            "policy_sha256",
            "admission_receipt_sha256",
            "evidence",
            "integrity",
        }
        if set(data) != required:
            raise ValueError("admission witness has missing or unknown fields")
        if data["schema_version"] != "0.1" or data["finality_version"] != FINALITY_VERSION:
            raise ValueError("unsupported admission witness version")
        integrity = data["integrity"]
        if not isinstance(integrity, Mapping) or set(integrity) != {"algorithm", "digest"}:
            raise ValueError("invalid admission witness integrity")
        if integrity["algorithm"] != "sha256":
            raise ValueError("unsupported admission witness integrity algorithm")
        witness = cls(
            event_sha256=str(data["event_sha256"]),
            policy_id=str(data["policy_id"]),
            policy_version=str(data["policy_version"]),
            policy_sha256=str(data["policy_sha256"]),
            admission_receipt_sha256=str(data["admission_receipt_sha256"]),
            evidence=tuple(BoundEvidence.from_dict(x) for x in data["evidence"]),
            digest=str(integrity["digest"]),
        )
        if not witness.verify():
            raise ValueError("admission witness digest mismatch")
        return witness


@dataclass(frozen=True)
class FinalityResult:
    disposition: Disposition
    ready: bool
    reason: str
    event_sha256: str
    admission_receipt_sha256: str | None = None
    finality_receipt_sha256: str | None = None
    witness_sha256: str | None = None
    evidence_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition.value,
            "ready": self.ready,
            "reason": self.reason,
            "event_sha256": self.event_sha256,
            "admission_receipt_sha256": self.admission_receipt_sha256,
            "finality_receipt_sha256": self.finality_receipt_sha256,
            "witness_sha256": self.witness_sha256,
            "evidence_key": self.evidence_key,
        }


@dataclass(frozen=True)
class AdmissionResult:
    disposition: Disposition
    ready_for_finality: bool
    reason: str
    receipt_sha256: str
    witness: AdmissionWitness | None = None
    evidence_key: str | None = None


class MappingEvidenceStore:
    """Small deterministic store for integration tests/examples, not persistence."""

    def __init__(self, records: Iterable[EvidenceRecord] = ()) -> None:
        self._records = {record.key: record for record in records}

    def put(self, record: EvidenceRecord) -> None:
        self._records[record.key] = record

    def get_evidence(self, key: str) -> EvidenceRecord | None:
        return self._records.get(key)


class FinalityGate:
    """Re-evaluate a tool action and its dependency-scoped evidence at finality."""

    def __init__(self, runtime: Any, evidence_provider: EvidenceProvider):
        if not hasattr(runtime, "evaluate"):
            raise TypeError("runtime must provide evaluate(event)")
        if not hasattr(evidence_provider, "get_evidence"):
            raise TypeError("evidence_provider must provide get_evidence(key)")
        self.runtime = runtime
        self.evidence_provider = evidence_provider

    def admit(
        self,
        event: AssuranceEvent,
        requirements: Iterable[EvidenceRequirement],
    ) -> AdmissionResult:
        self._require_tool_event(event)
        requirements = tuple(requirements)
        if not requirements:
            raise ValueError("at least one evidence requirement is required")

        receipt = self.runtime.evaluate(event)
        event_digest = _event_sha256(event)
        receipt_verification = receipt.verify()
        if not receipt_verification.valid:
            return AdmissionResult(
                Disposition.REVIEW, False, "admission-receipt-invalid", receipt.digest
            )
        if receipt.decision != Disposition.ALLOW:
            return AdmissionResult(
                receipt.decision,
                False,
                "underlying-runtime-not-allow",
                receipt.digest,
            )

        bound: list[BoundEvidence] = []
        for requirement in requirements:
            current = self.evidence_provider.get_evidence(requirement.key)
            if current is None:
                return AdmissionResult(
                    Disposition.REVIEW,
                    False,
                    "required-evidence-missing",
                    receipt.digest,
                    evidence_key=requirement.key,
                )
            if not _predicate_satisfied(requirement, current):
                return AdmissionResult(
                    Disposition.REVIEW,
                    False,
                    "required-evidence-unsatisfied",
                    receipt.digest,
                    evidence_key=requirement.key,
                )
            bound.append(BoundEvidence(requirement, current))

        policy = receipt.policy
        witness = AdmissionWitness.issue(
            event_sha256=event_digest,
            policy_id=str(policy.get("id", "")),
            policy_version=str(policy.get("version", "")),
            policy_sha256=str(policy.get("sha256", "")),
            admission_receipt_sha256=receipt.digest,
            evidence=bound,
        )
        return AdmissionResult(
            Disposition.ALLOW,
            True,
            "admitted",
            receipt.digest,
            witness=witness,
        )

    def finalize(
        self,
        witness: AdmissionWitness,
        event: AssuranceEvent,
    ) -> FinalityResult:
        self._require_tool_event(event)
        event_digest = _event_sha256(event)

        if not witness.evidence:
            return FinalityResult(Disposition.REVIEW, False, "witness-evidence-empty", event_digest)
        if not witness.verify():
            return FinalityResult(
                Disposition.REVIEW,
                False,
                "witness-integrity-invalid",
                event_digest,
                witness_sha256=witness.digest,
            )
        if event_digest != witness.event_sha256:
            return FinalityResult(
                Disposition.REVIEW,
                False,
                "event-changed-after-admission",
                event_digest,
                admission_receipt_sha256=witness.admission_receipt_sha256,
                witness_sha256=witness.digest,
            )

        receipt = self.runtime.evaluate(event)
        verification = receipt.verify()
        if not verification.valid:
            return FinalityResult(
                Disposition.REVIEW,
                False,
                "finality-receipt-invalid",
                event_digest,
                admission_receipt_sha256=witness.admission_receipt_sha256,
                finality_receipt_sha256=receipt.digest,
                witness_sha256=witness.digest,
            )

        if receipt.decision == Disposition.BLOCK:
            return FinalityResult(
                Disposition.BLOCK,
                False,
                "underlying-runtime-blocked-at-finality",
                event_digest,
                admission_receipt_sha256=witness.admission_receipt_sha256,
                finality_receipt_sha256=receipt.digest,
                witness_sha256=witness.digest,
            )
        if receipt.decision != Disposition.ALLOW:
            return FinalityResult(
                Disposition.REVIEW,
                False,
                "underlying-runtime-not-allow-at-finality",
                event_digest,
                admission_receipt_sha256=witness.admission_receipt_sha256,
                finality_receipt_sha256=receipt.digest,
                witness_sha256=witness.digest,
            )

        policy = receipt.policy
        current_policy = (
            str(policy.get("id", "")),
            str(policy.get("version", "")),
            str(policy.get("sha256", "")),
        )
        admitted_policy = (
            witness.policy_id,
            witness.policy_version,
            witness.policy_sha256,
        )
        if current_policy != admitted_policy:
            return FinalityResult(
                Disposition.REVIEW,
                False,
                "policy-changed-after-admission",
                event_digest,
                admission_receipt_sha256=witness.admission_receipt_sha256,
                finality_receipt_sha256=receipt.digest,
                witness_sha256=witness.digest,
            )

        for bound in witness.evidence:
            current = self.evidence_provider.get_evidence(bound.requirement.key)
            if current is None:
                return _review(
                    "required-evidence-missing-at-finality",
                    event_digest,
                    witness,
                    receipt.digest,
                    bound.requirement.key,
                )
            if bound.requirement.mode == EvidenceMode.EXACT:
                if current != bound.admitted:
                    return _review(
                        "exact-evidence-changed-after-admission",
                        event_digest,
                        witness,
                        receipt.digest,
                        bound.requirement.key,
                    )
            elif not _predicate_satisfied(bound.requirement, current):
                return _review(
                    "evidence-predicate-false-at-finality",
                    event_digest,
                    witness,
                    receipt.digest,
                    bound.requirement.key,
                )

        return FinalityResult(
            Disposition.ALLOW,
            True,
            "fresh-evidence-and-current-policy",
            event_digest,
            admission_receipt_sha256=witness.admission_receipt_sha256,
            finality_receipt_sha256=receipt.digest,
            witness_sha256=witness.digest,
        )

    @staticmethod
    def _require_tool_event(event: AssuranceEvent) -> None:
        if not isinstance(event, AssuranceEvent):
            raise TypeError("event must be AssuranceEvent")
        if event.phase != Phase.TOOL:
            raise ValueError("finality gate accepts tool events only")


def _review(
    reason: str,
    event_digest: str,
    witness: AdmissionWitness,
    receipt_digest: str,
    evidence_key: str,
) -> FinalityResult:
    return FinalityResult(
        Disposition.REVIEW,
        False,
        reason,
        event_digest,
        admission_receipt_sha256=witness.admission_receipt_sha256,
        finality_receipt_sha256=receipt_digest,
        witness_sha256=witness.digest,
        evidence_key=evidence_key,
    )


def _predicate_satisfied(
    requirement: EvidenceRequirement,
    record: EvidenceRecord,
) -> bool:
    if record.key != requirement.key:
        return False
    if record.status != requirement.required_status:
        return False
    return (
        requirement.required_subject_hash is None
        or record.subject_hash == requirement.required_subject_hash
    )


def _event_sha256(event: AssuranceEvent) -> str:
    return sha256_json(
        {
            "phase": event.phase.value,
            "content": event.content,
            "event_id": event.event_id,
            "trace_id": event.trace_id,
            "tool_name": event.tool_name,
            "tool_arguments": jsonable(event.tool_arguments),
            "scopes": list(event.scopes),
            "side_effect": event.side_effect,
            "human_approved": event.human_approved,
            "context": jsonable(event.context),
            "metadata": jsonable(event.metadata),
        }
    )
