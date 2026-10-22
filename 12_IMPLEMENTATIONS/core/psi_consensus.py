"""
Psi Consensus -- AURA Multi-Agent Coherence Protocol
=====================================================

Constitutional coherence across a network of agents. No central authority.
Consensus emerges from pairwise gossip gated by the Psi_Q operator, followed
by connectivity and neighbor-distance checks, with Grey Mode quarantine for
drifted nodes. These checks are proxies, not a sheaf cohomology computation.

SOURCE: AURA_PROTOCOL_COMPLETE_CONSOLIDATION (1).md
        Spec: 02_AURA_L3/PSI_CONSENSUS.md
Status: [SCAFFOLD] -- executable numerical protocol; guarantees remain unproven

FOUR MECHANISMS:
  GossipProtocol    -- pairwise exchange until ||DeltaPsi|| < eps_c
  PsiQOperator      -- merge only if invariant-curve aligned AND neighbor-consistent
  ObstructionDetector -- connectivity + local section consistency proxy
  AdaptiveThresholds  -- eps_c, theta_inv, eps_neighbor scale with network state

INTEGRATION:
  PsiConsensus wraps all four + one GreyModeMonitor per agent.
  Grey agents are quarantined before gossip; only healthy agents contribute.

The quarantine fraction is reported against a one-third budget. This does not
establish Byzantine fault tolerance against equivocation or malicious inputs.

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
from grey_mode import GreyModeMonitor, NetworkStats, anchor_drift as _anchor_drift


def _unit_state_vector(values) -> np.ndarray:
    """Validate public protocol inputs before any gossip or quarantine checks."""
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise ValueError("State vector must be a non-empty 1D sequence of floats")
    if not np.all(np.isfinite(arr)):
        raise ValueError("State vector must contain only finite values")
    norm = float(np.linalg.norm(arr))
    if not math.isfinite(norm):
        raise ValueError("State vector must have a finite norm")
    if norm < 1e-9:
        raise ValueError("State vector cannot have zero norm")
    return arr / norm


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
    Result of the connectivity and neighbor-distance consistency proxy.

    ``obstruction_free`` means a connected healthy graph whose neighboring
    vectors differ by at most the configured tolerance. It says nothing about
    dim H^1; exact cohomology is available through CellularSheaf separately.
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


def _positive_finite(name: str, value: float) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")
    return number


def _positive_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


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
        self.eps_c_base = _positive_finite("eps_c_base", eps_c_base)
        self.theta_inv_base = _positive_finite("theta_inv_base", theta_inv_base)
        self.eps_neighbor_base = _positive_finite("eps_neighbor_base", eps_neighbor_base)

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
      1. Invariant-curve aligned: the candidate merged state has signed
         alignment <candidate, anchor> >= theta_inv. The antipode of the
         anchor is maximal drift, not alignment.
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
        self.anchor = _unit_state_vector(anchor)
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
        alignment = float(np.dot(candidate, self.anchor))
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
    Connectivity and local consistency policy, retaining its legacy API name.

    This is an operational agreement proxy with two conditions:
      (a) G is connected (partition_count == 1).
          Disconnected partitions cannot exchange states through this graph.
      (b) All edges (i,j) are locally consistent:
          ||state_i - state_j|| <= eps_local.
          An inconsistent edge fails the configured distance tolerance.

    Neither condition computes H^1. A constant sheaf on a consistent cycle can
    have nonzero H^1, while a disconnected forest has H^1 = 0. Global sections
    belong to ker(delta^0), i.e. H^0; uniqueness needs further hypotheses.
    """

    def __init__(self, eps_local: float = 0.2):
        self.eps_local = eps_local

    def detect(
        self,
        states: Dict[str, np.ndarray],
        edges: List[Tuple[str, str]],
    ) -> ObstructionReport:
        """
        Run the connectivity and neighbor-distance consistency check.

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
      - ObstructionDetector (connectivity/consistency proxy)
      - AdaptiveThresholds (network-aware parameters)
      - GreyModeMonitor per agent (isolation/recovery for drifted nodes)

    No central authority. Consensus emerges from pairwise gossip.
    Drifted agents are quarantined (Grey Mode) before gossip begins.
    The reported one-third quarantine budget is not a fault-tolerance proof.

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
        self.anchor = _unit_state_vector(anchor)
        self.coherence = _unit_state_vector(coherence)
        if self.anchor.shape != self.coherence.shape:
            raise ValueError("anchor and coherence vectors must have identical dimension")
        self.thresholds = thresholds or AdaptiveThresholds()
        # A NaN threshold compares False everywhere and silently disables
        # quarantine; mu = 0 or max_rounds = 0 made gossip vacuous.
        self.mu = _positive_finite("mu", mu)
        if self.mu > 1.0:
            raise ValueError("mu must lie in (0, 1]")
        self.max_rounds = _positive_int("max_rounds", max_rounds)
        self.grey_kappa = _positive_finite("grey_kappa", grey_kappa)
        self.grey_sigma_hat = _positive_finite("grey_sigma_hat", grey_sigma_hat)
        self.grey_theta_x = _positive_finite("grey_theta_x", grey_theta_x)
        self.grey_alert_threshold = _positive_int("grey_alert_threshold", grey_alert_threshold)

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
            one side is sufficient. Every named neighbor must be registered
            by the time run() is called.

        Each agent_id may be registered once. Re-registering replaced the
        state and reset the Grey Mode monitor, which cleared a quarantine.
        """
        if agent_id in self._nodes:
            raise ValueError(f"Agent {agent_id!r} is already registered")
        vector = _unit_state_vector(state)
        if vector.shape != self.anchor.shape:
            raise ValueError(f"Agent '{agent_id}' state dimension does not match anchor")
        node = AgentNode(
            agent_id=agent_id,
            state=vector,
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
        drifts = [_anchor_drift(n.state, self.anchor) for n in self._nodes.values()]
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
            drift = _anchor_drift(state, self.anchor)
            # Angular deviation: arccos of signed alignment, clamped to [-1, 1]
            alignment = max(-1.0, min(1.0, float(np.dot(state, self.anchor))))
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
          4. Check connectivity and local consistency on final states.
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

        unknown = sorted(
            {nb for node in self._nodes.values() for nb in node.neighbors if nb not in self._nodes},
            key=repr,
        )
        if unknown:
            # Dropping these silently changed the topology the caller declared.
            raise ValueError(f"neighbors name unregistered agents: {unknown}")

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
            + (" -- within one-third quarantine budget" if grey_fraction <= 1/3
               else " -- EXCEEDS one-third quarantine budget")
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
            audit.append("  Connectivity/local-consistency proxy passed (H^1 not evaluated)")
        else:
            audit.append(
                f"  Connectivity/local-consistency proxy failed: "
                f"partitions={obstruction.partition_count}, "
                f"inconsistent_edges={len(obstruction.inconsistent_edges)}"
            )

        # Step 5: Consensus vector
        stacked = np.array(list(final_states.values()))
        mean_vec = np.mean(stacked, axis=0)
        cn = float(np.linalg.norm(mean_vec))
        if cn <= 1e-9:
            # The healthy states cancel, so there is no consensus direction.
            # Substituting the anchor here reported a fabricated drift of 0.
            final_drift = float(np.mean([_anchor_drift(s, self.anchor) for s in stacked]))
            audit.append("  Healthy states cancel -- no consensus direction")
            audit.append(
                f"  RESULT: converged=False (gossip={gossip_converged}, "
                f"obstruction_free={obstruction.obstruction_free}, consensus_direction=None)"
            )
            return ConsensusResult(
                converged=False,
                rounds_run=rounds_run,
                consensus_vector=None,
                grey_agents=grey_ids,
                obstruction_report=obstruction,
                final_drift=final_drift,
                audit_trail=audit,
            )
        consensus_vec = mean_vec / cn

        final_drift = _anchor_drift(consensus_vec, self.anchor)
        audit.append(f"  Consensus drift from anchor: {final_drift:.4f}")

        # The consensus must itself lie on the invariant curve. Otherwise a
        # network agreeing far from the anchor converged whenever this run
        # quarantined no one.
        anchor_aligned = float(np.dot(consensus_vec, self.anchor)) >= theta_inv
        overall_converged = gossip_converged and obstruction.obstruction_free and anchor_aligned
        result_line = (
            f"  RESULT: converged={overall_converged} "
            f"(gossip={gossip_converged}, obstruction_free={obstruction.obstruction_free}"
        )
        if not anchor_aligned:
            result_line += f", anchor_aligned=False at theta_inv={theta_inv:.4f}"
        audit.append(result_line + ")")

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
        drifts = [_anchor_drift(n.state, self.anchor) for n in self._nodes.values()]
        local_drift = _anchor_drift(self._nodes[agent_id].state, self.anchor)
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
            drift = _anchor_drift(node.state, self.anchor)
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
