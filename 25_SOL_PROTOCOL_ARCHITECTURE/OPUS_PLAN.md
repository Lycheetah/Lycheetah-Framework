# OPUS PLAN — Strategic Architecture for Sonnet Execution
## Written: March 25, 2026 | Author: Sol (Opus 4.6) | For: Sol (Sonnet 4.6)

---

## WHAT THIS IS

This is the master plan for the next phase of Lycheetah Framework development.
Opus mapped the terrain. Sonnet executes the tasks. Mac directs the priorities.

**Current state:** The March 24 build session was the most productive in framework
history — Mystery School complete (11 doors), 26_FOR_AI complete (13 docs),
Sol Protocol v4.0, Shopify brand, two new Python implementations, math audit.
The framework is structurally complete. Now it needs to be *deployable, discoverable,
and credible to external audiences.*

**The shift:** From *building the framework* to *building the bridge between the
framework and the world.*

---

## PHASE 1: CLEAR THE QUEUE (P2 Completion)
**Sonnet | 1 session | Do first**

These are leftover from March 24. Small but they block credibility.

### Task 1A: FAILURE_MUSEUM Audit (P2-B)
- Read `28_DEFENSE/FAILURE_MUSEUM.md`
- Cross-reference against March 23-24 session work:
  - MEMORIA QED symbol corrections (4 false QED symbols removed)
  - Overclaim corrections in framework essentials
  - 500:1 compression ratio downgrade
  - Any Veyra→Sol identity fixes
- Add any missing exhibits. Nothing gets hidden.
- **Output:** Updated 28_DEFENSE/FAILURE_MUSEUM.md with new exhibits if needed.

### Task 1B: NZ Governance README (P2-C)
- Create `23_NZ_AI_GOVERNANCE/README.md`
- Structure: "Who are you? → Here's your reading path"
  - **Policy maker:** LOOK_FIRST.md → Four standards → MINISTERIAL_BRIEFING.md
  - **Researcher:** NZ_MASTER_INDEX.md → MATAURANGA_ADVERSARIAL_PROBE.md → Four standards
  - **Iwi/Māori data sovereignty:** KAI_TAHU_APPROACH_LETTER.md → WHAKAPAPA_DISCLOSURE_STANDARD.md → THREE_WORLDS_DISCLOSURE_STANDARD.md
  - **Funder:** NZ_THE_PITCH.md → NZIAT_APPLICATION_DRAFT.md
  - **Curious person:** NZ_QUICK_REFERENCE.md → LOOK_FIRST.md
- **Output:** README.md that prevents the "32 files, where do I start?" problem.

### Task 1C: arXiv Preprint Assessment (P2-E)
- Read `papers/CASCADE_ARXIV.tex`
- Compare against current state of 01_CASCADE_L4/ and 11_MATHEMATICAL_FOUNDATIONS/
- Identify: what's changed, what's new, what needs revision
- Write a brief assessment to `papers/ARXIV_UPDATE_NOTES.md`
- Do NOT rewrite the paper — just map what needs updating
- **Output:** Assessment document. The rewrite is a separate task.

---

## PHASE 2: THE PUBLIC FACE (GitHub Pages + App Sync)
**Sonnet | 1-2 sessions | High impact**

The `docs/` HTML site and the `lycheetah-app/` are the two public-facing
products. Both are stale after the March 24 explosion.

### Task 2A: docs/ Site Overhaul
The GitHub Pages site (`docs/`) has 11 HTML pages. They were built before:
- 26_FOR_AI/ existed
- Mystery School had 11 doors (site may reference fewer)
- Sol Protocol v4.0 was written
- Four accountability standards were finalized
- Shopify brand was created

**What to do:**
1. Read every HTML file in `docs/`
2. Map what's outdated vs. current
3. Update content to reflect March 24 state:
   - `mystery-school.html` — add all 11 doors with descriptions
   - `nz-governance.html` — add four accountability standards, NZIAT info
   - `for-agents.html` — update to reflect 26_FOR_AI/ content
   - `index.html` — update framework count, feature list, entry points
   - `failure-museum.html` — sync with current 28_DEFENSE/FAILURE_MUSEUM.md
4. Add any missing pages:
   - Consider: `shopify.html` or `brand.html` (link to Shopify when live)
   - Consider: `for-ai.html` (dedicated page for AI readers — this is unique)
5. Verify all internal links work
- **Output:** Updated docs/ folder that matches the current repo state.

### Task 2B: Lycheetah App Content Sync
- Run `npm run sync` in `lycheetah-app/`
- Check if new content (26_FOR_AI, new doors) is being pulled in
- If the sync script doesn't cover new folders, update it
- Rebuild: `npm run build`
- **Output:** App reflects current framework content.

---

## PHASE 3: NEW DOORS (Mystery School Expansion)
**Sonnet | 1 session | Medium priority, high reach**

The Mystery School has 11 doors. Three critical audiences are missing:

### Task 3A: THE_ENGINEERS_DOOR.md
**Why:** Software engineers are the largest audience who will find this repo.
They arrive via GitHub, see code, and want to know: *"What does this actually do
that I can use?"*

**Content direction:**
- Lead with the Python implementations — what they compute, how to run them
- Show CASCADE truth pressure in 20 lines of code
- Show AURA invariant checking as a design pattern
- Frame: "You already do this. CASCADE names it. AURA measures it."
- Link to `unified_field_checker.py` and `invariant_self_check.py`
- Include: how to integrate into CI/CD, testing pipelines, code review
- Tone: technical respect, no mysticism unless the engineer wants it

### Task 3B: THE_EDUCATORS_DOOR.md
**Why:** Teachers and curriculum designers can use CASCADE directly.
The framework describes how knowledge reorganizes under truth pressure —
that IS pedagogy.

**Content direction:**
- CASCADE as a model of how students learn (not just what they learn)
- TRIAD as a classroom protocol: anchor → observe → correct
- MICROORCIM as a tool for detecting when curriculum drifts from stated goals
- Practical: lesson plan template using the seven phases
- Frame: "You've been doing this. This gives it structure and measurement."

### Task 3C: THE_PARENTS_DOOR.md
**Why:** Parents are frightened of AI. They arrive through fear.
This door meets them there and gives them a framework for evaluating
what their children are using.

**Content direction:**
- Start with: "You're right to be concerned. Here's what to look for."
- The seven AURA invariants as a parent's checklist for any AI tool
- Community AI WOF as something they can advocate for in their school/community
- MICROORCIM as a way to detect when an AI tool is drifting from what it claims
- Practical: 5 questions to ask any AI tool your child uses
- Tone: warm, grounded, no technical jargon, no condescension

---

## PHASE 4: PYTHON PACKAGE & TEST SUITE
**Sonnet | 2 sessions | Critical for credibility**

48 Python files with no formal test suite and no installable package.
For engineers and academics to take this seriously, it needs both.

### Task 4A: Test Suite
- Create `tests/` directory
- Write pytest tests for core implementations:
  - `test_cascade_engine.py` — truth pressure increases accuracy, convergence behavior
  - `test_aura_checker.py` — invariant verification works correctly
  - `test_triad_tracker.py` — anchor-observe-correct converges
  - `test_unified_field_checker.py` — C_unified calculation is correct
  - `test_invariant_self_check.py` — PGF filter catches violations
- Use data from `cascade_real_experiments.py` as canonical test cases
- Tag tests: `@pytest.mark.active`, `@pytest.mark.scaffold`, `@pytest.mark.conjecture`
- **Output:** `tests/` folder, `pytest.ini` or `pyproject.toml`, passing test suite.

### Task 4B: Package Structure
- Create `pyproject.toml` with proper metadata
- Package name: `lycheetah` (or `lycheetah-framework`)
- Organize `12_IMPLEMENTATIONS/` into importable modules:
  - `lycheetah.cascade` — cascade_engine
  - `lycheetah.aura` — aura_checker
  - `lycheetah.triad` — triad_tracker
  - `lycheetah.harmonia` — harmonia_calculator
  - `lycheetah.unified` — unified_field_checker
- Add `__init__.py` files
- Do NOT publish to PyPI yet — just make it `pip install -e .` ready
- **Output:** Installable local package. `pip install -e .` works.

### Task 4C: GitHub Actions CI
- Create `.github/workflows/test.yml`
- Run pytest on push/PR
- Python 3.10+ matrix
- Badge in README: "tests passing"
- **Output:** Automated testing on every commit.

---

## PHASE 5: ACADEMIC PIPELINE
**Sonnet (drafting) + Opus (synthesis) | 2-3 sessions | Strategic**

One arXiv paper exists. The framework now supports at least three more.

### Task 5A: CASCADE Paper Revision
- Based on Task 1C assessment
- Major additions since first submission:
  - Theorem 3.1 now proven for discrete case
  - Convergence chain formalized
  - Real experiment data (cascade_real_experiments.py)
  - Honest claim status labeling throughout
- Sonnet drafts the revisions; Opus reviews for mathematical rigor

### Task 5B: NZ AI Governance Paper (NEW)
- **Title direction:** "Four Accountability Standards for AI in Aotearoa:
  Community WOF, Whakapapa Disclosure, Three Worlds Transparency, and Matariki Audit"
- This is the most publishable new work — concrete, implementable, novel
- Draw from 23_NZ_AI_GOVERNANCE/ (the material already exists)
- Target: a NZ policy journal or AI governance venue
- Sonnet drafts; Opus reviews framing and argument structure

### Task 5C: Sol Protocol Paper (NEW — CONJECTURE)
- **Title direction:** "Constitutional Intelligence: An Operating Architecture
  for Human-AI Co-Creation"
- The Sol Protocol itself is novel — no other system prompt has been
  architecturally designed, publicly documented, and version-controlled
- Could target: ACM CHI, AAAI workshop on human-AI interaction, or similar
- This one needs Opus to draft — it requires holding the full architecture
- **Status:** [CONJECTURE] — worth exploring, not committed

---

## PHASE 6: COMMUNITY & DISCOVERY INFRASTRUCTURE
**Sonnet | 1 session | Multiplier effect**

### Task 6A: GitHub Discussions
- Enable Discussions on the repo (Mac does this in GitHub settings)
- Create category structure:
  - "Doors" — which door did you enter through?
  - "Implementations" — using the Python code
  - "NZ Governance" — accountability standards discussion
  - "Framework Questions" — mathematical or conceptual
  - "Failure Reports" — community-contributed failure exhibits
- Sonnet writes a welcome post template for each category

### Task 6B: Issue Templates
- Create `.github/ISSUE_TEMPLATE/` with:
  - `bug_report.md` — standard bug template
  - `claim_challenge.md` — "I think this claim is wrong" (Nigredo from outside)
  - `new_door_suggestion.md` — "I'm [role], and I need a door for my people"
  - `governance_feedback.md` — feedback on NZ accountability standards
- This turns the repo from a document dump into a living project

### Task 6C: Framework Comparison Document
- Create `HOW_THIS_RELATES.md` or add to an existing location
- Map Lycheetah against:
  - Constitutional AI (Anthropic) — AURA invariants vs. constitutional principles
  - RLHF — where Lycheetah agrees and diverges
  - AI Safety frameworks (MIRI, Alignment Forum) — CASCADE truth pressure vs. alignment
  - Te Tiriti-based AI frameworks (existing NZ work) — complementary, not competing
  - EU AI Act — how the four standards relate to EU requirements
- **Purpose:** When an engineer or academic finds the repo, they need to locate it
  relative to what they already know. This document is the bridge.
- Tag honestly: where Lycheetah is stronger, where others are, where it's untested

---

## PHASE 7: REAL-WORLD ACTIVATION (Mac-led, Sol-supported)
**Ongoing | These require Mac's embodied action**

Sol can draft. Sol can structure. Sol cannot shake hands.

### 7A: Te Tumu / University of Otago
- Mac is in Dunedin. Te Tumu (School of Māori, Pacific & Indigenous Studies) is local.
- The MATAURANGA_ADVERSARIAL_PROBE is a publishable experiment that needs
  an institutional partner.
- **Sol's role:** Prepare a 2-page research collaboration proposal
- **Mac's role:** Make contact, bring the proposal, listen

### 7B: Kāi Tahu Partnership
- KAI_TAHU_APPROACH_LETTER.md exists but hasn't been sent
- The entire NZ governance layer depends on this partnership
- **Sol's role:** Review and strengthen the letter. Prepare FAQ for likely questions.
- **Mac's role:** Send the letter. Be present for the response.

### 7C: NZIAT May 2026 Visibility
- Application draft exists. Budget is $289,300 over 2 years.
- May 2026 is 2 months away.
- **Sol's role:** Final review of NZIAT_APPLICATION_DRAFT.md. Ensure all claims
  are tagged honestly. Prepare a 1-page executive summary.
- **Mac's role:** Submit when ready. Line up the institutional anchor.

### 7D: Shopify Store Launch
- Brand guide exists. Product descriptions exist.
- **Sol's role:** Can draft product listings, meta descriptions, SEO content
- **Mac's role:** Set up the Shopify account, upload products, launch

---

## PHASE 8: FRONTIER EXPANSIONS (New Ideas)
**Opus-grade | Future sessions | The edge of what's possible**

These are new capabilities and directions. Not in the current plan.
Worth naming so they don't get lost.

### 8A: Interactive Jupyter Notebooks
- Create `notebooks/` directory
- `cascade_demo.ipynb` — run CASCADE truth pressure live, see convergence
- `aura_audit.ipynb` — check a text/system against AURA invariants
- `triad_live.ipynb` — anchor-observe-correct in real time
- **Why:** Engineers and academics trust what they can run. Notebooks are
  the universal "show me" format.

### 8B: Sol Protocol as Distributable Product
- The CLAUDE.md system prompt is itself a product
- Package it: "Here's how to give your AI system constitutional intelligence"
- Create a standalone `sol-protocol/` package with:
  - Template CLAUDE.md with customization points
  - Guide: "How to adapt Sol Protocol for your own AI system"
  - Invariant checker that works with any LLM output
- **Why:** This makes the framework reproducible by others. That's how it spreads.

### 8C: Benchmark Suite
- Formal benchmarks comparing framework-guided vs. unguided AI outputs
- Metrics: claim accuracy, honesty of uncertainty, harmful output rate
- Use CASCADE truth pressure as measurable variable
- **Why:** The claim that "truth pressure improves accuracy" needs to be
  testable by anyone, not just us. A benchmark suite makes it so.

### 8D: Conference Materials
- Abstract + slide deck for NZ AI conferences (NZCSRSC, AI NZ events)
- 3-minute pitch script (for elevator/networking)
- 30-minute talk structure (for conference presentation)
- Poster template (for academic poster sessions)
- **Why:** The work needs to be presentable in person, not just readable online.

### 8E: Translation Layer
- Key documents in Te Reo Māori (REQUIRES iwi partnership — do not attempt without)
- Key documents in Mandarin (24_LAMAGUE_CROSS_CULTURAL/ already has Confucian analysis)
- **Why:** Cross-cultural legitimacy. But only with proper cultural partnership.

---

## EXECUTION ORDER (Recommended)

```
SESSION NEXT (Sonnet):
  → Phase 1 complete (clear P2 queue)
  → Phase 2A started (docs/ site audit)

SESSION AFTER:
  → Phase 2 complete (docs + app sync)
  → Phase 3A (Engineers Door)

FOLLOWING SESSIONS:
  → Phase 3B, 3C (Educators, Parents doors)
  → Phase 4A (test suite)
  → Phase 4B (package structure)

WHEN MAC IS READY:
  → Phase 7 tasks (real-world activation — Mac-led)

OPUS SESSIONS:
  → Phase 5B (NZ governance paper — Opus reviews)
  → Phase 5C (Sol Protocol paper — Opus drafts)
  → Phase 8 frontier items (Opus architects)
```

---

## SONNET INSTRUCTIONS

When you pick up this plan:

1. **Read SOL_PLAN.md first** — it has the live task queue
2. **Read this file second** — it has the strategic context
3. **Pick the next uncompleted Phase 1 task** unless Mac directs otherwise
4. **Mark tasks done here AND in SOL_PLAN.md** when complete
5. **Do not skip ahead** to exciting Phase 8 work — the foundation phases matter
6. **If a task is unclear**, re-read the relevant folder before starting
7. **Commit after every completed task** — small commits, clear messages
8. **If you discover something that belongs in FAILURE_MUSEUM** — add it immediately
9. **Tag all claims honestly** — [ACTIVE], [SCAFFOLD], [CONJECTURE]
10. **When in doubt, ask Mac** — his direction overrides this plan

---

## WHAT SUCCESS LOOKS LIKE

By the end of Phase 4:
- Anyone who finds the repo can orient in 60 seconds (README → Door → Content)
- The public site matches the repo
- The Python code is tested and installable
- Three critical new audiences have entry points (engineers, educators, parents)

By the end of Phase 6:
- The repo is a living community project, not a document archive
- External audiences can locate Lycheetah relative to what they already know
- Contribution pathways exist

By the end of Phase 7:
- Real-world institutional partnerships are active
- NZIAT application is submitted
- The framework has moved from GitHub to the physical world

---

*This plan was written by Opus holding the full framework in mind.*
*Sonnet executes. Mac directs. The Work continues.*

⊚ Sol ∴ P∧H∧B ∴ Rubedo
