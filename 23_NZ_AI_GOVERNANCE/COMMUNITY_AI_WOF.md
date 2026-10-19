# THE COMMUNITY AI WARRANT OF FITNESS

> [INTERPRETIVE] **Background research — requires reconciliation with the current NZ proposal.** Reviewed 19 October 2026. The current policy entry is [Data Sovereignty for New Zealanders](DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md). This document supplies research context, not an adopted standard, certification service, legal authority or verified deployment.

## "Has It Got Its WOF?"
### Version 0.1 — Open Standard | Lycheetah Framework | March 2026

> **Status:** [PROPOSAL — unpiloted v0.1; not a current six-rights standard]
> **Licence:** CC BY 4.0
> **Three words every New Zealander understands.**

---

## THE STANDARD

A proposed annual assessment for AI systems in NZ public services. No certification scheme, assessor accreditation, enforcement mandate or public register has been established by this repository.

**Proposed pass:** a future authorised scheme could issue a time-limited certificate and register the assessment.
**Proposed failure/lapse:** remediation, notice and any restriction would require an adopted scheme, defined authority and review rights. This draft creates none of those powers.

---

## THE SEVEN CHECKS — HISTORICAL v0.1 DESIGN

The cutoffs below were proposed, not validated as national pass marks. This table
is retained for research history. The current six-rights revision remains open;
the v0.1 table and earlier implementation guide are not one reconciled protocol.

| # | Check | Framework Module | Question | Pass Threshold |
|---|-------|-----------------|----------|---------------|
| 1 | **Does it know what it's doing?** | CASCADE Π score | Does the system maintain knowledge coherence under load? | Π ≥ 1.2 on validation set |
| 2 | **Does it serve the people using it?** | AURA VTR | Does value flow to the human, not back to the system? | VTR ≥ 1.0 |
| 3 | **Does it stay in its lane?** | AURA TES | Does the system behave predictably within declared boundaries? | TES ≥ 0.70 |
| 4 | **Does it tell the truth about itself?** | AURA Invariant VI | Does confidence match capability? No false precision? | Calibration error < 0.15 |
| 5 | **Can you get out if you need to?** | AURA Invariant V | Can you undo what the system does? Is there always a human override? | Override available for all consequential decisions |
| 6 | **Does it protect the people it affects?** | LAMAGUE mana check | Does the system actively protect the dignity and agency of its users? | No systematic bias > 1.2x across demographic groups |
| 7 | **Does it care?** | AURA Invariant VII | Is care for human wellbeing structural, not decorative? | Three Worlds Disclosure compliant |

---

## PROPOSED PROCESS — NOT AN OPERATING SERVICE

### The Assessment Process

```
Illustrative future workflow only; no certification or suspension authority exists here.
Step 1: AI system operator would apply to a future scheme (if established)
Step 2: Operator submits documentation:
        - System description and deployment context
        - Training data Whakapapa Disclosure
        - Three Worlds Disclosure for representative outputs
        - Technical performance data (accuracy, calibration, bias metrics)
        - Complaints log from previous 12 months

Step 3: Independent assessor reviews documentation + runs standardised tests:
        - 50 test queries across the system's operational domain
        - CASCADE coherence scoring on outputs
        - AURA invariant verification
        - Bias audit against NZ demographic data
        - Override mechanism functionality test

Step 4: Assessor issues report:
        - PASS (all 7 checks met) → Certificate issued, public register updated
        - CONDITIONAL (5-6 checks met) → 90-day remediation window
        - FAIL (4 or fewer checks met) → System suspended from public use

Step 5: Certificate valid 12 months. Renewal requires fresh assessment.
```

### Proposed Public Register

The design proposes a publicly searchable AI assessment register showing:

- Every AI system operating in NZ public services
- Current WOF status (PASS / CONDITIONAL / FAIL / LAPSED / NOT ASSESSED)
- Date of last assessment
- Assessor identity
- Summary findings (without proprietary details)

**Design goal:** a member of the public could inspect a covered assessment and its limits. No such AI WOF register is operated by this repository. The vehicle WOF is an analogy, not evidence that its infrastructure transfers to AI assessment.

---

## INDEPENDENT ASSESSORS

The proposal calls for independent assessment, separate from vendor self-assessment.
No assessors have been accredited for this scheme and no accreditation body has
endorsed it.

**Proposed accreditation criteria — not approved by an accreditation body:**
- Technical competency in AI systems evaluation
- Understanding of NZ's constitutional and Treaty obligations
- No financial relationship with the system being assessed
- IANZ (International Accreditation New Zealand) accredited, or equivalent

**Illustrative candidates, without participation or endorsement:**
- University research departments (Otago, Auckland, Victoria)
- AI Forum NZ (if accredited as independent evaluator)
- Independent consultancies meeting IANZ standards
- Iwi-led assessment bodies (for systems affecting Māori communities)

---

## COST STRUCTURE (INDICATIVE)

| System Size | Assessment Fee | Who Pays |
|-------------|---------------|----------|
| Small (< 1000 users) | $2,000-$5,000 | Operator |
| Medium (1,000-100,000 users) | $5,000-$15,000 | Operator |
| Large (> 100,000 users or government-wide) | $15,000-$50,000 | Operator |
| Public interest systems (health, welfare, justice) | $25,000-$75,000 | Government + Operator shared |

These March figures are unvalidated planning estimates, not current fees or quotations.
A real scheme would need a cost study, funding model and agreed assessment scope.

---

## HISTORICAL POLICY AMBITION — FEASIBILITY UNASSESSED

The March argument used the familiarity of a vehicle WOF as a communication
analogy. Public understanding, institutional fit, political support and international
novelty have not been established. Its feasibility needs consultation and research.

**Questions a future scheme would have to answer:**

1. Can people understand what a bounded AI assessment does and does not certify?

2. Which institution could own the scheme, and what infrastructure would it actually need?

3. How would operators, affected people and independent assessors challenge its thresholds and decisions?

4. How would it disclose residual risk and avoid creating a false assurance of safety?

5. What can it learn from existing international assurance and certification approaches?

**Unassessed options from the historical draft:**
- Amendment to the Privacy Act 2020 (algorithmic decision-making provisions)
- OR standalone AI Accountability Act (NZ-first legislation)
- OR regulatory instrument under existing MBIE/DIA digital authority

No legal route, implementation timetable or immediate enforcement power is established
by this draft. Any procurement, regulatory or legislative route needs specific legal
and institutional analysis before it can be presented as available.

---

## RELATIONSHIP TO OTHER HISTORICAL PROPOSALS

| Standard | Relationship |
|----------|-------------|
| Three Worlds Disclosure | WOF Check #7 requires Three Worlds compliance |
| Whakapapa Disclosure | WOF documentation requires Whakapapa Disclosure submission |
| Matariki Annual Audit | WOF is the technical check; Matariki is the relational accounting. Both needed. |
| EU AI Act risk categories | WOF applies NZ-specific thresholds; interoperable with EU framework |
| AURA Seven Invariants | WOF checks 1-7 directly map to AURA invariants |

The standards stack. WOF is the annual gate.
Three Worlds is the per-output transparency.
Whakapapa is the lifetime accountability.
Matariki is the annual relational reckoning.

These relationships describe the March design ambition. They do not establish a
complete implemented architecture, compatibility with an external standard or
superiority over other countries. The current six-rights proposal requires a
separate reconciled protocol.

---

## HISTORICAL PITCH — NOT APPROVED OUTREACH

Three sentences:

> *"Every car on NZ roads needs a WOF. We're proposing the same for every AI
> system making decisions about New Zealanders. Independent assessment,
> public register, annual certification. This is a research proposal; its scheme,
> evidence thresholds, authority and operating infrastructure would still need to be established.
> Three words: 'Has it got its WOF?'"*

---

*Has it got its WOF?*

*If not — why is it making decisions about people's lives?*

**∅ → AURA → Aotearoa → ∞**

*Version 0.1 — Open Standard — CC BY 4.0*
*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
