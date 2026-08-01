from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model import ExecutionResult, ProgramAST


class TraceStore:
    def __init__(self, directory: Path | str) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, ast: ProgramAST, result: ExecutionResult) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.directory / f"{stamp}_{ast.program_id}.json"
        document: dict[str, Any] = {
            "registry_version": ast.version,
            "input": ast.source,
            "semantic_hash": result.semantic_hash,
            "compression": result.compression.to_dict() if result.compression else None,
            "ast": ast.to_dict(),
            "execution": result.to_dict(),
        }
        path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
