#!/usr/bin/env python3
"""
CURRICULUM BUILDER
==================
Transform massive mystery school curriculum into structured, testable modules.

Takes the 400+ page curriculum and creates:
1. Modular courses with clear prerequisites
2. Testing frameworks for each practice
3. Integration with research pipeline
4. Progressive difficulty levels
"""

import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class DifficultyLevel(Enum):
    """Course difficulty levels"""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class TimeCommitment(Enum):
    """Expected time investment"""
    DAILY_5MIN = "5 min/day"
    DAILY_15MIN = "15 min/day"
    DAILY_30MIN = "30 min/day"
    DAILY_60MIN = "60 min/day"
    WEEKLY_2HR = "2 hr/week"
    WEEKLY_5HR = "5 hr/week"
    INTENSIVE = "full-time intensive"


@dataclass
class LearningObjective:
    """Specific skill or understanding to be gained"""
    description: str
    measurable: bool  # Can this be objectively tested?
    measurement_method: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "description": self.description,
            "measurable": self.measurable,
            "measurement_method": self.measurement_method
        }


@dataclass
class CourseModule:
    """Single course module within mystery school"""
    
    # Basic info
    id: str
    name: str
    description: str
    domain: str  # Alchemy, Divination, Energy Healing, etc.
    
    # Difficulty
    difficulty: DifficultyLevel
    time_commitment: TimeCommitment
    duration_weeks: int
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)  # List of module IDs
    
    # Content
    learning_objectives: List[LearningObjective] = field(default_factory=list)
    practices: List[str] = field(default_factory=list)
    readings: List[str] = field(default_factory=list)
    
    # Evidence base
    research_backing: Optional[float] = None  # Π value if available
    current_layer: Optional[str] = None  # EDGE, MIDDLE, or FOUNDATION
    
    # Safety
    contraindications: List[str] = field(default_factory=list)
    safety_notes: str = ""
    
    # Metadata
    created_by: str = "mystery_school"
    last_updated: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "difficulty": self.difficulty.name,
            "time_commitment": self.time_commitment.value,
            "duration_weeks": self.duration_weeks,
            "prerequisites": self.prerequisites,
            "learning_objectives": [obj.to_dict() for obj in self.learning_objectives],
            "practices": self.practices,
            "readings": self.readings,
            "research_backing": self.research_backing,
            "current_layer": self.current_layer,
            "contraindications": self.contraindications,
            "safety_notes": self.safety_notes
        }
    
    def get_total_prerequisites(self, all_modules: Dict[str, 'CourseModule']) -> Set[str]:
        """Recursively get all prerequisites"""
        prereqs = set(self.prerequisites)
        for prereq_id in self.prerequisites:
            if prereq_id in all_modules:
                prereqs.update(all_modules[prereq_id].get_total_prerequisites(all_modules))
        return prereqs


@dataclass
class LearningPath:
    """Ordered sequence of modules for a specific goal"""
    name: str
    description: str
    module_sequence: List[str]  # Ordered list of module IDs
    estimated_months: int
    target_audience: str
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "module_sequence": self.module_sequence,
            "estimated_months": self.estimated_months,
            "target_audience": self.target_audience
        }


class CurriculumDatabase:
    """Database of all courses and learning paths"""
    
    def __init__(self):
        self.modules: Dict[str, CourseModule] = {}
        self.paths: Dict[str, LearningPath] = {}
        self.domains: Set[str] = set()
    
    def add_module(self, module: CourseModule):
        """Add a course module"""
        self.modules[module.id] = module
        self.domains.add(module.domain)
    
    def add_path(self, path: LearningPath):
        """Add a learning path"""
        self.paths[path.name] = path
    
    def get_module(self, module_id: str) -> Optional[CourseModule]:
        """Get module by ID"""
        return self.modules.get(module_id)
    
    def get_modules_by_domain(self, domain: str) -> List[CourseModule]:
        """Get all modules in a domain"""
        return [m for m in self.modules.values() if m.domain == domain]
    
    def get_modules_by_difficulty(self, difficulty: DifficultyLevel) -> List[CourseModule]:
        """Get modules at a difficulty level"""
        return [m for m in self.modules.values() if m.difficulty == difficulty]
    
    def get_beginner_modules(self) -> List[CourseModule]:
        """Get all beginner-friendly modules (no prerequisites)"""
        return [m for m in self.modules.values() if not m.prerequisites]
    
    def validate_prerequisites(self) -> List[str]:
        """Check for invalid prerequisites"""
        errors = []
        for module in self.modules.values():
            for prereq in module.prerequisites:
                if prereq not in self.modules:
                    errors.append(f"{module.id} requires {prereq} which doesn't exist")
        return errors
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular prerequisite chains"""
        circles = []
        
        def has_cycle(module_id: str, visited: Set[str], path: List[str]) -> bool:
            if module_id in visited:
                cycle_start = path.index(module_id)
                circles.append(path[cycle_start:])
                return True
            
            if module_id not in self.modules:
                return False
            
            visited.add(module_id)
            path.append(module_id)
            
            for prereq in self.modules[module_id].prerequisites:
                if has_cycle(prereq, visited.copy(), path.copy()):
                    return True
            
            return False
        
        for module_id in self.modules:
            has_cycle(module_id, set(), [])
        
        return circles
    
    def export_to_json(self, filename: str):
        """Export entire curriculum to JSON"""
        data = {
            "modules": {
                module_id: module.to_dict()
                for module_id, module in self.modules.items()
            },
            "paths": {
                path_name: path.to_dict()
                for path_name, path in self.paths.items()
            },
            "domains": list(self.domains)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_catalog(self) -> str:
        """Generate human-readable course catalog"""
        catalog = []
        catalog.append("=" * 70)
        catalog.append("MYSTERY SCHOOL COURSE CATALOG")
        catalog.append("=" * 70)
        
        # Group by domain
        for domain in sorted(self.domains):
            catalog.append(f"\n{domain.upper()}")
            catalog.append("-" * 70)
            
            modules = self.get_modules_by_domain(domain)
            modules.sort(key=lambda m: m.difficulty.value)
            
            for module in modules:
                catalog.append(f"\n{module.name} ({module.id})")
                catalog.append(f"  Difficulty: {module.difficulty.name}")
                catalog.append(f"  Time: {module.time_commitment.value} for {module.duration_weeks} weeks")
                
                if module.prerequisites:
                    catalog.append(f"  Prerequisites: {', '.join(module.prerequisites)}")
                
                if module.research_backing:
                    catalog.append(f"  Evidence: Π = {module.research_backing:.2f} ({module.current_layer})")
                
                if module.contraindications:
                    catalog.append(f"  ⚠️  Contraindications: {len(module.contraindications)}")
        
        # Learning paths
        catalog.append("\n" + "=" * 70)
        catalog.append("LEARNING PATHS")
        catalog.append("=" * 70)
        
        for path_name, path in self.paths.items():
            catalog.append(f"\n{path.name}")
            catalog.append(f"  {path.description}")
            catalog.append(f"  Duration: ~{path.estimated_months} months")
            catalog.append(f"  Target: {path.target_audience}")
            catalog.append(f"  Modules: {len(path.module_sequence)}")
        
        return "\n".join(catalog)


# =========================
# EXAMPLE CURRICULUM
# =========================

def build_example_curriculum() -> CurriculumDatabase:
    """Build example curriculum from mystery school subjects"""
    db = CurriculumDatabase()
    
    # FOUNDATION: Body Sovereignty
    body_sovereignty = CourseModule(
        id="foundation_body_sovereignty",
        name="Body Sovereignty & Consent",
        description="Learn to inhabit your body, set boundaries, and practice consent in all areas of life.",
        domain="Foundation",
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.DAILY_15MIN,
        duration_weeks=12,
        prerequisites=[],
        learning_objectives=[
            LearningObjective("Identify body sensations without judgment", True, "Body scan self-assessment"),
            LearningObjective("Communicate clear boundaries", True, "Role-play exercises"),
            LearningObjective("Distinguish 'yes' from 'maybe' from 'no'", True, "Somatic awareness test")
        ],
        practices=["Body scan meditation", "Boundary setting exercises", "Consent practice"],
        research_backing=1.5,
        current_layer="FOUNDATION",
        contraindications=[],
        safety_notes="Trauma survivors should work with therapist alongside this course"
    )
    db.add_module(body_sovereignty)
    
    # BEGINNER: Mindfulness Meditation
    mindfulness = CourseModule(
        id="meditation_mindfulness_basic",
        name="Mindfulness Meditation Fundamentals",
        description="Learn shamatha (concentration) and vipassana (insight) meditation.",
        domain="Meditation",
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.DAILY_30MIN,
        duration_weeks=8,
        prerequisites=[],
        learning_objectives=[
            LearningObjective("Maintain focus on breath for 10 minutes", True, "Timed meditation session"),
            LearningObjective("Notice thoughts without following them", True, "Mental noting practice"),
            LearningObjective("Reduce reactivity to emotions", True, "Pre/post psychological assessment")
        ],
        practices=["Breath meditation", "Body scan", "Walking meditation", "Mental noting"],
        research_backing=1.30,
        current_layer="MIDDLE",
        contraindications=["Active psychosis", "Severe dissociation without therapist"],
        safety_notes="Start with 5 minutes, increase gradually"
    )
    db.add_module(mindfulness)
    
    # INTERMEDIATE: Shadow Work
    shadow_work = CourseModule(
        id="psychology_shadow_work",
        name="Shadow Work Intensive",
        description="Integrate disowned parts of self through Jungian active imagination and parts work.",
        domain="Psychological Integration",
        difficulty=DifficultyLevel.INTERMEDIATE,
        time_commitment=TimeCommitment.DAILY_30MIN,
        duration_weeks=12,
        prerequisites=["foundation_body_sovereignty", "meditation_mindfulness_basic"],
        learning_objectives=[
            LearningObjective("Identify personal shadow patterns", True, "Projection tracking"),
            LearningObjective("Dialogue with rejected parts", False, None),
            LearningObjective("Reduce judgment of others", True, "Pre/post bias assessment")
        ],
        practices=["Active imagination", "Dream journaling", "Projection work", "Parts dialogue"],
        research_backing=1.7,
        current_layer="FOUNDATION",
        contraindications=["Unstable mental health", "Recent trauma without support"],
        safety_notes="Recommend working with therapist during this course"
    )
    db.add_module(shadow_work)
    
    # ADVANCED: Jhana States
    jhanas = CourseModule(
        id="meditation_jhanas",
        name="Jhana States (Meditative Absorption)",
        description="Develop concentration to access jhana 1-4, states of deep meditative absorption.",
        domain="Meditation",
        difficulty=DifficultyLevel.ADVANCED,
        time_commitment=TimeCommitment.DAILY_60MIN,
        duration_weeks=24,
        prerequisites=["meditation_mindfulness_basic"],
        learning_objectives=[
            LearningObjective("Sustain focus for 45+ minutes", True, "Timed sessions"),
            LearningObjective("Access jhana 1 reliably", False, "Self-report + instructor verification"),
            LearningObjective("Understand jhana factors", True, "Written assessment")
        ],
        practices=["Extended sitting", "Jhana practice", "Retreat attendance"],
        research_backing=1.6,
        current_layer="MIDDLE",
        contraindications=["Epilepsy (check with doctor)", "Dissociative disorders"],
        safety_notes="Not for beginners. Requires solid shamatha foundation."
    )
    db.add_module(jhanas)
    
    # EDGE: Reiki
    reiki = CourseModule(
        id="energy_reiki",
        name="Reiki Level 1 (Evidence-Based)",
        description="Learn Reiki as nervous system co-regulation, not 'energy channeling'.",
        domain="Energy Healing",
        difficulty=DifficultyLevel.INTERMEDIATE,
        time_commitment=TimeCommitment.WEEKLY_2HR,
        duration_weeks=12,
        prerequisites=["foundation_body_sovereignty"],
        learning_objectives=[
            LearningObjective("Self-regulate nervous system", True, "HRV measurement"),
            LearningObjective("Provide grounded presence", True, "Co-regulation assessment"),
            LearningObjective("Set appropriate boundaries", True, "Ethics exam")
        ],
        practices=["Self-Reiki", "Partner exchanges", "Grounding techniques"],
        research_backing=0.61,
        current_layer="EDGE",
        contraindications=[],
        safety_notes="Framed as psychology/touch, not supernatural. No grandiose claims."
    )
    db.add_module(reiki)
    
    # EXPERT: Death Doula Training
    death_doula = CourseModule(
        id="death_doula",
        name="Death Doula Certification",
        description="Professional training for end-of-life support and sacred dying practices.",
        domain="Death Studies",
        difficulty=DifficultyLevel.EXPERT,
        time_commitment=TimeCommitment.INTENSIVE,
        duration_weeks=20,
        prerequisites=["psychology_shadow_work", "foundation_body_sovereignty"],
        learning_objectives=[
            LearningObjective("Recognize active dying symptoms", True, "Medical assessment"),
            LearningObjective("Hold vigil without collapse", True, "Distress tolerance measure"),
            LearningObjective("Support families through grief", True, "Practical exam")
        ],
        practices=["Vigil holding", "Family support", "Ritual facilitation", "After-death care"],
        research_backing=1.4,
        current_layer="MIDDLE",
        contraindications=["Unresolved death trauma", "Active grief"],
        safety_notes="Requires strong boundaries and self-care practices"
    )
    db.add_module(death_doula)
    
    # Learning Paths
    beginner_path = LearningPath(
        name="Consciousness Foundations",
        description="Start here: Body sovereignty, meditation basics, shadow work",
        module_sequence=[
            "foundation_body_sovereignty",
            "meditation_mindfulness_basic",
            "psychology_shadow_work"
        ],
        estimated_months=8,
        target_audience="Complete beginners to mystery school work"
    )
    db.add_path(beginner_path)
    
    advanced_meditation = LearningPath(
        name="Advanced Meditation Track",
        description="From basics to jhanas to formless realms",
        module_sequence=[
            "meditation_mindfulness_basic",
            "meditation_jhanas"
        ],
        estimated_months=8,
        target_audience="Serious meditators seeking depth"
    )
    db.add_path(advanced_meditation)
    
    death_worker = LearningPath(
        name="Death Work Professional",
        description="Complete training for death doula certification",
        module_sequence=[
            "foundation_body_sovereignty",
            "meditation_mindfulness_basic",
            "psychology_shadow_work",
            "death_doula"
        ],
        estimated_months=14,
        target_audience="Healthcare workers, hospice volunteers, spiritual guides"
    )
    db.add_path(death_worker)
    
    return db


# =========================
# DEMONSTRATION
# =========================

def main():
    print("=" * 70)
    print("CURRICULUM BUILDER - Mystery School Course Management")
    print("=" * 70)
    
    # Build example curriculum
    db = build_example_curriculum()
    
    # Validate
    errors = db.validate_prerequisites()
    if errors:
        print("\n⚠️  Prerequisite errors found:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("\n✅ All prerequisites valid")
    
    circles = db.detect_circular_dependencies()
    if circles:
        print("\n⚠️  Circular dependencies found:")
        for circle in circles:
            print(f"  • {' → '.join(circle)}")
    else:
        print("✅ No circular dependencies")
    
    # Generate catalog
    print("\n" + db.generate_catalog())
    
    # Export
    db.export_to_json("/home/claude/curriculum.json")
    print("\n✅ Exported to curriculum.json")
    
    # Show module details
    print("\n" + "=" * 70)
    print("EXAMPLE MODULE DETAIL")
    print("=" * 70)
    
    shadow = db.get_module("psychology_shadow_work")
    if shadow:
        print(f"\nModule: {shadow.name}")
        print(f"Domain: {shadow.domain}")
        print(f"Difficulty: {shadow.difficulty.name}")
        print(f"Duration: {shadow.duration_weeks} weeks @ {shadow.time_commitment.value}")
        print(f"\nPrerequisites: {len(shadow.prerequisites)}")
        for prereq in shadow.prerequisites:
            prereq_module = db.get_module(prereq)
            if prereq_module:
                print(f"  • {prereq_module.name}")
        
        print(f"\nLearning Objectives: {len(shadow.learning_objectives)}")
        for i, obj in enumerate(shadow.learning_objectives, 1):
            measurable = "✓" if obj.measurable else "✗"
            print(f"  {i}. {obj.description} [Measurable: {measurable}]")
        
        if shadow.contraindications:
            print(f"\n⚠️  Contraindications:")
            for contra in shadow.contraindications:
                print(f"  • {contra}")


if __name__ == "__main__":
    main()
