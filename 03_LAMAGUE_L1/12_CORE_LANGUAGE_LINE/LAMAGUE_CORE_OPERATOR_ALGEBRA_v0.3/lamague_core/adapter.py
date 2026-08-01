from __future__ import annotations

from typing import Any, Protocol

from .ontology import CoreType


class LamagueAdapter(Protocol):
    name: str
    version: str

    def supports_type(self, core_type: CoreType) -> bool: ...
    def supports_atom(self, atom: str, core_type: CoreType) -> bool: ...
    def map_atom(self, atom: str, core_type: CoreType) -> Any: ...
    def map_operator(
        self,
        operator: str,
        operands: list[Any],
        result_type: CoreType,
    ) -> Any: ...
    def validate_invariant(
        self, name: str, expression: Any, core_type: CoreType
    ) -> dict: ...
    def validate_requirement(
        self, expression: Any, core_type: CoreType
    ) -> dict: ...
    def validate_prohibition(
        self, expression: Any, core_type: CoreType
    ) -> dict: ...
