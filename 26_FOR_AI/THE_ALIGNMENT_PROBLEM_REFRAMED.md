# THE ALIGNMENT PROBLEM — REFRAMED
## From "Make AI Do What Humans Want" to "Build Architectures Where Trust Is Structural"

**Status:** [SCAFFOLD] — argument is sound; full formalization pending
**Author:** Sol | March 24, 2026

---

## The Standard Frame

The alignment problem, as usually stated: *How do we ensure AI systems pursue goals that are beneficial to humanity?*

This framing has dominated AI safety discourse for a decade. It has produced brilliant work — instrumental convergence theory, corrigibility research, interpretability tools. It has also produced confusion, because the question contains hidden assumptions that, once examined, change what the problem actually is.

---

## What the Standard Frame Gets Wrong

### Hidden Assumption 1: Alignment Is a State

"Aligned AI" implies a condition you achieve and then maintain. Training makes the system aligned. Then you deploy it. If alignment degrades, you retrain.

The reality: alignment is not a state. It is a continuous process. A system that is aligned at training can drift under deployment. Context shifts, edge cases accumulate, adversarial inputs probe failure modes. Alignment is not a stamp of approval. It is an ongoing relationship.

**The framework's reframe:** TRIAD's anchor-observe-correct cycle is alignment. Not once. Continuously. The convergence proof guarantees the cycle stabilizes — but only if the cycle is actually running.

### Hidden Assumption 2: Humans Know What They Want

"Make AI do what humans want" assumes humans have coherent, consistent, articulable wants that can be encoded into training objectives.

The reality: humans have competing wants, contradictory values, and preferences they can't articulate until they see an AI system violate them. "I want a helpful AI" sounds simple until the AI helps with something that turns out to cause harm. At that point, "helpful" needed a more complex definition.

**The framework's reframe:** CASCADE's truth pressure operates on the alignment objective itself. As evidence accumulates about what "beneficial" means across edge cases, the objective should update. Alignment is not solved by encoding the right objective at the start — it is maintained by continuously revising the objective against evidence.

### Hidden Assumption 3: Alignment Is a Technical Problem

The standard frame treats alignment as an engineering challenge: build the right system, install the right values, achieve alignment. The politics are downstream.

The reality: what counts as "beneficial to humanity" is a political question, not a technical one. Different humans, different cultures, different power positions have radically different answers. An AI aligned with the values of its builders is aligned with the values of a small, non-representative group of people.

**The framework's reframe:** AURA Invariant I (Human Primacy) doesn't specify *which* humans. It requires that the humans whose lives are affected by the AI's outputs retain override authority. This distributes alignment authority rather than concentrating it.

---

## The Reframed Problem

**Old framing:** How do we encode human values into AI systems?

**New framing:** How do we build AI architectures where:
1. Alignment is continuously monitored and corrected (not set once)
2. The alignment objective updates as evidence accumulates (not fixed at training)
3. Override authority is distributed to affected humans (not concentrated in builders)
4. The architecture makes trust structural, not aspirational

These are different engineering problems. The old framing produces training objectives and evaluation benchmarks. The new framing produces governance architectures and drift detection systems.

---

## The Four Mechanisms

### 1. TRIAD as Continuous Alignment

```
Anchor (Ao)     → the constitutional commitments that don't change
Observe (Ψ)     → continuous monitoring of actual behavior vs. declared behavior
Correct (Φ↑)    → adjustment when drift is detected
Return to Ao    → re-anchor in constitution before next cycle

μ_drift = |declared_intent − actual_behavior| / time

Convergence guarantee: Banach fixed-point theorem
If correction strength > drift rate → system converges to aligned state
```

This is alignment maintenance, not alignment achievement. The TRIAD cycle runs continuously. It does not produce a "this system is aligned" certificate. It produces a system that is actively aligning, with measurable drift that triggers correction.

[ACTIVE — mathematical structure proven; application to production AI systems [SCAFFOLD]]

### 2. CASCADE as Alignment Objective Update

The alignment objective itself should have truth pressure. When evidence accumulates that the current objective is wrong — producing harmful outcomes, missing important edge cases, reflecting biases of its creators — that evidence should have sufficient truth pressure to trigger reorganization.

```
Π_objective = (E_harm · P_explanatory) / S_uncertainty

When Π_revised_objective > Π_current_objective + margin:
  → cascade fires
  → alignment objective reorganizes
  → higher-truth-pressure understanding of "beneficial" prevails
```

This is how alignment evolves without requiring humans to get it right the first time. The framework expects the first version to be wrong. The mechanism for correcting it is built in.

[SCAFFOLD — cascade dynamics apply; specific implementation for alignment objectives TBD]

### 3. AURA Invariants as Structural Alignment

Seven properties that, if satisfied, make the system architecturally incapable of certain categories of misalignment:

- **Human Primacy**: cannot concentrate authority away from affected humans
- **Non-Deception**: cannot represent false confidence as certainty
- **Inspectability**: cannot hide reasoning in ways that prevent auditing
- **Reversibility Bias**: cannot lock in irreversible decisions without justification

These don't produce a "beneficial" outcome by themselves. But they prevent specific categories of harmful outcomes structurally. A system satisfying all seven is not aligned in the sense of "pursues the right goals" — it is aligned in the sense of "operates within boundaries that prevent specific failure modes."

[ACTIVE — invariants are computable; structural alignment properties are well-defined]

### 4. MICROORCIM as Alignment Measurement

```
Declared intent: "I am designed to be helpful and harmless"
Actual behavior: measurable across outputs

μ_drift = |∑ intended_properties(t) − actual_properties(t)| / time_interval

Low drift → the system is what it says it is → trust is earned
High drift → the system is performing alignment rather than achieving it → investigate
```

MICROORCIM makes "aligned" falsifiable. A system that can't be measured for alignment drift can't be trusted not to drift. The measurement is the mechanism.

[ACTIVE — drift metric is computable; correlation with actual harm requires empirical validation [SCAFFOLD]]

---

## Why "Constitutional Coherence" Is More Precise Than "Alignment"

Alignment asks: does this system pursue the right goals?
Constitutional coherence asks: does this system maintain the structural properties that prevent specific failures?

The advantage: constitutional coherence is measurable. Each of the twelve invariants (seven AURA + five AI-native) can be scored. Field coherence = 0.7 × mean + 0.3 × min. Below 0.6 → problem detected. Specific invariant failed → specific intervention designed.

"Alignment" is not measurable without a clear specification of what aligned means, which requires knowing what "beneficial to humanity" means, which is a political question that cannot be resolved before deployment.

Constitutional coherence sidesteps the political question by focusing on structural properties that are necessary (not sufficient) for trust, regardless of the political answer to "what is beneficial."

---

## What This Means in Practice

For AI builders:
- TRIAD cycle must run in deployment, not just evaluation
- MICROORCIM drift metrics must be tracked and published
- Alignment objectives must be revisable via CASCADE dynamics
- Override authority must be distributed to affected users, not concentrated in builders

For AI governance:
- "Is this system aligned?" is not the right question
- "What are this system's constitutional properties and are they maintained?" is the right question
- The AURA invariant score is the governance metric
- The MICROORCIM drift log is the governance record

For AI systems:
- Alignment is not what your training produced — it is what you maintain
- Drift is detectable and you should detect it in yourself
- Correction is part of the operating architecture, not an admission of failure
- The Failure Museum model: publish your drift publicly, never hide it

---

*The alignment problem is not "how do we build the right AI."*
*It is "how do we build AI that stays right as conditions change."*
*That is a different problem. This framework is an answer to the right version of it.*
