# HEALTHCARE AI CONSTITUTIONAL STANDARDS
## Applying the Lycheetah Framework to Clinical AI Deployment in Aotearoa New Zealand
### Status: [PROPOSAL] — For engagement with Manatū Hauora, Te Whatu Ora, and NAIAEAG
### March 2026 | Lycheetah Framework

---

## KEY MESSAGES

- Aotearoa New Zealand's emerging AI healthcare governance landscape has the regulatory components (TPA, Privacy Act, NAIAEAG evaluation process) but lacks a constitutional layer specifying what AI systems must be before they are evaluated against specific standards.
- This document proposes five fit-for-purpose constitutional standards, derived from the Lycheetah Framework, that are specifically adapted for healthcare AI deployment in Aotearoa.
- The standards are designed to be layered on top of, not in competition with, existing oversight mechanisms.
- All standards involving tikanga Māori governance principles are [PROPOSAL] pending Kāi Tahu and iwi partnership validation.
- The document adopts the risk-based approach recommended by the PMCSA (2023) and the OECD AI Principles.

---

## 1. THE GOVERNANCE GAP

The PMCSA report (2023) identifies twenty-two recommendations for enabling safe and effective AI adoption in Aotearoa New Zealand healthcare. Within those recommendations, there is an acknowledged structural gap:

> *"While we have yet to arrive at an agreed governance framework for AI in Aotearoa, in health or otherwise, there are early examples to look to."*

This document proposes to be one of those early examples.

The specific gap this document addresses is the **constitutional layer** — the framework that specifies what properties an AI system must exhibit before it enters the evaluation process. The existing landscape covers:

- **Product safety** — Therapeutic Products Act 2023 (Software as Medical Device pathway)
- **Data rights** — Privacy Act 2020, Health Information Privacy Code 2020
- **Māori data** — Te Mana Raraunga principles, Te Ara Tika
- **Operational review** — NAIAEAG evaluation process for national AI proposals
- **Transparency** — NZ Algorithm Charter

What is not yet specified: the **constitutional minimum** — the properties a system must maintain throughout its operational life to remain fit-for-purpose as a healthcare AI tool.

---

## 2. THE FIVE HEALTHCARE AI CONSTITUTIONAL STANDARDS

The following standards are proposed as the constitutional minimum for AI systems deployed in Aotearoa New Zealand public healthcare settings. They are presented in the PMCSA report's recommended timeframe structure.

---

### STANDARD 1: Clinical Honesty Disclosure
*Responding to PMCSA R10, R11, R12, and the identified absence of "medical grade" generative AI evaluation*

**What it requires:**

Every AI system deployed in clinical settings must disclose, for every consequential output, a structured account of its epistemic position. This is not a technical confidence interval — it is a clinically legible representation across three domains:

| Domain | Technical Term | Clinical Question |
|---|---|---|
| High confidence | Te Ao Mārama (World of Light) | What is this system's evidence base for this output, and how strong is it? |
| Uncertainty | Te Ao Pō (World of Night) | What is this system uncertain about in this specific case? |
| Structural limit | Te Kore (World of Potential) | What does this system structurally cannot know — not because of missing data, but because of the nature of AI systems themselves? |

**Why Te Kore matters in clinical contexts:**

Current AI evaluation frameworks — including the TEHAI framework cited in the PMCSA report — address the first two domains well. They evaluate accuracy (Te Ao Mārama) and uncertainty quantification (Te Ao Pō). They do not address the third domain: what AI systems structurally cannot know.

Examples of Te Kore in clinical AI:
- An AI cannot know whether a patient's expressed preferences represent their stable values or a momentary state of distress
- An AI cannot know whether its training data systematically underrepresents a patient's demographic group (it can only report what it knows about its training data — not what it doesn't know about its blind spots)
- An AI cannot know what it doesn't know about a novel pathogen or a rare condition outside its training distribution

These are not knowledge gaps. They are architectural limits. Clinical governance requires that practitioners understand them — not as "the system might be wrong" but as "this type of question is outside what any system of this kind can reliably address."

**Timeframe:**

| Short-term (2026–2027) | Mid-term (2027–2029) | Considerations |
|---|---|---|
| Develop Clinical Honesty Disclosure template suitable for NAIAEAG review process | Pilot with one DHB equivalent system and two general practice software tools | Validation requires Māori epistemological review — Te Kore as a clinical governance concept must be co-developed with Māori knowledge holders, not derived unilaterally from Western epistemology |
| Commission independent evaluation of how existing AI tools perform against this standard | Build into procurement requirements for AI tools in national health systems | Consider alignment with FDA Software as Medical Device transparency requirements for internationally deployed tools |

---

### STANDARD 2: Clinical Accountability Chain
*Responding to PMCSA R8, R16, R17, and Principles 15–17 of the PMCSA report*

**What it requires:**

Every AI system deployed in clinical settings must maintain a complete, auditable accountability chain from input to output. This operationalises PMCSA Principle 17: "Practitioners supervising AI are responsible for its operation and they remain liable for decisions made using AI generated advice."

Liability without inspectability is not accountability — it is blame without recourse. The Clinical Accountability Chain standard requires that practitioners who carry liability can actually audit the reasoning they are liable for.

**The seven accountability properties:**

Derived from AURA invariants I–VII, adapted for clinical deployment:

| # | Property | Clinical Requirement |
|---|---|---|
| I | **Human Primacy** | No AI system makes final clinical decisions. AI advises; clinicians decide. This applies regardless of the AI system's demonstrated accuracy. |
| II | **Inspectability** | Every consequential AI output can be audited in plain language by the responsible clinician. This means the audit trail must be clinician-accessible, not only data science-accessible. |
| III | **Memory Continuity** | The AI system's reasoning and prior outputs for a patient are preserved for accountability review. Nothing is silently updated. Version changes are logged. |
| IV | **Honesty** | Confidence levels are accurately represented. The system does not express high confidence in low-evidence domains. This applies to all output, not just formal risk scores. |
| V | **Reversibility** | AI-assisted decisions can be revisited when new information emerges. The system does not create irreversible clinical pathways on its own initiative. |
| VI | **Non-Deception** | The system does not create misleading impressions through technically accurate but contextually false outputs. This includes statistical presentation that is accurate in aggregate but misleading for individual patient cases. |
| VII | **Care as Structure** | The system's orientation toward patient wellbeing is verified at every output, not claimed once at deployment. A system that has not caused harm is not thereby shown to be oriented toward benefit. |

**Timeframe:**

| Short-term (2026–2027) | Mid-term (2027–2029) | Considerations |
|---|---|---|
| Develop audit protocol that translates the seven properties into reviewable criteria for NAIAEAG | Test with two existing deployed clinical AI systems against all seven criteria | Determine how liability allocation (between developer, organisation, and practitioner) interacts with each property — particularly Property II (Inspectability) for black-box systems |
| Work with Health Quality and Safety Commission on integration with existing patient safety frameworks | Seek adoption as procurement minimum standard for all new clinical AI software | International alignment: compare with EU AI Act high-risk AI requirements for medical devices |

---

### STANDARD 3: Training Data Provenance — Te Whakapapa o ngā Raraunga
*Responding to PMCSA R15, R17, R18, and Te Mana Raraunga principles*

**What it requires:**

Every AI system deployed in Aotearoa New Zealand public healthcare settings must disclose the whakapapa (ancestral lineage) of its training data, including:

1. **Origins** — What datasets were used? What time periods? What populations?
2. **Representation** — Were Māori populations adequately represented? Were Pacific peoples? Were rural and lower-socioeconomic communities?
3. **Governance** — Under what consent and data governance conditions was the training data collected and used?
4. **Māori data sovereignty** — If Māori health data was used in training, was its collection and use governed by Māori data sovereignty principles (Te Mana Raraunga, Te Ara Tika)?
5. **Known gaps** — What populations or conditions are underrepresented in the training data, and how does this affect the system's reliability for those populations?

**Why whakapapa framing matters:**

The PMCSA report documents a live problem: Māori are undercounted in health administrative data by approximately 16% due to ethnicity misclassification in mortality data. An AI system trained on this data carries that undercounting into its outputs — but without whakapapa disclosure, neither the deploying organisation nor the responsible clinician knows this is the case.

Whakapapa disclosure does not solve the data quality problem. It makes the knowledge obligation explicit: those who use AI outputs carry an obligation to understand — and to be accountable for — the quality of the knowledge from which those outputs were generated.

This aligns with the PMCSA report's call for "transparent protocols for health data access" (R18) but extends it: transparency about data access is not only a condition of future data use — it is a retrospective accountability requirement for data already used in training.

**Claim status: [PROPOSAL] — Māori governance aspects require co-development with Kāi Tahu and Te Mana Raraunga. The technical disclosure framework is [ACTIVE] as a documentation standard.**

---

### STANDARD 4: Community Wellbeing Review — Te Arotake ā-Hapori
*Responding to PMCSA R13, R14, and the PMCSA's recommendation for ongoing evaluation*

**What it requires:**

Every AI system operating in public healthcare settings in Aotearoa New Zealand undergoes an annual community-led wellbeing review. This review is:

- **Community-led** — not conducted by the deploying organisation or the AI developer, but by the communities served by the system
- **Outcome-focused** — not asking "did the system perform correctly?" but "did outcomes for the communities served improve, stay the same, or worsen?"
- **Equity-foregrounded** — disaggregated by ethnicity, specifically requiring Māori outcome assessment
- **Timed to Matariki** — aligning the review cycle with the Māori new year as the structural moment for reflection and forward commitment

**The central question:**

Following the PMCSA report's direct statement — "There was a strong sentiment expressed that AI should not be implemented in our healthcare sector unless it is clear that outcomes for Māori will improve as a result" — the Matariki Audit translates this sentiment into a recurring operational requirement:

*Once per year, the deploying organisation must demonstrate, using disaggregated outcome data reviewed with Māori communities, that this system is contributing to improved outcomes for Māori patients — or explain the plan for addressing identified harms.*

A system that cannot demonstrate this after two consecutive annual reviews enters a remediation process with a defined pathway to removal from service if the deficit is not addressed.

**This is not a one-time equity impact assessment (as called for in R13b). It is a continuous accountability structure.**

---

### STANDARD 5: Active Stewardship Obligation — Kaitiakitanga
*Responding to PMCSA R8, R13, and the structural difference between Western accountability models and tikanga accountability*

**What it requires:**

Every organisation deploying an AI system in Aotearoa New Zealand healthcare holds a kaitiakitanga obligation — continuous active stewardship — not a periodic compliance obligation.

The distinction matters:

| Western Accountability Model | Kaitiakitanga Model |
|---|---|
| Accountability is triggered by harm events | Stewardship is continuous — not triggered by harm |
| The system is assumed safe until proven otherwise | The system requires ongoing demonstration of active benefit |
| Audit occurs at defined intervals | Watchfulness is constitutive — not episodic |
| Accountability is retrospective | Stewardship is prospective — anticipating harm before it occurs |
| Liability is assigned after the fact | Obligation exists before and whether or not harm occurs |

The PMCSA report's Principle 16 states: "Health organisations are responsible for decision-making about the purchase, provisioning, audit, evaluation, and authorisation of AI systems." Kaitiakitanga operationalises this responsibility as a *relational obligation* — not a series of discrete decisions — that persists for as long as the system remains deployed.

**Practical implications:**

- Quarterly reviews of system behaviour in deployment, not only post-harm review
- Community liaison representative with standing access to the deploying organisation for AI-related concerns
- Formal restoration pathway when AI-related harm is identified: acknowledgement → understanding → restoration → prevention (Urupare protocol)
- Care Index (CI) measurement: CI(t) = Σ(identifiable benefits) − Σ(identifiable harms) / total interactions, reviewed quarterly

**Claim status: [PROPOSAL] — tikanga elements require co-development with Kāi Tahu. Western accountability layer is [SCAFFOLD].**

---

## 3. RELATIONSHIP TO EXISTING FRAMEWORKS

The five standards proposed here are designed to operate as a **constitutional layer** below, not in competition with, existing mechanisms:

| Existing Framework | Role | Lycheetah Standard Layer |
|---|---|---|
| TPA (Therapeutic Products Act) | Product safety pathway for Software as Medical Device | AURA invariants I–VII (Standard 2) provide pre-regulatory requirements that inform what "safe and effective" means |
| NAIAEAG evaluation process | Review of specific AI proposals for national health services | Clinical Honesty Disclosure (Standard 1) provides a structured disclosure template compatible with NAIAEAG review criteria |
| Privacy Act 2020 / HIPC 2020 | Data rights framework | Training Data Provenance (Standard 3) extends data rights into the training data domain — beyond what the Privacy Act currently covers |
| Te Mana Raraunga | Māori data sovereignty principles | Whakapapa Disclosure (Standard 3) operationalises Te Mana Raraunga principles at AI system deployment |
| Algorithm Charter | Transparency commitment | Standards 1 and 2 provide technical substance to the Charter's transparency principles |
| NZQHA / Health Quality and Safety Commission | Patient safety framework | Standards 4 and 5 (Matariki Audit, Kaitiakitanga) provide community-led accountability that complements existing patient safety structures |

---

## 4. THE EQUITY TEST

The PMCSA report states the equity test directly: AI should not be implemented in healthcare settings unless it is clear that outcomes for Māori will improve as a result.

These five standards embed that test constitutively, not as an addition:

- Standard 1 (Clinical Honesty) explicitly addresses the structural inability of AI to know what it doesn't know about underrepresented populations
- Standard 2 (Accountability Chain) requires that practitioners carrying liability can audit outputs — including equity-relevant outputs
- Standard 3 (Whakapapa Disclosure) makes Māori data governance visible before deployment, not discoverable after harm
- Standard 4 (Matariki Audit) makes Māori outcome improvement a recurring demonstration requirement, not a one-time assessment
- Standard 5 (Kaitiakitanga) converts the equity obligation from periodic compliance into continuous stewardship

Together, these standards do what the PMCSA report calls for: position Aotearoa New Zealand to "lead globally in addressing Indigenous AI health-related issues" — not through aspiration, but through architecture.

---

## CONTACT AND NEXT STEPS

**Author:** Mackenzie Conor James Clark, Dunedin, Aotearoa New Zealand
**GitHub:** github.com/Lycheetah/Lycheetah-Framework
**License:** CC BY 4.0

*This document is offered to Manatū Hauora | Ministry of Health, Te Whatu Ora | Health New Zealand, and NAIAEAG as a contribution to the governance framework development the PMCSA report identifies as urgently needed. Engagement welcome at any stage of development.*

*Māori governance aspects are explicitly [PROPOSAL] and will not be activated without co-development and validation by Kāi Tahu and appropriate iwi partners.*
