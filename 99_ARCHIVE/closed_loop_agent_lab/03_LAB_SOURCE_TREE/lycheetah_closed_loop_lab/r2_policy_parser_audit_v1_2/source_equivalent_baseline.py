"""Focused source-equivalent fixture for the upstream TextRule parser.

This is not the installed package. It retains the specific conversion behavior
observed in Lycheetah-Framework's TextRule.from_dict at blob
913006991327ac40bf34e96fce591ca100334ca9.
"""
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
    title: Any
    description: Any
    status_basis: Any = ""

    def __post_init__(self) -> None:
        # The upstream class validates id and pattern types, but does not
        # validate the optional descriptive text types here.
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
        if self.claim_status_active and not self.status_basis.strip():
            raise PolicyError("ACTIVE rule requires a non-empty status_basis")

    @property
    def claim_status_active(self) -> bool:
        return False

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
        # Matches the upstream string coercions under audit.
        return cls(
            rule_id=str(data["id"]),
            pattern=str(data["pattern"]),
            title=str(data.get("title", data["id"])),
            description=str(data.get("description", "Policy text rule matched")),
            status_basis=str(data.get("status_basis", "")),
        )
