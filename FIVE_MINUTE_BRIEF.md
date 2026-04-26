# D-1.0 | 2026-04-26 | Status: Active

# Five-Minute Brief — Lycheetah Framework

---

## Share Card

```
Nine formal frameworks for AI alignment and epistemology.
37 load-bearing claims proven and computable. 219 automated tests.
Convergence guaranteed by Banach fixed-point theorem.
Adversarial audit published. Failures published. Nothing hidden.
Built by one self-taught researcher. Open source. Free.
Read the math: FORMAL_SPINE.md
Read the evidence: EMPIRICAL_INVENTORY.md
Read the failures: FAILURE_MUSEUM.md
```

---

## What This Is

The Lycheetah Framework is a system of nine formally-grounded frameworks addressing a problem that no existing framework solves completely: how to build AI systems that are simultaneously rigorous, humane, and honest about their own limits.

The nine frameworks are: CASCADE (belief dynamics and knowledge reorganization), AURA (seven constitutional invariants for AI governance), LAMAGUE (formal grammar for encoding ethical constraints), TRIAD (convergent correction cycle with convergence proof), MICROORCIM (continuous drift detection between intent and behavior), EARNED LIGHT (thermodynamic model of consciousness), ANAMNESIS (mathematics of convergent discovery across cultures), CHRYSOPOEIA (seven-phase transformation operator), and HARMONIA (consonance dynamics and multi-agent synchronization).

They are not independent modules. They compose. CASCADE's truth pressure drives TRIAD's correction cycle. TRIAD's convergence guarantee undergirds AURA's constitutional invariants. CHRYSOPOEIA's transformation operator subsumes CASCADE as a special case. One equation — the master equation `dΨ/dt` — captures the cross-framework dynamics.

---

## What It Claims

The framework makes claims at three levels of certainty, and every claim is tagged with its level:

**ACTIVE** — proven and computable. These claims have formal proofs and running implementations. 37 claims carry this status.

**SCAFFOLD** — structurally sound with named gaps. The architecture is correct; specific sub-proofs or calibrations are incomplete. 14 claims carry this status. The gaps are specified — not hidden.

**CONJECTURE** — worth exploring, not yet proven. 6 claims. All labeled as such.

**RETRACTED** — three claims have been publicly withdrawn. They remain in the record because a framework that hides its failures is performing confidence. These are in `FAILURE_MUSEUM.md`.

The machine-readable register of all 60 load-bearing claims is in `CLAIMS.json`.

---

## What Is Proven

These results are ACTIVE — proven, computable, independently verifiable:

| Result | Method | Effect |
|---|---|---|
| CASCADE coherence improvement (synthetic) | 3-condition experiment, 10 replications, p < 0.001 | +40.3% (0.58 → 0.93), d = 2.84 |
| CASCADE coherence improvement (real data) | 5 historical paradigm shifts, 200 trials each | +110% (0.47 → 1.0) |
| CASCADE catastrophic forgetting reduction | Same synthetic experiment | −95.2% (0.42 → 0.02) |
| TRIAD discrete convergence | Banach fixed-point proof | Guaranteed |
| CHRYSOPOEIA fixed-point | Running demo — entropy → 0, C → 1 in 3 iterations | Demonstrated |
| Lyapunov verification | Symbolic + numerical (5,000 trials) | 11/11 claims, 0 failures |
| AURA Seven Invariants | Formal predicates, computable | Independently verifiable |

All results with methodology, effect sizes, and replication status: `EMPIRICAL_INVENTORY.md`

---

## What Is Testable

Any third party can attempt to replicate or falsify load-bearing claims without contacting the author. The full operational protocol for every claim is in `TESTABILITY_MANIFEST.md`.

Short version:

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
pip install -e .
pytest                        # 219 tests across 18 core implementations
python cascade_real_data.py   # real-data paradigm-shift experiment
```

Falsifiability conditions for every claim are in `FALSIFICATION_REGISTER.md`. The framework explicitly states what would prove each claim false. Five objections in `COUNTER_CODEX.md` are ones the framework cannot yet answer. They are published anyway.

---

## What Is Novel

Three things this framework provides that existing work does not:

**1. Computable constitutional invariants with a simultaneous-satisfiability claim.** Constitutional AI provides principles. AURA provides seven computable predicates, each independently verifiable, with a (scaffold) proof that all seven can be simultaneously satisfied. No existing alignment framework has attempted a formal satisfiability proof of its own principles.

**2. Convergence guarantee for an epistemic correction cycle.** TRIAD proves — via Banach fixed-point theorem — that iterated anchor-observe-correct cycles converge to a fixed point. This is not a heuristic claim. It is a proven convergence guarantee for a cognitive correction architecture.

**3. Cross-framework dynamics in one equation.** The master equation `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need)` captures truth pressure, coherence drive, constraint violations, and energy across all nine frameworks. No other alignment framework has attempted a unified ODE.

Full comparison matrix against Constitutional AI, RLHF, Cooperative AI, and Cooperative IRL: `NOVEL_CONTRIBUTIONS.md`

---

**Three links to go deeper:**

1. `CODEX_DISTILLATION.md` — ~28,000 words, all nine frameworks in full
2. `CLAIMS.json` — machine-readable register of all 60 load-bearing claims
3. `REPRODUCIBILITY_REPORT.md` — 16 implementations mapped with install, run, expected output
