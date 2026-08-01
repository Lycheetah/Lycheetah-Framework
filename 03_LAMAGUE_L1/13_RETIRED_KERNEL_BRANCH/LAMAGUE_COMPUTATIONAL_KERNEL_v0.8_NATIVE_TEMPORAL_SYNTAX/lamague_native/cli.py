from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .parser import parse_file, NativeSyntaxError, VERSION
from .compiler import compile_program, NativeCompileError


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="LAMAGUE v0.8 native temporal syntax compiler"
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        program = parse_file(args.source)
        result = compile_program(program).to_dict()
        text = json.dumps(
            result,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
        )
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except (OSError, NativeSyntaxError, NativeCompileError) as exc:
        payload = {
            "native_version": VERSION,
            "status": "REJECTED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        print(
            json.dumps(payload, ensure_ascii=False, indent=2),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
