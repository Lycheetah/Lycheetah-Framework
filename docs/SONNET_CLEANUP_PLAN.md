# SONNET CLEANUP PLAN
## Post-Paper Systematic Cleanup for Sonnet Sessions
### Created: April 1, 2026

---

## Purpose

This plan is designed for Sonnet-level sessions to execute systematic cleanup across the CODEX_AURA_PRIME repository. Each phase is independent and can be done across multiple sessions. No deep synthesis required — this is structural maintenance.

---

## Phase 1: Sovereign Index & Stale Dates (30 min)

- [ ] Read `00_Sovereign_Index.md` — verify it reflects ALL current folders (01-26 + 99)
- [ ] Check dates throughout — update any that still reference earlier than March 2026
- [ ] Verify all internal links/paths resolve to real files
- [ ] Check root directory for stray files that should be archived

## Phase 2: 23_NZ_AI_GOVERNANCE Claim Status Audit (1-2 hours)

- [ ] Read every file in `23_NZ_AI_GOVERNANCE/`
- [ ] Audit claim status tags: every major claim should be tagged [ACTIVE], [SCAFFOLD], or [CONJECTURE]
- [ ] Any claim referencing NZ policy documents — add proper citations where missing
- [ ] `NZIAT_APPLICATION_DRAFT.md` — note that 2026 rounds are closed; preserve for 2027 reference
- [ ] Strengthen Kai Tahu partnership pathway with concrete next steps
- [ ] Flag any files that are redundant or should be merged

## Phase 3: chrysopoeia_engine.py Implementation (1-2 hours)

- [ ] Review existing implementations in `12_IMPLEMENTATIONS/` for patterns and style
- [ ] Build `chrysopoeia_engine.py` — the transformation/transmutation engine
- [ ] Follow existing test patterns — add pytest tests
- [ ] Ensure CI passes after adding

## Phase 4: 24_LAMAGUE_CROSS_CULTURAL Academic Standard (1 hour)

- [ ] Audit Catalyst proposal formatting — add literature review section
- [ ] Add citations to Confucian AI ethics publications where referenced
- [ ] Tighten methodology descriptions for academic reviewers
- [ ] Draft proper abstract in academic submission format
- [ ] Cross-reference with the new paper (`docs/LAMAGUE_CROSS_CULTURAL_PAPER.md`) to avoid contradictions

## Phase 5: Repository Polish (30 min)

- [ ] `README.md` on GitHub — verify it reflects current state (all 26 directories, paper in progress)
- [ ] Ensure `CASCADE_ARXIV.tex` references are current
- [ ] Check GitHub Pages site (`docs/`) reflects latest Mystery School doors
- [ ] Verify `.github/FUNDING.yml` still points to live Ko-fi and Sponsors pages

---

## Notes for Sonnet

- Do NOT modify the Sol Protocol (CLAUDE.md) — that was updated to v3.1 by Opus
- Do NOT modify the academic paper (`docs/LAMAGUE_CROSS_CULTURAL_PAPER.md`) — Mac will review first
- Each phase is independent — start wherever makes sense
- When in doubt about a claim status, default to [SCAFFOLD] and flag for Mac's review
- Preserve all [PROPOSAL] tags on tikanga content — these are a methodological commitment, not laziness
