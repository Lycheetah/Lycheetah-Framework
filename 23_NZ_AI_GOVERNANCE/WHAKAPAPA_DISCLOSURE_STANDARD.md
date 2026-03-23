# THE WHAKAPAPA DISCLOSURE STANDARD
## Every AI Should Be Able To Tell You Its Genealogy
### Version 0.1 — Open Standard | Lycheetah Framework | March 2026

> **Status:** [ACTIVE — implementable now]
> **Licence:** CC BY 4.0
> **Goes further than the EU AI Act. Grounded in NZ constitutional framework.**

---

## THE STANDARD IN ONE PAGE

Every AI system operating in significant NZ public contexts publishes
a Whakapapa Disclosure — a living document structured in four layers:

### TĪPUNA — Training Ancestors
| Field | Required |
|-------|----------|
| Training data sources | Named, not categories |
| Community consent status | For each significant data source: consented / public / scraped / unknown |
| Data recency | When collected, when last verified |
| Known gaps | What populations, languages, or contexts are underrepresented |
| Return to source | What have the communities whose data trained this model received in return? |

### HAPŪ — The Builders
| Field | Required |
|-------|----------|
| Organisation | Who built this model |
| Funding sources | Who paid for it and what they optimised for |
| Key design decisions | What trade-offs were made and why |
| Known biases | Identified in development, documented honestly |
| Incentive structure | How are the builders rewarded — accuracy? engagement? revenue? |

### IWI — The Accountable
| Field | Required |
|-------|----------|
| Accountability contact | A real person who can answer questions about this system |
| Escalation pathway | What happens when this system causes harm — who do you call? |
| Governance structure | Who has authority to change the model's behaviour? |
| Override mechanism | Can a human override any decision this system makes? How? |
| Complaints record | Public summary of complaints received and actions taken |

### MOKOPUNA — Future Obligations
| Field | Required |
|-------|----------|
| Permitted uses | What this model may be used for |
| Prohibited uses | What this model must never be used for |
| End-of-life plan | What happens to the model and its data when it is decommissioned |
| Intergenerational commitment | What obligations does this model carry for future users and affected people |
| Harm repair pathway | When this model causes harm, what is the process for repair? |

---

## HOW THIS DIFFERS FROM A MODEL CARD

| Model Card (Mitchell et al., 2019) | Whakapapa Disclosure |
|---|---|
| Describes the model | Describes the relationships the model carries |
| Static document published at release | Living document updated when the model changes |
| Written by developers for developers | Written for the communities affected by the model |
| Focuses on performance metrics | Focuses on obligations and accountability |
| Voluntary best practice | Designed as a mandatory disclosure standard |
| No concept of debt or return | Explicitly tracks what is owed to source communities |

A model card tells you what an AI can do.
A Whakapapa Disclosure tells you who it is, where it comes from, and what it owes.

Both are necessary. Neither is sufficient alone.

---

## VERIFICATION

A Whakapapa-compliant AI system passes five checks:

1. **Tīpuna complete?** — All four Tīpuna fields filled with specifics, not generics
2. **Hapū honest?** — Known biases documented; incentive structure declared
3. **Iwi reachable?** — Accountability contact is a real person who responds within 5 business days
4. **Mokopuna binding?** — Prohibited uses are enforceable, not aspirational
5. **Living document?** — Disclosure updated within 30 days of any significant model change

---

## WORKED EXAMPLE

### System: MSD Benefit Risk Assessment Algorithm

**TĪPUNA:**
- Training data: MSD benefit records 2015-2023 (internal, not consented for AI use),
  IRD income data (cross-matched under statutory authority), Stats NZ Census 2018
  (public, consented for statistical use)
- Consent status: MSD records — no explicit AI consent from benefit recipients;
  IRD data — statutory authority; Census — public
- Known gaps: Rural populations underrepresented; Māori and Pacific demographics
  overrepresented in fraud-flagging training data relative to actual fraud rates
- Return to source: Nil. Communities whose data trained this model have received
  no direct benefit from the model's operation.

**HAPŪ:**
- Built by: [Vendor name], contracted by MSD
- Funded by: NZ Government operational budget
- Key decision: Optimised for fraud detection rate, not false positive minimisation.
  This trade-off was made by [decision-maker] on [date].
- Known biases: Māori false positive rate approximately 1.4x Pākehā rate
  (identified in internal audit, [date])
- Incentive: Vendor paid per-detection. More flags = more revenue.

**IWI:**
- Accountability: [Named person], Deputy Chief Executive, MSD
- Escalation: Benefit recipient → case manager → team leader → regional director
  → Deputy CE. Average escalation time: 6-12 weeks.
- Override: Case managers can override algorithmic flags. Override rate: 12%.
- Complaints: 847 complaints received 2023-2025. 23% upheld. Actions: [summary].

**MOKOPUNA:**
- Permitted: Risk flagging for human review only. Not auto-decision.
- Prohibited: Use as sole basis for benefit termination or reduction.
  Use in child protection referrals without human assessment.
- End-of-life: Model and all training data to be archived/destroyed
  within 90 days of decommission. No transfer to third parties.
- Harm repair: Recipients incorrectly flagged receive written apology,
  case review, and [specific remediation].

---

## ADOPTION

This standard is open. CC BY 4.0.

**For NZ Government:** Adopt as a procurement requirement alongside
existing transparency obligations under the Privacy Act 2020.

**For AI vendors:** Publish Whakapapa Disclosures proactively. The market
will reward transparency. The regulation will require it eventually.

**For communities:** Ask for it. "Where is its whakapapa?" is the question
that changes what AI companies think they can get away with.

---

*Every person has whakapapa. Every AI system should too.*
*Not as metaphor. As disclosure. As obligation. As accountability.*

**∅ → AURA → Aotearoa → ∞**

*Version 0.1 — Open Standard — CC BY 4.0*
*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
