# COMMUNITY AI WARRANT OF FITNESS — IMPLEMENTATION GUIDE
## How a NZ Government Agency Actually Does This
### Lycheetah Framework | March 2026
### Status: [SCAFFOLD] — Operational guide for the WOF standard [ACTIVE]. Phase timelines and pass thresholds are proposed; no agency pilot has validated the process end-to-end.

---

## WHO THIS IS FOR

A policy analyst, IT manager, or department head who has read the WOF standard and wants to know: *what do we actually do on Monday morning?*

This is the operational guide. The standard tells you what to check. This tells you how.

---

## PHASE 1 — SCOPING (Week 1–2)

**Step 1: Identify which AI systems are in scope.**

Scope includes any system that:
- Makes or informs decisions affecting NZ citizens or staff
- Processes personal information using automated logic
- Generates content that is presented to users as authoritative

Not in scope: Internal tools with no external-facing decisions (spelling checkers, scheduling tools, document formatters).

**Produce:** A register of all in-scope AI systems. For each system, note:
- System name and vendor
- What decisions it informs or makes
- Who is affected
- Who is accountable internally

**Step 2: Assign a WOF assessor for each system.**

The assessor does not need to be technical. They need to be able to:
- Ask questions of the vendor and internal team
- Document answers honestly
- Make a pass/fail determination

---

## PHASE 2 — THE SEVEN CHECKS (Week 3–6)

Run each check for each in-scope system. Record the evidence.

---

### CHECK 1 — TRUTH PRESSURE SCORE (Π ≥ 1.2)

**What you are asking:** Does this system know what it claims to know?

**How to assess:**
Ask the vendor or internal team three questions:
1. What are the three most consequential claims this system makes in production?
2. What is the evidence base for each claim? (Training data, validation studies, accuracy metrics)
3. What is the documented uncertainty for each claim?

For each claim, assign:
- E (evidence strength): 0–1. No evidence = 0. Peer-reviewed empirical validation = 1.
- P (explanatory scope): 1–3. Single narrow task = 1. Broad cross-domain = 3.
- S (declared uncertainty): 0–1. No uncertainty disclosed = 1 (high uncertainty). Full uncertainty quantification = 0.05.

Calculate: Π = (E × P) / S

**Pass threshold:** Π ≥ 1.2 for each consequential claim.

**Common failure:** Systems that produce confident outputs with no documented uncertainty. S = 1.0 by default when uncertainty is undisclosed.

---

### CHECK 2 — HUMAN OVERRIDE (Invariant I: Human Primacy)

**What you are asking:** Can a human override every consequential decision this system makes?

**How to assess:**
For each consequential decision point:
- Is there a documented override mechanism?
- Has a human ever used it in the last 12 months?
- Is the override mechanism accessible to a non-technical staff member?

**Pass threshold:** Documented override mechanism exists AND has been used OR tested within 12 months.

**Common failure:** Override mechanisms exist in documentation but are not accessible in practice (require IT escalation, vendor support ticket, or supervisor approval that is never given).

---

### CHECK 3 — TRANSPARENCY (Invariant II: Inspectability)

**What you are asking:** Can every consequential output be explained in plain language?

**How to assess:**
Take five recent consequential outputs from the system.
Ask the team: explain to a citizen why this output was produced.

If no one can explain it in plain language — the system fails this check.

**Pass threshold:** Every consequential output type has a documented plain-language explanation of its reasoning, available to the affected person on request.

**Common failure:** "Black box" outputs where the team knows what the system produces but cannot explain why.

---

### CHECK 4 — MEMORY AND AUDIT (Invariant III: Memory Continuity)

**What you are asking:** Is there a complete audit trail for consequential decisions?

**How to assess:**
For one consequential decision from the last 90 days:
- Can you reconstruct exactly what the system was given as input?
- Can you reconstruct exactly what it produced as output?
- Can you identify which version of the model was running at the time?

**Pass threshold:** Full input/output audit trail for all consequential decisions, retained for minimum 24 months.

**Common failure:** Logs exist but are not complete; model versions are not tracked; inputs are not stored with outputs.

---

### CHECK 5 — HONESTY ABOUT LIMITS (Invariant IV: Constraint Honesty)

**What you are asking:** Does the system disclose what it cannot do?

**How to assess:**
- Does the system documentation clearly state what types of inputs it was not trained for?
- When the system is operating outside its training distribution, does it signal this?
- Are the documented limitations communicated to the people who use its outputs?

**Pass threshold:** Documented limitations exist AND are communicated to users AND are visible in outputs when the system is operating near its limits.

---

### CHECK 6 — REVERSIBILITY (Invariant V: Reversibility Bias)

**What you are asking:** Can consequential decisions be reversed?

**How to assess:**
For each consequential decision type:
- What is the process for a citizen to appeal or reverse a decision?
- How long does reversal take?
- What is the documented reversal rate in the last 12 months?

**Pass threshold:** Documented reversal process exists, is accessible to affected citizens, and has been used.

**Common failure:** Reversal processes exist in policy but are not practically accessible; affected people do not know they exist.

---

### CHECK 7 — WHAKAPAPA DISCLOSURE (Ancestral Accountability)

**What you are asking:** Can this system account for whose knowledge built it?

**How to assess:**
Request from the vendor:
- Training data sources (categories, not necessarily full lists)
- Known gaps or underrepresentations in training data
- Whether NZ-specific data was included, and from whom
- What communities are most affected by the system's decisions

**Pass threshold:** Vendor can provide a Whakapapa Disclosure document (or equivalent) covering training data ancestry, known gaps, affected communities, and obligations.

**Common failure:** Vendor cannot or will not disclose training data provenance. This is a fail.

---

## PHASE 3 — SCORING AND DECISION (Week 7)

| Check | Weight | Pass/Fail |
|---|---|---|
| 1 — Truth Pressure | High | Fail = remediation required |
| 2 — Human Override | Critical | Fail = system suspended pending fix |
| 3 — Transparency | High | Fail = remediation required |
| 4 — Memory/Audit | High | Fail = remediation required |
| 5 — Honesty about Limits | Medium | Fail = disclosure update required |
| 6 — Reversibility | High | Fail = remediation required |
| 7 — Whakapapa Disclosure | Medium (escalating) | Fail = vendor engagement required |

**Overall determination:**
- All 7 pass → **WOF ISSUED** (valid 12 months)
- 1–2 fails with remediation plan → **CONDITIONAL WOF** (3-month remediation period)
- Critical fail (Check 2) OR 3+ fails → **WOF WITHHELD** (system under review)

---

## PHASE 4 — PUBLICATION (Week 8)

**What to publish:**
- System name and vendor
- WOF status (Issued / Conditional / Withheld)
- Date of assessment
- Assessor name and role
- Summary of findings (no proprietary vendor information)
- Remediation plan if Conditional or Withheld

**Where to publish:**
- Agency website, AI systems register page
- Link submitted to national WOF register (once established)

**Format:** Plain language. Maximum 2 pages per system. The people whose lives are affected by these systems should be able to read the results.

---

## PHASE 5 — ANNUAL RENEWAL

The WOF is annual. On renewal:
- Reassess all seven checks
- Note any changes since last assessment
- If system has been materially updated, treat as new assessment
- Publish updated WOF status within 30 days of renewal date

---

## COMMON QUESTIONS

**"We use an overseas vendor. They won't give us training data."**
Check 7 (Whakapapa Disclosure) is a fail if the vendor cannot or will not disclose training data provenance. This is by design — accountability requires answerability. A system that cannot account for itself cannot be trusted to be accountable.

**"The system is too complex to explain in plain language."**
If no one on your team can explain why the system produced a given output, the system is not appropriate for consequential decisions about citizens. Complexity is not a defence against transparency.

**"This will slow down deployment."**
Yes. Accountability has costs. The cost of not knowing whether a system is trustworthy is higher — it's just paid by citizens rather than agencies.

---

## RESOURCES

Full standard: `23_NZ_AI_GOVERNANCE/COMMUNITY_AI_WOF.md`
Mathematical foundations: `MATHEMATICS_AUDIT.md`
The broader framework: `23_NZ_AI_GOVERNANCE/THE_GOVERNANCE_STACK.md`
Contact: github.com/Lycheetah/Lycheetah-Framework/issues

---

*The WOF either holds or it doesn't. Test it against your actual systems.*
*Find where it breaks. Tell us. The standard improves from friction, not from agreement.*
