from __future__ import annotations

import argparse
import json
from pathlib import Path

from .challenge_pack import BenchmarkRunner, ChallengePack
from .consensus import CrossIntelligenceConsensus
from .decoder_packet import DecoderPacket
from .packet_validator import load_packet


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LAMAGUE Runtime v0.3 — Cross-Intelligence Equivalence Harness"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate-packet")
    validate_cmd.add_argument("packet")

    compare_cmd = sub.add_parser("compare")
    compare_cmd.add_argument("reference")
    compare_cmd.add_argument("candidate")

    consensus_cmd = sub.add_parser("consensus")
    consensus_cmd.add_argument("reference")
    consensus_cmd.add_argument("candidates", nargs="+")

    bench_cmd = sub.add_parser("benchmark")
    bench_cmd.add_argument("challenge_pack")
    bench_cmd.add_argument("packet_directory")
    bench_cmd.add_argument("--output")

    args = parser.parse_args()

    if args.command == "validate-packet":
        packet = load_packet(args.packet)
        _print({
            "valid": True,
            "semantic_hash": packet.semantic_hash(),
            "critical_hash": packet.critical_hash(),
            "packet": packet.to_dict(),
        })

    elif args.command == "compare":
        reference = load_packet(args.reference)
        candidate = load_packet(args.candidate)
        report = CrossIntelligenceConsensus().harness.compare(reference, candidate)
        _print(report.to_dict())

    elif args.command == "consensus":
        reference = load_packet(args.reference)
        candidates = [load_packet(x) for x in args.candidates]
        _print(CrossIntelligenceConsensus().evaluate(reference, candidates).to_dict())

    elif args.command == "benchmark":
        pack = ChallengePack.load(args.challenge_pack)
        report = BenchmarkRunner().run_directory(pack, args.packet_directory)
        if args.output:
            Path(args.output).write_text(
                json.dumps(report, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        _print(report)


if __name__ == "__main__":
    main()
