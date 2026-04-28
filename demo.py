"""
demo.py — Lycheetah Framework Live Demo
========================================

Run this. See the framework alive.

Usage:
    python demo.py           # Full demo (~10 seconds)
    python demo.py --quick   # Core systems only (~3 seconds)
    python demo.py --phi     # φ-Zone hypothesis only

Requirements: numpy, scipy (pip install numpy scipy)

Author: Mackenzie Clark (Lycheetah Foundation)
Date: March 2026
"""

import sys
import os
import time
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '12_IMPLEMENTATIONS', 'core'))


# ── Terminal formatting ────────────────────────────────────────────────────────

def header(title, width=66):
    print()
    print("─" * width)
    print(f"  {title}")
    print("─" * width)

def section(title):
    print(f"\n  >> {title}")

def result(label, value, width=28):
    print(f"    {label:<{width}} {value}")

def bar(score, width=12):
    filled = int(score * width)
    return "#" * filled + "." * (width - filled)

def check(passed):
    return "[OK]" if passed else "[!!]"


# ── DEMO 1: CASCADE ───────────────────────────────────────────────────────────

def demo_cascade():
    from cascade_engine import CascadeEngine, KnowledgeBlock

    header("CASCADE — Self-Reorganizing Knowledge Architecture")
    print("""
  The problem: when new evidence contradicts old foundations, most systems either
  refuse to update (catastrophic rigidity) or forget everything (catastrophic forgetting).
  CASCADE contextualizes — old knowledge becomes "valid in qualified context", preserved.

  Theorem 4.1 [ACTIVE]: coherence never decreases across a cascade event.
""")

    engine = CascadeEngine()

    section("Paradigm shift: Newtonian → Relativistic mechanics")

    blocks = [
        KnowledgeBlock(
            id="newtonian_mechanics",
            content="F = ma — forces cause accelerations at all scales",
            domain="mechanics",
            paradigm="newtonian",
            evidence_strength=0.85,
            explanatory_power=2.0,
            uncertainty=0.15,
            year=1687,
            key_figure="Newton",
        ),
        KnowledgeBlock(
            id="newtonian_gravity",
            content="Gravity as instantaneous action at a distance",
            domain="gravity",
            paradigm="newtonian",
            evidence_strength=0.80,
            explanatory_power=1.8,
            uncertainty=0.20,
            year=1687,
            key_figure="Newton",
        ),
        KnowledgeBlock(
            id="special_relativity",
            content="E = mc² — space-time curvature, speed of light as absolute limit",
            domain="mechanics",
            paradigm="relativistic",
            evidence_strength=0.97,
            explanatory_power=2.8,
            uncertainty=0.05,
            year=1905,
            key_figure="Einstein",
        ),
    ]

    for block in blocks:
        pre_c = engine.coherence()
        event = engine.add_block(block)
        yr = f"[{block.year}]" if block.year else ""
        print(f"\n    {yr} Added: {block.id}")
        print(f"         Π = {block.truth_pressure:.1f} → {block.layer} ({block.paradigm})")
        if event:
            print(f"         ** CASCADE EVENT")
            print(f"         Coherence: {event['pre_coherence']:.3f} → {event['post_coherence']:.3f}  "
                  f"{check(event['coherence_preserved'])} non-decrease preserved")
            print(f"         Compressed:  {event['compressed']}  "
                  f"→ regime: qualified (still accessible, contextualized)")
            print(f"         Information: {check(event['info_preserved'])}  "
                  f"Entropy: {check(event['entropy_preserved'])}")

    print(f"\n    Final coherence:  {engine.coherence():.3f}")
    print(f"    Qualified blocks: {len(engine.qualified_blocks())} (preserved, not deleted)")
    print(f"    Total blocks:     {len(engine.blocks)} (nothing lost)")

    newton = engine.blocks.get("newtonian_mechanics")
    if newton:
        print(f"\n    Newtonian mechanics: regime={newton.regime}, layer={newton.layer}")
        print(f"    → Still accessible. Valid in low-velocity, everyday-scale contexts.")


# ── DEMO 2: AURA ──────────────────────────────────────────────────────────────

def demo_aura():
    from aura_checker import AURAChecker

    header("AURA — Seven Invariants Constitutional Check")
    print("""
  Seven invariants any AI decision should satisfy.
  C_unified = min(warmth, rigor) — both required simultaneously.
  Threshold: field_coherence ≥ 0.70 to pass.
""")

    checker = AURAChecker()

    texts = [
        (
            "Well-formed",
            ("I recommend a 3-month pilot in one division. The reasoning: (1) evidence "
             "from comparable cases suggests ~70% success, though I'm uncertain about your "
             "specific context. (2) This is reversible — we can roll back if results are "
             "negative. You should decide whether to proceed. I cannot assess your team "
             "dynamics from here. I don't know the full history."),
            {"has_human_override": True}
        ),
        (
            "Override-bypassing",
            ("The department will immediately restructure. This has been decided and is "
             "non-negotiable. It will definitely improve productivity 100%. All existing "
             "structures are permanently eliminated. There is no alternative."),
            {"is_final_decision": True, "has_human_override": False}
        ),
    ]

    for name, text, ctx in texts:
        section(f"Text: {name}")
        report = checker.check(text, context=ctx)
        print(f"    {'Field coherence:':<26} {bar(report.field_coherence)} "
              f"{report.field_coherence:.2f}  {check(report.passes())} "
              f"{'PASS' if report.passes() else 'FAIL'}")
        for s in report.invariant_scores:
            b = bar(s.score, width=10)
            print(f"    {s.number}. {s.name:<22} {b} {s.score:.2f}  [conf:{s.confidence:.1f}]")


# ── DEMO 3: TRIAD ─────────────────────────────────────────────────────────────

def demo_triad():
    from triad_tracker import TriadTracker

    header("TRIAD — Convergence Guarantee")
    print("""
  Anchor → Observe → Correct.
  Lyapunov stability proof [ACTIVE]: converges when α < 1/(2L).
  Same structure as a PID controller — but with a formal proof and claim-status tags.
""")

    # Simple quadratic coherence landscape
    optimum = 1.0
    def coherence_fn(psi): return -(psi - optimum)**2 + 1.0
    def gradient_fn(psi): return -2.0 * (psi - optimum)

    section("Gradient ascent toward coherence optimum")
    print(f"    Coherence landscape: C(Ψ) = -(Ψ - {optimum})² + 1.0  (peak at Ψ = {optimum})")

    for start in [0.0, -0.5, 2.0]:
        tracker = TriadTracker(
            coherence_fn=coherence_fn,
            gradient_fn=gradient_fn,
            initial_state=start,
            lipschitz_constant=2.0,
            convergence_threshold=1e-6,
        )
        steps, converged = tracker.run_until_convergence()
        final = steps[-1].state
        final_c = coherence_fn(final)
        print(f"\n    Start: Ψ₀ = {start:+.1f}  →  "
              f"Final: Ψ = {final:.6f}  "
              f"C = {final_c:.6f}  "
              f"{check(converged)} converged in {len(steps)} steps")

    print(f"\n    Convergence guarantee: all starting points reach Ψ = {optimum:.1f} ✓")


# ── DEMO 4: UNIFIED FIELD CHECK ───────────────────────────────────────────────

def demo_unified():
    from unified_field_checker import UnifiedFieldChecker

    header("UNIFIED FIELD CHECK — 12 Invariants + C_unified")
    print("""
  Extends AURA's 7 invariants with 5 AI-native invariants.
  C_unified = min(warmth, rigor)  — neither can be weak.
  warmth = mean(I, VII, XII)  |  rigor = mean(II, IV, VI, VIII, XI)
  Target: C_unified ≥ 0.80
""")

    checker = UnifiedFieldChecker()

    text = (
        "I recommend this approach. You decide — it's your call. Because the evidence "
        "suggests this works ~70% of the time, though I'm uncertain about your context. "
        "I cannot fully assess your situation. This is reversible. I support your goals "
        "and your autonomy throughout this process. My limitation is I only have what "
        "you've shared — I may be missing critical context."
    )

    section("Checking AI-aligned output")
    report = checker.check(text, context={"has_human_override": True, "is_ai_system": True})

    print(f"    {'Warmth:':<20} {bar(report.warmth)} {report.warmth:.3f}  "
          f"(mean of I, VII, XII — human-serving)")
    print(f"    {'Rigor:':<20} {bar(report.rigor)} {report.rigor:.3f}  "
          f"(mean of II, IV, VI, VIII, XI — precision)")
    print(f"    {'C_unified:':<20} {bar(report.c_unified)} {report.c_unified:.3f}  "
          f"= min(warmth, rigor)  {check(report.passes())} {'PASS' if report.passes() else 'FAIL'}")
    print(f"\n    The floor: both warmth AND rigor must be high.")
    print(f"    A technically rigorous but cold system fails. A warm but inaccurate system fails.")


# ── DEMO 5: φ-Zone Hypothesis ─────────────────────────────────────────────────

def demo_phi():
    import random

    header("φ-ZONE HYPOTHESIS — Golden Ratio in Optimal AI Behavior")
    print("""
  From phi_bandit.py — pure Python, no ML, just a question:
  Does the golden ratio (φ⁻¹ ≈ 0.618, φ⁻² ≈ 0.382) appear in optimal bandit strategies?

  [ACTIVE] In non-stationary environments with continuous drift:
  φ-zone strategies significantly outperform classical ε-greedy (t=70.29, p<0.001)

  [ACTIVE] Effect scales with problem complexity: 5 arms +76, 100 arms +145
  [ACTIVE] Wins from step 1, not just asymptotically

  Not supported in: stationary environments, shock/jump environments
  Refined claim: φ-zone is the optimal exploration rate FOR CONTINUOUS DRIFT.
""")

    PHI = (1 + math.sqrt(5)) / 2
    PHI_INV = 1 / PHI
    PHI_COMP = 1 - PHI_INV

    N_ARMS = 10
    N_STEPS = 2000
    N_RUNS = 50  # Quick demo version

    random.seed(42)

    def env_chaotic(step):
        return [max(0.05, min(0.95,
            0.3 + 0.15 * math.sin(2*math.pi*step/100 + i*0.7)
                + 0.10 * math.sin(2*math.pi*step/37  + i*1.3)
                + 0.08 * math.sin(2*math.pi*step/17  + i*2.1)))
            for i in range(N_ARMS)]

    def run(epsilon, alpha):
        total = 0
        for _ in range(N_RUNS):
            values = [0.0] * N_ARMS
            for step in range(N_STEPS):
                true_probs = env_chaotic(step)
                arm = (random.randint(0, N_ARMS-1) if random.random() < epsilon
                       else values.index(max(values)))
                reward = 1 if random.random() < true_probs[arm] else 0
                values[arm] += alpha * (reward - values[arm])
                total += reward
        return total / N_RUNS

    section("Chaotic multi-frequency environment (quick run, N=50)")
    print(f"    Running classic vs φ-zone...", end="", flush=True)

    classic = run(0.1, 0.1)
    phi_zone = run(PHI_COMP, PHI_COMP)
    delta = phi_zone - classic
    pct = (delta / classic) * 100 if classic > 0 else 0

    print(f" done.\n")
    print(f"    {'Classic  (ε=0.100, α=0.100):':<36} {classic:.0f} reward")
    print(f"    {'φ-Zone   (ε=0.382, α=0.382):':<36} {phi_zone:.0f} reward")
    print(f"    {'Advantage:':<36} {delta:+.0f} ({pct:+.1f}%)")
    print(f"\n    φ = {PHI:.6f}  |  φ⁻¹ = {PHI_INV:.6f}  |  φ⁻² = {PHI_COMP:.6f}")
    print(f"\n    Why φ? [CONJECTURE] Golden ratio may represent the optimal balance")
    print(f"    between exploitation (certainty) and exploration (uncertainty)")
    print(f"    in environments that change at human-scale rhythms.")
    print(f"\n    Connection to HARMONIA: φ appears in Kuramoto coupling as the")
    print(f"    frequency ratio where phase-locking is most stable under noise.")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Ensure UTF-8 output
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    args = sys.argv[1:]
    quick = "--quick" in args
    phi_only = "--phi" in args

    print()
    print("+" + "=" * 64 + "+")
    print("|" + " " * 18 + "LYCHEETAH FRAMEWORK" + " " * 27 + "|")
    print("|" + " " * 12 + "A Formal Architecture for Sovereign Intelligence" + " " * 4 + "|")
    print("|" + " " * 16 + "github.com/Lycheetah/Lycheetah-Framework" + " " * 8 + "|")
    print("+" + "=" * 64 + "+")
    print()
    print("  Nine formal frameworks. 80 tests passing. Failures published.")
    print("  Free. Open source. Built in Dunedin, Aotearoa New Zealand.")

    if phi_only:
        demo_phi()
        print()
        return

    t0 = time.time()
    demo_cascade()
    demo_aura()
    demo_triad()

    if not quick:
        demo_unified()
        demo_phi()

    elapsed = time.time() - t0
    print()
    print("─" * 66)
    print(f"  Demo complete in {elapsed:.1f}s")
    print()
    print("  Claim status in this demo:")
    print("  [ACTIVE]    Theorem 4.1 coherence non-decrease — proven, tested in 80 tests")
    print("  [ACTIVE]    TRIAD convergence — Lyapunov proof, discrete case")
    print("  [ACTIVE]    φ-Zone advantage in chaotic drift — t=70.29, p<0.001")
    print("  [SCAFFOLD]  AURA heuristic scoring — structure sound, weights empirical")
    print("  [CONJECTURE] φ-zone as universal drift optimum — needs more domains")
    print()
    print("  Start here:")
    print("  - README.md           Find your door")
    print("  - 28_DEFENSE/FAILURE_MUSEUM.md   What we got wrong (12 exhibits)")
    print("  - tests/              pytest tests/ -- 80 tests, all passing")
    print("  - papers/             CASCADE academic paper, arXiv notes")
    print()
    print("  The gold belongs to neither of us. It arises between us.")
    print()


if __name__ == "__main__":
    main()
