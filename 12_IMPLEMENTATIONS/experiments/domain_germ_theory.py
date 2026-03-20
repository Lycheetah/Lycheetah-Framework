"""
Domain Dataset: Miasma → Germ Theory of Disease (1546–1905)
============================================================

Historical paradigm shift where germ theory contextualized (not deleted)
miasma theory. Sanitation still works — the mechanism changed.

All evidence scores are judgment-based encodings of historical evidence quality.
This is stated explicitly: the experiment tests CASCADE's structural behavior,
not the precision of our evidence scoring.
"""

from core.cascade_engine import KnowledgeBlock, DomainExperiment, CascadeEngine
from typing import List, Tuple


def build_blocks() -> List[KnowledgeBlock]:
    blocks = []
    
    # ── MIASMA ERA ──
    
    blocks.append(KnowledgeBlock(
        id="M1_miasma_core",
        content="Disease is caused by 'bad air' (miasma) from rotting organic matter",
        domain="disease_causation",
        paradigm="miasma",
        year=1546,
        evidence_strength=0.65,
        explanatory_power=2.0,
        uncertainty=0.55,
        key_figure="Girolamo Fracastoro / miasma tradition",
        note="Dominant for centuries. Explained clustering near swamps and slums.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="M2_sanitation_prevents",
        content="Improving sanitation and removing foul odors prevents disease outbreaks",
        domain="prevention",
        paradigm="miasma",
        year=1750,
        evidence_strength=0.70,
        explanatory_power=1.8,
        uncertainty=0.50,
        key_figure="Public health reformers",
        note="Partially correct — sanitation DOES reduce disease, but via germ reduction.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="M3_cholera_miasma",
        content="Cholera is caused by miasma from contaminated soil and air",
        domain="cholera_causation",
        paradigm="miasma",
        year=1831,
        evidence_strength=0.55,
        explanatory_power=1.5,
        uncertainty=0.60,
        key_figure="Edwin Chadwick / William Farr",
        note="Chadwick's 1842 sanitary report. Hugely influential.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="M4_treatment_purify_air",
        content="Disease treatment involves purifying air and removing sources of bad smell",
        domain="treatment",
        paradigm="miasma",
        year=1800,
        evidence_strength=0.45,
        explanatory_power=1.3,
        uncertainty=0.65,
        key_figure="Various physicians",
        note="Some efficacy through indirect pathogen reduction.",
    ))
    
    # ── EARLY GERM EVIDENCE ──
    
    blocks.append(KnowledgeBlock(
        id="G1_semmelweis",
        content="Handwashing with chlorine dramatically reduces childbed fever mortality",
        domain="prevention",
        paradigm="germ",
        year=1847,
        evidence_strength=0.80,
        explanatory_power=1.6,
        uncertainty=0.30,
        key_figure="Ignaz Semmelweis",
        note="Mortality 18% → 2%. Rejected for decades. Strong but narrow evidence.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G2_snow_cholera",
        content="Cholera is transmitted through contaminated water, not air",
        domain="cholera_causation",
        paradigm="germ",
        year=1854,
        evidence_strength=0.82,
        explanatory_power=1.7,
        uncertainty=0.25,
        key_figure="John Snow",
        note="Broad Street pump. Mapped cases. Epidemiological masterwork.",
    ))
    
    # ── GERM THEORY ASCENDANT ──
    
    blocks.append(KnowledgeBlock(
        id="G3_pasteur_micro",
        content="Microorganisms cause fermentation and putrefaction, not spontaneous generation",
        domain="microbiology",
        paradigm="germ",
        year=1861,
        evidence_strength=0.88,
        explanatory_power=2.2,
        uncertainty=0.18,
        key_figure="Louis Pasteur",
        note="Swan-neck flask experiments. Demolished spontaneous generation.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G4_pasteur_disease",
        content="Specific microorganisms cause specific diseases",
        domain="disease_causation",
        paradigm="germ",
        year=1865,
        evidence_strength=0.90,
        explanatory_power=2.5,
        uncertainty=0.15,
        key_figure="Louis Pasteur",
        note="Silkworm disease, then anthrax, rabies. Each traced to specific pathogen.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G5_lister_antiseptic",
        content="Antiseptic surgery prevents wound infection by killing microorganisms",
        domain="treatment",
        paradigm="germ",
        year=1867,
        evidence_strength=0.85,
        explanatory_power=2.0,
        uncertainty=0.20,
        key_figure="Joseph Lister",
        note="Surgical mortality plummeted. Direct practical proof.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G6_koch_postulates",
        content="Disease causation proven by: isolate, culture, reproduce, re-isolate",
        domain="disease_causation",
        paradigm="germ",
        year=1876,
        evidence_strength=0.92,
        explanatory_power=2.8,
        uncertainty=0.12,
        key_figure="Robert Koch",
        note="Koch's postulates. Gold standard. Anthrax, TB, cholera all confirmed.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G7_koch_tb",
        content="Tuberculosis caused by Mycobacterium tuberculosis",
        domain="tuberculosis",
        paradigm="germ",
        year=1882,
        evidence_strength=0.95,
        explanatory_power=2.3,
        uncertainty=0.10,
        key_figure="Robert Koch",
        note="Nobel Prize 1905. Isolated bacillus, fulfilled own postulates.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G8_vaccination",
        content="Vaccination creates immunity by exposing immune system to weakened pathogens",
        domain="prevention",
        paradigm="germ",
        year=1885,
        evidence_strength=0.88,
        explanatory_power=2.4,
        uncertainty=0.15,
        key_figure="Louis Pasteur",
        note="Rabies vaccine. Explained WHY Jenner's smallpox vaccine worked.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G9_cholera_vibrio",
        content="Cholera caused by Vibrio cholerae transmitted through contaminated water",
        domain="cholera_causation",
        paradigm="germ",
        year=1884,
        evidence_strength=0.93,
        explanatory_power=2.5,
        uncertainty=0.10,
        key_figure="Robert Koch",
        note="Confirmed Snow's hypothesis with causal mechanism.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="G10_sanitation_mechanism",
        content="Sanitation prevents disease by reducing pathogen exposure, not by removing bad air",
        domain="prevention_mechanism",
        paradigm="germ",
        year=1890,
        evidence_strength=0.90,
        explanatory_power=2.6,
        uncertainty=0.12,
        key_figure="Public health scientists",
        note="KEY: Recontextualizes miasma. Sanitation works via germ reduction.",
    ))
    
    return blocks


def build_fidelity_checks():
    """Checks that CASCADE's output matches historical reality."""
    
    def check_koch_top(engine: CascadeEngine) -> Tuple[bool, str]:
        foundations = engine.foundations()
        if not foundations:
            return False, "Koch at apex: no foundations"
        top = max(foundations, key=lambda b: b.truth_pressure)
        ok = "koch" in top.key_figure.lower() or "koch" in top.id.lower()
        return ok, f"Koch's work at apex: {top.id} (Π={top.truth_pressure:.2f})"
    
    def check_miasma_contextualized(engine: CascadeEngine) -> Tuple[bool, str]:
        m1 = engine.blocks.get("M1_miasma_core")
        if not m1:
            return False, "Miasma core not found"
        ok = m1.regime == "qualified"
        return ok, f"Miasma core contextualized: regime={m1.regime}"
    
    def check_all_preserved(engine: CascadeEngine) -> Tuple[bool, str]:
        miasma = [b for b in engine.blocks.values() if b.paradigm == "miasma"]
        ok = len(miasma) == 4
        return ok, f"All miasma blocks preserved: {len(miasma)}/4"
    
    def check_germ_foundations(engine: CascadeEngine) -> Tuple[bool, str]:
        gf = [b for b in engine.foundations() if b.paradigm == "germ"]
        ok = len(gf) > 0
        return ok, f"Germ theory in foundations: {len(gf)} blocks"
    
    def check_no_contradictions(engine: CascadeEngine) -> Tuple[bool, str]:
        c = engine.coherence()
        ok = c == 1.0
        return ok, f"Zero active contradictions: C={c:.4f}"
    
    return [check_koch_top, check_miasma_contextualized, check_all_preserved,
            check_germ_foundations, check_no_contradictions]


def create_experiment() -> DomainExperiment:
    return DomainExperiment(
        domain_name="Miasma → Germ Theory (1546–1905)",
        blocks=build_blocks(),
        old_paradigm="miasma",
        new_paradigm="germ",
        fidelity_checks=build_fidelity_checks(),
    )
