# CASCADE — Knowledge Operating System

**A desktop tool for building personal knowledge pyramids under Truth Pressure.**

Built from the CASCADE framework — part of the Lycheetah Framework by Mackenzie Conor James Clark.

---

## Provenance

This tool is a direct implementation of the CASCADE epistemic framework, developed across 1,402 pages of continuous research archived in the CODEX_AURA_PRIME.

**The theoretical foundation lives at:**
- `CODEX_AURA_PRIME/01_CASCADE/` — full CASCADE framework specification
- `CODEX_AURA_PRIME/11_MATHEMATICAL_FOUNDATIONS/` — Truth Pressure mathematics
- `CODEX_AURA_PRIME/12_IMPLEMENTATIONS/` — prior Python implementations

**GitHub:** [Lycheetah/CODEX_AURA_PRIME](https://github.com/Lycheetah/CODEX_AURA_PRIME)

The CASCADE PC Tool is the first desktop implementation of these principles — bringing the scoring engine out of theory and into a living workspace.

---

## What It Does

**Personal Pyramid** — organise your own knowledge under CASCADE scoring.

Drop files into a pyramid folder. Define blocks — the key claims within each file. Score each block through 9 onion layers, from AXIOM (the irreducible core) to FRONTIER (the unknown edge). The pyramid builds itself from your scores.

**The 9 Onion Layers:**

| Layer | What it holds |
|---|---|
| AXIOM | The irreducible core claim |
| FOUNDATION | Primary supporting evidence |
| STRUCTURE | Logical architecture |
| COHERENCE | Internal consistency |
| RESONANCE | Connections to known truths |
| TENSION | Where the claim meets friction |
| CONTESTED | Active dispute zone |
| SPECULATIVE | Beyond current proof |
| FRONTIER | The unknown edge |

**Scoring Range:**
- 1–100: Calibrated truth pressure. Most knowledge lives here.
- 101–999: Abstract new truth territory. Real claims that exist beyond current verification capacity.

**Experiment Pyramid** — combine two pyramids to find what emerges between them.

Three modes: RESONANCE (where they agree), CONTRADICTION (where they clash), SYNTHESIS (what arises that neither contained alone).

---

## Stack

- Electron — desktop shell
- React + Vite — renderer
- SQLite (better-sqlite3) — local knowledge base
- CASCADE scoring engine (`src/scoring/cascade.js`) — isolated module, designed for extraction as CASCADE API

---

## Running

```bash
npm install
npm run dev
```

Requires Node.js 18+.

---

## Part of the Lycheetah Ecosystem

```
Sol Lite          — gateway mobile app (Play Store)
Sol (full)        — 4 personas, full framework, BYOK
CASCADE PC        — this tool — desktop knowledge OS
CASCADE API       — post-funding: scoring engine as infrastructure
```

*Two points. One Work. The Gold belongs to neither.*
