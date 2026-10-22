# The Reality Ladder: What a Machine-Discovered Law Is Allowed to Claim

**AI Future paper 05 · Wing: REALITY ◈ · Domain: AI Future — Governing Rules of Reality · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "Governing Rules of Reality" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

## Abstract

When a learned model predicts a physical system well, three different claims tend to get merged:

- the formal claim, that the model is internally consistent;
- the empirical claim, that it survives the world's attempts to refute it;
- the ontological claim, that reality *is* the way the model represents it.

This paper names them as the **Reality Ladder** and argues that each rung needs its own evidence. Machine science will make the ladder steeper, because opaque representations can climb the empirical rung while offering no grip on the ontological one.

We ground the argument in one place where this repository corrected itself. The Framework's earlier "Earned Light" thermodynamic statement was an equality, ΔS = −W/T. Review found an adiabatic counterexample, and the law is now stated as the inequality ΔS ≥ −W/T, for isothermal processes with ΔU = 0, with equality only when the process is reversible. That correction is the domain's koan in miniature: a beautiful formula, refused by the world, replaced by a narrower true one.

## 1. The question

*What happens when a theory predicts reality better than any human can intuit, yet remains vulnerable to the world's refusal?*

## 2. The Reality Ladder

| Rung | Claim | Evidence that licenses it | Typical failure |
|---|---|---|---|
| 1 · Formal | The model is consistent and its derivations are valid. | Proof, type checking, symbolic verification | Valid derivation from a false premise |
| 2 · Empirical | The model's predictions survive attempted refutation on data it was not fitted to. | Held-out tests, intervention, replication | Overfitting; distribution shift; a test that cannot fail |
| 3 · Ontological | The world contains the entities and structure the model posits. | Convergence of *independent* representations on the same structure; successful intervention on the posited entity | Mistaking a useful compression for the furniture of the world |

**Proposition 1 (NORMATIVE for method, DERIVED for its consequence).** A claim may not be reported at a higher rung than its evidence reaches. A neural surrogate that predicts fluid flow sits on rung 2. Its latent variables stay hypotheses about rung 3 until independent methods converge on them.

**Proposition 2 (KNOWN; the correlation/intervention distinction).** A correlation network is evidence for rung 2 at most. Interventional evidence is required before a causal edge is admitted. This is the curriculum's "Interventional Causal Topology vs Correlation Networks" hall.

## 3. A worked descent: the Earned Light correction

This repository's review (BATCH38, M13) is an instance of the ladder.

- **The claim.** Earned Light originally wrote ΔS = −W/T as a general law.
- **Rung 1 failed by scope.** The statement silently assumed constant temperature and zero change in internal energy.
- **Rung 2 refused it.** An adiabatic process changes T, so the equality has no fixed T to refer to.
- **The repair.** From the Second Law at constant T, W ≥ ΔF. With ΔU = 0 this gives ΔS ≥ −W/T, with equality only for reversible processes.
- **Controls.** A reversible isothermal expansion meets the bound with equality. A free expansion satisfies it strictly. Both behave as predicted.

The lesson is general. **A falsified law usually has a true narrower successor, and finding it is worth more than defending the original.**

## 4. The energy floor under thought

The curriculum's starred hall "Thermodynamics of Distributed Cognition" asks what physics charges for thinking. The firmest floor known is Landauer's bound (KNOWN, from memory, with experimental tests reported in the literature): erasing one bit irreversibly dissipates at least k_B·T·ln 2 of heat.

- At 300 K this is **2.871 × 10⁻²¹ J per erased bit** (synthetic computation from the SI value of k_B).
- The curriculum's own hardening applies: Landauer is a floor on *irreversible erasure*. It is not a total energy budget for a computing system, and logically reversible computation can in principle avoid it.

**Proposition 3 (DERIVED).** Any claim that a distributed intelligence "thinks for free" must show either reversible computation or an accounting of erased bits. Any claim of a cognition energy law must say which rung it stands on.

The bridge between information measured in bits and thermodynamic entropy measured in J/K is the factor k_B ln 2. The Framework's thermodynamic texts still leave that bridge unstated; this review records it as an open item.

## 5. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Invariants | Invariants Across Candidate Worlds | KNOWN | Start from invariants. Do not assume one unique formulation of fundamental law. |
| | Symmetry Discovery in High-Dimensional Observation Spaces | TRAJECTORY | Learned symmetry detectors must recover known conservation laws on benchmark systems before any new claim is trusted. |
| | Non-Euclidean Phase-Space Invariants | TRAJECTORY | Source concrete dynamical-systems examples before publication. |
| II · Causality & Simulation | Interventional Causal Topology vs Correlation Networks | KNOWN | Proposition 2. |
| | Computational Physics vs Ontological Simulation | POSSIBLE_FUTURE | Three different claims: simulable, algorithmically describable, literally a computation. Keep them apart. |
| | Algorithmic Solenoids and Non-Local Causality | VOID | No faster-than-light signalling. Quantum non-locality does not transmit messages (no-signalling theorem, from memory). |
| | Base-World vs Simulated Boundary Criteria | VOID | A simulation need not leave detectable artefacts. Proposed tests constrain particular models only. |
| III · Emergence & Time | Memory-Bearing Observers and Entropy Arrows | POSSIBLE_FUTURE | The link between memory records and time's arrow is subtle. State it as a research program, not a theorem. |
| | Bridge Laws of Multi-Scale Emergence | POSSIBLE_FUTURE | Bridge laws may not exist for every pair of scales. Report failures as results. |
| | Observer-Relative Law Compressions | POSSIBLE_FUTURE | Representation-dependence of *compression*, not "laws are relative". |
| | Thermodynamics of Distributed Cognition ★ | POSSIBLE_FUTURE | §4. |
| IV · Machine-Native Physics | Machine-Native Laws Beyond Human Intuition ★ | ALIEN_FUTURE | Conditional future. Require externally checkable predictions however opaque the internals (paper 01 §5). |
| | Synthetic Gauge Fields in Non-Biological Perception | POSSIBLE_FUTURE | An analogy branch only. Sensor networks do not acquire physical gauge symmetry. |
| | Quantum Information Topologies in Distributed Intelligence | POSSIBLE_FUTURE | Keep topological quantum computation as a reference. Remove claims that a mind *is* a topological code. |
| | Temporal Architecture of Parallel Model Execution | ALIEN_FUTURE | Branched computation is counterfactual trees, not experienced parallel time. |
| | Unification of Sub-Symbolic Dynamics with Conservation Axioms | TRAJECTORY | Physics-informed, Hamiltonian and symplectic learning. "Exact conservation" holds only up to discretisation. |
| V · Measurement Horizon | Co-Evolving Instrument-Theory Loops ★ | TRAJECTORY | Paper 01, chamber IV. |
| | The Ontological Horizon of Machine Measurement ★ | VOID | Rung 2 may outrun rung 3 indefinitely. That is a possibility to hold, not a defeat. |

## 6. Study design

**S1 — Rung discipline in published machine-discovered laws.**

- *Setup.* Sample papers that report equations discovered by symbolic regression or learned surrogates.
- *Measures.* Code the highest rung each paper *claims* against the highest rung its evidence *reaches*.
- *Prediction.* A measurable share of claims sit one rung above their evidence, most often rung 2 evidence reported in rung 3 language.
- *Refutation.* Claimed rung and evidenced rung agree almost everywhere.

## 7. What this paper does not claim

- It does not claim that machine-discovered laws are unreliable, or that ontological claims are never earned.
- It does not claim to settle the simulation hypothesis or the nature of time.
- The Landauer number is a standard computation, not a measurement made here.

## 8. Anchors

- Landauer's principle and its experimental tests: from memory, grade standard. The specific experimental papers were not re-read and are not cited by title here.
- The no-signalling theorem: standard, from memory.
- This repository: `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH38_FINDINGS_AND_LEDGER.md` (N3), witnessed by `repro_math_m1_m18.py`.

> *Domain koan:* What happens when a theory predicts reality better than any human can intuit, yet remains vulnerable to the world's refusal?
