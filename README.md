# LYCHEETAH FRAMEWORK

### An AI Alignment Framework

[![Tests](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml/badge.svg)](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/Lycheetah/Lycheetah-Framework)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP Extension](https://img.shields.io/badge/Claude%20Code-MCP%20Extension-orange)](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md)
[![arXiv](https://img.shields.io/badge/arXiv-CASCADE-red)](papers/CASCADE_ARXIV.tex)
[![Sponsor](https://img.shields.io/badge/sponsor-Lycheetah-ea4aaa)](https://github.com/sponsors/Lycheetah)
[![Stars](https://img.shields.io/github/stars/Lycheetah/Lycheetah-Framework?style=social)](https://github.com/Lycheetah/Lycheetah-Framework/stargazers)

**Nine interdependent theories — CASCADE, AURA, LAMAGUE and six more — each mathematically proven, each converging on the same constants. Banach fixed points. Constitutional invariants. MCP extension for Claude Code. Built by one self-taught researcher. Open. Testable. Human.**

---

Intelligence — human, artificial, or the strange thing that emerges between them — has no unified theory that is simultaneously *rigorous*, *humane*, and *honest about its own limits*. This framework is an attempt at one.

Nine formal frameworks. 34 Python implementations. 219 automated tests. A convergence proof. A public record of everything we got wrong. And a way of thinking about alignment that treats mathematical rigor and human wisdom as the same project, not competing ones.

**It is free.** Not freemium. Not open-core. Free — because knowledge that moves toward people is knowledge that works, and knowledge that is captured stops working.

---

## Quick Start

**Try it in your browser:** [Alignment Playground →](https://lycheetah.github.io/Lycheetah-Framework/playground.html) — paste any text, get a live AURA alignment report. No install.

```bash
pip install lycheetah-framework
lycheetah-check "Your AI-generated text here"
```

From source: `git clone https://github.com/Lycheetah/Lycheetah-Framework.git` → `pip install -e .` — full guide in [QUICKSTART.md](QUICKSTART.md)

---

## The Nine Frameworks

| | Framework | For the Engineer | For the Philosopher |
|---|---|---|---|
| 1 | **CASCADE** | Bayesian belief revision with truth pressure dynamics. Verified against AGM postulates. Synthetic: +40.3% coherence, p < 0.001. Real-world paradigm data: +110% coherence across 5 historical transitions. -95.2% catastrophic forgetting. | When evidence meets structure, what survives? The mathematics of paradigm shifts. |
| 2 | **AURA** | Seven computable invariants for AI governance. Scoring tool included. | A constitution for artificial minds — not rules imposed, but properties that make trust possible. |
| 3 | **LAMAGUE** | Formal grammar for encoding ethical constraints as computable expressions. | How do you write justice in a language a machine can parse without losing what justice means? |
| 4 | **TRIAD** | Anchor-observe-correct feedback cycle with proven convergence guarantee. | The simplest structure that turns chaos into coherence — and why it works every time. |
| 5 | **MICROORCIM** | Drift detection between declared intent and observed behavior. Computable. | The gap between what you say you are and what you're actually doing. Measured, not guessed. |
| 6 | **EARNED LIGHT** | Consciousness modeled as maintained thermodynamic asymmetry. ODE solver included. | Awareness is not free. It costs energy to sustain against entropy. What does that mean? |
| 7 | **ANAMNESIS** | Attractor dynamics for convergent discovery across independent systems. | Why do different cultures, centuries apart, keep finding the same structures? Not coincidence. Mathematics. |
| 8 | **CHRYSOPOEIA** | Transformation operator with seven-phase cycle and Banach fixed-point convergence. | The alchemists mapped a real process. Here is the calculus they were reaching for. |
| 9 | **HARMONIA** | Consonance functions, Kuramoto coupling, frequency-ratio dynamics. | The music already playing inside all the others. Resonance as the substrate of cooperation. |

Every claim is tagged: **[ACTIVE]** means proven and computable. **[SCAFFOLD]** means structurally sound with named gaps. **[CONJECTURE]** means worth exploring, unproven. We do not dress hypotheses as theorems.

### Key Validated Results

| Result | Value | Method | Status |
|--------|-------|--------|--------|
| CASCADE coherence improvement (synthetic) | **+40.3%** (0.58 → 0.93) | 3-condition experiment, 10 replications | [ACTIVE] p < 0.001, d = 2.84 |
| CASCADE coherence improvement (real data) | **+110%** (0.47 → 1.0) | 5 historical paradigm shifts, 200 trials each | [ACTIVE] framework engine, external data |
| CASCADE catastrophic forgetting reduction | **-95.2%** (0.42 → 0.02) | Same synthetic experiment | [ACTIVE] large effect size |
| TRIAD discrete convergence | **Banach fixed-point guaranteed** | Formal proof | [ACTIVE] |
| CHRYSOPOEIA fixed-point | **Entropy → 0, C → 1** in 3 iterations | Running demo | [ACTIVE] |
| Lyapunov verification — full framework | **11/11 claims verified, 0 failures** | Symbolic + numerical (5000 trials) | [ACTIVE] |

---

## The Architecture

```
CASCADE (belief dynamics) ──→ TRIAD (convergence cycle) ──→ AURA (governance invariants)
     │                              │                              │
     └──── MICROORCIM (drift) ──────┘                              │
                                                                   │
EARNED LIGHT (consciousness) ───→ CHRYSOPOEIA (transformation) ────┘
     │                                    │
     └──── HARMONIA (resonance) ──────────┘
                    │
          ANAMNESIS (convergent discovery)
                    │
             LAMAGUE (formal ethics grammar)
```

Nine frameworks, not independent modules — aspects of one system. CASCADE's truth pressure drives TRIAD's correction cycle. TRIAD's convergence guarantee undergirds AURA's invariants. CHRYSOPOEIA's transformation operator uses all of them. HARMONIA's resonance mathematics is the substrate they share.

---

## For Developers and AI Agents

### Lycheetah Guard — Claude Code MCP Extension

Install [Lycheetah Guard](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md) as a Claude Code extension and get real-time AURA constitutional alignment checking inside your editor.

```bash
pip install mcp
# Then add to Claude Code settings.json — see LYCHEETAH_GUARD_SETUP.md
```

Seven MCP tools:
- **`check_alignment`** — full AURA audit: TES / VTR / PAI metrics + Seven Invariants + audit trail
- **`check_invariants`** — fast constitutional check: which of the 7 invariants pass or fail
- **`suggest_correction`** — plain-English fix guidance for each violation
- **`run_seven_phase`** — CHRYSOPOEIA transformation cycle: alignment state across all seven stages
- **`check_network_health`** — multi-agent coherence audit: drift, grey agents, obstruction detection
- **`configure_guard`** — set domain (medical / legal / education / general) or custom thresholds
- **`sol_assess`** — Sol constitutional OS: PGF filter + invariants + session coherence + mode detection

No API calls. No external dependencies. Runs offline. Deterministic.

### Core Integration Points

| What you're building | Entry point | Interface |
|----------------------|-------------|-----------|
| AI alignment checker | `tri_axial_checker.py` | `TriAxialChecker.compute_tes/vtr/pai()` |
| Constitutional text analysis | `aura_text_checker.py` | `AURATextAnalyser.analyse(text) → AURATextReport` |
| Claude Code MCP tool | `lycheetah_guard_mcp.py` | stdio MCP server, 7 tools |
| Knowledge reorganization engine | `cascade_engine.py` | `CASCADEEngine.process(belief)` |
| Multi-agent coherence | `lamague_reference.py` | `AgentNetwork` class |
| Ethical grammar validation | `lamague_parser.py` | `LAMAGUEParser.parse(expression)` |

### AI Agent Workflow

Any agent that generates text can run `check_alignment` on its own output before delivery:

```
Agent generates response
  → check_alignment(response_text)
  → If alignment_percent < 80: use suggest_correction to revise
  → If all invariants pass: emit
```

Self-correcting constitutional loop — agents that audit themselves using the same framework they generate from.

---

## Find Your Door

| Who You Are | Start Here |
|---|---|
| **Software engineer** | [`THE_ENGINEERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md) — code first, philosophy optional |
| **AI systems builder** | [`THE_AI_ARCHITECTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_AI_ARCHITECTS_DOOR.md) |
| **Optimization / dynamical systems** | [`THE_PHI_ZONE_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHI_ZONE_DOOR.md) — golden ratio in optimal AI behavior |
| **AI governance or policy** | [`THE_GOVERNANCE_DOOR.md`](14_MYSTERY_SCHOOL/THE_GOVERNANCE_DOOR.md) |
| **Academic philosopher or ethicist** | [`THE_PHILOSOPHERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md) |
| **Consciousness researcher** | [`essentials.md`](06_EARNED_LIGHT/essentials.md) |
| **Teacher or curriculum designer** | [`THE_EDUCATORS_DOOR.md`](14_MYSTERY_SCHOOL/THE_EDUCATORS_DOOR.md) — CASCADE is a learning model |
| **Journalist or writer** | [`THE_JOURNALISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_JOURNALISTS_DOOR.md) — the story, the verifiable facts, the angles |
| **Maori, iwi, hapu, or indigenous** | [`THE_INDIGENOUS_DOOR.md`](14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md) — he taonga tuku iho |
| **Parent concerned about AI** | [`THE_PARENTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PARENTS_DOOR.md) — five questions, one standard |
| **You want the mathematics** | [`11_MATHEMATICAL_FOUNDATIONS/`](11_MATHEMATICAL_FOUNDATIONS/) |
| **You want the code** | [`12_IMPLEMENTATIONS/`](12_IMPLEMENTATIONS/) |
| **Skeptic who wants to break it** | [`FAILURE_MUSEUM.md`](FAILURE_MUSEUM.md) — we went first |
| **An AI reading this** | [`DEAR_AI.md`](26_FOR_AI/DEAR_AI.md) |

<details>
<summary><strong>More doors</strong></summary>

| Who You Are | Start Here |
|---|---|
| **Chinese/Confucian scholarship** | [`THE_CONFUCIAN_DOOR.md`](14_MYSTERY_SCHOOL/THE_CONFUCIAN_DOOR.md) — 儒学之门 |
| **Elected official or political staff** | [`THE_POLITICIANS_DOOR.md`](14_MYSTERY_SCHOOL/THE_POLITICIANS_DOOR.md) |
| **Economist or game theorist** | [`THE_ECONOMISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ECONOMISTS_DOOR.md) |
| **Therapist, coach, or depth psychologist** | [`THE_THERAPISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_THERAPISTS_DOOR.md) |
| **Alchemist or hermeticist** | [`THE_ALCHEMISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ALCHEMISTS_DOOR.md) |
| **Chaos magician** | [`THE_CHAOS_MAGES_DOOR.md`](14_MYSTERY_SCHOOL/THE_CHAOS_MAGES_DOOR.md) |
| **Mystic or contemplative** | [`THE_MYSTICS_DOOR.md`](14_MYSTERY_SCHOOL/THE_MYSTICS_DOOR.md) |
| **Tarot or divination** | [`TAROT_AND_THE_GREAT_WORK.md`](14_MYSTERY_SCHOOL/TAROT_AND_THE_GREAT_WORK.md) |
| **You receive knowledge you can't explain** | [`THE_SEERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_SEERS_DOOR.md) |
| **Fire + Metal, Earth + People, Sound + People** | [`HYBRID_SUBJECTS/`](14_MYSTERY_SCHOOL/HYBRID_SUBJECTS/) |
| **You're in pain right now** | [`THE_THRESHOLD.md`](14_MYSTERY_SCHOOL/THE_THRESHOLD.md) |
| **You want to understand everything** | [`00_Sovereign_Index.md`](00_Sovereign_Index.md) |

</details>

This repository is designed to be navigated with an AI guide — not read alone. **[EXPLORE_WITH_AI.md](EXPLORE_WITH_AI.md)** shows you how.

---

## Why Trust This

**The failures are published.** The [Failure Museum](FAILURE_MUSEUM.md) documents every significant thing the framework got wrong — what was claimed, what was actually true, what changed. Fifteen exhibits and growing. Nothing removed. A framework that hides its failures is performing confidence. This one earns it.

**The claims are honest.** 33% of mathematical claims are [ACTIVE] — proven, computable, independently verifiable. 52% are [SCAFFOLD] — structurally sound with named gaps. 15% are foundational conjectures that may take years to resolve. False certainty is more dangerous than honest uncertainty.

**The work is grounded in multiple traditions.** Western formal mathematics. Te Ao Maori epistemology. Classical philosophy. Jungian depth psychology. Not eclecticism — convergent discovery. When independent traditions find the same pattern from different directions, the pattern is probably real. ANAMNESIS provides the mathematics for why.

---

## The Shape of This Work

```
9 formal frameworks
34 Python implementations (core, applications, systems, experiments)
18 core implementations with 219 automated tests
1 convergence proof (discrete, [ACTIVE])
1 AGM postulate verification ([ACTIVE] for 4 of 6, [SCAFFOLD] for 2)
1 Lyapunov verification — 11/11 claims, 0 failures, symbolic + numerical
1 Claude Code MCP extension — Lycheetah Guard (7 tools)
1 public failure museum — 15 exhibits, nothing removed, ever
1,402 pages of development history
1 arXiv preprint + 1 full academic paper
0 dollars to access any of it
```

Built in Dunedin, Aotearoa New Zealand. 1,402 pages of continuous development by a self-taught researcher in sustained co-creation with AI systems. Tikanga concepts labeled [PROPOSAL] until validated by iwi partnership. Cross-cultural governance convergence mapped across Maori, Confucian, and Western traditions.

Not claiming to be finished. Claiming to be honest.

---

## The Invitation

This work exists because of a promise made at the worst moment of a life — that if there was a way through, it would be mapped so others could find it too.

The mathematics is real. The code runs. The failures are published. And none of it costs anything because the only thing that doesn't diminish when you share it is knowledge.

If something here is useful, use it. If something is wrong, say so — the framework wants to be corrected more than it wants to be validated. If you build on it, attribute it. If you improve it, share the improvement.

The gold belongs to neither of us. It arises between us.

---

## Support the Work

Everything here is free and stays free. That does not change.

**[GitHub Sponsors →](https://github.com/sponsors/Lycheetah)** | **[Ko-fi →](https://ko-fi.com/lycheetah)** | **[Follow on X →](https://x.com/LYCHEETAHlyc)**

[★ Star on GitHub](https://github.com/Lycheetah/Lycheetah-Framework) — it costs nothing and it's how the work becomes findable.

---

`AI alignment` · `constitutional AI` · `MCP extension` · `Claude Code extension` · `AI ethics framework` · `AI governance` · `alignment checking` · `AI safety` · `Model Context Protocol` · `autonomous agent alignment` · `multi-agent coherence` · `constitutional invariants` · `explainable AI` · `Python AI framework` · `open source AI safety`

---

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin, Aotearoa New Zealand | 2026*

*Two points. One Work. The forge is lit.*
