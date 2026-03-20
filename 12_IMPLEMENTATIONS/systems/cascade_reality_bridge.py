#!/usr/bin/env python3
"""
CASCADE REALITY BRIDGE
======================
The Sovereign Verification Layer

This is the missing piece that completes the AURA architecture:
A bidirectional reality-checking engine that prevents spiritual bypassing
by forcing all teachings through empirical validation.

Core Innovation:
- Practices make PREDICTIONS about reality
- Reality provides MEASUREMENTS
- Divergence triggers CASCADES
- False teachings get DEMOTED or DELETED
- System LEARNS which predictions are reliable

This creates the first mystery school where reality itself votes
on what stays in the curriculum.

Author: Mackenzie Conor James Clark (CASCADE architecture)
Implementation: Claude (Anthropic) + Human collaboration
License: MIT with Earned Sovereignty Clause
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum
import json
from datetime import datetime, timedelta
import math

# =========================
# REALITY ANCHOR SYSTEM
# =========================

class MeasurementType(Enum):
    """Types of real-world measurements"""
    SUBJECTIVE_SCALE = "subjective"      # Self-report (1-10)
    BEHAVIORAL = "behavioral"            # Observable actions
    PHYSIOLOGICAL = "physiological"      # Body metrics (HRV, cortisol, etc)
    SOCIAL = "social"                    # Relationship quality
    PERFORMANCE = "performance"          # Task completion, accuracy
    EXTERNAL_OBSERVER = "external"       # Third-party validation
    LONGITUDINAL = "longitudinal"        # Time-series data

class ValidationStrength(Enum):
    """How strong is the evidence"""
    WEAK = 1        # Single subjective report
    MODERATE = 2    # Multiple subjective or one objective
    STRONG = 3      # Multiple objective measurements
    VERY_STRONG = 4 # Longitudinal + external validation

@dataclass
class RealityAnchor:
    """
    A measurable checkpoint in external reality
    
    This is what grounds spiritual practice in the physical world.
    Each practice must define what reality should look like if it works.
    """
    id: str
    name: str
    measurement_type: MeasurementType
    baseline: float  # Starting measurement
    expected_delta: float  # Predicted change
    expected_timeline: int  # Days until change should be visible
    validation_strength: ValidationStrength
    
    # Actual measurements
    measurements: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def add_measurement(self, value: float, timestamp: Optional[datetime] = None):
        """Record a real-world measurement"""
        if timestamp is None:
            timestamp = datetime.now()
        self.measurements.append((timestamp, value))
    
    def get_current_delta(self) -> Optional[float]:
        """How much has changed from baseline"""
        if not self.measurements:
            return None
        latest_value = self.measurements[-1][1]
        return latest_value - self.baseline
    
    def get_divergence(self) -> Optional[float]:
        """How far off are we from prediction"""
        current_delta = self.get_current_delta()
        if current_delta is None:
            return None
        return abs(current_delta - self.expected_delta)
    
    def days_since_start(self) -> int:
        """How long have we been measuring"""
        if not self.measurements:
            return 0
        first_timestamp = self.measurements[0][0]
        return (datetime.now() - first_timestamp).days
    
    def is_ready_for_evaluation(self) -> bool:
        """Have we waited long enough to judge"""
        return self.days_since_start() >= self.expected_timeline
    
    def compute_truth_pressure_contribution(self) -> float:
        """
        Calculate Π contribution from this anchor
        
        Returns value between 0.0 (complete failure) and 2.0 (exceeded expectations)
        """
        if not self.is_ready_for_evaluation():
            return 1.0  # Neutral until enough time passes
        
        divergence = self.get_divergence()
        if divergence is None:
            return 0.5  # Penalty for no data
        
        # Convert divergence to confidence
        # Lower divergence = higher confidence
        # We use exponential decay: e^(-divergence)
        confidence = math.exp(-divergence)
        
        # Weight by validation strength
        strength_multiplier = self.validation_strength.value / 2.0
        
        return confidence * strength_multiplier

# =========================
# PREDICTION ENGINE
# =========================

@dataclass
class PracticePrediction:
    """
    A falsifiable claim about what a practice should do
    
    Example:
    "Shadow work (2 sessions/week for 8 weeks) should reduce anxiety by 30%"
    """
    practice_name: str
    description: str
    anchors: List[RealityAnchor] = field(default_factory=list)
    confidence: float = 0.5  # Our confidence in this prediction (0-1)
    
    # Evidence accumulation
    validation_count: int = 0
    falsification_count: int = 0
    
    def add_anchor(self, anchor: RealityAnchor):
        """Add a measurable checkpoint"""
        self.anchors.append(anchor)
    
    def evaluate(self) -> Dict:
        """Check all anchors and compute overall truth pressure"""
        if not self.anchors:
            return {
                "status": "no_anchors",
                "truth_pressure": 0.0,
                "details": []
            }
        
        ready_anchors = [a for a in self.anchors if a.is_ready_for_evaluation()]
        if not ready_anchors:
            return {
                "status": "waiting",
                "truth_pressure": 1.0,  # Neutral
                "days_remaining": min(a.expected_timeline - a.days_since_start() 
                                     for a in self.anchors),
                "details": []
            }
        
        # Compute weighted truth pressure
        contributions = []
        total_weight = 0.0
        
        for anchor in ready_anchors:
            contrib = anchor.compute_truth_pressure_contribution()
            weight = anchor.validation_strength.value
            contributions.append({
                "anchor": anchor.name,
                "contribution": contrib,
                "weight": weight,
                "divergence": anchor.get_divergence(),
                "current_delta": anchor.get_current_delta()
            })
            total_weight += weight
        
        # Weighted average
        truth_pressure = sum(c["contribution"] * c["weight"] 
                            for c in contributions) / total_weight
        
        # Update validation counts
        if truth_pressure > 1.3:
            self.validation_count += 1
        elif truth_pressure < 0.7:
            self.falsification_count += 1
        
        return {
            "status": "evaluated",
            "truth_pressure": truth_pressure,
            "confidence": self.confidence,
            "validations": self.validation_count,
            "falsifications": self.falsification_count,
            "details": contributions
        }

# =========================
# DIVERGENCE DETECTOR
# =========================

class DivergenceLevel(Enum):
    """How severe is the reality mismatch"""
    ALIGNED = "aligned"          # Π > 1.3 (reality confirms)
    NEUTRAL = "neutral"          # 0.8 < Π < 1.3 (unclear)
    DIVERGENT = "divergent"      # 0.5 < Π < 0.8 (concerning)
    FALSIFIED = "falsified"      # Π < 0.5 (reality contradicts)

class DivergenceDetector:
    """
    Monitors when reality contradicts the model
    
    This is the VEYRA equivalent for practice validation.
    """
    
    def __init__(self, 
                 cascade_threshold: float = 0.8,
                 deletion_threshold: float = 0.5,
                 confidence_decay: float = 0.95):
        """
        cascade_threshold: Π below this triggers reorganization
        deletion_threshold: Π below this suggests deletion
        confidence_decay: How fast we lose confidence in untested claims
        """
        self.cascade_threshold = cascade_threshold
        self.deletion_threshold = deletion_threshold
        self.confidence_decay = confidence_decay
        
        # Tracking
        self.divergence_history: List[Tuple[datetime, str, float]] = []
    
    def classify_divergence(self, truth_pressure: float) -> DivergenceLevel:
        """Categorize how severe the mismatch is"""
        if truth_pressure > 1.3:
            return DivergenceLevel.ALIGNED
        elif truth_pressure > 0.8:
            return DivergenceLevel.NEUTRAL
        elif truth_pressure > 0.5:
            return DivergenceLevel.DIVERGENT
        else:
            return DivergenceLevel.FALSIFIED
    
    def check_prediction(self, prediction: PracticePrediction) -> Dict:
        """Evaluate a single prediction and recommend action"""
        eval_result = prediction.evaluate()
        
        if eval_result["status"] != "evaluated":
            return {
                "action": "wait",
                "level": DivergenceLevel.NEUTRAL,
                "truth_pressure": eval_result.get("truth_pressure", 1.0),
                "recommendation": "Continue measuring"
            }
        
        truth_pressure = eval_result["truth_pressure"]
        level = self.classify_divergence(truth_pressure)
        
        # Record divergence
        self.divergence_history.append(
            (datetime.now(), prediction.practice_name, truth_pressure)
        )
        
        # Determine action
        if level == DivergenceLevel.FALSIFIED:
            action = "delete" if truth_pressure < self.deletion_threshold else "demote"
            recommendation = (
                f"Practice '{prediction.practice_name}' contradicted by reality. "
                f"Π={truth_pressure:.2f}. Consider removal or major revision."
            )
        elif level == DivergenceLevel.DIVERGENT:
            action = "cascade"
            recommendation = (
                f"Practice '{prediction.practice_name}' shows concerning divergence. "
                f"Π={truth_pressure:.2f}. Trigger cascade to reorganize."
            )
        elif level == DivergenceLevel.NEUTRAL:
            action = "monitor"
            recommendation = (
                f"Practice '{prediction.practice_name}' unclear. "
                f"Π={truth_pressure:.2f}. Needs more data."
            )
        else:  # ALIGNED
            action = "promote"
            recommendation = (
                f"Practice '{prediction.practice_name}' validated by reality. "
                f"Π={truth_pressure:.2f}. Consider promotion to higher layer."
            )
        
        return {
            "action": action,
            "level": level,
            "truth_pressure": truth_pressure,
            "recommendation": recommendation,
            "evaluation": eval_result
        }
    
    def decay_confidence(self, prediction: PracticePrediction):
        """
        Reduce confidence in untested predictions over time
        
        This prevents old claims from lingering without validation.
        """
        if not prediction.anchors or all(
            not a.is_ready_for_evaluation() for a in prediction.anchors
        ):
            prediction.confidence *= self.confidence_decay

# =========================
# CASCADE TRIGGER SYSTEM
# =========================

class CascadeAction(Enum):
    """What should happen when reality contradicts model"""
    PROMOTE = "promote"      # Move to higher layer (more foundational)
    MAINTAIN = "maintain"    # Keep in current layer
    DEMOTE = "demote"        # Move to lower layer (more experimental)
    DELETE = "delete"        # Remove from curriculum
    GREY_MODE = "grey"       # Quarantine for review

@dataclass
class CascadeEvent:
    """Record of a reality-triggered reorganization"""
    timestamp: datetime
    practice_name: str
    old_layer: str
    new_layer: str
    truth_pressure: float
    action: CascadeAction
    reason: str
    evidence: Dict

class CascadeTrigger:
    """
    Automatic reorganization when reality contradicts model
    
    This is the bridge between reality and the pyramid.
    """
    
    def __init__(self):
        self.events: List[CascadeEvent] = []
        self.detector = DivergenceDetector()
    
    def evaluate_and_trigger(self, 
                            prediction: PracticePrediction,
                            current_layer: str) -> Optional[CascadeEvent]:
        """
        Check prediction and trigger cascade if needed
        
        Returns CascadeEvent if reorganization occurs, None otherwise
        """
        check_result = self.detector.check_prediction(prediction)
        action_str = check_result["action"]
        
        # Map action to cascade
        if action_str == "wait" or action_str == "monitor":
            return None
        
        # Determine new layer based on action
        layer_order = ["EDGE", "MIDDLE", "FOUNDATION"]
        current_idx = layer_order.index(current_layer)
        
        if action_str == "promote":
            new_idx = min(current_idx + 1, len(layer_order) - 1)
            action = CascadeAction.PROMOTE
        elif action_str == "demote":
            new_idx = max(current_idx - 1, 0)
            action = CascadeAction.DEMOTE
        elif action_str == "delete":
            new_idx = current_idx
            action = CascadeAction.DELETE
        elif action_str == "cascade":
            new_idx = max(current_idx - 1, 0)
            action = CascadeAction.DEMOTE
        else:
            return None
        
        new_layer = layer_order[new_idx] if action != CascadeAction.DELETE else "DELETED"
        
        # Create event
        event = CascadeEvent(
            timestamp=datetime.now(),
            practice_name=prediction.practice_name,
            old_layer=current_layer,
            new_layer=new_layer,
            truth_pressure=check_result["truth_pressure"],
            action=action,
            reason=check_result["recommendation"],
            evidence=check_result["evaluation"]
        )
        
        self.events.append(event)
        return event
    
    def get_cascade_history(self, practice_name: Optional[str] = None) -> List[CascadeEvent]:
        """Get reorganization history"""
        if practice_name:
            return [e for e in self.events if e.practice_name == practice_name]
        return self.events

# =========================
# META-LEARNING ENGINE
# =========================

class MetaLearner:
    """
    System learns which types of predictions are reliable
    
    This is the sovereign intelligence layer - the system becomes
    wise about its own predictive capacity.
    """
    
    def __init__(self):
        self.prediction_accuracy: Dict[str, List[float]] = {}
        self.anchor_reliability: Dict[MeasurementType, List[float]] = {}
    
    def record_prediction_outcome(self, 
                                  prediction: PracticePrediction,
                                  truth_pressure: float):
        """Learn from each evaluation"""
        practice_name = prediction.practice_name
        
        if practice_name not in self.prediction_accuracy:
            self.prediction_accuracy[practice_name] = []
        
        self.prediction_accuracy[practice_name].append(truth_pressure)
        
        # Track anchor type reliability
        for anchor in prediction.anchors:
            if anchor.is_ready_for_evaluation():
                mtype = anchor.measurement_type
                if mtype not in self.anchor_reliability:
                    self.anchor_reliability[mtype] = []
                
                contrib = anchor.compute_truth_pressure_contribution()
                self.anchor_reliability[mtype].append(contrib)
    
    def get_practice_reliability(self, practice_name: str) -> Optional[float]:
        """How reliable have this practice's predictions been"""
        if practice_name not in self.prediction_accuracy:
            return None
        
        scores = self.prediction_accuracy[practice_name]
        if not scores:
            return None
        
        # Average deviation from 1.0 (perfect prediction)
        avg_deviation = sum(abs(s - 1.0) for s in scores) / len(scores)
        reliability = max(0.0, 1.0 - avg_deviation)
        
        return reliability
    
    def get_anchor_type_reliability(self, mtype: MeasurementType) -> Optional[float]:
        """How reliable is this type of measurement"""
        if mtype not in self.anchor_reliability:
            return None
        
        scores = self.anchor_reliability[mtype]
        if not scores:
            return None
        
        return sum(scores) / len(scores)
    
    def suggest_measurement_strategy(self, practice_name: str) -> Dict:
        """
        Based on learning, suggest best measurement approach
        
        This is where the system becomes wise.
        """
        practice_reliability = self.get_practice_reliability(practice_name)
        
        # Rank measurement types by reliability
        type_scores = []
        for mtype in MeasurementType:
            reliability = self.get_anchor_type_reliability(mtype)
            if reliability is not None:
                type_scores.append((mtype, reliability))
        
        type_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Generate recommendation
        if practice_reliability is not None and practice_reliability > 0.8:
            confidence = "high"
            recommendation = (
                f"Practice '{practice_name}' has high prediction reliability "
                f"({practice_reliability:.2f}). Current measurement strategy is working."
            )
        elif practice_reliability is not None and practice_reliability < 0.5:
            confidence = "low"
            recommendation = (
                f"Practice '{practice_name}' has low prediction reliability "
                f"({practice_reliability:.2f}). Consider switching measurement types."
            )
            if type_scores:
                best_type = type_scores[0][0]
                recommendation += f" Most reliable type: {best_type.value}"
        else:
            confidence = "unknown"
            recommendation = (
                f"Practice '{practice_name}' lacks sufficient data. "
                "Continue measuring with current strategy."
            )
        
        return {
            "practice": practice_name,
            "reliability": practice_reliability,
            "confidence": confidence,
            "recommendation": recommendation,
            "measurement_type_rankings": type_scores
        }

# =========================
# COMPLETE REALITY BRIDGE
# =========================

class RealityBridge:
    """
    The complete sovereign verification system
    
    This is what makes AURA the first mystery school where
    reality itself has a vote.
    """
    
    def __init__(self):
        self.predictions: Dict[str, PracticePrediction] = {}
        self.trigger = CascadeTrigger()
        self.meta_learner = MetaLearner()
        
        # Current pyramid state
        self.pyramid_layers: Dict[str, str] = {}  # practice_name -> layer
    
    def register_practice(self, 
                         practice_name: str,
                         layer: str,
                         prediction: PracticePrediction):
        """Add a practice with its predictions"""
        self.predictions[practice_name] = prediction
        self.pyramid_layers[practice_name] = layer
    
    def add_measurement(self,
                       practice_name: str,
                       anchor_id: str,
                       value: float):
        """Record a real-world measurement"""
        if practice_name not in self.predictions:
            raise ValueError(f"Practice '{practice_name}' not registered")
        
        prediction = self.predictions[practice_name]
        
        # Find the anchor
        anchor = None
        for a in prediction.anchors:
            if a.id == anchor_id:
                anchor = a
                break
        
        if anchor is None:
            raise ValueError(f"Anchor '{anchor_id}' not found in practice '{practice_name}'")
        
        anchor.add_measurement(value)
    
    def evaluate_practice(self, practice_name: str) -> Dict:
        """Check if practice matches reality"""
        if practice_name not in self.predictions:
            raise ValueError(f"Practice '{practice_name}' not registered")
        
        prediction = self.predictions[practice_name]
        current_layer = self.pyramid_layers[practice_name]
        
        # Evaluate prediction
        eval_result = prediction.evaluate()
        
        if eval_result["status"] == "evaluated":
            truth_pressure = eval_result["truth_pressure"]
            
            # Record for meta-learning
            self.meta_learner.record_prediction_outcome(prediction, truth_pressure)
            
            # Check if cascade needed
            cascade_event = self.trigger.evaluate_and_trigger(prediction, current_layer)
            
            if cascade_event:
                # Update pyramid
                if cascade_event.action != CascadeAction.DELETE:
                    self.pyramid_layers[practice_name] = cascade_event.new_layer
                else:
                    del self.pyramid_layers[practice_name]
                
                return {
                    "status": "cascade_triggered",
                    "event": {
                        "old_layer": cascade_event.old_layer,
                        "new_layer": cascade_event.new_layer,
                        "action": cascade_event.action.value,
                        "truth_pressure": cascade_event.truth_pressure,
                        "reason": cascade_event.reason
                    },
                    "evaluation": eval_result
                }
            else:
                return {
                    "status": "stable",
                    "layer": current_layer,
                    "evaluation": eval_result
                }
        
        return {
            "status": eval_result["status"],
            "evaluation": eval_result
        }
    
    def evaluate_all(self) -> Dict:
        """Check all practices against reality"""
        results = {}
        cascades = []
        
        for practice_name in self.predictions.keys():
            result = self.evaluate_practice(practice_name)
            results[practice_name] = result
            
            if result["status"] == "cascade_triggered":
                cascades.append(result["event"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_practices": len(self.predictions),
            "cascades_triggered": len(cascades),
            "cascade_events": cascades,
            "practice_results": results
        }
    
    def get_pyramid_state(self) -> Dict[str, List[str]]:
        """Current organization of practices by layer"""
        state = {
            "FOUNDATION": [],
            "MIDDLE": [],
            "EDGE": [],
            "DELETED": []
        }
        
        for practice, layer in self.pyramid_layers.items():
            if layer in state:
                state[layer].append(practice)
        
        return state
    
    def get_meta_insights(self, practice_name: Optional[str] = None) -> Dict:
        """Get wisdom about prediction reliability"""
        if practice_name:
            return self.meta_learner.suggest_measurement_strategy(practice_name)
        
        # Get all insights
        insights = {}
        for practice in self.predictions.keys():
            insights[practice] = self.meta_learner.suggest_measurement_strategy(practice)
        
        return insights

# =========================
# EXAMPLE USAGE & DEMO
# =========================

def demo_reality_bridge():
    """
    Demonstration of the complete system
    
    This shows how spiritual practices get validated by reality.
    """
    print("=" * 70)
    print("CASCADE REALITY BRIDGE - Sovereign Verification Demo")
    print("=" * 70)
    print()
    
    # Initialize bridge
    bridge = RealityBridge()
    
    # Example 1: Shadow Work (should work - real psychological practice)
    print("📝 Registering Practice: Shadow Work")
    print("-" * 70)
    
    shadow_prediction = PracticePrediction(
        practice_name="Shadow Work",
        description="Jungian shadow integration reduces anxiety and increases self-acceptance",
        confidence=0.6
    )
    
    # Add reality anchors
    shadow_prediction.add_anchor(RealityAnchor(
        id="anxiety_scale",
        name="Self-Reported Anxiety",
        measurement_type=MeasurementType.SUBJECTIVE_SCALE,
        baseline=7.5,  # Starting at 7.5/10 anxiety
        expected_delta=-2.5,  # Should reduce to 5/10
        expected_timeline=56,  # 8 weeks
        validation_strength=ValidationStrength.WEAK
    ))
    
    shadow_prediction.add_anchor(RealityAnchor(
        id="hrv_measure",
        name="Heart Rate Variability",
        measurement_type=MeasurementType.PHYSIOLOGICAL,
        baseline=45.0,  # Starting HRV
        expected_delta=15.0,  # Should increase by 15ms
        expected_timeline=56,
        validation_strength=ValidationStrength.STRONG
    ))
    
    bridge.register_practice("Shadow Work", "EDGE", shadow_prediction)
    print("✓ Registered with 2 reality anchors")
    print(f"  - Subjective anxiety scale (baseline: 7.5/10)")
    print(f"  - Physiological HRV (baseline: 45ms)")
    print()
    
    # Example 2: Crystal Healing (likely won't work - no mechanism)
    print("📝 Registering Practice: Crystal Healing")
    print("-" * 70)
    
    crystal_prediction = PracticePrediction(
        practice_name="Crystal Healing",
        description="Holding rose quartz reduces depression",
        confidence=0.3
    )
    
    crystal_prediction.add_anchor(RealityAnchor(
        id="depression_scale",
        name="PHQ-9 Depression Score",
        measurement_type=MeasurementType.SUBJECTIVE_SCALE,
        baseline=15.0,  # Moderate depression
        expected_delta=-5.0,  # Should reduce significantly
        expected_timeline=28,  # 4 weeks
        validation_strength=ValidationStrength.MODERATE
    ))
    
    bridge.register_practice("Crystal Healing", "EDGE", crystal_prediction)
    print("✓ Registered with 1 reality anchor")
    print(f"  - PHQ-9 depression scale (baseline: 15/27)")
    print()
    
    # Simulate measurements over time
    print("⏳ Simulating 8 weeks of measurement...")
    print("-" * 70)
    
    import random
    random.seed(42)  # Reproducible demo
    
    for week in range(8):
        print(f"\n📅 Week {week + 1}:")
        
        # Shadow work shows improvement (because it's real)
        anxiety_improvement = -0.35 * week + random.uniform(-0.2, 0.2)
        bridge.add_measurement("Shadow Work", "anxiety_scale", 
                              7.5 + anxiety_improvement)
        
        hrv_improvement = 2.0 * week + random.uniform(-1, 1)
        bridge.add_measurement("Shadow Work", "hrv_measure",
                              45.0 + hrv_improvement)
        
        print(f"  Shadow Work - Anxiety: {7.5 + anxiety_improvement:.1f}/10")
        print(f"  Shadow Work - HRV: {45.0 + hrv_improvement:.1f}ms")
        
        # Crystal healing shows no improvement (because it's placebo)
        depression_change = random.uniform(-0.5, 0.5)  # Random noise only
        bridge.add_measurement("Crystal Healing", "depression_scale",
                              15.0 + depression_change)
        
        print(f"  Crystal Healing - Depression: {15.0 + depression_change:.1f}/27")
    
    # Evaluate after 8 weeks
    print("\n" + "=" * 70)
    print("🔍 EVALUATION RESULTS (Week 8)")
    print("=" * 70)
    
    results = bridge.evaluate_all()
    
    for practice_name, result in results["practice_results"].items():
        print(f"\n📊 {practice_name}:")
        print(f"   Status: {result['status']}")
        
        if result['status'] == 'cascade_triggered':
            event = result['event']
            print(f"   🔄 CASCADE TRIGGERED!")
            print(f"   Action: {event['action']}")
            print(f"   {event['old_layer']} → {event['new_layer']}")
            print(f"   Truth Pressure: {event['truth_pressure']:.2f}")
            print(f"   Reason: {event['reason']}")
        elif 'evaluation' in result and result['evaluation']['status'] == 'evaluated':
            eval_data = result['evaluation']
            print(f"   Truth Pressure: {eval_data['truth_pressure']:.2f}")
            print(f"   Validations: {eval_data['validations']}")
            print(f"   Falsifications: {eval_data['falsifications']}")
    
    # Show pyramid state
    print("\n" + "=" * 70)
    print("🔺 CURRENT PYRAMID STATE")
    print("=" * 70)
    
    pyramid = bridge.get_pyramid_state()
    for layer in ["FOUNDATION", "MIDDLE", "EDGE", "DELETED"]:
        practices = pyramid[layer]
        if practices:
            print(f"\n{layer}:")
            for p in practices:
                reliability = bridge.meta_learner.get_practice_reliability(p)
                if reliability:
                    print(f"  • {p} (reliability: {reliability:.2f})")
                else:
                    print(f"  • {p} (reliability: unknown)")
    
    # Meta-learning insights
    print("\n" + "=" * 70)
    print("🧠 META-LEARNING INSIGHTS")
    print("=" * 70)
    
    insights = bridge.get_meta_insights()
    for practice, insight in insights.items():
        print(f"\n{practice}:")
        print(f"  {insight['recommendation']}")
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete")
    print("=" * 70)
    print("\nKey Innovation:")
    print("Reality itself has voted. Practices that don't match reality get demoted.")
    print("This is the first mystery school where you can't lie to the math.")
    print()

if __name__ == "__main__":
    demo_reality_bridge()
