from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class Severity(str, Enum):
    FATAL = "FATAL"
    RECOVERABLE = "RECOVERABLE"
    ADVISORY = "ADVISORY"

@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    repair: str = ""
    def to_dict(self):
        return {"severity": self.severity.value, "code": self.code, "message": self.message, "repair": self.repair}

class LamagueError(Exception):
    pass

class ParseFailure(LamagueError):
    pass

class CompileFailure(LamagueError):
    def __init__(self, diagnostics: Iterable[Diagnostic]):
        self.diagnostics = tuple(diagnostics)
        super().__init__("\n".join(f"{d.severity.value} {d.code}: {d.message}" for d in self.diagnostics))

class RuntimeHalt(LamagueError):
    pass
