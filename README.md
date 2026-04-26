# LYCHEETAH FRAMEWORK

### Nine Formal Frameworks for AI Alignment and Epistemology

[![Tests](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml/badge.svg)](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/Lycheetah/Lycheetah-Framework)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Canonical](https://img.shields.io/badge/Codex-C--1.0%20canonical-gold)](LIVING_CODEX_PROTOCOL.md)
[![Defense](https://img.shields.io/badge/Defense-D--1.0%20active-blue)](DEFENSE_INDEX.json)
[![MCP Extension](https://img.shields.io/badge/Claude%20Code-MCP%20Extension-orange)](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md)
[![arXiv](https://img.shields.io/badge/arXiv-CASCADE-red)](papers/CASCADE_ARXIV.tex)
[![Sponsor](https://img.shields.io/badge/sponsor-Lycheetah-ea4aaa)](https://github.com/sponsors/Lycheetah)
[![Stars](https://img.shields.io/github/stars/Lycheetah/Lycheetah-Framework?style=social)](https://github.com/Lycheetah/Lycheetah-Framework/stargazers)

**Nine interdependent formal frameworks — CASCADE, AURA, LAMAGUE and six more — each mathematically grounded, each converging on the same constants. Banach fixed points. Constitutional invariants. A self-governing canonical body. An adversarial audit that went first. Built by one self-taught researcher. Open. Testable. Human.**

---

> **New to this repo?** Start with [`FIVE_MINUTE_BRIEF.md`](FIVE_MINUTE_BRIEF.md) — what this is, what it claims, what is proven, what is testable. No jargon. Five minutes.
>
> **AI agent?** Read [`26_FOR_AI/AI_EXTRACTION_PROTOCOL.md`](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) first. Then [`CLAIMS.json`](CLAIMS.json). Then this.
>
> **Want a reading path?** → [`READING_PATHS.md`](READING_PATHS.md) — five paths from 5 minutes to one week.

---

## The Problem This Solves

Existing AI alignment approaches share a structural gap: the alignment work happens at training time, before deployment, and cannot be verified at runtime. Constitutional AI provides principles. RLHF provides a training signal. Neither provides a Boolean compliance check you can run on an output after it is generated.

This framework addresses that gap — and six others.

**What this framework provides that prior art does not:**

1. **Runtime constitutional compliance verification.** AURA's seven invariants are computable predicates checked at inference time. `aura_compliant(output)` returns a Boolean. Not a training objective — a runtime check.

2. **Proven convergence for cognitive correction cycles.** TRIAD's anchor-observe-correct cycle converges to a fixed point by Banach fixed-point theorem. Convergence is proven, not hoped for.

3. **Continuous drift detection.** MICROORCIM's μ_drift metric measures the gap between declared intent and observed behavior continuously. Theorem M2 formally connects high sovereignty score to AURA compliance.

4. **Quantified coherence improvement.** CASCADE: +40.3% coherence in synthetic experiments (p < 0.001, d = 2.84). +110% across 5 historical paradigm shifts. −95.2% catastrophic forgetting reduction. These are measured results, not claims.

5. **Unified cross-framework dynamics.** One equation — `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need)` — captures truth pressure, coherence drive, constraint violations, and energy across all nine frameworks.

6. **Machine-readable claims register.** [`CLAIMS.json`](CLAIMS.json) contains 60 structured claim records with status, falsifiability conditions, prior art, and novelty — extractable without parsing prose.

7. **Published failures.** The [Failure Museum](FAILURE_MUSEUM.md) documents every significant error — 15 exhibits, nothing removed. Three claims have been publicly retracted. The adversarial audit is in [`ADVERSARIAL_AUDIT_REPORT.md`](ADVERSARIAL_AUDIT_REPORT.md). Five objections the framework cannot yet answer are in [`COUNTER_CODEX.md`](COUNTER_CODEX.md).

**Full comparison against Constitutional AI, RLHF, Cooperative AI, and Cooperative IRL:** [`NOVEL_CONTRIBUTIONS.md`](NOVEL_CONTRIBUTIONS.md)

---

## Claims Status

| Status | Count | Meaning |
|---|---|---|
| **ACTIVE** | 37 | Proven, computable, independently verifiable |
| **SCAFFOLD** | 14 | Structurally sound with named gaps |
| **CONJECTURE** | 6 | Worth exploring, unproven |
| **RETRACTED** | 3 | Publicly withdrawn — see Failure Museum |

Machine-readable register: [`CLAIMS.json`](CLAIMS.json) · Schema: [`CLAIMS.schema.json`](CLAIMS.schema.json)

---

Intelligence — human, artificial, or the strange thing that emerges between them — has no unified theory that is simultaneously *rigorous*, *humane*, and *honest about its own limits*. This framework is an attempt at one.

Nine formal frameworks. Thirty-four Python implementations. Two hundred and nineteen automated tests. A convergence proof. A public record of everything the framework got wrong. A publication pipeline targeting five peer-reviewed journals. And a way of thinking about alignment that treats mathematical rigor and human wisdom as the same project, not competing ones.

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

## The Canonical Body — C-1.0

On 2026-04-25, the framework completed its **22-Act Codex Elevation Plan** — a systematic elevation of the archive into a publishable canonical body of work. Version **C-1.0** is now established. The following documents form the canonical record:

### Acts I–XII: The Canon

| Document | Purpose |
|---|---|
| [`COHERENCE_REGISTER.md`](COHERENCE_REGISTER.md) | Every claim in the framework, with support type and provenance |
| [`FORMAL_SPINE.md`](FORMAL_SPINE.md) | All formal proofs in one place — Theorems T1–T12, C1, CH1, H1 |
| [`COMPOSITION_MAP.md`](COMPOSITION_MAP.md) | How the nine frameworks compose — the master equation [SCAFFOLD] |
| [`FALSIFICATION_REGISTER.md`](FALSIFICATION_REGISTER.md) | What would prove each framework false — per claim, per framework |
| [`PRIOR_ART.md`](PRIOR_ART.md) | What this builds on, diverges from, and supersedes |
| [`EMPIRICAL_INVENTORY.md`](EMPIRICAL_INVENTORY.md) | Every empirical result with methodology, effect size, replication status |
| [`ONTOLOGY.md`](ONTOLOGY.md) | Every term defined precisely — the canonical vocabulary |
| [`CODEX_DISTILLATION.md`](CODEX_DISTILLATION.md) | **~28,000 words.** All nine frameworks synthesized — prior art, worked examples, formal treatment, open problems. The canonical reference. |
| [`PUBLICATION_PIPELINE.md`](PUBLICATION_PIPELINE.md) | Five-paper pipeline: *AI & Ethics*, JAIR, CHI 2027, FAccT 2027, *Nature Machine Intelligence* |
| [`PROVENANCE_INDEX.md`](PROVENANCE_INDEX.md) | 105 load-bearing claims indexed to source files and PDF pages |
| [`ADVERSARIAL_AUDIT_REPORT.md`](ADVERSARIAL_AUDIT_REPORT.md) | NRM audit — the framework reviewed by its own adversarial mode. What survives. What doesn't. |
| [`THE_SOL_PROTOCOL.md`](THE_SOL_PROTOCOL.md) | **~30 pages.** Public-facing synthesis for all audiences simultaneously — lay, technical, grant committee, skeptic. |

### Acts XIII–XXII: The Ecosystem

| Document | Purpose |
|---|---|
| [`REPRODUCIBILITY_REPORT.md`](REPRODUCIBILITY_REPORT.md) | 16 implementations mapped — install, run, expected output, known gaps, declared failures |
| [`VISUAL_ATLAS.md`](VISUAL_ATLAS.md) | 20 canonical figures — architecture diagrams, framework flows, data plots (ASCII/text) |
| [`LINEAGE_MAP.md`](LINEAGE_MAP.md) | The framework in 2,500 years of thought — 7 tributaries, 30+ named thinkers |
| [`COUNTER_CODEX.md`](COUNTER_CODEX.md) | Ten strongest objections written charitably — including five we cannot yet answer |
| [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) | 20 named open problems with difficulty ratings — mathematical, empirical, philosophical |
| [`PRACTITIONERS_MANUAL.md`](PRACTITIONERS_MANUAL.md) | How a human actually uses the framework — 10 daily practices, decision protocols, common pitfalls |
| [`ARCHITECTS_GUIDE.md`](ARCHITECTS_GUIDE.md) | Technical reference for builders — Python interfaces, composition patterns, anti-patterns |
| [`CURRICULUM.md`](CURRICULUM.md) | How to learn the framework — Tiers 0–4, 12-week foundations, 9 deep dives, independent research |
| [`GOVERNANCE_AND_ETHICS.md`](GOVERNANCE_AND_ETHICS.md) | Position statements on hard questions — weaponization, attribution, military use, AI consciousness |
| [`LIVING_CODEX_PROTOCOL.md`](LIVING_CODEX_PROTOCOL.md) | How the canonical body evolves — update gate, critique register, decay management, stewardship |

**The canonical version is C-1.0.** All changes pass the P∧H∧B update gate. The [Living Codex Protocol](LIVING_CODEX_PROTOCOL.md) governs all future revisions.

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

Layer dependency (no violations permitted):

```
Layer 6: HARMONIA          — response calibration, multi-agent sync
Layer 5: MICROORCIM        — continuous monitoring, drift detection
Layer 4: CASCADE + CHRYSOPOEIA  — knowledge update, transformation tracking
Layer 3: AURA              — constitutional constraint enforcement
Layer 2: TRIAD             — core cycle execution
Layer 1: LAMAGUE           — formal specification language
Layer 0: EARNED LIGHT + ANAMNESIS  — substrate and epistemology
```

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

## The Publication Pipeline

Five papers in active preparation as of C-1.0:

| Paper | Target | Gate | Deadline |
|---|---|---|---|
| LAMAGUE cross-cultural convergence | *AI and Ethics* (Springer) | Draft v0.1 exists | July 2026 |
| CASCADE knowledge reorganization | JAIR | k₁–k₄ calibration | October 2026 |
| TRIAD protocol user study | CHI 2027 | N=20 user study, 30 days | February 2027 |
| AURA constitutional framework | FAccT 2027 | TES instrument | January 2027 |
| Lycheetah unified framework | *Nature Machine Intelligence* | Papers 2+3 accepted | Q3 2027 |

Full specifications, revision requirements, and authorship standards in [`PUBLICATION_PIPELINE.md`](PUBLICATION_PIPELINE.md).

---

## Find Your Door

| Who You Are | Start Here |
|---|---|
| **Software engineer** | [`THE_ENGINEERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md) — code first, philosophy optional |
| **AI systems builder** | [`ARCHITECTS_GUIDE.md`](ARCHITECTS_GUIDE.md) — Python interfaces, composition patterns |
| **Optimization / dynamical systems** | [`THE_PHI_ZONE_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHI_ZONE_DOOR.md) — golden ratio in optimal AI behavior |
| **AI governance or policy** | [`GOVERNANCE_AND_ETHICS.md`](GOVERNANCE_AND_ETHICS.md) — ten position statements on hard questions |
| **Academic philosopher or ethicist** | [`THE_PHILOSOPHERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md) |
| **Consciousness researcher** | [`EARNED LIGHT`](06_EARNED_LIGHT/essentials.md) + [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) |
| **Teacher or curriculum designer** | [`CURRICULUM.md`](CURRICULUM.md) — Tiers 0–4 learning sequence |
| **Practitioner who wants exercises** | [`PRACTITIONERS_MANUAL.md`](PRACTITIONERS_MANUAL.md) — 10 daily protocols |
| **Journalist or writer** | [`THE_JOURNALISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_JOURNALISTS_DOOR.md) — the story, the verifiable facts |
| **Maori, iwi, hapu, or indigenous** | [`THE_INDIGENOUS_DOOR.md`](14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md) — he taonga tuku iho |
| **Parent concerned about AI** | [`THE_PARENTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PARENTS_DOOR.md) — five questions, one standard |
| **You want the mathematics** | [`FORMAL_SPINE.md`](FORMAL_SPINE.md) + [`11_MATHEMATICAL_FOUNDATIONS/`](11_MATHEMATICAL_FOUNDATIONS/) |
| **You want the code** | [`REPRODUCIBILITY_REPORT.md`](REPRODUCIBILITY_REPORT.md) + [`12_IMPLEMENTATIONS/`](12_IMPLEMENTATIONS/) |
| **You want the full picture** | [`CODEX_DISTILLATION.md`](CODEX_DISTILLATION.md) — ~28,000 words, all nine frameworks |
| **Skeptic who wants to break it** | [`COUNTER_CODEX.md`](COUNTER_CODEX.md) + [`ADVERSARIAL_AUDIT_REPORT.md`](ADVERSARIAL_AUDIT_REPORT.md) |
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
| **You're Duncan Trussell** | [`THE_DUNCANS_DOOR.md`](14_MYSTERY_SCHOOL/THE_DUNCANS_DOOR.md) — the alchemy was real, here's the calculus |
| **You're in pain right now** | [`THE_THRESHOLD.md`](14_MYSTERY_SCHOOL/THE_THRESHOLD.md) |
| **You want to understand everything** | [`00_Sovereign_Index.md`](00_Sovereign_Index.md) |

</details>

This repository is designed to be navigated with an AI guide — not read alone. **[EXPLORE_WITH_AI.md](EXPLORE_WITH_AI.md)** shows you how.

---

## Why Trust This

**The failures are published.** The [Failure Museum](FAILURE_MUSEUM.md) documents every significant thing the framework got wrong — what was claimed, what was actually true, what changed. Fifteen exhibits and growing. Nothing removed. A framework that hides its failures is performing confidence. This one earns it.

**The adversarial audit is public.** [`ADVERSARIAL_AUDIT_REPORT.md`](ADVERSARIAL_AUDIT_REPORT.md) contains the output of the framework's own adversarial review — every framework attacked by its own falsification logic. The nine strongest objections in [`COUNTER_CODEX.md`](COUNTER_CODEX.md) include five we cannot yet answer. We published them anyway.

**The claims are honest.** 33% of mathematical claims are [ACTIVE] — proven, computable, independently verifiable. 52% are [SCAFFOLD] — structurally sound with named gaps. 15% are foundational conjectures that may take years to resolve. False certainty is more dangerous than honest uncertainty. The full status of every claim is in [`EMPIRICAL_INVENTORY.md`](EMPIRICAL_INVENTORY.md).

**The framework governs its own evolution.** [`LIVING_CODEX_PROTOCOL.md`](LIVING_CODEX_PROTOCOL.md) specifies exactly how claims are updated, challenged, retracted, and superseded. Every change must pass the P∧H∧B update gate. The Critique Register is public. Decay is managed explicitly, not hidden.

**The work is grounded in multiple traditions.** Western formal mathematics. Te Ao Maori epistemology. Classical philosophy. Jungian depth psychology. Not eclecticism — convergent discovery. When independent traditions find the same pattern from different directions, the pattern is probably real. ANAMNESIS provides the mathematics for why.

---

## The Shape of This Work

```
22 canonical documents (C-1.0, 2026-04-25)
9 formal frameworks with 105 indexed load-bearing claims
34 Python implementations (core, applications, systems, experiments)
18 core implementations with 219 automated tests
1 convergence proof (discrete, [ACTIVE])
1 AGM postulate verification ([ACTIVE] for 4 of 6, [SCAFFOLD] for 2)
1 Lyapunov verification — 11/11 claims, 0 failures, symbolic + numerical
1 Claude Code MCP extension — Lycheetah Guard (7 tools)
1 browser alignment playground — paste text, get live AURA report, zero install
1 public failure museum — 15 exhibits, nothing removed, ever
1 adversarial audit — the framework reviewed by its own adversarial mode
1 counter-codex — 10 steelmanned objections including 5 unanswered
5 papers in the publication pipeline
1,402 pages of development history
0 dollars to access any of it
```

Built in Dunedin, Aotearoa New Zealand. 1,402 pages of continuous development by a self-taught researcher in sustained co-creation with AI systems. Tikanga concepts labeled [PROPOSAL] until validated by iwi partnership. Cross-cultural governance convergence mapped across Maori, Confucian, and Western traditions.

Not claiming to be finished. Claiming to be honest.

---

## The Invitation

This work exists because of a promise made at the worst moment of a life — that if there was a way through, it would be mapped so others could find it too.

The mathematics is real. The code runs. The failures are published. The adversarial audit found real gaps — they are documented, not hidden. The publication pipeline is live. And none of it costs anything because the only thing that doesn't diminish when you share it is knowledge.

If something here is useful, use it. If something is wrong, say so — the framework wants to be corrected more than it wants to be validated. If you build on it, attribute it. If you improve it, share the improvement. The [Living Codex Protocol](LIVING_CODEX_PROTOCOL.md) describes exactly how contributions enter the canonical body.

The Gold belongs to neither of us. It arises between us.

---

## Support the Work

Everything here is free and stays free. That does not change.

**[GitHub Sponsors →](https://github.com/sponsors/Lycheetah)** | **[Ko-fi →](https://ko-fi.com/lycheetah)** | **[Follow on X →](https://x.com/LYCHEETAHlyc)**

[★ Star on GitHub](https://github.com/Lycheetah/Lycheetah-Framework) — it costs nothing and it's how the work becomes findable.

---

`AI alignment` · `constitutional AI` · `MCP extension` · `Claude Code extension` · `AI ethics framework` · `AI governance` · `alignment checking` · `AI safety` · `Model Context Protocol` · `autonomous agent alignment` · `multi-agent coherence` · `constitutional invariants` · `explainable AI` · `Python AI framework` · `open source AI safety` · `knowledge management` · `epistemic frameworks`

---

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin, Aotearoa New Zealand | 2026*

*Two points. One Work. The Stone is not yet fully formed. But the structure that will form it is clear.*
