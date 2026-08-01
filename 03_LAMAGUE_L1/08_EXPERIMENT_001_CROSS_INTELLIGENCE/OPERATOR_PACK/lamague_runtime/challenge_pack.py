from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any

from .decoder_packet import DecoderPacket
from .consensus import CrossIntelligenceConsensus


@dataclass
class ChallengeCase:
    case_id: str
    title: str
    source_expression: str
    source_text: str
    instructions: str
    reference_packet: DecoderPacket

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["reference_packet"] = self.reference_packet.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChallengeCase":
        data = dict(data)
        data["reference_packet"] = DecoderPacket.from_dict(data["reference_packet"])
        return cls(**data)


class ChallengePack:
    def __init__(self, cases: list[ChallengeCase]) -> None:
        self.cases = cases

    def write(self, directory: Path | str) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "challenge_pack.json"
        path.write_text(
            json.dumps(
                {"schema_version": "0.3", "cases": [c.to_dict() for c in self.cases]},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    @classmethod
    def load(cls, path: Path | str) -> "ChallengePack":
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([ChallengeCase.from_dict(x) for x in doc["cases"]])


class BenchmarkRunner:
    def __init__(self) -> None:
        self.consensus = CrossIntelligenceConsensus()

    def run_case(
        self,
        case: ChallengeCase,
        candidate_packets: list[DecoderPacket],
    ) -> dict[str, Any]:
        report = self.consensus.evaluate(case.reference_packet, candidate_packets)
        return {
            "case": case.to_dict(),
            "consensus": report.to_dict(),
        }

    def run_directory(
        self,
        pack: ChallengePack,
        packet_directory: Path | str,
    ) -> dict[str, Any]:
        packet_directory = Path(packet_directory)
        results = []
        for case in pack.cases:
            packets = []
            for path in sorted(packet_directory.glob(f"{case.case_id}__*.json")):
                packets.append(
                    DecoderPacket.from_dict(
                        json.loads(path.read_text(encoding="utf-8"))
                    )
                )
            results.append(self.run_case(case, packets))
        return {
            "runtime": "LAMAGUE Runtime v0.3",
            "language_registry": "0.2",
            "case_count": len(pack.cases),
            "results": results,
        }
