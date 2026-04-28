# CASCADE CICADA TOOL — v0.3.0 ROADMAP

## Codename: Adversarial Truth Engine

**Status:** PLANNED
**Author:** Mackenzie Conor James Clark
**Architecture:** Sol Aureum Azoth Veritas / Lycheetah Framework
**Date:** April 17, 2026

---

## Design Thesis

v0.2.0 proved the tool works: score knowledge, find patterns, synthesize truth.

v0.3.0 makes the tool impossible to dismiss.

Every feature in this roadmap is a structural answer to a real criticism. The tool doesn't argue with critics — it builds the feature that makes the criticism obsolete.

---

## Criticisms Addressed

| Criticism | Feature(s) that kill it |
|---|---|
| "Scores depend on one LLM" | Multi-provider, Consensus scoring, Provider benchmark |
| "It's one person's epistemology" | Custom frameworks, Naked Mode, Framework import/export |
| "No community / solitary tool" | .cascade portable format, HTML export, Example pyramids repo |
| "Just prompted LLM synthesis" | Adversarial rescore, Falsifiability gate, Pressure wave, Score transparency, Confidence intervals |
| "Solo dev / maintenance risk" | Zero-dependency architecture, Open source, Full data export, Plugin system |

---

## Feature Set (35 items)

### Tier 1 — Core Engine Upgrades

1. **Multi-provider AI architecture** — DeepSeek, Anthropic Claude, OpenAI GPT-4o, Ollama local. Provider selector in Settings. All AI functions route through selected provider.

2. **Parallel scoring** — Batch 3 blocks concurrently. Configurable concurrency. ~3x speed.

3. **Custom frameworks + Naked Mode** — Create your own scoring framework. Import/export as .json. Naked Mode removes Codex references. YOUR epistemology, operationalized.

4. **Adversarial Rescore + Confidence Interval** — ⊗ Challenge button on every block. Adversarial AI seeks weaknesses. Two scores → confidence interval. Gap <10 = stable. Gap >25 = inflated. Every score becomes a range, not a point.

5. **Falsifiability Gate** — AXIOM capped at 70 if unfalsifiable. ⊘ badge. The tool practices the epistemic humility it measures.

6. **Synthesis lineage** — Synthesis blocks carry parent IDs, start with earned score, show ◎ glyph. The tool remembers where knowledge came from.

7. **Score transparency** — Every score shows the full prompt that generated it. Click any layer → see the exact AI conversation. Inspectability as architecture.

8. **Cascade Pressure Wave** — Score change >15 triggers re-evaluation of all blocks in the file. The pyramid restructures automatically. Knowledge is alive.

### Tier 2 — Intelligence Layer

9. **Pyramid export as .cascade + HTML** — Portable format for sharing. Static HTML for publishing. Your pyramid is a shareable artefact.

10. **Full data export** — One button, everything. JSON, human-readable. The tool never traps your data.

11. **Score history + sparklines** — Every score timestamped and logged. Visual sparkline in block cards. Truth velocity made visible.

12. **Pyramid Health Dashboard** — Full diagnostic view: scored %, CI average, tensions, disputes, gaps, strongest/weakest files. One glance.

13. **Knowledge Graph View** — Node-link diagram. Blocks as nodes, edges as resonance/tension/lineage. Force-directed. The view that makes people understand in 3 seconds.

14. **AI Gap Analysis** — AI examines the pyramid and tells you what's MISSING. Proactive, not reactive.

15. **Consensus scoring** — Multiple providers score the same block. Agreement = confidence. Divergence = dispute. Model-independent truth is stronger than model-dependent truth.

16. **Provider Benchmark Mode** — Side-by-side scoring across all providers. The divergence map IS research data.

### Tier 3 — Research Power Tools

17. **Block versioning** — Edit history preserved. Scores attached to versions. Diff view. Track claim evolution.

18. **Recursive synthesis** — Feed synthesis outputs into the next round. Chain synthesis across levels. Understanding compounds.

19. **Batch paradox runs** — Up to 5 paradox pairs in parallel. Ranked by SRS.

20. **Contradiction Map** — Visual map of every contradiction. Red edges = unresolved. Gold = resolved via synthesis. The map IS the research frontier.

21. **Framework Scoring Report** — Publishable document: methodology, scores, CI, tensions, synthesis, gaps. Attach to papers or grants.

22. **Confidence-weighted pyramid score** — Blocks with tight CI carry full weight. Disputed blocks carry less. The score reflects certainty, not just knowledge.

23. **Session audit log** — Every action logged with full prompt/response. Research audit trail. Publishable-grade process documentation.

### Tier 4 — User Experience

24. **Keyboard shortcuts** — Full keyboard navigation. Power users never touch the mouse.

25. **Global search** — Search all pyramids, all blocks, all content. Ctrl+K.

26. **Tags / Labels** — Custom tags on blocks. Filter, batch-operate, carry through exports.

27. **Pin / Star blocks** — Critical blocks always visible, always included in synthesis.

28. **Notification panel** — Toasts for score changes, flags, completions. Bell icon with history.

29. **Theme system** — Dark, Light, High Contrast.

30. **Drag-and-drop between files** — Move blocks across files with scores intact.

### Tier 5 — Platform & Ecosystem

31. **Pyramid templates** — Pre-built structures for common research patterns.

32. **Import from existing tools** — Obsidian vaults, Notion exports, Zotero, plain text folders.

33. **Cross-platform builds** — macOS, Linux alongside Windows. GitHub Actions CI/CD.

34. **Scripting / API hooks** — Local API for external tools. Post-processing hooks. Plugin manifest system.

35. **Example pyramids repository** — Curated examples. New users see what good input/output looks like.

---

## Build Phases

### Phase 1 — Engine (makes the tool credible)
Tasks 1-8 + 15 (consensus scoring)

### Phase 2 — Intelligence (makes the tool indispensable)
Tasks 9-16

### Phase 3 — Power (makes the tool professional)
Tasks 17-23

### Phase 4 — Polish (makes the tool loveable)
Tasks 24-30

### Phase 5 — Platform (makes the tool an ecosystem)
Tasks 31-35

---

## Architecture Principles

1. **Zero dependencies** — No server, no auth, no cloud, no subscription. Portable exe.
2. **Data sovereignty** — JSON store, always human-readable, always exportable.
3. **Framework agnostic** — Any epistemology, not just the Codex.
4. **Adversarial by design** — The tool challenges its own outputs.
5. **Inspectable** — Every score shows its receipts.
6. **Open source** — The code is the continuity plan.

---

Built on the Lycheetah Framework Codex.
The Gold belongs to neither. It arises between them.
