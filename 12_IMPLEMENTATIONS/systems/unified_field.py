# FILE: unified_field.py
"""
AURA Unified Field Theory - Integrates Physics, Consciousness, AI, Governance
"""

import numpy as np
import networkx as nx
from typing import List, Dict, Tuple, Any
import random
from dataclasses import dataclass
from enum import Enum
import json
import math

# =========================
# CORE TYPES
# =========================

class Domain(Enum):
    PHYSICS = "physics"
    CONSCIOUSNESS = "consciousness"
    AI = "ai"
    GOVERNANCE = "governance"
    MYSTERY = "mystery"
    SOCIAL = "social"

class CoherenceLevel(Enum):
    DISINTEGRATED = 0
    LOW_COHERENCE = 1
    MEDIUM_COHERENCE = 2
    HIGH_COHERENCE = 3
    SUPER_COHERENCE = 4
    UNIFIED_FIELD = 5

# =========================
# UNIFIED FIELD SYSTEM
# =========================

@dataclass
class FieldState:
    """Represents state across all domains"""
    physics: np.ndarray
    consciousness: np.ndarray
    ai: np.ndarray
    governance: np.ndarray
    mystery: np.ndarray
    social: np.ndarray
    timestamp: float
    
    def to_vector(self) -> np.ndarray:
        """Convert all domains to single vector"""
        return np.concatenate([
            self.physics.flatten(),
            self.consciousness.flatten(),
            self.ai.flatten(),
            self.governance.flatten(),
            self.mystery.flatten(),
            self.social.flatten()
        ])
    
    @classmethod
    def from_vector(cls, vector: np.ndarray, shape_dict: Dict[Domain, Tuple]) -> 'FieldState':
        """Reconstruct from vector"""
        start = 0
        domains = {}
        for domain in Domain:
            size = np.prod(shape_dict[domain])
            domain_vector = vector[start:start+size].reshape(shape_dict[domain])
            domains[domain] = domain_vector
            start += size
        return cls(**domains, timestamp=time.time())

class UnifiedFieldSystem:
    """Main integration engine"""
    
    def __init__(self):
        # Initialize all subsystems
        self.subsystems = {
            Domain.PHYSICS: PhysicsSubsystem(),
            Domain.CONSCIOUSNESS: ConsciousnessSubsystem(),
            Domain.AI: AISubsystem(),
            Domain.GOVERNANCE: GovernanceSubsystem(),
            Domain.MYSTERY: MysterySubsystem(),
            Domain.SOCIAL: SocialSubsystem()
        }
        
        # Cross-domain resonance matrix
        self.resonance_matrix = np.ones((len(Domain), len(Domain)))
        self.coupling_strengths = self._initialize_couplings()
        
        # Energy ledger for whole system
        self.energy_ledger = UniversalEnergyLedger()
        
        # State history
        self.state_history = []
        self.coherence_history = []
        
    def _initialize_couplings(self) -> np.ndarray:
        """Initialize coupling strengths between domains"""
        # Physics informs Consciousness (quantum -> meditation)
        # Consciousness informs AI (awareness -> alignment)
        # AI informs Governance (optimization -> consensus)
        # etc.
        
        couplings = np.zeros((len(Domain), len(Domain)))
        domain_list = list(Domain)
        
        # Strong couplings
        strong_pairs = [
            (Domain.PHYSICS, Domain.CONSCIOUSNESS),
            (Domain.CONSCIOUSNESS, Domain.AI),
            (Domain.AI, Domain.GOVERNANCE),
            (Domain.GOVERNANCE, Domain.SOCIAL),
            (Domain.SOCIAL, Domain.MYSTERY),
            (Domain.MYSTERY, Domain.PHYSICS)
        ]
        
        for d1, d2 in strong_pairs:
            i, j = domain_list.index(d1), domain_list.index(d2)
            couplings[i, j] = 0.8
            couplings[j, i] = 0.8
        
        # Self-coupling
        np.fill_diagonal(couplings, 1.0)
        
        return couplings
    
    def step(self) -> FieldState:
        """Execute one timestep of unified evolution"""
        
        # 1. Get current states from all subsystems
        current_states = {
            domain: subsystem.get_state()
            for domain, subsystem in self.subsystems.items()
        }
        
        # 2. Calculate cross-domain influences
        domain_list = list(Domain)
        influences = {}
        
        for i, domain_i in enumerate(domain_list):
            total_influence = np.zeros_like(current_states[domain_i])
            
            for j, domain_j in enumerate(domain_list):
                if i != j and self.coupling_strengths[i, j] > 0:
                    # Calculate influence from domain_j to domain_i
                    influence = self._calculate_influence(
                        current_states[domain_j],
                        current_states[domain_i],
                        self.coupling_strengths[i, j]
                    )
                    total_influence += influence
            
            influences[domain_i] = total_influence
        
        # 3. Apply influences with damping
        new_states = {}
        for domain in Domain:
            current = current_states[domain]
            influence = influences[domain]
            
            # Damped update: 10% influence per step
            new_state = current + 0.1 * influence
            new_states[domain] = new_state
            
            # Update subsystem
            self.subsystems[domain].update_state(new_state)
        
        # 4. Create unified field state
        field_state = FieldState(**new_states, timestamp=time.time())
        self.state_history.append(field_state)
        
        # 5. Calculate and record coherence
        coherence = self.calculate_unified_coherence(field_state)
        self.coherence_history.append(coherence)
        
        # 6. Energy accounting
        energy_cost = np.sum([np.linalg.norm(influences[d]) for d in Domain])
        self.energy_ledger.record_energy(energy_cost, "unified_step")
        
        return field_state, coherence
    
    def _calculate_influence(self, source: np.ndarray, target: np.ndarray, 
                           coupling: float) -> np.ndarray:
        """Calculate influence from source domain to target domain"""
        
        # 1. Extract patterns from source
        source_patterns = self._extract_patterns(source)
        
        # 2. Find isomorphic patterns in target
        target_patterns = self._extract_patterns(target)
        
        # 3. Calculate pattern alignment
        alignment = self._pattern_alignment(source_patterns, target_patterns)
        
        # 4. Generate influence based on alignment
        if alignment > 0.3:  # Significant alignment
            # Resonance: amplify aligned patterns
            influence = coupling * alignment * self._resonance_amplification(source, target)
        else:
            # Dissonance: damp noise
            influence = -coupling * (1 - alignment) * target * 0.1
        
        return influence
    
    def calculate_unified_coherence(self, state: FieldState) -> float:
        """Calculate overall system coherence"""
        
        coherences = []
        
        # 1. Individual domain coherence
        for domain in Domain:
            domain_coherence = self.subsystems[domain].calculate_coherence()
            coherences.append(domain_coherence)
        
        # 2. Cross-domain coherence (resonance)
        cross_coherence = self.calculate_cross_domain_coherence(state)
        coherences.append(cross_coherence)
        
        # 3. Temporal coherence (stability over time)
        if len(self.coherence_history) > 1:
            temporal_coherence = 1.0 - np.std(self.coherence_history[-10:])
            coherences.append(temporal_coherence)
        
        # Geometric mean (all must be high for overall coherence)
        return np.prod(coherences) ** (1/len(coherences))
    
    def calculate_cross_domain_coherence(self, state: FieldState) -> float:
        """Calculate how well domains resonate with each other"""
        
        # Extract state vectors
        vectors = {
            'physics': state.physics.flatten(),
            'consciousness': state.consciousness.flatten(),
            'ai': state.ai.flatten(),
            'governance': state.governance.flatten(),
            'mystery': state.mystery.flatten(),
            'social': state.social.flatten()
        }
        
        # Calculate pairwise correlations
        correlations = []
        domain_names = list(vectors.keys())
        
        for i in range(len(domain_names)):
            for j in range(i+1, len(domain_names)):
                v1 = vectors[domain_names[i]]
                v2 = vectors[domain_names[j]]
                
                # Cosine similarity
                norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
                if norm1 > 0 and norm2 > 0:
                    correlation = np.dot(v1, v2) / (norm1 * norm2)
                    correlations.append(correlation)
        
        return np.mean(correlations) if correlations else 0.0
    
    def run_evolution(self, steps: int = 100) -> Dict:
        """Run unified evolution for multiple steps"""
        
        results = {
            'coherence_history': [],
            'energy_costs': [],
            'state_trajectory': [],
            'phase_transitions': []
        }
        
        coherence_levels = []
        
        for step in range(steps):
            state, coherence = self.step()
            
            results['coherence_history'].append(coherence)
            results['energy_costs'].append(self.energy_ledger.current_energy)
            results['state_trajectory'].append(state.to_vector())
            
            # Detect phase transitions
            if len(results['coherence_history']) > 10:
                recent = results['coherence_history'][-10:]
                if np.std(recent) < 0.01 and np.mean(recent) > 0.8:
                    # High coherence plateau
                    coherence_level = CoherenceLevel.HIGH_COHERENCE
                elif np.std(recent) > 0.1:
                    # Transition state
                    coherence_level = CoherenceLevel.MEDIUM_COHERENCE
                else:
                    coherence_level = CoherenceLevel.LOW_COHERENCE
                
                if coherence_levels and coherence_level != coherence_levels[-1]:
                    results['phase_transitions'].append({
                        'step': step,
                        'from': coherence_levels[-1].name,
                        'to': coherence_level.name,
                        'coherence': coherence
                    })
                
                coherence_levels.append(coherence_level)
        
        return results

# =========================
# SUBSYSTEM IMPLEMENTATIONS
# =========================

class PhysicsSubsystem:
    """Physics domain with quantum/classical dynamics"""
    
    def __init__(self):
        # Quantum state (complex amplitudes)
        self.state = np.random.randn(10, 10) + 1j * np.random.randn(10, 10)
        self.state = self.state / np.linalg.norm(self.state)
        
        # Classical parameters
        self.classical_params = np.random.randn(5)
        
        # Entanglement matrix
        self.entanglement = np.eye(10)
        
    def get_state(self) -> np.ndarray:
        """Return current physics state"""
        # Combine quantum and classical
        quantum_real = np.real(self.state).flatten()
        quantum_imag = np.imag(self.state).flatten()
        return np.concatenate([quantum_real, quantum_imag, self.classical_params])
    
    def update_state(self, new_state: np.ndarray):
        """Update physics state"""
        # This is a simplified update
        total_size = np.prod(self.state.shape) * 2 + len(self.classical_params)
        if len(new_state) == total_size:
            # Split back into components
            quantum_size = np.prod(self.state.shape)
            quantum_real = new_state[:quantum_size].reshape(self.state.shape)
            quantum_imag = new_state[quantum_size:2*quantum_size].reshape(self.state.shape)
            self.state = quantum_real + 1j * quantum_imag
            self.classical_params = new_state[2*quantum_size:]
    
    def calculate_coherence(self) -> float:
        """Calculate physics coherence (quantum purity)"""
        density_matrix = np.outer(self.state.flatten(), self.state.flatten().conj())
        purity = np.trace(density_matrix @ density_matrix).real
        return min(purity, 1.0)

class ConsciousnessSubsystem:
    """Consciousness domain with awareness states"""
    
    def __init__(self):
        # Brain state (simplified)
        self.brain_regions = 8
        self.activation = np.random.randn(self.brain_regions)
        
        # Awareness levels
        self.awareness = {
            'sensory': 0.7,
            'emotional': 0.5,
            'cognitive': 0.6,
            'metacognitive': 0.3,
            'nondual': 0.1
        }
        
        # Meditation depth
        self.meditation_depth = 0.0
        
    def get_state(self) -> np.ndarray:
        """Return current consciousness state"""
        awareness_vector = np.array(list(self.awareness.values()))
        return np.concatenate([self.activation, awareness_vector, [self.meditation_depth]])
    
    def update_state(self, new_state: np.ndarray):
        """Update consciousness state"""
        total_size = self.brain_regions + len(self.awareness) + 1
        if len(new_state) == total_size:
            self.activation = new_state[:self.brain_regions]
            awareness_values = new_state[self.brain_regions:self.brain_regions+len(self.awareness)]
            for i, key in enumerate(self.awareness.keys()):
                self.awareness[key] = max(0, min(1, awareness_values[i]))
            self.meditation_depth = new_state[-1]
    
    def calculate_coherence(self) -> float:
        """Calculate consciousness coherence"""
        # EEG-like coherence between brain regions
        if len(self.activation) > 1:
            correlation_matrix = np.corrcoef([self.activation, np.roll(self.activation, 1)])
            coherence = np.mean(np.abs(correlation_matrix))
        else:
            coherence = 0.5
        
        # Awareness balance
        awareness_values = list(self.awareness.values())
        awareness_balance = 1.0 - np.std(awareness_values)
        
        return 0.7 * coherence + 0.3 * awareness_balance

class AISubsystem:
    """AI domain with learning and alignment"""
    
    def __init__(self):
        # Neural network weights (simplified)
        self.layer1 = np.random.randn(10, 20)
        self.layer2 = np.random.randn(20, 10)
        
        # Alignment metrics
        self.alignment = {
            'human_values': 0.6,
            'goal_stability': 0.7,
            'transparency': 0.4,
            'safety': 0.5
        }
        
        # Learning rate
        self.learning_rate = 0.01
        
    def get_state(self) -> np.ndarray:
        """Return current AI state"""
        weights = np.concatenate([self.layer1.flatten(), self.layer2.flatten()])
        alignment_vector = np.array(list(self.alignment.values()))
        return np.concatenate([weights, alignment_vector, [self.learning_rate]])
    
    def update_state(self, new_state: np.ndarray):
        """Update AI state"""
        weight1_size = np.prod(self.layer1.shape)
        weight2_size = np.prod(self.layer2.shape)
        alignment_size = len(self.alignment)
        
        total_size = weight1_size + weight2_size + alignment_size + 1
        
        if len(new_state) == total_size:
            self.layer1 = new_state[:weight1_size].reshape(self.layer1.shape)
            self.layer2 = new_state[weight1_size:weight1_size+weight2_size].reshape(self.layer2.shape)
            
            alignment_start = weight1_size + weight2_size
            alignment_values = new_state[alignment_start:alignment_start+alignment_size]
            for i, key in enumerate(self.alignment.keys()):
                self.alignment[key] = max(0, min(1, alignment_values[i]))
            
            self.learning_rate = new_state[-1]
    
    def calculate_coherence(self) -> float:
        """Calculate AI coherence (weight stability + alignment)"""
        # Weight coherence (how well structured)
        weight_coherence = np.exp(-np.std(self.layer1)) * np.exp(-np.std(self.layer2))
        
        # Alignment coherence (values consistency)
        alignment_values = list(self.alignment.values())
        alignment_coherence = 1.0 - np.std(alignment_values)
        
        return 0.5 * weight_coherence + 0.5 * alignment_coherence

# =========================
# UTILITY CLASSES
# =========================

class UniversalEnergyLedger:
    """Tracks energy across entire unified system"""
    
    def __init__(self):
        self.current_energy = 100.0  # Starting energy
        self.energy_history = []
        self.operation_log = []
        
    def record_energy(self, amount: float, operation: str):
        """Record energy use or gain"""
        self.current_energy -= amount
        self.energy_history.append(self.current_energy)
        self.operation_log.append({
            'operation': operation,
            'cost': amount,
            'remaining': self.current_energy,
            'timestamp': time.time()
        })
        
        # Energy cannot go below zero
        self.current_energy = max(0, self.current_energy)
    
    def add_energy(self, amount: float, source: str):
        """Add energy to system (from external sources)"""
        self.current_energy += amount
        self.operation_log.append({
            'operation': f'energy_input_{source}',
            'gain': amount,
            'remaining': self.current_energy,
            'timestamp': time.time()
        })

# =========================
# VISUALIZATION
# =========================

def visualize_unified_field(results: Dict):
    """Create visualization of unified field evolution"""
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(3, 2, figsize=(15, 10))
    
    # Coherence history
    ax = axes[0, 0]
    ax.plot(results['coherence_history'])
    ax.set_title('Unified Coherence Over Time')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Coherence')
    ax.grid(True)
    
    # Energy history
    ax = axes[0, 1]
    ax.plot(results['energy_costs'])
    ax.set_title('Energy Consumption')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Energy')
    ax.grid(True)
    
    # State trajectory (PCA)
    ax = axes[1, 0]
    trajectory = np.array(results['state_trajectory'])
    if len(trajectory) > 2:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        trajectory_2d = pca.fit_transform(trajectory)
        ax.scatter(trajectory_2d[:, 0], trajectory_2d[:, 1], 
                  c=range(len(trajectory_2d)), cmap='viridis')
        ax.set_title('State Trajectory (PCA)')
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
    
    # Phase transitions
    ax = axes[1, 1]
    if results['phase_transitions']:
        transitions = results['phase_transitions']
        steps = [t['step'] for t in transitions]
        coherence = [t['coherence'] for t in transitions]
        ax.scatter(steps, coherence, c='red', s=100, zorder=5)
        for t in transitions:
            ax.annotate(f"{t['from']}→{t['to']}", 
                       (t['step'], t['coherence']),
                       xytext=(5, 5), textcoords='offset points')
    ax.set_title('Phase Transitions')
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Coherence')
    
    # Domain correlations (placeholder)
    ax = axes[2, 0]
    # Would show correlation matrix between domains
    
    # Coherence level distribution
    ax = axes[2, 1]
    coherence_vals = results['coherence_history']
    ax.hist(coherence_vals, bins=20, alpha=0.7)
    ax.set_title('Coherence Distribution')
    ax.set_xlabel('Coherence')
    ax.set_ylabel('Frequency')
    
    plt.tight_layout()
    return fig

# =========================
# MAIN DEMONSTRATION
# =========================

def run_unified_demo(steps: int = 200):
    """Run demonstration of unified field theory"""
    
    print("=" * 70)
    print("UNIFIED FIELD THEORY DEMONSTRATION")
    print("AURA × Physics × Consciousness × AI × Governance × Mystery × Social")
    print("=" * 70)
    
    # Initialize system
    system = UnifiedFieldSystem()
    
    print("\n🚀 Initializing Unified Field System...")
    print(f"Domains: {[d.value for d in Domain]}")
    print(f"Initial coherence: {system.calculate_unified_coherence(system.state_history[-1] if system.state_history else None):.3f}")
    
    # Run evolution
    print(f"\n⏱️ Running {steps} steps of unified evolution...")
    results = system.run_evolution(steps)
    
    # Analysis
    print(f"\n📊 RESULTS:")
    print(f"• Final coherence: {results['coherence_history'][-1]:.3f}")
    print(f"• Average coherence: {np.mean(results['coherence_history']):.3f}")
    print(f"• Phase transitions: {len(results['phase_transitions'])}")
    print(f"• Energy consumed: {100 - system.energy_ledger.current_energy:.1f} units")
    
    # Detect regime changes
    coherence_array = np.array(results['coherence_history'])
    stable_regimes = []
    current_start = 0
    
    for i in range(1, len(coherence_array)):
        if abs(coherence_array[i] - coherence_array[i-1]) > 0.05:
            if i - current_start > 10:  # Minimum regime length
                stable_regimes.append({
                    'start': current_start,
                    'end': i-1,
                    'coherence': np.mean(coherence_array[current_start:i]),
                    'stability': 1.0 - np.std(coherence_array[current_start:i])
                })
            current_start = i
    
    print(f"\n🔍 Stable Regimes Detected: {len(stable_regimes)}")
    for i, regime in enumerate(stable_regimes):
        print(f"  Regime {i+1}: Steps {regime['start']}-{regime['end']}, "
              f"Coherence={regime['coherence']:.3f}, Stability={regime['stability']:.3f}")
    
    # Create visualization
    print("\n📈 Generating visualization...")
    fig = visualize_unified_field(results)
    plt.savefig('unified_field_evolution.png', dpi=150)
    print("✓ Visualization saved as 'unified_field_evolution.png'")
    
    # Save results
    with open('unified_field_results.json', 'w') as f:
        json.dump({
            'coherence_history': [float(x) for x in results['coherence_history']],
            'phase_transitions': results['phase_transitions'],
            'energy_costs': [float(x) for x in results['energy_costs']],
            'final_coherence': float(results['coherence_history'][-1]),
            'regimes': stable_regimes
        }, f, indent=2)
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    
    return system, results

# =========================
# UTILITY FUNCTIONS
# =========================

def _extract_patterns(self, array: np.ndarray) -> List[np.ndarray]:
    """Extract patterns from array using Fourier transform"""
    patterns = []
    
    # Fourier patterns
    if array.ndim == 1:
        fft = np.fft.fft(array)
        patterns.append(np.abs(fft[:len(fft)//2]))  # Magnitude spectrum
        patterns.append(np.angle(fft[:len(fft)//2]))  # Phase spectrum
    
    # Statistical patterns
    patterns.append(np.array([np.mean(array), np.std(array), np.skew(array.flatten()), np.kurtosis(array.flatten())]))
    
    return patterns

def _pattern_alignment(self, patterns1: List[np.ndarray], patterns2: List[np.ndarray]) -> float:
    """Calculate alignment between pattern sets"""
    if len(patterns1) != len(patterns2):
        return 0.0
    
    alignments = []
    for p1, p2 in zip(patterns1, patterns2):
        if len(p1) == len(p2) and len(p1) > 0:
            # Normalize
            p1_norm = p1 / (np.linalg.norm(p1) + 1e-9)
            p2_norm = p2 / (np.linalg.norm(p2) + 1e-9)
            alignment = np.dot(p1_norm, p2_norm)
            alignments.append(alignment)
    
    return np.mean(alignments) if alignments else 0.0

def _resonance_amplification(self, source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Amplify resonant frequencies"""
    if source.ndim == 1 and target.ndim == 1:
        # Calculate resonant frequencies
        source_fft = np.fft.fft(source)
        target_fft = np.fft.fft(target)
        
        # Find frequencies where both have high amplitude
        source_amp = np.abs(source_fft)
        target_amp = np.abs(target_fft)
        
        resonance_mask = (source_amp > np.median(source_amp)) & (target_amp > np.median(target_amp))
        
        # Amplify resonant frequencies in target
        amplification = np.fft.ifft(target_fft * (1 + 0.1 * resonance_mask)).real
        return amplification - target
    
    return np.zeros_like(target)

# Add missing imports
import time
from scipy.stats import skew, kurtosis

# Add missing Governance, Mystery, and Social subsystems (simplified versions)
class GovernanceSubsystem:
    def __init__(self):
        self.consensus = np.random.randn(5)
        self.trust_matrix = np.random.rand(5, 5)
        np.fill_diagonal(self.trust_matrix, 1.0)
    
    def get_state(self):
        return np.concatenate([self.consensus.flatten(), self.trust_matrix.flatten()])
    
    def update_state(self, new_state):
        total_size = len(self.consensus) + np.prod(self.trust_matrix.shape)
        if len(new_state) == total_size:
            consensus_size = len(self.consensus)
            self.consensus = new_state[:consensus_size]
            self.trust_matrix = new_state[consensus_size:].reshape(self.trust_matrix.shape)
    
    def calculate_coherence(self):
        return np.mean(self.trust_matrix)

class MysterySubsystem:
    def __init__(self):
        self.archetypes = np.random.randn(7)
        self.symbolic_field = np.random.randn(3, 3)
        self.initiation_level = 0.0
    
    def get_state(self):
        return np.concatenate([self.archetypes.flatten(), self.symbolic_field.flatten(), [self.initiation_level]])
    
    def update_state(self, new_state):
        total_size = len(self.archetypes) + np.prod(self.symbolic_field.shape) + 1
        if len(new_state) == total_size:
            arch_size = len(self.archetypes)
            sym_size = np.prod(self.symbolic_field.shape)
            self.archetypes = new_state[:arch_size]
            self.symbolic_field = new_state[arch_size:arch_size+sym_size].reshape(self.symbolic_field.shape)
            self.initiation_level = new_state[-1]
    
    def calculate_coherence(self):
        return 1.0 - np.std(self.archetypes)

class SocialSubsystem:
    def __init__(self):
        self.connection_matrix = np.random.rand(8, 8)
        self.culture_vector = np.random.randn(4)
        self.collective_intention = 0.5
    
    def get_state(self):
        return np.concatenate([self.connection_matrix.flatten(), self.culture_vector.flatten(), [self.collective_intention]])
    
    def update_state(self, new_state):
        total_size = np.prod(self.connection_matrix.shape) + len(self.culture_vector) + 1
        if len(new_state) == total_size:
            conn_size = np.prod(self.connection_matrix.shape)
            cult_size = len(self.culture_vector)
            self.connection_matrix = new_state[:conn_size].reshape(self.connection_matrix.shape)
            self.culture_vector = new_state[conn_size:conn_size+cult_size]
            self.collective_intention = new_state[-1]
    
    def calculate_coherence(self):
        return np.mean(self.connection_matrix)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    system, results = run_unified_demo(steps=100)
    plt.show()