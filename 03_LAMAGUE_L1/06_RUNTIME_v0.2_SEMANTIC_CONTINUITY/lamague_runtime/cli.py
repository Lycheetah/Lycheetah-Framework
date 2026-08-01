from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compiler import CanonicalMilestoneCompiler
from .interpreter import AbstractInterpreter
from .model import ContextCapsule
from .parser import Parser
from .semantic_hash import semantic_hash
from .trace_store import TraceStore


CANONICAL = (
    "Human and AI collaborators examine an unproven claim, preserve uncertainty, "
    "record contributions, and publish only what the evidence supports."
)


def _print(obj: object) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def demo() -> None:
    compiler = CanonicalMilestoneCompiler()
    ast = compiler.compile(CANONICAL)
    result = AbstractInterpreter().execute(ast)
    store = TraceStore(Path(__file__).resolve().parents[1] / "traces")
    trace_path = store.save(ast, result)
    _print({
        "input": CANONICAL,
        "operation_path": ast.operation_path,
        "semantic_hash": result.semantic_hash,
        "compression": result.compression.to_dict(),
        "audit": result.audit.to_dict(),
        "executed": result.executed,
        "proof_status": result.state.get("proof_status"),
        "unknowns": result.state.get("unknowns"),
        "trace_path": str(trace_path),
        "explanation": result.explanation,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="LAMAGUE Runtime v0.2")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo")
    parse_cmd = sub.add_parser("parse")
    parse_cmd.add_argument("expression")
    hash_cmd = sub.add_parser("hash")
    hash_cmd.add_argument("expression")
    compile_cmd = sub.add_parser("compile")
    compile_cmd.add_argument("text")

    args = parser.parse_args()
    if args.command == "demo":
        demo()
    elif args.command == "parse":
        ast = Parser().parse(args.expression, ContextCapsule())
        _print(ast.to_dict())
    elif args.command == "hash":
        ast = Parser().parse(args.expression, ContextCapsule())
        _print({"semantic_hash": semantic_hash(ast)})
    elif args.command == "compile":
        ast = CanonicalMilestoneCompiler().compile(args.text)
        result = AbstractInterpreter().execute(ast)
        _print(result.to_dict())


if __name__ == "__main__":
    main()
