"""Assurance Receipt issuance, integrity verification, and JSONL chains."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from .jsonutil import jsonable, sha256_json
from .models import Disposition, Finding, capped_disposition, strongest


SCHEMA_VERSION = "0.1"
CANONICALIZATION = "lycheetah-json-v1"


class ReceiptError(ValueError):
    """Raised when a receipt or chain cannot be safely accepted."""


@dataclass(frozen=True)
class VerificationReport:
    valid: bool
    digest: str
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    hmac_authenticated: bool = False


@dataclass(frozen=True)
class LogVerificationReport:
    valid: bool
    receipt_count: int
    head_digest: Optional[str]
    tail_digest: Optional[str]
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssuranceReceipt:
    receipt_id: str
    issued_at: str
    runtime: Mapping[str, Any]
    policy: Mapping[str, Any]
    event: Mapping[str, Any]
    decision: Disposition
    findings: tuple[Finding, ...]
    metrics: Mapping[str, Any]
    limitations: tuple[str, ...]
    lineage: Mapping[str, Any]
    integrity: Mapping[str, Any]
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def issue(
        cls,
        *,
        runtime: Mapping[str, Any],
        policy: Mapping[str, Any],
        event: Mapping[str, Any],
        decision: Disposition,
        findings: Iterable[Finding],
        metrics: Mapping[str, Any],
        limitations: Iterable[str],
        trace_id: str,
        previous_receipt_sha256: Optional[str] = None,
        hmac_secret: Optional[bytes] = None,
        hmac_key_id: Optional[str] = None,
        issued_at: Optional[str] = None,
        receipt_id: Optional[str] = None,
    ) -> "AssuranceReceipt":
        if hmac_secret is not None:
            if not isinstance(hmac_secret, bytes) or not hmac_secret:
                raise ReceiptError("hmac_secret must be non-empty bytes")
            if not isinstance(hmac_key_id, str) or not hmac_key_id:
                raise ReceiptError(
                    "hmac_key_id must be a non-empty string when hmac_secret is supplied"
                )
        body = {
            "schema_version": SCHEMA_VERSION,
            "receipt_id": receipt_id or f"urn:uuid:{uuid.uuid4()}",
            "issued_at": issued_at or _utc_now(),
            "runtime": jsonable(runtime),
            "policy": jsonable(policy),
            "event": jsonable(event),
            "decision": Disposition(decision).value,
            "findings": [finding.to_dict() for finding in findings],
            "metrics": jsonable(metrics),
            "limitations": [str(item) for item in limitations],
            "lineage": {
                "trace_id": str(trace_id),
                "previous_receipt_sha256": previous_receipt_sha256,
            },
        }
        digest = sha256_json(body)
        seal = None
        if hmac_secret is not None:
            seal = {
                "algorithm": "hmac-sha256",
                "key_id": hmac_key_id,
                "value": hmac.new(
                    hmac_secret, digest.encode("ascii"), hashlib.sha256
                ).hexdigest(),
            }
        return cls.from_dict(
            {
                **body,
                "integrity": {
                    "algorithm": "sha256",
                    "canonicalization": CANONICALIZATION,
                    "digest": digest,
                    "seal": seal,
                },
            }
        )

    def body_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "receipt_id": self.receipt_id,
            "issued_at": self.issued_at,
            "runtime": jsonable(self.runtime),
            "policy": jsonable(self.policy),
            "event": jsonable(self.event),
            "decision": self.decision.value,
            "findings": [finding.to_dict() for finding in self.findings],
            "metrics": jsonable(self.metrics),
            "limitations": list(self.limitations),
            "lineage": jsonable(self.lineage),
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.body_dict(), "integrity": jsonable(self.integrity)}

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=indent is None,
            separators=(",", ":") if indent is None else None,
            indent=indent,
        )

    @property
    def digest(self) -> str:
        return str(self.integrity.get("digest", ""))

    @property
    def previous_digest(self) -> Optional[str]:
        value = self.lineage.get("previous_receipt_sha256")
        return str(value) if value is not None else None

    def verify(self, hmac_secret: Optional[bytes] = None) -> VerificationReport:
        errors: list[str] = []
        warnings: list[str] = []
        if hmac_secret is not None and (
            not isinstance(hmac_secret, bytes) or not hmac_secret
        ):
            errors.append("HMAC verification secret must be non-empty bytes")
            hmac_secret = None
        if self.schema_version != SCHEMA_VERSION:
            errors.append(
                f"unsupported schema_version {self.schema_version!r}; expected {SCHEMA_VERSION!r}"
            )
        if self.integrity.get("algorithm") != "sha256":
            errors.append("integrity.algorithm must be 'sha256'")
        if self.integrity.get("canonicalization") != CANONICALIZATION:
            errors.append(
                f"integrity.canonicalization must be {CANONICALIZATION!r}"
            )
        expected = sha256_json(self.body_dict())
        stored = self.digest
        if not hmac.compare_digest(expected, stored):
            errors.append("receipt body digest mismatch")

        for finding in self.findings:
            expected_disposition, expected_cap_reason = capped_disposition(
                finding.requested_disposition,
                finding.claim_status,
                finding.deterministic,
            )
            if finding.effective_disposition != expected_disposition:
                errors.append(
                    f"finding {finding.finding_id}: effective disposition violates "
                    "evidence cap"
                )
            if finding.cap_reason != expected_cap_reason:
                errors.append(
                    f"finding {finding.finding_id}: cap_reason does not match evidence cap"
                )
        expected_decision = strongest(
            [finding.effective_disposition for finding in self.findings]
        )
        if self.decision != expected_decision:
            errors.append(
                "receipt decision does not match strongest effective finding "
                f"({self.decision.value} != {expected_decision.value})"
            )

        authenticated = False
        seal = self.integrity.get("seal")
        if seal is not None:
            if not isinstance(seal, Mapping):
                errors.append("integrity.seal must be an object or null")
            elif seal.get("algorithm") != "hmac-sha256":
                errors.append("unsupported receipt seal algorithm")
            elif not isinstance(seal.get("key_id"), str) or not seal.get("key_id"):
                errors.append("HMAC seal key_id must be a non-empty string")
            elif not isinstance(seal.get("value"), str) or not _is_sha256(
                seal.get("value", "")
            ):
                errors.append("HMAC seal value must be 64 lowercase hexadecimal characters")
            elif hmac_secret is None:
                warnings.append("HMAC seal present but no verification key was supplied")
            else:
                expected_mac = hmac.new(
                    hmac_secret, stored.encode("ascii"), hashlib.sha256
                ).hexdigest()
                if hmac.compare_digest(expected_mac, str(seal.get("value", ""))):
                    authenticated = True
                else:
                    errors.append("HMAC seal mismatch")
        elif hmac_secret is not None:
            warnings.append("verification key supplied but receipt has no HMAC seal")

        return VerificationReport(
            valid=not errors,
            digest=expected,
            errors=tuple(errors),
            warnings=tuple(warnings),
            hmac_authenticated=authenticated,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AssuranceReceipt":
        required = {
            "schema_version",
            "receipt_id",
            "issued_at",
            "runtime",
            "policy",
            "event",
            "decision",
            "findings",
            "metrics",
            "limitations",
            "lineage",
            "integrity",
        }
        missing = sorted(required.difference(data))
        if missing:
            raise ReceiptError(f"receipt missing required fields: {', '.join(missing)}")
        unknown = sorted(set(data).difference(required))
        if unknown:
            raise ReceiptError(f"receipt contains unknown fields: {', '.join(unknown)}")
        for key in ("runtime", "policy", "event", "metrics", "lineage", "integrity"):
            if not isinstance(data[key], Mapping):
                raise ReceiptError(f"receipt {key} must be an object")
        if not isinstance(data["findings"], list):
            raise ReceiptError("receipt findings must be an array")
        if not isinstance(data["limitations"], list) or any(
            not isinstance(item, str) for item in data["limitations"]
        ):
            raise ReceiptError("receipt limitations must be an array of strings")
        if not isinstance(data["receipt_id"], str) or not data["receipt_id"]:
            raise ReceiptError("receipt_id must be a non-empty string")
        if not isinstance(data["issued_at"], str) or not data["issued_at"]:
            raise ReceiptError("issued_at must be a non-empty string")
        try:
            return cls(
                schema_version=str(data["schema_version"]),
                receipt_id=str(data["receipt_id"]),
                issued_at=str(data["issued_at"]),
                runtime=jsonable(data["runtime"]),
                policy=jsonable(data["policy"]),
                event=jsonable(data["event"]),
                decision=Disposition(data["decision"]),
                findings=tuple(Finding.from_dict(item) for item in data["findings"]),
                metrics=jsonable(data["metrics"]),
                limitations=tuple(str(item) for item in data["limitations"]),
                lineage=jsonable(data["lineage"]),
                integrity=jsonable(data["integrity"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ReceiptError(f"invalid receipt: {exc}") from exc

    @classmethod
    def from_json(cls, text: str) -> "AssuranceReceipt":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ReceiptError(f"invalid receipt JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ReceiptError("receipt JSON must contain an object")
        return cls.from_dict(data)


class ReceiptLog:
    """Single-writer JSONL receipt chain.

    The append operation verifies the existing chain and fsyncs the new record.
    Cross-process locking is intentionally not claimed in v0.1.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def read(self) -> list[AssuranceReceipt]:
        if not self.path.exists():
            return []
        receipts = []
        for line_number, line in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                receipts.append(AssuranceReceipt.from_json(line))
            except ReceiptError as exc:
                raise ReceiptError(f"line {line_number}: {exc}") from exc
        return receipts

    @property
    def tail_digest(self) -> Optional[str]:
        receipts = self.read()
        return receipts[-1].digest if receipts else None

    def append(
        self,
        receipt: AssuranceReceipt,
        hmac_keys: Optional[Mapping[str, bytes]] = None,
    ) -> None:
        report = self.verify(hmac_keys)
        if not report.valid:
            raise ReceiptError(
                "refusing to append to an invalid receipt log: " + "; ".join(report.errors)
            )
        expected_previous = report.tail_digest
        if receipt.previous_digest != expected_previous:
            raise ReceiptError(
                "receipt previous digest does not match current log tail "
                f"({receipt.previous_digest!r} != {expected_previous!r})"
            )
        secret = None
        seal = receipt.integrity.get("seal")
        if hmac_keys is not None:
            if not isinstance(seal, Mapping):
                raise ReceiptError(
                    "HMAC-authenticated append requested but new receipt has no seal"
                )
            key_id = str(seal.get("key_id", ""))
            secret = hmac_keys.get(key_id)
            if secret is None:
                raise ReceiptError(f"no HMAC key for new receipt key_id {key_id!r}")
        verification = receipt.verify(secret)
        if not verification.valid:
            raise ReceiptError(
                "refusing to append invalid receipt: " + "; ".join(verification.errors)
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(receipt.to_json(indent=None))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

    def verify(
        self,
        hmac_keys: Optional[Mapping[str, bytes]] = None,
    ) -> LogVerificationReport:
        errors: list[str] = []
        warnings: list[str] = []
        try:
            receipts = self.read()
        except ReceiptError as exc:
            return LogVerificationReport(
                valid=False,
                receipt_count=0,
                head_digest=None,
                tail_digest=None,
                errors=(str(exc),),
            )

        previous = None
        seen_ids: set[str] = set()
        for index, receipt in enumerate(receipts, start=1):
            secret = None
            seal = receipt.integrity.get("seal")
            if hmac_keys is not None:
                if not isinstance(seal, Mapping):
                    errors.append(
                        f"line {index}: HMAC authentication requested but receipt has no seal"
                    )
                else:
                    key_id = str(seal.get("key_id", ""))
                    secret = hmac_keys.get(key_id)
                    if secret is None:
                        errors.append(
                            f"line {index}: no HMAC key for key_id {key_id!r}"
                        )
            report = receipt.verify(secret)
            errors.extend(f"line {index}: {item}" for item in report.errors)
            warnings.extend(f"line {index}: {item}" for item in report.warnings)
            if hmac_keys is not None and not report.hmac_authenticated:
                errors.append(f"line {index}: receipt was not HMAC-authenticated")
            if receipt.receipt_id in seen_ids:
                errors.append(f"line {index}: duplicate receipt_id {receipt.receipt_id!r}")
            seen_ids.add(receipt.receipt_id)
            if receipt.previous_digest != previous:
                errors.append(
                    f"line {index}: chain link mismatch "
                    f"({receipt.previous_digest!r} != {previous!r})"
                )
            previous = receipt.digest

        return LogVerificationReport(
            valid=not errors,
            receipt_count=len(receipts),
            head_digest=receipts[0].digest if receipts else None,
            tail_digest=receipts[-1].digest if receipts else None,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )


def load_receipt(path: str | Path) -> AssuranceReceipt:
    try:
        return AssuranceReceipt.from_json(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ReceiptError(f"cannot read receipt {path}: {exc}") from exc


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)
