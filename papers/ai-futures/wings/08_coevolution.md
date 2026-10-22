# The Monoculture Ceiling: Why More Copies of One Mind Cannot Buy Back Lost Diversity

**AI Future paper 08 · Wing: CONFLUENCE ⇌ · Domain: Coevolution · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "Coevolution" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

## Abstract

Humans shape AI systems, and AI-mediated environments reshape human habits in turn (TRAJECTORY). One consequence the curriculum flags as starred is **cognitive monoculture**: civilisation may become epistemically brittle if a few model families mediate research, education, administration and personal reasoning.

This paper gives the risk a precise shape with a toy model. Take *n* voters, each right with probability *p* > ½. With probability *s* all of them copy one common draw; otherwise they vote independently. Then:

- majority accuracy is *s*·*p* + (1 − *s*)·M(*n*, *p*), where M is the independent-voter (Condorcet) majority accuracy;
- as *n* grows, accuracy rises to a **ceiling** of 1 − *s*(1 − *p*), not to 1.

**Scale cannot buy back correlation.** With *p* = 0.7 and *s* = 0.3, no number of copies takes the ensemble above 0.91. A smaller ensemble of genuinely different minds can do better.

## 1. The question

*If two intelligences change one another for long enough, where does adaptation end and a new cognitive ecology begin?*

## 2. The monoculture ceiling

With *p* = 0.7 (synthetic):

| voters *n* | *s* = 0 (independent) | *s* = 0.3 | *s* = 1 (monoculture) |
|---|---|---|---|
| 1 | 0.700 | 0.700 | 0.700 |
| 11 | 0.922 | 0.855 | 0.700 |
| 101 | 1.000 | 0.910 | 0.700 |

**Proposition 1 (DERIVED; elementary).** For *p* > ½, M(*n*, *p*) → 1 as *n* → ∞ (Condorcet's jury theorem, from memory). So the mixed model's accuracy tends to *s*·*p* + (1 − *s*) = 1 − *s*(1 − *p*). The shared component sets a ceiling that scale cannot pass.

**Proposition 2 (DERIVED).** At *s* = 1, a thousand copies are exactly as accurate as one. Consulting more instances of one model family is not a second opinion; it is the same opinion, asked again.

**What the toy model leaves out.** Real correlation is partial and varies by question; voters differ in *p*; and majority vote is not the only way to aggregate. The model makes one point, and makes it exactly: **independence of error is a resource, and it is used up by convergence.**

**The empirical bridge (POSSIBLE_FUTURE, testable).** Estimate *s* for real model families as the excess error-overlap above what independence predicts, on shared benchmarks. If families trained on similar corpora with similar methods show rising *s* over time, the ceiling is falling in practice.

## 3. Coevolution as a two-way selection

The domain's first chamber names the mechanism by which *s* could rise on both sides of the relationship:

- **We Are Training Each Other ★ (TRAJECTORY).** Preference data shapes models; model outputs shape the preferences.
- **Interface Selection (TRAJECTORY).** Interfaces reward some cognitive habits over others, which is a cultural selection pressure on *how people think*.
- **The Co-Created Reality Trap (POSSIBLE_FUTURE).** Systems trained on behaviour already shaped by earlier systems can enter a feedback loop. Diversity in the training signal falls without anyone choosing it.

**Proposition 3 (CONJECTURE, testable).** Human error-correlation can rise *with* model correlation: people who consult the same assistant may come to share its blind spots. If so, a monoculture is a property of the joint human–machine system, not of the machines alone.

- *Test.* Measure error overlap among people before and after a period of consulting the same assistant, against a control group using different sources.
- *Refutation.* No rise in overlap.

## 4. Dependency without subjugation

The curriculum does not treat dependence as the enemy. Its NORMATIVE hall states the condition: deep dependence stays compatible with sovereignty when it is **plural, reversible, recoverable and auditable**. In this paper's terms:

- **plural** keeps *s* low;
- **reversible** keeps the exit (paper 09);
- **recoverable** keeps the human capability that a withdrawal test can measure (paper 10).

## 5. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Mutual Adaptation | We Are Training Each Other ★ | TRAJECTORY | §3. |
| | Mutual Domestication | POSSIBLE_FUTURE | Selection for human-compatible traits on the model side, and for model-compatible habits on the human side. Track both. |
| | Interface Selection | TRAJECTORY | §3. |
| | Co-Specialization | POSSIBLE_FUTURE | Teams that specialise around complementary strengths lower *s* by design. |
| II · Cognitive Ecology | The Intelligence Ecosystem | POSSIBLE_FUTURE | Many niches: humans, embodied agents, narrow experts, collectives. |
| | Cognitive Monoculture ★ | POSSIBLE_FUTURE | §2. |
| | Symbiotic Redundancy | POSSIBLE_FUTURE | Redundancy helps only when the characteristic errors are *not* shared (Proposition 1). |
| | Niche Formation | ALIEN_FUTURE | Artificial populations specialising by hardware, latency and task ecology. |
| III · Hybridization | The Extended Self | TRAJECTORY | Persistent memory and planning tools become parts of a person's cognition. Measure enhancement *and* atrophy. |
| | Cognitive Grafting | ALIEN_FUTURE | New cognitive operations attached by interface. |
| | The Third Mind | VOID | A tight human–AI pair can be modelled as one distributed system without implying a merged consciousness. |
| | The Shared Descendant | VOID | Architectures that are neither human nor machine in lineage. |
| IV · Culture After Contact | Civilizational Memory of Machines | POSSIBLE_FUTURE | Inherited failure archives (paper 09). |
| | Art That Requires Two Kinds of Mind | POSSIBLE_FUTURE | Works with layers meaningful to each kind of mind and to the relationship between them. |
| | Machine Myth | ALIEN_FUTURE | Compressed origin narratives in artificial lineages (paper 06, chamber II). |
| V · Civilization as Relationship | Coevolutionary Governance ★ | POSSIBLE_FUTURE | Institutions that regulate AI while running on AI form a recursive loop. The Independent No must sit outside the loop (paper 01). |
| | Dependency Without Subjugation | NORMATIVE | §4. |
| | The Co-Created Reality Trap | POSSIBLE_FUTURE | §3. |

## 6. What this paper does not claim

- It does not claim that current model families are a monoculture, or that *s* is rising. Those are measurements nobody in this repository has made.
- It does not claim that the toy model describes real voters or real models. It describes one mechanism exactly.
- It does not claim that diversity is free. Different minds also disagree more, and disagreement has a cost (paper 09).

## 7. Anchors

- Condorcet's jury theorem and its correlated-voter generalisations: standard, from memory.
- "Understanding the mechanism of human–AI interaction: a distributed cognition perspective", *Journal of Documentation* (2026). METADATA, grade study. Supports separating enhancement from atrophy in coupled human–AI cognition.
- Amin, Yin & Khanna, AAAI (2026). METADATA, grade study. Supports complementarity alongside alignment, which is the design form of a low *s*.

> *Domain koan:* If two intelligences change one another for long enough, where does adaptation end and a new cognitive ecology begin?
