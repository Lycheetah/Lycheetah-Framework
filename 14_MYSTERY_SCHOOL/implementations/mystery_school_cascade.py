"""
SOVEREIGN MYSTERY SCHOOL - PYRAMID CASCADE SYSTEM
==================================================

A world-class implementation integrating:
- LAMAGUE symbolic grammar
- Pyramid Cascade knowledge architecture  
- Seven-Phase awareness engine
- AURA constitutional ethics

This system provides:
1. Knowledge block validation and organization
2. Curriculum progression based on evidence
3. Practice efficacy measurement
4. Ethical alignment monitoring
5. Student transformation tracking

Author: Integrating work by Mackenzie Clark (AURA/LAMAGUE)
License: Sovereign - Open for educational use
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import json
import math


# ============================================================================
# LAMAGUE SYMBOLIC OPERATORS
# ============================================================================

class LAMAGUEOperator(Enum):
    """Core symbolic operators from LAMAGUE grammar"""
    AO = "Ao"           # Anchor/Ground - stable baseline
    PHI_UP = "Φ↑"       # Ascent/Activation - growth vector
    PSI = "Ψ"           # Fold/Return - correction curve
    NABLA_CAS = "∇cas"  # Cascade - transformational reorganization
    OMEGA_HEAL = "Ωheal" # Healed whole - integration completion
    NULL = "∅"          # Void/Zero-point - potential space
    TENSOR = "⊗"        # Fusion/Union - combining operations
    Z = "Z"             # Compression - condensing complexity


# ============================================================================
# SEVEN-PHASE AWARENESS ENGINE
# ============================================================================

class AwarenessPhase(Enum):
    """Seven phases of consciousness transformation"""
    CENTER = ("⟟", 0, "Establish presence, ground in reality")
    FLOW = ("≋", 1, "Regulate movement, find rhythm")
    INSIGHT = ("Ψ", 2, "Perceive truth, gain clarity")
    RISE = ("Φ↑", 3, "Activate will, take directed action")
    LIGHT = ("✧", 4, "Illuminate understanding, share wisdom")
    INTEGRITY = ("|◁▷|", 5, "Enforce boundaries, maintain alignment")
    SYNTHESIS = ("⟲", 6, "Reintegrate and evolve, complete cycle")
    
    def __init__(self, symbol: str, index: int, meaning: str):
        self.symbol = symbol
        self.index = index
        self.meaning = meaning


# ============================================================================
# PYRAMID CASCADE LAYERS
# ============================================================================

class PyramidLayer(Enum):
    """Three-tier knowledge validation system"""
    EDGE = "Edge"           # Experimental, high entropy, unvalidated
    MIDDLE = "Middle"       # Tested, moderate evidence, useful
    FOUNDATION = "Foundation"  # Proven, heavy truth, reliable


# ============================================================================
# AURA CONSTITUTIONAL METRICS
# ============================================================================

@dataclass
class AURAMetrics:
    """Tri-Axial ethical alignment scores"""
    TES: float  # Trust Entropy Score (stability) - target > 0.70
    VTR: float  # Value-Transfer Ratio (generativity) - target > 1.5
    PAI: float  # Purpose Alignment Index (direction) - target > 0.80
    
    def is_aligned(self) -> bool:
        """Check if all metrics meet AURA Prime thresholds"""
        return self.TES > 0.70 and self.VTR > 1.5 and self.PAI > 0.80
    
    def alignment_score(self) -> float:
        """Composite alignment measure (0-1 scale)"""
        tes_norm = min(self.TES / 0.70, 1.0)
        vtr_norm = min(self.VTR / 1.5, 1.0)
        pai_norm = min(self.PAI / 0.80, 1.0)
        return (tes_norm + vtr_norm + pai_norm) / 3.0


# ============================================================================
# KNOWLEDGE BLOCK (Pyramid Unit)
# ============================================================================

@dataclass
class KnowledgeBlock:
    """
    A discrete unit of knowledge in the Mystery School curriculum.
    
    Attributes:
        name: Practice or teaching name
        domain: Subject area (e.g., "Alchemy", "Tarot", "Meditation")
        evidence: Measured efficacy data (studies, outcomes)
        power: Transformative impact potential
        entropy: Noise/uncertainty in the knowledge
        layer: Current validation tier
        prerequisites: Required prior knowledge
        aura_metrics: Ethical alignment scores
    """
    name: str
    domain: str
    evidence: float  # 0.0 to 1.0
    power: float     # 0.0 to 1.0
    entropy: float   # 0.0 to 1.0 (lower is better)
    layer: PyramidLayer
    prerequisites: List[str] = field(default_factory=list)
    aura_metrics: Optional[AURAMetrics] = None
    phase_affinity: Optional[AwarenessPhase] = None
    
    @property
    def compression_score(self) -> float:
        """
        Π = (Evidence × Power) / Entropy
        
        The "weight" of this knowledge block.
        Higher scores indicate heavier, more fundamental truths.
        """
        if self.entropy == 0:
            return float('inf')
        return (self.evidence * self.power) / self.entropy
    
    @property
    def truth_pressure(self) -> float:
        """Alias for compression_score using document terminology"""
        return self.compression_score
    
    def can_cascade(self, foundation_threshold: float = 1.5) -> bool:
        """
        Determines if this block has sufficient weight to trigger
        a cascade (paradigm shift) in the pyramid.
        """
        return self.compression_score > foundation_threshold


# ============================================================================
# MYSTERY SCHOOL CURRICULUM DATABASE
# ============================================================================

class MysterySchoolCurriculum:
    """
    Central registry of all practices, teachings, and knowledge blocks
    in the Sovereign Mystery School system.
    """
    
    def __init__(self):
        self.blocks: Dict[str, KnowledgeBlock] = {}
        self._initialize_curriculum()
    
    def _initialize_curriculum(self):
        """Load initial curriculum from the comprehensive syllabus"""
        
        # FOUNDATION LAYER - Proven Practices
        self.add_block(KnowledgeBlock(
            name="Shamatha (Calm Abiding)",
            domain="Meditation",
            evidence=0.95,  # 2500+ years documentation, brain changes
            power=0.85,     # Transferable focus skill
            entropy=0.15,   # Well-understood
            layer=PyramidLayer.FOUNDATION,
            aura_metrics=AURAMetrics(TES=0.92, VTR=1.7, PAI=0.95),
            phase_affinity=AwarenessPhase.CENTER
        ))
        
        self.add_block(KnowledgeBlock(
            name="Vipassana (Insight Meditation)",
            domain="Meditation",
            evidence=0.90,
            power=0.90,
            entropy=0.12,
            layer=PyramidLayer.FOUNDATION,
            prerequisites=["Shamatha (Calm Abiding)"],
            aura_metrics=AURAMetrics(TES=0.95, VTR=1.8, PAI=0.92),
            phase_affinity=AwarenessPhase.INSIGHT
        ))
        
        self.add_block(KnowledgeBlock(
            name="Craniosacral Therapy",
            domain="Energy Healing",
            evidence=0.80,  # Strong evidence for migraines, TMJ
            power=0.70,
            entropy=0.20,
            layer=PyramidLayer.FOUNDATION,
            aura_metrics=AURAMetrics(TES=0.85, VTR=1.6, PAI=0.88),
            phase_affinity=AwarenessPhase.FLOW
        ))
        
        self.add_block(KnowledgeBlock(
            name="Consent & Boundaries Training",
            domain="Sacred Sexuality",
            evidence=0.88,
            power=0.95,  # Critical foundation for all intimacy work
            entropy=0.10,
            layer=PyramidLayer.FOUNDATION,
            aura_metrics=AURAMetrics(TES=0.98, VTR=2.0, PAI=0.99),
            phase_affinity=AwarenessPhase.INTEGRITY
        ))
        
        self.add_block(KnowledgeBlock(
            name="Vision Quest (Modern Protocol)",
            domain="Shamanic Arts",
            evidence=0.82,
            power=0.88,
            entropy=0.18,
            layer=PyramidLayer.FOUNDATION,
            prerequisites=["Wilderness First Aid", "Solo Camping Practice"],
            aura_metrics=AURAMetrics(TES=0.87, VTR=1.5, PAI=0.93),
            phase_affinity=AwarenessPhase.SYNTHESIS
        ))
        
        # MIDDLE LAYER - Validated but Moderate Evidence
        self.add_block(KnowledgeBlock(
            name="Reiki Level 1-3",
            domain="Energy Healing",
            evidence=0.65,
            power=0.70,
            entropy=0.35,
            layer=PyramidLayer.MIDDLE,
            aura_metrics=AURAMetrics(TES=0.75, VTR=1.2, PAI=0.82),
            phase_affinity=AwarenessPhase.LIGHT
        ))
        
        self.add_block(KnowledgeBlock(
            name="Tarot Major Arcana Journey",
            domain="Divination",
            evidence=0.60,  # Psychological benefits documented
            power=0.75,
            entropy=0.40,
            layer=PyramidLayer.MIDDLE,
            aura_metrics=AURAMetrics(TES=0.73, VTR=1.3, PAI=0.85),
            phase_affinity=AwarenessPhase.INSIGHT
        ))
        
        self.add_block(KnowledgeBlock(
            name="Lucid Dreaming (MILD/WILD)",
            domain="Consciousness Tech",
            evidence=0.70,
            power=0.65,
            entropy=0.30,
            layer=PyramidLayer.MIDDLE,
            aura_metrics=AURAMetrics(TES=0.77, VTR=1.4, PAI=0.80),
            phase_affinity=AwarenessPhase.RISE
        ))
        
        # EDGE LAYER - Experimental, High Entropy
        self.add_block(KnowledgeBlock(
            name="Ayahuasca Ceremony",
            domain="Plant Medicine",
            evidence=0.45,  # Some studies, high variability
            power=0.90,     # Potentially transformative
            entropy=0.70,   # High risk, complex factors
            layer=PyramidLayer.EDGE,
            prerequisites=[
                "Psychiatric Evaluation",
                "Integration Therapist Secured",
                "Stable Life Situation"
            ],
            aura_metrics=AURAMetrics(TES=0.65, VTR=1.1, PAI=0.75),
            phase_affinity=AwarenessPhase.INSIGHT
        ))
        
        self.add_block(KnowledgeBlock(
            name="Sigil Magic (Chaos)",
            domain="Ritual Arts",
            evidence=0.35,
            power=0.55,
            entropy=0.65,
            layer=PyramidLayer.EDGE,
            aura_metrics=AURAMetrics(TES=0.68, VTR=1.1, PAI=0.72),
            phase_affinity=AwarenessPhase.RISE
        ))
        
        self.add_block(KnowledgeBlock(
            name="Crystal Grid Engineering",
            domain="Energy Healing",
            evidence=0.20,  # Weak evidence
            power=0.30,
            entropy=0.80,
            layer=PyramidLayer.EDGE,
            aura_metrics=AURAMetrics(TES=0.55, VTR=0.8, PAI=0.60),
            phase_affinity=AwarenessPhase.CENTER
        ))
    
    def add_block(self, block: KnowledgeBlock):
        """Register a knowledge block in the curriculum"""
        self.blocks[block.name] = block
    
    def get_block(self, name: str) -> Optional[KnowledgeBlock]:
        """Retrieve a knowledge block by name"""
        return self.blocks.get(name)
    
    def get_blocks_by_layer(self, layer: PyramidLayer) -> List[KnowledgeBlock]:
        """Get all blocks at a specific validation tier"""
        return [b for b in self.blocks.values() if b.layer == layer]
    
    def get_blocks_by_domain(self, domain: str) -> List[KnowledgeBlock]:
        """Get all blocks in a subject area"""
        return [b for b in self.blocks.values() if b.domain == domain]
    
    def get_blocks_by_phase(self, phase: AwarenessPhase) -> List[KnowledgeBlock]:
        """Get blocks aligned with a specific awareness phase"""
        return [b for b in self.blocks.values() 
                if b.phase_affinity == phase]


# ============================================================================
# PYRAMID CASCADE ENGINE
# ============================================================================

class PyramidCascadeEngine:
    """
    Manages the dynamic reorganization of knowledge blocks
    based on evolving evidence and truth pressure.
    
    Implements the core Pyramid Cascade logic:
    - Blocks accumulate at layers based on validation
    - When Edge block achieves high compression score, it "pops up"
    - If popped block heavier than Foundation, cascade triggers
    - Entire pyramid reorganizes to new equilibrium
    """
    
    def __init__(self, curriculum: MysterySchoolCurriculum):
        self.curriculum = curriculum
        self.cascade_history: List[Dict] = []
        self.cascade_threshold = 1.5  # Minimum Π to trigger cascade
    
    def evaluate_block(self, block_name: str, 
                       new_evidence: float,
                       new_entropy: float) -> Dict:
        """
        Update a block's metrics and check if it should move layers.
        
        Returns:
            Dictionary with evaluation results and any layer changes
        """
        block = self.curriculum.get_block(block_name)
        if not block:
            return {"error": f"Block '{block_name}' not found"}
        
        old_score = block.compression_score
        old_layer = block.layer
        
        # Update metrics
        block.evidence = new_evidence
        block.entropy = new_entropy
        new_score = block.compression_score
        
        # Determine appropriate layer based on compression score
        if new_score < 0.5:
            target_layer = PyramidLayer.EDGE
        elif new_score < 1.2:
            target_layer = PyramidLayer.MIDDLE
        else:
            target_layer = PyramidLayer.FOUNDATION
        
        # Check for layer change
        layer_changed = (target_layer != old_layer)
        
        result = {
            "block": block_name,
            "old_compression": round(old_score, 3),
            "new_compression": round(new_score, 3),
            "old_layer": old_layer.value,
            "new_layer": target_layer.value,
            "layer_changed": layer_changed,
            "can_cascade": block.can_cascade(self.cascade_threshold)
        }
        
        if layer_changed:
            block.layer = target_layer
            result["cascade_triggered"] = self._check_cascade(block)
        
        return result
    
    def _check_cascade(self, promoted_block: KnowledgeBlock) -> bool:
        """
        Check if a promoted block triggers a cascade event.
        
        A cascade occurs when:
        1. A block reaches Foundation layer
        2. Its compression score exceeds current Foundation average
        3. This forces reorganization of the entire knowledge base
        """
        if promoted_block.layer != PyramidLayer.FOUNDATION:
            return False
        
        foundation_blocks = self.curriculum.get_blocks_by_layer(
            PyramidLayer.FOUNDATION
        )
        
        if len(foundation_blocks) <= 1:
            return False
        
        avg_foundation_score = np.mean([
            b.compression_score for b in foundation_blocks
        ])
        
        if promoted_block.compression_score > avg_foundation_score * 1.3:
            self._trigger_cascade(promoted_block)
            return True
        
        return False
    
    def _trigger_cascade(self, catalyst_block: KnowledgeBlock):
        """
        Execute a cascade event - paradigm shift in knowledge organization.
        
        This represents a fundamental reorganization where:
        - New truth is heavier than current foundation
        - Old foundation blocks may compress up to Middle layer
        - System seeks new equilibrium
        """
        cascade_event = {
            "timestamp": datetime.now().isoformat(),
            "catalyst": catalyst_block.name,
            "catalyst_score": catalyst_block.compression_score,
            "reorganizations": []
        }
        
        # Get all blocks and sort by compression score
        all_blocks = list(self.curriculum.blocks.values())
        sorted_blocks = sorted(
            all_blocks, 
            key=lambda b: b.compression_score, 
            reverse=True
        )
        
        # Redistribute across layers based on new ordering
        total = len(sorted_blocks)
        foundation_cutoff = int(total * 0.25)  # Top 25%
        middle_cutoff = int(total * 0.65)      # Next 40%
        
        for i, block in enumerate(sorted_blocks):
            old_layer = block.layer
            
            if i < foundation_cutoff:
                new_layer = PyramidLayer.FOUNDATION
            elif i < middle_cutoff:
                new_layer = PyramidLayer.MIDDLE
            else:
                new_layer = PyramidLayer.EDGE
            
            if old_layer != new_layer:
                block.layer = new_layer
                cascade_event["reorganizations"].append({
                    "block": block.name,
                    "old_layer": old_layer.value,
                    "new_layer": new_layer.value,
                    "compression": round(block.compression_score, 3)
                })
        
        self.cascade_history.append(cascade_event)
        print(f"\n🌊 CASCADE EVENT TRIGGERED 🌊")
        print(f"Catalyst: {catalyst_block.name}")
        print(f"Reorganized: {len(cascade_event['reorganizations'])} blocks")
    
    def get_cascade_history(self) -> List[Dict]:
        """Return history of all cascade events"""
        return self.cascade_history


# ============================================================================
# STUDENT TRANSFORMATION TRACKER
# ============================================================================

@dataclass
class StudentProgress:
    """
    Track an individual student's journey through the Mystery School.
    
    Integrates:
    - Seven-phase awareness state
    - Completed knowledge blocks
    - AURA metric evolution
    - Transformation milestones
    """
    student_id: str
    current_phase: AwarenessPhase
    phase_entry_date: datetime
    completed_blocks: List[str] = field(default_factory=list)
    current_blocks: List[str] = field(default_factory=list)
    aura_history: List[Tuple[datetime, AURAMetrics]] = field(default_factory=list)
    transformation_log: List[Dict] = field(default_factory=list)
    
    def advance_phase(self):
        """Move to next phase in the seven-cycle"""
        phases = list(AwarenessPhase)
        current_index = phases.index(self.current_phase)
        next_index = (current_index + 1) % len(phases)
        
        self.transformation_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "phase_advancement",
            "from_phase": self.current_phase.symbol,
            "to_phase": phases[next_index].symbol,
            "days_in_phase": (datetime.now() - self.phase_entry_date).days
        })
        
        self.current_phase = phases[next_index]
        self.phase_entry_date = datetime.now()
    
    def complete_block(self, block_name: str, 
                       outcome_metrics: Optional[AURAMetrics] = None):
        """Mark a knowledge block as completed"""
        if block_name in self.current_blocks:
            self.current_blocks.remove(block_name)
        
        self.completed_blocks.append(block_name)
        
        if outcome_metrics:
            self.aura_history.append((datetime.now(), outcome_metrics))
        
        self.transformation_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "block_completion",
            "block": block_name,
            "phase": self.current_phase.symbol
        })
    
    @property
    def current_aura_metrics(self) -> Optional[AURAMetrics]:
        """Get most recent AURA scores"""
        if not self.aura_history:
            return None
        return self.aura_history[-1][1]
    
    @property
    def days_in_current_phase(self) -> int:
        """Days since entering current awareness phase"""
        return (datetime.now() - self.phase_entry_date).days
    
    def recommend_next_blocks(self, 
                             curriculum: MysterySchoolCurriculum,
                             max_recommendations: int = 5) -> List[KnowledgeBlock]:
        """
        Intelligent recommendation of next practices based on:
        - Current awareness phase alignment
        - Prerequisite completion
        - AURA metric gaps
        - Layer appropriateness
        """
        recommendations = []
        
        # Get blocks aligned with current phase
        phase_aligned = curriculum.get_blocks_by_phase(self.current_phase)
        
        for block in phase_aligned:
            # Skip if already completed or in progress
            if (block.name in self.completed_blocks or 
                block.name in self.current_blocks):
                continue
            
            # Check prerequisites
            prereqs_met = all(
                prereq in self.completed_blocks 
                for prereq in block.prerequisites
            )
            
            if not prereqs_met:
                continue
            
            # Prefer Foundation and Middle layer for safety
            if block.layer in [PyramidLayer.FOUNDATION, PyramidLayer.MIDDLE]:
                recommendations.append(block)
        
        # Sort by compression score (prioritize heavier truths)
        recommendations.sort(key=lambda b: b.compression_score, reverse=True)
        
        return recommendations[:max_recommendations]


# ============================================================================
# MYSTERY SCHOOL ORCHESTRATOR
# ============================================================================

class SovereignMysterySchool:
    """
    Main orchestration class integrating all systems:
    - Curriculum management
    - Pyramid cascade dynamics
    - Student progression
    - Seven-phase awareness tracking
    - AURA constitutional ethics
    """
    
    def __init__(self):
        self.curriculum = MysterySchoolCurriculum()
        self.cascade_engine = PyramidCascadeEngine(self.curriculum)
        self.students: Dict[str, StudentProgress] = {}
        self.founding_date = datetime.now()
    
    def enroll_student(self, student_id: str, 
                       starting_phase: AwarenessPhase = AwarenessPhase.CENTER) -> StudentProgress:
        """Register a new student in the Mystery School"""
        if student_id in self.students:
            raise ValueError(f"Student {student_id} already enrolled")
        
        student = StudentProgress(
            student_id=student_id,
            current_phase=starting_phase,
            phase_entry_date=datetime.now()
        )
        
        self.students[student_id] = student
        return student
    
    def get_student(self, student_id: str) -> Optional[StudentProgress]:
        """Retrieve student progress record"""
        return self.students.get(student_id)
    
    def update_practice_evidence(self, practice_name: str,
                                 new_evidence: float,
                                 new_entropy: float) -> Dict:
        """
        Update evidence for a practice and trigger cascade if appropriate.
        
        This is how the Mystery School evolves - as research accumulates,
        practices move between layers, and paradigms shift.
        """
        result = self.cascade_engine.evaluate_block(
            practice_name, new_evidence, new_entropy
        )
        return result
    
    def generate_curriculum_report(self) -> Dict:
        """Generate comprehensive state of the knowledge pyramid"""
        foundation = self.curriculum.get_blocks_by_layer(PyramidLayer.FOUNDATION)
        middle = self.curriculum.get_blocks_by_layer(PyramidLayer.MIDDLE)
        edge = self.curriculum.get_blocks_by_layer(PyramidLayer.EDGE)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_practices": len(self.curriculum.blocks),
            "layers": {
                "Foundation": {
                    "count": len(foundation),
                    "avg_compression": np.mean([b.compression_score for b in foundation]),
                    "practices": [b.name for b in foundation]
                },
                "Middle": {
                    "count": len(middle),
                    "avg_compression": np.mean([b.compression_score for b in middle]) if middle else 0,
                    "practices": [b.name for b in middle]
                },
                "Edge": {
                    "count": len(edge),
                    "avg_compression": np.mean([b.compression_score for b in edge]) if edge else 0,
                    "practices": [b.name for b in edge]
                }
            },
            "cascade_events": len(self.cascade_engine.cascade_history),
            "total_students": len(self.students)
        }
        
        return report
    
    def generate_student_report(self, student_id: str) -> Dict:
        """Generate detailed progress report for a student"""
        student = self.get_student(student_id)
        if not student:
            return {"error": f"Student {student_id} not found"}
        
        current_metrics = student.current_aura_metrics
        
        report = {
            "student_id": student_id,
            "current_phase": {
                "symbol": student.current_phase.symbol,
                "name": student.current_phase.name,
                "days_in_phase": student.days_in_current_phase,
                "meaning": student.current_phase.meaning
            },
            "progress": {
                "completed_blocks": len(student.completed_blocks),
                "in_progress": len(student.current_blocks),
                "completed_list": student.completed_blocks
            },
            "aura_metrics": {
                "TES": round(current_metrics.TES, 3) if current_metrics else None,
                "VTR": round(current_metrics.VTR, 3) if current_metrics else None,
                "PAI": round(current_metrics.PAI, 3) if current_metrics else None,
                "aligned": current_metrics.is_aligned() if current_metrics else None
            },
            "recommendations": [
                {
                    "name": block.name,
                    "domain": block.domain,
                    "layer": block.layer.value,
                    "compression_score": round(block.compression_score, 3)
                }
                for block in student.recommend_next_blocks(self.curriculum)
            ],
            "transformation_events": len(student.transformation_log)
        }
        
        return report


# ============================================================================
# DEMONSTRATION & TESTING
# ============================================================================

def demonstrate_system():
    """
    Comprehensive demonstration of the Sovereign Mystery School system.
    """
    print("=" * 80)
    print("SOVEREIGN MYSTERY SCHOOL - PYRAMID CASCADE SYSTEM")
    print("=" * 80)
    print()
    
    # Initialize school
    school = SovereignMysterySchool()
    
    # Show initial curriculum state
    print("📚 INITIAL CURRICULUM STATE")
    print("-" * 80)
    report = school.generate_curriculum_report()
    print(f"Total Practices: {report['total_practices']}")
    print(f"\nFoundation Layer ({report['layers']['Foundation']['count']} practices):")
    print(f"  Avg Compression Score: {report['layers']['Foundation']['avg_compression']:.3f}")
    for practice in report['layers']['Foundation']['practices']:
        block = school.curriculum.get_block(practice)
        print(f"  • {practice} (Π={block.compression_score:.3f})")
    
    print(f"\nMiddle Layer ({report['layers']['Middle']['count']} practices):")
    for practice in report['layers']['Middle']['practices']:
        block = school.curriculum.get_block(practice)
        print(f"  • {practice} (Π={block.compression_score:.3f})")
    
    print(f"\nEdge Layer ({report['layers']['Edge']['count']} practices):")
    for practice in report['layers']['Edge']['practices']:
        block = school.curriculum.get_block(practice)
        print(f"  • {practice} (Π={block.compression_score:.3f})")
    
    # Enroll a student
    print("\n" + "=" * 80)
    print("👤 STUDENT ENROLLMENT")
    print("-" * 80)
    student = school.enroll_student("alice_2025", AwarenessPhase.CENTER)
    print(f"Enrolled: {student.student_id}")
    print(f"Starting Phase: {student.current_phase.symbol} ({student.current_phase.name})")
    print(f"Meaning: {student.current_phase.meaning}")
    
    # Get recommendations
    print("\n📋 RECOMMENDED PRACTICES FOR CURRENT PHASE")
    print("-" * 80)
    recommendations = student.recommend_next_blocks(school.curriculum)
    for i, block in enumerate(recommendations, 1):
        print(f"{i}. {block.name}")
        print(f"   Domain: {block.domain} | Layer: {block.layer.value}")
        print(f"   Truth Pressure (Π): {block.compression_score:.3f}")
        print(f"   Phase Affinity: {block.phase_affinity.symbol if block.phase_affinity else 'N/A'}")
    
    # Student completes a practice
    print("\n" + "=" * 80)
    print("✅ STUDENT COMPLETES PRACTICE")
    print("-" * 80)
    practice_name = "Shamatha (Calm Abiding)"
    print(f"Completing: {practice_name}")
    student.complete_block(
        practice_name,
        AURAMetrics(TES=0.85, VTR=1.6, PAI=0.90)
    )
    print("Practice completed with strong AURA metrics!")
    
    # Simulate research update that triggers cascade
    print("\n" + "=" * 80)
    print("🔬 RESEARCH UPDATE - NEW EVIDENCE EMERGES")
    print("-" * 80)
    print("Simulating: Major breakthrough study on Lucid Dreaming...")
    print("New evidence significantly increases compression score...")
    
    result = school.update_practice_evidence(
        "Lucid Dreaming (MILD/WILD)",
        new_evidence=0.92,  # Dramatic improvement
        new_entropy=0.10    # Much clearer understanding
    )
    
    print(f"\nEvaluation Results:")
    print(f"  Old Compression: {result['old_compression']}")
    print(f"  New Compression: {result['new_compression']}")
    print(f"  Old Layer: {result['old_layer']}")
    print(f"  New Layer: {result['new_layer']}")
    print(f"  Layer Changed: {result['layer_changed']}")
    
    if result.get('cascade_triggered'):
        print("\n  ⚡ CASCADE EVENT TRIGGERED! ⚡")
        print("  The pyramid is reorganizing based on new heavy truth...")
    
    # Show updated curriculum
    print("\n" + "=" * 80)
    print("📚 UPDATED CURRICULUM STATE")
    print("-" * 80)
    report = school.generate_curriculum_report()
    print(f"Cascade Events: {report['cascade_events']}")
    print(f"\nFoundation Layer: {report['layers']['Foundation']['count']} practices")
    for practice in report['layers']['Foundation']['practices']:
        block = school.curriculum.get_block(practice)
        print(f"  • {practice} (Π={block.compression_score:.3f})")
    
    # Generate student progress report
    print("\n" + "=" * 80)
    print("📊 STUDENT PROGRESS REPORT")
    print("-" * 80)
    student_report = school.generate_student_report("alice_2025")
    print(json.dumps(student_report, indent=2))
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_system()
