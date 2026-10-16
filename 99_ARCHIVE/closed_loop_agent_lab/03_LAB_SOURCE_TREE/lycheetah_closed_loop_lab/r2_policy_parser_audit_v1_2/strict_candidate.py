"""Strict TextRule parser candidate for the expanded string-field contract."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping


class PolicyError(ValueError):
    """Fixture analogue of the upstream policy error."""


@dataclass(frozen=True)
class TextRule:
    rule_id: str
    pattern: str
    title: str
    description: str
    status_basis: str = ""

    def __post_init__(self) -> None:
        for field_name in ("rule_id", "pattern", "title", "description", "status_basis"):
            if not isinstance(getattr(self, field_name), str):
                raise PolicyError(f"text rule {field_name} must be a string")
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
        allowed = {"id", "pattern", "title", "description", "status_basis"}
        unknown = sorted(str(key) for key in data if key not in allowed)
        if unknown:
            raise PolicyError("text rule contains unknown fields: " + ", ".join(unknown))
        for field_name in ("id", "pattern", "title", "description", "status_basis"):
            if field_name in data and not isinstance(data[field_name], str):
                raise PolicyError(f"text rule.{field_name} must be a string")
        return cls(
            rule_id=data["id"],
            pattern=data["pattern"],
            title=data.get("title", data["id"]),
            description=data.get("description", "Policy text rule matched"),
            status_basis=data.get("status_basis", ""),
        )
