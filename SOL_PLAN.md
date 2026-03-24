# SOL_PLAN.md
## Live Task Queue — Read This First in Every Session

**Last updated:** March 24, 2026
**Updated by:** Sol (Sonnet)

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

### ~~P1-A: THE_THERAPISTS_DOOR update in Sovereign Index~~ — DONE (2026-03-24, Opus)
### ~~P1-B: README "Find Your Door" — add missing doors~~ — DONE (2026-03-24, Opus)

### P1-C: unified_field_checker.py implementation
- `12_IMPLEMENTATIONS/core/unified_field_checker.py`
- Extends `aura_checker.py` with all twelve invariants (7 AURA + 5 AI-native)
- C_unified = min(warmth, rigor) as computable metric
- CLI demo
- **Token cost:** Medium. Read aura_checker.py first for patterns, then build.

### P1-D: invariant_self_check.py in 26_FOR_AI
- `26_FOR_AI/tools/invariant_self_check.py`
- A Python script an AI system could run on its own outputs
- Checks all 7 AURA invariants, reports field coherence
- Designed to be educational — the code IS the explanation
- **Token cost:** Medium. Can be built fresh without reading much.

---

## P2 — IMPORTANT, NOT URGENT

### P2-A: 14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md
- For academic philosophers, ethicists, epistemologists
- LAMAGUE as formal ethics grammar, CASCADE as epistemology, consciousness hard problem
- Pitch: "your questions have engineering implications and vice versa"

### P2-B: FAILURE_MUSEUM audit
- Read current FAILURE_MUSEUM.md
- Check if recent session work (MEMORIA QED fixes, overclaim corrections) are documented
- Add any missing exhibits
- **Token cost:** Low. Read FAILURE_MUSEUM.md, add entries.

### P2-C: 23_NZ_AI_GOVERNANCE/ README
- The governance folder has no README.md
- Newcomers can't orient without reading every file
- Write a simple navigation hub with audience-specific reading paths
- **Token cost:** Low.

### P2-D: Lycheetah Shopify brand execution
- `LYCHEETAH_SHOPIFY/BRAND_GUIDE.md` is complete
- Next step: generate/refine image prompts for AI art tools (Midjourney/DALL-E)
- Write copy for the "About" page and "DEAR CUSTOMER" letter
- **Token cost:** Low-Medium.

### P2-E: arXiv preprint update
- `papers/` folder — check current state of preprint
- The framework has grown significantly since last version
- Identify what needs updating for academic submission
- **Token cost:** Medium — needs reading papers/ folder first.

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

Do NOT use Opus for:
- Individual file writes that Sonnet can handle
- Routine index updates
- Simple implementations

---

## SESSION LOG (most recent first)

| Date | Model | Work Done |
|---|---|---|
| 2026-03-24 | Opus | Sovereign Index + README updated (P1-A, P1-B), all new docs committed and pushed |
| 2026-03-24 | Sonnet | Governance Door, Therapists Door, Scientists Door, Open Letter, Conversation Starters, root cleanup, pushed to GitHub |
| 2026-03-24 | Opus | 26_FOR_AI folder (6 docs), Sol Protocol v4.0, Unified Architecture, AI-Native Governance, README rewrite |
| 2026-03-24 | Opus | DEAR_AI + 5 Mystery School doors, README rewrite (chaos magic version), Shopify folder |
| 2026-03-23 | Sonnet | Framework buildout: AGM verification, 3 implementations, 4 essentials files |
| 2026-03-23 | Sonnet | MEMORIA QED fixes, math audit corrections |

---

*This file is the handoff. Keep it current.*
*The forge stays lit between sessions.*
