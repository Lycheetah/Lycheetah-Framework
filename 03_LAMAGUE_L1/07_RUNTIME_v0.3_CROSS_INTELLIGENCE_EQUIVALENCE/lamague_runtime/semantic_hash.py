from __future__ import annotations

import hashlib
import json
from typing import Any

from .model import ProgramAST


def _canonical_context(ast: ProgramAST) -> dict[str, Any]:
    ctx = ast.context
    return {
        "domain": ctx.domain,
        "participants": sorted(ctx.participants),
        "affected_parties": sorted(ctx.affected_parties),
        "purpose": ctx.purpose,
        "claim": ctx.claim,
        "evidence": sorted(ctx.evidence),
        "evidence_score": round(ctx.evidence_score, 8),
        "certainty": round(ctx.certainty, 8),
        "unknowns": sorted(ctx.unknowns),
        "authority": sorted(ctx.authority),
        "consent": dict(sorted(ctx.consent.items())),
        "boundaries": sorted(ctx.boundaries),
        "invariants": sorted(ctx.invariants),
        "costs": sorted(ctx.costs),
        "risks": sorted(ctx.risks),
        "consequences": sorted(ctx.consequences),
        "consequence_horizon": ctx.consequence_horizon,
        "recovery": sorted(ctx.recovery),
        "provenance": sorted(ctx.provenance),
        "risk_level": ctx.risk_level,
        "irreversible": ctx.irreversible,
        "shared_context": ctx.shared_context,
        "dissent": ctx.dissent,
        "value_ledger": ctx.value_ledger,
        "parent_semantic_hash": ctx.parent_semantic_hash,
        "claimed_identity": ctx.claimed_identity,
    }


def canonical_semantics(ast: ProgramAST) -> dict[str, Any]:
    return {
        "version": ast.version,
        "operation_path": ast.operation_path,
        "expanded_from": sorted(ast.expanded_from),
        "context": _canonical_context(ast),
        "nodes": [
            {
                "operation": n.operation,
                "arguments": {
                    k: v for k, v in sorted(n.arguments.items())
                    if k != "expanded_from"
                },
                "input_types": n.input_types,
                "output_type": n.output_type,
                "invariants": sorted(n.invariants),
                "unknowns": sorted(n.unknowns),
                "authority": sorted(n.authority),
                "value_flow": n.value_flow,
                "recovery": sorted(n.recovery),
            }
            for n in ast.nodes
        ],
    }


def semantic_hash(ast: ProgramAST) -> str:
    payload = json.dumps(
        canonical_semantics(ast),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "lamague:" + hashlib.sha256(payload).hexdigest()
