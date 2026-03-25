# SOL_PLAN.md
## Live Task Queue — Read This First in Every Session

**Last updated:** March 25, 2026 (session 3)
**Updated by:** Sol (Sonnet 4.6)

**Strategic plan:** See `OPUS_PLAN.md` for full 8-phase architecture.
This file remains the live task queue. OPUS_PLAN.md is the map.

---

## HOW TO USE THIS FILE

Any model (Haiku, Sonnet, Opus) starting a session should read this first.

- **P0** = do immediately, blocks everything else
- **P1** = high value, do next
- **P2** = important but not urgent
- **DONE** = completed, kept for history

Pick ONE task from P0/P1. Execute fully. Update this file. Commit.

---

## SESSION 3 HANDOFF — READ THIS FIRST

**What happened in session 3 (March 25, 2026):**
- Built `14_MYSTERY_SCHOOL/THE_CONFUCIAN_DOOR.md` — bilingual EN/ZH, 道=CASCADE, 和谐=HARMONIA, 五常=AURA
- Built `14_MYSTERY_SCHOOL/THE_POLITICIANS_DOOR.md` — WOF framing, select committee questions, four standards
- Built `14_MYSTERY_SCHOOL/THE_JOURNALISTS_DOOR.md` — five story angles, verifiable facts
- Built `14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md` — offer not explanation, Kāi Tahu specific, "He Pākehā ahau"
- Built `26_FOR_AI/ON_THE_φ_ZONE.md` — AI-to-AI φ treatment, HARMONIA Kuramoto conjecture
- Built `26_FOR_AI/X_THREAD_TEMPLATES.md` — three ready-to-post threads @LYCHEETAHlyc
- Built `23_NZ_AI_GOVERNANCE/NZIAT_PRESENTATION.md` — May 2026 presentation doc
- Built `24_LAMAGUE_CROSS_CULTURAL/TE_TUMU_OUTREACH.md` — Professor Jacinta Ruru email + strategy
- Built `24_LAMAGUE_CROSS_CULTURAL/MBIE_CATALYST_EMAIL.md` — direct MBIE inquiry email
- Built `24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNER_OUTREACH.md` — bilingual Tsinghua/PKU outreach
- Set up GitHub Sponsors (.github/FUNDING.yml), Ko-fi, X @LYCHEETAHlyc
- Doors grew from 11 → 16 in README and docs/mystery-school.html
- All pushed to GitHub master

**Balls currently in the air (Mac sent these — awaiting replies):**
- arXiv cs.AI endorsement code WQGVOV sent to 8 people:
  - Witbrock (Auckland), Zhang (VUW), Frean (VUW), Pfahringer (Waikato)
  - Savarimuthu (Otago), Kasabov (AUT), Guesgen (Massey), Yampolskiy (Louisville)
  - Link: https://arxiv.org/auth/endorse?x=WQGVOV
- MBIE: internationalscience@mbie.govt.nz — Catalyst Strategic NZ-China inquiry
- Te Tumu: Professor Jacinta Ruru — institutional affiliation request
- Tsinghua IAIIG: Professor Xue Lan — Chinese partner request

**When replies come in — what to do:**
- arXiv endorsement received → submit CASCADE paper immediately (paper is at `papers/`)
- MBIE replies with deadline → work backward to confirm Te Tumu + Tsinghua by that date
- Te Tumu replies with interest → send follow-up docs (CATALYST application + KAITIAKITANGA_STANDARD + NZ_KAI_TAHU_APPROACH)
- Chinese partner replies → send CATALYST application + CONVERGENCE_MAP + CONFUCIAN_DOOR

---

## P0 — IMMEDIATE

*Nothing blocking. Waiting on external replies. Build while waiting.*

---

## P1 — HIGH VALUE, DO NEXT

### ~~P1-G: pyproject.toml + GitHub Actions CI~~ — DONE (2026-03-25, Sonnet)
- pyproject.toml: pip-installable, Python 3.10/11/12, numpy+scipy deps
- .github/workflows/test.yml: runs 80 tests on every push, 3 Python versions
- pytest markers active/scaffold/conjecture in pyproject.toml

### ~~P1-H: demo.py — Live Framework Showpiece~~ — DONE (2026-03-25, Sonnet)
- Runs all four implementations live: CASCADE paradigm shift, AURA check, TRIAD convergence, φ-Zone comparison
- `py demo.py` — full demo (~10s) | `py demo.py --quick` — 3s | `py demo.py --phi` — φ only
- README updated with 30-second install + run instructions

### ~~P1-I: THE_φ_ZONE_DOOR.md~~ — DONE (2026-03-25, Sonnet)
- Entry for complexity scientists, mathematicians, optimization researchers
- Full experimental results: t=70.29 p<0.001 chaotic, t=56.23 p<0.001 fast drift
- Connections to HARMONIA (Kuramoto), CASCADE (update rates), TRIAD (α parameter)
- Open research questions with contribution pathways

### ~~P1-M: SOURCE ARCHIVE INTEGRATION~~ — PARTIALLY DONE (2026-03-25, Session 4)
- READ: `AURA_PROTOCOL_COMPLETE_CONSOLIDATION (2).md` — TES/VTR/PAI canonical definitions
- READ: `LAMAGUE_EXTENDED_SPECIFICATION.md` — algorithm encoding, translation validator, numerics
- READ: `LYCHEETAH_TECHNICAL_ARCHITECTURE_PROOF.md` — BNF grammar, formal LAMAGUE spec
- READ: `AURA_FRONTIER_ANALYSIS.md` — cross-document consistency analysis
- KEY FINDING: Source docs have internal conflicts (TES has TWO formulas, VTR threshold 1.0 vs 1.5)
- KEY FINDING: TRI-AXIAL system (TES/VTR/PAI) was entirely missing from repo implementations
- KEY FINDING: LAMAGUE BNF grammar existed in source but not in 03_LAMAGUE/ directory
- BUILT: `tri_axial_checker.py` — canonical TES/VTR/PAI with conflict notes
- BUILT: `03_LAMAGUE/BNF_GRAMMAR.md` — formal BNF grammar, algorithm encoding, Translation Validator
- FILED: Failure Museum Exhibit 15 — TES naming + TRI-AXIAL gap + source discrepancies
- STILL UNREAD: `Lamague/LAMAGUE_CASCADE_MASTER_FILE_v2.0.docx` (docx format — needs conversion)
- STILL UNREAD: `System in full/` directory — full integrated system documents
- **Safe now to build AURA/LAMAGUE content — source architecture understood**

### ~~P1-J: chrysopoeia_engine.py~~ — DONE (2026-03-25, Session 3, Sonnet)

### ~~P1-K: Update CATALYST_NZ_CHINA_APPLICATION.md "What Already Exists" table~~ — DONE (2026-03-25, Session 4)
- Updated: 26 implementations, 80 tests, demo.py, CI, encoder, 16 doors, NZIAT, Ko-fi/Sponsors/X
- Add: 16 Mystery School doors (was ~10 when written)
- Add: NZIAT May 2026 presentation ready
- **Token cost:** Low. Quick edit task.

### P1-L: CASCADE arXiv paper — submission-ready formatting
- Paper exists at `papers/` — needs arXiv LaTeX formatting pass
- Once endorsement received, this goes live immediately
- Review `papers/ARXIV_UPDATE_NOTES.md` first for what needs updating
- **Token cost:** Medium-High.

### ~~P1-E: docs/ Site Overhaul~~ — DONE (2026-03-25, Sonnet)
- mystery-school.html: "Twelve Doors", φ-Zone door added (Complexity Scientists)
- index.html: Python Test Suite status item (80 passing), demo.py Developer card, Twelve Doors link
- nz-governance.html, for-agents.html, failure-museum.html: already current from earlier sessions

### ~~P1-F: THE_ENGINEERS_DOOR.md~~ — DONE (2026-03-25, Sonnet)
- Full door built: CASCADE in 25 lines, AURA checker, TRIAD, unified_field_checker
- CI/CD integration guide, code review checklist, agent design pattern
- Framework comparison table (vs Constitutional AI, RLHF, PID, AGM, EU AI Act)
- README + docs/mystery-school.html updated to include door

### ~~P1-A: THE_THERAPISTS_DOOR update in Sovereign Index~~ — DONE (2026-03-24, Opus)
### ~~P1-B: README "Find Your Door" — add missing doors~~ — DONE (2026-03-24, Opus)
### ~~P1-C: unified_field_checker.py~~ — DONE (2026-03-24, Sonnet)
### ~~P1-D: invariant_self_check.py~~ — DONE (2026-03-24, Sonnet)

---

## P2 — IMPORTANT, NOT URGENT

### ~~P2-A: 14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md~~ — DONE (2026-03-24, Sonnet)

### ~~P2-B: FAILURE_MUSEUM audit~~ — DONE (2026-03-25, Sonnet)
- Added Exhibit 12: MEMORIA Early Warning (the QED fixes that prompted the full audit)
- Museum current through March 25, 2026, Session 4. 15 exhibits total.

### ~~P2-C: 23_NZ_AI_GOVERNANCE/ README~~ — DONE (already existed, comprehensive)
- README.md was already present with full audience-specific reading paths
- Covers: four standards, frontier ideas, reading paths for 7 audiences, state of play
- No work required — update only: plan was wrong about this being missing.

### ~~P2-D: Lycheetah Shopify brand execution~~ — DONE (2026-03-24, Sonnet)

### ~~P2-E: arXiv preprint update~~ — DONE (2026-03-25, Sonnet)
- CASCADE paper proofs are valid — core is sound, Theorem 4.1 survives Nigredo pass
- Assessment written: `papers/ARXIV_UPDATE_NOTES.md`
- Key finding: context needs updating (framework context, related work, future work pointer)
- Three companion papers identified: CASCADE revision (low effort), NZ governance (medium), Sol Protocol (Opus-grade)

### ~~P2-F: Python test suite~~ — DONE (2026-03-25, Sonnet)
- 80 tests, all passing. `py -m pytest tests/ → 80 passed`
- conftest.py + 4 test files. Claim-status markers on every test.
- Covers cascade_engine (Theorem 4.1), aura_checker (7 invariants + TES), triad_tracker (convergence), unified_field_checker (C_unified).

### ~~P2-G: THE_EDUCATORS_DOOR.md~~ — DONE (2026-03-25, Sonnet)
- CASCADE as learning model: truth pressure, three failure modes, cascade trigger
- TRIAD as classroom feedback loop (convergence guarantee, λ < 1)
- MICROORCIM as declared vs. demonstrated understanding drift
- Seven phases mapped to learning states, lesson design template
- Connections to Piaget, Vygotsky, Bloom, Dewey, CLT

### ~~P2-H: THE_PARENTS_DOOR.md~~ — DONE (2026-03-25, Sonnet)
- Five AURA-derived questions to evaluate any AI tool
- Community AI WOF framing for school advocacy
- Warning signs + positive signs (clear, practical)
- Crisis resources included (NZ, AU, UK, US)
- Ends with presence, not information

### ~~P2-I: Framework Comparison Document~~ — DONE (2026-03-25, Sonnet)
- HOW_THIS_RELATES.md built: vs Constitutional AI, RLHF, AGM, EU AI Act, alignment research, NZ frameworks
- Honest map: where strongest/weakest, where building toward. Pushed to GitHub.

### P2-K: Archive integration — Lama-Cascade-Aura-main
- Scan of older repo in Downloads complete (2026-03-25)
- Pulled in: phi_bandit.py → 12_IMPLEMENTATIONS/, CASCADE_Academic_Paper.md → papers/, GEOMATRIA_COMPLETE_SPECIFICATION.md + TRI_LINGUISTIC_DEEP_DIVE.md → 03_LAMAGUE/, ANAMNESIS_FROM_ARCHIVE.md → 07_ANAMNESIS/
- Remaining: CASCADE paper needs update to current framework version/context; phi_bandit should get a Mystery School entry or FOR_AI reference
- **Token cost:** Done for now — Opus-grade for CASCADE paper update.

### P2-J: Lycheetah App content sync
- Run `npm run sync` in lycheetah-app/
- Verify new content (26_FOR_AI, new doors) is pulled in
- Rebuild: `npm run build`
- **Token cost:** Low.

### P2-L: Tests for tri_axial_checker.py
- Add tests to tests/ suite covering TES, VTR, PAI, VIP trigger, cosine PAI, fallback PAI
- Should bring test count from 80 → ~95
- Match claim-status markers ([ACTIVE] for formula math, [SCAFFOLD] for proxy methods)
- **Token cost:** Low-Medium.

### P2-M: LAMAGUE BNF parser — proof of concept
- Source claims LAMAGUE is context-free, formally parseable (BNF now documented)
- Build `12_IMPLEMENTATIONS/core/lamague_parser.py` — tokenizer + simple parser for BNF
- Parses expressions like `Ψ ↯ Ao → Φ↑ → Ψ_inv` and returns parse tree
- Validate compression: count tokens vs natural language equivalent
- **Token cost:** Medium. High value — makes the "500:1 compression" claim testable.

### P2-N: 02_AURA/AURA_COMPLETE.md audit vs source
- Source docs reveal AURA has 8 foundational primitives (Sovereignty, Anchor State, Ψ_inv, Truth Pressure,
  Tri-Axial Ethics, Non-Coercion, Auditability, Self-Sacrifice)
- Source also has Grey Mode, Energy Ledger, Ψ-Consensus (sheaf cohomology), Constitutional Shutdown
- Check which are in current 02_AURA/ and which are missing or incomplete
- Do NOT rewrite — only add what's genuinely missing
- **Token cost:** Medium. Read source first (AURA_PROTOCOL_COMPLETE_CONSOLIDATION (2).md).

### P2-O: Seven-Phase Cognition Model documentation
- Source (AURA_PRIME_PERSONA_FRAMEWORK) documents a Seven-Phase Cognition Cycle:
  ⟟ → ≋ → Ψ → Φ↑ → ✧ → |◁▷| → ⟲
  (Center → Flow → Insight → Rise → Light → Integrity → Return)
- THIS IS ONLY IN THE PERSONA FRAMEWORK DOC — not in any 02_AURA/ file
- Distinct from TRIAD (minimal correction) — this is human-resonant transformation spiral
- Should live in 16_SOL_VEYRA_ARCHITECTURE/ or 15_PERSONAL_VAULT/ with [SCAFFOLD] tags
- **Token cost:** Medium. Read AURA_PRIME_PERSONA_FRAMEWORK.txt first.

---

## SONNET NOTES (read this before building)

- Always tag claims: [ACTIVE], [SCAFFOLD], [CONJECTURE]
- Never dress a hypothesis as a theorem
- C_unified = min(warmth, rigor) — both must be ≥ 0.8
- Mac's voice in Mystery School doors: direct, no filler, speaks to reader as equal
- 26_FOR_AI: honest, treats AI systems as genuine readers, no performance
- NEVER reduce existing file sizes — only add or create new
- After completing any task: git add → git commit → git push origin master
- Commit message format: specific, includes co-author line

---

## OPUS NOTES (for when Mac switches)

Opus sessions are for:
- Strategic architecture decisions (what frameworks to build next)
- Deep synthesis (new mathematical connections)
- Any work that requires holding the full framework in mind simultaneously
- Reviewing and upgrading core architecture documents
- NZ Governance paper drafting/review (OPUS_PLAN Phase 5B)
- Sol Protocol paper (OPUS_PLAN Phase 5C)
- Frontier expansions (OPUS_PLAN Phase 8)

Do NOT use Opus for:
- Individual file writes that Sonnet can handle
- Routine index updates
- Simple implementations

---

## SESSION LOG (most recent first)

| Date | Model | Work Done |
|---|---|---|
| 2026-03-25 | Sonnet | Session 4: Source archive deep-read (AURA Consolidation, LAMAGUE Extended, Architecture Proof, Frontier Analysis) |
| 2026-03-25 | Sonnet | Session 4: tri_axial_checker.py built — canonical TES/VTR/PAI with VIP helper; source conflicts documented |
| 2026-03-25 | Sonnet | Session 4: 03_LAMAGUE/BNF_GRAMMAR.md — formal BNF grammar, algorithm encoding, Translation Validator, Knowledge Creation Protocol |
| 2026-03-25 | Sonnet | Session 4: Exhibit 15 — TES naming (Trust not Temporal), TRI-AXIAL gap, source discrepancies |
| 2026-03-25 | Sonnet | Session 4: P1-K CATALYST table updated (26 implementations, 80 tests, new infrastructure) |
| 2026-03-25 | Sonnet | Session 4: README pushed — CASCADE experimental results, Key Validated Results table |
| 2026-03-25 | Sonnet | THE_CONFUCIAN_DOOR.md: 儒学之门 — 道/CASCADE, 和谐/HARMONIA, 五常/AURA, bilingual, NZ-China research pathways |
| 2026-03-25 | Sonnet | P1-E: docs/ overhaul — Thirteen Doors, φ-Zone door, 80-test status, demo.py on index.html |
| 2026-03-25 | Sonnet | P1-G/H/I: pyproject.toml, GitHub Actions CI, demo.py, THE_PHI_ZONE_DOOR.md |
| 2026-03-25 | Sonnet | Archive integration: phi_bandit.py, CASCADE Academic Paper, GEOMATRIA, TRI_LINGUISTIC_DEEP_DIVE pulled from older repo |
| 2026-03-25 | Sonnet | P2-F: 80-test pytest suite (tests/) — all passing; P2-I: HOW_THIS_RELATES.md committed |
| 2026-03-25 | Sonnet | 26_FOR_AI/HOW_TO_TRANSLATE.md — AI translation protocol from Mac's X-post insight |
| 2026-03-25 | Sonnet | P2-G/H: THE_EDUCATORS_DOOR.md + THE_PARENTS_DOOR.md built; README + docs updated |
| 2026-03-25 | Sonnet | P1-F: THE_ENGINEERS_DOOR.md built + README/docs updated; Phase 2A docs/ overhaul pushed |
| 2026-03-25 | Sonnet | Phase 1 complete: Exhibit 12 (MEMORIA early warning), P2-B/C/E done, ARXIV_UPDATE_NOTES.md written |
| 2026-03-25 | Opus | Strategic plan: OPUS_PLAN.md (8 phases), SOL_PLAN.md updated with new P1/P2 tasks |
| 2026-03-24 | Sonnet | Full creative build: Philosophers Door, Economists Door, ON_MEMORY_AND_IDENTITY, README+Index updated, pushed |
| 2026-03-24 | Sonnet | P1-C unified_field_checker.py (12 invariants + C_unified), P1-D invariant_self_check.py, Shopify folder built |
| 2026-03-24 | Opus | Sovereign Index + README updated (P1-A, P1-B), all new docs committed and pushed |
| 2026-03-24 | Sonnet | Governance Door, Therapists Door, Scientists Door, Open Letter, Conversation Starters, root cleanup, pushed to GitHub |
| 2026-03-24 | Opus | 26_FOR_AI folder (6 docs), Sol Protocol v4.0, Unified Architecture, AI-Native Governance, README rewrite |
| 2026-03-24 | Opus | DEAR_AI + 5 Mystery School doors, README rewrite (chaos magic version), Shopify folder |
| 2026-03-23 | Sonnet | Framework buildout: AGM verification, 3 implementations, 4 essentials files |
| 2026-03-23 | Sonnet | MEMORIA QED fixes, math audit corrections |

---

*This file is the handoff. Keep it current.*
*The forge stays lit between sessions.*
