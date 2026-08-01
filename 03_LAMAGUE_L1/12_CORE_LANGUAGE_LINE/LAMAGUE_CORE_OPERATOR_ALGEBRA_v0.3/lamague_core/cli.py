from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import run_source
from .errors import LamagueError
from .graph import semantic_graph
from .ontology import ontology_export
from .contracts import contracts_export, composition_matrix


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="LAMAGUE Core v0.3 — Complete Operator Algebra and Transformation Contracts"
    )
    parser.add_argument("path", type=Path, nargs="?")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--ontology", action="store_true")
    parser.add_argument("--contracts", action="store_true")
    parser.add_argument("--composition-matrix", action="store_true")
    args = parser.parse_args(argv)

    if args.contracts:
        print(json.dumps(contracts_export(), ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

    if args.composition_matrix:
        print(json.dumps(composition_matrix(), ensure_ascii=False, indent=2 if args.pretty else None))
        return 0

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
        parser.error("path is required unless an export flag is used")

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
                    "lamague_core_version": "0.3.0",
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
