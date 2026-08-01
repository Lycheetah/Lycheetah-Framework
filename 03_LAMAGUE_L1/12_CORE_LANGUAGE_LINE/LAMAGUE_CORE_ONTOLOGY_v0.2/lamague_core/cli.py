from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import run_source
from .errors import LamagueError
from .graph import semantic_graph
from .ontology import ontology_export


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="LAMAGUE Core v0.2 — Primitive Ontology and Type Lock"
    )
    parser.add_argument("path", type=Path, nargs="?")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--ontology", action="store_true")
    args = parser.parse_args(argv)

    if args.ontology:
        print(
            json.dumps(
                ontology_export(),
                ensure_ascii=False,
                indent=2 if args.pretty else None,
            )
        )
        return 0

    if args.path is None:
        parser.error("path is required unless --ontology is used")

    try:
        source = args.path.read_text(encoding="utf-8")
        _, runtime, result = run_source(source)
        if args.graph:
            result["semantic_graphs"] = [
                semantic_graph(node) for node in runtime.expressions
            ]
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2 if args.pretty else None,
            )
        )
        return 0
    except (OSError, LamagueError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "lamague_core_version": "0.2.0",
                    "status": "REJECTED",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
