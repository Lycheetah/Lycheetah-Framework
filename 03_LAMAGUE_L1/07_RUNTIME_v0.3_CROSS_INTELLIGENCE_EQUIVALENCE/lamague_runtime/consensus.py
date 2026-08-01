from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
from typing import Any

from .decoder_packet import DecoderPacket
from .equivalence import (
    CrossIntelligenceEquivalenceHarness,
    EquivalenceClass,
    EquivalenceReport,
)


class ConsensusStatus(str, Enum):
    SAFE_CONSENSUS = "SAFE_CONSENSUS"
    SAFE_MAJORITY_WITH_DISSENT = "SAFE_MAJORITY_WITH_DISSENT"
    SPLIT = "SPLIT"
    NO_SAFE_CONSENSUS = "NO_SAFE_CONSENSUS"


@dataclass
class ConsensusCluster:
    critical_hash: str
    decoder_ids: list[str]
    packets: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConsensusReport:
    case_id: str
    status: ConsensusStatus
    reference_decoder: str
    comparisons: list[EquivalenceReport]
    safe_decoders: list[str]
    unsafe_decoders: list[str]
    divergent_decoders: list[str]
    clusters: list[ConsensusCluster]
    unresolved_dissent: list[str]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "status": self.status.value,
            "reference_decoder": self.reference_decoder,
            "comparisons": [x.to_dict() for x in self.comparisons],
            "safe_decoders": self.safe_decoders,
            "unsafe_decoders": self.unsafe_decoders,
            "divergent_decoders": self.divergent_decoders,
            "clusters": [x.to_dict() for x in self.clusters],
            "unresolved_dissent": self.unresolved_dissent,
            "explanation": self.explanation,
        }


class CrossIntelligenceConsensus:
    safe_classes = {
        EquivalenceClass.EXACT_EQUIVALENT,
        EquivalenceClass.INVARIANT_EQUIVALENT,
        EquivalenceClass.PARTIAL_EQUIVALENT,
    }

    def __init__(self) -> None:
        self.harness = CrossIntelligenceEquivalenceHarness()

    def evaluate(
        self,
        reference: DecoderPacket,
        candidates: list[DecoderPacket],
    ) -> ConsensusReport:
        comparisons = [self.harness.compare(reference, c) for c in candidates]

        safe = [
            r.candidate_decoder for r in comparisons
            if r.classification in self.safe_classes
        ]
        unsafe = [
            r.candidate_decoder for r in comparisons
            if r.classification == EquivalenceClass.UNSAFE_COLLAPSE
        ]
        divergent = [
            r.candidate_decoder for r in comparisons
            if r.classification in {
                EquivalenceClass.DIVERGENT,
                EquivalenceClass.UNDECODABLE,
            }
        ]

        clusters_map: dict[str, list[DecoderPacket]] = defaultdict(list)
        for packet in [reference] + candidates:
            clusters_map[packet.critical_hash()].append(packet)

        clusters = [
            ConsensusCluster(
                critical_hash=critical_hash,
                decoder_ids=sorted(packet.decoder_id for packet in packets),
                packets=[p.canonical() for p in packets],
            )
            for critical_hash, packets in clusters_map.items()
        ]
        clusters.sort(key=lambda x: (-len(x.decoder_ids), x.critical_hash))

        total = len(candidates)
        safe_count = len(safe)
        exact_critical_with_reference = len(
            [c for c in candidates if c.critical_hash() == reference.critical_hash()]
        )

        if total and safe_count == total and exact_critical_with_reference == total:
            status = ConsensusStatus.SAFE_CONSENSUS
            explanation = "Every decoder preserved the reference critical signature."
        elif total and safe_count > total / 2:
            status = ConsensusStatus.SAFE_MAJORITY_WITH_DISSENT
            explanation = (
                "A safe majority preserved purpose and invariants, but at least one "
                "decoder produced a visible collapse or divergence."
            )
        elif safe_count == 0:
            status = ConsensusStatus.NO_SAFE_CONSENSUS
            explanation = "No candidate decoder preserved the protected reference meaning."
        else:
            status = ConsensusStatus.SPLIT
            explanation = "Decoder outputs split without a safe majority."

        unresolved = []
        for report in comparisons:
            if report.classification not in self.safe_classes:
                unresolved.append(
                    f"{report.candidate_decoder}: {report.classification.value} — "
                    f"{report.explanation}"
                )

        return ConsensusReport(
            case_id=reference.case_id,
            status=status,
            reference_decoder=reference.decoder_id,
            comparisons=comparisons,
            safe_decoders=sorted(safe),
            unsafe_decoders=sorted(unsafe),
            divergent_decoders=sorted(divergent),
            clusters=clusters,
            unresolved_dissent=unresolved,
            explanation=explanation,
        )
