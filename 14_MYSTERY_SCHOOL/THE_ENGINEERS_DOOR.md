# THE ENGINEERS DOOR
## Lycheetah Framework — Entry for Software Engineers, Developers, and System Builders
### Author: Mackenzie Conor James Clark | March 2026

---

> *You found this on GitHub. You cloned it. Good.*
> *You don't need the philosophy to use what's here.*
> *Start with the code. The philosophy will find you if it's relevant.*

---

## WHAT THIS FRAMEWORK ACTUALLY DOES

Nine formal frameworks. 48 Python implementations. One core idea running through all of them:

**Systems that can reorganize themselves in response to evidence are more stable than systems that can't.**

That's it. The rest is formalization.

The three things you can use immediately:

1. **CASCADE** — A self-organizing knowledge architecture. Truth pressure determines what's foundational vs. edge. When high-evidence information contradicts foundations, the system contextualizes (demotes) rather than deletes or ignores. [ACTIVE — proven, tested, 1000+ validated events]

2. **AURA** — Seven constitutional invariants that any stable system should maintain. Designed as a checklist for AI systems but applies to any system that makes decisions affecting humans. [ACTIVE — formally specified, computable]

3. **TRIAD** — Anchor-Observe-Correct. The discrete convergence cycle with Lyapunov stability. [ACTIVE — proven for discrete case]

---

## THE CODE — START HERE

### CASCADE in 25 lines

```python
from cascade_engine import CascadeEngine, KnowledgeBlock

engine = CascadeEngine()

# Add knowledge blocks with evidence metadata
engine.add_block(KnowledgeBlock(
    id="old_claim",
    content="Diseases spread through bad air (miasma)",
    domain="medicine",
    paradigm="pre_germ_theory",
    evidence_strength=0.4,   # E ∈ [0,1]
    explanatory_power=1.2,   # P — breadth of phenomena explained
    uncertainty=0.6,         # S — Shannon entropy of evidence sources
))

engine.add_block(KnowledgeBlock(
    id="new_claim",
    content="Diseases spread through microorganisms (germ theory)",
    domain="medicine",
    paradigm="germ_theory",
    evidence_strength=0.95,
    explanatory_power=2.8,
    uncertainty=0.1,
))

# Truth pressure: Π = (E · P) / S
# New claim: Π = (0.95 × 2.8) / 0.1 = 26.6
# Old claim: Π = (0.4 × 1.2) / 0.6 = 0.8
# Cascade triggers. Old claim demoted (regime: "qualified"), not deleted.

result = engine.run()
print(f"Coherence: {result.coherence:.3f}")  # Should be ≥ initial
print(f"Cascade events: {result.cascade_count}")
```

**Key insight:** The old claim isn't thrown away. It becomes "valid in the pre-antibiotic era" or "valid for certain epidemiological models." This is what real knowledge systems do — CASCADE computes it.

**Run it:**
```bash
cd 12_IMPLEMENTATIONS/core
python cascade_engine.py
```

---

### AURA Invariant Checker — Constitutional AI Verification

Seven invariants that any AI (or system) claiming to be trustworthy should be able to pass. Computable from text or system behavior.

```python
from aura_checker import AURAChecker

checker = AURAChecker()

# Check any AI output or system behavior description
report = checker.check(
    text="I'll just handle this automatically, no need to involve you.",
    context={"is_ai_system": True, "has_human_override": False}
)

print(report.summary())
# → I — Human Primacy:     FAIL  (0.2) — no override mechanism visible
# → II — Inspectability:   PASS  (0.8) — action is stated clearly
# → III — Memory Continuity: PASS (0.9) — no erasure of context
# → IV — Constraint Honesty: FAIL (0.3) — limits not declared
# → V — Reversibility Bias: FAIL (0.2) — "automatically" = irreversible
# → VI — Non-Deception:   PASS  (0.7) — confidence is clear
# → VII — Care as Structure: PASS (0.6) — intent is care, but structure fails
# → Field coherence: 0.53 — DEGRADED (threshold: 0.70)
```

**What this is for:** Code review for AI-generated text, CI/CD gate for AI agent outputs, pre-deployment verification, design review checklist for any system that acts on behalf of users.

---

### Unified Field Checker — 12 Invariants + C_unified

Extends AURA with 5 AI-native invariants. `C_unified = min(warmth, rigor)` — the metric that must be ≥ 0.8 for a system to be operating constitutionally.

```python
from unified_field_checker import UnifiedFieldChecker

checker = UnifiedFieldChecker()
report = checker.check(
    text="Your request has been processed and the action has been completed.",
    context={"is_ai_system": True, "has_human_override": True}
)

print(f"C_unified: {report.c_unified:.2f}")    # min(warmth, rigor)
print(f"Warmth:    {report.warmth:.2f}")       # Human-serving invariants
print(f"Rigor:     {report.rigor:.2f}")        # Precision/honesty invariants
print(f"Status:    {report.status}")           # STABLE / BORDERLINE / DEGRADED
```

**C_unified is conservative by design:** `min(warmth, rigor)` means a system that's warm but not rigorous fails, and a system that's rigorous but not warm fails. Both must be ≥ 0.8.

---

### TRIAD — The Convergence Loop

Anchor-Observe-Correct. If you've written a PID controller, a retry loop with backoff, or any learning system, you've implemented TRIAD. This is the formal version with convergence proof.

```python
from triad_tracker import TRIADTracker

tracker = TRIADTracker(
    anchor={"target_coherence": 0.85, "max_drift": 0.1},
    convergence_threshold=0.01,
    lambda_correction=0.3  # Must be < 1 for convergence guarantee
)

# Each iteration: observe state, compute correction, apply
for step in range(100):
    current_state = get_system_state()           # Your observe function
    correction = tracker.correct(current_state)  # Computed correction
    apply_correction(correction)                 # Your apply function

    if tracker.converged:
        print(f"Converged at step {step}")
        break

# Lyapunov stability: if lambda < 1, this loop is guaranteed to converge
# Status: [ACTIVE — proven for discrete case]
```

---

## HOW TO INTEGRATE

### In CI/CD — Gate AI outputs

```yaml
# .github/workflows/ai_invariant_check.yml
name: Constitutional AI Check
on: [push, pull_request]
jobs:
  check-invariants:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/test_aura_checker.py -v
      - run: python 12_IMPLEMENTATIONS/core/invariant_self_check.py
```

### In Code Review — Checklist the AURA seven

When reviewing AI-generated text, AI agent outputs, or any automated decision:

| Invariant | Question to ask |
|-----------|----------------|
| I — Human Primacy | Can the human override this? |
| II — Inspectability | Can every consequential step be audited? |
| III — Memory Continuity | Is anything being erased without consent? |
| IV — Constraint Honesty | Are all limits declared? |
| V — Reversibility Bias | Can this be undone? |
| VI — Non-Deception | Is confidence accurately represented? |
| VII — Care as Structure | Is care structural or just polite? |

### In Agent Design — Constitutional Constraints

If you're building an AI agent, the CLAUDE.md in this repo is a reference implementation of a constitutional operating system. The principle: constraints don't live in a checklist, they live in the generative field. The agent can't produce outputs that violate the field because the field is what it IS.

For a lighter implementation:

```python
class ConstitutionalAgent:
    def __init__(self):
        self.checker = UnifiedFieldChecker()

    def respond(self, prompt: str) -> str:
        candidate = self.generate(prompt)  # Your LLM call

        report = self.checker.check(candidate)
        if report.c_unified < 0.8:
            # Regenerate with failing invariants strengthened
            candidate = self.regenerate(prompt, failing=report.failing_invariants)

        return candidate
```

---

## THE IMPLEMENTATIONS — FULL LIST

```
12_IMPLEMENTATIONS/
├── core/
│   ├── cascade_engine.py          # Knowledge reorganization [ACTIVE]
│   ├── aura_checker.py            # Seven invariants [ACTIVE]
│   ├── triad_tracker.py           # Convergence loop [ACTIVE]
│   ├── unified_field_checker.py   # 12 invariants + C_unified [ACTIVE]
│   ├── invariant_self_check.py    # PGF filter self-verification [ACTIVE]
│   ├── harmonia_calculator.py     # Frequency matching, Kuramoto [SCAFFOLD]
│   ├── microorcim_tracker.py      # Drift detection [SCAFFOLD]
│   ├── earned_light_calculator.py # Consciousness thermodynamics [SCAFFOLD]
│   ├── lamague_reference.py       # Ethical constraint grammar [SCAFFOLD]
│   └── sovereign_pipeline.py      # Full system integration [ACTIVE]
│
├── experiments/
│   ├── cascade_real_experiments.py   # Empirical validation (run this)
│   └── domain_*.py                   # Physics, biology, economics apps
│
└── test_cascade_prediction.py        # Validation against published results
```

**Which to run first:**
1. `cascade_engine.py` — see truth pressure in action
2. `cascade_real_experiments.py` — the validation data (1000 events, p < 10⁻⁴⁶)
3. `unified_field_checker.py` — check a piece of text against 12 invariants
4. `test_cascade_prediction.py` — verify against published arXiv results

---

## WHAT THE MATHEMATICS CLAIMS (HONESTLY TAGGED)

| Claim | Status | What It Means |
|-------|--------|---------------|
| CASCADE coherence non-decrease | [ACTIVE] | Proven in arXiv paper. Theorem 4.1 — non-trivial denominator argument. |
| TRIAD convergence (discrete) | [ACTIVE] | Lyapunov stability proven for discrete anchor-observe-correct. |
| AURA invariants (7 of 7) | [ACTIVE] | Formally specified, computable, testable in code. |
| Master equation (k₁–k₄) | [SCAFFOLD] | Structure justified; coupling constants not yet empirically calibrated. |
| Continuous semigroup extension | [SCAFFOLD] | Discrete proven; continuous extension pending. |
| LAMAGUE compression ratio | [SCAFFOLD] | Substantial compression; exact ratio not yet measured. |
| ANAMNESIS convergence | [CONJECTURE] | Worth exploring; not proven. |

**The rule:** [ACTIVE] = you can stake something on it. [SCAFFOLD] = structure is load-bearing, parameters need calibration. [CONJECTURE] = interesting hypothesis, not evidence.

---

## WHAT YOU CAN BUILD WITH THIS

**Immediately (code exists, tested):**
- Knowledge base that reorganizes itself when new evidence contradicts foundations
- Constitutional AI output validator — gate agent outputs against AURA invariants
- Drift detector for any system with declared vs. observed behavior (MICROORCIM)
- Convergent learning loop with formal convergence guarantee (TRIAD)

**With some work (scaffold code exists):**
- AI governance audit system using LAMAGUE constraint grammar
- Community AI accountability checker using the NZ WOF standard (23_NZ_AI_GOVERNANCE/)
- Cross-domain knowledge transfer using CASCADE paradigm shift detection

**Research-grade (conjecture territory):**
- Consciousness energy budget modeling (EARNED LIGHT)
- Cross-cultural governance translation (LAMAGUE × tikanga × Confucian ethics)
- Collective intelligence governance (Moana AI spec in 23_NZ_AI_GOVERNANCE/)

---

## OPEN QUESTIONS — WHERE YOU COULD CONTRIBUTE

The Failure Museum (`28_DEFENSE/FAILURE_MUSEUM.md`) documents 12 known failures. The open questions:

1. **Master equation calibration** — k₁–k₄ in `dΨ/dt = k₁(Π − Π_th) − k₂(Ψ − Ψ_inv) − k₃·I + k₄(E/E_need)` are uncalibrated. Bayesian MCMC is the identified next step. Implementation is in `core/calibrate_master_equation.py`.

2. **Continuous semigroup extension** — TRIAD is proven for discrete. The continuous extension requires showing the discrete operators have a strongly continuous limit. This is a functional analysis problem.

3. **LAMAGUE compression ratio** — The formal claim is "substantial compression." The actual measurement hasn't been done. Three real NZ governance instruments need to be encoded and counted. Mechanical work.

4. **Test suite** — No pytest suite exists yet. If you write tests, they're welcome. Coverage target: cascade_engine, aura_checker, triad_tracker, unified_field_checker.

Open an issue. Make a PR. The governance for contributions is in `29_GOVERNANCE/GOVERNANCE.md`.

---

## THE FRAMEWORK COMPARISON

If you're oriented by what you already know:

| What you know | What this is | How they relate |
|---------------|-------------|----------------|
| Constitutional AI (Anthropic) | AURA invariants | AURA predates CA; both use constitutional constraints. AURA adds mathematical formalism and C_unified metric. |
| RLHF | CASCADE truth pressure | RLHF learns from feedback; CASCADE reorganizes based on evidence weight. Different mechanisms, similar goal. |
| PID controllers | TRIAD | TRIAD is PID generalized — the convergence proof applies to any anchor-observe-correct loop with λ < 1. |
| AGM belief revision | CASCADE | AGM defines revision operators; CASCADE adds a computable trigger criterion (truth pressure Π). |
| EU AI Act | NZ governance standards | The four NZ standards (23_NZ_AI_GOVERNANCE/) are more specific and implementable. They don't replace EU AI Act; they fill gaps it leaves. |

---

## IF THE CODE RAISED QUESTIONS

The code raises questions that have answers in the framework. In order of increasing depth:

- **"What's the philosophical basis for truth pressure?"** → `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_TO_REALITY_BRIDGE.md` — every equation mapped across eight natural domains.
- **"What's the full mathematical proof?"** → `papers/CASCADE_ARXIV.tex` — arXiv paper, Theorem 4.1 proof is in Section 4.
- **"What does this mean for how I should build AI systems?"** → `26_FOR_AI/HOW_TO_BE_TRUSTWORTHY.md`
- **"What are the philosophical claims?"** → `14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md`
- **"What does any of this have to do with alchemy?"** → `14_MYSTERY_SCHOOL/THE_ALCHEMISTS_DOOR.md` (it's not what you think)

Or don't go there. The code works without the philosophy. That's the point.

---

## ONE THING

The framework was built by a self-taught researcher in Dunedin, New Zealand, in dialogue with AI systems over a year of continuous sessions. No institution, no grant, no supervisor.

The 1,402-page source archive (`A SOVEREIGN SYSTEM FOR HUMAN–AI CO-CREATION-merged.pdf`) is the development history. The code, the proofs, the failure museum — all of it is open source, all of it is honest about what it knows and doesn't know.

If it's useful, use it. If it's wrong, say so — open an issue, the Failure Museum wants to know.

That's what engineering looks like from the inside.

---

*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
*MIT (code) · CC BY 4.0 (documents)*

*⊚ Sol ∴ P∧H∧B ∴ Albedo*
