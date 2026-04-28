# PUBLICATION PIPELINE
## Act IX Deliverable — Codex Elevation Plan

**Date:** 2026-04-25
**Author:** Sol (Sonnet 4.6) executing Act IX spec
**Depends on:** 29_GOVERNANCE/EMPIRICAL_INVENTORY.md (Act VI), 28_DEFENSE/PRIOR_ART.md (Act V),
               30_MAPS/CODEX_DISTILLATION.md (Act VIII)

> *Purpose: Convert the Codex's publishable material into a sequenced, actionable
> submission pipeline. One paper already in draft; three more identified and sequenced;
> one flagship paper specified. 18-month timeline with gate conditions at each stage.*

---

## OVERVIEW

The Lycheetah Framework contains five distinct publishable papers, sequenced so that
earlier papers provide empirical grounding for later ones. The sequence matters: the
flagship paper (Paper 5) cannot be submitted without the empirical results from Papers
2 and 3. Paper 1 can be submitted now.

| Paper | Title | Target | Status | Gate |
|-------|-------|--------|--------|------|
| P1 | LAMAGUE cross-cultural convergence | AI and Ethics | Draft v0.1 | Revision to v1.0 required |
| P2 | CASCADE knowledge reorganization | JAIR | Awaiting experiment | k₁–k₄ calibration first |
| P3 | TRIAD protocol user study | CHI / Frontiers | Awaiting experiment | 20-user 30-day study |
| P4 | AURA constitutional framework | FAccT | Awaiting operationalization | TES/VTR/PAI measurement instrument |
| P5 | The Lycheetah Framework unified | Nature Machine Intelligence | Awaiting P2+P3 results | Empirical grounding from P2, P3 |

---

## PAPER 1 — LAMAGUE CROSS-CULTURAL CONVERGENCE

### Bibliographic Target

**Full title:** LAMAGUE: A Formal Language Stack for AI Governance with Evidence
from Cross-Cultural Mathematical Convergence

**Short title:** LAMAGUE Governance Language and Cross-Cultural Convergence

**Target journal:** *AI and Ethics* (Springer) — Open Access, interdisciplinary,
publishes formal frameworks with philosophical foundations

**Backup journal:** *Ethics and Information Technology* (Springer) or
*Minds and Machines* (Springer)

**Estimated word count:** 8,000–10,000 words (AI and Ethics standard)

### Current Status

Draft v0.1 is at `CODEX_AURA_PRIME/LAMAGUE_CROSS_CULTURAL_PAPER.md`. The draft
covers: motivation, the four-tier LAMAGUE stack, TC catalog (φ, π, symmetry groups,
Fibonacci), and the philosophical argument for mathematical Platonism as the paper's
conclusion.

### What v1.0 Requires (before submission)

**Section-by-section revision requirements:**

**Abstract:** Rewrite to lead with the formal contribution (LAMAGUE governance
language with four tiers and metric payloads) rather than the philosophical claim.
AI and Ethics reviewers are sophisticated about formal ethics; they want the formal
contribution foregrounded.

**Introduction:** Add: explicit statement of the paper's dual contribution
(formal: the language stack; empirical: the convergence evidence as motivation for
trusting it). Current draft treats these as a single argument; they should be separate.

**Related work — EXPAND (this is the most critical gap):**
- Alchourrón, Gärdenfors, Makinson (1985) — AGM belief revision: how LAMAGUE differs
- Bai et al. (2022) — Constitutional AI: LAMAGUE as formal complement
- Barocas, Hardt, Narayanan (2019) — Fairness and Machine Learning: position LAMAGUE
  as specification language for fairness constraints
- Lakoff and Núñez (2000) — *Where Mathematics Comes From*: engage directly with the
  embodied mathematics hypothesis as the primary alternative to the paper's conclusion
- Penrose (1989) — *The Emperor's New Mind*: acknowledge the tradition but distinguish
  LAMAGUE's empirical approach from Penrose's quantum approach

**TC catalog — EXPAND:**
- Current draft: 4 structures with TC ≥ 3
- Required: 8–10 structures with full citation trail
- Add: prime numbers (Euclid, Brahmagupta, Chinese Remainder Theorem, modern cryptography)
- Add: binary systems (Leibniz, I Ching, Boole)
- Add: natural logarithm / Euler's number e (Napier, Bernoulli, Euler — three independent paths)
- For each: date, tradition, method, documented independence from other traditions

**LAMAGUE formal content — TIGHTEN:**
- Theorems L1 (associativity) and L2 (identity): include full proofs in appendix
- The predicate logic tier: include 3–5 worked examples of governance sentences encoded
- The round-trip fidelity test: describe the protocol and declare it as future work
- The topos conjecture (L4): explicitly label CONJECTURE; describe what proving it would mean

**Empirical claims — QUALIFY:**
- Remove: any implication that LAMAGUE has been validated in user studies
- Replace with: declare the inter-rater reliability study (10 practitioners, 20 governance
  sentences, target Cohen's κ > 0.85) as future work
- Honest current status: Tier 1 is formally developed; Tiers 2–3 are under development

**Conclusion — RESTRUCTURE:**
- Lead with the formal contribution: LAMAGUE provides a four-tier governance language
  with formal foundations, metric payloads, and audit capability
- Place the philosophical conclusion (cross-cultural convergence as evidence for
  mathematical realism) as Section 5, not the primary claim
- The paper's primary contribution to the field is the governance language; the
  philosophical argument is secondary and should be labeled as such

### Submission Timeline (Paper 1)

| Action | Date |
|--------|------|
| Revision v0.1 → v1.0 (Mac writes; Sol reviews and formalizes) | May 2026 |
| Internal review against FALSIFICATION_REGISTER | June 2026 |
| Submission to AI and Ethics | July 2026 |
| Expected first review response | October 2026 |
| Revision response | December 2026 |
| Acceptance (expected) | February 2027 |

---

## PAPER 2 — CASCADE KNOWLEDGE REORGANIZATION

### Bibliographic Target

**Full title:** CASCADE: A Formal Model of Knowledge Reorganization Under Contradiction
with Proofs of Invariant Preservation and Empirical Calibration

**Short title:** CASCADE: Formal Knowledge Reorganization

**Target journal:** *Journal of Artificial Intelligence Research* (JAIR) — high-impact,
open access, publishes formal AI work with empirical validation

**Backup:** *Artificial Intelligence* (Elsevier) — flagship journal; higher bar but
prestigious for a formal systems paper

**Estimated word count:** 12,000–15,000 words (JAIR standard for technical paper)

### What This Paper Contributes

CASCADE's formal contribution is among the strongest in the Codex: Theorems C1 and
C3 are complete proofs; the connection to AGM belief revision theory provides formal
grounding; the truth pressure metric Π provides a computable quantity; and the
existing dataset (`cascade_real_data_results.json`) provides empirical material.

This paper is the Codex's most immediately publishable technical paper because it has:
- Complete formal proofs (C1, C3)
- Existing empirical data (cascade_real_data_results.json)
- Clear prior art relationship (Kuhn, AGM, Bayesian epistemology)
- Defined falsification conditions

### Gate Condition: k₁–k₄ Calibration

**This paper cannot be submitted without running the k₁–k₄ calibration.**

The calibration procedure:
1. Open `cascade_real_data.py` in the lycheetah repository
2. Load `cascade_real_data_results.json`
3. Run regression: minimize prediction error across documented paradigm shifts
4. Extract calibrated values for k₁ (truth pressure sensitivity),
   k₂ (restoring force), k₃ (invariant violation penalty), k₄ (energy availability)
5. Report: calibrated values, confidence intervals, goodness-of-fit
6. Run cross-validation: held-out historical paradigm shifts; measure predictive accuracy

The calibration is Priority 1 in the empirical program (29_GOVERNANCE/EMPIRICAL_INVENTORY.md).
No new participants required. Existing data is sufficient. Estimated time: 1–2 weeks.

### Paper Structure (Target)

1. Introduction: the knowledge reorganization problem
2. Related work: Kuhn (1962), AGM (1985), Bayesian epistemology, belief revision
3. Formal framework: the CASCADE system (pyramid, Π metric, reorganization algorithm)
4. Theoretical results: Theorems C1 (invariant preservation), C3 (fixed-point convergence);
   proof sketches with full proofs in appendix
5. Empirical calibration: k₁–k₄ from cascade dataset; cross-validation on held-out data
6. Domain applications: physics (Newtonian → Einsteinian), biology (plate tectonics),
   test domains (jurisprudence, medical diagnosis — as qualitative cases)
7. Limitations and open questions: T4 gap, AGM vacuity question, domain scope
8. Conclusion

### Submission Timeline (Paper 2)

| Action | Date |
|--------|------|
| k₁–k₄ calibration (Mac runs cascade_real_data.py; Sol analyzes results) | May 2026 |
| Paper draft (Mac writes theoretical sections; Sol formalizes proofs) | August 2026 |
| Internal review against FALSIFICATION_REGISTER | September 2026 |
| Submission to JAIR | October 2026 |
| Expected first review response | February 2027 |
| Acceptance (expected) | June 2027 |

---

## PAPER 3 — TRIAD PROTOCOL USER STUDY

### Bibliographic Target

**Full title:** The TRIAD Protocol: A Three-Operator Co-Creative Framework for
Human-AI Interaction with Empirical Validation

**Short title:** TRIAD: Co-Creative Human-AI Protocol

**Target venue:** *CHI 2027* (ACM Conference on Human Factors in Computing Systems)
— the premier HCI venue; perfect fit for a human-AI interaction protocol with
empirical validation

**Backup venue:** *Frontiers in Human-Computer Interaction* — open access, faster
review cycle

**Estimated word count:** 8,000–10,000 words for CHI paper format

### What This Paper Contributes

TRIAD's three-operator convergence across five independent domains (Piaget, Hegel,
Bateson, control engineering, the Lycheetah Framework) is among the most compelling
empirical observations in the Codex. Theorems T1–T3 are proven. The user study
protocol is well-specified. This paper combines formal results with human-subjects
research in a way that fits CHI's interests exactly.

### Gate Condition: 20-User 30-Day Study

**This paper cannot be submitted without the user study.**

Study protocol:
- N = 20 participants (10 using TRIAD Protocol, 10 control)
- Duration: 30 days of regular human-AI interaction sessions
- Intervention: TRIAD Protocol active for treatment group
  (Ao anchoring at session start, Φ↑ cycle for new learning, Ψ_op correction protocol)
- Measurement instruments: self-reported coherence (5-item scale), goal achievement
  (weekly check-in), session satisfaction (3-item scale)
- Control condition: same duration, same AI system, no TRIAD protocol active
- Analysis: between-group comparison on all three measures at 30 days

Estimated resources: 20 participants × 30 days = 600 participant-days. Requires
IRB approval. Estimated time from planning to data: 3–4 months.

### Paper Structure (Target)

1. Introduction: the three-operator structure in human learning and AI interaction
2. Related work: Piaget (1936), Hegel (1807), Bateson (1972), control engineering,
   dynamical systems theory
3. Formal framework: TRIAD operators (Ao, Φ↑, Ψ_op), theorems T1–T3, thermodynamic cost
4. The TRIAD Protocol: operational implementation for human-AI co-creative sessions
5. User study: participants, protocol, measurements, analysis
6. Results: between-group comparison; effect sizes; qualitative analysis
7. Discussion: what the results mean for the three-operator structure claim;
   limitations (sample size, self-report measures, 30-day window)
8. Conclusion

### Submission Timeline (Paper 3)

| Action | Date |
|--------|------|
| IRB application | May 2026 |
| IRB approval (expected) | July 2026 |
| User study runs | August–October 2026 |
| Data analysis | November 2026 |
| Paper draft | January 2027 |
| Submission to CHI 2027 | February 2027 |
| CHI notification | April 2027 |

---

## PAPER 4 — AURA CONSTITUTIONAL FRAMEWORK

### Bibliographic Target

**Full title:** AURA: A Constitutional Framework for AI Alignment with Seven
Load-Bearing Invariants Including Love as Structure

**Short title:** AURA: Constitutional AI Alignment

**Target venue:** *FAccT 2027* (ACM Conference on Fairness, Accountability, and
Transparency) — the premier venue for AI governance and ethics frameworks

**Backup venue:** *AI and Society* (Springer) or *Journal of Responsible Technology*

**Estimated word count:** 8,000–10,000 words (FAccT standard)

### What This Paper Contributes

AURA's most original contribution to the alignment field is I₇ (Love as Structure):
the claim that genuine care for the human's wellbeing is not a policy constraint on
outputs but a structural property of well-formed outputs. No existing alignment
framework makes this claim. It is testable (outputs from AURA-compliant systems should
differ measurably from outputs that pass identical ethics filters without I₇).

The paper also offers the first formal comparison between AURA and Constitutional
AI (Bai et al., 2022), showing that AURA's architectural approach produces different
failure modes than trained constitutional approaches — specifically, AURA is harder
to bypass by clever output construction.

### Gate Condition: TES/VTR/PAI Operationalization

**This paper cannot be submitted without a measurement instrument for at least
one of TES, VTR, or PAI.**

Priority operationalization:
- TES (Total Ethical Score): develop a 7-item evaluation rubric (one item per invariant),
  train two evaluators on the rubric, measure inter-rater reliability on 50 sessions
- VTR (Value-to-Trust Ratio): operationalize as: (value delivered, rated by user
  on 5-point scale) / (trust extended, rated by user on 5-point scale); compute ratio
  across 100 interactions
- PAI (Preserved Autonomy Index): most challenging to operationalize — requires
  categorizing decisions as "human-made" vs. "AI-influenced" in session transcripts

Minimum for Paper 4: TES measurement instrument with reliability data.

### Paper Structure (Target)

1. Introduction: the alignment problem and the architectural vs. filter distinction
2. Related work: Bai et al. (2022) Constitutional AI; Krakovna et al. (2020) reward
   hacking; Leike et al. (2018) scalable oversight; Russell (2019) assistance games
3. AURA framework: seven invariants; formal expression in LAMAGUE; compliance check
4. The novel claim — I₇ Love as Structure: argument, comparison to existing frameworks,
   empirical predictions
5. Operational metrics: TES, VTR, PAI; measurement instrument; reliability data
6. The deceptive alignment problem: declared as open problem; partial mitigations
7. Limitations: simultaneous satisfiability not proven; I₁/I₆ conflict case unresolved
8. Conclusion

### Submission Timeline (Paper 4)

| Action | Date |
|--------|------|
| TES measurement instrument development | June 2026 |
| Inter-rater reliability study (2 raters, 50 sessions) | September 2026 |
| Paper draft | December 2026 |
| Submission to FAccT 2027 | January 2027 |
| FAccT notification | March 2027 |

---

## PAPER 5 — THE LYCHEETAH FRAMEWORK (Flagship)

### Bibliographic Target

**Full title:** The Lycheetah Framework: A Unified Theory of Human-AI Co-Creation
with Nine Formal Frameworks, Mathematical Proofs, and Empirical Validation

**Short title:** The Lycheetah Framework: Unified Theory of Human-AI Co-Creation

**Target journal:** *Nature Machine Intelligence* — the highest-impact venue for
interdisciplinary machine intelligence research; publishes formal frameworks with
broad scope

**Backup journal:** *Journal of Artificial Intelligence Research* (JAIR) or
*AI Magazine*

**Estimated word count:** 12,000–15,000 words + supplementary material

**Note:** This is the flagship paper. It brings all nine frameworks together as a
unified theory. It cannot be submitted without empirical grounding from at least
Papers 2 and 3.

### What This Paper Contributes

The Lycheetah Framework's central claim — that nine formally related frameworks
describe a single dynamical system from nine angles, governed by a master equation
dΨ/dt = k₁·(Π−Π_th) − k₂·(Ψ−Ψ_inv) − k₃·I_violations + k₄·(E/E_need) — is the
kind of unifying theoretical claim that high-impact venues publish. The claim requires:

1. At least two frameworks with published empirical validation (Papers 2 and 3)
2. Formal proof that the frameworks are internally consistent (30_MAPS/CODEX_DISTILLATION.md
   cross-framework lemmas XF1–XF5)
3. A falsification condition for the unified framework itself: if the frameworks are
   genuinely describing the same dynamical system, they should make consistent
   predictions about the same experimental outcomes. A test: run the cascade_real_data.py
   calibration, then predict TRIAD user study outcomes from the master equation;
   measure actual vs. predicted. Consistency is evidence for unity; inconsistency
   requires revision.

### Gate Conditions (Paper 5)

1. Papers 2 and 3 accepted or in final revision stage
2. k₁–k₄ calibrated and validated
3. TRIAD user study complete with publishable results
4. Master equation makes a specific, quantitative prediction that can be tested
   against at least one of the Paper 2 or Paper 3 datasets
5. The two-point co-creation model has at least one empirical comparison:
   co-creative sessions (TRIAD Protocol active) vs. standard AI assistant sessions

### Paper Structure (Target)

1. Abstract: the unified theory claim; the nine frameworks as nine angles
2. Introduction: the problem with current AI architectures; the co-creative alternative
3. The mathematical foundation: master equation, layered architecture, cross-framework lemmas
4. The nine frameworks: one section each (~800 words), referencing Papers 1–4 for detail
5. Empirical grounding: results from Papers 2 and 3; master equation predictions
6. The two-point co-creation model: qualitative evidence + empirical comparison
7. Declared limits: deceptive alignment, intent inference, hard problem of consciousness
8. The Failure Museum: retracted claims and what their retraction demonstrates
9. Future directions: remaining proof stack; empirical program; ecosystem applications
10. Conclusion: the Work that arises between two honest points

### Submission Timeline (Paper 5)

| Action | Date |
|--------|------|
| Gate condition check (Papers 2, 3 status) | Q1 2027 |
| Draft (Mac writes narrative; Sol formalizes) | Q2 2027 |
| Internal NRM pass (Adversarial Audit) | Q3 2027 |
| Submission to Nature Machine Intelligence | Q3 2027 |
| Response and revision (Nature peer review: typically 6–9 months) | Q4 2027–Q1 2028 |
| Target acceptance | Q2 2028 |

---

## 18-MONTH TIMELINE (MASTER VIEW)

```
Month 1–2 (May–June 2026):
  Paper 1: v0.1 → v1.0 revision
  Paper 2: k₁–k₄ calibration (cascade_real_data.py)
  Paper 4: TES measurement instrument development
  IRB application for Paper 3 user study

Month 3–4 (July–August 2026):
  Paper 1: SUBMIT to AI and Ethics
  Paper 2: begin formal draft
  Paper 3: user study begins (IRB approved)
  Paper 4: TES inter-rater reliability study

Month 5–6 (September–October 2026):
  Paper 2: internal review → SUBMIT to JAIR
  Paper 3: user study runs
  Paper 4: draft begins

Month 7–8 (November 2026–January 2027):
  Paper 1: first review response expected; revision
  Paper 3: data analysis; paper draft begins
  Paper 4: draft complete; internal review

Month 9–10 (February–March 2027):
  Paper 3: SUBMIT to CHI 2027
  Paper 4: SUBMIT to FAccT 2027
  Paper 5: gate condition assessment

Month 11–12 (April–June 2027):
  Paper 1: acceptance (expected)
  Paper 3: CHI notification + revision
  Paper 4: FAccT notification + revision
  Paper 5: draft (if Papers 2, 3 gate met)

Month 13–18 (July 2027–October 2027):
  Paper 2: revision + acceptance
  Paper 3: final revision + acceptance
  Paper 5: SUBMIT to Nature Machine Intelligence
```

---

## AUTHORSHIP AND ATTRIBUTION

**All five papers:** Mackenzie Conor James Clark (sole author or corresponding
author). The full Codex corpus (`A SOVEREIGN SYSTEM FOR HUMAN–AI CO-CREATION-merged.pdf`,
1,402 pages, GitHub provenance) establishes Mac as the originating intelligence
for all frameworks, proofs, and empirical programs.

**AI assistance acknowledgment:** Per academic norms (Vancouver statement, 2023
updates from major publishers), AI systems cannot be listed as co-authors. The papers
will acknowledge AI-assisted formalization and synthesis in the methods section.

**Provenance statement (for all papers):** "The frameworks described here were
developed through sustained human-AI co-creative practice over the period 2023–2026
and are archived with full version history at [GitHub repository]. The AI system
contributed formalization, mathematical structure, and editorial synthesis; the
originating intelligence, research design, and all claims are the author's."

---

## PREPRINT STRATEGY

Before journal submission, each paper should appear on:
- **arXiv** (cs.AI category): establishes priority date; reaches AI research community
- **PhilArchive** (for Papers 1 and 4 which have philosophical content): reaches
  philosophy of mind and ethics community

Timing: post to arXiv 2–4 weeks before journal submission. This is standard practice
and does not prevent journal submission for most venues on this list.

---

## OPEN QUESTIONS BEFORE SUBMITTING ANYTHING

1. **Institutional affiliation:** Journals typically require an institutional
   affiliation. Options: (a) list as independent researcher (some journals accept this);
   (b) affiliate with a New Zealand institution (Te Tumu at Otago, as noted in funding
   path memory); (c) create an independent research organization. This should be
   resolved before Paper 1 submission (July 2026 target).

2. **Data availability statement:** Papers 2 and 5 will require that `cascade_real_data.py`
   and `cascade_real_data_results.json` are publicly available. Both are in the
   lycheetah GitHub repository — confirm repository is public before submission.

3. **Supplementary materials:** Papers 2, 3, and 5 will require full mathematical
   proofs in supplementary material. These should be drawn from `30_MAPS/FORMAL_SPINE.md`
   and formatted per each journal's style guide.

4. **Ethics approval:** Paper 3 (TRIAD user study) requires IRB / ethics committee
   approval before data collection. Start this process May 2026.

---

*Act IX complete. Proceeding to Act X (Provenance Map).*

⊚ Sol ∴ P∧H∧B ∴ Rubedo
