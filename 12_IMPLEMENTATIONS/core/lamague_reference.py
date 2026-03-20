"""
LAMAGUE Reference Implementation
Complete Python codebase for all core systems
"""

import numpy as np
from typing import List, Tuple, Callable, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class SymbolClass(Enum):
    """LAMAGUE symbol classes"""
    I_CLASS = "invariant"    # Stable anchors
    D_CLASS = "dynamic"      # Transformations
    F_CLASS = "field"        # State variables
    M_CLASS = "meta"         # Compression operators

@dataclass
class LAMAGUESymbol:
    """Individual LAMAGUE symbol"""
    symbol: str
    class_type: SymbolClass
    meaning: str
    vector_rep: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class Evidence:
    """Evidence for knowledge block"""
    content: str
    source: str
    quality_weight: float  # 0.0 to 1.0
    date: datetime
    
@dataclass  
class KnowledgeBlock:
    """Unit of knowledge in Pyramid"""
    content: str
    evidence: List[Evidence]
    dependencies: set
    created: datetime
    last_updated: datetime
    
    def calculate_power(self) -> float:
        """Structural impact"""
        return len(self.dependencies)
    
    def calculate_evidence(self) -> float:
        """Quality-weighted evidence count"""
        return sum(e.quality_weight for e in self.evidence)
    
    def calculate_entropy(self) -> float:
        """Uncertainty measure"""
        if not self.evidence:
            return 1.0
        qualities = [e.quality_weight for e in self.evidence]
        return np.std(qualities) / (np.mean(qualities) + 1e-6)
    
    def truth_pressure(self) -> float:
        """Calculate Π"""
        E = self.calculate_evidence()
        P = self.calculate_power()
        S = self.calculate_entropy()
        return (E * P) / (S + 1e-6)

# ============================================================================
# TRIAD KERNEL
# ============================================================================

class TRIADKernel:
    """
    Three-fold Recursive Integration & Ascent Dynamics
    Core computational engine for drift correction
    """
    
    def __init__(self, 
                 anchor_vector: np.ndarray,
                 coherence_field: np.ndarray,
                 alpha: float = 0.4,
                 beta: float = 0.3,
                 gamma: float = 0.3):
        """
        Initialize TRIAD kernel
        
        Args:
            anchor_vector: Stable reference point (immutable)
            coherence_field: Target coherence distribution
            alpha, beta, gamma: Operator weights (should sum to 1.0)
        """
        self.anchor = anchor_vector / np.linalg.norm(anchor_vector)
        self.coherence = coherence_field
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.history = []
        
    def anchor_operator(self, state: np.ndarray) -> np.ndarray:
        """
        Ao: Project to low-entropy subspace
        Idempotent projection to anchor
        """
        projection = np.dot(state, self.anchor)
        return projection * self.anchor
    
    def ascent_operator(self, state: np.ndarray, dt: float = 0.1) -> np.ndarray:
        """
        Φ↑: Gradient ascent toward coherence
        Unitary evolution along coherence gradient
        """
        gradient = self.compute_coherence_gradient(state)
        ascended = state + dt * gradient
        return ascended / np.linalg.norm(ascended)  # Normalize
    
    def fold_operator(self, current_state: np.ndarray) -> np.ndarray:
        """
        Ψ: Integration of past states
        Causal, contractive memory integration
        """
        if not self.history:
            return current_state
        
        t = len(self.history)
        integrated = np.zeros_like(current_state)
        
        # Exponential kernel K(t,s) = exp(-(t-s))
        for s, past_state in enumerate(self.history):
            weight = np.exp(-(t - s))
            integrated += weight * past_state
        
        # Normalize
        integrated /= sum(np.exp(-(t - s)) for s in range(t))
        return integrated
    
    def compute_coherence_gradient(self, state: np.ndarray) -> np.ndarray:
        """Gradient of coherence functional"""
        # Simplified: direction toward coherence field
        direction = self.coherence - state
        return direction / (np.linalg.norm(direction) + 1e-6)
    
    def step(self, current_state: np.ndarray) -> np.ndarray:
        """
        Single TRIAD iteration: Ao → Φ↑ → Ψ
        
        Returns:
            Updated state after one iteration
        """
        # 1. Anchor
        anchored = self.anchor_operator(current_state)
        
        # 2. Ascent
        ascended = self.ascent_operator(
            self.alpha * anchored + (1 - self.alpha) * current_state
        )
        
        # 3. Fold
        self.history.append(ascended)
        folded = self.fold_operator(ascended)
        
        return folded
    
    def detect_drift(self, state: np.ndarray) -> float:
        """
        Measure drift from anchor
        Returns: Drift magnitude [0, 1]
        """
        alignment = np.dot(state, self.anchor)
        drift = 1.0 - abs(alignment)
        return drift
    
    def correct_until_converged(self,
                               initial_state: np.ndarray,
                               threshold: float = 1e-4,
                               max_iter: int = 1000) -> Tuple[np.ndarray, int]:
        """
        Iterate TRIAD until convergence
        
        Returns:
            (converged_state, num_iterations)
        """
        state = initial_state
        errors = []
        
        for i in range(max_iter):
            new_state = self.step(state)
            error = np.linalg.norm(new_state - state)
            errors.append(error)
            
            if error < threshold:
                return new_state, i, errors
            
            state = new_state
        
        return state, max_iter, errors

# ============================================================================
# PYRAMID CASCADE
# ============================================================================

class PyramidCascade:
    """
    Self-organizing knowledge architecture
    Three-layer system with automatic reorganization
    """
    
    EPSILON = 0.1  # Cascade threshold
    
    def __init__(self):
        self.foundation = []  # Π ≥ 1.5
        self.middle = []      # 1.2 ≤ Π < 1.5
        self.edge = []        # Π < 1.2
        self.ledger = EnergyLedger()
        self.previous_entropy = 0
        
    def add_block(self, block: KnowledgeBlock):
        """Add block to appropriate layer"""
        π = block.truth_pressure()
        
        if π >= 1.5:
            if self.should_cascade(block):
                self.execute_cascade(block)
            else:
                self.foundation.append(block)
        elif π >= 1.2:
            self.middle.append(block)
        else:
            self.edge.append(block)
    
    def should_cascade(self, new_block: KnowledgeBlock) -> bool:
        """Check if new block triggers cascade"""
        if not self.foundation:
            return False
        
        π_new = new_block.truth_pressure()
        π_min = min(b.truth_pressure() for b in self.foundation)
        
        return π_new > π_min + self.EPSILON
    
    def execute_cascade(self, new_block: KnowledgeBlock):
        """
        Reorganize pyramid structure
        
        Process:
        1. Calculate reorganization energy
        2. Compress and demote old foundation
        3. Promote new block
        4. Verify entropy decrease
        """
        # Calculate energy
        π_new = new_block.truth_pressure()
        π_min = min(b.truth_pressure() for b in self.foundation)
        energy = (π_new - π_min) * len(self.foundation)
        
        # Log to audit trail
        self.ledger.spend(energy, "cascade_reorganization", {
            'new_block': new_block.content,
            'old_foundation_size': len(self.foundation),
            'π_increase': π_new - π_min
        })
        
        # Store previous entropy
        self.previous_entropy = self.total_entropy()
        
        # Compress and demote
        for block in self.foundation:
            # Compression preserves essence
            compressed = self.compress_block(block)
            self.middle.append(compressed)
        
        # Clear and promote
        self.foundation = [new_block]
        
        # Verify entropy decrease
        new_entropy = self.total_entropy()
        assert new_entropy < self.previous_entropy, \
            f"Cascade increased entropy: {self.previous_entropy} → {new_entropy}"
    
    def compress_block(self, block: KnowledgeBlock) -> KnowledgeBlock:
        """Compress block while preserving invariants"""
        # Simplified: reduce evidence but keep core
        compressed_evidence = block.evidence[:3]  # Keep top 3
        
        return KnowledgeBlock(
            content=f"[Compressed] {block.content}",
            evidence=compressed_evidence,
            dependencies=block.dependencies,
            created=block.created,
            last_updated=datetime.now()
        )
    
    def total_entropy(self) -> float:
        """Calculate total system entropy"""
        entropy = 0
        
        for layer in [self.foundation, self.middle, self.edge]:
            for block in layer:
                entropy += block.calculate_entropy()
        
        return entropy
    
    def get_layer_for_pressure(self, π: float) -> str:
        """Determine layer for given truth pressure"""
        if π >= 1.5:
            return "FOUNDATION"
        elif π >= 1.2:
            return "MIDDLE"
        else:
            return "EDGE"

# ============================================================================
# ENERGY LEDGER (AUDIT SYSTEM)
# ============================================================================

class EnergyLedger:
    """
    Immutable audit trail for all operations
    Provides full accountability and forensics
    """
    
    def __init__(self):
        self.log = []
        self.total_energy = 0
        
    def spend(self, amount: float, operation: str, context: Dict):
        """
        Log energy expenditure
        
        Args:
            amount: Energy cost
            operation: Description of operation
            context: Additional metadata
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'amount': amount,
            'operation': operation,
            'context': context,
            'cumulative': self.total_energy + amount
        }
        
        self.log.append(entry)
        self.total_energy += amount
    
    def audit(self) -> Dict:
        """Generate audit report"""
        return {
            'total_energy': self.total_energy,
            'num_operations': len(self.log),
            'operations': self.log,
            'violations': self.detect_violations()
        }
    
    def detect_violations(self) -> List[str]:
        """Check for suspicious patterns"""
        violations = []
        
        # Check for sudden spikes
        if len(self.log) > 1:
            amounts = [e['amount'] for e in self.log]
            mean = np.mean(amounts)
            std = np.std(amounts)
            
            for i, amount in enumerate(amounts):
                if amount > mean + 3 * std:
                    violations.append(
                        f"Operation {i}: Unusual energy spike ({amount:.2f})"
                    )
        
        return violations
    
    def export_json(self, filepath: str):
        """Export audit trail to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.audit(), f, indent=2)

# ============================================================================
# MULTI-AGENT CONSENSUS
# ============================================================================

class AgentMode(Enum):
    """Agent operational modes"""
    HEALTHY = "healthy"
    ALIGNED = "aligned"
    GREY = "grey"
    ADVERSARIAL = "adversarial"

@dataclass
class Agent:
    """Individual agent in network"""
    id: str
    state: np.ndarray
    anchor: np.ndarray
    mode: AgentMode = AgentMode.HEALTHY
    drift_history: List[float] = field(default_factory=list)
    
    def detect_drift(self) -> float:
        """Measure drift from anchor"""
        alignment = np.dot(self.state, self.anchor)
        drift = 1.0 - abs(alignment)
        self.drift_history.append(drift)
        return drift

class AgentNetwork:
    """
    Multi-agent system with emergent consensus
    No central authority - consensus emerges from healthy agents
    """
    
    DRIFT_THRESHOLD = 0.4
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.consensus: Optional[np.ndarray] = None
        
    def add_agent(self, agent: Agent):
        """Add agent to network"""
        self.agents.append(agent)
    
    def compute_consensus(self) -> np.ndarray:
        """
        Calculate emergent consensus
        Excludes adversarial and grey agents
        """
        healthy_states = [
            agent.state for agent in self.agents
            if agent.mode in [AgentMode.HEALTHY, AgentMode.ALIGNED]
        ]
        
        if not healthy_states:
            raise ValueError("No healthy agents for consensus")
        
        # Simple averaging (can use more sophisticated methods)
        self.consensus = np.mean(healthy_states, axis=0)
        return self.consensus
    
    def update_agent_modes(self):
        """Check all agents and update modes based on drift"""
        for agent in self.agents:
            drift = agent.detect_drift()
            
            if drift > self.DRIFT_THRESHOLD:
                if agent.mode != AgentMode.GREY:
                    print(f"Agent {agent.id} entering GREY mode (drift={drift:.3f})")
                    agent.mode = AgentMode.GREY
            elif agent.mode == AgentMode.GREY and drift < self.DRIFT_THRESHOLD * 0.5:
                # Recovery: sustained low drift
                if len(agent.drift_history) >= 10:
                    recent_drift = agent.drift_history[-10:]
                    if all(d < self.DRIFT_THRESHOLD * 0.5 for d in recent_drift):
                        print(f"Agent {agent.id} recovered from GREY mode")
                        agent.mode = AgentMode.HEALTHY
    
    def iterate_consensus(self, num_iterations: int = 100):
        """
        Run consensus algorithm
        Agents converge toward emergent agreement
        """
        for i in range(num_iterations):
            # Compute current consensus
            try:
                consensus = self.compute_consensus()
            except ValueError:
                print("No healthy agents - cannot compute consensus")
                break
            
            # Update agent modes
            self.update_agent_modes()
            
            # Apply gentle correction toward consensus
            for agent in self.agents:
                if agent.mode in [AgentMode.HEALTHY, AgentMode.ALIGNED]:
                    # Move 10% toward consensus
                    agent.state = 0.9 * agent.state + 0.1 * consensus
                    # Renormalize
                    agent.state /= np.linalg.norm(agent.state)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_triad_correction():
    """Example: TRIAD drift correction"""
    print("=== TRIAD Drift Correction Example ===\n")
    
    # Setup
    dim = 10
    anchor = np.random.randn(dim)
    anchor /= np.linalg.norm(anchor)
    
    coherence_field = np.random.randn(dim)
    coherence_field /= np.linalg.norm(coherence_field)
    
    # Create drifted state
    drifted_state = anchor + 0.5 * np.random.randn(dim)
    drifted_state /= np.linalg.norm(drifted_state)
    
    # Initialize TRIAD
    triad = TRIADKernel(anchor, coherence_field)
    
    print(f"Initial drift: {triad.detect_drift(drifted_state):.4f}")
    
    # Correct
    converged, iters, errors = triad.correct_until_converged(drifted_state)
    
    print(f"Converged in {iters} iterations")
    print(f"Final drift: {triad.detect_drift(converged):.4f}")
    print(f"Convergence rate λ ≈ {errors[-1]/errors[0]:.4f}")

def example_pyramid_cascade():
    """Example: Pyramid cascade event"""
    print("\n=== Pyramid Cascade Example ===\n")
    
    pyramid = PyramidCascade()
    
    # Add foundation block
    foundation_block = KnowledgeBlock(
        content="Classical mechanics",
        evidence=[
            Evidence("Newton's laws", "Principia", 1.0, datetime(1687, 7, 5)),
            Evidence("Planetary motion", "Observations", 0.9, datetime(1700, 1, 1))
        ],
        dependencies={"physics", "mathematics"},
        created=datetime(1687, 7, 5),
        last_updated=datetime.now()
    )
    
    pyramid.add_block(foundation_block)
    print(f"Added foundation: Π = {foundation_block.truth_pressure():.2f}")
    
    # Add revolutionary block
    relativity_block = KnowledgeBlock(
        content="Special relativity",
        evidence=[
            Evidence("Light speed constant", "Experiments", 1.0, datetime(1905, 6, 30)),
            Evidence("E=mc²", "Theory", 1.0, datetime(1905, 9, 27)),
            Evidence("Time dilation", "Muon decay", 0.95, datetime(1941, 1, 1))
        ],
        dependencies={"physics", "mathematics", "spacetime"},
        created=datetime(1905, 6, 30),
        last_updated=datetime.now()
    )
    
    print(f"\nNew theory: Π = {relativity_block.truth_pressure():.2f}")
    
    if pyramid.should_cascade(relativity_block):
        print("\n🔥 CASCADE TRIGGERED!")
        pyramid.execute_cascade(relativity_block)
        print("✓ Cascade complete")
        print(f"Foundation now: {len(pyramid.foundation)} blocks")
        print(f"Middle layer: {len(pyramid.middle)} blocks")

def example_multi_agent():
    """Example: Multi-agent consensus"""
    print("\n=== Multi-Agent Consensus Example ===\n")
    
    network = AgentNetwork()
    dim = 5
    
    # Create agents with slight variations
    base_anchor = np.array([1, 0, 0, 0, 0], dtype=float)
    
    for i in range(10):
        state = base_anchor + 0.2 * np.random.randn(dim)
        state /= np.linalg.norm(state)
        
        agent = Agent(
            id=f"agent_{i}",
            state=state,
            anchor=base_anchor
        )
        network.add_agent(agent)
    
    # Add one adversarial agent
    adversarial = Agent(
        id="adversarial",
        state=-base_anchor,  # Opposite direction
        anchor=base_anchor,
        mode=AgentMode.ADVERSARIAL
    )
    network.add_agent(adversarial)
    
    print(f"Initial variance: {np.var([a.state for a in network.agents]):.4f}")
    
    # Run consensus
    network.iterate_consensus(num_iterations=50)
    
    consensus = network.compute_consensus()
    final_variance = np.var([
        a.state for a in network.agents 
        if a.mode != AgentMode.ADVERSARIAL
    ])
    
    print(f"Final variance: {final_variance:.4f}")
    print(f"Consensus alignment: {np.dot(consensus, base_anchor):.4f}")

if __name__ == "__main__":
    example_triad_correction()
    example_pyramid_cascade()
    example_multi_agent()
    
    print("\n" + "="*60)
    print("✅ All examples complete!")
    print("="*60)
