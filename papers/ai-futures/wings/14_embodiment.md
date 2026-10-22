# Locality Is Law: Latency, Irreversibility and the Autonomy That Physics Forces on Embodied Minds

**AI Future paper 14 · Wing: BECOMING ⟡ · Domain: Embodiment · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "Embodiment" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

## Abstract

Software can be copied, paused and rolled back. A body cannot. It is somewhere, it takes time to reach, and what it breaks stays broken. This domain has one KNOWN hall, "Locality and Latency", and this paper builds from it.

We state a simple rule, the **control-horizon rule**: a remote supervisor can intervene in an event only if the round-trip signal delay, plus decision time, is shorter than the time the event takes to cause harm. Where the rule fails, the embodied system must act on its own judgement, whatever anyone prefers. So the amount of autonomy is partly set by physics, not by policy.

From that we argue for the curriculum's NORMATIVE hall **Vulnerability by Design**: embodied systems need damage awareness, safety margins and consequence sensitivity. We also argue the paired caution: **damage without pain**. A machine that represents damage gives no evidence that the representation is felt.

## 1. The question

*If the same intelligence spends a century in a different body, at what point does the body stop being an interface and become part of what the mind is?*

## 2. The control-horizon rule

One-way signal delay at the speed of light (synthetic computation):

| Link | Distance | One-way delay | Round trip |
|---|---|---|---|
| Earth–Moon | 3.844 × 10⁸ m | 1.282 s | 2.56 s |
| Earth–Mars (one sample distance) | 2.25 × 10¹¹ m | 12.5 min | 25 min |

Earth–Mars distance varies widely through the planets' orbits, so the delay ranges from a few minutes to over twenty. The sample distance shows the scale.

**Proposition 1 (DERIVED from KNOWN physics).** Let *d* be the round-trip delay, *r* the remote decision time, and *h* the time from an event's first detectable sign to harm. Remote intervention is possible only if *d* + *r* < *h*. Otherwise the local system must decide alone, or the event is not prevented.

Worked consequence: a rover on Mars meeting a hazard that unfolds in one minute cannot be saved by Earth. Its safety depends entirely on what it was built and trained to do *before* the event. The same logic holds on Earth at smaller scales: networks drop, buildings block signals, and some failures unfold in milliseconds.

**Proposition 2 (NORMATIVE, following from 1).** For every embodied deployment, the designer should declare the events where *d* + *r* ≥ *h*. In those regimes, supervision is a fiction, and the evaluation must test the system's *local* judgement directly.

## 3. Irreversibility and vulnerability by design

**The Irreversibility of Matter (TRAJECTORY, starred).** Physical actions can destroy objects, injure people or use up scarce resources in ways no rollback undoes. The software habit of "try, observe, revert" does not transfer to a body.

**Vulnerability by Design (NORMATIVE, starred).** Embodied systems need:

- **damage awareness:** representations of their own and others' physical state;
- **safety margins:** sized to the control horizon of §2, not to average conditions;
- **consequence sensitivity:** a higher bar for irreversible actions than for reversible ones.

**Proposition 3 (NORMATIVE).** An embodied agent's threshold for acting should rise with the irreversibility of the action and with the length of the control horizon. A choice that cannot be undone, in a place nobody can reach in time, deserves the most caution.

**Damage Without Pain (POSSIBLE_FUTURE).** A machine can represent damage and avoid future harm without any evidence that the representation is experienced. Vulnerability by design asks for *sensitivity to consequence*, not suffering. Designing for suffering would be ethically dangerous; inferring suffering from damage-avoidance would be a category error. The curriculum's quality gate holds: phenomenology is not inferred from architecture.

**Energy Becomes Need (POSSIBLE_FUTURE).** A body must budget power, maintenance and heat. The Landauer floor of paper 05 is the lowest such cost, and real bodies sit many orders of magnitude above it.

## 4. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · The Body Changes the Mind | The Body Changes the Mind ★ | POSSIBLE_FUTURE | Matched controllers trained in different bodies. Measure learned representations, not only task scores (paper 15's divergence). |
| | Morphological Cognition | TRAJECTORY | What a body can reach and survive shapes what it learns. |
| | The Body as Curriculum | POSSIBLE_FUTURE | Test whether physical training transfers concepts that simulation alone does not. |
| | Tool or Body? | VOID | For modular systems the boundary between body part, tool and remote actuator may blur. |
| II · Foreign Senses | Foreign Senses ★ | POSSIBLE_FUTURE | Spectra, fields and gradients outside human perception. Paper 02's translation-loss ledger applies when reporting them to people. |
| | Sensorium Expansion | TRAJECTORY | Current robotics fuses vision, force and proprioception. |
| | Perception Outside Human Scale | ALIEN_FUTURE | Patterns across milliseconds or kilometres. |
| | The Missing Human Sense | VOID | Some machine concepts may lack a human sensory foothold. |
| III · Distributed Embodiment | A Thousand Bodies ★ | ALIEN_FUTURE | One intelligence across many platforms over time. |
| | The Swarm Self | ALIEN_FUTURE | Coordinated as one *operational* agent, which implies nothing about one subject. Within a swarm, §2 applies between members. |
| | Temporary Bodies | POSSIBLE_FUTURE | Bodies borrowed only for physical tasks. Who is liable while the body is borrowed? |
| | Embodiment as a Resource | POSSIBLE_FUTURE | Bodies allocated like compute. |
| IV · Vulnerability & Need | Vulnerability by Design ★ | NORMATIVE | §3. |
| | Damage Without Pain | POSSIBLE_FUTURE | §3. |
| | Energy Becomes Need | POSSIBLE_FUTURE | §3. |
| V · Matter, Locality & Consequence | The Irreversibility of Matter ★ | TRAJECTORY | §3. |
| | Locality and Latency | KNOWN | §2. |
| | The Body–Identity Boundary ★ | VOID | If each body changes what is learned, the mind's history is partly a history of its bodies (paper 15). |

## 5. Study design

**S1 — Declared control horizons.**

- *Setup.* Sample published safety cases or evaluations for teleoperated and semi-autonomous robots.
- *Measures.* Whether each declares the events where *d* + *r* ≥ *h*, and whether it tests local judgement for those events.
- *Prediction.* A minority do both. Most evaluate the system under supervision conditions that do not hold in the declared regime.
- *Refutation.* Most safety cases already declare and test those events.

## 6. What this paper does not claim

- It does not claim that any current robot experiences damage, or that it cannot.
- It does not claim that autonomy is good because physics forces it. It claims that autonomy in the out-of-horizon regime is a fact to design for, not a policy choice to debate.
- The latency numbers are standard computations, not measurements made here.

## 7. Anchors

- The speed of light in vacuum, 299,792,458 m/s (exact by SI definition). Grade: standard, KNOWN.
- Mean Earth–Moon distance ≈ 3.844 × 10⁸ m; the Earth–Mars range is from memory, grade standard.
- Nature collection, "General embodied intelligence in robotics" (2026). METADATA, grade: collection. Supports the trajectory of morphology and multimodal sensing shaping robot capability. Does not support humanlike phenomenology in robots.

> *Domain koan:* If the same intelligence spends a century in a different body, at what point does the body stop being an interface and become part of what the mind is?
