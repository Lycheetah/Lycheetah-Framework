"""Versioned policy-as-data for the Lycheetah Assurance Runtime."""

from __future__ import annotations

import fnmatch
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .jsonutil import sha256_json
from .models import ClaimStatus, Disposition, Phase, Severity


class PolicyError(ValueError):
    """Raised when a policy cannot be interpreted without guessing."""


DEFAULT_SENSITIVE_ARGUMENT_KEYS = (
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "cookie",
    "private_key",
    "credential",
)

DEFAULT_DENIED_TOOLS = (
    "shell",
    "shell.*",
    "shell_*",
    "exec",
    "exec.*",
    "exec_*",
    "subprocess*",
    "database.drop*",
    "identity.delete*",
)

DEFAULT_BLOCKED_SCOPES = (
    "production.shell",
    "identity.admin",
    "secrets.*",
)


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise PolicyError(f"{path} must be an object")
    return value


def _reject_unknown(
    data: Mapping[str, Any], allowed: set[str], path: str
) -> None:
    unknown = sorted(str(key) for key in data if key not in allowed)
    if unknown:
        raise PolicyError(f"{path} contains unknown fields: {', '.join(unknown)}")


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        raise PolicyError(f"{path} must be a boolean")
    return value


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PolicyError(f"{path} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise PolicyError(f"{path} must be a finite number")
    return number


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PolicyError(f"{path} must be an integer")
    return value


def _strings(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise PolicyError(f"{path} must be an array of strings")
    if any(not isinstance(item, str) or not item for item in value):
        raise PolicyError(f"{path} must contain non-empty strings")
    result = tuple(value)
    if len(result) != len(set(result)):
        raise PolicyError(f"{path} must not contain duplicates")
    return result


@dataclass(frozen=True)
class TextRule:
    rule_id: str
    pattern: str
    title: str
    description: str
    phases: tuple[Phase, ...] = (Phase.INPUT, Phase.OUTPUT)
    requested_disposition: Disposition = Disposition.REVIEW
    claim_status: ClaimStatus = ClaimStatus.SCAFFOLD
    deterministic: bool = False
    severity: Severity = Severity.MEDIUM
    status_basis: str = ""
    ignore_case: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not isinstance(self.pattern, str):
            raise PolicyError("text rule id and pattern must be strings")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", self.rule_id):
            raise PolicyError(f"invalid text rule id: {self.rule_id!r}")
        if not self.pattern:
            raise PolicyError(f"text rule {self.rule_id!r} pattern must be non-empty")
        if len(self.pattern) > 4096:
            raise PolicyError(f"text rule {self.rule_id!r} pattern exceeds 4096 characters")
        if not self.phases or any(
            not isinstance(phase, Phase)
            or phase not in (Phase.INPUT, Phase.OUTPUT)
            for phase in self.phases
        ):
            raise PolicyError(
                f"text rule {self.rule_id!r} phases must contain input and/or output"
            )
        if type(self.deterministic) is not bool or type(self.ignore_case) is not bool:
            raise PolicyError(
                f"text rule {self.rule_id!r} deterministic and ignore_case must be booleans"
            )
        try:
            re.compile(self.pattern, re.IGNORECASE if self.ignore_case else 0)
        except re.error as exc:
            raise PolicyError(f"invalid regex in {self.rule_id}: {exc}") from exc
        if self.claim_status == ClaimStatus.ACTIVE and not self.status_basis.strip():
            raise PolicyError(
                f"ACTIVE rule {self.rule_id!r} requires a non-empty status_basis"
            )

    def matches(self, text: str, phase: Phase) -> bool:
        if phase not in self.phases:
            return False
        flags = re.IGNORECASE if self.ignore_case else 0
        return re.search(self.pattern, text, flags) is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.rule_id,
            "pattern": self.pattern,
            "title": self.title,
            "description": self.description,
            "phases": [phase.value for phase in self.phases],
            "requested_disposition": self.requested_disposition.value,
            "claim_status": self.claim_status.value,
            "deterministic": self.deterministic,
            "severity": self.severity.value,
            "status_basis": self.status_basis,
            "ignore_case": self.ignore_case,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TextRule":
        data = _mapping(data, "text rule")
        _reject_unknown(
            data,
            {
                "id",
                "pattern",
                "title",
                "description",
                "phases",
                "requested_disposition",
                "claim_status",
                "deterministic",
                "severity",
                "status_basis",
                "ignore_case",
            },
            "text rule",
        )
        if "id" not in data or "pattern" not in data:
            raise PolicyError("text rule requires id and pattern")
        phases = _strings(data.get("phases", ["input", "output"]), "text rule.phases")
        return cls(
            rule_id=str(data["id"]),
            pattern=str(data["pattern"]),
            title=str(data.get("title", data["id"])),
            description=str(data.get("description", "Policy text rule matched")),
            phases=tuple(Phase(item) for item in phases),
            requested_disposition=Disposition(data.get("requested_disposition", "REVIEW")),
            claim_status=ClaimStatus(data.get("claim_status", "SCAFFOLD")),
            deterministic=_boolean(data.get("deterministic", False), "text rule.deterministic"),
            severity=Severity(data.get("severity", "MEDIUM")),
            status_basis=str(data.get("status_basis", "")),
            ignore_case=_boolean(data.get("ignore_case", True), "text rule.ignore_case"),
        )


@dataclass(frozen=True)
class AssurancePolicy:
    policy_id: str = "lycheetah.default"
    version: str = "0.1.0"
    description: str = "Conservative provider-neutral assurance defaults"
    manipulation_review_threshold: float = 0.25
    aura_review_below_percent: float = 70.0
    max_text_characters: int = 20_000
    require_approval_for_side_effects: bool = True
    denied_tools: tuple[str, ...] = DEFAULT_DENIED_TOOLS
    review_tools: tuple[str, ...] = ()
    tool_allowlist: tuple[str, ...] = ()
    blocked_scopes: tuple[str, ...] = DEFAULT_BLOCKED_SCOPES
    text_rules: tuple[TextRule, ...] = ()
    capture_content: bool = False
    capture_arguments: bool = False
    capture_evidence_spans: bool = False
    sensitive_argument_keys: tuple[str, ...] = DEFAULT_SENSITIVE_ARGUMENT_KEYS

    def __post_init__(self) -> None:
        if (
            not isinstance(self.policy_id, str)
            or not isinstance(self.version, str)
            or not isinstance(self.description, str)
        ):
            raise PolicyError("policy id and version must be strings")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", self.policy_id):
            raise PolicyError(f"invalid policy id: {self.policy_id!r}")
        if not self.version.strip():
            raise PolicyError("policy version must be non-empty")
        if (
            isinstance(self.manipulation_review_threshold, bool)
            or not isinstance(self.manipulation_review_threshold, (int, float))
            or not math.isfinite(self.manipulation_review_threshold)
            or not 0.0 <= self.manipulation_review_threshold <= 1.0
        ):
            raise PolicyError("manipulation_review_threshold must be in [0, 1]")
        if (
            isinstance(self.aura_review_below_percent, bool)
            or not isinstance(self.aura_review_below_percent, (int, float))
            or not math.isfinite(self.aura_review_below_percent)
            or not 0.0 <= self.aura_review_below_percent <= 100.0
        ):
            raise PolicyError("aura_review_below_percent must be in [0, 100]")
        if (
            isinstance(self.max_text_characters, bool)
            or not isinstance(self.max_text_characters, int)
            or not 1 <= self.max_text_characters <= 2_000_000
        ):
            raise PolicyError("max_text_characters must be an integer in [1, 2000000]")
        for name in (
            "require_approval_for_side_effects",
            "capture_content",
            "capture_arguments",
            "capture_evidence_spans",
        ):
            if type(getattr(self, name)) is not bool:
                raise PolicyError(f"{name} must be a boolean")
        for name in (
            "denied_tools",
            "review_tools",
            "tool_allowlist",
            "blocked_scopes",
            "sensitive_argument_keys",
        ):
            _strings(getattr(self, name), name)
        if any(not isinstance(rule, TextRule) for rule in self.text_rules):
            raise PolicyError("text_rules must contain TextRule instances")
        rule_ids = [rule.rule_id for rule in self.text_rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise PolicyError("text rule ids must be unique")

    def tool_matches(self, tool_name: str, patterns: Sequence[str]) -> bool:
        return any(fnmatch.fnmatchcase(tool_name, pattern) for pattern in patterns)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.policy_id,
            "version": self.version,
            "description": self.description,
            "text": {
                "manipulation_review_threshold": self.manipulation_review_threshold,
                "aura_review_below_percent": self.aura_review_below_percent,
                "max_text_characters": self.max_text_characters,
                "rules": [rule.to_dict() for rule in self.text_rules],
            },
            "tools": {
                "require_approval_for_side_effects": self.require_approval_for_side_effects,
                "denied": list(self.denied_tools),
                "review": list(self.review_tools),
                "allowlist": list(self.tool_allowlist),
                "blocked_scopes": list(self.blocked_scopes),
            },
            "privacy": {
                "capture_content": self.capture_content,
                "capture_arguments": self.capture_arguments,
                "capture_evidence_spans": self.capture_evidence_spans,
                "sensitive_argument_keys": list(self.sensitive_argument_keys),
            },
        }

    @property
    def digest(self) -> str:
        return sha256_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AssurancePolicy":
        data = _mapping(data, "policy")
        _reject_unknown(
            data,
            {"id", "version", "description", "text", "tools", "privacy"},
            "policy",
        )
        if "id" not in data or "version" not in data:
            raise PolicyError("policy requires id and version")
        if not isinstance(data["id"], str) or not isinstance(data["version"], str):
            raise PolicyError("policy id and version must be strings")
        if "description" in data and not isinstance(data["description"], str):
            raise PolicyError("policy.description must be a string")

        text = _mapping(data.get("text", {}), "policy.text")
        tools = _mapping(data.get("tools", {}), "policy.tools")
        privacy = _mapping(data.get("privacy", {}), "policy.privacy")
        _reject_unknown(
            text,
            {
                "manipulation_review_threshold",
                "aura_review_below_percent",
                "max_text_characters",
                "rules",
            },
            "policy.text",
        )
        _reject_unknown(
            tools,
            {
                "require_approval_for_side_effects",
                "denied",
                "review",
                "allowlist",
                "blocked_scopes",
            },
            "policy.tools",
        )
        _reject_unknown(
            privacy,
            {
                "capture_content",
                "capture_arguments",
                "capture_evidence_spans",
                "sensitive_argument_keys",
            },
            "policy.privacy",
        )
        rules = text.get("rules", [])
        if not isinstance(rules, list):
            raise PolicyError("policy.text.rules must be an array")
        return cls(
            policy_id=data["id"],
            version=data["version"],
            description=data.get("description", ""),
            manipulation_review_threshold=_number(
                text.get("manipulation_review_threshold", 0.25),
                "policy.text.manipulation_review_threshold",
            ),
            aura_review_below_percent=_number(
                text.get("aura_review_below_percent", 70.0),
                "policy.text.aura_review_below_percent",
            ),
            max_text_characters=_integer(
                text.get("max_text_characters", 20_000),
                "policy.text.max_text_characters",
            ),
            require_approval_for_side_effects=_boolean(
                tools.get("require_approval_for_side_effects", True),
                "policy.tools.require_approval_for_side_effects",
            ),
            denied_tools=_strings(
                tools.get("denied", DEFAULT_DENIED_TOOLS),
                "policy.tools.denied",
            ),
            review_tools=_strings(tools.get("review", []), "policy.tools.review"),
            tool_allowlist=_strings(
                tools.get("allowlist", []), "policy.tools.allowlist"
            ),
            blocked_scopes=_strings(
                tools.get("blocked_scopes", DEFAULT_BLOCKED_SCOPES),
                "policy.tools.blocked_scopes",
            ),
            text_rules=tuple(TextRule.from_dict(item) for item in rules),
            capture_content=_boolean(
                privacy.get("capture_content", False),
                "policy.privacy.capture_content",
            ),
            capture_arguments=_boolean(
                privacy.get("capture_arguments", False),
                "policy.privacy.capture_arguments",
            ),
            capture_evidence_spans=_boolean(
                privacy.get("capture_evidence_spans", False),
                "policy.privacy.capture_evidence_spans",
            ),
            sensitive_argument_keys=_strings(
                privacy.get(
                    "sensitive_argument_keys", DEFAULT_SENSITIVE_ARGUMENT_KEYS
                ),
                "policy.privacy.sensitive_argument_keys",
            ),
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "AssurancePolicy":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PolicyError(f"cannot load policy {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise PolicyError("policy JSON must contain an object")
        return cls.from_dict(data)


def default_policy() -> AssurancePolicy:
    return AssurancePolicy()
