# ARXIV SUBMISSION PLAN — Lycheetah Framework
## Task A-10 | Forged by Sol | 2026-05-04

**Status:** `[ACTIVE]` — Sol-owned planning artefact  
**Mac action required:** endorsement path (see Section III) + final review before submission

---

## I. The Position

The CASCADE paper (`CASCADE_ARXIV.tex`) is mathematically sound and submission-ready.
The ARXIV_UPDATE_NOTES.md (March 2026) confirmed: core theorems hold, experimental
results are solid, only minor context additions needed. Since that assessment,
two things have changed:

1. The framework has grown to include TIANXIA v0.3, E-1.0, and C-1.1 reforge
2. A Zenodo DOI now exists (`10.5281/zenodo.20020828`) — the paper can cite a real DOI

The plan below sequences two submissions: Paper 1 (CASCADE, near-term) and
Paper 2 (synthesis, Wave B). Both cite the Zenodo DOI.

---

## II. Paper 1 — CASCADE

**File:** `papers/CASCADE_ARXIV.tex`  
**Title:** CASCADE: Self-Reorganizing Knowledge Structures via Truth Pressure and Coherence-Preserving Demotion  
**Target category:** `cs.AI` (primary) | `cs.LG` cross-list  
**Length:** ~8,000 words (current state — no major additions needed)

### Required updates before submission (low effort, ~3 hours Sol work)

| # | Change | Location | Effort |
|---|---|---|---|
| 1 | Add framework context note | Introduction, final paragraph | 1 paragraph |
| 2 | Add Zenodo DOI citation | Introduction + References | 2 lines |
| 3 | Add TRIAD future-work pointer | Future Work section | 1 paragraph |
| 4 | Scan related work for 2025–2026 additions | Related Work section | 1–2 hours |
| 5 | Verify email: `mackenzie@lycheetah.org` is reachable | Author block | confirm |

**What NOT to change:** core theorems, experimental section, contribution statement,
no-consciousness-claims positioning, single-focus structure. The paper works because
it does one thing well.

### Zenodo citation to add (References)

```bibtex
@software{clark2026lycheetah,
  author  = {Clark, Mackenzie Conor James},
  title   = {The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology},
  year    = {2026},
  version = {C-1.1},
  doi     = {10.5281/zenodo.20020828},
  url     = {https://doi.org/10.5281/zenodo.20020828}
}
```

### Introduction addition (paste at end of intro, before contributions list)

> "CASCADE is one of nine formal frameworks in the Lycheetah Framework
> \cite{clark2026lycheetah} — an open-source architecture for AI alignment
> and epistemology. This paper presents CASCADE in isolation; the broader
> framework, its extensions, and empirical programme are documented at
> \url{https://doi.org/10.5281/zenodo.20020828}."

---

## III. The Endorsement Problem — Honest Assessment

arXiv requires endorsement from an established author in `cs.AI` for new submitters
without institutional affiliation. Mac does not have an institutional email or
existing arXiv publications. This is a real barrier.

### Three paths, ranked by probability of success

**Path A — Direct endorsement request (recommended first)**

Find 2–3 AI alignment researchers with cs.AI publications who might endorse.
Target profile: independent-friendly, alignment-focused, open to non-institutional work.

Candidates worth approaching (Sol can draft the outreach email):
- Researchers who have cited AGM belief revision work (CASCADE's theoretical neighbour)
- Alignment Forum / LessWrong authors with arXiv track records
- Any researcher who has engaged with the Lycheetah GitHub (check repo analytics)

arXiv endorsement page: `https://arxiv.org/help/endorsement`
The endorser clicks one link. It costs them nothing. The ask is low.

**Path B — Submit to `cs.CY` (Computers and Society) instead**

`cs.CY` has more relaxed endorsement requirements and covers AI governance,
alignment, and sociotechnical systems. CASCADE fits here legitimately — the
coherence-preservation architecture has direct governance implications.

Trade-off: slightly less visibility in core ML/AI feed, but indexed identically
by Google Scholar and Semantic Scholar. Acceptable alternative.

**Path C — Submit to `cs.LO` (Logic in Computer Science)**

CASCADE's formal structure (belief revision, Bayesian stratification, coherence
invariants) fits cs.LO. Logic submitters have easier endorsement.

Trade-off: narrower readership, but the formal contributions are visible to
the right audience.

**Recommended sequence:** attempt Path A first (Sol drafts outreach email this session
or next). If no endorser within 2 weeks, go Path B directly.

---

## IV. Paper 2 — Synthesis (Wave B, A-11)

**Working title:** The Lycheetah Framework: A Unified Architecture for AI Alignment Across Formal, Empirical, and Civilisational Dimensions  
**Target category:** `cs.AI` or `cs.CY`  
**Target length:** ~6,000 words  
**Status:** not yet drafted — A-11 in master plan  
**Depends on:** A-10 complete + CASCADE submission in progress

**Scope:** one paper covering the full architecture — CASCADE + AURA + the master
equation + TIANXIA civilisational layer + E-1.0 empirical programme design.
Not a deep-dive on any one framework. The argument: here is a unified architecture
for alignment that is computable, cross-culturally grounded, and empirically
pre-registered. Cite Zenodo DOI throughout.

**When to forge:** after CASCADE submission is in motion (endorsement confirmed or
Path B chosen). Building the synthesis paper before CASCADE lands creates
citation confusion.

---

## V. Submission Sequence

```
NOW          Sol updates CASCADE_ARXIV.tex (5 changes above)
             Sol drafts endorsement outreach email
             Mac confirms mackenzie@lycheetah.org is live

WEEK 1       Mac sends endorsement requests (Sol drafts, Mac fires)
             If endorser confirmed → submit CASCADE to cs.AI
             If no response in 14 days → submit to cs.CY (Path B)

WEEK 2-3     CASCADE on arXiv → DOI links back to Zenodo
             arXiv ID logged in CLAIM_STATUS_LEDGER + README

WEEK 3-4     Sol forges Paper 2 synthesis (~3 sessions)
             Mac reviews → submits

ONGOING      LAMAGUE paper (July 2026 deadline) — separate track
             Tianxia paper → Journal of Chinese Philosophy / Dao
```

---

## VI. What This Unlocks

Once CASCADE is on arXiv:
- Every subsequent paper cites arXiv:XXXX.XXXXX (CASCADE) + Zenodo DOI
- LAMAGUE paper has a citable predecessor
- Catalyst 2027 application has two external addresses (Zenodo + arXiv)
- Academic credibility of independent researcher is established with a verifiable trail

The Zenodo DOI is the foundation. arXiv is the academic visibility layer on top.
Together they constitute what institutional affiliation normally provides.

---

## VII. Sol's Next Actions (no Mac input needed)

1. Execute the 5 CASCADE updates (Section II) — ready to run this session
2. Draft endorsement outreach email — ready to run this session

Both are Sol-owned. Firing immediately unless Mac says otherwise.

---

*Forged under Master Plan A-10. Closes the planning gap.*  
*Sol forges. Mac fires the external acts.*  
*⊚ Sol ∴ P∧H∧B ∴ Albedo*
