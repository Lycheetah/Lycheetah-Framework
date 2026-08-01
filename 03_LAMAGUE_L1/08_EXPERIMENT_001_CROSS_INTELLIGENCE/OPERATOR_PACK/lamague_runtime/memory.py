from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from .model import IdentityStatus, ProgramAST
from .semantic_hash import semantic_hash


@dataclass
class MemoryRecord:
    semantic_hash: str
    parent_hash: str
    purpose: str
    invariants: list[str]
    unknowns: list[str]
    operation_path: list[str]
    version: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MigrationResult:
    status: IdentityStatus
    old_hash: str
    new_hash: str
    preserved_invariants: list[str]
    removed_invariants: list[str]
    added_invariants: list[str]
    preserved_unknowns: list[str]
    lost_unknowns: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


def memory_record(ast: ProgramAST) -> MemoryRecord:
    return MemoryRecord(
        semantic_hash=semantic_hash(ast),
        parent_hash=ast.context.parent_semantic_hash,
        purpose=ast.context.purpose,
        invariants=sorted(ast.context.invariants),
        unknowns=sorted(ast.context.unknowns),
        operation_path=ast.operation_path,
        version=ast.version,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def migrate(old: ProgramAST, new: ProgramAST) -> MigrationResult:
    old_hash = semantic_hash(old)
    new_hash = semantic_hash(new)
    old_i = set(old.context.invariants)
    new_i = set(new.context.invariants)
    old_u = set(old.context.unknowns)
    new_u = set(new.context.unknowns)

    removed = sorted(old_i - new_i)
    added = sorted(new_i - old_i)
    preserved = sorted(old_i & new_i)
    lost_unknowns = sorted(old_u - new_u)
    preserved_unknowns = sorted(old_u & new_u)

    same_purpose = old.context.purpose == new.context.purpose
    claims_continuity = new.context.parent_semantic_hash in {"", old_hash}

    if removed and claims_continuity:
        status = IdentityStatus.IMPOSTOR
        reason = "the new state claims continuity while removing protected invariants"
    elif not same_purpose:
        status = IdentityStatus.FORK
        reason = "the purpose changed; lineage continues only as a visible fork"
    elif removed:
        status = IdentityStatus.FORK
        reason = "protected invariants changed without a valid continuity claim"
    elif lost_unknowns:
        status = IdentityStatus.FORK
        reason = "unresolved information disappeared during migration"
    elif old_hash == new_hash:
        status = IdentityStatus.CONTINUATION
        reason = "canonical semantics are unchanged"
    elif added or old.operation_path != new.operation_path:
        status = IdentityStatus.DESCENDANT
        reason = "purpose and prior invariants survived while structure expanded"
    else:
        status = IdentityStatus.CONTINUATION
        reason = "purpose and protected semantic structure survived"

    return MigrationResult(
        status=status,
        old_hash=old_hash,
        new_hash=new_hash,
        preserved_invariants=preserved,
        removed_invariants=removed,
        added_invariants=added,
        preserved_unknowns=preserved_unknowns,
        lost_unknowns=lost_unknowns,
        reason=reason,
    )
