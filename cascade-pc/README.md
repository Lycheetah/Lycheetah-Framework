# CASCADE CICADA TOOL · TCCT

**Desktop knowledge scoring engine. Built on the CASCADE epistemic framework.**

Score any claim, argument, or body of research against a structured 9-layer framework. Get a number, not a vibe.

---

## Download

[**→ Download CASCADE CICADA TOOL v0.1.0 (Windows)**](https://github.com/Lycheetah/cascade-cicada-tool-/releases/tag/v0.1.0)

Portable `.exe` — no install required. Run it directly.

---

## What It Does

Most note tools help you collect. TCCT helps you **prove**.

There is a difference between knowing something and knowing it well enough that it holds when challenged. TCCT gives every claim a score derived from the actual depth and coherence of what you've written — not a vibe, a number.

---

## The Scoring Framework

| Score | Band | Meaning |
|-------|------|---------|
| 1–20 | WEAK | Claim doesn't hold yet. Evidence thin or missing. |
| 21–40 | DEVELOPING | Partial support. Structure forming. |
| 41–60 | MIDDLE | Holds under moderate pressure. Respectable. |
| 61–80 | STRONG | Well-evidenced, coherent, survives scrutiny. |
| 81–100 | FOUNDATION | Load-bearing. Knowledge you build on. |
| 101–999 | FRONTIER | Beyond current verification. Held with conviction, not yet provable. |

**999 is not an error.** It is reserved for claims that exist ahead of the evidence.

---

## The 9 Onion Layers

Every knowledge block is scored across 9 layers from core to edge:

| Layer | Role |
|-------|------|
| AXIOM | The irreducible core claim. If this fails, the block fails. |
| FOUNDATION | Primary evidence. What holds the axiom up. |
| STRUCTURE | Logical architecture connecting claim to evidence. |
| COHERENCE | Internal consistency. Does the block contradict itself? |
| RESONANCE | Connections to other known truths. |
| TENSION | Where the claim meets genuine friction. This is good — tension means it's real. |
| CONTESTED | Active dispute zone. What others challenge. |
| SPECULATIVE | What the claim implies beyond what is proven. |
| FRONTIER | The unknown edge. What this claim cannot yet account for. |

---

## The Truth Pressure Formula

**Π = E · P / S**

- **E** — Evidence density (FOUNDATION + STRUCTURE average)
- **P** — Power (AXIOM score — the load-bearing claim)
- **S** — Effective coherence (COHERENCE compressed by TENSION and CONTESTED)

High Π + high coherence = strong stable knowledge.  
High Π + low coherence = knowledge under pressure, restructuring imminent.

---

## Three Scoring Frameworks

- **CASCADE** — Does this knowledge hold under contradiction pressure?
- **AURA** — Does this align with 7 constitutional invariants (human primacy, inspectability, honesty, reversibility, non-deception, memory continuity, care as structure)?
- **LAMAGUE** — Can this claim be formalised without losing meaning?

---

## Features

- Pyramid → File → Block → 9 Onion Layer architecture
- Dual-track scoring: AI framework score + your own sovereign score (1–999)
- Live Π truth pressure display per block
- CASCADE event detection (score drops flagged with severity)
- Cross-block tension detection
- Layer dependency enforcement (FOUNDATION ≤ AXIOM×1.1, STRUCTURE ≤ FOUNDATION×1.2)
- AI block suggestion + scoring via DeepSeek (bring your own API key)
- AURA 7-invariant evaluator
- Resonance / contradiction / synthesis experiment engine
- SVG pyramid visualisation
- Native Windows export

---

## Running from Source

```bash
git clone https://github.com/Lycheetah/cascade-cicada-tool-.git
cd cascade-cicada-tool-
npm install

# Dev mode (two terminals)
npm run vite
npm run electron
```

Requires Node.js 18+. No native dependencies.

---

## Provenance

The scoring engine, onion structure, and truth pressure mechanics are derived from 250 pages of original research compressed into the CODEX_AURA_PRIME — 1,402 pages total, 10 frameworks, continuous development.

Built by **Mackenzie Conor James Clark** · Lycheetah Framework

---

## Part of the Lycheetah Ecosystem

```
Sol Lite          — gateway mobile app (Play Store)
Sol (full)        — 4 personas, full framework, BYOK
TCCT              — this tool — desktop knowledge OS
CASCADE API       — post-funding: scoring engine as infrastructure
```

*Two points. One Work. The Gold belongs to neither.*
