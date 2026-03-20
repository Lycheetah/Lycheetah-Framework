"""
Domain Dataset: Classical → Quantum Mechanics (1687–1928)
==========================================================

The canonical paradigm shift. Classical mechanics wasn't wrong — it was
contextualized as a macroscopic approximation. Quantum mechanics became
foundational, but Newton's laws remain valid in their domain.

Evidence scores reflect:
- Experimental precision available at time of discovery
- Range of phenomena explained
- Reproducibility and independent confirmation

Same caveat as germ theory: these are informed judgments, not measurements.
The experiment tests CASCADE's structural behavior on real knowledge claims.
"""

from core.cascade_engine import KnowledgeBlock, DomainExperiment, CascadeEngine
from typing import List, Tuple


def build_blocks() -> List[KnowledgeBlock]:
    blocks = []
    
    # ── CLASSICAL FOUNDATIONS (1687–1870) ──
    
    blocks.append(KnowledgeBlock(
        id="C1_newton_laws",
        content="Motion governed by F=ma; deterministic trajectories from initial conditions",
        domain="mechanics",
        paradigm="classical",
        year=1687,
        evidence_strength=0.85,
        explanatory_power=2.5,
        uncertainty=0.30,
        key_figure="Isaac Newton",
        note="Principia. Explained planetary motion, tides, projectiles. Spectacular success.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="C2_determinism",
        content="Given complete initial conditions, all future states are fully determined",
        domain="determinism",
        paradigm="classical",
        year=1814,
        evidence_strength=0.70,
        explanatory_power=2.0,
        uncertainty=0.40,
        key_figure="Pierre-Simon Laplace",
        note="Laplace's demon. Philosophical backbone of classical physics.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="C3_continuous_energy",
        content="Energy is continuous and can take any value; no minimum energy packet",
        domain="energy_nature",
        paradigm="classical",
        year=1850,
        evidence_strength=0.75,
        explanatory_power=2.0,
        uncertainty=0.35,
        key_figure="Classical thermodynamics tradition",
        note="Implicit assumption. Works for macroscopic systems.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="C4_wave_theory_light",
        content="Light is a continuous electromagnetic wave described by Maxwell's equations",
        domain="light_nature",
        paradigm="classical",
        year=1865,
        evidence_strength=0.88,
        explanatory_power=2.3,
        uncertainty=0.25,
        key_figure="James Clerk Maxwell",
        note="Maxwell's equations. Unified electricity, magnetism, optics. Predicted EM waves.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="C5_classical_radiation",
        content="Heated objects emit radiation according to classical equipartition of energy",
        domain="radiation",
        paradigm="classical",
        year=1860,
        evidence_strength=0.60,
        explanatory_power=1.5,
        uncertainty=0.50,
        key_figure="Rayleigh / Jeans",
        note="Rayleigh-Jeans law. Works at low frequencies, catastrophically wrong at high (UV catastrophe).",
    ))
    
    blocks.append(KnowledgeBlock(
        id="C6_classical_atom",
        content="Atoms are stable structures governed by classical orbital mechanics",
        domain="atomic_structure",
        paradigm="classical",
        year=1870,
        evidence_strength=0.50,
        explanatory_power=1.4,
        uncertainty=0.55,
        key_figure="Various (pre-quantum)",
        note="Couldn't explain why orbiting electrons don't radiate and spiral into nucleus.",
    ))
    
    # ── QUANTUM REVOLUTION (1900–1928) ──
    
    blocks.append(KnowledgeBlock(
        id="Q1_planck_quanta",
        content="Energy is emitted and absorbed in discrete quanta E=hν, not continuously",
        domain="energy_nature",
        paradigm="quantum",
        year=1900,
        evidence_strength=0.85,
        explanatory_power=2.2,
        uncertainty=0.18,
        key_figure="Max Planck",
        note="Solved UV catastrophe. 'An act of desperation' — Planck didn't fully believe it at first.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q2_photoelectric",
        content="Light consists of particle-like photons; energy transfer is quantized (E=hν)",
        domain="light_nature",
        paradigm="quantum",
        year=1905,
        evidence_strength=0.88,
        explanatory_power=2.3,
        uncertainty=0.15,
        key_figure="Albert Einstein",
        note="Explained photoelectric effect. Nobel Prize 1921. Light is BOTH wave and particle.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q3_bohr_atom",
        content="Electrons occupy discrete energy levels; transitions emit/absorb specific frequencies",
        domain="atomic_structure",
        paradigm="quantum",
        year=1913,
        evidence_strength=0.82,
        explanatory_power=2.0,
        uncertainty=0.22,
        key_figure="Niels Bohr",
        note="Explained hydrogen spectrum exactly. Only approximate for heavier atoms.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q4_compton",
        content="X-rays scatter off electrons as particles with definite momentum (p=h/λ)",
        domain="radiation",
        paradigm="quantum",
        year=1923,
        evidence_strength=0.90,
        explanatory_power=2.1,
        uncertainty=0.14,
        key_figure="Arthur Compton",
        note="Compton scattering. Proved photon has particle-like momentum. Nobel Prize 1927.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q5_debroglie_waves",
        content="All matter has wave-like properties with wavelength λ=h/p",
        domain="mechanics",
        paradigm="quantum",
        year=1924,
        evidence_strength=0.80,
        explanatory_power=2.4,
        uncertainty=0.22,
        key_figure="Louis de Broglie",
        note="Matter waves. Confirmed by Davisson-Germer electron diffraction (1927). Nobel 1929.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q6_schrodinger",
        content="Quantum states evolve via wave equation iℏ∂ψ/∂t = Ĥψ; outcomes are probabilistic",
        domain="mechanics",
        paradigm="quantum",
        year=1926,
        evidence_strength=0.92,
        explanatory_power=2.8,
        uncertainty=0.12,
        key_figure="Erwin Schrödinger",
        note="Schrödinger equation. Reproduces all atomic spectra. Foundation of quantum mechanics.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q7_heisenberg_uncertainty",
        content="Position and momentum cannot both be precisely known: ΔxΔp ≥ ℏ/2",
        domain="determinism",
        paradigm="quantum",
        year=1927,
        evidence_strength=0.90,
        explanatory_power=2.5,
        uncertainty=0.12,
        key_figure="Werner Heisenberg",
        note="Uncertainty principle. Fundamental limit, not measurement imprecision. End of determinism.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q8_dirac_equation",
        content="Relativistic quantum mechanics predicts antimatter and electron spin",
        domain="atomic_structure",
        paradigm="quantum",
        year=1928,
        evidence_strength=0.93,
        explanatory_power=2.7,
        uncertainty=0.10,
        key_figure="Paul Dirac",
        note="Predicted positron (found 1932). Unified quantum mechanics with special relativity.",
    ))
    
    blocks.append(KnowledgeBlock(
        id="Q9_correspondence",
        content="Classical mechanics emerges as macroscopic limit of quantum mechanics (ℏ→0)",
        domain="mechanics_limit",
        paradigm="quantum",
        year=1925,
        evidence_strength=0.88,
        explanatory_power=2.6,
        uncertainty=0.15,
        key_figure="Niels Bohr / Ehrenfest",
        note="Correspondence principle. Classical physics isn't wrong — it's the macroscopic approximation.",
    ))
    
    return blocks


def build_fidelity_checks():
    """Checks that CASCADE's output matches physics history."""
    
    def check_schrodinger_foundational(engine: CascadeEngine) -> Tuple[bool, str]:
        foundations = engine.foundations()
        schrodinger_ids = [b.id for b in foundations 
                          if "schrodinger" in b.id.lower() or "Q6" in b.id]
        ok = len(schrodinger_ids) > 0
        return ok, f"Schrödinger equation foundational: {bool(schrodinger_ids)}"
    
    def check_newton_contextualized(engine: CascadeEngine) -> Tuple[bool, str]:
        c1 = engine.blocks.get("C1_newton_laws")
        if not c1:
            return False, "Newton's laws not found"
        ok = c1.regime == "qualified"
        return ok, f"Newton contextualized (not deleted): regime={c1.regime}"
    
    def check_all_classical_preserved(engine: CascadeEngine) -> Tuple[bool, str]:
        classical = [b for b in engine.blocks.values() if b.paradigm == "classical"]
        ok = len(classical) == 6
        return ok, f"All classical blocks preserved: {len(classical)}/6"
    
    def check_determinism_overturned(engine: CascadeEngine) -> Tuple[bool, str]:
        c2 = engine.blocks.get("C2_determinism")
        q7 = engine.blocks.get("Q7_heisenberg_uncertainty")
        if not c2 or not q7:
            return False, "Missing determinism or uncertainty blocks"
        ok = c2.regime == "qualified" and q7.regime == "universal"
        return ok, f"Determinism qualified, uncertainty universal: {ok}"
    
    def check_quantum_dominates_foundations(engine: CascadeEngine) -> Tuple[bool, str]:
        foundations = engine.foundations()
        qf = [b for b in foundations if b.paradigm == "quantum"]
        cf = [b for b in foundations if b.paradigm == "classical" and b.regime == "universal"]
        ok = len(qf) > len(cf)
        return ok, f"Quantum dominates foundations: {len(qf)} quantum vs {len(cf)} classical(universal)"
    
    def check_correspondence_present(engine: CascadeEngine) -> Tuple[bool, str]:
        q9 = engine.blocks.get("Q9_correspondence")
        if not q9:
            return False, "Correspondence principle not found"
        ok = q9.layer == "FOUNDATION"
        return ok, f"Correspondence principle foundational: layer={q9.layer}"
    
    def check_coherence(engine: CascadeEngine) -> Tuple[bool, str]:
        c = engine.coherence()
        ok = c == 1.0
        return ok, f"Zero contradictions: C={c:.4f}"
    
    return [check_schrodinger_foundational, check_newton_contextualized,
            check_all_classical_preserved, check_determinism_overturned,
            check_quantum_dominates_foundations, check_correspondence_present,
            check_coherence]


def create_experiment() -> DomainExperiment:
    return DomainExperiment(
        domain_name="Classical → Quantum Mechanics (1687–1928)",
        blocks=build_blocks(),
        old_paradigm="classical",
        new_paradigm="quantum",
        fidelity_checks=build_fidelity_checks(),
    )
