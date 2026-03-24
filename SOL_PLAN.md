# SOL_PLAN.md
## Live Task Queue — Read This First in Every Session

**Last updated:** March 25, 2026 (session 2)
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

## P0 — IMMEDIATE

*Nothing currently blocking. All clear.*

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

### ~~P1-G: pyproject.toml + GitHub Actions CI~~
- Make framework pip-installable: `pip install -e .`
- CI pipeline: `.github/workflows/test.yml` — runs pytest on every push
- Green badge on README: "tests passing"
- See OPUS_PLAN Phase 4B/4C
- **Token cost:** Low-Medium.

### P1-H: demo.py — Live Framework Showpiece
- Single runnable file at repo root
- Shows CASCADE paradigm shift, AURA check, TRIAD convergence, φ-Zone comparison
- Target: 30 seconds to run, beautiful terminal output, anyone understands immediately
- **Token cost:** Medium.

### P1-I: THE_φ_ZONE_DOOR.md — Mystery School entry for complexity/math/optimization
- φ-Zone Hypothesis: golden ratio in optimal AI behavior
- phi_bandit.py results: t=70.29, p<0.001 for chaotic environments
- Connections to HARMONIA (Kuramoto coupling, φ resonance)
- Entry for: mathematicians, complexity scientists, optimization researchers, physicists
- **Token cost:** Medium.

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
- Museum current through March 25, 2026. 12 exhibits total.

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
| 2026-03-25 | Sonnet | P1-E: docs/ overhaul — Twelve Doors, φ-Zone door, 80-test status, demo.py on index.html |
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
