
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lamague_codec import build_codebook, decode, encode


def main():
    parser = argparse.ArgumentParser(description="LAMAGUE reversible semantic packet codec")
    sub = parser.add_subparsers(dest="command", required=True)

    encode_parser = sub.add_parser("encode")
    encode_parser.add_argument("packet")
    encode_parser.add_argument("--codebook")
    encode_parser.add_argument("-o", "--output")

    decode_parser = sub.add_parser("decode")
    decode_parser.add_argument("source")
    decode_parser.add_argument("--codebook")
    decode_parser.add_argument("-o", "--output")

    codebook_parser = sub.add_parser("build-codebook")
    codebook_parser.add_argument("packets_jsonl")
    codebook_parser.add_argument("--max-entries", type=int, default=20)
    codebook_parser.add_argument("-o", "--output", required=True)

    args = parser.parse_args()

    if args.command == "encode":
        packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
        codebook = json.loads(Path(args.codebook).read_text(encoding="utf-8")) if args.codebook else None
        result = encode(packet, codebook)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            print(result)

    elif args.command == "decode":
        source = Path(args.source).read_text(encoding="utf-8")
        codebook = json.loads(Path(args.codebook).read_text(encoding="utf-8")) if args.codebook else None
        result = decode(source, codebook)
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)

    elif args.command == "build-codebook":
        packets = [
            json.loads(line)
            for line in Path(args.packets_jsonl).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        result = build_codebook(packets, max_entries=args.max_entries)
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
