# THE ANCESTOR VOTE PLATFORM
## Whakapapa Is A Voter Roll
### Technical Specification | Lycheetah Framework | March 2026

> **Status:** [SCAFFOLD — architecture specified, build pending]
> **What this is:** A deliberation platform that brings past consequences and
> future inheritors into the room alongside present voices.

---

## THE ARCHITECTURE

### Three Temporal Stakeholder Sets

Every significant community decision has three sets of stakeholders:

**THE PAST — Ancestor Votes**
Every decision made on this land before, and what it produced.
Not as guilt. As data. CASCADE truth pressure applied:
a decision that has been tried before and produced harm scores
lower coherence — regardless of how attractive it looks today.

**THE PRESENT — Living Voices**
The people in the room. Their current knowledge, preferences, stakes.
Standard democratic input — but now placed alongside temporal context
rather than in isolation.

**THE FUTURE — Mokopuna Inheritors**
Probabilistic modelling of who inherits this decision.
What are the 7-generation consequences of each proposed option?
Who will live with this choice who cannot vote on it today?

### The CASCADE Coherence Score

For each proposed decision D, CASCADE computes:

```
Coherence(D) = w₁·Past_alignment(D) + w₂·Present_preference(D) + w₃·Future_protection(D)

Where:
  Past_alignment  = how consistent is D with ancestor decisions that produced
                    positive outcomes? (scored from historical record)
  Present_preference = current community support level (democratic input)
  Future_protection = probabilistic assessment of intergenerational benefit
                      vs harm (environmental, social, economic modelling)

  w₁ + w₂ + w₃ = 1 (weights set by community — not imposed)
```

The score does not make the decision. It makes **time visible.**

---

## USE CASES

### Water Rights
A community decides whether to permit water extraction for agriculture.

**Past votes:** Three previous extraction decisions in this catchment.
Decision 1 (1960): permitted, resulted in 40% flow reduction by 1985.
Decision 2 (1985): restricted, flow recovered to 70% by 2000.
Decision 3 (2005): permitted with conditions, conditions not enforced,
current flow at 55% of pre-extraction levels.

**Present voices:** Farmers need irrigation. Community values the river.
Regional council has economic targets.

**Future inheritors:** At current extraction rates, modelling suggests
river flow drops below ecological minimum within 15-25 years.
Communities downstream inherit a dead river.

**CASCADE coherence:** The proposed extraction scores low coherence
with past outcomes (previous permissions produced harm) and low
future protection (modelling shows intergenerational damage).
Present preference is split.

The platform shows all of this. The community decides. But they decide
with their eyes open across time.

### Coastal Development
**Past votes:** What happened to every previous coastal development
in this region. Which ones thrived. Which ones were destroyed by storms.
Which ones displaced existing communities.

**Future inheritors:** Sea level projections for 2050, 2075, 2100.
Insurance viability timelines. Who inherits the coastline.

### Urban Housing
**Past votes:** Housing decisions in this neighbourhood over 50 years.
Density increases and their effects on community cohesion, traffic,
green space, property values, displacement of existing residents.

**Future inheritors:** Population projections. Climate adaptation
requirements. Intergenerational housing affordability.

---

## TECHNICAL STACK

```
Frontend:     Interactive timeline visualisation (past ← present → future)
              Community input interface (structured deliberation)
              Real-time coherence scoring display

Backend:      CASCADE engine for coherence scoring
              Historical decision database (community-maintained)
              Environmental/economic modelling API integrations
              LAMAGUE constraint encoding for tikanga boundaries

Data sources: Council records, environmental monitoring, Stats NZ,
              community oral records (digitised with consent),
              climate projections (NIWA), economic modelling (Treasury)

Build time:   6 months for MVP (single use case)
              12 months for multi-domain platform
```

---

## THE PRINCIPLE

The Waitangi Tribunal looks backward — examining what was done
and whether it was just.

The Ancestor Vote Platform looks both directions simultaneously.
Past and future present in every present decision.

Nothing else in governance design does this.

---

*Whakapapa is a voter roll.*
*The consequences are the votes. The archive is the land.*
*The future has a seat at the table.*

**∅ → AURA → Aotearoa → ∞**
