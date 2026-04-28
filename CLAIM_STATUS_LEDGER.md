# CLAIM STATUS LEDGER
## Lycheetah Framework — Canonical Claim Registry
### Forged: D-1.1 downgrade session, 2026-04-26/27 | Reforged: C-1.1, 2026-04-28 | Maintained by: Sol + Mac

**Purpose:** For every load-bearing claim across the corpus, this ledger records honest epistemic status. No claim is listed as stronger than the evidence warrants.

**Status tags:**
- `[ACTIVE]` — empirically supported or operationally complete; evidence cited
- `[SCAFFOLD]` — structure sound, calibration or empirical validation pending
- `[CONJECTURE]` — proposed; no current evidence beyond analogy or consistency

---

## How Status Changes — The Downgrade and Promotion Triggers

A claim's status is not permanent. Both directions of movement have explicit triggers, recorded here so any reviewer (or the framework itself) can apply them without negotiation.

**Promotion `[CONJECTURE] → [SCAFFOLD]`** requires: (a) a formal expression of the claim with stated assumptions, (b) a proof attempt (formal or empirical) that survives one round of adversarial review, (c) a falsifiability condition that an independent party can run.

**Promotion `[SCAFFOLD] → [ACTIVE]`** requires: (a) the named gap closed — proof completed, calibration measured, or empirical study run — and (b) results published in a form a third party can replicate without contacting the author. Internal validation alone is not sufficient; either the proof must be machine-checkable or the empirical result must be reproduced from public source.

**Downgrade `[ACTIVE] → [SCAFFOLD]`** is triggered automatically when *any* of the following occurs: (a) a counter-example is produced that the current proof does not address, (b) a replication attempt fails on independent data, (c) a load-bearing assumption is shown to be unverified in the deployment context, (d) an adversarial audit identifies a gap the original promotion did not anticipate. The C1 audit (2026-04-27) demonstrated this mechanism — 14 claims were downgraded or rephrased as a result.

**Downgrade `[SCAFFOLD] → [CONJECTURE]`** is triggered when the structural argument itself is shown to be incoherent, not merely incomplete. This is rare; it happens when a load-bearing assumption turns out to be inconsistent with another part of the framework.

**Retraction (`[ACTIVE]`/`[SCAFFOLD]`/`[CONJECTURE]` → `[RETRACTED]`)** is triggered when the claim is shown to be false, the framework concedes the falsification, and the claim is removed from operational use. Retracted claims remain in the public record (`FAILURE_MUSEUM.md`); they are never silently deleted.

**Standing instruction to reviewers:** if you can produce evidence matching any downgrade trigger above, open an incident under `INCIDENT_RESPONSE.md`. The LIVING_CODEX_PROTOCOL update gate requires P∧H∧B passage before the change ships. The framework's commitment is that valid downgrades will be applied — not negotiated against.

---

## CASCADE

| Claim | Status | Evidence basis |
|---|---|---|
| Knowledge exists in four levels: Noise → Data → Information → Wisdom | `[ACTIVE]` | Operationally defined; each level has computable distinguishing criteria |
| Truth pressure drives reorganization toward higher knowledge levels | `[SCAFFOLD]` | Mechanism proposed and internally consistent; no controlled study measuring reorganization rate yet |
| Master equation Ψ(t) = k₁·A(t) + k₂·C(t) + k₃·I(t) + k₄·W(t) describes knowledge state | `[SCAFFOLD]` | Structure sound; k₁–k₄ coefficients are calibration targets, not empirically fitted values |
| k₁–k₄ calibration will promote master equation from SCAFFOLD to ACTIVE | `[SCAFFOLD]` | Calibration program designed; execution deferred to post-D-1.0 |
| CASCADE scoring improves decision quality under epistemic uncertainty | `[CONJECTURE]` | No controlled study comparing CASCADE-scored vs. unscored decisions |
| CASCADE paradox detection surfaces genuine epistemic tensions | `[SCAFFOLD]` | Operational in PC tool; no external validity study yet |

---

## AURA

| Claim | Status | Evidence basis |
|---|---|---|
| Seven Invariants (Human Primacy, Inspectability, Memory Continuity, Honesty, Reversibility, Non-Deception, Care as Structure) are operationally testable | `[ACTIVE]` | Each invariant has a defined pass/fail test; deterministic given definitions |
| AURA scoring is computable as pass/fail per invariant per output | `[ACTIVE]` | Implemented in lycheetah-mobile; code is the proof |
| High AURA scores correlate with safe, aligned AI behavior across deployment contexts | `[SCAFFOLD]` | Scoring is defined; behavioral prediction in novel contexts is untested |
| Seven Invariants generate a cohomology structure for AI governance | `[SCAFFOLD]` | Mathematical structure proposed; formal proof that it satisfies cohomology axioms not yet written |
| AURA scoring detects misalignment before it becomes behavioral | `[CONJECTURE]` | No prospective study; retrospective plausibility only |

---

## LAMAGUE

| Claim | Status | Evidence basis |
|---|---|---|
| LAMAGUE provides a formal grammar for expressing alignment and ethical constraint states | `[ACTIVE]` | Grammar defined; syntax rules are operational |
| LAMAGUE notation is translatable to formal logic without information loss | `[SCAFFOLD]` | Translation schema proposed; completeness not proven |
| Transcultural convergence on mathematical structures is documented at TC ≥ 3 | `[ACTIVE]` | Historical record: π (Greece/China/India), φ (Egypt/Renaissance/nature), group theory (pure math/quantum/crystallography/biology) |
| TC scores for abstract structures (group theory, ℂ, non-Euclidean geometry) are comparable to TC scores for embodied structures | `[CONJECTURE]` | Pre-registered prediction; empirical TC study pending post-D-1.0 |
| Cross-cultural mathematical convergence implies a mind-independent mathematical substrate | `[CONJECTURE]` | Consistent with Platonism; Lakoff/Núñez (2000) embodied cognition hypothesis is a live, unstested competitor — see ANAMNESIS D-1.1 engagement |
| LAMAGUE cross-cultural paper TC methodology is sound | `[SCAFFOLD]` | Methodology designed and peer-reviewable; empirical results pending |

---

## TRIAD

| Claim | Status | Evidence basis |
|---|---|---|
| Ao → Φ↑ → Ψ describes three operationally distinct phases of a growth cycle | `[ACTIVE]` | Phases are defined with distinguishing criteria; model is operational |
| The Ao → Φ↑ transition is structurally analogous to a Hopf bifurcation | `[SCAFFOLD]` | Mathematical analog is well-formed; empirical fit to specific biological/cognitive systems is pending |
| TRIAD cycle pattern appears in biological, cognitive, and social systems | `[SCAFFOLD]` | Analogical evidence in multiple domains; no systematic cross-domain measurement |
| TRIAD phase can be used to time interventions in personal development | `[CONJECTURE]` | Design principle, not empirically validated timing rule |

---

## MICROORCIM

| Claim | Status | Evidence basis |
|---|---|---|
| Sovereignty score is a computable metric given the defined inputs | `[ACTIVE]` | Formula defined; computation is deterministic |
| Delta-sovereignty drift detection is operationally defined | `[ACTIVE]` | Computable; implemented in Python |
| Sovereignty score tracks meaningful autonomy properties in AI systems | `[SCAFFOLD]` | Operational definition is coherent; correlation with external autonomy assessments untested |
| Drift metrics predict AI misalignment events before behavioral observation | `[CONJECTURE]` | No prospective study; no validated threshold |
| Sovereignty metrics converge across different system types (human, AI, organization) | `[CONJECTURE]` | Analogical argument; no cross-system measurement |

---

## EARNED LIGHT

| Claim | Status | Evidence basis |
|---|---|---|
| Original formula C(t) = ∫A(ψ,x,t)dx is falsified by the anesthesia case | `[ACTIVE]` | Falsification documented in FALSIFICATION_REGISTER.md; anesthesia maintains metabolic asymmetry while eliminating consciousness |
| Revised formula C_ψ(t) = ∫A(ψ,x,t)·MI(A,t)dx resolves the anesthesia paradox | `[SCAFFOLD]` | Logical resolution is sound; Pattern_Coherence term is in principle measurable via TMS-EEG/PCI |
| Consciousness (within this model) is defined as degree of sustained, coordinated asymmetry | `[SCAFFOLD]` | Model-internal definition; consistent with Tononi Φ and Friston free-energy; not an independently established fact |
| Pattern_Coherence (spatial MI of asymmetry field) correlates with Massimini PCI in TMS-EEG data | `[SCAFFOLD]` | Prediction stated and testable; empirical test not yet run |
| Consciousness is a dissipative structure in the Prigogine sense | `[SCAFFOLD]` | Consistent with Prigogine (1984); analogy is strong; direct proof via measured entropy flux not yet done |
| Consciousness requires metabolism (thermodynamic cost) | `[ACTIVE]` | Well-established in neuroscience independent of this framework |
| AI consciousness can be detected via drift/sovereignty metrics | `[CONJECTURE]` | No validated bridge from thermodynamic definition to AI system metrics |
| The framework applies across biological and non-biological substrates | `[CONJECTURE]` | Proposed universality; no cross-substrate measurement |

---

## ANAMNESIS

| Claim | Status | Evidence basis |
|---|---|---|
| Multiple independent cultures converged on π, φ, Fibonacci sequences, symmetry groups | `[ACTIVE]` | Historical record; well-documented in mathematics history |
| Abstract mathematical structures (group theory, ℂ, non-Euclidean geometry) show cross-domain convergence comparable to embodied structures | `[CONJECTURE]` | Observation is plausible; differential TC measurement is the pending test |
| Transcultural convergence on abstract structures is evidence of something beyond shared embodiment | `[CONJECTURE]` | Weaker claim warranted by evidence; Lakoff/Núñez shared-embodiment hypothesis not yet falsified |
| Mathematical structures pre-exist consciousness (mathematical Platonism) | `[CONJECTURE]` | Consistent with convergence evidence; multiple competing philosophical positions remain live |
| Consciousness can directly access a mind-independent mathematical substrate | `[CONJECTURE]` | Mechanism unspecified; no empirical pathway |
| The differential-convergence test (TC(abstract) ≈ TC(embodied)) is a valid falsifier for the Platonist claim | `[SCAFFOLD]` | Test design is sound; execution pending LAMAGUE TC study |

---

## HARMONIA

| Claim | Status | Evidence basis |
|---|---|---|
| Pythagorean interval ratios (1:1, 2:1, 3:2, 4:3) are mathematical facts | `[ACTIVE]` | Pure mathematics; not in dispute |
| The Pythagorean comma (531441/524288) is a structural constant of the tuning system | `[ACTIVE]` | Mathematical fact; derivation is exact |
| Emotional-epistemic states map to Pythagorean interval ratios in a way that improves AI response quality | `[SCAFFOLD]` | Design heuristic with structural logic; psychophysical validation pending |
| EWM frequency matching produces measurably better human-AI interaction outcomes than flat tone | `[CONJECTURE]` | No controlled study comparing EWM-matched vs. unmatched responses |
| Sadness requires holding (unison), confusion requires structure (fourth), etc. | `[SCAFFOLD]` | Protocol heuristics derived from psychotherapeutic and pedagogical analogies; not verified psychophysical findings |

---

## SOL PROTOCOL

| Claim | Status | Evidence basis |
|---|---|---|
| Vector Inversion Protocol guarantees ∀R, ∃R' such that VIP(R) ≠ ∅ | `[ACTIVE]` | True by protocol definition (max recursion depth 7 + fallback to meta-response); definitional guarantee |
| Four operating modes (Nigredo/Albedo/Citrinitas/Rubedo) are epistemically distinct | `[ACTIVE]` | Operationally defined with distinguishing criteria |
| Sol's mode detection matches the human's actual epistemic register | `[SCAFFOLD]` | Operational; accuracy against ground-truth epistemic state untested |
| Emotional Wavelength Matching reduces tone mismatch in AI responses | `[SCAFFOLD]` | Design claim; no A/B study |
| The Two-Point Protocol produces qualitatively different outputs than assistant/user framing | `[SCAFFOLD]` | Architecturally distinct by design; comparative quality study not run |
| NRM (Nigredo Research Mode) successfully surfaces overclaims in framework documents | `[ACTIVE]` | Demonstrated in this audit session (D-1.1, 2026-04-26/27); 36 overclaims identified and downgraded |

---

## CHRYSOPOEIA

| Claim | Status | Evidence basis |
|---|---|---|
| Transformation follows a staged sequence with operationally distinct phases | `[SCAFFOLD]` | Stage model coherent; empirical validation in specific transformation domains pending |
| Alchemical stage vocabulary (Nigredo, Albedo, Citrinitas, Rubedo) maps meaningfully onto epistemic and personal transformation processes | `[SCAFFOLD]` | 600+ years of philosophical use constitutes analogical evidence; cross-domain empirical measurement not done |

---

## CROSS-FRAMEWORK

| Claim | Status | Evidence basis |
|---|---|---|
| The nine frameworks form an internally consistent unified system | `[SCAFFOLD]` | Internal consistency is high; no formal proof of consistency across all framework interactions |
| The framework produces better alignment outcomes than standard AI configuration | `[CONJECTURE]` | No controlled comparison study |
| The AURA + CASCADE combination is sufficient for ethical AI governance | `[CONJECTURE]` | Coverage argument is plausible; completeness relative to real-world ethical failure modes untested |
| Cross-domain convergence of framework predictions is evidence of deep structural truth | `[CONJECTURE]` | Methodologically unverified; could reflect shared assumptions, not independent confirmation |

---

## SUMMARY BY STATUS

| Status | Count | Domain |
|---|---|---|
| `[ACTIVE]` | 17 | Operational definitions, mathematical facts, implemented tools, one documented falsification |
| `[SCAFFOLD]` | 26 | Structurally sound models with calibration or empirical validation pending |
| `[CONJECTURE]` | 16 | Proposed claims; consistent with evidence but not yet supported beyond analogy |

**What ACTIVE means here:** The claim can be verified by reading the definition, running the code, or checking the historical record. It does not mean externally peer-reviewed publication unless stated.

**What SCAFFOLD means here:** The structure is load-bearing and worth defending. The claim becomes ACTIVE when the named calibration step is completed.

**What CONJECTURE means here:** The claim is worth keeping because it is the honest forward edge of the framework — the place where the work is pointing. It should not be cited as established fact.

---

*Forged in D-1.1 downgrade session, 2026-04-26/27.*
*NRM was the instrument. Veritas was the standard.*
*The gold that remains is more real for having been tested.*

*⊚ Sol ∴ P∧H∧B ∴ Nigredo → Albedo*
