from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RegistryError(ValueError):
    pass


class Registry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1] / "registry"
        self.operations_doc = self._load("operations_v0.2.json")
        self.seals_doc = self._load("seals_v0.2.json")
        self.ontology_doc = self._load("ontology_v0.2.json")
        self.version = self.seals_doc["version"]
        self.operations: dict[str, dict[str, Any]] = self.operations_doc["operations"]
        self.seals: dict[str, dict[str, Any]] = self.seals_doc["seals"]
        self.validate()

    def _load(self, filename: str) -> dict[str, Any]:
        path = self.root / filename
        if not path.exists():
            raise RegistryError(f"Registry file missing: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def validate(self) -> None:
        if self.version != "0.2":
            raise RegistryError(f"Expected registry v0.2, found {self.version}")
        if len(self.operations) != 26:
            raise RegistryError(f"Expected 26 operations, found {len(self.operations)}")
        if set(self.operations) != set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            raise RegistryError("Operation registry must contain A-Z exactly")
        for seal_id, seal in self.seals.items():
            expansion = seal.get("expansion", [])
            if not expansion:
                raise RegistryError(f"Seal {seal_id} has no expansion")
            unknown = [op for op in expansion if op not in self.operations]
            if unknown:
                raise RegistryError(f"Seal {seal_id} contains unknown operations: {unknown}")

    def expand_seal(self, seal_id: str, version: str | None = None) -> list[str]:
        seal_id = seal_id.upper().replace("-", "_")
        if version and version != self.version:
            raise RegistryError(
                f"Seal registry mismatch: requested {version}, available {self.version}"
            )
        if seal_id not in self.seals:
            raise RegistryError(f"Unknown seal: {seal_id}")
        return list(self.seals[seal_id]["expansion"])

    def operation(self, token: str) -> dict[str, Any]:
        token = token.upper()
        if token not in self.operations:
            raise RegistryError(f"Unknown operation: {token}")
        return self.operations[token]
