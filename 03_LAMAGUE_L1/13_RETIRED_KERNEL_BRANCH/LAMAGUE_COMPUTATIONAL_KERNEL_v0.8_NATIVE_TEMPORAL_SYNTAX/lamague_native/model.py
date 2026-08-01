from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class SourceStatement:
    keyword: str
    positional: tuple[str, ...]
    options: dict[str, Any]
    raw: str
    index: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NativeProgram:
    packet_id: str
    observability_class: str
    statements: tuple[SourceStatement, ...]
    source_hash: str
    warnings: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "observability_class": self.observability_class,
            "source_hash": self.source_hash,
            "statements": [x.to_dict() for x in self.statements],
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class NativeCompileResult:
    native_version: str
    source_hash: str
    ast: dict[str, Any]
    temporal_packet: dict[str, Any]
    preserved_targets: tuple[str, ...]
    analysis: dict[str, Any]
    warnings: tuple[dict[str, Any], ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
