"""Isolated candidate for strict TextRule.from_dict type validation."""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any, Mapping

class PolicyError(ValueError):
    pass

@dataclass(frozen=True)
class TextRule:
    rule_id: str
    pattern: str
    title: str
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, str) or not isinstance(self.pattern, str):
            raise PolicyError("text rule id and pattern must be strings")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", self.rule_id):
            raise PolicyError(f"invalid text rule id: {self.rule_id!r}")
        if not self.pattern:
            raise PolicyError(f"text rule {self.rule_id!r} pattern must be non-empty")
        try:
            re.compile(self.pattern)
        except re.error as exc:
            raise PolicyError(f"invalid regex in {self.rule_id}: {exc}") from exc

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TextRule":
        if not isinstance(data, Mapping):
            raise PolicyError("text rule must be an object")
        if "id" not in data or "pattern" not in data:
            raise PolicyError("text rule requires id and pattern")
        for field in ("id", "pattern"):
            if not isinstance(data[field], str):
                raise PolicyError(f"text rule.{field} must be a string")
        for field in ("title", "description"):
            if field in data and not isinstance(data[field], str):
                raise PolicyError(f"text rule.{field} must be a string")
        allowed = {"id", "pattern", "title", "description", "phases", "requested_disposition", "claim_status", "deterministic", "severity", "status_basis", "ignore_case"}
        unknown = sorted(str(key) for key in data if key not in allowed)
        if unknown:
            raise PolicyError("text rule contains unknown fields: " + ", ".join(unknown))
        return cls(data["id"], data["pattern"], data.get("title", data["id"]), data.get("description", "Policy text rule matched"))
