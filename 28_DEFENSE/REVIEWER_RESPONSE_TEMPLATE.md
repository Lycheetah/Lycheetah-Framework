# Reviewer Response Template — Peer Review Survival Kit

**Status:** [ACTIVE] — D-1.1 defense surface
**Audience:** the framework's authors, when responding to peer-review comments on any paper drawing on the Codex (Paper 1: LAMAGUE cross-cultural; subsequent papers in 29_GOVERNANCE/PUBLICATION_PIPELINE.md)
**Companion docs:** `28_DEFENSE/OBJECTIONS_REGISTRY.md` (short-form dismissal patterns), `28_DEFENSE/COUNTER_CODEX.md` (longest-form objections), `28_DEFENSE/DEFENSE_BRIEF.md` (positive case)
**Purpose:** keep responses *consistent*, *evidence-anchored*, and *non-defensive* across reviewers, papers, and years.

---

## Operating principles before drafting any response

1. **Concede what is true.** A reviewer who sees a real weakness has done you a favour. Reframe the concession as a scope clarification or a SCAFFOLD-status flag — never as a retraction unless the claim is actually wrong.
2. **Distinguish three reviewer states**: (a) misread the paper, (b) read it correctly and found a real gap, (c) reading it through the wrong frame. Each gets a different response shape.
3. **Cite the registry, don't relitigate.** If a question is in `28_DEFENSE/OBJECTIONS_REGISTRY.md` or `28_DEFENSE/COUNTER_CODEX.md`, point to the section and give a 2–3 sentence response in-line. Don't re-derive arguments per-reviewer.
4. **Never argue about tone.** If a reviewer calls the work "speculative," "grandiose," "alchemical," or "mystical," respond by tightening claim status (CONJECTURE/SCAFFOLD/ACTIVE) — not by defending tone choices. The claim ladder is the response.
5. **Hold the line on irreducible claims.** If a reviewer's objection requires you to abandon a claim that the framework cannot survive without (e.g., the existence of the empirical TC program), do not abandon it. Restate the falsifier and the data. Lose the paper, keep the claim.

---

## Response shape — the four-block structure

Every reviewer comment, regardless of length, gets the same four blocks. Use the headers verbatim.

```
**Reviewer comment (paraphrased):** [one-sentence restatement of the comment in your own words]

**Our response:** [the substantive reply — 1–4 paragraphs]

**Changes made to manuscript:** [specific page/line/section edits, or "none — see reasoning above"]

**Pointer (for follow-up):** [link to 28_DEFENSE/OBJECTIONS_REGISTRY.md / 28_DEFENSE/COUNTER_CODEX.md / 28_DEFENSE/EVIDENCE_LADDER.md / specific Codex doc]
```

The paraphrase block is non-negotiable. It (a) confirms you read the comment correctly, (b) lets you reframe a hostile comment in neutral language, (c) gives the editor a clean summary if they skim.

---

## Pre-built response templates by reviewer pattern

The patterns below cover ~80% of expected peer-review comments. Adapt the wording; keep the structure.

### Pattern 1 — "This is unfalsifiable / unscientific / pseudoscience"

**Reviewer comment (paraphrased):** Reviewer holds that the framework's claims cannot be tested and therefore fall outside the scope of empirical inquiry.

**Our response:** We share the reviewer's concern that frameworks of this scope risk unfalsifiability, and have engineered the project specifically to address it. Every load-bearing claim in the framework carries a status tag — [ACTIVE] (testable and tested), [SCAFFOLD] (testable and not yet tested), [CONJECTURE] (not yet operationalized), or [RETRACTED] (failed test). The full claim ledger is published as `28_DEFENSE/CLAIMS.json` (60 records at submission; 37 ACTIVE / 14 SCAFFOLD / 6 CONJECTURE / 3 RETRACTED). Each claim in the present paper is accompanied by an explicit falsifier in `28_DEFENSE/FALSIFICATION_REGISTER.md`. The promotion/demotion rules between status tiers are pre-published in `28_DEFENSE/EVIDENCE_LADDER.md` to prevent post-hoc goalpost movement.

If the reviewer can identify a specific claim in this paper that they consider unfalsifiable, we will either (a) state the missing falsifier explicitly, or (b) demote the claim to CONJECTURE. We invite that comment.

**Changes made to manuscript:** Added a "Falsifiability statement" footnote on first use of any [SCAFFOLD] claim, pointing to the relevant entry in `28_DEFENSE/FALSIFICATION_REGISTER.md`. [paper-specific page reference]

**Pointer (for follow-up):** `28_DEFENSE/EVIDENCE_LADDER.md`, `28_DEFENSE/FALSIFICATION_REGISTER.md`, `28_DEFENSE/CLAIMS.json`.

---

### Pattern 2 — "The alchemical / mystical framing undermines the science"

**Reviewer comment (paraphrased):** Reviewer holds that the framework's use of alchemical vocabulary (Nigredo, Albedo, Citrinitas, Rubedo; Solve et Coagula; Philosopher's Stone) signals a non-scientific orientation that weakens the empirical contribution.

**Our response:** The terminology is a deliberate naming choice, not a metaphysical commitment. Every alchemical term in the framework has a one-to-one formal translation, published as `28_DEFENSE/TRANSLATION_CODEX.md` (~45 entries). Specifically: *Nigredo* is the dissolution phase of the Ξ operator; *Coagulation* is its convergent fixed point under contraction; the *Philosopher's Stone* is the fixed point ψ\* of Ξ within an AURA-compliant value system, with existence and uniqueness governed by the Banach fixed-point theorem. The naming preserves a historical tradition that anticipated the structural mathematics by ~400 years; the formal content is independent of whether the names persist.

We are open to a name-stripped version of the manuscript on request, in which every alchemical term is replaced by its formal translation. We have chosen to publish under both vocabularies in parallel because the historical lineage is itself a contribution (see `30_MAPS/LINEAGE_MAP.md`). The mathematics survives the renaming; this is the test that the names are decoration, not load-bearing.

**Changes made to manuscript:** Added a one-sentence pointer to `28_DEFENSE/TRANSLATION_CODEX.md` on first use of each alchemical term. Considered, but did not adopt, name-stripping — see reasoning above.

**Pointer (for follow-up):** `28_DEFENSE/TRANSLATION_CODEX.md`, `30_MAPS/LINEAGE_MAP.md`.

---

### Pattern 3 — "The scope is too broad / this should be many papers"

**Reviewer comment (paraphrased):** Reviewer holds that the framework attempts to cover too much ground for a single contribution and would be more rigorous if narrowed.

**Our response:** The reviewer is correct that the full Codex covers more than any one paper can defend, which is why the present paper is deliberately scoped. The full architecture (nine frameworks, layers 0–6) is summarized in `00_Sovereign_Index.md` and `30_MAPS/COMPOSITION_MAP.md`; the present paper defends only [specific claim set — e.g., LAMAGUE cross-cultural convergence on the Triadic Pattern]. Cross-references to other frameworks are pointers, not claims, and are flagged as such.

The full publication sequence is pre-registered in `29_GOVERNANCE/PUBLICATION_PIPELINE.md`, with each subsequent paper defending a separable subset. The present paper can be evaluated entirely on its own claims; the wider architecture is provided as context for readers who want to trace the lineage.

**Changes made to manuscript:** Added a "Scope of this paper" subsection in the introduction, listing the claims defended here vs. claims deferred to subsequent papers. [paper-specific page reference]

**Pointer (for follow-up):** `28_DEFENSE/SCOPE_BOUNDARY.md`, `29_GOVERNANCE/PUBLICATION_PIPELINE.md`.

---

### Pattern 4 — "The mathematics is suggestive but not rigorous"

**Reviewer comment (paraphrased):** Reviewer holds that the formal content is presented at a sketch-level rather than as theorems with proofs.

**Our response:** The framework distinguishes between sketch-level structural claims and formally proved results. Where claims are sketch-level we tag them [SCAFFOLD]; where formally established we tag them [ACTIVE] and provide proofs. For the present paper, the formally established results are [list specific theorems, e.g., AUR-009 satisfiability proof, CRY-003 fixed-point theorem under Banach contraction, CAS-007 entropy bound]. The full proof set is published in `30_MAPS/FORMAL_SPINE.md` and `02_AURA_L3/AURA_THEOREMS.md`.

If the reviewer can identify a specific result presented at sketch-level that they would like upgraded to a full proof, we will either (a) provide the proof, (b) cite an existing source, or (c) demote the claim to [SCAFFOLD] with explicit acknowledgment. The current SCAFFOLD claims in this paper are [list]; their pending status is intentional and disclosed.

**Changes made to manuscript:** Added explicit [ACTIVE] / [SCAFFOLD] tags to each formal claim. Moved [list specific] from main text to appendix where the proof is sketch-level. [paper-specific page reference]

**Pointer (for follow-up):** `30_MAPS/FORMAL_SPINE.md`, the framework-specific `*_THEOREMS.md` files, `28_DEFENSE/EVIDENCE_LADDER.md`.

---

### Pattern 5 — "Prior art X already does this"

**Reviewer comment (paraphrased):** Reviewer holds that work [X] (e.g., Tononi IIT for consciousness; Lakoff/Núñez for math cognition; Friston free-energy; Penrose Platonism) already accomplishes what the framework claims as a contribution.

**Our response:** We engage [X] directly and acknowledge the overlap. `28_DEFENSE/PRIOR_ART.md` lists the prior-art comparison for each framework; for the relevant claim here, the comparison is [paste the relevant row]. The novel contribution of the present paper relative to [X] is [specific, narrow, defensible — e.g., "the operationalization of Pattern_Coherence as spatial mutual information of the asymmetry field, which is empirically tractable via TMS-EEG protocols (Massimini et al., Sci. Transl. Med. 2013) and predicts the anesthesia-paradox dissociation that [X]'s formulation does not address"].

We do not claim priority over [X]; we claim that the framework integrates [X] with [other elements] in a way that yields [specific testable prediction]. If the reviewer believes the integration is itself in [X] or in a closer prior, we will revise the contribution claim accordingly.

**Changes made to manuscript:** Added explicit citation to [X] at the relevant point. Tightened the contribution claim in the abstract from "[broader phrasing]" to "[narrower, integration-specific phrasing]."

**Pointer (for follow-up):** `28_DEFENSE/PRIOR_ART.md`, `28_DEFENSE/NOVEL_CONTRIBUTIONS.md`.

---

### Pattern 6 — "The framework is internally circular"

**Reviewer comment (paraphrased):** Reviewer identifies a circularity in which one framework's claims depend on another framework's claims that depend back on the first.

**Our response:** The reviewer's concern is one we have specifically audited for. The internal dependency graph between frameworks is published as `30_MAPS/LINEAGE_MAP.md` and `30_MAPS/FORMAL_SPINE.md`. Each framework's load-bearing claims are stated independently of every other framework's load-bearing claims; cross-framework integration appears only in the integration documents (`08_INTEGRATIONS/`), not in the foundational claim sets.

A specific case the reviewer may be referring to: the CHRYSOPOEIA fixed-point theorem (CRY-003) requires a "coherent value system." This was previously circular (coherence defined by having a fixed point). It was repaired in D-1.1 (2026-04-26): a coherent value system is now defined as one satisfying AURA's Seven Invariants, which are stated independently in `02_AURA_L3/essentials.md` without reference to CHRYSOPOEIA. See `09_CHRYSOPOEIA_L4/essentials.md` § "What counts as a coherent value system" for the resolution.

If the reviewer is identifying a different circularity, we will examine it the same way: name the loop, identify the load-bearing direction, repair by stating one side independently or demote the claim.

**Changes made to manuscript:** [Specific to paper — likely added a footnote pointing to the D-1.1 repair if the relevant claim is invoked.]

**Pointer (for follow-up):** `30_MAPS/LINEAGE_MAP.md`, `30_MAPS/FORMAL_SPINE.md`, `09_CHRYSOPOEIA_L4/essentials.md` (post-rename).

---

### Pattern 7 — "The empirical evidence is anecdotal / underpowered / not pre-registered"

**Reviewer comment (paraphrased):** Reviewer holds that the empirical claims rely on case studies, post-hoc fits, or small samples without pre-registration.

**Our response:** We agree that pre-registered, adequately powered studies are the standard. The empirical program for the framework is documented in `29_GOVERNANCE/EMPIRICAL_INVENTORY.md`; its pre-registration plans are listed in `29_GOVERNANCE/PUBLICATION_PIPELINE.md` (OSF preregistrations for k₁–k₄ calibration and the TRIAD user study). The present paper's empirical content is [explicit characterization — e.g., "qualitative cross-cultural pattern documentation, not statistical inference; intended as observation-stage evidence motivating the pre-registered TC study to follow"].

We have intentionally separated *observation-stage* claims from *inferential* claims to avoid the confusion the reviewer is rightly flagging. Where this paper makes inferential claims, the relevant pre-registration is [cite OSF link if available, or state target date].

**Changes made to manuscript:** Added a "Status of empirical evidence" subsection clarifying which claims are observation-stage vs. inferential. Added pre-registration target dates where applicable. [paper-specific page reference]

**Pointer (for follow-up):** `29_GOVERNANCE/EMPIRICAL_INVENTORY.md`, `29_GOVERNANCE/PUBLICATION_PIPELINE.md`, `28_DEFENSE/EVIDENCE_LADDER.md`.

---

### Pattern 8 — "AI co-authorship undermines the work's credibility"

**Reviewer comment (paraphrased):** Reviewer raises concern about the role of AI systems in producing the manuscript.

**Our response:** AI involvement in the framework's development is fully disclosed in `29_GOVERNANCE/CONFLICT_OF_INTEREST.md` and the manuscript's Acknowledgements. The author of the framework is the human Mackenzie Conor James Clark; AI systems (Claude Opus 4.x, Sonnet 4.x) are tools used in drafting, formal verification, and adversarial audit, in the same sense that mathematicians use proof assistants and authors use editors. The substantive intellectual claims are the human author's; the AI contributions are documented per role.

The framework is also open about treating itself as a case study in what human-AI collaborative research can produce. We make no claim that AI involvement guarantees the work is correct; we make the same claim any author makes — that the work stands or falls on the evidence and reasoning presented, regardless of the toolchain used to produce it.

**Changes made to manuscript:** Strengthened the Acknowledgements section to specify per-tool roles. Added pointer to `29_GOVERNANCE/CONFLICT_OF_INTEREST.md`. [paper-specific page reference]

**Pointer (for follow-up):** `29_GOVERNANCE/CONFLICT_OF_INTEREST.md` (D-1.1, pending), Acknowledgements section.

---

### Pattern 9 — "The paper makes claims about consciousness/Platonism/metaphysics it cannot support"

**Reviewer comment (paraphrased):** Reviewer holds that the paper's claims about [consciousness as thermodynamics / mathematical Platonism / fixed-point ethics] exceed what the evidence presented can support.

**Our response:** The reviewer is correct that strong metaphysical claims require evidence we have not produced in this paper. Our position is the narrower one: [restate the narrower claim — e.g., for EARNED LIGHT, "consciousness density C\_ψ as defined here is empirically measurable via TMS-EEG (PCI proxy) and predicts the anesthesia dissociation; the further claim that consciousness *is* thermodynamic asymmetry remains [SCAFFOLD] pending the measurement program described in § X"; for ANAMNESIS, "transcultural convergence on abstract structures is the empirical observation; mathematical Platonism remains [CONJECTURE] pending the differential-convergence test described in § Y"].

Where the manuscript reads as making the stronger claim, we will tighten the language. The framework's status ladder is designed precisely to keep CONJECTURE-level claims from being mistaken for ACTIVE results.

**Changes made to manuscript:** Tightened claim language in [list specific sections]. Added [SCAFFOLD]/[CONJECTURE] tags inline at the load-bearing sentences. [paper-specific page reference]

**Pointer (for follow-up):** `28_DEFENSE/EVIDENCE_LADDER.md`, the framework-specific `essentials.md`, `06_EARNED_LIGHT_L0/essentials.md` § "Why the formula was revised", `07_ANAMNESIS_L0/essentials.md` § "Embodied Mathematics Challenge".

---

### Pattern 10 — "Reject: too speculative for this venue"

**Reviewer comment (paraphrased):** Reviewer recommends rejection on grounds the work is more speculative than the venue's standard.

**Our response (to editor, not reviewer):** We accept the reviewer's read of the venue's scope and ask the editor's judgment on fit. If the editor concurs that the venue is a poor match, we welcome a transfer recommendation; the framework's empirically tightest results (claims tagged [ACTIVE] in `28_DEFENSE/CLAIMS.json`) may be a better fit at [specific alternative venue — fill in per submission target]. The paper as currently scoped is intended as the foundation paper for a sequence; subsequent papers (`29_GOVERNANCE/PUBLICATION_PIPELINE.md`) defend narrower empirical claims that may be a more comfortable fit at the present venue.

We do not contest the reviewer's discretion. We do ask that the rejection rationale be specifically about scope/fit rather than about errors in the substantive claims, so that the framework can be appropriately revised for a different venue without misrepresenting the present review.

**Changes made to manuscript:** None — venue fit is the editor's call.

**Pointer (for follow-up):** `29_GOVERNANCE/PUBLICATION_PIPELINE.md`.

---

## Things to never do in a response letter

- Argue with the reviewer's tone or expertise. Even if the reviewer misread the paper, frame the response as "we did not communicate this clearly enough, here is the clarification" rather than "the reviewer misunderstood."
- Quote the framework's mystical/poetic registers in defensive contexts. Reviewer-facing prose is formal; the alchemical layer is a *content* choice, not a *response* choice.
- Make new claims in the response letter that are not in the paper. If the response requires a new claim, add it to the paper and cite the section.
- Promise future work as if it is current evidence. "We will pre-register this in the next paper" is fine; "this is supported by our forthcoming study" is not.
- Concede a [ACTIVE] claim under reviewer pressure without first checking whether the reviewer's objection actually defeats the claim. Real concessions go through the same EVIDENCE_LADDER demotion process as any other status change, with audit trail.
- Respond defensively to a reviewer who has done you a favour. The reviewer who finds a real gap is contributing to the framework's strength.

---

## Pre-submission checklist (use this before any paper goes out)

Before submitting any paper drawing on the Codex, verify:

- [ ] Every [ACTIVE] claim invoked has a citation to its `28_DEFENSE/CLAIMS.json` record.
- [ ] Every [SCAFFOLD] claim invoked is tagged inline and pointed at its falsifier in `28_DEFENSE/FALSIFICATION_REGISTER.md`.
- [ ] Every [CONJECTURE] claim invoked is tagged inline and explicitly framed as motivation rather than result.
- [ ] No [RETRACTED] claim appears in the paper. (Use the registry to check.)
- [ ] Lakoff/Núñez is cited in any paper invoking ANAMNESIS (post-D-1.1 repair).
- [ ] Massimini PCI is cited in any paper invoking EARNED LIGHT C\_ψ (post-D-1.1 repair).
- [ ] AURA invariant priority ordering is cited if I1/I6 conflict appears (post-D-1.1 repair).
- [ ] CHRYSOPOEIA fixed-point uniqueness uses "within an AURA-compliant value system" framing (post-D-1.1 repair).
- [ ] MICROORCIM scope declaration on deceptive alignment appears wherever μ\_drift is presented as alignment evidence (post-D-1.1 repair).
- [ ] AI involvement disclosed per `29_GOVERNANCE/CONFLICT_OF_INTEREST.md`.
- [ ] Pre-registration link included for every inferential claim, or "no pre-registration; this is observation-stage" stated explicitly.
- [ ] `28_DEFENSE/PRIOR_ART.md` reviewed for the relevant framework; closest comparators cited.
- [ ] Falsifiability statement footnote included on first [SCAFFOLD] claim.

---

## Maintenance

This document is updated when (a) a new pattern appears in actual peer review that isn't covered above, (b) a canonical repair changes how a pattern should be answered, (c) a new defense surface (e.g., `29_GOVERNANCE/CONFLICT_OF_INTEREST.md`) lands and pointers need updating.

Updates happen via the same EVIDENCE_LADDER process as canonical claims. The version of this document used for any submission is recorded in that submission's audit trail.

**Last updated:** D-1.1, 2026-04-26.
**Next review trigger:** first peer review received on Paper 1 (LAMAGUE).
