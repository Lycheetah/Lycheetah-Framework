from __future__ import annotations

import json
from pathlib import Path

from lamague_runtime import (
    AbstractInterpreter,
    ContextCapsule,
    Parser,
    TraceStore,
    memory_record,
    migrate,
    semantic_hash,
)


def main() -> None:
    base_ctx = ContextCapsule(
        domain="human-AI research",
        participants=["Mac", "AI collaborator"],
        affected_parties=["future testers"],
        purpose="develop LAMAGUE without erasing uncertainty or disagreement",
        claim="breathing compression can preserve accountable meaning",
        evidence=["Runtime v0.1 trace", "Runtime v0.2 test suite"],
        evidence_score=0.72,
        certainty=0.60,
        unknowns=["cross-model reliability"],
        authority=["Mac authorises abstract execution"],
        consent={"Mac": "explicit", "AI collaborator": "operational"},
        boundaries=["no external action", "no hidden extraction"],
        invariants=[
            "uncertainty remains visible",
            "lineage remains recoverable",
            "dissent remains attributable",
        ],
        costs=["time", "computation"],
        consequences=["new abstract state and trace"],
        consequence_horizon="immediate",
        recovery=["restore prior state"],
        provenance=["LAMAGUE Frontier Canon", "Runtime v0.1"],
        risk_level="low",
        execute_requested=True,
        decoder_confidence=0.96,
        shared_context=True,
        dissent=[{
            "parties": ["Mac", "AI collaborator"],
            "positions": {
                "Mac": "continue inventing at the frontier",
                "AI collaborator": "bind each leap to tests and lineage",
            },
            "protected_boundaries": ["creative agency", "epistemic honesty"],
            "status": "UNRESOLVED",
        }],
    )

    ast = Parser().parse("W -> U<disagreement> -> G -> V -> Y", base_ctx)
    result = AbstractInterpreter().execute(ast)
    trace_path = TraceStore(Path(__file__).resolve().parents[1] / "traces").save(ast, result)

    descendant_ctx = ContextCapsule(**{
        **base_ctx.to_dict(),
        "unknowns": ["cross-model reliability", "human learnability"],
        "parent_semantic_hash": semantic_hash(ast),
        "migration_reason": "human learnability added as an explicit unresolved dimension",
    })
    descendant = Parser().parse("W -> U<disagreement> -> G -> V -> F -> Y", descendant_ctx)
    migration = migrate(ast, descendant)

    output = {
        "runtime": "LAMAGUE Runtime v0.2",
        "expression": ast.source,
        "operation_path": ast.operation_path,
        "semantic_hash": result.semantic_hash,
        "compression": result.compression.to_dict(),
        "audit": result.audit.to_dict(),
        "executed": result.executed,
        "dissent_preserved": result.state["dissent"],
        "unknowns_preserved": result.state["unknowns"],
        "memory_record": memory_record(ast).to_dict(),
        "migration": migration.to_dict(),
        "trace_path": str(trace_path),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
