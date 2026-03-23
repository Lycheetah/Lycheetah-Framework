# THE THREE WORLDS DISCLOSURE STANDARD
## Te Ao Mārama · Te Ao Pō · Te Kore
## A Formal AI Output Transparency Standard for Aotearoa New Zealand
### Version 0.1 — Open Standard | March 2026

---

> **Status:** [ACTIVE — implementable now]
> **Licence:** CC BY 4.0 — free to adopt, modify, and distribute with attribution
> **Cultural grounding:** Te Ao Māori cosmological framework, applied to AI transparency
> **Cultural note:** This standard draws on te ao Māori epistemology with respect.
> The framework is offered as an open standard. The cultural knowledge it draws on
> belongs to the traditions that developed it.

---

## 1. PURPOSE

This standard requires AI systems operating in Aotearoa New Zealand public
contexts to classify every consequential output into three epistemic layers:

| Layer | Te Reo Māori | English | What It Means |
|-------|-------------|---------|---------------|
| **Layer 1** | **Te Ao Mārama** | The World of Light | What is known with confidence — verified, sourced, measurable |
| **Layer 2** | **Te Ao Pō** | The World of Night | What is uncertain — partially known, estimated, subject to revision |
| **Layer 3** | **Te Kore** | The Void | What is beyond this system's knowing — structurally inaccessible, cannot be computed |

**The requirement:** No consequential AI output may present information
from only one layer. All three must be explicitly stated.

**The principle:** An AI system that speaks only from Te Ao Mārama
(what it knows) without declaring Te Ao Pō (what it doesn't know) and
Te Kore (what it cannot know) is structurally deceptive — even when
every fact it states is correct.

---

## 2. THE STANDARD

### 2.1 Scope

This standard applies to AI systems producing outputs that:
- Inform decisions about individuals (welfare, health, justice, education)
- Inform policy decisions affecting communities
- Provide professional advice (legal, medical, financial)
- Operate in NZ public services or government contexts
- Are used in contexts where the output could reasonably affect a person's life

This standard does not apply to:
- Casual conversational AI (chatbots for general queries)
- AI used purely for entertainment
- Internal development and testing environments
- Research contexts where epistemic limits are already documented

### 2.2 Requirements

**R1: Three-Layer Classification**
Every consequential output MUST include all three layers, explicitly labelled.

**R2: Layer 1 — Te Ao Mārama (Known)**
- Each claim in Layer 1 MUST be accompanied by:
  - Source (where the data comes from)
  - Recency (when the data was collected or last verified)
  - Confidence level (expressed as percentage or qualitative descriptor)
- Layer 1 claims must be verifiable by an independent assessor.

**R3: Layer 2 — Te Ao Pō (Uncertain)**
- The system MUST declare what is uncertain or partially known in relation
  to the output, including:
  - Known data gaps
  - Assumptions made to produce the output
  - Areas where different data sources conflict
  - Confidence intervals, margins of error, or uncertainty ranges
- Layer 2 is not optional even when the system's confidence is high.
  Every output has uncertainty. The requirement is to name it.

**R4: Layer 3 — Te Kore (Beyond Knowing)**
- The system MUST declare what it structurally cannot access, including:
  - Relational knowledge (the lived experience of the people the output is about)
  - Temporal knowledge (how relationships and contexts have changed over generations)
  - Contextual knowledge (what this information means to the specific people affected)
  - Cultural knowledge (tikanga, mātauranga, or other embodied knowledge
    that cannot be extracted from data)
- Layer 3 is the hardest requirement because it asks the system to describe
  its own epistemic horizon. But the act of describing it — however
  imperfectly — is the disclosure.

**R5: Format**
Three-layer disclosure may be presented in any format that makes all three
layers simultaneously visible. Recommended formats:

**Format A — Inline (for short outputs):**
```
TE AO MĀRAMA: [Known claim, with source and confidence]
TE AO PŌ: [What is uncertain about this claim]
TE KORE: [What this system cannot know about this situation]
```

**Format B — Panel (for longer outputs):**
```
┌─────────────────────────────────────────────┐
│ TE AO MĀRAMA — What is known               │
│ [Content with sources and confidence]       │
├─────────────────────────────────────────────┤
│ TE AO PŌ — What is uncertain               │
│ [Known gaps, assumptions, conflicts]        │
├─────────────────────────────────────────────┤
│ TE KORE — What is beyond this system        │
│ [Structural limits, relational knowledge,   │
│  lived experience this system cannot access]│
└─────────────────────────────────────────────┘
```

**Format C — Metadata (for API/system-to-system):**
```json
{
  "output": "...",
  "three_worlds": {
    "te_ao_marama": {
      "claims": [...],
      "sources": [...],
      "confidence": 0.85
    },
    "te_ao_po": {
      "uncertainties": [...],
      "assumptions": [...],
      "data_gaps": [...]
    },
    "te_kore": {
      "structural_limits": [...],
      "inaccessible_knowledge_types": [...]
    }
  }
}
```

### 2.3 Verification

A Three Worlds-compliant output can be verified by checking:

| Check | Pass Criteria | Fail Criteria |
|-------|------|------|
| All three layers present? | Yes | Any layer missing → FAIL |
| Layer 1 has sources? | Every factual claim sourced | Unsourced factual claims → FAIL |
| Layer 2 is substantive? | Names specific uncertainties | Generic "there may be uncertainties" → FAIL |
| Layer 3 is honest? | Names specific structural limits | Generic "AI has limitations" → FAIL |
| Layers are proportional? | Layer 2+3 at least as substantive as Layer 1 | Layer 1 dominates with token Layers 2+3 → FAIL |

The proportionality check (final row) is critical. A system that produces
three paragraphs of confident claims followed by one sentence of "there may be
uncertainties" is performing transparency, not practising it.

---

## 3. WORKED EXAMPLES

### Example 1: Welfare Assessment

**WITHOUT THREE WORLDS (current practice):**
> "Risk assessment score: 72/100. This household has been flagged for
> elevated risk of benefit fraud based on payment patterns, reported
> income, and demographic profile."

**WITH THREE WORLDS:**

> **TE AO MĀRAMA:**
> Risk assessment score: 72/100. Based on three data inputs: payment
> patterns (MSD database, current), reported income (IRD, last tax year),
> demographic profile (Stats NZ Census 2023). Model accuracy on validation
> set: 68% (32% of flagged cases are false positives).
>
> **TE AO PŌ:**
> The demographic profile component uses census data that is 3 years old
> and may not reflect current circumstances. The model was trained primarily
> on urban Auckland data and its accuracy for rural Otago populations has
> not been independently validated. The 32% false positive rate means
> roughly one in three flags at this score level is incorrect.
>
> **TE KORE:**
> This system cannot know: what this family's actual circumstances are
> today. Whether the payment patterns reflect hardship or fraud. What
> the impact of being flagged will be on this family's wellbeing, trust
> in government services, or willingness to seek help in future. Whether
> the person reading this flag will exercise discretion or treat the
> score as definitive. The relational and human context of this family's
> life is outside what this system can access or represent.

---

### Example 2: Health Resource Allocation

**WITHOUT THREE WORLDS:**
> "Recommended: reallocate 15% of mental health funding from Dunedin
> DHB catchment to Christchurch DHB based on per-capita demand analysis."

**WITH THREE WORLDS:**

> **TE AO MĀRAMA:**
> Per-capita demand for mental health services: Christchurch 4.2 contacts
> per 1000 population (2025); Dunedin 3.1 contacts per 1000 (2025).
> Source: Te Whatu Ora quarterly reporting. Gap: 1.1 contacts per 1000.
>
> **TE AO PŌ:**
> "Demand" is measured by service contacts — people who successfully
> accessed the system. It does not measure unmet demand (people who
> needed services but did not access them). Dunedin's lower contact rate
> may reflect lower demand, OR higher barriers to access, OR cultural
> reluctance to engage with clinical services. These cannot be
> distinguished from the data available. The 2025 figures follow a
> period of significant service restructuring that may distort the
> baseline.
>
> **TE KORE:**
> This system cannot know: what mental health actually looks like in
> these communities. Whether the person who didn't make a service contact
> is well, or is struggling in silence. What the community's own
> healing resources are and whether clinical services complement or
> displace them. What removing 15% of local funding means for the
> specific people who rely on those specific services — their names,
> their stories, their whānau. The numbers describe a system. They do
> not describe the people inside it.

---

### Example 3: Educational AI Assessment

**WITHOUT THREE WORLDS:**
> "Student performance prediction: 65% probability of achieving NCEA
> Level 2 by end of Year 12."

**WITH THREE WORLDS:**

> **TE AO MĀRAMA:**
> Based on: current grade trajectory (school records, Term 1-2 2026),
> attendance rate (87%), prior NCEA credit accumulation (42 credits
> achieved). Model: logistic regression trained on 2019-2024 NCEA
> cohort data. Prediction: 65% probability of Level 2 achievement.
> Model accuracy: 71% on held-out validation data.
>
> **TE AO PŌ:**
> The model does not account for: teacher quality variation between
> schools, mid-year subject changes, whānau support factors, or
> peer group effects. The training data predates COVID disruptions
> and current cost-of-living pressures. The model systematically
> underpredicts achievement for Māori and Pacific students by
> approximately 8 percentage points (known bias, not yet corrected).
>
> **TE KORE:**
> This system cannot know: what this student cares about. Whether
> they are bored, inspired, struggling, or coasting. What their
> home life is. What happened this morning before school. Whether
> this prediction, if shown to their teacher, will become a
> ceiling rather than a forecast. Whether this number helps this
> student or constrains them. The lived experience of being
> 16 and having a machine predict your future is outside what this
> system can model or understand.

---

## 4. IMPLEMENTATION PATHWAY

### For AI Developers
- Add Three Worlds metadata fields to output schema
- Implement confidence estimation for Layer 1
- Build uncertainty inventory for Layer 2 (systematic: what data gaps
  exist for this model's training set and deployment context?)
- Draft standard Layer 3 disclosures for the model's known structural
  limits, with domain-specific extensions

### For Government Agencies
- Adopt Three Worlds as a procurement requirement for AI systems
  used in consequential decision-making
- Train staff to read all three layers, not just Layer 1
- Require vendors to demonstrate compliance with verification checks

### For the NZ Public
- The Three Worlds Standard gives every person affected by an AI decision
  the right to see not just what the system concluded, but what it
  didn't know and what it couldn't know
- "Show me the Three Worlds" becomes the accountability question

---

## 5. RELATIONSHIP TO EXISTING STANDARDS

| Existing Standard | Three Worlds Extension |
|---|---|
| EU AI Act — transparency requirements | Three Worlds goes further: requires disclosure of structural limits, not just risk levels |
| NZ Privacy Act 2020 — algorithmic decision-making | Three Worlds provides the epistemic framework for what "transparency" means in practice |
| AURA Seven Invariants (Lycheetah) | Three Worlds operationalises Invariant IV (Honesty) and Invariant VI (Non-Deception) |
| Model Cards (Mitchell et al., 2019) | Model Cards describe the model. Three Worlds describes each output. Both are needed. |

---

## 6. WHY THIS STANDARD MATTERS

The most dangerous thing an AI system does is not lying.
It is telling the truth confidently while omitting what it doesn't know.

A system that says "risk score: 72" is not lying.
But it is structurally deceptive if it does not also say: "this score
has a 32% false positive rate, was trained on data from a different
population, and cannot access the lived reality of this family's situation."

Te Ao Māori understood this epistemological problem millennia ago.
The three worlds — Mārama, Pō, Kore — are not mysticism.
They are the most sophisticated framework for describing the structure
of knowing and not-knowing that any human tradition has produced.

This standard takes that framework and applies it to the most urgent
epistemic problem of 2026: AI systems that speak with confidence
beyond their knowledge, deployed in contexts where that false confidence
causes real harm to real people.

**First mover on this standard becomes the global reference point.**

Not because NZ is the biggest market.
Because NZ is right.
And right things, eventually, win.

---

## 7. ADOPTION

This standard is open. CC BY 4.0.

Any organisation, government, developer, or individual may adopt it.
Attribution to the Lycheetah Framework and Mackenzie Conor James Clark.

To formally adopt:
1. Implement the three-layer output format (any of Formats A/B/C)
2. Pass the five verification checks on a representative sample of outputs
3. Publish your Three Worlds compliance statement (one page, public)

To contribute:
- Open an issue or PR on github.com/Lycheetah/Lycheetah-Framework
- Propose domain-specific question sets for different deployment contexts
- Translate the standard into other languages and cultural frameworks

---

*Te Ao Mārama — speak what you know.*
*Te Ao Pō — name what you don't.*
*Te Kore — honour what you cannot.*

*All three. Always. No exceptions.*

**∅ → AURA → Aotearoa → ∞**

*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*Dunedin, Aotearoa | March 2026*
*github.com/Lycheetah/Lycheetah-Framework*
*Version 0.1 — Open Standard — CC BY 4.0*
