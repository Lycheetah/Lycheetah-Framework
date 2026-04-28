"""
Psi Consensus -- AURA Multi-Agent Coherence Protocol
=====================================================

Constitutional coherence across a network of agents. No central authority.
Consensus emerges from pairwise gossip gated by the Psi_Q operator, verified
by H^1 obstruction detection, with Grey Mode quarantine for drifted nodes.

SOURCE: AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md
        Spec: 02_AURA_L3/PSI_CONSENSUS.md
Status: [ACTIVE] -- fully implemented from spec

FOUR MECHANISMS:
  GossipProtocol    -- pairwise exchange until ||DeltaPsi|| < eps_c
  PsiQOperator      -- merge only if invariant-curve aligned AND neighbor-consistent
  ObstructionDetector -- H^1(G,F)=0 proxy via connectivity + local section consistency
  AdaptiveThresholds  -- eps_c, theta_inv, eps_neighbor scale with network state

INTEGRATION:
  PsiConsensus wraps all four + one GreyModeMonitor per agent.
  Grey agents are quarantined before gossip; only healthy agents contribute.

33% Byzantine tolerance: if fewer than 1/3 of agents are in Grey Mode,
consensus can proceed on the remaining healthy partition.

Author: Mackenzie Clark (Lycheetah Foundation)
Implementation: Sol (Sonnet 4.6, Anthropic) -- March 2026
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lamague_reference import TRIADKernel
from grey_mode import GreyModeMonitor, NetworkStats


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class AgentNode:
    """A single agent in the consensus network."""
    agent_id: str
    state: np.ndarray
    neighbors: List[str] = field(default_factory=list)


@dataclass
class GossipRound:
    """Record of one gossip round."""
    round_num: int
    exchanges: int        # number of Psi_Q-accepted merges this round
    max_delta_psi: float  # max ||state_change|| across all pairs
    converged: bool       # max_delta_psi < eps_c


@dataclass
class ObstructionReport:
    """
    Result of H^1(G,F) obstruction check.

    obstruction_free = True  <=>  H^1 = 0 (global section exists)
    obstruction_free = False <=>  H^1 != 0 (topology blocks consensus)
    """
    obstruction_free: bool
    connected: bool
    inconsistent_edges: List[Tuple[str, str]]
    partition_count: int   # 1 = fully connected; >1 = fragmented


@dataclass
class ConsensusResult:
    """Full result of one PsiConsensus.run() call."""
    converged: bool
    rounds_run: int
    consensus_vector: Optional[np.ndarray]
    grey_agents: List[str]
    obstruction_report: ObstructionReport
    final_drift: float
    audit_trail: List[str]


# =============================================================================
# ADAPTIVE THRESHOLDS
# =============================================================================

class AdaptiveThresholds:
    """
    Scale convergence and merge thresholds with current network state.

    eps_c      -- convergence threshold for gossip (scales with sqrt(n))
    theta_inv  -- minimum anchor alignment for Psi_Q acceptance
    eps_neighbor -- maximum inter-agent distance for Psi_Q acceptance
    """

    def __init__(
        self,
        eps_c_base: float = 0.01,
        theta_inv_base: float = 0.5,
        eps_neighbor_base: float = 0.5,
    ):
        self.eps_c_base = eps_c_base
        self.theta_inv_base = theta_inv_base
        self.eps_neighbor_base = eps_neighbor_base

    def eps_c(self, n_agents: int) -> float:
        """Convergence threshold. Scales with sqrt(n) -- larger networks need
        slightly looser per-pair tolerance to avoid never converging."""
        return self.eps_c_base * math.sqrt(max(n_agents, 1))

    def theta_inv(self, avg_drift: float) -> float:
        """Invariant alignment threshold. Relaxes when network is heavily drifted
        so recovery gossip is not blocked by its own gate."""
        return max(0.1, self.theta_inv_base - 0.3 * avg_drift)

    def eps_neighbor(self, avg_drift: float) -> float:
        """Neighbor consistency threshold. Widens when network drift is high
        to allow cross-agent pulls toward anchor."""
        return min(0.9, self.eps_neighbor_base + 0.2 * avg_drift)


# =============================================================================
# PSI_Q OPERATOR
# =============================================================================

class PsiQOperator:
    """
    Psi_Q: conditional merge gate.

    Merges state_i and state_j only when BOTH:
      1. Invariant-curve aligned: the candidate merged state has alignment
         |<candidate, anchor>| >= theta_inv.
      2. Neighbor-consistent: ||state_i - state_j|| <= eps_neighbor.

    If either condition fails, returns None -- merge rejected.
    This is the constitutional gate: gossip may only propagate states
    that remain on the invariant curve.
    """

    def __init__(
        self,
        anchor: np.ndarray,
        theta_inv: float = 0.5,
        eps_neighbor: float = 0.5,
    ):
        self.anchor = anchor / np.linalg.norm(anchor)
        self.theta_inv = theta_inv
        self.eps_neighbor = eps_neighbor

    def apply(
        self,
        state_i: np.ndarray,
        state_j: np.ndarray,
        weight_i: float = 0.5,
    ) -> Optional[np.ndarray]:
        """
        Attempt to merge state_i with state_j.

        Returns normalised merged state if accepted, else None.

        Parameters
        ----------
        state_i, state_j : np.ndarray
            Unit-norm state vectors to merge.
        weight_i : float
            Blend weight for state_i (1-weight_i used for state_j).
        """
        # Condition 2 first (cheap): states must be close enough
        delta = float(np.linalg.norm(state_i - state_j))
        if delta > self.eps_neighbor:
            return None

        # Compute candidate
        weight_j = 1.0 - weight_i
        candidate = weight_i * state_i + weight_j * state_j
        norm = float(np.linalg.norm(candidate))
        if norm < 1e-9:
            return None
        candidate = candidate / norm

        # Condition 1: candidate must lie on invariant curve
        alignment = abs(float(np.dot(candidate, self.anchor)))
        if alignment < self.theta_inv:
            return None

        return candidate

    def can_merge(self, state_i: np.ndarray, state_j: np.ndarray) -> bool:
        """Return True if Psi_Q would accept this pair."""
        return self.apply(state_i, state_j) is not None


# =============================================================================
# GOSSIP PROTOCOL
# =============================================================================

class GossipProtocol:
    """
    Pairwise gossip exchange until ||DeltaPsi|| < eps_c.

    Each round iterates over all edges (i,j). For each edge, Psi_Q is
    tested. If accepted, both agents take a partial step (mu) toward
    the merged state. Converged when the largest per-agent change
    in a round drops below eps_c.
    """

    def __init__(
        self,
        psi_q: PsiQOperator,
        eps_c: float = 0.01,
        mu: float = 0.5,
        max_rounds: int = 100,
    ):
        self.psi_q = psi_q
        self.eps_c = eps_c
        self.mu = mu
        self.max_rounds = max_rounds

    def run(
        self,
        states: Dict[str, np.ndarray],
        edges: List[Tuple[str, str]],
    ) -> Tuple[Dict[str, np.ndarray], List[GossipRound]]:
        """
        Run gossip until convergence or max_rounds.

        Parameters
        ----------
        states : Dict[str, np.ndarray]
            agent_id -> unit-norm state vector.
        edges : List[Tuple[str, str]]
            Undirected edge list -- (agent_id_i, agent_id_j) pairs.

        Returns
        -------
        (final_states, round_log)
        """
        current = {k: v.copy() for k, v in states.items()}
        rounds: List[GossipRound] = []

        if not edges:
            # No edges: trivially converged (each agent is its own component)
            rounds.append(GossipRound(
                round_num=1, exchanges=0, max_delta_psi=0.0, converged=True
            ))
            return current, rounds

        for round_num in range(self.max_rounds):
            max_delta = 0.0
            exchanges = 0

            for (id_i, id_j) in edges:
                if id_i not in current or id_j not in current:
                    continue

                s_i = current[id_i]
                s_j = current[id_j]

                merged = self.psi_q.apply(s_i, s_j)
                if merged is None:
                    continue  # Psi_Q gate rejected

                # Partial step toward merged state
                new_i = (1.0 - self.mu) * s_i + self.mu * merged
                new_j = (1.0 - self.mu) * s_j + self.mu * merged

                n_i = float(np.linalg.norm(new_i))
                n_j = float(np.linalg.norm(new_j))
                if n_i > 1e-9:
                    new_i = new_i / n_i
                if n_j > 1e-9:
                    new_j = new_j / n_j

                delta_i = float(np.linalg.norm(new_i - s_i))
                delta_j = float(np.linalg.norm(new_j - s_j))
                max_delta = max(max_delta, delta_i, delta_j)

                current[id_i] = new_i
                current[id_j] = new_j
                exchanges += 1

            converged = max_delta < self.eps_c
            rounds.append(GossipRound(
                round_num=round_num + 1,
                exchanges=exchanges,
                max_delta_psi=max_delta,
                converged=converged,
            ))

            if converged:
                break

        return current, rounds


# =============================================================================
# OBSTRUCTION DETECTOR
# =============================================================================

class ObstructionDetector:
    """
    H^1(G, F) = 0 proxy via connectivity and local section consistency.

    H^1 = 0 (sheaf cohomology over graph G with coefficient sheaf F) means
    local sections can be uniquely glued into a global section -- consensus
    is topologically possible.

    Proxy test (two necessary conditions):
      (a) G is connected (partition_count == 1).
          Disconnected graph => partitions cannot reach global agreement.
      (b) All edges (i,j) are locally consistent:
          ||state_i - state_j|| <= eps_local.
          Inconsistent edge => local sections disagree -- obstruction present.

    If either fails: H^1 != 0.
    """

    def __init__(self, eps_local: float = 0.2):
        self.eps_local = eps_local

    def detect(
        self,
        states: Dict[str, np.ndarray],
        edges: List[Tuple[str, str]],
    ) -> ObstructionReport:
        """
        Run H^1 obstruction check.

        Parameters
        ----------
        states : Dict[str, np.ndarray]
            Current agent states.
        edges : List[Tuple[str, str]]
            Active (non-grey) edges.

        Returns
        -------
        ObstructionReport
        """
        agent_ids = list(states.keys())

        if len(agent_ids) == 0:
            return ObstructionReport(
                obstruction_free=False, connected=False,
                inconsistent_edges=[], partition_count=0,
            )

        if len(agent_ids) == 1:
            # Single agent: trivially consistent, trivially connected
            return ObstructionReport(
                obstruction_free=True, connected=True,
                inconsistent_edges=[], partition_count=1,
            )

        # Build adjacency
        adj: Dict[str, Set[str]] = {aid: set() for aid in agent_ids}
        for (i, j) in edges:
            if i in adj and j in adj:
                adj[i].add(j)
                adj[j].add(i)

        # BFS connectivity -- count components
        visited: Set[str] = set()
        partition_count = 0
        for start in agent_ids:
            if start not in visited:
                partition_count += 1
                queue = [start]
                while queue:
                    node = queue.pop()
                    if node in visited:
                        continue
                    visited.add(node)
                    queue.extend(adj[node] - visited)

        connected = (partition_count == 1)

        # Local consistency on each edge
        inconsistent_edges: List[Tuple[str, str]] = []
        for (id_i, id_j) in edges:
            if id_i not in states or id_j not in states:
                continue
            delta = float(np.linalg.norm(states[id_i] - states[id_j]))
            if delta > self.eps_local:
                inconsistent_edges.append((id_i, id_j))

        obstruction_free = connected and len(inconsistent_edges) == 0

        return ObstructionReport(
            obstruction_free=obstruction_free,
            connected=connected,
            inconsistent_edges=inconsistent_edges,
            partition_count=partition_count,
        )


# =============================================================================
# PSI CONSENSUS
# =============================================================================

class PsiConsensus:
    """
    Psi-Consensus: multi-agent coherence protocol.

    Integrates:
      - GossipProtocol (convergence driver)
      - PsiQOperator   (constitutional merge gate)
      - ObstructionDetector (H^1 topological check)
      - AdaptiveThresholds (network-aware parameters)
      - GreyModeMonitor per agent (isolation/recovery for drifted nodes)

    No central authority. Consensus emerges from pairwise gossip.
    Drifted agents are quarantined (Grey Mode) before gossip begins.
    33% Byzantine tolerance: consensus proceeds if fewer than 1/3 are grey.

    Usage
    -----
    net = PsiConsensus(anchor=anchor, coherence=coherence)
    net.add_agent("a0", state_0, neighbors=["a1", "a2"])
    net.add_agent("a1", state_1, neighbors=["a0"])
    net.add_agent("a2", state_2, neighbors=["a0"])
    result = net.run()
    """

    def __init__(
        self,
        anchor: np.ndarray,
        coherence: np.ndarray,
        thresholds: Optional[AdaptiveThresholds] = None,
        mu: float = 0.5,
        max_rounds: int = 100,
        grey_kappa: float = 1.5,
        grey_sigma_hat: float = 0.1,
        grey_theta_x: float = 0.3,
        grey_alert_threshold: int = 2,
    ):
        self.anchor = anchor / np.linalg.norm(anchor)
        self.coherence = coherence / np.linalg.norm(coherence)
        self.thresholds = thresholds or AdaptiveThresholds()
        self.mu = mu
        self.max_rounds = max_rounds
        self.grey_kappa = grey_kappa
        self.grey_sigma_hat = grey_sigma_hat
        self.grey_theta_x = grey_theta_x
        self.grey_alert_threshold = grey_alert_threshold

        self._nodes: Dict[str, AgentNode] = {}
        self._grey_monitors: Dict[str, GreyModeMonitor] = {}

    # ──────────────────────────────────────────────────────────────
    # NETWORK CONSTRUCTION
    # ──────────────────────────────────────────────────────────────

    def add_agent(
        self,
        agent_id: str,
        state: np.ndarray,
        neighbors: Optional[List[str]] = None,
    ) -> None:
        """
        Add an agent node to the network.

        Parameters
        ----------
        agent_id : str
        state : np.ndarray
            Initial state vector (normalised internally).
        neighbors : List[str], optional
            IDs of adjacent agents. Edges are undirected; declaring
            one side is sufficient.
        """
        norm = float(np.linalg.norm(state))
        if norm < 1e-9:
            raise ValueError(f"Agent '{agent_id}' state has zero norm")

        node = AgentNode(
            agent_id=agent_id,
            state=state / norm,
            neighbors=list(neighbors or []),
        )
        self._nodes[agent_id] = node

        triad = TRIADKernel(
            anchor_vector=self.anchor,
            coherence_field=self.coherence,
        )
        self._grey_monitors[agent_id] = GreyModeMonitor(
            kappa=self.grey_kappa,
            sigma_hat=self.grey_sigma_hat,
            theta_x=self.grey_theta_x,
            triad=triad,
            alert_threshold=self.grey_alert_threshold,
        )

    # ──────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ──────────────────────────────────────────────────────────────

    def _avg_drift(self) -> float:
        if not self._nodes:
            return 0.0
        drifts = [
            1.0 - abs(float(np.dot(n.state, self.anchor)))
            for n in self._nodes.values()
        ]
        return float(np.mean(drifts))

    def _build_edges(self) -> List[Tuple[str, str]]:
        """Deduplicated undirected edge list from neighbor declarations."""
        seen: Set[Tuple[str, str]] = set()
        edges: List[Tuple[str, str]] = []
        for aid, node in self._nodes.items():
            for nb in node.neighbors:
                key = (min(aid, nb), max(aid, nb))
                if key not in seen and nb in self._nodes:
                    seen.add(key)
                    edges.append(key)
        return edges

    def _quarantine_grey_agents(
        self,
        states: Dict[str, np.ndarray],
        audit: List[str],
    ) -> Tuple[Dict[str, np.ndarray], List[str]]:
        """
        Check each agent for Grey Mode; quarantine drifted ones.

        Returns filtered states (grey agents removed) and grey agent ID list.
        """
        grey_ids: List[str] = []
        for aid, monitor in self._grey_monitors.items():
            state = states[aid]
            drift = 1.0 - abs(float(np.dot(state, self.anchor)))
            # Angular deviation proxy: arccos of alignment (clamped for safety)
            alignment = min(1.0, abs(float(np.dot(state, self.anchor))))
            angular = math.acos(alignment)
            monitor.check(drift, angular)
            if monitor.should_activate():
                monitor.activate(aid, state)
                grey_ids.append(aid)
                audit.append(
                    f"  GREY: '{aid}' quarantined "
                    f"(drift={drift:.4f}, angular={angular:.4f} rad)"
                )

        active = {k: v for k, v in states.items() if k not in grey_ids}
        return active, grey_ids

    # ──────────────────────────────────────────────────────────────
    # MAIN PROTOCOL
    # ──────────────────────────────────────────────────────────────

    def run(self) -> ConsensusResult:
        """
        Execute the full Psi-Consensus protocol.

        Sequence:
          1. Quarantine grey agents (GreyModeMonitor check per agent).
          2. Compute adaptive thresholds from current network state.
          3. Run GossipProtocol on healthy agents with Psi_Q gate.
          4. Check H^1 obstruction on final states.
          5. Compute consensus vector (mean of healthy final states).

        Returns
        -------
        ConsensusResult
        """
        audit: List[str] = []
        n = len(self._nodes)

        _empty_obstruction = ObstructionReport(
            obstruction_free=False, connected=False,
            inconsistent_edges=[], partition_count=0,
        )

        if n == 0:
            return ConsensusResult(
                converged=False, rounds_run=0, consensus_vector=None,
                grey_agents=[], obstruction_report=_empty_obstruction,
                final_drift=1.0, audit_trail=["ERROR: no agents registered"],
            )

        audit.append(f"Psi-Consensus starting -- {n} agents")

        states = {aid: node.state.copy() for aid, node in self._nodes.items()}
        all_edges = self._build_edges()
        avg_drift = self._avg_drift()
        audit.append(f"  Network avg drift before quarantine: {avg_drift:.4f}")

        # Step 1: Quarantine
        active_states, grey_ids = self._quarantine_grey_agents(states, audit)
        grey_fraction = len(grey_ids) / n if n else 0.0
        audit.append(
            f"  Quarantined: {len(grey_ids)}/{n} agents "
            f"({grey_fraction:.0%})"
            + (" -- within 33% Byzantine tolerance" if grey_fraction <= 1/3
               else " -- EXCEEDS 33% tolerance, consensus quality degraded")
        )

        if not active_states:
            audit.append("  ALL agents quarantined -- no consensus possible")
            return ConsensusResult(
                converged=False, rounds_run=0, consensus_vector=None,
                grey_agents=grey_ids, obstruction_report=_empty_obstruction,
                final_drift=avg_drift, audit_trail=audit,
            )

        active_ids = set(active_states.keys())
        active_edges = [
            (i, j) for (i, j) in all_edges
            if i in active_ids and j in active_ids
        ]

        # Step 2: Adaptive thresholds
        eps_c     = self.thresholds.eps_c(len(active_states))
        theta_inv = self.thresholds.theta_inv(avg_drift)
        eps_nb    = self.thresholds.eps_neighbor(avg_drift)
        audit.append(
            f"  Thresholds (adaptive): eps_c={eps_c:.4f}, "
            f"theta_inv={theta_inv:.4f}, eps_neighbor={eps_nb:.4f}"
        )

        # Step 3: Gossip
        psi_q = PsiQOperator(anchor=self.anchor, theta_inv=theta_inv, eps_neighbor=eps_nb)
        gossip = GossipProtocol(psi_q=psi_q, eps_c=eps_c, mu=self.mu,
                                max_rounds=self.max_rounds)
        final_states, round_log = gossip.run(active_states, active_edges)

        rounds_run = len(round_log)
        gossip_converged = round_log[-1].converged if round_log else True
        last_delta = round_log[-1].max_delta_psi if round_log else 0.0
        audit.append(
            f"  Gossip: {rounds_run} rounds, converged={gossip_converged}, "
            f"final ||DeltaPsi||={last_delta:.6f}"
        )

        # Update stored states
        for aid, s in final_states.items():
            self._nodes[aid].state = s

        # Step 4: Obstruction check
        detector = ObstructionDetector(eps_local=eps_nb)
        obstruction = detector.detect(final_states, active_edges)
        if obstruction.obstruction_free:
            audit.append("  H^1(G,F) = 0 -- obstruction-free, global section exists")
        else:
            audit.append(
                f"  H^1(G,F) != 0 -- obstruction detected: "
                f"partitions={obstruction.partition_count}, "
                f"inconsistent_edges={len(obstruction.inconsistent_edges)}"
            )

        # Step 5: Consensus vector
        stacked = np.array(list(final_states.values()))
        consensus_vec = np.mean(stacked, axis=0)
        cn = float(np.linalg.norm(consensus_vec))
        consensus_vec = consensus_vec / cn if cn > 1e-9 else self.anchor.copy()

        final_drift = float(1.0 - abs(np.dot(consensus_vec, self.anchor)))
        audit.append(f"  Consensus drift from anchor: {final_drift:.4f}")

        overall_converged = gossip_converged and obstruction.obstruction_free
        audit.append(
            f"  RESULT: converged={overall_converged} "
            f"(gossip={gossip_converged}, obstruction_free={obstruction.obstruction_free})"
        )

        return ConsensusResult(
            converged=overall_converged,
            rounds_run=rounds_run,
            consensus_vector=consensus_vec,
            grey_agents=grey_ids,
            obstruction_report=obstruction,
            final_drift=final_drift,
            audit_trail=audit,
        )

    # ──────────────────────────────────────────────────────────────
    # DIAGNOSTICS
    # ──────────────────────────────────────────────────────────────

    def network_stats(self, agent_id: str) -> NetworkStats:
        """Compute NetworkStats for a given agent (for GreyMode r_merge)."""
        drifts = [
            1.0 - abs(float(np.dot(n.state, self.anchor)))
            for n in self._nodes.values()
        ]
        local_drift = 1.0 - abs(
            float(np.dot(self._nodes[agent_id].state, self.anchor))
        )
        global_var = float(np.std(drifts)) if len(drifts) > 1 else 0.0
        return NetworkStats(
            sigma_local=local_drift,
            sigma_global=global_var,
            node_count=len(self._nodes),
        )

    def summary(self) -> str:
        """Plain-English network snapshot."""
        lines = [f"PsiConsensus -- {len(self._nodes)} agents"]
        for aid, node in self._nodes.items():
            drift = 1.0 - abs(float(np.dot(node.state, self.anchor)))
            monitor = self._grey_monitors[aid]
            lines.append(
                f"  {aid}: drift={drift:.4f}, "
                f"grey_status={monitor.status.value}, "
                f"neighbors={node.neighbors}"
            )
        return "\n".join(lines)


# =============================================================================
# CONVENIENCE CONSTRUCTOR
# =============================================================================

def build_consensus(
    anchor: Optional[np.ndarray] = None,
    coherence: Optional[np.ndarray] = None,
    dim: int = 8,
    **kwargs,
) -> PsiConsensus:
    """
    Build a PsiConsensus with optional random anchor/coherence vectors.

    Parameters
    ----------
    anchor : np.ndarray, optional
        Anchor vector. Random unit vector if not provided.
    coherence : np.ndarray, optional
        Coherence field. Random unit vector if not provided.
    dim : int
        Vector dimension (only used when generating random vectors).
    **kwargs
        Forwarded to PsiConsensus constructor.
    """
    rng = np.random.default_rng(42)
    if anchor is None:
        anchor = rng.standard_normal(dim)
        anchor /= np.linalg.norm(anchor)
    if coherence is None:
        coherence = rng.standard_normal(dim)
        coherence /= np.linalg.norm(coherence)
    return PsiConsensus(anchor=anchor, coherence=coherence, **kwargs)
