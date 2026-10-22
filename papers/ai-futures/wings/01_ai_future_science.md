# The Independent No at Scale: Science When the Investigator Changes

**AI Future paper 01 · Wing: SCIENCE ⟁ · Domain: AI Future Science · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "AI Future Science" domain in the AI Future Master Curriculum v1.0 (Lycheetah Mystery School, 2026-09-28). That curriculum is private School canon and is not in this repository.

Every claim carries one register: KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. Numbers marked *synthetic* come from [`models.py`](models.py) and illustrate a mechanism. They are not observations.

## Abstract

Machine systems now generate hypotheses, run experiments and critique one another (TRAJECTORY). The usual worry is that machines will be wrong. This paper argues for a sharper one: **the more original the search, the more stringent the contradiction must become, and stringency has to be designed in.** The reason is arithmetic, not opinion. As a generator explores further from known ground, the base rate of true hypotheses among its outputs falls. If the verifier's false-pass rate stays fixed, the share of accepted "discoveries" that are true falls with it (KNOWN; Bayes' rule).

We name the requirement **the Independent No**: something the generator does not control and that can contradict it. That might be an instrument, a proof checker, held-out data, a rival model or the phenomenon itself. We show that it must scale its stringency with the generator's novelty. The paper then follows the domain's eighteen halls from the question engine to the first machine mystery and states which are tractable now. It ends with one translation contract for results that machine science can predict but humans cannot yet intuit.

## 1. The question

*What happens when science itself gains new kinds of scientist?* The curriculum separates five movements, which are the chambers below:

1. who chooses the questions;
2. what counts as an observation;
3. what new objects of study appear;
4. what happens when laboratories design laboratories;
5. what happens when prediction outruns understanding.

## 2. Core contribution: novelty raises the price of a No

Let a generator propose hypotheses of which a fraction *b* are true. A verifier passes a true hypothesis with probability *s* and a false one with probability *f*. The precision of the accepted set is

> P(true | accepted) = b·s / (b·s + (1 − b)·f).

With *s* = 0.9 and *f* = 0.05 (synthetic):

| base rate *b* | precision of accepted | false-pass rate needed for precision 0.9 |
|---|---|---|
| 0.5 | 0.947 | 1.0 × 10⁻¹ |
| 0.1 | 0.667 | 1.1 × 10⁻² |
| 0.01 | 0.154 | 1.0 × 10⁻³ |
| 0.001 | 0.018 | 1.0 × 10⁻⁴ |

**Proposition 1 (KNOWN, elementary).** To hold accepted precision constant while the base rate falls by a factor of ten, the verifier's false-pass rate must fall by roughly a factor of ten.

**Consequence (DERIVED).** "Science That Chooses Its Own Questions" and "Unknown-Unknown Detection" are exactly the regimes where *b* is lowest. Autonomy in question choice is therefore not separable from investment in contradiction. A lab that scales generation without scaling its Independent No will, by arithmetic, publish more falsehoods per truth as it becomes more ambitious. This is the Framework's own lesson about green gates (a check must be seen to fail) restated as a law of discovery throughput.

**What would refute the application (not the arithmetic).** Evidence that autonomous discovery pipelines keep a roughly constant true-positive share as their outputs move away from the training distribution, *without* tightening their verification. That would mean *b* does not fall with novelty in practice.

## 3. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Question Engine | Science That Chooses Its Own Questions ★ | POSSIBLE_FUTURE | Log attention allocation: which anomalies the system pursued, which it ignored, and why. Question choice becomes auditable data. |
| | Hypothesis Ecologies | TRAJECTORY | Model hypotheses as a population with birth, merger and death under evidence. Keep the dead ones resurrectable (§4, the negative-results archive). |
| | The Independent No | KNOWN | §2. Each pipeline declares its contradiction source and its measured false-pass rate. |
| | Unknown-Unknown Detection | POSSIBLE_FUTURE | Operational test: the system flags residual structure that no existing category compresses, and a later category does. A detection is retrospective by nature. |
| II · Sensorium | The Machine Observatory | TRAJECTORY | When the observation is itself a model output, its provenance chain is part of the datum. |
| | New Senses, New Objects | POSSIBLE_FUTURE | Compare the object segmentations of sensors with different modalities over the same scene. Disagreements are candidate new objects. |
| | Science Outside the Human Clock | ALIEN_FUTURE | Persistence demands lineage: who is "the investigator" after three hardware generations? (See paper 15.) |
| | Machine-Native Variables ★ | ALIEN_FUTURE | A variable is admissible if it predicts held-out data. It need not compress into a human concept, but its *predictions* must be translatable (§5). |
| III · Natural Histories | Machine Ethology | TRAJECTORY | Behavioural regularities of persistent agents, measured the way ethologists measure animals: by observation protocols, not source reading. |
| | Artificial Species | POSSIBLE_FUTURE | The question is when version control stops describing a population and phylogeny starts. Test: do lineage trees predict capability better than version numbers? |
| | Comparative Consciousness Science | VOID | Its legitimate present form is the comparison of *theories'* predictions across substrates, not the measurement of experience. |
| | Hybrid Minds as a New Experimental Class | POSSIBLE_FUTURE | Prosthetic memory gives cases where substrate changes while some psychological continuity remains. These are natural experiments for identity theory. |
| IV · Recursive Labs | Laboratory Ecologies | TRAJECTORY | Replication is the Independent No *between* labs. Diversity of method is a safety property (paper 08). |
| | Instrument–Theory Coevolution ★ | POSSIBLE_FUTURE | Closed-loop design of the experiment that best separates rival theories. The risk is an instrument designed only to confirm. |
| | Recursive Science | ALIEN_FUTURE | A successor intelligence designed for a question inherits the parent's blind spots unless the Independent No is external to both. |
| V · Epistemic Horizon | Truth Without Intuition ★ | ALIEN_FUTURE | Prediction, verification and understanding can come apart. Keep all three as separate fields in every result record. |
| | The Translation Gate ★ | POSSIBLE_FUTURE | §5. |
| | The First Machine Mystery ★ | VOID | Define it operationally: a residual the system cannot reduce with any of its representations *and* can show is not noise. |

## 4. Study designs

**S1 — Novelty against precision (preregisterable).**

- *Setup.* Take one generator with a fixed verifier. Bin its proposals by distance from the training corpus, using embedding distance or citation-graph distance.
- *Measures.* In each bin, measure accepted precision against slow ground truth: replication, a proof assistant, or a later experiment.
- *Prediction.* Precision falls with distance at fixed *f*.
- *Refutation.* A flat precision curve.

**S2 — The negative-results archive.**

- *Setup.* Persist every rejected hypothesis with its killing evidence.
- *Measures.* Count how often a later observation revives a dead hypothesis.
- *Lesson.* A revival rate above zero turns "Hypothesis Ecologies" from metaphor into infrastructure. It connects to the Framework's failure-museum practice and to paper 11's "Negative Results Become Valuable".

## 5. The Translation Gate contract

A machine-native result may cross into human institutions only with a record that keeps:

- **predictions**, with uncertainty;
- **assumptions**;
- **failure conditions**: what observation would refute it;
- **causal dependencies**;
- **safety constraints**;
- **translation loss**: what the human-language version drops.

The contract does not demand that the internal concept be translated. It demands that its *consequences* be contestable. That is the line between "Truth Without Intuition" and truth without accountability.

## 6. What this paper does not claim

- It does not claim that autonomous science is generally reliable. The anchors below explicitly do not support that.
- It does not claim machine consciousness, and it does not claim that any variable discovered by a machine is real rather than useful.
- The precision table is synthetic arithmetic. The empirical question is how *b* actually varies with novelty in real pipelines.

## 7. Anchors

All anchors are at verification level METADATA: carried from the curriculum's research ledger, not re-read in this session. Each one supports a trajectory, never a speculative endpoint.

- Gottweis et al., "Accelerating scientific discovery with Co-Scientist", *Nature* (2026). Grade: study. Supports multi-agent hypothesis generation with critique and validation as a present trajectory.
- Canty & Abolhasani, "The past, present and future of self-driving laboratories", *Nature Reviews Chemistry* (2026). Grade: review. Supports autonomous experimentation and provenance-complete infrastructure.
- Bayes' rule and the base-rate effect: standard probability, from memory.

> *Domain koan:* When a non-human intelligence begins asking questions of its own, will humans recognize them as science if they do not resemble ours?
