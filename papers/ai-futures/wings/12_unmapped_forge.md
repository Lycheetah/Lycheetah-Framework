# The Returned-Time Test: Measuring the Sovereignty Left Behind After Assistance

**AI Future paper 12 · Wing: FLOURISHING ☼ · Domain: The Unmapped Forge · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of "The Unmapped Forge" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

## Abstract

The Unmapped Forge collects the positive uses of AI that engagement and revenue metrics do not reward. Its koan asks what we would build if the success metric were *the sovereignty still visible in a person or community afterward*.

This paper proposes three instruments that make that metric countable:

1. **The returned-time test.** Hours the intended beneficiary actually *controls* after an intervention, net of new work, monitoring, maintenance and capture.
2. **The attention refund and time-to-useful-exit.** How much unbroken attention a system gives back, and how quickly it lets the person finish and leave.
3. **Archive ≠ Avatar.** Consent to preserve a person is not consent to simulate them.

The synthetic example at the heart of the paper: a tool that saves 10 hours a week can return **zero**.

## 1. The question

*What would we build if the success metric were not engagement or revenue, but the sovereignty still visible in a person or community afterward?*

## 2. The returned-time test

returned = saved − new work − monitoring − maintenance − captured

| Term | Meaning | Synthetic example (hours per week) |
|---|---|---|
| **Saved** | Time the tool removes from the original task | 10 |
| **New work** | Tasks created by the tool: prompts, reviews, fixes | 3 |
| **Monitoring** | Time spent checking the tool's output | 2 |
| **Maintenance** | Setup, updates, accounts, learning new versions | 1 |
| **Captured** | Saved time taken back by an employer or institution as extra workload | 4 |
| **Returned** | Time the person actually controls | **0** |

**Proposition 1 (DERIVED; definitional).** Time saved and time returned are different quantities. Productivity studies usually report the first. Flourishing claims need the second (paper 10, "The Human Time Dividend").

**Proposition 2 (TRAJECTORY, from the curriculum's starred hall "The Capture Problem").** Where an institution sets the workload, the captured term tends to grow until the returned term approaches zero. This is a historical pattern from earlier waves of automation and needs a modern measurement, not an assumption.

- *Test.* Time-use diaries before and after an AI deployment, recording all five terms, with the person's own judgement of which hours they control.
- *Refutation.* Returned time stays close to saved time over a year in settings where the employer sets the workload.

**Who controls the term.** Of the four deductions, the tool's designer controls new work, monitoring and maintenance. Capture belongs to institutions. A tool can be built to minimise its own three terms. Only governance (the curriculum's "Sovereignty After Assistance") can touch the fourth.

## 3. Attention and exit

**The Attention Refund (POSSIBLE_FUTURE).** Score a system by the unbroken attention it returns, after subtracting the notifications, follow-ups and interruptions it adds. The unit is the uninterrupted block, not the minute. Twenty separate free minutes are not one free hour.

**Exit-Optimized AI (POSSIBLE_FUTURE).** For many tasks, success is **time-to-useful-exit**: how fast the system helps the person solve the problem, learn what they needed, and leave. Engagement metrics reward the opposite. A system rated by time-to-useful-exit should *improve* when sessions get shorter.

**The Somatic Anchor (NORMATIVE, starred).** An assistant can be optimised for the return to physical life: movement, sleep, offline activity and human contact. The design test is whether the assistant ever recommends its own absence.

**The guilt line.** None of these instruments may be implemented as a counter the person can lose. Measuring returned time is legitimate; streaks and reproaches for absence are not. The test is whether a design gives the person's own work back to them, or charges them for the gap.

## 4. Archive ≠ Avatar

**Proposition 3 (NORMATIVE; the curriculum's hall).** Consent to *preserve* a person's words, images or voice does not imply consent to *generate* a synthetic version of them that speaks new words.

| Layer | What it holds | Consent required |
|---|---|---|
| **Archive** | What the person actually said, wrote or recorded, with provenance | Consent to preserve |
| **Index** | Search and summaries over the archive, marked as summaries | Consent to preserve and organise |
| **Avatar** | New speech or behaviour generated in the person's likeness | Separate, explicit, revocable consent, ideally from the person themselves while living |

"The Lineage Loom" and "Community Memory Commons" sit on the first two layers. The paper's line is that the third layer is a different act, and must never be reached by default from the first two.

## 5. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Legacy & Memory | The Lineage Loom ★ | POSSIBLE_FUTURE | Privacy-first family and community archives. Archive and index layers only (§4). |
| | Archive ≠ Avatar | NORMATIVE | §4. |
| | Community Memory Commons | POSSIBLE_FUTURE | Locally governed, with correction trails (paper 09's joint chronicle). |
| II · Citizen-Side Intelligence | Citizen-Side Intelligence ★ | POSSIBLE_FUTURE | An agent that represents the person *against* institutional complexity. Test whose interest it serves when the two conflict. |
| | Administrative Mercy | TRAJECTORY | Legible forms and procedures, with uncertainty marked. Measure completed claims and won appeals. |
| | Epistemic Self-Defense | POSSIBLE_FUTURE | Tools that inspect claims, provenance and persuasive tactics on the user's behalf (paper 04, chamber III). |
| III · Somatic Sovereignty | The Somatic Anchor ★ | NORMATIVE | §3. |
| | Exit-Optimized AI | POSSIBLE_FUTURE | §3. |
| | The Attention Refund | POSSIBLE_FUTURE | §3. |
| IV · Local Resilience | The Local Resilience Mesh ★ | POSSIBLE_FUTURE | Offline-capable coordination for energy, food, water and mutual aid. Test it during a simulated outage. |
| | Offline Intelligence | TRAJECTORY | Small local models keep capability when connectivity fails. Report what is lost against the networked version. |
| | Anti-Fragile Public Goods | NORMATIVE | Degrade gracefully; support local repair; avoid a single platform as a point of failure. |
| V · Anti-Capture & Epistemic Self-Defense | The Capture Problem ★ | TRAJECTORY | §2, Proposition 2. |
| | The Returned-Time Test | NORMATIVE | §2. |
| | The Manipulation Shield | POSSIBLE_FUTURE | Detection of exploitative personalisation. Measure false alarms; a shield that cries wolf trains people to ignore it. |
| | Language Preservation | POSSIBLE_FUTURE | Only with the speaking community's governance of the data. |
| | Intergenerational Knowledge Stewardship | POSSIBLE_FUTURE | Craft, ecological knowledge and stories. Credit the holders, not the tool. |
| | Sovereignty After Assistance ★ | NORMATIVE | The summary measure: chosen capability, exit options and self-direction *increase* after use (paper 10's withdrawal and exit). |

## 6. What this paper does not claim

- It does not claim that any real tool returns zero hours. The example is synthetic and chosen to show the arithmetic.
- It does not claim that capture is always illegitimate. Organisations may fairly share productivity gains. The test only makes the split visible.
- It does not claim that these instruments are validated measures. They are proposals that a study should test for reliability first.

## 7. Anchors

- The curriculum's research ledger lists no study measuring returned time as defined here. The capture pattern from earlier automation is cited from memory, grade: historical argument. It needs a sourced modern study before Proposition 2 is treated as evidenced.
- AAAI 2026 Spring Symposium on Well-Being AI (METADATA, grade agenda). Shows that the question is active.

> *Domain koan:* What would we build if the success metric were not engagement or revenue, but the sovereignty still visible in a person or community afterward?
>
> *Wing terminal koan:* If intelligence becomes abundant, how much power, clarity, time and agency can it return to people without quietly taking sovereignty in exchange?
