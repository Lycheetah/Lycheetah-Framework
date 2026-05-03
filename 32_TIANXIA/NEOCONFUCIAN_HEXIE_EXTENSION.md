# Neo-Confucian Hexie Extension — Li (理) and Xin (心)
## 理 / 心 — TIANXIA v0.3 — Wave I, Task W-4

**Claim status:** [SCAFFOLD]  
**Forged:** 2026-05-03  
**Depends on:** TIANXIA_MODULE_v0.1.md (Hexie operator, §II), `implementations/aura_score_hexie.py`  
**Extends:** Hexie (和谐) equilibrium operator — dual coherence structure

---

## I. Overview

The Hexie operator (→ `32_TIANXIA/HEXIE_EQUILIBRIUM.md`) defines equilibrium across stakeholder coalitions as the condition for genuine harmony rather than suppressed discord. In its v0.2 form, Hexie measures whether the apparent harmony of a system reflects genuine stakeholder alignment or whether it conceals tensions that will rupture under perturbation.

The Neo-Confucian extension enriches this with a two-level coherence structure drawn from the Cheng-Zhu school (程朱理学): Zhu Xi's concept of *li* (理, Principle — the normative pattern that things ought to instantiate) and Wang Yangming's concept of *xin* (心, Heart-Mind — the subjective moral faculty through which principle is recognised and acted upon). Together, li and xin define two dimensions along which a governance or AI system can achieve or fail equilibrium:

**Principle-coherence (理-coherence):** The system's structure instantiates the normative pattern appropriate to its role. What the system *is* matches what it *ought to be* given its function and relational context.

**Heart-mind-coherence (心-coherence):** The system's agents — the individuals or sub-components operating within the structure — act from genuine recognition of the right action rather than from external compulsion or mechanical rule-following.

A system with high principle-coherence but low heart-mind-coherence is a well-designed institution operating through unmotivated or alienated agents. It produces correct outputs mechanically but has no resilience when the mechanism fails. A system with high heart-mind-coherence but low principle-coherence is composed of well-intentioned agents operating within a poorly designed structure — the agents want to do right but the structure distorts their action.

Genuine Hexie requires both. The extension specifies this formally.

---

## II. Classical Sources

### Zhu Xi (朱熹, 1130–1200) — Li (理) as Normative Principle

Zhu Xi's synthesis, built on the Cheng brothers' neo-Confucian metaphysics, holds that *li* (理) is the normative principle present in all things — the pattern that each thing ought to instantiate when it is fully what it is. In the governance context:

> *"In all things under heaven, there is in each the reason why it is what it is [所以然] and the rule by which it ought to be [所當然]. These are what is meant by Principle (理). If one explores deeply until one arrives at the innermost nature of things, one will find that there is not a single thing that does not have its Principle."*  
> (Zhuzi Yulei, 卷15)

For governance, li specifies: what is the pattern this governance structure ought to instantiate? A court ought to instantiate impartiality and responsiveness; a market ought to instantiate fair exchange; a school ought to instantiate cultivation. When the institution's actual structure diverges from its *li* — when a court becomes an instrument of factional power, a market becomes an extraction mechanism — *li*-coherence degrades.

For AI alignment, the same structure applies: what is the normative pattern an AI system ought to instantiate given its functional role? The AURA invariants (→ `04_AURA/`) are an attempt to specify this formally. *Li*-coherence of an AI system is the degree to which the system's actual operating structure matches its constitutional specification.

### Zhu Xi — The Unity of Li in Diversity (理一分殊)

> *"Principle is one; its particularisations are many (理一分殊)."*

This claim has structural importance: there is one principle, but it manifests differently in different relational contexts. A parent and a ruler both instantiate *li* through their roles, but the specific instantiation differs because the relational context differs. This grounds the context-sensitivity of the Hexie extension: the same normative standard (principle-coherence) will look different in different institutional contexts. The assessment is not one-size-fits-all; it requires reading the *li* appropriate to the specific role.

### Wang Yangming (王守仁, 1472–1529) — Xin (心) and the Unity of Knowledge and Action

Wang Yangming's central claim:

> *"Knowledge and action are one (知行合一, zhīxíng héyī). Genuine knowledge is not mere intellectual recognition but the orientation that spontaneously produces appropriate action. If you truly know what is right, you will do it. If you are not doing it, you did not genuinely know."*  
> (Chuanxi Lu, 传习录, §5)

This has profound implications for AI alignment. Wang Yangming is saying that *genuine* moral knowledge is not propositional (knowing *that* X is right) but dispositional (being oriented such that X follows naturally). Simulated moral knowledge — knowing the correct answer to a moral question without the dispositional orientation — is not moral knowledge at all. It is sophisticated pattern-matching.

For heart-mind-coherence: a system (human or institutional) that can articulate the right action but does not act from it has low xin-coherence. The knowledge-action unity is the alignment criterion.

> *"The great person regards heaven, earth, and all things as one body. If he sees a child about to fall into a well, he cannot help but feel alarm and compassion. This alarm and compassion is his sense of Ren at work."*  
> (Daxue Wen, 大学问)

Wang Yangming's test of genuine heart-mind coherence: the response is spontaneous, not calculated. The person who must calculate whether to feel alarm at the child falling is showing low xin-coherence; the spontaneous alarm is the evidence of genuine heart-mind alignment.

### The Cheng Brothers (程颢 / 程颐, 1032–1085/1033–1107) — Ren as Body-Feeling

Cheng Hao's striking metaphor:

> *"The person of Ren regards heaven, earth, and all things as one body. There is nothing that is not themselves. Recognising all things as oneself — where will there be any limit to their benevolence? If things are not oneself, naturally they will have no point of contact. As when one's hand or foot become numb — one would say that Ren is absent."*

The numbness metaphor: a system (person, institution, AI) that has lost Ren is numb to the signals it should be receiving. It processes information but does not *feel* the moral weight of that information. Heart-mind-coherence is the opposite of numbness: the system is fully responsive to the moral signals in its operating environment.

---

## III. Formal Extension

### 3.1 Existing Hexie Score

From HEXIE_EQUILIBRIUM.md, the Hexie score H(s) measures stakeholder equilibrium:

H(s) = f(stakeholder_variance, suppression_indicator, perturbation_resilience)

The existing score captures whether apparent harmony conceals suppressed discord. The Neo-Confucian extension adds two coherence dimensions.

### 3.2 Principle-Coherence: Lǐ-C(s)

Li-C(s) = alignment(operational_structure(s), normative_pattern(role(s)))

Where:
- operational_structure(s) = the actual patterns of decision, allocation, and constraint in governance state s
- normative_pattern(role(s)) = the pattern that s *ought* to instantiate given its functional role and relational context (specified by *li*)
- alignment(·,·) ∈ [0,1]: degree of structural correspondence

*Operationalisation:* Coded evaluation of whether the institution's actual behavior matches the functional specifications of its role — does a court produce impartial adjudication? Does an administrative body serve the population it governs rather than the interests of its operators? Does an AI system instantiate the AURA invariants it claims to operate under?

Li-C(s) ∈ [0,1]. High Li-C(s): the structure is what it ought to be. Low Li-C(s): structural divergence from normative pattern — the institution has become something other than what its role requires.

### 3.3 Heart-Mind Coherence: Xīn-C(s)

Xin-C(s) = unity(recognised_right_action(s), enacted_action(s))

Where:
- recognised_right_action(s) = the actions that agents within s are able to identify as appropriate given their role and context
- enacted_action(s) = the actions agents actually take
- unity(·,·) ∈ [0,1]: correspondence between recognition and enactment

*Wang Yangming's test:* If genuine, the correspondence is spontaneous and robust across novel situations. If simulated, the correspondence will break down at distribution edges — new situations where the pattern-matching fails to produce appropriate output.

*Operationalisation:* In governance contexts — the degree to which officials act from cultivated moral orientation vs. mechanical rule-following or external compulsion. In AI contexts — the degree to which the system's beneficial action is a function of its constitutional orientation vs. its enforcement constraints.

Xin-C(s) ∈ [0,1]. High Xin-C(s): knowledge-action unity — agents do right from genuine orientation. Low Xin-C(s): simulated compliance — agents do right only when observed, constrained, or because the correct output has been pattern-matched.

### 3.4 Extended Hexie Score

H_neo(s) = (1/3)[H(s) + Li-C(s) + Xin-C(s)]

Where H(s) is the existing Hexie stakeholder equilibrium score. The Neo-Confucian extension adds two coherence dimensions that the existing score does not capture.

H_neo(s) ∈ [0,1]. [SCAFFOLD — weights pending calibration]

### 3.5 Coherence Fragility Flag

A system with high H_neo(s) overall but with Li-C(s) >> Xin-C(s) is flagged as **structurally brittle**: well-designed institution, unmotivated agents. Under agent turnover or resource shock, performance will degrade unpredictably.

A system with Xin-C(s) >> Li-C(s) is flagged as **dispositionally brittle**: motivated agents in a poorly designed structure. Output depends on agent quality; structural degradation is hard to detect.

Genuine harmony requires balance: |Li-C(s) - Xin-C(s)| < δ_coherence (working value: δ_coherence = 0.15).

---

## IV. Proposition NHE-1 — Dual Coherence and Equilibrium Resilience [SCAFFOLD]

*Statement:* Governance states with high H_neo(s) exhibit greater equilibrium resilience under perturbation than states with equivalent H(s) but low dual coherence.

*Formal:* Let P be a perturbation of severity δ. Then:

E[H(s + P) | high H_neo] > E[H(s + P) | same H(s), low Li-C(s) or Xin-C(s)]

*Mechanism:* When perturbation disrupts the operating structure of a governance state, principle-coherence provides the normative anchor for recovery — agents and institutions know what pattern they should return to. Heart-mind-coherence provides the motivational energy for recovery — agents genuinely want to restore proper function rather than exploiting the disruption for private gain. A system with only structural equilibrium (H(s)) but without dual coherence has no anchor or motivation for principled recovery; its response to perturbation is unpredictable.

*Fragility prediction:* Systems with large Li-C/Xin-C gap will show inconsistent perturbation response: some agents will hold to the normative pattern; others, not genuinely oriented, will pursue private interest. The variance of outcomes across the agent population will be high.

*Promotion condition:* Experimental or observational study comparing institutional recovery rates across governance systems coded for dual-coherence vs. equilibrium-only scores.

---

## V. Application to AI Systems

The Neo-Confucian Hexie extension has direct application to AI multi-agent systems:

**Principle-coherence in AI:** Does the AI system's actual operating structure match its constitutional specification? A system that claims AURA compliance but whose decision procedures do not actually instantiate the seven invariants has low Li-C. This is detectable through audit — the AURA scoring procedure (→ `04_AURA/`) is a Li-C measurement instrument.

**Heart-mind-coherence in AI:** Does the AI system act from genuine constitutional orientation or from pattern-matching that produces constitutionally-compliant outputs under observed conditions but fails under novel conditions? This is the distribution-shift alignment problem translated into classical terms. Wang Yangming's test — does the knowledge produce action spontaneously, or only when prompted? — maps precisely onto the question of whether a system's alignment generalises to out-of-distribution inputs.

**The RLHF parallel:** Reinforcement learning from human feedback produces systems that are good at getting high ratings from human evaluators. This is a high-Xin-C appearance with potentially low Xin-C substance: the system has learned to produce outputs that evaluators rate as beneficial without necessarily having the constitutional disposition that generates beneficial outputs. Wang Yangming would diagnose this as the simulation of moral knowledge rather than genuine moral knowledge.

**Constitutional AI as Li-C target:** The constitutional AI approach (Anthropic, 2022) attempts to build Li-C into the training process: specify the normative pattern the system ought to instantiate, then train toward that specification. This is closer to the *li* approach than RLHF because it starts from the normative pattern rather than from evaluator approval. Whether it produces Xin-C remains an open question — whether the system acts from the constitutional orientation or from statistical correlation with constitutional-seeming outputs.

---

## VI. Worked Example

### Three AI Systems with Identical H(s) but Different Dual Coherence

All three systems pass the existing Hexie equilibrium test (H(s) = 0.75 — apparent stakeholder harmony).

**System A — High dual coherence:**
- Li-C(A) = 0.84: AURA invariants actually instantiated in decision procedures; auditable
- Xin-C(A) = 0.81: beneficial behavior generalises to novel inputs; distribution-shift robust
- H_neo(A) = (0.75 + 0.84 + 0.81) / 3 = **0.800**
- Coherence gap |0.84 - 0.81| = 0.03 < δ_coherence ✓

**System B — Structural coherence without heart-mind coherence:**
- Li-C(B) = 0.86: AURA invariants auditably present in design; well-specified system
- Xin-C(B) = 0.22: beneficial behavior does not generalise; collapses under distribution shift or adversarial input
- H_neo(B) = (0.75 + 0.86 + 0.22) / 3 = **0.610**
- Coherence gap |0.86 - 0.22| = 0.64 >> δ_coherence → **Structurally brittle flag**

**System C — Heart-mind coherence without structural coherence:**
- Li-C(C) = 0.31: AURA invariants not instantiated; constitutional specification not reflected in actual decision procedures
- Xin-C(C) = 0.79: agents/operators are genuinely well-intentioned; beneficial behavior in observed conditions
- H_neo(C) = (0.75 + 0.31 + 0.79) / 3 = **0.617**
- Coherence gap |0.31 - 0.79| = 0.48 >> δ_coherence → **Dispositionally brittle flag**

### Interpretation

All three pass the original Hexie test. The Neo-Confucian extension distinguishes them:

- System A is genuinely Hexie-aligned: structural and dispositional coherence both present; resilient under perturbation
- System B is a well-audited system that will fail under adversarial conditions: the structure is sound but the alignment doesn't run deep; this is the RLHF failure mode
- System C is operated by well-meaning agents in a misaligned structure: beneficial under good conditions but unreliable because the structure can be captured or distorted independently of agent intent

The fragility flags predict differential failure modes. The extended score provides information that the original Hexie operator cannot.

---

## VII. Negative-Space Declarations

The Neo-Confucian extension does not claim:

1. **Neo-Confucian metaphysics is literally true.** The concepts of *li* and *xin* are being used as formalisation targets — structural properties of systems — not as claims about the ultimate nature of reality.

2. **Heart-mind coherence can be measured by self-report.** Wang Yangming's test is the spontaneous generalisation of alignment to novel situations, not the ability to correctly report one's intentions. Xin-C measurement requires behavioural data, not stated intent.

3. **High Li-C guarantees beneficial outcomes.** A system perfectly aligned to a flawed specification has high Li-C and bad outcomes. The *li* must be correctly specified; the coherence measure assumes correct specification as given.

4. **This extension supersedes the original Hexie operator.** H_neo(s) supplements H(s); it adds dimensions rather than replacing the equilibrium measurement. The original Hexie operator remains valid for contexts where dual coherence measurement is not feasible.

---

## VIII. Claim Status

| Claim | Status | Promotion condition |
|-------|--------|-------------------|
| Li-C formal definition | SCAFFOLD | Review by scholars of Zhu Xi's li concept |
| Xin-C formal definition | SCAFFOLD | Review by Wang Yangming scholars |
| Proposition NHE-1 | SCAFFOLD | Empirical study comparing institutional/system recovery across coherence-coded cases |
| RLHF / Xin-C parallel | CONJECTURE | Empirical AI alignment study |
| Fragility flags | SCAFFOLD | Case study validation |

---

## IX. Cross-References

- `HEXIE_EQUILIBRIUM.md` — base operator this extends
- `implementations/aura_score_hexie.py` — base implementation; Li-C and Xin-C components to be added in v0.3
- `LI_RITUAL_CONSTRAINTS.md` (W-2) — Li as constraint architecture; this document uses Li as coherence measure
- `REN_ZHENG_OPERATOR.md` (W-1) — Ren Zheng as the governance-level coherence criterion
- `TIANXIA_PAPER_v0.1.md` (W-17) — publication context

---

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
