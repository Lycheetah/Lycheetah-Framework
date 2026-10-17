"""Lycheetah Multi-Agent Epistemic Consensus (`lycheetah.consensus`).

Exposes the AURA Psi-Consensus protocol (pairwise Psi_Q-gated gossip, H^1 sheaf
cohomology obstruction detection, 33% Byzantine fault tolerance, and Grey Mode
quarantine + TRIAD recovery) along with the high-level `ConsensusArena`.
"""

from __future__ import annotations

from .._bootstrap import ensure_implementation_on_path

ensure_implementation_on_path()

from core.grey_mode import (  # noqa: E402
    GreyModeMonitor,
    GreyModeStatus,
    IsolationRecord,
    NetworkStats,
    RecoveryResult,
    TriggerEvent,
)
from core.psi_consensus import (  # noqa: E402
    AdaptiveThresholds,
    AgentNode,
    ConsensusResult,
    GossipProtocol,
    GossipRound,
    ObstructionDetector,
    ObstructionReport,
    PsiConsensus,
    PsiQOperator,
    build_consensus,
)

from .arena import (  # noqa: E402
    AgentProposal,
    ConsensusArena,
    DeliberationVerdict,
)

__all__ = [
    "AdaptiveThresholds",
    "AgentNode",
    "AgentProposal",
    "ConsensusArena",
    "ConsensusResult",
    "DeliberationVerdict",
    "GossipProtocol",
    "GossipRound",
    "GreyModeMonitor",
    "GreyModeStatus",
    "IsolationRecord",
    "NetworkStats",
    "ObstructionDetector",
    "ObstructionReport",
    "PsiConsensus",
    "PsiQOperator",
    "RecoveryResult",
    "TriggerEvent",
    "build_consensus",
]
