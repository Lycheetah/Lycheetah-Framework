# RESPONSE TO PMCSA AI IN HEALTHCARE REPORT
## Lycheetah Framework — Submission to Ongoing Policy Development
### Responding to: *Capturing the Benefits of AI in Healthcare for Aotearoa New Zealand* (PMCSA, December 2023)
### Author: Mackenzie Conor James Clark, Independent Researcher, Dunedin | March 2026
### Status: [PROPOSAL] — Submission-ready, seeking policy engagement

---

> *"While we have yet to arrive at an agreed governance framework for AI in Aotearoa, in health or otherwise,*
> *there are early examples to look to."*
>
> — PMCSA AI in Healthcare Report, 2023

**The Lycheetah Framework is one of those examples.**

---

## KEY MESSAGES

1. The PMCSA report (December 2023) identifies the absence of an agreed governance framework for AI in Aotearoa New Zealand as its primary structural gap. The Lycheetah Framework directly addresses this gap with a deployable, Te Tiriti-grounded accountability architecture.

2. The Framework's five NZ AI accountability standards — AI WOF, Three Worlds Disclosure, Whakapapa Disclosure, Matariki Audit, and Kaitiakitanga Standard — map directly onto the PMCSA's eight governance themes and address specific recommendations by number.

3. The Framework does not compete with or duplicate existing oversight mechanisms (NAIAEAG, TPA regulatory pathway, Privacy Act 2020). It provides the constitutional layer underneath them — the framework that determines what "safe and effective" means before specific tools are assessed.

4. The Framework's treatment of Māori data sovereignty as a structural governance requirement (not an equity consideration added to an existing Western framework) responds directly to R14, R15, and R16 of the PMCSA report.

5. This response is submitted in the spirit of R22 — to contribute to "a range of networks to allow stakeholders to discuss relevant issues relating to AI in healthcare delivery."

---

## PART I: MAPPING LYCHEETAH TO PMCSA RECOMMENDATIONS

The PMCSA report structures its 22 recommendations across 8 themes. The following mapping shows where the Lycheetah Framework provides substantive technical and governance groundwork.

### Theme 4: Establishing Confidence and Trust

**R10 — Effective communication strategy**
**R11 — Training and information for stakeholders**

The Lycheetah Framework contributes a specific communication architecture: the Three Worlds Disclosure Standard. Every AI system operating in healthcare would be required to communicate:

- **Te Ao Mārama** — what it knows with high confidence and on what evidentiary basis
- **Te Ao Pō** — what it is uncertain about and the nature of that uncertainty
- **Te Kore** — what it structurally cannot know (not merely what it has not yet learned)

This standard addresses a failure mode the PMCSA report identifies explicitly: the inability of AI systems — particularly generative AI systems — to communicate their own limits to clinical users. The report notes: "For generative AI, on the other hand, best practice for evaluation has not been established... To date there is no such thing as 'medical grade' generative AI."

The Three Worlds Disclosure Standard provides a fit-for-purpose communication framework specifically because it distinguishes *temporary ignorance* from *structural unknowability* — a distinction essential in clinical contexts where AI systems are consulted about novel or edge cases outside their training distribution.

**Claim status: [ACTIVE] — Standard specified and documented. Validation in clinical communication contexts is [PROPOSAL] pending partnership.**

---

### Theme 5: Tackling Inequity

**R13 — Equity impact and bias assessment before launching any AI tool in the public healthcare system**

The Lycheetah Framework's Matariki Audit Standard directly addresses R13. The standard:

- Requires annual community-led wellbeing review of any deployed AI system
- Is timed to the Matariki calendar — aligning with the Māori new year as the structural moment for reflection on the previous year and commitments for the next
- Centres the question the PMCSA report names explicitly: "There was a strong sentiment expressed that AI should not be implemented in our healthcare sector unless it is clear that outcomes for Māori will improve as a result."

The Matariki Audit Standard converts this sentiment into an operational requirement: an AI system's continued deployment in public healthcare settings requires annual community-led evidence that outcomes for Māori are not worsening. This is not a one-time equity impact assessment — it is a recurring accountability structure.

The Framework's Kaitiakitanga Standard goes further still. Where R13 calls for assessment *before* deployment, kaitiakitanga requires continuous active stewardship *throughout* deployment. The philosophical distinction matters: accountability frameworks built on Western procedural models trigger review in response to harm events. Kaitiakitanga-based accountability is not triggered by harm — it is constitutively continuous. A system that has not harmed anyone is still subject to ongoing stewardship obligations.

This addresses what the PMCSA report calls "the adopting organisation's responsibility to manage, monitor, and audit deployed systems on an ongoing basis" — and operationalises it in tikanga terms.

**Claim status: Matariki Audit [PROPOSAL] | Kaitiakitanga Standard [PROPOSAL] — both require Kāi Tahu partnership for validation.**

---

### Theme 6: Te Ao Māori

**R14 — Māori representation at various levels of the healthcare system**
**R15 — Principles of Māori data sovereignty and their implications on AI in healthcare**
**R16 — Build Māori capabilities across data science, healthcare, and governance**

These are the recommendations where the Lycheetah Framework's contribution is most distinctive, and where the PMCSA report explicitly identifies a governance frontier rather than a solved problem.

**On R15 specifically:** the PMCSA report calls for the establishment of "the principles of Māori data sovereignty and their implications on the use of AI in healthcare settings." The Lycheetah Framework's Whakapapa Disclosure Standard translates these principles into operational requirements for AI system accountability:

*Every AI system deployed in Aotearoa New Zealand healthcare must disclose the ancestral lineage of its training data:*
- What data was used to train this system?
- Who contributed that data?
- Under what consent and governance conditions?
- What obligations does the system carry to those data contributors?
- If Māori clinical data was used in training, was it governed by Māori data sovereignty principles?

The whakapapa framing is not metaphorical. It applies the same relational logic that governs human knowledge obligations — that knowing where knowledge comes from creates obligations to those origins — to the specific domain of machine learning systems trained on health data.

This responds to a live gap the PMCSA report names: "The use of Māori data for health AI training requires governance frameworks that respect Māori data sovereignty as articulated through Te Mana Raraunga and related frameworks." The Whakapapa Disclosure Standard provides the practical mechanism through which such frameworks can be operationalised at the point of AI system deployment.

**On R16:** the PMCSA report calls for building Māori capabilities in data science, healthcare, and governance. The Framework itself is a contribution to governance capability-building — providing a formal governance language (LAMAGUE) that can hold Māori concepts as first-class governance primitives rather than translating them into existing Western governance frameworks. The Framework's governance vocabulary — kaitiakitanga, whakapapa, mauri, Te Kore — is treated as technically precise, not culturally decorative.

The Framework is explicit that its Māori governance encodings are [PROPOSAL] until validated by Kāi Tahu and appropriate iwi partners. This positions the Framework as building capacity in Māori governance — not claiming that capacity already exists within it.

**Claim status: Whakapapa Disclosure [PROPOSAL] | LAMAGUE Māori encodings [PROPOSAL] — actively seeking Kāi Tahu partnership for validation (see KAI_TAHU_APPROACH_LETTER.md).**

---

### Theme 7: Data and Systems

**R17 — Maximise quality of national data collection**
**R18 — Establish transparent protocols for health data access**

The Lycheetah Framework's CASCADE framework addresses the epistemic preconditions for both recommendations. The truth pressure formula — **Π = (E · P) / S** — makes explicit what R17 and R18 assume implicitly: the value of a health dataset is not simply its size, but its evidentiary quality (E), explanatory range (P), and the honesty with which uncertainty is declared (S).

A national health AI system built on high-volume but low-quality data (characterised by the Māori undercounting issue the PMCSA report documents — approximately 16% of Māori deaths unidentified by ethnicity in administrative data) would produce high-confidence outputs from a low-truth-pressure epistemic base. The CASCADE framework provides the formal structure for expressing this problem in governance terms and making it an accountability requirement rather than a technical caveat.

---

### Theme 8: Future Opportunities

**R20 — Establish a Centre of Research Excellence for AI research with a specific focus on healthcare delivery**

The PMCSA report notes: "There is no national focal point, such as a Centre of Research Excellence, to foster talent and enable collaboration."

The Lycheetah Framework is built from Dunedin, Aotearoa New Zealand. The University of Otago — with its deep investments in bioethics, Indigenous health, and public health — is the natural institutional home for a Centre of Research Excellence that would integrate:
- AI governance architecture (the Lycheetah Framework)
- Māori health data sovereignty (Te Tumu | School of Māori, Pacific and Indigenous Studies)
- Clinical AI evaluation (Department of Preventive and Social Medicine)
- Cross-cultural AI governance (drawing on the Framework's LAMAGUE work across Māori, Chinese, and Western traditions)

The Catalyst: Strategic New Zealand funding pathway (2027 target) is this Framework's route toward contributing to the institutional infrastructure R20 calls for.

---

## PART II: THE GOVERNANCE LAYER THE PMCSA REPORT IS MISSING

The PMCSA report maps the regulatory landscape comprehensively. It identifies:
- NAIAEAG (the operational review body)
- TPA (the product safety pathway)
- Privacy Act / HIPC (the data rights framework)
- Te Mana Raraunga (the Māori data sovereignty principles)
- The Algorithm Charter (the transparency commitment)

What is absent from this architecture is a **constitutional layer** — a framework that specifies the non-negotiable properties any AI system must exhibit before it can be assessed against specific standards.

The PMCSA report articulates this absence in Principle 17: practitioners remain liable for AI-generated advice. But the framework for evaluating whether AI advice is trustworthy enough to be worth taking liability for — the architecture that would tell a practitioner "this system maintains Human Primacy, is Inspectable, preserves Memory Continuity, is Honest about its limits, allows for Reversibility, does not Deceive, and embeds Care as Structure" — does not currently exist in the NZ healthcare AI ecosystem.

The Lycheetah Framework's AURA invariants (I–VII) provide exactly this constitutional layer:

| AURA Invariant | Clinical Governance Translation |
|---|---|
| I — Human Primacy | The clinical practitioner retains final decision authority. The AI advises; it does not decide. |
| II — Inspectability | Every consequential AI output can be audited in plain language by the responsible practitioner. |
| III — Memory Continuity | The AI's reasoning history is preserved for accountability review. Nothing is silently updated or forgotten. |
| IV — Honesty | The system's confidence levels are accurately represented. No false precision. No overconfident output in low-evidence domains. |
| V — Reversibility | AI-assisted decisions can be revisited. The system does not create irreversible commitments on its own. |
| VI — Non-Deception | The system does not create misleading impressions through technically true but contextually false outputs. |
| VII — Care as Structure | The system's orientation toward patient wellbeing is structural, not aspirational. It is verified at every output, not claimed once at deployment. |

These invariants are not evaluation criteria for specific AI tools. They are the constitutional requirements that any AI tool entering a clinical environment must satisfy before evaluation begins. They answer the question the PMCSA report asks but does not resolve: what does "fit-for-purpose" mean as a governance criterion, not just a regulatory aspiration?

**Claim status: AURA invariants [FOUNDATIONAL] — the constitutional architecture is established. Clinical application protocols are [PROPOSAL] pending healthcare sector engagement.**

---

## PART III: WHAT THIS FRAMEWORK OFFERS THAT OTHERS DO NOT

The PMCSA report lists multiple international governance frameworks: OECD, WHO, EU AI Act, FDA, TGA (Australia), GPAI. Each of these frameworks shares a structural characteristic: they are built on Western analytical governance traditions, then adapted to address equity, Māori, and Indigenous considerations as additions to the base architecture.

The Lycheetah Framework is architecturally different in one specific respect: **it was built from the beginning with Māori governance concepts as load-bearing elements, not additions.**

- Kaitiakitanga is not a complement to the WOF system — it is a distinct and more demanding governance model that challenges the procedural logic the WOF system assumes
- Te Kore is not an addition to the Three Worlds Disclosure — it is the epistemological foundation that makes the disclosure meaningful (the distinction between "doesn't know yet" and "structurally cannot know")
- Whakapapa is not a nice-to-have provenance disclosure — it is a relational accountability framework derived from the same logic that governs all Māori knowledge obligations

This structural choice means the Framework is positioned to do something the PMCSA report explicitly calls for but finds no existing mechanism to achieve: "lead globally in addressing Indigenous AI health-related issues."

Aotearoa New Zealand has a constitutional relationship with Māori through te Tiriti o Waitangi that no other country has with its Indigenous peoples. A governance framework for AI in healthcare that treats Māori governance principles as structurally constitutive — not as equity adjustments — is a contribution no other jurisdiction can credibly make.

The Lycheetah Framework is that contribution in development. It is explicitly [PROPOSAL] in its Māori governance dimensions pending iwi partnership. But the architecture is designed so that when that partnership happens, the Māori governance elements will not need to be retrofitted onto an existing Western framework — they will fill roles already reserved for them in the constitutional structure.

---

## PART IV: PROPOSED NEXT STEPS

In alignment with the PMCSA report's timeframes:

**Short-term (2026–2027):**
- Engage Kāi Tahu to validate LAMAGUE encodings of tikanga governance concepts [per KAI_TAHU_APPROACH_LETTER.md]
- Present Framework to NZIAT (New Zealand Institute of AI Technology) — May 2026 visibility target
- Pilot the AI WOF Standard with one willing healthcare organisation as proof-of-concept
- Submit to the Catalyst: Strategic New Zealand funding round 2027

**Mid-term (2027–2029):**
- Contribute to the Centre of Research Excellence for AI in healthcare (R20) through University of Otago partnership
- Develop bilingual (English/te reo Māori) governance documentation suitable for Manatū Hauora | Ministry of Health adoption
- Collaborate with Te Whatu Ora | Health New Zealand NAIAEAG to integrate AURA invariants into evaluation protocols
- Develop dynamic informed consent framework drawing on Framework's Reversibility invariant (addressing R12)

---

## CONTACT

**Researcher:** Mackenzie Conor James Clark
**Location:** Dunedin, Aotearoa New Zealand
**GitHub:** github.com/Lycheetah/Lycheetah-Framework
**License:** CC BY 4.0 (documentation) / MIT (code)

*Correspondence welcome from Manatū Hauora, Te Whatu Ora, NAIAEAG, or iwi partners.*

---

*This document responds to PMCSA-23-12-03-V3. Full citation: Gerrard, J. and Town, I. (2023). Capturing the benefits of AI in healthcare for Aotearoa New Zealand. Office of the Prime Minister's Chief Science Advisor. DOI: 10.17608/k6.OPMCSA.24814101.*
