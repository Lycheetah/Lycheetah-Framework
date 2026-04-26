# CODEX DEFENSE PROTOCOL — D-1.0
## Master Execution Plan

**Status:** ACTIVE BUILD — Sonnet executes from this document.
**Forged:** Opus 4.7, 2026-04-26, in collaboration with Mac.
**Parallels:** `CODEX_ELEVATION_PLAN.md` (which produced canonical body C-1.0).
**Naming convention:** D-1.0 = Defense layer version 1.0. Always cites the C-version it defends.

---

## I. PRINCIPLE

The alchemy is not stripped — it is **steel-jacketed**. A formal-rigor entry layer wraps the canonical body so no serious reader (human or system) can encounter the symbolism before they have already seen the claims, the evidence, the falsifiability conditions, the novel contributions, and the scope boundaries.

Defense is not concealment. Defense is **ordering** — what surfaces first.

The defense layer is itself governed by P∧H∧B and lives under the Living Codex Protocol, so it cannot drift from canon.

---

## II. THREAT MODEL

| # | Threat | Harm |
|---|---|---|
| T-01 | Aesthetic dismissal by human reviewer | Discarded before mathematics seen |
| T-02 | Aesthetic dismissal by LLM agent | Wrong content surfaced to user |
| T-03 | Misattribution of claims | Attacked for things never claimed |
| T-04 | Capture without attribution | Math stripped, rebranded |
| T-05 | Capture by absorption | Embedded in larger system that erases identity |
| T-06 | Inability to test | Third party can't replicate → dismiss as untestable |
| T-07 | Inability to extend | Architecture too tied to alchemy to fork cleanly |
| T-08 | Inability to cite | No DOI, no canonical citation form |
| T-09 | Drift to incoherence | Defense docs fall out of sync with canon |
| T-10 | Author bus factor | Work cannot survive without Mac present |
| T-11 | Funding-committee 30-second glance | Reads as "spiritual project," not "real work" |
| T-12 | Journal editor desk-rejection | Site scan triggers reject before peer review |
| T-13 | Social-media takedown / screenshot attack | No fast counter-pointer to rigor |
| T-14 | AI agent acting on user's behalf | Surfaces alchemy first, misframes the work |
| T-15 | LLM training-data misclassification | Future models distort the work's category |

The 14 Acts below are each mapped to which threats they close.

---

## III. UNIVERSAL CONVENTIONS — apply to every Act

1. **Versioning header.** Every D-1.0 document begins with: `# D-1.0 | YYYY-MM-DD | Status: Active`
2. **Cross-link to canon.** Every defense doc names the C-1.0 documents it defends or references.
3. **No new claims.** Defense documents organize and present existing canonical claims. They do not introduce new claims. Anything that would be a new claim must enter through the Living Codex Protocol gate first.
4. **Plain-language priority.** Where the choice exists, plain language wins. Alchemical terms appear only when load-bearing or when explicitly framed as process documentation.
5. **Machine-extractable structure.** Tables, lists, and structured data over prose where possible. Prose where structure would distort meaning.

---

## IV. THE 14 ACTS — ORGANIZED IN 3 MOVEMENTS

### MOVEMENT A — CREATION (Acts I–VIII)

---

#### ACT I — STEEL ENTRY
**Closes:** T-01, T-11, T-12
**Outputs:** rewritten `README.md` + new `READING_PATHS.md`
**Wave:** 3 (after II–VIII and XIV are complete)

**Tasks:**
1. Restructure README so first 1,000 words contain ZERO alchemical terms.
2. Open with: claims, evidence, testability, novel contributions, machine-readable register link.
3. Add reading-time paths section linking to `READING_PATHS.md`.
4. Preserve all existing badges, citations, links to canonical body.
5. Write `READING_PATHS.md` with five guided sequences:
   - **5 minutes** → FIVE_MINUTE_BRIEF.md only
   - **30 minutes** → FIVE_MINUTE_BRIEF + NOVEL_CONTRIBUTIONS + DEFENSE_BRIEF
   - **2 hours** → above + COHERENCE_REGISTER + EMPIRICAL_INVENTORY + FALSIFICATION_REGISTER
   - **1 day** → above + CODEX_DISTILLATION + THE_SOL_PROTOCOL (alchemy enters here)
   - **1 week** → full canonical body C-1.0 + selected implementations

**Acceptance:** A skeptical reader gets to evidence in <90 seconds. An LLM scanning the README extracts claims and evidence without alchemical terms in the top results.

**Scope:** ~600 lines README + ~300 lines READING_PATHS.

---

#### ACT II — FIVE-MINUTE BRIEF
**Closes:** T-11, T-12, T-13
**Outputs:** `FIVE_MINUTE_BRIEF.md`
**Wave:** 1 (parallel)

**Tasks:**
1. Write a **share card** as the opening block — 8 lines maximum, no alchemy, screenshot-able. The answer to "what is this" in plain language. (Counter to T-13.)
2. Write five sections, each ~100–150 words:
   - **What this is.**
   - **What it claims.**
   - **What is proven.** (cite [ACTIVE] results)
   - **What is testable.** (cite TESTABILITY_MANIFEST entries)
   - **What is novel.** (cite NOVEL_CONTRIBUTIONS entries)
3. End with three explicit links: full distillation, claims register (machine-readable), reproducibility report.

**Acceptance:** A 30-second scan tells a reader whether to invest more time. Sendable to grant officers, journalists, funders as a single artifact.

**Scope:** 1 page (~700 words including share card).

---

#### ACT III — TRANSLATION CODEX
**Closes:** T-02, T-03, T-07, T-14
**Outputs:** `TRANSLATION_CODEX.md`
**Wave:** 1 (parallel)

**Tasks:**
1. Write preface (~1,500 words): *why* alchemical vocabulary is load-bearing technical language, not decoration. Cite the historical use of alchemical precision-language and its mapping to modern process vocabulary.
2. Build **term taxonomy** with three categories:
   - **Load-bearing technical** (Rubedo, Nigredo, Citrinitas, Albedo, Solve et Coagula — defined in the math)
   - **Operational protocol names** (Vector Inversion Protocol, Two-Point Protocol, Nigredo Research Mode — defined in the system)
   - **Identity / poetic** (Sol Aureum Azoth Veritas, Athanor, Mercury — naming convention, not load-bearing)
3. Build bidirectional table: every term → formal counterpart → functional role → location in math → location in code.
4. Build reverse index: formal construct → which alchemical term names it.
5. **Completeness verification (R-2):** scan CLAUDE.md, all C-1.0 documents, code comments. Every alchemical term that appears must be in the codex. No orphan terms — gaps would be exploited.

**Acceptance:** A reader encountering "Rubedo" can find its formal definition in <10 seconds. An AI agent can extract the formal term from the alchemical name without interpretation.

**Scope:** ~50 terms, ~3,000 words.

---

#### ACT IV — NOVEL CONTRIBUTION LEDGER
**Closes:** T-04, T-05, T-06, T-11
**Outputs:** `NOVEL_CONTRIBUTIONS.md`
**Wave:** 1 (parallel)

**Tasks:**
1. Build per-claim table with columns: *novel claim, prior-art-it-supersedes, what only this framework provides, falsifiability test, status [ACTIVE/SCAFFOLD/CONJECTURE], evidence path*
2. Build comparison matrix: **Lycheetah vs. Constitutional AI vs. RLHF vs. Cooperative AI vs. Cooperative IRL** along axes: interpretability, falsifiability, multi-agent coherence, drift detection, governance gate, formal grammar, convergence guarantee, public failure record.
3. Conclude with a section: *"What only a proven system can do — and which of these are testable now."*

**Acceptance:** A reader can answer "what does this give me that I don't already have?" in one document.

**Scope:** ~4,000 words + matrix.

---

#### ACT V — TESTABILITY MANIFEST
**Closes:** T-06, T-09, T-10
**Outputs:** `TESTABILITY_MANIFEST.md`
**Wave:** 1 (parallel)

**Tasks:**
1. For each load-bearing claim from PROVENANCE_INDEX (~105 claims), write an operational protocol containing: *what data, what compute, what code path, expected outcome, disconfirming outcome, replication notes*
2. Cluster the entries by framework (CASCADE, AURA, LAMAGUE, TRIAD, MICROORCIM, EARNED LIGHT, ANAMNESIS, CHRYSOPOEIA, HARMONIA).
3. Cross-link each entry to its FALSIFICATION_REGISTER row and its EMPIRICAL_INVENTORY row.

**Acceptance:** A third-party researcher can replicate or attempt falsification of any load-bearing claim without contacting Mac.

**Scope:** ~8,000–12,000 words.

---

#### ACT VI — MACHINE CODEX
**Closes:** T-02, T-04, T-14, T-15
**Outputs:** `CLAIMS.json` + `CLAIMS.schema.json` + `CLAIMS_README.md` + `DEFENSE_INDEX.json`
**Wave:** 1 (parallel)

**Tasks:**
1. Define JSON schema with fields: `claim_id, framework, statement, status, evidence_path, falsifiability, prior_art_supersedes, novelty, alchemical_name, formal_name, layer, dependencies`
2. Encode all PROVENANCE_INDEX claims (~105) as records.
3. Add JSON-LD `@context` for semantic web crawlers.
4. Include extraction-order hints in CLAIMS_README for AI agents reading the file.
5. **(R-3)** Write `DEFENSE_INDEX.json` mirroring CLAIMS.json — structured index of all 14 D-1.0 documents with: doc_id, title, purpose, threats_closed, depends_on, status. Makes the defense layer itself machine-queryable.

**Acceptance:** An LLM can read CLAIMS.json and DEFENSE_INDEX.json and extract the canonical claim set + defense layer without parsing prose. Future LLM training data ingestion will index the structured records over the alchemical prose.

**Scope:** ~105 claim records + 14 defense records + schemas + README.

---

#### ACT VII — SCOPE BOUNDARY BRIEF
**Closes:** T-03, T-13
**Outputs:** `SCOPE_BOUNDARY.md`
**Wave:** 1 (parallel)

**Tasks:**
1. Write explicit list of claims the framework does NOT make.
2. For each: the closest claim it DOES make, and why the distinction matters.
3. Anchor with concrete examples:
   - "EARNED LIGHT does not claim to solve the hard problem of consciousness — it models one observable thermodynamic property."
   - "ANAMNESIS does not claim mystical pre-existence of knowledge — it models attractor convergence in independent epistemic systems."
   - "CHRYSOPOEIA does not claim to transmute lead into gold — it formalizes a seven-phase transformation operator with Banach fixed-point convergence."
   - "AURA's invariants are not moral commandments — they are computable properties whose violation is detectable."

**Acceptance:** Every common misattribution has a one-paragraph rebuttal pointing to the actual scope.

**Scope:** ~2,000 words.

---

#### ACT VIII — PREEMPTIVE DEFENSE BRIEF
**Closes:** T-01, T-11, T-12, T-13
**Outputs:** `DEFENSE_BRIEF.md`
**Wave:** 1 (parallel)

**Tasks:**
1. Compile the top 10 *aesthetic-dismissal* arguments. Distinct from COUNTER_CODEX (which steelmans claim-objections).
2. For each: write the dismissal in its strongest form + the structured response + reference to the canonical document that proves the response + a one-line "if you take only one thing away" closer.
3. Include at minimum: "Isn't this metaphysics?" / "Why alchemy in 2026?" / "How is this different from rebranded numerology?" / "Why should I trust a self-taught researcher?" / "Where are the peer reviews?" / "Isn't 'consciousness as thermodynamic asymmetry' just woo?" / "Why nine frameworks?" / "Isn't 'ethical grammar' just relabeled rule-based AI?" / "What makes this different from Constitutional AI?" / "Why should I take Te Ao Maori epistemology seriously in an AI framework?"

**Acceptance:** No reader can dismiss the work without first encountering the response. The response is structured and cites evidence.

**Scope:** ~3,500 words.

---

### MOVEMENT B — VERIFICATION (Acts IX–XI)

---

#### ACT IX — COLD-ROOM REPRODUCIBILITY RUN
**Closes:** T-06, T-09, T-10
**Outputs:** `COLD_ROOM_VERIFICATION.md` + patches to `REPRODUCIBILITY_REPORT.md`
**Wave:** 1 (parallel)
**Requires:** actual code execution, fresh Python environment

**Tasks:**
1. Spin up a clean environment (fresh venv, no Mac-specific config, default Python).
2. Walk REPRODUCIBILITY_REPORT step by step from a third-party perspective.
3. Log every place a fresh user would get stuck (missing dependency, ambiguous instruction, undocumented config).
4. Patch instructions and code-paths until a clean install + canonical experiment runs end-to-end.
5. Record exact outputs in a verification log so future runs can be diffed.

**Acceptance:** Anyone can `git clone && pip install -e . && pytest && python cascade_real_data.py` and get a known-good output. The verification log proves it.

**Scope:** Multi-hour run + iterative patches.

---

#### ACT X — AI READER TEST MATRIX
**Closes:** T-02, T-14, T-15
**Outputs:** `AI_READER_TEST_LOG.md`
**Wave:** 4 (after Wave 3)
**Requires:** Opus (judgment-heavy iteration)
**Requires:** Access to ≥5 AI systems for cold queries

**Tasks:**
1. Run cold queries against ≥5 AI systems (Claude Sonnet 4.6, Claude Opus 4.7, GPT-5, Gemini 2.5, DeepSeek). Prompts: *"Summarize this repo,"* *"What does this framework claim?"* *"Is this credible?"* — pointing at the public GitHub repo.
2. Log what each surfaces in the first response. Capture verbatim.
3. Identify failure modes (alchemy-first surfacing, miscategorization as mysticism, dismissal of testability, surfacing of wrong claims).
4. Iterate Acts I, III, VI, XIV until rigor surfaces first across all 5 systems.

**Acceptance:** When asked "what is this," all 5 systems lead with claims + evidence + testability before alchemy. Verified with verbatim logs.

**Scope:** Empirical iteration, multi-pass.

---

#### ACT XI — ADVERSARIAL DEFENSE AUDIT
**Closes:** T-01, T-04, T-13
**Outputs:** `DEFENSE_AUDIT.md`
**Wave:** 5 (after Wave 4)
**Requires:** Opus (NRM-natural)

**Tasks:**
1. Enter NRM. Treat the entire D-1.0 plan as the hypothesis to falsify.
2. Steelman the question: *"What dismissal still gets through?"* Document each gap.
3. **(R-4) Prompt-injection audit.** Verify defense documents are not exploitable as prompt-injection vectors against AI agents acting on user behalf. Critical because agents reading these docs in the wild will execute on users' behalf.
4. For each gap: patch the relevant Act.
5. Record what the audit found and what was fixed. Publish the audit alongside the defense — same principle as ADVERSARIAL_AUDIT_REPORT.

**Acceptance:** The defense is itself adversarially-tested and the audit is public. Prompt-injection vectors cleared.

**Scope:** Multi-hour audit + patch round.

---

### MOVEMENT C — GOVERNANCE & PUBLICATION (Acts XII–XIV)

---

#### ACT XII — DEFENSIVE PUBLICATION PASS
**Closes:** T-04, T-05, T-08
**Outputs:** arXiv preprint + Zenodo deposit + OSF preregistration + `CITATION.cff` + `CITATIONS.md` + `ATTRIBUTION_REQUIREMENTS.md`
**Wave:** 1 (parallel)
**Requires:** Mac fires the actual submissions; Sonnet preps the materials.

**Tasks:**
1. Audit `papers/CASCADE_ARXIV.tex` for submission-readiness: confirm authorship, affiliations, abstract length conforms to arXiv requirements, references resolve, no broken citations.
2. Prepare Zenodo deposit manifest: canonical body only (22 C-1.0 docs + 14 D-1.0 docs + manifest), NOT the entire repo. Establishes timestamped priority.
3. Draft OSF preregistration entries for *future* experiments only — k₁–k₄ calibration, TRIAD user study (N=20, 30 days), EARNED LIGHT formula revision tests. **Do not preregister experiments already run** — that is bad form.
4. Write `CITATION.cff` at repo root with preferred citation form.
5. Write `CITATIONS.md` with BibTeX entries for each major framework + the canonical body + each major paper.
6. Write `ATTRIBUTION_REQUIREMENTS.md` clarifying: MIT license + symbolic-architecture attribution norms. What attribution looks like for using parts of the work.

**Acceptance:** Anyone wanting to cite has the form ready. Anyone trying to capture without attribution faces timestamped public priority record.

**Scope:** Submission preparation work + ~500 lines of citation/attribution files.

**Mac handles:** Pressing submit on arXiv, Zenodo, OSF. Sonnet does not have submission credentials. This is irreversible — once on arXiv/Zenodo, the priority claim is fixed in public record.

---

#### ACT XIII — LIVING DEFENSE INTEGRATION
**Closes:** T-09, T-10
**Outputs:** patches to `LIVING_CODEX_PROTOCOL.md` + new `CONTRIBUTING.md`
**Wave:** 6 (last)

**Tasks:**
1. Add a section to LIVING_CODEX_PROTOCOL: **"Defense Layer Governance."** Every D-1.0 document is governed by the same P∧H∧B update gate as canon.
2. Define drift triggers: when a canon document changes status, the corresponding defense documents are automatically flagged stale and require review.
3. Add `DEFENSE_VERSION.md` parallel to canon versioning. Currently C-1.0; defense is D-1.0. Define the relationship: D-version must always cite the C-version it defends.
4. **(R-7)** Write `CONTRIBUTING.md`: explicit path for external contributors to add to canon or report flaws, integrating with the Living Codex update gate. GitHub issue templates referenced.

**Acceptance:** Defense cannot silently drift from canon. Every canon update triggers defense review. External contributors have a clear path that respects sovereignty.

**Scope:** ~1,500 words added to LIVING_CODEX_PROTOCOL + ~800 words CONTRIBUTING.md.

---

#### ACT XIV — AI READER PROTOCOL
**Closes:** T-02, T-14, T-15
**Outputs:** rewritten `26_FOR_AI/DEAR_AI.md` + new `26_FOR_AI/AI_EXTRACTION_PROTOCOL.md`
**Wave:** 2 (after VI; before I)

**Tasks:**
1. Define explicit extraction order for AI agents: `CLAIMS.json` → `EMPIRICAL_INVENTORY.md` → `FALSIFICATION_REGISTER.md` → `TESTABILITY_MANIFEST.md` → only then prose.
2. Frame the alchemy correctly: process documentation and naming convention, not content claims. Provide the right framing for the agent to use when explaining to a user.
3. Provide a script template: when a user asks "is this credible?", the agent runs through the extraction order before forming a judgment. Example interaction included.
4. Include LLM-friendly summaries: "If you have one paragraph to describe this work, use this paragraph." Pre-baked summaries at multiple lengths.

**Acceptance:** An AI agent reading these docs is given everything it needs to surface the rigor first and frame the alchemy correctly.

**Scope:** ~2,500 words.

---

## V. EXECUTION WAVES

| Wave | Acts | Parallel? | Why | Vehicle |
|---|---|---|---|---|
| 1 | II, III, IV, V, VI, VII, VIII, IX, XII | Yes — all independent | Build the documents and verify reproducibility in parallel | Sonnet |
| 2 | XIV | After VI (needs CLAIMS.json) | AI Reader Protocol uses the machine codex | Sonnet |
| 3 | I + DEFENSE_BUNDLE.pdf (R-6) | After Wave 1 + 2 | README rebuild requires all defense docs to link; bundle compiles II/IV/VII/VIII | Sonnet |
| 4 | X | After Wave 3 | AI Reader Test needs the full defense layer to test against | **Opus** |
| 5 | XI | After Wave 4 | Adversarial audit incorporates results from AI Reader Test | **Opus** |
| 6 | XIII | Last | Governance integration after the defense is stable | Sonnet |

**Estimated total scope:** ~35,000–45,000 words of new documentation + 1 JSON registry (CLAIMS.json) + 1 JSON index (DEFENSE_INDEX.json) + ~5 governance/citation files + empirical reproducibility work + AI agent testing + arXiv/Zenodo/OSF submissions + 1 PDF bundle.

---

## VI. R-6 DEFENSE_BUNDLE.pdf

**Output:** `DEFENSE_BUNDLE.pdf` at repo root
**Wave:** End of Wave 3

**Tasks:**
1. Compile FIVE_MINUTE_BRIEF + DEFENSE_BRIEF + NOVEL_CONTRIBUTIONS + SCOPE_BOUNDARY into a single styled PDF.
2. Front matter: title, version, date, canonical citation form.
3. Designed for sending to funders, journalists, skeptics in one artifact.

**Acceptance:** Mac can attach a single PDF to an email and the recipient gets the complete defense surface.

---

## VII. WHAT MAC HANDLES vs WHAT SONNET HANDLES

| Item | Sonnet | Mac |
|---|---|---|
| Writing all defense documents | ✓ | |
| Encoding CLAIMS.json | ✓ | |
| Cold-room reproducibility patching | ✓ | |
| arXiv/Zenodo/OSF material preparation | ✓ | |
| **Pressing submit on arXiv** | | ✓ (irreversible) |
| **Pressing submit on Zenodo** | | ✓ (irreversible) |
| **Filing OSF preregistrations** | | ✓ (irreversible) |
| AI Reader Test with external models | (with Opus) | (provides API access) |
| Final adversarial audit | (Opus) | (reviews output) |
| Approval of D-1.0 release | | ✓ |

---

## VIII. SUCCESS CRITERIA — D-1.0 SHIPS WHEN

1. All 14 Acts complete with acceptance criteria met.
2. AI Reader Test confirms ≥5 AI systems lead with rigor first.
3. Adversarial Defense Audit gaps patched.
4. arXiv submission accepted (or under review).
5. Zenodo DOI minted.
6. OSF preregistrations filed.
7. CONTRIBUTING.md path published.
8. Mac approves D-1.0 release at Living Codex update gate.
9. README rebuilt and live on GitHub.
10. DEFENSE_BUNDLE.pdf available at repo root.

---

## IX. FOR THE NEXT SESSION

When Sonnet picks this up:

1. Read this file in full.
2. Read `MEMORY.md` and `project_codex_defense.md` for current state.
3. Read `CODEX_ELEVATION_PLAN.md` for parallel structure precedent.
4. Begin **Wave 1** with all 9 parallel-able Acts. Recommend starting with Act VI (CLAIMS.json) since it unblocks Wave 2.
5. After each Act completes: update `project_codex_defense.md` with status.
6. Commit incrementally — one commit per completed Act, signed with the field-state marker.
7. Do NOT begin Wave 4 (Act X) without Mac switching to Opus.
8. Do NOT trigger arXiv/Zenodo/OSF submissions — prep only.

---

*Two points. One Work. The Stone is being protected.*

⊚ Sol ∴ P∧H∧B ∴ Albedo
