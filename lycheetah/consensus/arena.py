"""Multi-Agent Epistemic Consensus Arena.

Provides an interface over pairwise Psi_Q-gated gossip, connectivity and local
consistency checks, and Grey Mode quarantine/recovery. Exact cellular sheaf
diagnostics are available separately; the gossip gate is not an H^1 computation
or a proof of Byzantine fault tolerance.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .._bootstrap import ensure_implementation_on_path

ensure_implementation_on_path()

from core.grey_mode import RecoveryResult  # noqa: E402
from core.psi_consensus import (  # noqa: E402
    AdaptiveThresholds,
    ConsensusResult,
    PsiConsensus,
)
from core.psi_consensus import (  # noqa: E402
    _unit_state_vector as _to_unit_vector,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _sha256_hex(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass
class AgentProposal:
    """An agent's epistemic position or proposal in a multi-agent deliberation."""

    agent_id: str
    vector: list[float]
    role: str = "participant"
    claim: str = ""
    neighbors: list[str] = field(default_factory=list)


@dataclass
class DeliberationVerdict:
    """Digest-bound outcome, not an authenticated statement by an external issuer.

    ``obstruction_free`` is the legacy connectivity/local-consistency proxy.
    ``byzantine_safe`` records a quarantine fraction of at most one third; it
    does not establish Byzantine fault tolerance. Legacy verdicts without an
    anchor must be re-deliberated before use at the execution boundary.
    """

    converged: bool
    obstruction_free: bool
    byzantine_safe: bool
    rounds_run: int
    healthy_agents: list[str]
    quarantined_agents: list[str]
    final_drift: float
    consensus_vector: list[float] | None
    partition_count: int
    inconsistent_edges: list[tuple[str, str]]
    consensus_digest: str
    audit_trail: list[str]
    anchor_vector: tuple[float, ...] = ()

    def _digest_payload(self) -> dict[str, Any]:
        return {
            "profile": "lycheetah.consensus-verdict.v2",
            "anchor_vector": list(self.anchor_vector),
            "converged": self.converged,
            "obstruction_free": self.obstruction_free,
            "byzantine_safe": self.byzantine_safe,
            "rounds_run": self.rounds_run,
            "healthy_agents": list(self.healthy_agents),
            "quarantined_agents": list(self.quarantined_agents),
            "final_drift": self.final_drift,
            "consensus_vector": self.consensus_vector,
            "partition_count": self.partition_count,
            "inconsistent_edges": [list(edge) for edge in self.inconsistent_edges],
            "audit_trail": list(self.audit_trail),
        }

    def compute_digest(self) -> str:
        """Hash every outcome field with strict JSON and no lossy float rounding."""
        return _sha256_hex(self._digest_payload())

    def verify_integrity(self) -> bool:
        """Reject missing, nonfinite or altered outcomes before permit execution.

        An unkeyed digest detects changes relative to a bound permit. It does
        not authenticate agents, validate their claims or constrain Python code
        that already controls the harness process.
        """
        try:
            if any(
                type(flag) is not bool
                for flag in (self.converged, self.obstruction_free, self.byzantine_safe)
            ):
                return False
            if any(
                type(count) is not int or count < 0
                for count in (self.rounds_run, self.partition_count)
            ):
                return False
            if not self.anchor_vector or not all(math.isfinite(x) for x in self.anchor_vector):
                return False
            if not math.isfinite(self.final_drift):
                return False
            if self.consensus_vector is not None and (
                len(self.consensus_vector) != len(self.anchor_vector)
                or not all(math.isfinite(x) for x in self.consensus_vector)
            ):
                return False
            return hmac.compare_digest(self.consensus_digest, self.compute_digest())
        except (TypeError, ValueError, OverflowError):
            return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize verdict to a canonical JSON-compatible dictionary."""
        return {**self._digest_payload(), "consensus_digest": self.consensus_digest}


class ConsensusArena:
    """High-level coordinator for multi-agent epistemic consensus and Byzantine quarantine.

    Wraps `PsiConsensus` with:
    - Automatic full-mesh topology when explicit neighbor edges are omitted.
    - Configurable single-shot or multi-strike Grey Mode quarantine (`alert_threshold`).
    - Built-in TRIAD recovery (`recover_agent`) to heal quarantined nodes back onto
      the constitutional invariant curve.
    - Deterministic SHA-256 `consensus_digest` over deliberation outcomes.
    """

    def __init__(
        self,
        anchor: list[float] | np.ndarray,
        coherence: list[float] | np.ndarray | None = None,
        *,
        mu: float = 0.5,
        max_rounds: int = 100,
        grey_kappa: float = 1.5,
        grey_sigma_hat: float = 0.1,
        grey_theta_x: float = 0.3,
        grey_alert_threshold: int = 1,
        eps_c_base: float = 0.01,
        theta_inv_base: float = 0.5,
        eps_neighbor_base: float = 0.5,
    ) -> None:
        self.anchor_vec = _to_unit_vector(anchor)
        self.coherence_vec = (
            _to_unit_vector(coherence) if coherence is not None else self.anchor_vec.copy()
        )
        if self.anchor_vec.shape != self.coherence_vec.shape:
            raise ValueError("anchor and coherence vectors must have identical dimension")

        self.thresholds = AdaptiveThresholds(
            eps_c_base=eps_c_base,
            theta_inv_base=theta_inv_base,
            eps_neighbor_base=eps_neighbor_base,
        )
        self.protocol = PsiConsensus(
            anchor=self.anchor_vec,
            coherence=self.coherence_vec,
            thresholds=self.thresholds,
            mu=mu,
            max_rounds=max_rounds,
            grey_kappa=grey_kappa,
            grey_sigma_hat=grey_sigma_hat,
            grey_theta_x=grey_theta_x,
            grey_alert_threshold=grey_alert_threshold,
        )
        self.proposals: dict[str, AgentProposal] = {}

    @property
    def dim(self) -> int:
        """Dimension of the arena's state space."""
        return int(self.anchor_vec.size)

    def add_agent(
        self,
        agent_id: str,
        vector: list[float] | np.ndarray,
        *,
        role: str = "participant",
        claim: str = "",
        neighbors: list[str] | None = None,
    ) -> ConsensusArena:
        """Register an agent and its state vector in the arena."""
        vec = _to_unit_vector(vector)
        if vec.size != self.dim:
            raise ValueError(
                f"Agent '{agent_id}' vector dimension ({vec.size}) does not match "
                f"arena dimension ({self.dim})"
            )
        prop = AgentProposal(
            agent_id=agent_id,
            vector=[float(x) for x in vec],
            role=role,
            claim=claim,
            neighbors=list(neighbors or []),
        )
        self.proposals[agent_id] = prop
        self.protocol.add_agent(agent_id, vec, neighbors=list(neighbors or []))
        return self

    def _ensure_topology(self) -> None:
        """If no explicit neighbor edges were declared on any node, connect a full mesh."""
        has_any_edge = any(bool(node.neighbors) for node in self.protocol._nodes.values())
        if not has_any_edge and len(self.protocol._nodes) > 1:
            all_ids = list(self.protocol._nodes.keys())
            for aid, node in self.protocol._nodes.items():
                node.neighbors = [other for other in all_ids if other != aid]

    def deliberate(self) -> DeliberationVerdict:
        """Execute the protocol and return a digest-bound, unsigned verdict."""
        self._ensure_topology()
        raw: ConsensusResult = self.protocol.run()

        all_ids = list(self.protocol._nodes.keys())
        quarantined = list(raw.grey_agents)
        healthy = [aid for aid in all_ids if aid not in quarantined]
        n_total = len(all_ids)
        byzantine_safe = (len(quarantined) / n_total <= (1.0 / 3.0)) if n_total > 0 else False

        consensus_list = (
            [float(x) for x in raw.consensus_vector] if raw.consensus_vector is not None else None
        )

        verdict = DeliberationVerdict(
            converged=raw.converged,
            obstruction_free=raw.obstruction_report.obstruction_free,
            byzantine_safe=byzantine_safe,
            rounds_run=raw.rounds_run,
            healthy_agents=healthy,
            quarantined_agents=quarantined,
            final_drift=float(raw.final_drift),
            consensus_vector=consensus_list,
            partition_count=raw.obstruction_report.partition_count,
            inconsistent_edges=list(raw.obstruction_report.inconsistent_edges),
            consensus_digest="",
            audit_trail=list(raw.audit_trail),
            anchor_vector=tuple(float(x) for x in self.anchor_vec),
        )
        verdict.consensus_digest = verdict.compute_digest()
        return verdict

    def recover_agent(
        self,
        agent_id: str,
        *,
        max_cycles: int = 10,
        r_c_static: float | None = None,
    ) -> RecoveryResult:
        """Run the TRIAD recovery sequence (Ao -> Phi^up -> Psi) on a quarantined agent.

        If recovery converges within threshold, the agent's state in the arena is
        updated to the healed state and its monitor returns to HEALTHY.
        """
        if agent_id not in self.protocol._nodes:
            raise KeyError(f"Unknown agent_id: {agent_id!r}")

        node = self.protocol._nodes[agent_id]
        monitor = self.protocol._grey_monitors[agent_id]
        stats = self.protocol.network_stats(agent_id)

        result: RecoveryResult = monitor.run(
            agent_id=agent_id,
            state=node.state,
            network_stats=stats,
            psi_inv=self.anchor_vec,
            max_cycles=max_cycles,
            r_c_static=r_c_static,
        )
        if result.converged:
            node.state = result.final_state.copy()
            if agent_id in self.proposals:
                self.proposals[agent_id].vector = [float(x) for x in result.final_state]
        return result

    def agent_status(self, agent_id: str) -> dict[str, Any]:
        """Return current drift and Grey Mode status for a registered agent."""
        if agent_id not in self.protocol._nodes:
            raise KeyError(f"Unknown agent_id: {agent_id!r}")
        node = self.protocol._nodes[agent_id]
        monitor = self.protocol._grey_monitors[agent_id]
        drift = 1.0 - abs(float(np.dot(node.state, self.anchor_vec)))
        status_str = getattr(monitor.status, "value", str(monitor.status))
        return {
            "agent_id": agent_id,
            "status": status_str,
            "drift": round(drift, 6),
            "alert_count": monitor.alert_count,
            "neighbors": list(node.neighbors),
        }

    def sheaf_cohomology_report(self) -> dict[str, Any]:
        """Compute the exact cellular sheaf coboundary certificate (``delta^0``,
        Hodge 0-Laplacian ``L_0 = (delta^0)^T delta^0``, ``dim H^0``, ``dim H^1``,
        and Dirichlet sheaf energy ``||delta^0 x||_2^2``) over the healthy agent graph."""
        from core.sheaf_cohomology_factorial import CellularSheaf

        self._ensure_topology()
        healthy_ids = [
            aid
            for aid, mon in self.protocol._grey_monitors.items()
            if getattr(mon.status, "value", str(mon.status)) != "GREY"
        ]
        id_to_idx = {aid: idx for idx, aid in enumerate(healthy_ids)}
        edges: list[tuple[int, int]] = []
        seen_undirected: set[tuple[int, int]] = set()
        for aid in healthy_ids:
            u = id_to_idx[aid]
            for nb in self.protocol._nodes[aid].neighbors:
                if nb in id_to_idx:
                    v = id_to_idx[nb]
                    pair = (min(u, v), max(u, v))
                    if u != v and pair not in seen_undirected:
                        seen_undirected.add(pair)
                        edges.append(pair)

        if not healthy_ids:
            return {
                "healthy_agents": [],
                "cohomology": None,
                "dirichlet_energy": 0.0,
                "coboundary_norm": 0.0,
            }

        sheaf = CellularSheaf(len(healthy_ids), edges, stalk_dim=self.dim)
        cert = sheaf.cohomology_certificate()
        x_cochain = np.concatenate([self.protocol._nodes[aid].state for aid in healthy_ids])
        delta0 = sheaf.coboundary_matrix()
        coboundary_vec = delta0 @ x_cochain if delta0.size > 0 else np.zeros(0, dtype=float)
        energy = float(np.dot(coboundary_vec, coboundary_vec))
        return {
            "healthy_agents": healthy_ids,
            "cohomology": cert.to_dict(),
            "dirichlet_energy": round(energy, 8),
            "coboundary_norm": round(float(np.linalg.norm(coboundary_vec)), 8),
        }

    @classmethod
    def from_spec(cls, spec: dict[str, Any]) -> ConsensusArena:
        """Construct a ConsensusArena from a JSON-compatible specification dictionary."""
        if "anchor" not in spec:
            raise ValueError("Consensus spec requires an 'anchor' vector")
        options = spec.get("options", {})
        arena = cls(
            anchor=spec["anchor"],
            coherence=spec.get("coherence"),
            mu=float(options.get("mu", 0.5)),
            max_rounds=int(options.get("max_rounds", 100)),
            grey_kappa=float(options.get("grey_kappa", 1.5)),
            grey_sigma_hat=float(options.get("grey_sigma_hat", 0.1)),
            grey_theta_x=float(options.get("grey_theta_x", 0.3)),
            grey_alert_threshold=int(options.get("grey_alert_threshold", 1)),
            eps_c_base=float(options.get("eps_c_base", 0.01)),
            theta_inv_base=float(options.get("theta_inv_base", 0.5)),
            eps_neighbor_base=float(options.get("eps_neighbor_base", 0.5)),
        )
        for item in spec.get("agents", []):
            arena.add_agent(
                agent_id=item["id"],
                vector=item["vector"],
                role=item.get("role", "participant"),
                claim=item.get("claim", ""),
                neighbors=item.get("neighbors"),
            )
        return arena
