from __future__ import annotations
import argparse, json
from pathlib import Path
from .runner import run_manifest


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lamague-benchmark")
    parser.add_argument("manifest")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)
    report = run_manifest(args.manifest)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
