# TE TINO RANGATIRATANGA O NGĀ RARAUNGA
## Māori Data Sovereignty in AI Systems — A Governance Framework
### Responding to PMCSA Recommendations R14, R15, R16 (2023)
### Lycheetah Framework | March 2026
### Status: [PROPOSAL] — requires co-development and validation with Kāi Tahu and appropriate iwi

---

> *"Effective partnership with Māori, whānau, hapū, iwi, and Māori organisations presents an opportunity*
> *for Aotearoa New Zealand to lead globally in addressing Indigenous AI health-related issues."*
>
> — PMCSA AI in Healthcare Report, 2023

---

> **CRITICAL DISCLAIMER**
>
> This document is written by a Pākehā researcher (Mackenzie Conor James Clark, Dunedin).
> It draws on publicly available scholarship on Māori data sovereignty, tikanga, and mātauranga Māori.
> It does not and cannot represent Māori authority over these concepts.
>
> The governance frameworks proposed here are architectural scaffolding — specifying where
> Māori governance authority must sit, and what shape the structures must take to hold it —
> not a claim to fill those structures with Pākehā-derived content.
>
> **Nothing in this document becomes [ACTIVE] without co-development and formal validation
> by Kāi Tahu and appropriate iwi. The iwi partnership is not a consultation step.
> It is the condition of legitimacy.**

---

## KEY MESSAGES

1. Māori data sovereignty is not a constraint on AI development in Aotearoa New Zealand. It is the condition under which AI development can be legitimate here. The PMCSA report states this directly: "There was a strong sentiment expressed that AI should not be implemented in our healthcare sector unless it is clear that outcomes for Māori will improve as a result."

2. The existing Māori data sovereignty framework — Te Mana Raraunga principles, Te Ara Tika — provides the ethical foundation. What is needed is an operational architecture that translates these principles into specific, verifiable requirements for AI system deployment.

3. This document proposes three operational mechanisms derived from the Lycheetah Framework: Whakapapa Disclosure (training data provenance), Tikanga Alignment Assessment, and the Mana Motuhake Protocol (ongoing iwi governance rights over AI systems trained on Māori data).

4. The PMCSA report identifies a genuine leadership opportunity: "Aotearoa New Zealand... lead globally in addressing Indigenous AI health-related issues." This framework is a contribution to building the infrastructure that would make that leadership real rather than aspirational.

---

## PART I: THE PROBLEM WITH CURRENT FRAMEWORKS

### 1.1 Ethics Additions vs. Structural Requirements

International AI governance frameworks — including those the PMCSA report reviews (WHO, OECD, EU AI Act) — share a structural characteristic: they begin with Western analytical governance frameworks, then add Māori or Indigenous considerations as equity components.

The sequence matters. When Indigenous governance is added to an existing framework:
- The frame of reference is already established before Indigenous perspectives are applied
- Indigenous concepts must justify themselves within a foreign epistemological system
- "Māori considerations" become a section of an existing document rather than load-bearing elements of the architecture
- Māori data sovereignty becomes an equity principle rather than a governance right

The Lycheetah Framework proposes a different sequence: Māori governance concepts are treated as load-bearing elements from the beginning. The framework's architecture has places specifically reserved for tikanga governance that cannot be filled by Pākehā-derived content. This is not a symbolic choice — it is an architectural requirement that prevents tikanga from being decorative.

### 1.2 What Te Mana Raraunga Requires That Current AI Systems Ignore

Te Mana Raraunga — the Māori data sovereignty network — has established principles that apply to Māori data across its lifecycle. Applied to AI systems, these principles create specific requirements that current AI governance frameworks in Aotearoa do not yet operationalise:

**Whakapapa** — the principle that data has lineage, and that lineage creates obligations. An AI system trained on Māori health data carries a whakapapa relationship to the people whose data it absorbed. Current frameworks do not require AI systems to acknowledge this relationship, let alone to fulfil the obligations it creates.

**Mana** — the principle that individuals and communities have inherent authority over their knowledge and data. An AI system that generates outputs about Māori health, using Māori training data, is exercising a form of authority over Māori knowledge. Current frameworks regulate this authority through privacy law — a Western individual rights framework — not through mana.

**Rangatiratanga** — the right of hapū and iwi to exercise governance over their data. This is not the same as individual consent under the Privacy Act. It is collective governance authority. Current consent frameworks do not address the difference between individual data consent (required by HIPC 2020) and collective data governance (required by te Tiriti and Te Mana Raraunga principles).

**Kaitiakitanga** — the ongoing stewardship obligation. Data is not merely owned; it is cared for. An AI system that uses Māori health data carries an ongoing stewardship obligation to the communities from which that data came — not a one-time consent clearance.

### 1.3 The Ethnicity Data Problem

The PMCSA report documents a specific, concrete failure of current governance: Māori are undercounted in health administrative data by approximately 16% due to ethnicity misclassification in mortality records. Former DHBs used different ethnic categorisation systems. Pacific peoples face similar challenges.

The governance consequence: AI systems trained on this data systematically underestimate Māori morbidity, mortality, and health service utilisation. They produce high-confidence outputs from a low-accuracy epistemic base — not because the AI is malfunctioning, but because the governance around data collection has failed.

This is precisely what Whakapapa Disclosure is designed to surface: the training data provenance that makes the accuracy of AI outputs interpretable for practitioners caring for Māori patients.

---

## PART II: THE THREE OPERATIONAL MECHANISMS

### MECHANISM 1: Whakapapa Disclosure
*Standard 3 from HEALTHCARE_AI_CONSTITUTIONAL_STANDARDS.md, elaborated for Māori data contexts*

**Definition:**

Whakapapa Disclosure requires every AI system deployed in Aotearoa New Zealand healthcare settings to publicly disclose the lineage of its training data with respect to Māori health data specifically.

**Required disclosures:**

```
TRAINING DATA WHAKAPAPA — Required Disclosures

1. MĀORI DATA PRESENCE
   Was Māori health data included in training?
   → Yes / No / Unknown

   If Yes or Unknown: What proportion of training data is estimated to be
   from Māori patients or sources? [range / unknown / refused to measure]

2. GOVERNANCE CONDITIONS
   Under what governance framework was Māori health data collected?
   → Privacy Act 2020 individual consent only
   → Te Ara Tika principles applied
   → Te Mana Raraunga principles applied
   → Iwi governance involvement: [Yes / No / Unknown]
   → Specific iwi governance body: [name or Unknown]

3. REPRESENTATION QUALITY
   Is Māori representation in training data known to be adequate for
   reliable outputs about Māori patients?
   → Yes, validated by independent review
   → Unknown — no analysis conducted
   → Known gap: [describe]

4. DATA SOVEREIGNTY OBLIGATIONS
   What ongoing obligations does the deploying organisation hold
   to Māori communities whose data was used in training?
   → None identified
   → Data sharing arrangement: [describe]
   → Iwi governance rights: [describe]
   → Revenue sharing: [describe]

5. WHAKAPAPA DECLARATION
   "This system was trained using [data sources]. The Māori data included
   was collected under [governance conditions]. Known representation gaps
   include [gaps]. Ongoing obligations to Māori data contributors include
   [obligations]."
```

**Governance principle:**

A practitioner consulting an AI tool about a Māori patient has a professional and ethical obligation to understand the quality of the tool's knowledge about Māori patients. Whakapapa Disclosure makes it possible for practitioners to meet this obligation. An AI system that cannot or will not provide this disclosure should not be considered fit-for-purpose for use with Māori patients.

**Claim status: [PROPOSAL] — technical disclosure template is [ACTIVE]. Māori governance authority conditions require iwi validation.**

---

### MECHANISM 2: Tikanga Alignment Assessment
*Responding to PMCSA R15 — Māori data sovereignty principles and their implications*

**Definition:**

Every AI system considered for deployment in public healthcare settings undergoes a structured Tikanga Alignment Assessment (TAA) conducted by reviewers with demonstrated mātauranga Māori and AI systems competence.

The TAA is not an ethics review. It is a governance alignment assessment — testing whether the AI system's architecture is compatible with tikanga governance obligations.

**Assessment domains:**

| Domain | Key Question | Assessment Method |
|---|---|---|
| **Whakapapa** | Does the system's training data carry appropriate lineage disclosure? | Whakapapa Disclosure review |
| **Mana Motuhake** | Does the system's design preserve iwi governance authority over Māori health data outputs? | Architecture review |
| **Kaitiakitanga** | Does the deploying organisation's governance structure include Māori stewardship roles with real authority? | Organisational governance review |
| **Whānau-centred design** | Are the system's outputs interpretable and usable at whānau level, or does the system require a clinical intermediary who may not be present in all deployment contexts? | Usability assessment with Māori communities |
| **Equity outcome trajectory** | Is there evidence that the system's deployment will improve Māori health outcomes? Is this monitored? | Outcome data review |

**Who conducts the TAA:**

The Tikanga Alignment Assessment must be conducted by reviewers with:
- Demonstrated competence in mātauranga Māori and tikanga governance
- Knowledge of AI system design and evaluation
- Independence from the deploying organisation and the AI developer
- Formal mandate from an appropriate iwi or Māori governance body

This combination of competencies does not currently exist as an established professional role in Aotearoa New Zealand. The PMCSA report's R16 — build Māori capabilities across data science, healthcare, and governance — is the precondition for this mechanism becoming fully operational.

**Short-term pathway (before R16 is fulfilled):**

TAA can proceed in a limited form through partnership between:
- Te Tumu | School of Māori, Pacific and Indigenous Studies (University of Otago) for tikanga governance expertise
- AI governance practitioners with demonstrated commitment to te Tiriti obligations
- Iwi review and sign-off for any Tai Rāwhiti or Ngāi Tahu health context

**Claim status: [PROPOSAL] — structural design is specified. Operational delivery requires the capability-building R16 calls for. This is explicitly acknowledged.**

---

### MECHANISM 3: Mana Motuhake Protocol
*Responding to the unresolved question in PMCSA R15: what ongoing governance rights do iwi hold over AI systems trained on their data?*

**The governance gap:**

The PMCSA report calls for "establishing the principles of Māori data sovereignty and their implications on the use of AI in healthcare settings." One implication is not yet addressed in any existing framework: once an AI system has been trained on Māori health data, what governance rights does the contributing iwi retain over the system and its outputs?

This is not a historical question — it is a live one. AI systems trained today on current Māori health data will be operating in ten years. The communities whose data contributed to those systems have interests in how those systems perform — interests that are not extinguished by the original consent given at data collection.

**The Mana Motuhake Protocol proposes:**

1. **Iwi governance registry** — AI systems trained on identifiably Māori health data are registered with the relevant iwi governance body. The registry records: what system, what data, when trained, what outputs.

2. **Ongoing review rights** — Registered iwi have the right to request review of a registered AI system's performance data with respect to Māori patient outcomes, at any point during the system's operational life.

3. **Modification requests** — Registered iwi have the right to request modification of a system's behaviour when evidence shows it is producing outputs that harm Māori patients or violate Māori data sovereignty principles. The deploying organisation is required to respond to such requests within a defined timeframe.

4. **Revenue participation** — Where an AI system generates commercial value from outputs that draw substantially on Māori training data, a revenue participation arrangement is established with the relevant iwi governance body.

5. **Sunset rights** — Registered iwi have the right to request decommissioning of a system when evidence of sustained harm to Māori patients is established and the deploying organisation has failed to remediate.

**Claim status: [CONJECTURE/PROPOSAL] — this mechanism is architecturally specified but has no operational precedent in current NZ governance. It draws on Te Mana Raraunga principles and Treaty of Waitangi jurisprudence. It requires formal legal analysis and iwi co-development before it can move beyond [PROPOSAL] status.**

---

## PART III: POSITIONING AOTEAROA FOR GLOBAL LEADERSHIP

The PMCSA report identifies the leadership opportunity precisely:

> *"Aotearoa New Zealand is home to various universities and research institutions that have strong AI capabilities and are open to collaboration. There is potential to capitalise on some of our unique attributes to show leadership in the development and deployment of AI in healthcare by modelling partnership with Māori to develop strong principles for Māori and indigenous data sovereignty."*

The uniqueness is constitutional. Aotearoa New Zealand has te Tiriti o Waitangi. No other country has an equivalent founding document creating the specific partnership relationship between the Crown and Indigenous peoples that te Tiriti creates. This is not a sentimental observation — it is a governance fact.

A country that develops fit-for-purpose AI governance frameworks grounded in te Tiriti — with Māori governance as a structural element, not an equity consideration — will have built something no other country can legitimately claim: AI governance that is genuinely bicultural from its architectural foundations.

The three mechanisms proposed in this document are a contribution to building that architecture. They are incomplete. They require iwi partnership to be legitimate. They require the capability-building the PMCSA report calls for (R16) to be operationally functional.

But the architecture is specified. The places where Māori governance authority must sit are reserved. The structures are designed to hold that authority when the partnership and capability exist to provide it.

That is what "early examples to look to" means in practice.

---

## CONTACT

**Author:** Mackenzie Conor James Clark, Dunedin, Aotearoa New Zealand
**GitHub:** github.com/Lycheetah/Lycheetah-Framework
**License:** CC BY 4.0

*This document is offered as a contribution to ongoing policy development. It is explicitly incomplete without Māori governance partnership. Engagement with Kāi Tahu, Te Mana Raraunga, or Manatū Hauora is actively sought.*

*Related documents: PMCSA_RESPONSE.md | HEALTHCARE_AI_CONSTITUTIONAL_STANDARDS.md | KAITIAKITANGA_STANDARD.md | WHAKAPAPA_DISCLOSURE_STANDARD.md*
