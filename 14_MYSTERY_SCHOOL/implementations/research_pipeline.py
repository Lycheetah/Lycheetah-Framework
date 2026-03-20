#!/usr/bin/env python3
"""
RESEARCH DATA PIPELINE
======================
Ingest real research, calculate Truth Pressure (Π), validate practices.

This is what was missing: actual data handling, not just mock tests.
"""

import json
import statistics
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import csv


class StudyType(Enum):
    """Types of research studies"""
    RCT = "randomized_controlled_trial"
    META_ANALYSIS = "meta_analysis"
    OBSERVATIONAL = "observational"
    CASE_STUDY = "case_study"
    SYSTEMATIC_REVIEW = "systematic_review"


class QualityRating(Enum):
    """Study quality ratings"""
    HIGH = 1.0      # Well-designed RCT, large sample
    MODERATE = 0.7  # Good design, some limitations
    LOW = 0.4       # Observational, small sample
    VERY_LOW = 0.1  # Anecdotal, major flaws


@dataclass
class ResearchStudy:
    """Single research study"""
    practice_name: str
    effect_size: float  # Cohen's d or similar
    sample_size: int
    p_value: float
    study_type: StudyType
    quality: QualityRating
    year: int
    citation: str
    notes: str = ""
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check statistical significance"""
        return self.p_value < alpha
    
    def weighted_effect(self) -> float:
        """Effect size weighted by quality and sample size"""
        size_weight = min(1.0, self.sample_size / 100)  # Cap at 100
        return self.effect_size * self.quality.value * size_weight
    
    def to_dict(self) -> Dict:
        return {
            "practice": self.practice_name,
            "effect_size": self.effect_size,
            "sample_size": self.sample_size,
            "p_value": self.p_value,
            "study_type": self.study_type.value,
            "quality": self.quality.name,
            "year": self.year,
            "citation": self.citation,
            "significant": self.is_significant()
        }


@dataclass
class PracticeEvidence:
    """All evidence for a specific practice"""
    practice_name: str
    studies: List[ResearchStudy] = field(default_factory=list)
    
    def add_study(self, study: ResearchStudy):
        """Add a study to evidence base"""
        if study.practice_name != self.practice_name:
            raise ValueError(f"Study for {study.practice_name} added to {self.practice_name}")
        self.studies.append(study)
    
    def calculate_truth_pressure(self) -> float:
        """
        Calculate Π (Truth Pressure) from all studies.
        
        Π = (mean_effect × consistency × quality) / noise
        
        Higher Π = stronger evidence
        Π < 1.2 : EDGE (experimental)
        1.2 ≤ Π < 1.5 : MIDDLE (validated)
        Π ≥ 1.5 : FOUNDATION (proven)
        """
        if not self.studies:
            return 0.0
        
        # Get weighted effects
        weighted_effects = [s.weighted_effect() for s in self.studies]
        
        # Mean effect (strength of signal)
        mean_effect = statistics.mean(weighted_effects)
        
        # Consistency (how much studies agree)
        if len(weighted_effects) > 1:
            effect_range = max(weighted_effects) - min(weighted_effects)
            consistency = 1.0 - (effect_range / (abs(mean_effect) + 0.1))
            consistency = max(0.0, min(1.0, consistency))
        else:
            consistency = 1.0  # Single study, no disagreement yet
        
        # Quality (average study quality)
        avg_quality = statistics.mean([s.quality.value for s in self.studies])
        
        # Noise (inverse of sample sizes and p-values)
        avg_sample = statistics.mean([s.sample_size for s in self.studies])
        sample_factor = min(1.0, avg_sample / 200)  # Normalize
        
        # Significance factor (how many are significant)
        sig_count = sum(1 for s in self.studies if s.is_significant())
        sig_ratio = sig_count / len(self.studies) if self.studies else 0
        
        noise = 1.0 - (sample_factor * sig_ratio)
        noise = max(0.1, noise)  # Prevent division by very small numbers
        
        # Final Π calculation
        pi = (mean_effect * consistency * avg_quality) / noise
        
        return max(0.0, pi)  # Can't be negative
    
    def get_layer_recommendation(self) -> str:
        """Recommend which layer this practice belongs in"""
        pi = self.calculate_truth_pressure()
        
        if pi < 1.2:
            return "EDGE"
        elif pi < 1.5:
            return "MIDDLE"
        else:
            return "FOUNDATION"
    
    def summary(self) -> Dict:
        """Summary of evidence"""
        pi = self.calculate_truth_pressure()
        
        return {
            "practice": self.practice_name,
            "num_studies": len(self.studies),
            "truth_pressure": round(pi, 2),
            "layer": self.get_layer_recommendation(),
            "mean_effect_size": round(statistics.mean([s.effect_size for s in self.studies]), 3) if self.studies else 0,
            "significant_studies": sum(1 for s in self.studies if s.is_significant()),
            "avg_sample_size": round(statistics.mean([s.sample_size for s in self.studies])) if self.studies else 0,
            "quality_distribution": {
                "HIGH": sum(1 for s in self.studies if s.quality == QualityRating.HIGH),
                "MODERATE": sum(1 for s in self.studies if s.quality == QualityRating.MODERATE),
                "LOW": sum(1 for s in self.studies if s.quality == QualityRating.LOW),
                "VERY_LOW": sum(1 for s in self.studies if s.quality == QualityRating.VERY_LOW),
            }
        }


class ResearchDatabase:
    """Database of all practice evidence"""
    
    def __init__(self):
        self.practices: Dict[str, PracticeEvidence] = {}
    
    def add_study(self, study: ResearchStudy):
        """Add study to database"""
        if study.practice_name not in self.practices:
            self.practices[study.practice_name] = PracticeEvidence(study.practice_name)
        
        self.practices[study.practice_name].add_study(study)
    
    def get_practice(self, name: str) -> Optional[PracticeEvidence]:
        """Get evidence for a practice"""
        return self.practices.get(name)
    
    def calculate_all_pi(self) -> Dict[str, float]:
        """Calculate Π for all practices"""
        return {
            name: evidence.calculate_truth_pressure()
            for name, evidence in self.practices.items()
        }
    
    def get_layer_assignments(self) -> Dict[str, List[str]]:
        """Get practices organized by layer"""
        layers = {"EDGE": [], "MIDDLE": [], "FOUNDATION": []}
        
        for name, evidence in self.practices.items():
            layer = evidence.get_layer_recommendation()
            layers[layer].append(name)
        
        return layers
    
    def export_to_csv(self, filename: str):
        """Export all evidence to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Practice", "Truth_Pressure", "Layer", "Num_Studies",
                "Mean_Effect", "Significant_Studies", "Avg_Sample_Size"
            ])
            
            for name, evidence in self.practices.items():
                summary = evidence.summary()
                writer.writerow([
                    name,
                    summary["truth_pressure"],
                    summary["layer"],
                    summary["num_studies"],
                    summary["mean_effect_size"],
                    summary["significant_studies"],
                    summary["avg_sample_size"]
                ])
    
    def export_to_json(self, filename: str):
        """Export full evidence to JSON"""
        data = {
            name: {
                "summary": evidence.summary(),
                "studies": [s.to_dict() for s in evidence.studies]
            }
            for name, evidence in self.practices.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, filename: str):
        """Import evidence from JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        for practice_name, practice_data in data.items():
            for study_dict in practice_data["studies"]:
                study = ResearchStudy(
                    practice_name=study_dict["practice"],
                    effect_size=study_dict["effect_size"],
                    sample_size=study_dict["sample_size"],
                    p_value=study_dict["p_value"],
                    study_type=StudyType(study_dict["study_type"]),
                    quality=QualityRating[study_dict["quality"]],
                    year=study_dict["year"],
                    citation=study_dict["citation"]
                )
                self.add_study(study)
    
    def generate_report(self) -> str:
        """Generate text report of all evidence"""
        report = []
        report.append("=" * 70)
        report.append("RESEARCH DATABASE REPORT")
        report.append("=" * 70)
        
        layers = self.get_layer_assignments()
        
        for layer_name in ["FOUNDATION", "MIDDLE", "EDGE"]:
            practices = layers[layer_name]
            report.append(f"\n{layer_name} LAYER ({len(practices)} practices)")
            report.append("-" * 70)
            
            for practice in sorted(practices):
                evidence = self.practices[practice]
                summary = evidence.summary()
                report.append(f"\n{practice}:")
                report.append(f"  Π = {summary['truth_pressure']}")
                report.append(f"  Studies: {summary['num_studies']} (sig: {summary['significant_studies']})")
                report.append(f"  Mean effect: {summary['mean_effect_size']}")
                report.append(f"  Avg N: {summary['avg_sample_size']}")
        
        report.append("\n" + "=" * 70)
        report.append(f"TOTAL PRACTICES: {len(self.practices)}")
        report.append("=" * 70)
        
        return "\n".join(report)


# =========================
# EXAMPLE DATA
# =========================

def load_example_data() -> ResearchDatabase:
    """Load example research data (real-ish values)"""
    db = ResearchDatabase()
    
    # Mindfulness meditation (strong evidence)
    db.add_study(ResearchStudy(
        practice_name="Mindfulness Meditation",
        effect_size=0.53,
        sample_size=209,
        p_value=0.001,
        study_type=StudyType.META_ANALYSIS,
        quality=QualityRating.HIGH,
        year=2014,
        citation="Khoury et al. (2015) Clinical Psychology Review"
    ))
    
    db.add_study(ResearchStudy(
        practice_name="Mindfulness Meditation",
        effect_size=0.38,
        sample_size=142,
        p_value=0.02,
        study_type=StudyType.RCT,
        quality=QualityRating.MODERATE,
        year=2018,
        citation="Goldberg et al. (2018) JAMA"
    ))
    
    # Reiki (weak evidence)
    db.add_study(ResearchStudy(
        practice_name="Reiki",
        effect_size=0.24,
        sample_size=45,
        p_value=0.08,
        study_type=StudyType.OBSERVATIONAL,
        quality=QualityRating.LOW,
        year=2016,
        citation="McManus (2017) Holistic Nursing Practice"
    ))
    
    db.add_study(ResearchStudy(
        practice_name="Reiki",
        effect_size=0.19,
        sample_size=32,
        p_value=0.15,
        study_type=StudyType.RCT,
        quality=QualityRating.LOW,
        year=2015,
        citation="Joyce & Herbison (2015) Cochrane Review"
    ))
    
    # Crystal healing (very weak)
    db.add_study(ResearchStudy(
        practice_name="Crystal Healing",
        effect_size=0.02,
        sample_size=25,
        p_value=0.89,
        study_type=StudyType.CASE_STUDY,
        quality=QualityRating.VERY_LOW,
        year=2019,
        citation="Anonymous blog post"
    ))
    
    # Cognitive Behavioral Therapy (very strong)
    db.add_study(ResearchStudy(
        practice_name="Cognitive Behavioral Therapy",
        effect_size=0.75,
        sample_size=2500,
        p_value=0.0001,
        study_type=StudyType.META_ANALYSIS,
        quality=QualityRating.HIGH,
        year=2012,
        citation="Hofmann et al. (2012) Cognitive Therapy Research"
    ))
    
    db.add_study(ResearchStudy(
        practice_name="Cognitive Behavioral Therapy",
        effect_size=0.68,
        sample_size=1200,
        p_value=0.0001,
        study_type=StudyType.SYSTEMATIC_REVIEW,
        quality=QualityRating.HIGH,
        year=2018,
        citation="Carpenter et al. (2018) World Psychiatry"
    ))
    
    # Breathwork (moderate evidence)
    db.add_study(ResearchStudy(
        practice_name="Breathwork",
        effect_size=0.42,
        sample_size=89,
        p_value=0.03,
        study_type=StudyType.RCT,
        quality=QualityRating.MODERATE,
        year=2020,
        citation="Balban et al. (2023) Cell Reports Medicine"
    ))
    
    return db


# =========================
# DEMONSTRATION
# =========================

def main():
    print("=" * 70)
    print("RESEARCH DATA PIPELINE - Truth Pressure Calculator")
    print("=" * 70)
    
    # Load example data
    db = load_example_data()
    
    # Generate report
    print("\n" + db.generate_report())
    
    # Show detailed calculation for one practice
    print("\n" + "=" * 70)
    print("DETAILED CALCULATION: Mindfulness Meditation")
    print("=" * 70)
    
    mindfulness = db.get_practice("Mindfulness Meditation")
    if mindfulness:
        print(f"\nStudies: {len(mindfulness.studies)}")
        for i, study in enumerate(mindfulness.studies, 1):
            print(f"\n  Study {i}:")
            print(f"    Effect size: {study.effect_size}")
            print(f"    Sample: {study.sample_size}")
            print(f"    p-value: {study.p_value}")
            print(f"    Quality: {study.quality.name}")
            print(f"    Weighted effect: {study.weighted_effect():.3f}")
        
        print(f"\nΠ (Truth Pressure): {mindfulness.calculate_truth_pressure():.2f}")
        print(f"Layer: {mindfulness.get_layer_recommendation()}")
    
    # Export
    db.export_to_csv("research_evidence.csv")
    db.export_to_json("research_evidence.json")
    print(f"\n✅ Exported to research_evidence.csv and .json")
    
    # Show layer distribution
    print("\n" + "=" * 70)
    print("LAYER DISTRIBUTION")
    print("=" * 70)
    layers = db.get_layer_assignments()
    for layer, practices in layers.items():
        print(f"\n{layer}: {len(practices)} practices")
        for p in practices:
            pi = db.practices[p].calculate_truth_pressure()
            print(f"  • {p} (Π={pi:.2f})")


if __name__ == "__main__":
    main()
