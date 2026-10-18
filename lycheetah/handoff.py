"""Lycheetah Cross-Seat Task & Context Capsule (`lycheetah.handoff`).

Packages declared tasks and checks reported outcomes against their reference.
The checksum is unsigned. Verification compares declarations; it does not observe
filesystem effects, authenticate a human, or enforce an operating-system sandbox.

Schema: `lycheetah.handoff.v1`
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from types import MappingProxyType
from typing import Any, Literal

from .compaction import (
    VALID_RISKS,
    AgentStatePacket,
    CompactionShield,
)

HANDOFF_SCHEMA_VERSION = "lycheetah.handoff.v1"
CapsuleStatus = Literal["PROPOSED", "APPROVED", "EXECUTED", "VERIFIED", "REJECTED"]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_hex(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


class HandoffError(ValueError):
    """Raised when a capsule violates structure, invariants, or boundaries."""


def _text(name: str, value: Any, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise HandoffError(f"{name} must be a {'possibly empty ' if empty else 'non-empty '}string")
    return value


def _timestamp(name: str, value: Any) -> dt.datetime:
    value = _text(name, value)
    try:
        parsed = dt.datetime.fromisoformat(
            value.removesuffix("Z") + "+00:00" if value.endswith("Z") else value
        )
    except ValueError as err:
        raise HandoffError(f"{name} must be an ISO-8601 timestamp") from err
    if parsed.tzinfo is None:
        raise HandoffError(f"{name} must include a timezone")
    return parsed


def _sequence(name: str, value: Any) -> list[Any] | tuple[Any, ...]:
    if not isinstance(value, (list, tuple)):
        raise HandoffError(f"{name} must be a list or tuple")
    return value


def _path(value: Any) -> str:
    """Normalize portable relative paths for declaration comparison, without I/O."""
    value = _text("path", value)
    if any(ord(c) < 32 or ord(c) == 127 for c in value) or "\\" in value:
        raise HandoffError("paths must use printable POSIX components and forward slashes")
    path = PurePosixPath(value)
    if path.is_absolute() or PureWindowsPath(value).drive or ".." in path.parts:
        raise HandoffError("paths must be relative and cannot contain parent traversal")
    if str(path) == "." or any(c in value for c in "*?[]"):
        raise HandoffError("paths must name an entry; roots and globs are not supported")
    return str(path)


def _paths(name: str, value: Any) -> tuple[str, ...]:
    items = _sequence(name, value)
    for item in items:
        _path(item)
    return tuple(items)


def _records(name: str, value: Any, *, unknown: bool = False) -> tuple[Mapping[str, Any], ...]:
    keys = {"id", "text", "protected", "requiredFor"} if unknown else {"id", "text"}
    records = []
    seen = set()
    for item in _sequence(name, value):
        if not isinstance(item, Mapping) or set(item) != keys:
            raise HandoffError(f"{name} entries must contain exactly {sorted(keys)}")
        for key in keys - {"protected"}:
            _text(f"{name}.{key}", item[key])
        if unknown and not isinstance(item["protected"], bool):
            raise HandoffError(f"{name}.protected must be boolean")
        if item["id"] in seen:
            raise HandoffError(f"{name} entry ids must be unique")
        seen.add(item["id"])
        records.append(MappingProxyType(dict(item)))
    return tuple(records)


def _object(name: str, value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise HandoffError(f"{name} must be an object containing exactly {sorted(keys)}")
    return value


def _within(path: str, boundary: str) -> bool:
    return path == boundary or path.startswith(boundary + "/")


@dataclass(frozen=True)
class HandoffResult:
    """Execution outcome report submitted by the receiving agent."""

    completed_by: str
    completed_at: str
    summary: str
    modified_files: tuple[str, ...] = ()
    receipt_digest: str = ""
    evidence_notes: str = ""

    def __post_init__(self) -> None:
        _text("completed_by", self.completed_by)
        _text("summary", self.summary)
        _timestamp("completed_at", self.completed_at)
        _text("receipt_digest", self.receipt_digest, empty=True)
        _text("evidence_notes", self.evidence_notes, empty=True)
        object.__setattr__(self, "modified_files", _paths("modified_files", self.modified_files))

    def to_dict(self) -> dict[str, Any]:
        return {
            "completed_by": self.completed_by,
            "completed_at": self.completed_at,
            "summary": self.summary,
            "modified_files": list(self.modified_files),
            "receipt_digest": self.receipt_digest,
            "evidence_notes": self.evidence_notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HandoffResult:
        data = _object(
            "result",
            data,
            {
                "completed_by",
                "completed_at",
                "summary",
                "modified_files",
                "receipt_digest",
                "evidence_notes",
            },
        )
        return cls(
            completed_by=data["completed_by"],
            completed_at=data["completed_at"],
            summary=data["summary"],
            modified_files=_paths("modified_files", data["modified_files"]),
            receipt_digest=data["receipt_digest"],
            evidence_notes=data["evidence_notes"],
        )


@dataclass(frozen=True)
class HandoffCapsule:
    """Immutable declared task. Its digest checks consistency, not signer identity."""

    capsule_id: str
    created_at: str
    issuer: str
    recipient: str
    scope: str
    purpose: str
    risk: str
    target_paths: tuple[str, ...]
    protected_paths: tuple[str, ...]
    invariants: tuple[Mapping[str, str], ...]
    recovery: tuple[Mapping[str, str], ...]
    unknowns: tuple[Mapping[str, Any], ...]
    status: CapsuleStatus = "PROPOSED"
    authority_id: str | None = None
    result: HandoffResult | None = None
    schema: str = HANDOFF_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.risk, str) or self.risk not in VALID_RISKS:
            raise HandoffError(f"risk must be one of {sorted(VALID_RISKS)}, got '{self.risk}'")
        if isinstance(self.purpose, str) and not self.purpose.strip():
            raise HandoffError("purpose cannot be empty")
        if isinstance(self.capsule_id, str) and not self.capsule_id.strip():
            raise HandoffError("capsule_id cannot be empty")
        for name in ("capsule_id", "issuer", "recipient", "scope", "purpose"):
            _text(name, getattr(self, name))
        _timestamp("created_at", self.created_at)
        if self.schema != HANDOFF_SCHEMA_VERSION:
            raise HandoffError(f"Unrecognised schema: {self.schema}")
        if not isinstance(self.status, str) or self.status not in {
            "PROPOSED",
            "APPROVED",
            "EXECUTED",
            "VERIFIED",
            "REJECTED",
        }:
            raise HandoffError("unrecognised capsule status")
        if self.authority_id is not None:
            _text("authority_id", self.authority_id)
        for name in ("target_paths", "protected_paths"):
            object.__setattr__(self, name, _paths(name, getattr(self, name)))
        for name in ("invariants", "recovery", "unknowns"):
            object.__setattr__(
                self, name, _records(name, getattr(self, name), unknown=name == "unknowns")
            )
        if self.result is not None and not isinstance(self.result, HandoffResult):
            raise HandoffError("result must be a HandoffResult or null")

    def _task_payload(self) -> dict[str, Any]:
        """Core task specification payload without status/result."""
        return {
            "schema": self.schema,
            "capsule_id": self.capsule_id,
            "created_at": self.created_at,
            "issuer": self.issuer,
            "recipient": self.recipient,
            "scope": self.scope,
            "purpose": self.purpose,
            "risk": self.risk,
            "target_paths": sorted(self.target_paths),
            "protected_paths": sorted(self.protected_paths),
            "invariants": [dict(item) for item in self.invariants],
            "recovery": [dict(item) for item in self.recovery],
            "unknowns": [dict(item) for item in self.unknowns],
            "authority_id": self.authority_id,
        }

    def task_digest(self) -> str:
        """Compute deterministic SHA-256 digest of the task specification."""
        return _sha256_hex(self._task_payload())

    def to_dict(self) -> dict[str, Any]:
        """Serialize complete capsule to JSON-compatible dictionary."""
        out = self._task_payload()
        out["status"] = self.status
        out["task_digest"] = self.task_digest()
        out["result"] = self.result.to_dict() if self.result else None
        return out

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HandoffCapsule:
        data = _object(
            "capsule",
            data,
            {
                "schema",
                "capsule_id",
                "created_at",
                "issuer",
                "recipient",
                "scope",
                "purpose",
                "risk",
                "target_paths",
                "protected_paths",
                "invariants",
                "recovery",
                "unknowns",
                "authority_id",
                "status",
                "result",
                "task_digest",
            },
        )
        schema = data["schema"]
        if schema != HANDOFF_SCHEMA_VERSION:
            raise HandoffError(f"Unrecognised schema: {schema} (expected {HANDOFF_SCHEMA_VERSION})")

        res_data = data["result"]
        res_obj = HandoffResult.from_dict(res_data) if res_data is not None else None

        capsule = cls(
            capsule_id=data["capsule_id"],
            created_at=data["created_at"],
            issuer=data["issuer"],
            recipient=data["recipient"],
            scope=data["scope"],
            purpose=data["purpose"],
            risk=data["risk"],
            target_paths=_paths("target_paths", data["target_paths"]),
            protected_paths=_paths("protected_paths", data["protected_paths"]),
            invariants=_records("invariants", data["invariants"]),
            recovery=_records("recovery", data["recovery"]),
            unknowns=_records("unknowns", data["unknowns"], unknown=True),
            status=data["status"],
            authority_id=data["authority_id"],
            result=res_obj,
            schema=schema,
        )
        if data["task_digest"] != capsule.task_digest():
            raise HandoffError("task_digest does not match the serialized task specification")
        return capsule

    def to_agent_state_packet(self) -> AgentStatePacket:
        """Encode the declaration without inventing approval or a recovery path.

        The packet schema represents unknowns by identifiers. Their original
        wording is retained in the protected claim, alongside that index.
        """
        authority_entry = []
        if self.authority_id is not None:
            authority_entry.append(
                {
                    "id": self.authority_id,
                    "scope": self.scope,
                    "text": (
                        f"Declared authority label supplied by {self.issuer}; identity unverified"
                    ),
                }
            )

        evidence_entry = [
            {
                "id": f"EVID-{idx + 1}",
                "text": f"Declared target path: {p}",
                "provenance": f"handoff:{self.capsule_id}",
            }
            for idx, p in enumerate(self.target_paths)
        ]

        inv_entry = [
            {"id": str(i.get("id", f"INV-{idx + 1}")), "text": str(i.get("text", ""))}
            for idx, i in enumerate(self.invariants)
        ]

        rec_entry = [
            {"id": str(r.get("id", f"REC-{idx + 1}")), "text": str(r.get("text", ""))}
            for idx, r in enumerate(self.recovery)
        ]

        unk_entry = [
            {
                "id": str(u.get("id", f"UNK-{idx + 1}")),
                "protected": bool(u.get("protected", bool(rec_entry))),
                "requiredFor": str(u.get("requiredFor", self.scope)),
            }
            for idx, u in enumerate(self.unknowns)
        ]

        return AgentStatePacket(
            id=self.capsule_id,
            purpose=self.purpose,
            claim=_canonical_json(
                {
                    "declaration": (
                        f"Handoff from {self.issuer} to {self.recipient} in scope {self.scope}"
                    ),
                    "unknown_questions": [dict(item) for item in self.unknowns],
                }
            ),
            risk=self.risk,
            invariants=inv_entry,
            recovery=rec_entry,
            unknowns=unk_entry,
            authority=authority_entry,
            participants=[self.issuer, self.recipient],
            evidence=evidence_entry,
        )

    def complete(
        self,
        *,
        completed_by: str,
        summary: str,
        modified_files: tuple[str, ...] | list[str] = (),
        receipt_digest: str = "",
        evidence_notes: str = "",
        now: str | None = None,
    ) -> HandoffCapsule:
        """Return a report of claimed execution; this method performs no task."""
        if self.result is not None or self.status not in {"PROPOSED", "APPROVED"}:
            raise HandoffError("a completion report already exists or the capsule is not open")
        _text("Execution summary", summary)

        res = HandoffResult(
            completed_by=completed_by,
            completed_at=now or dt.datetime.now(dt.timezone.utc).isoformat(),
            summary=summary,
            modified_files=_paths("modified_files", modified_files),
            receipt_digest=receipt_digest,
            evidence_notes=evidence_notes,
        )
        return HandoffCapsule(
            capsule_id=self.capsule_id,
            created_at=self.created_at,
            issuer=self.issuer,
            recipient=self.recipient,
            scope=self.scope,
            purpose=self.purpose,
            risk=self.risk,
            target_paths=self.target_paths,
            protected_paths=self.protected_paths,
            invariants=self.invariants,
            recovery=self.recovery,
            unknowns=self.unknowns,
            status="EXECUTED",
            authority_id=self.authority_id,
            result=res,
            schema=self.schema,
        )

    def render_card(self) -> str:
        """Render a terminal card displaying the capsule's boundaries and status."""
        lines = []
        width = 72
        border = "─" * width

        lines.append(f"┌{border}┐")
        title = f" LYCHEETAH HANDOFF CAPSULE · {self.capsule_id}"
        lines.append(f"│{title:<{width}}│")
        route = f" From: {self.issuer} ──► To: {self.recipient}"
        lines.append(f"│{route:<{width}}│")
        meta = f" Status: [{self.status}] · Risk: {self.risk} · Scope: {self.scope}"
        lines.append(f"│{meta:<{width}}│")
        lines.append(f"├{border}┤")

        # Purpose
        lines.append(f"│{' PURPOSE':<{width}}│")
        for chunk in _wrap_text(self.purpose, width - 4):
            lines.append(f"│  {chunk:<{width - 2}}│")
        lines.append(f"├{border}┤")

        # Protected paths
        lines.append(f"│{' PROTECTED PATHS (HANDS OFF)':<{width}}│")
        if self.protected_paths:
            for p in self.protected_paths:
                item = f"  ✖ {p}"
                lines.append(f"│{item:<{width}}│")
        else:
            lines.append(f"│{'  (None declared)':<{width}}│")
        lines.append(f"├{border}┤")

        # Invariants
        lines.append(f"│{' NON-NEGOTIABLE INVARIANTS':<{width}}│")
        if self.invariants:
            for inv in self.invariants:
                text = f"  [{inv.get('id', 'INV')}] {inv.get('text', '')}"
                for chunk in _wrap_text(text, width - 4):
                    lines.append(f"│  {chunk:<{width - 2}}│")
        else:
            lines.append(f"│{'  (None declared)':<{width}}│")
        lines.append(f"├{border}┤")

        # Recovery
        lines.append(f"│{' RECOVERY / ROLLBACK PATH':<{width}}│")
        if self.recovery:
            for rec in self.recovery:
                text = f"  ↺ [{rec.get('id', 'REC')}] {rec.get('text', '')}"
                for chunk in _wrap_text(text, width - 4):
                    lines.append(f"│  {chunk:<{width - 2}}│")
        else:
            lines.append(f"│{'  (None noted)':<{width}}│")
        lines.append(f"├{border}┤")

        # Result if executed
        if self.result:
            lines.append(f"│{' EXECUTION RESULT':<{width}}│")
            by_line = f"  Completed by: {self.result.completed_by} at {self.result.completed_at}"
            lines.append(f"│{by_line:<{width}}│")
            sum_line = f"  Summary: {self.result.summary}"
            for chunk in _wrap_text(sum_line, width - 4):
                lines.append(f"│  {chunk:<{width - 2}}│")
            if self.result.modified_files:
                lines.append(f"│{'  Modified Files:':<{width}}│")
                for f in self.result.modified_files:
                    lines.append(f"│    • {f:<{width - 6}}│")
            if self.result.receipt_digest:
                r_line = f"  Receipt: {self.result.receipt_digest[:16]}..."
                lines.append(f"│{r_line:<{width}}│")
            lines.append(f"├{border}┤")

        digest_line = f" Task Digest: {self.task_digest()[:24]}..."
        lines.append(f"│{digest_line:<{width}}│")
        lines.append(f"└{border}┘")
        return "\n".join(lines)


def _wrap_text(text: str, max_len: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    out = []
    cur: list[str] = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + len(cur) > max_len:
            out.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += len(w)
    if cur:
        out.append(" ".join(cur))
    return out


def create_capsule(
    *,
    purpose: str,
    issuer: str = "Mac",
    recipient: str = "Aetheron",
    scope: str = "code:write",
    risk: str = "MEDIUM",
    target_paths: list[str] | tuple[str, ...] = (),
    protected_paths: list[str] | tuple[str, ...] = (),
    invariants: list[str] | tuple[str, ...] = (),
    recovery: list[str] | tuple[str, ...] = (),
    unknowns: list[str] | tuple[str, ...] = (),
    authority_id: str | None = None,
    capsule_id: str | None = None,
    created_at: str | None = None,
) -> HandoffCapsule:
    """Create a new validated HandoffCapsule."""
    now_dt = dt.datetime.now(dt.timezone.utc)
    cid = (
        f"ho-{now_dt.strftime('%Y%m%d')}-{secrets.token_hex(4)}"
        if capsule_id is None
        else capsule_id
    )
    ts = now_dt.isoformat() if created_at is None else created_at

    inv_entries = tuple(
        {"id": f"INV-{idx + 1}", "text": text}
        for idx, text in enumerate(_sequence("invariants", invariants))
    )
    rec_entries = tuple(
        {"id": f"REC-{idx + 1}", "text": text}
        for idx, text in enumerate(_sequence("recovery", recovery))
    )
    unk_entries = tuple(
        {"id": f"UNK-{idx + 1}", "text": text, "protected": True, "requiredFor": scope}
        for idx, text in enumerate(_sequence("unknowns", unknowns))
    )

    return HandoffCapsule(
        capsule_id=cid,
        created_at=ts,
        issuer=issuer,
        recipient=recipient,
        scope=scope,
        purpose=purpose,
        risk=risk,
        target_paths=_paths("target_paths", target_paths),
        protected_paths=_paths("protected_paths", protected_paths),
        invariants=inv_entries,
        recovery=rec_entries,
        unknowns=unk_entries,
        status="PROPOSED",
        authority_id=authority_id,
    )


@dataclass(frozen=True)
class VerificationVerdict:
    """Result of verifying an executed capsule against its reference specification."""

    passed: bool
    status: str
    violations: tuple[str, ...]
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status,
            "violations": list(self.violations),
            "details": self.details,
        }


def verify_handoff(reference: HandoffCapsule, executed: HandoffCapsule) -> VerificationVerdict:
    """Check the reported declaration against its reference, without filesystem I/O.

    Path entries cover that entry and descendants, by whole POSIX components.
    Empty target_paths authorizes no declared file modifications. Passing does
    not prove the report is truthful, authenticate an issuer, or observe effects.
    """
    violations: list[str] = []

    # 1. Identity & Task Digest Check
    if reference.capsule_id != executed.capsule_id:
        violations.append(
            f"capsule_id mismatch: reference '{reference.capsule_id}' "
            f"vs executed '{executed.capsule_id}'"
        )

    if reference.task_digest() != executed.task_digest():
        violations.append("task specification was mutated after issuance (digest mismatch)")

    # 2. Status Check
    if executed.status != "EXECUTED":
        violations.append(f"capsule is not in EXECUTED status (current: '{executed.status}')")

    if not executed.result:
        violations.append("missing execution result in completed capsule")
        return VerificationVerdict(
            passed=False,
            status="REJECTED_NO_RESULT",
            violations=tuple(violations),
            details={"reference_id": reference.capsule_id},
        )

    # 3. Protected Paths Violation Check (Absolute Barrier)
    res = executed.result
    if res.completed_by != reference.recipient:
        violations.append(
            "completion recipient mismatch: completed_by must match the receiving seat"
        )
    if _timestamp("completed_at", res.completed_at) < _timestamp(
        "created_at", reference.created_at
    ):
        violations.append("completion timestamp precedes task creation")
    modified_set = {_path(path) for path in res.modified_files}
    protected_set = {_path(path) for path in reference.protected_paths}
    breached_paths = {path for path in modified_set if any(_within(path, p) for p in protected_set)}
    if breached_paths:
        violations.append(
            f"PROTECTED PATH VIOLATION: modified forbidden files: {sorted(breached_paths)}"
        )

    # 4. Scope Expansion Check (Target Paths)
    allowed_set = {_path(path) for path in reference.target_paths}
    unapproved = {path for path in modified_set if not any(_within(path, p) for p in allowed_set)}
    if unapproved:
        violations.append(
            f"SCOPE EXPANSION: modified files outside target_paths: {sorted(unapproved)}"
        )

    # 5. Invariant & Recovery Preservation Check via Compaction Shield
    ref_pkt = reference.to_agent_state_packet()
    exec_pkt = executed.to_agent_state_packet()
    compaction_report = CompactionShield.verify_integrity(ref_pkt, exec_pkt)

    if not compaction_report.get("is_safe", False):
        cls_name = compaction_report.get("classification")
        reason = compaction_report.get("reason", "")
        detail = f" ({reason})" if reason else ""
        violations.append(f"Compaction shield reported semantic divergence: {cls_name}{detail}")

    passed = len(violations) == 0
    status_label = "DECLARATIONS_MATCH" if passed else "REJECTED_VIOLATION"

    return VerificationVerdict(
        passed=passed,
        status=status_label,
        violations=tuple(violations),
        details={
            "capsule_id": reference.capsule_id,
            "modified_count": len(modified_set),
            "protected_checked": len(reference.protected_paths),
            "invariants_count": len(reference.invariants),
            "compaction_safe": compaction_report.get("is_safe", False),
            "verification_basis": "DECLARATIONS_ONLY",
            "filesystem_observed": False,
            "issuer_authenticated": False,
            "recovery_executed": False,
        },
    )
