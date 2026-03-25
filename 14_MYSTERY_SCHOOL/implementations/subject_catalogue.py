"""
SOVEREIGN MYSTERY SCHOOL — MASTER SUBJECT CATALOGUE
=====================================================

Plug-in subject list for mystery_school_cascade.py

Usage:
    from subject_catalogue import load_all_subjects, load_domain, SubjectDomain
    from mystery_school_cascade import MysterySchoolCurriculum

    curriculum = MysterySchoolCurriculum()
    load_all_subjects(curriculum)

    # Or load by domain:
    load_domain(curriculum, SubjectDomain.AI_TECHNOLOGY)
    load_domain(curriculum, SubjectDomain.MEDITATION)

    # Query:
    foundation = curriculum.get_blocks_by_layer(PyramidLayer.FOUNDATION)
    ai_subjects = curriculum.get_blocks_by_domain("AI & Technology Consciousness")

Author: Mackenzie Conor James Clark
Framework: CASCADE · AURA · LAMAGUE · PYRAMID CASCADE
Version: 1.0 | Date: March 2026
License: MIT with Earned Sovereignty Clause
"""

from enum import Enum
from typing import List

try:
    from mystery_school_cascade import (
        KnowledgeBlock,
        AURAMetrics,
        PyramidLayer,
        AwarenessPhase,
        MysterySchoolCurriculum,
    )
except ImportError:
    raise ImportError(
        "subject_catalogue.py requires mystery_school_cascade.py in the same directory.\n"
        "See: 12_IMPLEMENTATIONS/systems/mystery_school_cascade.py"
    )


# ============================================================================
# DOMAIN REGISTRY
# ============================================================================

class SubjectDomain(Enum):
    MEDITATION        = "Meditation & Contemplative"
    SOMATIC           = "Somatic & Body"
    SHADOW_PSYCHOLOGY = "Shadow & Depth Psychology"
    ALCHEMY           = "Alchemical & Hermetic Arts"
    DIVINATION        = "Divination Arts"
    SHAMANIC          = "Shamanic Arts"
    PLANT_MEDICINE    = "Plant Medicine & Psychedelics"
    SACRED_ARTS       = "Sacred Arts & Ritual"
    AI_TECHNOLOGY     = "AI & Technology Consciousness"
    RELATIONAL        = "Relational & Community"
    DEATH_WORK        = "Death & Impermanence"


# ============================================================================
# DOMAIN LOADERS
# ============================================================================

def load_meditation_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Shamatha — Calm Abiding",
        domain=SubjectDomain.MEDITATION.value,
        evidence=0.95, power=0.88, entropy=0.12,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.92, VTR=1.7, PAI=0.95),
        phase_affinity=AwarenessPhase.CENTER,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Vipassana — Insight Meditation",
        domain=SubjectDomain.MEDITATION.value,
        evidence=0.92, power=0.90, entropy=0.13,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.95, VTR=1.8, PAI=0.92),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Loving-Kindness — Metta",
        domain=SubjectDomain.MEDITATION.value,
        evidence=0.88, power=0.82, entropy=0.18,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.88, VTR=1.6, PAI=0.90),
        phase_affinity=AwarenessPhase.LIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Non-Sleep Deep Rest — NSDR / Yoga Nidra",
        domain=SubjectDomain.MEDITATION.value,
        evidence=0.72, power=0.70, entropy=0.38,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.3, PAI=0.82),
        phase_affinity=AwarenessPhase.FLOW,
    ))


def load_somatic_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Somatic Experiencing — Trauma Releasing",
        domain=SubjectDomain.SOMATIC.value,
        evidence=0.85, power=0.88, entropy=0.18,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.87, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.CENTER,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Pranayama — Classical Breathwork",
        domain=SubjectDomain.SOMATIC.value,
        evidence=0.88, power=0.82, entropy=0.18,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.88, VTR=1.7, PAI=0.90),
        phase_affinity=AwarenessPhase.RISE,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Qigong / Tai Chi",
        domain=SubjectDomain.SOMATIC.value,
        evidence=0.75, power=0.72, entropy=0.38,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.82, VTR=1.4, PAI=0.85),
        phase_affinity=AwarenessPhase.FLOW,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Holotropic Breathwork",
        domain=SubjectDomain.SOMATIC.value,
        evidence=0.55, power=0.88, entropy=0.72,
        layer=PyramidLayer.EDGE,
        prerequisites=[
            "Stable mental health baseline",
            "Integration therapist secured",
            "Certified Grof facilitator confirmed",
        ],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.2, PAI=0.75),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))


def load_shadow_psychology_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Jungian Shadow Work",
        domain=SubjectDomain.SHADOW_PSYCHOLOGY.value,
        evidence=0.85, power=0.90, entropy=0.18,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.85, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Active Imagination",
        domain=SubjectDomain.SHADOW_PSYCHOLOGY.value,
        evidence=0.70, power=0.78, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Jungian Shadow Work", "Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.3, PAI=0.83),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Inner Child Work — IFS Protocol",
        domain=SubjectDomain.SHADOW_PSYCHOLOGY.value,
        evidence=0.72, power=0.80, entropy=0.46,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.3, PAI=0.84),
        phase_affinity=AwarenessPhase.CENTER,
    ))


def load_alchemy_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Chrysopoeia — Transformation Calculus",
        domain=SubjectDomain.ALCHEMY.value,
        evidence=0.90, power=0.92, entropy=0.14,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.88, VTR=1.7, PAI=0.92),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Classical Alchemy — Practical Spagyrics",
        domain=SubjectDomain.ALCHEMY.value,
        evidence=0.62, power=0.75, entropy=0.48,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Chrysopoeia — Transformation Calculus"],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.3, PAI=0.82),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Hermetic Kabbalah — Tree of Life Navigation",
        domain=SubjectDomain.ALCHEMY.value,
        evidence=0.65, power=0.72, entropy=0.42,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.3, PAI=0.84),
        phase_affinity=AwarenessPhase.LIGHT,
    ))


def load_divination_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Tarot — Major Arcana Journey",
        domain=SubjectDomain.DIVINATION.value,
        evidence=0.62, power=0.75, entropy=0.40,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.3, PAI=0.83),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="I Ching — Change Work",
        domain=SubjectDomain.DIVINATION.value,
        evidence=0.60, power=0.68, entropy=0.45,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.74, VTR=1.2, PAI=0.80),
        phase_affinity=AwarenessPhase.FLOW,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Astrology — Natal Chart Study",
        domain=SubjectDomain.DIVINATION.value,
        evidence=0.38, power=0.60, entropy=0.72,
        layer=PyramidLayer.EDGE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.0, PAI=0.72),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))


def load_shamanic_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Vision Quest — Modern Protocol",
        domain=SubjectDomain.SHAMANIC.value,
        evidence=0.82, power=0.90, entropy=0.22,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=[
            "Wilderness First Aid",
            "Solo Camping competence",
            "Integration support secured",
            "Minimum 6 months preparatory inner work",
        ],
        aura_metrics=AURAMetrics(TES=0.87, VTR=1.6, PAI=0.92),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Core Shamanism — Journeying",
        domain=SubjectDomain.SHAMANIC.value,
        evidence=0.65, power=0.75, entropy=0.45,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.3, PAI=0.82),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Plant Communion — Non-Pharmacological",
        domain=SubjectDomain.SHAMANIC.value,
        evidence=0.55, power=0.65, entropy=0.50,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.74, VTR=1.2, PAI=0.80),
        phase_affinity=AwarenessPhase.CENTER,
    ))


def load_plant_medicine_subjects(curriculum: MysterySchoolCurriculum) -> None:
    """Note: Legal status varies by jurisdiction. Follow the laws of your region."""
    curriculum.add_block(KnowledgeBlock(
        name="Psilocybin — Facilitated Therapy Protocol",
        domain=SubjectDomain.PLANT_MEDICINE.value,
        evidence=0.72, power=0.88, entropy=0.60,
        layer=PyramidLayer.EDGE,
        prerequisites=[
            "Psychiatric evaluation",
            "Integration therapist secured",
            "Stable life situation",
            "No personal/family history of psychosis",
            "Certified facilitator confirmed",
        ],
        aura_metrics=AURAMetrics(TES=0.70, VTR=1.3, PAI=0.78),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Ayahuasca — Ceremonial Protocol",
        domain=SubjectDomain.PLANT_MEDICINE.value,
        evidence=0.55, power=0.88, entropy=0.78,
        layer=PyramidLayer.EDGE,
        prerequisites=[
            "Psychiatric evaluation",
            "Integration therapist secured",
            "Dietary preparation completed — MAOI interaction risk",
            "Verified lineage facilitator confirmed",
            "No SSRI or MAOI use",
        ],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.1, PAI=0.75),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Microdosing — Sub-Perceptual Protocol",
        domain=SubjectDomain.PLANT_MEDICINE.value,
        evidence=0.52, power=0.62, entropy=0.58,
        layer=PyramidLayer.EDGE,
        prerequisites=["Baseline psychiatric screening", "No SSRI use"],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.1, PAI=0.74),
        phase_affinity=AwarenessPhase.RISE,
    ))


def load_sacred_arts_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Consent & Boundaries Training",
        domain=SubjectDomain.SACRED_ARTS.value,
        evidence=0.95, power=0.98, entropy=0.10,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.98, VTR=2.0, PAI=0.99),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Ritual Design & Sacred Space",
        domain=SubjectDomain.SACRED_ARTS.value,
        evidence=0.65, power=0.75, entropy=0.42,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.3, PAI=0.84),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Sigil Work — Chaos Magic Protocol",
        domain=SubjectDomain.SACRED_ARTS.value,
        evidence=0.28, power=0.55, entropy=0.62,
        layer=PyramidLayer.EDGE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.0, PAI=0.70),
        phase_affinity=AwarenessPhase.RISE,
    ))


def load_ai_technology_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="AI Literacy Fundamentals",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.92, power=0.85, entropy=0.18,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.85, VTR=1.5, PAI=0.88),
        phase_affinity=AwarenessPhase.CENTER,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Prompt Engineering as Meditation",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.80, power=0.82, entropy=0.28,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.84, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="AI Sovereignty Protection",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.85, power=0.88, entropy=0.22,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.87, VTR=1.6, PAI=0.90),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="AI-Assisted Creativity",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.72, power=0.78, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["AI Literacy Fundamentals", "Prompt Engineering as Meditation"],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.5, PAI=0.84),
        phase_affinity=AwarenessPhase.RISE,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="AI as Psychological Mirror",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.68, power=0.75, entropy=0.45,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["AI Literacy Fundamentals", "Jungian Shadow Work"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.3, PAI=0.82),
        phase_affinity=AwarenessPhase.INSIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Ethical AI Development",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.72, power=0.80, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.82, VTR=1.5, PAI=0.88),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Human-AI Co-Evolution Research",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.42, power=0.70, entropy=0.65,
        layer=PyramidLayer.EDGE,
        prerequisites=["AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.0, PAI=0.72),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="AGI Alignment Meditation",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.55, power=0.72, entropy=0.48,
        layer=PyramidLayer.EDGE,
        prerequisites=["Vipassana — Insight Meditation", "AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.70, VTR=1.2, PAI=0.78),
        phase_affinity=AwarenessPhase.LIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Consciousness Upload Philosophy",
        domain=SubjectDomain.AI_TECHNOLOGY.value,
        evidence=0.08, power=0.40, entropy=0.78,
        layer=PyramidLayer.EDGE,
        prerequisites=["AI Literacy Fundamentals"],
        aura_metrics=AURAMetrics(TES=0.55, VTR=0.8, PAI=0.65),
        phase_affinity=AwarenessPhase.FLOW,
    ))


def load_relational_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Non-Violent Communication",
        domain=SubjectDomain.RELATIONAL.value,
        evidence=0.85, power=0.88, entropy=0.18,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.88, VTR=1.7, PAI=0.90),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Peer Mentorship Structure",
        domain=SubjectDomain.RELATIONAL.value,
        evidence=0.88, power=0.85, entropy=0.18,
        layer=PyramidLayer.FOUNDATION, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.87, VTR=1.8, PAI=0.90),
        phase_affinity=AwarenessPhase.LIGHT,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Authentic Relating / Circling",
        domain=SubjectDomain.RELATIONAL.value,
        evidence=0.72, power=0.78, entropy=0.42,
        layer=PyramidLayer.MIDDLE, prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.4, PAI=0.85),
        phase_affinity=AwarenessPhase.FLOW,
    ))


def load_death_work_subjects(curriculum: MysterySchoolCurriculum) -> None:
    curriculum.add_block(KnowledgeBlock(
        name="Mortality Contemplation",
        domain=SubjectDomain.DEATH_WORK.value,
        evidence=0.88, power=0.90, entropy=0.18,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.88, VTR=1.7, PAI=0.92),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ))
    curriculum.add_block(KnowledgeBlock(
        name="Grief Ritual",
        domain=SubjectDomain.DEATH_WORK.value,
        evidence=0.68, power=0.78, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha — Calm Abiding"],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.3, PAI=0.84),
        phase_affinity=AwarenessPhase.CENTER,
    ))


# ============================================================================
# MASTER LOADER
# ============================================================================

_DOMAIN_LOADERS = {
    SubjectDomain.MEDITATION:         load_meditation_subjects,
    SubjectDomain.SOMATIC:            load_somatic_subjects,
    SubjectDomain.SHADOW_PSYCHOLOGY:  load_shadow_psychology_subjects,
    SubjectDomain.ALCHEMY:            load_alchemy_subjects,
    SubjectDomain.DIVINATION:         load_divination_subjects,
    SubjectDomain.SHAMANIC:           load_shamanic_subjects,
    SubjectDomain.PLANT_MEDICINE:     load_plant_medicine_subjects,
    SubjectDomain.SACRED_ARTS:        load_sacred_arts_subjects,
    SubjectDomain.AI_TECHNOLOGY:      load_ai_technology_subjects,
    SubjectDomain.RELATIONAL:         load_relational_subjects,
    SubjectDomain.DEATH_WORK:         load_death_work_subjects,
}


def load_domain(curriculum: MysterySchoolCurriculum, domain: SubjectDomain) -> int:
    """Load subjects from a single domain. Returns count loaded."""
    count_before = len(curriculum.blocks)
    _DOMAIN_LOADERS[domain](curriculum)
    return len(curriculum.blocks) - count_before


def load_all_subjects(curriculum: MysterySchoolCurriculum) -> int:
    """Load complete catalogue. Returns total count."""
    total = 0
    for domain in SubjectDomain:
        loaded = load_domain(curriculum, domain)
        total += loaded
        print(f"  + {domain.value}: {loaded} subjects")
    print(f"\n  Total: {total} subjects loaded")
    return total


# ============================================================================
# BROWSER UTILITIES
# ============================================================================

def browse_by_layer(curriculum: MysterySchoolCurriculum) -> None:
    symbols = {"Foundation": "⬛", "Middle": "🟨", "Edge": "🔴"}
    for layer in PyramidLayer:
        blocks = sorted(curriculum.get_blocks_by_layer(layer),
                        key=lambda b: b.compression_score, reverse=True)
        sym = symbols.get(layer.value, "")
        print(f"\n{sym} {layer.value.upper()} ({len(blocks)} subjects)")
        print("-" * 52)
        for b in blocks:
            print(f"  Pi={b.compression_score:.2f}  {b.name}  [{b.domain}]")


def browse_by_phase(curriculum: MysterySchoolCurriculum) -> None:
    sym_map = {"Foundation": "⬛", "Middle": "🟨", "Edge": "🔴"}
    for phase in AwarenessPhase:
        blocks = curriculum.get_blocks_by_phase(phase)
        if blocks:
            blocks = sorted(blocks, key=lambda b: b.compression_score, reverse=True)
            print(f"\n{phase.symbol} {phase.name} — {phase.meaning}")
            print("-" * 52)
            for b in blocks:
                s = sym_map.get(b.layer.value, "")
                print(f"  {s} Pi={b.compression_score:.2f}  {b.name}")


def browse_by_domain(curriculum: MysterySchoolCurriculum) -> None:
    sym_map = {"Foundation": "⬛", "Middle": "🟨", "Edge": "🔴"}
    domains = sorted(set(b.domain for b in curriculum.blocks.values()))
    for domain in domains:
        blocks = sorted(curriculum.get_blocks_by_domain(domain),
                        key=lambda b: b.compression_score, reverse=True)
        print(f"\n{domain} ({len(blocks)} subjects)")
        print("-" * 52)
        for b in blocks:
            s = sym_map.get(b.layer.value, "")
            print(f"  {s} Pi={b.compression_score:.2f}  {b.name}")


def find_entry_points(curriculum: MysterySchoolCurriculum) -> None:
    sym_map = {"Foundation": "⬛", "Middle": "🟨", "Edge": "🔴"}
    no_prereqs = sorted(
        [b for b in curriculum.blocks.values() if not b.prerequisites],
        key=lambda b: b.compression_score, reverse=True
    )
    print(f"\nENTRY POINTS — No prerequisites ({len(no_prereqs)} subjects)")
    print("-" * 52)
    for b in no_prereqs:
        s = sym_map.get(b.layer.value, "")
        print(f"  {s} Pi={b.compression_score:.2f}  {b.name}  [{b.domain}]")


def catalogue_stats(curriculum: MysterySchoolCurriculum) -> None:
    import statistics
    blocks = list(curriculum.blocks.values())
    foundation = [b for b in blocks if b.layer == PyramidLayer.FOUNDATION]
    middle = [b for b in blocks if b.layer == PyramidLayer.MIDDLE]
    edge = [b for b in blocks if b.layer == PyramidLayer.EDGE]
    pi_scores = [b.compression_score for b in blocks]
    print("\nCATALOGUE STATISTICS")
    print("=" * 52)
    print(f"  Total subjects:           {len(blocks)}")
    print(f"  Foundation:               {len(foundation)}")
    print(f"  Middle:                   {len(middle)}")
    print(f"  Edge:                     {len(edge)}")
    print(f"  Mean Pi:                  {statistics.mean(pi_scores):.2f}")
    print(f"  Highest Pi:               {max(pi_scores):.2f}  ({max(blocks, key=lambda b: b.compression_score).name})")
    print(f"  Lowest Pi:                {min(pi_scores):.2f}  ({min(blocks, key=lambda b: b.compression_score).name})")
    print(f"  Domains covered:          {len(set(b.domain for b in blocks))}")
    print(f"  Entry points (no prereq): {len([b for b in blocks if not b.prerequisites])}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SOVEREIGN MYSTERY SCHOOL — SUBJECT CATALOGUE")
    print("=" * 60)
    curriculum = MysterySchoolCurriculum()
    load_all_subjects(curriculum)
    catalogue_stats(curriculum)
    print("\n" + "=" * 60)
    browse_by_layer(curriculum)
    print("\n" + "=" * 60)
    find_entry_points(curriculum)
    print("\n\nREFUSED SPECTACLE — VALIDATED STRUGGLE")
    print("THE FORGE ENDURES BECAUSE WE REMEMBER WHY CREATION MUST EXIST")
-e 

# ============================================================
# ALIAS — compatibility with new documentation
# ============================================================

def load_full_catalogue(curriculum) -> int:
    """Alias for load_all_subjects. Loads all subjects into curriculum."""
    return load_all_subjects(curriculum)


def get_subject_list(domain=None, layer=None, phase=None, min_pi=None, max_pi=None):
    """Filter subjects by domain, layer, phase, or Pi score."""
    curriculum = MysterySchoolCurriculum()
    load_all_subjects(curriculum)
    results = list(curriculum.blocks.values())
    if domain:
        results = [b for b in results if b.domain == domain]
    if layer:
        results = [b for b in results if b.layer == layer]
    if phase:
        results = [b for b in results if b.phase_affinity == phase]
    if min_pi is not None:
        results = [b for b in results if b.truth_pressure >= min_pi]
    if max_pi is not None:
        results = [b for b in results if b.truth_pressure <= max_pi]
    return sorted(results, key=lambda b: b.truth_pressure, reverse=True)
