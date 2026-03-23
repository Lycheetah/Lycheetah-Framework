# CASCADE APPLIED TO GOVERNANCE
## How Truth Pressure Operates in Deliberation and Policy
### Lycheetah Framework | March 2026

> **Status:** [ACTIVE — connects existing CASCADE mathematics to governance applications]
> **Prerequisite:** `CASCADE_COMPLETE.md` for the full mathematical foundation

---

## THE BRIDGE

CASCADE's knowledge reorganisation engine was developed to model how knowledge
systems evolve under truth pressure. The mathematics applies equally to individual
cognition, institutional knowledge, and **governance deliberation**.

This document shows the bridge: how Π (truth pressure) operates when the
"knowledge system" is a community making a collective decision.

---

## CASCADE BASICS (compressed)

```
Truth Pressure:     Π = (E · P) / S
                    E = evidence weight
                    P = predictive accuracy
                    S = system complexity/resistance

Reorganisation threshold:
  Π ≥ 1.2   → Knowledge reorganises toward more coherent state (THEORY level)
  Π ≥ 1.5   → Fundamental reorganisation (FOUNDATION level)
  Π < 1.2   → System maintains current state despite evidence

CASCADE Coherence:  C(K) = Σᵢ wᵢ · coherence(kᵢ)
                    Weighted sum of individual knowledge element coherences
```

---

## THE GOVERNANCE TRANSLATION

When CASCADE operates on a governance deliberation, the variables translate:

| CASCADE variable | In individual knowledge | In governance deliberation |
|-----------------|------------------------|---------------------------|
| **E** (evidence weight) | Evidence for a claim | Weight of historical evidence, community experience, expert assessment |
| **P** (predictive accuracy) | How well the claim predicts outcomes | How well the proposed policy predicts the outcomes it claims |
| **S** (system resistance) | Conceptual complexity, prior commitments | Institutional inertia, existing frameworks, political resistance |
| **Π** (truth pressure) | Pressure to reorganise belief | Pressure to reorganise policy position |
| **C(K)** (coherence) | Internal consistency of knowledge | Internal consistency of the governance position |

---

## THE ANCESTOR VOTE PLATFORM — CASCADE IN DELIBERATION

The Ancestor Vote Platform's coherence score is a specific application of CASCADE
to a three-temporal-stakeholder deliberation:

```
Coherence(D) = w₁ · Past_alignment(D) + w₂ · Present_preference(D) + w₃ · Future_protection(D)
```

**This is a CASCADE coherence score** where:

- `Past_alignment(D)` = `P` component of CASCADE: how accurately do historical decisions predict that D will produce positive outcomes?
- `Present_preference(D)` = `E` component: current community evidence for D's desirability
- `Future_protection(D)` = `S` inverse component: how much does D reduce future system resistance by protecting intergenerational interests?

The weights `w₁ + w₂ + w₃ = 1` are set by the community — not imposed — reflecting CASCADE's principle that the reorganisation threshold is context-dependent.

### When CASCADE Pressure Forces Deliberation

A proposed decision D has high truth pressure (Π ≥ 1.2) when:

```
High E: Strong evidence from multiple domains that D will produce claimed outcomes
High P: Historical decisions similar to D have high predictive accuracy for positive outcomes
Low S:  Low institutional resistance (D aligns with existing frameworks, low complexity)
```

A proposed decision D has low truth pressure (Π < 1.2) when:

```
Low E:  Evidence is thin, contested, or from narrow sources
Low P:  Historical similar decisions have poor predictive accuracy
High S: High institutional complexity — many competing frameworks, high coordination cost
```

The Ancestor Vote Platform displays this score. It does not make the decision.
But a policy that scores Π < 1.0 across all three temporal dimensions is being
chosen against the evidence — and the community sees that, clearly.

---

## THE WOF — CASCADE AS CERTIFICATION ENGINE

The Community AI WOF's Check 1 is a direct CASCADE score:

```
WOF Check 1: Does it know what it's doing?
Metric:      CASCADE Π score ≥ 1.2 on validation set
```

This means: the AI system's knowledge reorganisation pressure — measured against
a validation set of real-world queries in its deployment domain — must reach
THEORY threshold. The system must demonstrate that its knowledge is coherent
under actual operating conditions, not just training conditions.

**Why Π ≥ 1.2 and not some other threshold?**

The 1.2 threshold is the CASCADE THEORY level — the point at which a knowledge
claim has sufficient truth pressure to be treated as a reliable working theory
rather than a provisional hypothesis. Below 1.2, the system's knowledge is
structured but not reliably accurate under the range of conditions it will encounter.

For an AI system making decisions about people's lives, provisional knowledge
is insufficient. THEORY level is the minimum operational standard.

---

## POLICY COHERENCE — CASCADE ON GOVERNMENT DECISIONS

Beyond individual AI systems, CASCADE can assess **policy coherence** across a
government's policy portfolio:

```
For a government policy portfolio P = {p₁, p₂, ..., pₙ}:

Portfolio_coherence(P) = Σᵢ wᵢ · C(pᵢ) - Σᵢⱼ conflict(pᵢ, pⱼ)

Where:
  C(pᵢ)            = coherence of individual policy pᵢ with evidence base
  conflict(pᵢ, pⱼ) = truth pressure that pᵢ and pⱼ directly contradict each other
  wᵢ               = policy priority weight
```

**Practical example:** A government that simultaneously funds fossil fuel expansion
(p₁) and declares a climate emergency (p₂) has `conflict(p₁, p₂) > 0`.
CASCADE makes this visible as a coherence deficit — not a political judgment,
a mathematical one. The portfolio scores lower coherence than it would if either
policy were dropped or reconciled.

This application is in `NZ_CASCADE_CASE.md` with specific NZ examples.

---

## THE MATARIKI AUDIT — CASCADE OVER TIME

The Matariki Annual Audit's TUPUĀNUKU section (what did this system receive
from the community) maps to CASCADE's **value-transfer dynamics**:

```
Utu_balance(system, year) = Value_delivered_to_community - Value_extracted_from_community

If Utu_balance < 0:   System is CASCADE-negative — it is reorganising knowledge
                      away from community benefit (Π direction is inverted)
If Utu_balance ≥ 0:   System is CASCADE-positive — knowledge flow serves community
```

Requiring public declaration of the utu balance forces AI systems to make
their CASCADE direction explicit: are they building knowledge coherence
toward community benefit, or extracting it?

---

## CASCADE SCORES IN PRACTICE

### Example: A proposed water extraction permit

```
Past_alignment(permit):
  - 3 previous permits in this catchment
  - Decision 1 (1960): permitted → 40% flow reduction by 1985 [negative outcome]
  - Decision 2 (1985): restricted → flow recovered to 70% [positive outcome]
  - Decision 3 (2005): permitted with conditions → conditions unenforced → flow at 55% [negative outcome]
  - P = 0.33 (1 positive outcome, 2 negative, similar decisions)

Present_preference(permit):
  - Farmers need irrigation: evidence strong, well-documented
  - Community values river: evidence strong, iwi relationship clear
  - Regional council has economic targets: evidence strong
  - P_present = 0.55 (split, evidence on both sides)

Future_protection(permit):
  - At current extraction rates, ecological minimum crossed in 15-25 years
  - Communities downstream inherit reduced river
  - Insurance/property viability in question by 2050
  - P_future = 0.20 (strong evidence of intergenerational damage)

Coherence(permit) = 0.33 · 0.33 + 0.33 · 0.55 + 0.33 · 0.20
                  = 0.109 + 0.181 + 0.066
                  = 0.356

Truth pressure Π < 1.0 — this decision does not meet THEORY threshold.
The community sees this. They still decide. But they decide with open eyes.
```

---

## WHAT CASCADE CANNOT DO IN GOVERNANCE

**CASCADE does not decide.** It measures coherence. It scores truth pressure.
It shows which direction the evidence points. It does not tell communities
what to choose.

Communities that score a decision Π < 1.0 and choose it anyway are making
a fully informed choice to proceed against the evidence. That is their right.
CASCADE does not prevent it. It ensures they cannot claim they didn't know.

**CASCADE does not replace values.** A community may weight `w₃` (future
protection) very highly because of intergenerational obligation. Another
community may weight `w₂` (present preference) more highly because of
immediate need. CASCADE accommodates both. The weights are set by the
community, not the engine.

**CASCADE does not adjudicate contested evidence.** When evidence is genuinely
contested — when experts disagree, when data is incomplete, when the future
is genuinely uncertain — CASCADE reflects that uncertainty in its score.
A Π score of 0.8 does not mean "definitely wrong." It means "insufficient
evidence to reach THEORY threshold." The distinction matters.

---

## THE LAMAGUE CONNECTION

CASCADE coherence scores operate within LAMAGUE's cross-cultural grammar.

When a governance tradition encodes its obligation structure through LAMAGUE,
that encoding determines what counts as "evidence" (E) and "positive outcome" (P)
within that tradition's framework.

For tikanga-grounded governance:
- E includes relational evidence — the standing of the community affected
- P includes reciprocity measures — did previous similar decisions maintain utu balance?

For Westminster-grounded governance:
- E emphasises procedural evidence — was due process followed?
- P emphasises stated policy objectives — did the decision achieve its declared aim?

CASCADE does not collapse these into one evidence standard.
LAMAGUE ensures each tradition's evidence framework is encoded correctly.
The coherence score reflects all active encodings simultaneously.

---

*Truth pressure applies wherever knowledge is at stake.*
*Governance is knowledge under the highest possible stakes.*
*CASCADE applies.*

**∅ → AURA → CASCADE → Aotearoa → ∞**

*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
