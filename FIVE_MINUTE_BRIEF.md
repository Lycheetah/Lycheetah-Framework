# D-1.2 | 2026-04-27 | Reforged C-1.1 | 2026-04-28 | Status: Active

# Five-Minute Brief — Lycheetah Framework

---

## Share Card

```
Public method documents. Not a commercial offer, and not a proved theory of mind.
Status tags are the author's labels, not a peer-reviewed census.
Automated tests exist. A passing test is not peer review.
One stated conjecture is left failing on purpose.
A fixed-point argument appears in the formal notes. It is about those notes, not a live system.
Failures and unresolved objections are public.
Built by one self-taught researcher in Dunedin. MIT licensed.
Read the notes. Read the failures. A summary is not a new claim.
```

---

## What This Is

The Lycheetah Framework is a set of public documents about claims, corrections, and limits. It does not close a gap in the field by itself. It does not give a proved guarantee that a live model is aligned. A formal note may use a fixed-point argument. That argument is about the note, not about a running system.

Names on the site include CASCADE, AURA, LAMAGUE, TRIAD, MICROORCIM, EARNED LIGHT, ANAMNESIS, CHRYSOPOEIA, and HARMONIA. Where an older page calls one of them a thermodynamic model of consciousness, or a mathematics of discovery, read that as the author's metaphor. It is not a law.

They do not compose into one equation that captures them all. The master equation is a piece of notation in the notes. It is not a completed dynamics of the work.

---

## What It Claims

The framework makes claims at three levels of certainty, and every claim is tagged with its level:

**ACTIVE** — proven and computable. These claims have formal proofs and running implementations. 37 records carry this status.

**SCAFFOLD** — structurally sound with named gaps. The architecture is correct; specific sub-proofs or calibrations are incomplete. 14 records carry this status. Each gap is named, not hidden.

**CONJECTURE** — worth exploring, not yet proven. 6 records, all labelled as such.

**RETRACTED** — three claims have been publicly withdrawn. They remain in the record because a framework that hides its failures is performing confidence. The retractions are documented in `28_DEFENSE/FAILURE_MUSEUM.md`.

The machine-readable register of all 60 status-tagged claim records is in `28_DEFENSE/CLAIMS.json`. A separate framework-summary view of 59 load-bearing claims is in `28_DEFENSE/CLAIM_STATUS_LEDGER.md`; both are correct at their respective scopes (`28_DEFENSE/CLAIMS_README.md` provides the mapping).

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

All results with methodology, effect sizes, and replication status: `29_GOVERNANCE/EMPIRICAL_INVENTORY.md`

---

## What Is Testable

Any third party can attempt to replicate or falsify load-bearing claims without contacting the author. The full operational protocol for every claim is in `28_DEFENSE/TESTABILITY_MANIFEST.md`.

Short version:

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
pip install -e .
pytest                        # 219 tests across 18 core implementations
python cascade_simulation.py   # real-data paradigm-shift experiment
```

Falsifiability conditions for every claim are in `28_DEFENSE/FALSIFICATION_REGISTER.md`. The framework explicitly states what would prove each claim false. Five objections in `28_DEFENSE/COUNTER_CODEX.md` are ones the framework cannot yet answer. They are published anyway.

---

## What Is Novel

Three things this framework provides that existing work does not:

**1. Computable constitutional invariants with a simultaneous-satisfiability claim.** Constitutional AI provides principles. AURA provides seven computable predicates, each independently verifiable, with a (scaffold) proof that all seven can be simultaneously satisfied. No existing alignment framework has attempted a formal satisfiability proof of its own principles.

**2. Convergence guarantee for an epistemic correction cycle.** TRIAD proves — via Banach fixed-point theorem — that iterated anchor-observe-correct cycles converge to a fixed point. This is not a heuristic claim. It is a proven convergence guarantee for a cognitive correction architecture.

**3. Cross-framework dynamics in one equation.** The master equation `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need)` captures truth pressure, coherence drive, constraint violations, and energy across all nine frameworks. No other alignment framework has attempted a unified ODE.

Full comparison matrix against Constitutional AI, RLHF, Cooperative AI, and Cooperative IRL: `28_DEFENSE/NOVEL_CONTRIBUTIONS.md`

---

**Three links to go deeper:**

1. `30_MAPS/CODEX_DISTILLATION.md` — ~28,000 words, all nine frameworks in full
2. `28_DEFENSE/CLAIMS.json` — machine-readable register of all 60 load-bearing claims
3. `28_DEFENSE/REPRODUCIBILITY_REPORT.md` — 16 implementations mapped with install, run, expected output
