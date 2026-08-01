from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .core import run_source
from .errors import LamagueError
from .graph import semantic_graph
from .normalizer import normalize


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LAMAGUE Core Algebra v0.1")
    parser.add_argument("path", type=Path)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--graph", action="store_true")
    args = parser.parse_args(argv)

    try:
        source = args.path.read_text(encoding="utf-8")
        program, runtime, result = run_source(source)
        if args.graph:
            graphs = []
            for node in runtime.expressions:
                graphs.append(semantic_graph(node))
            result["semantic_graphs"] = graphs
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (OSError, LamagueError) as exc:
        print(json.dumps({
            "lamague_core_version": "0.1.0",
            "status": "REJECTED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
