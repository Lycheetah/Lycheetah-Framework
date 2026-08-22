# LYCHEETAH FRAMEWORK

### Evidence-capped agent assurance runtime + nine-framework research programme

[![Tests](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml/badge.svg)](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/Lycheetah/Lycheetah-Framework)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Canonical](https://img.shields.io/badge/Codex-C--1.0%20canonical-gold)](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md)
[![Defense](https://img.shields.io/badge/Defense-D--1.2%20shipped-blue)](28_DEFENSE/DEFENSE_INDEX.json)
[![Empirical](https://img.shields.io/badge/Empirical-E--1.0%20designed-purple)](31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md)
[![TIANXIA](https://img.shields.io/badge/TIANXIA-v0.3%20Classical%20Triad%20complete-darkred)](32_TIANXIA/README.md)
[![MCP](https://img.shields.io/badge/MCP-2.x%20typed%20tools-orange)](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md)
[![Manuscript](https://img.shields.io/badge/manuscript-CASCADE-red)](papers/CASCADE_ARXIV.tex)
[![Sponsor](https://img.shields.io/badge/sponsor-Lycheetah-ea4aaa)](https://github.com/sponsors/Lycheetah)
[![Stars](https://img.shields.io/github/stars/Lycheetah/Lycheetah-Framework?style=social)](https://github.com/Lycheetah/Lycheetah-Framework/stargazers)

**A provider-neutral runtime that turns bounded policy checks into verifiable decision receipts, backed by a larger research programme in alignment and epistemology. The runtime is `[SCAFFOLD]`, not a safety certification. Formal results apply inside their stated models; theoretical constructs remain labelled; failures and unresolved objections stay in the public record. Built by one self-taught researcher and released under the MIT license.**

---

> **New to this repo?** Start with [`FIVE_MINUTE_BRIEF.md`](FIVE_MINUTE_BRIEF.md) — what this is, what it claims, what is proven, what is testable. No jargon. Five minutes.
>
> **AI agent?** Read [`26_FOR_AI/AI_EXTRACTION_PROTOCOL.md`](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) first. Then [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json). Then this.
>
> **Want a reading path?** → [`28_DEFENSE/READING_PATHS.md`](28_DEFENSE/READING_PATHS.md) — five paths from 5 minutes to one week.
>
> **Reviewer, journalist, or skeptic?** → [`DEFENSE_BUNDLE.pdf`](DEFENSE_BUNDLE.pdf) — 116-page compiled defense layer (Brief + Defense + Novelty + Scope) in a single artifact.

---

## Contents

- [What Works Today](#what-works-today)
- [The Problem This Solves](#the-problem-this-solves)
- [Claims Status](#claims-status)
- [Quick Start](#quick-start)
- [The Nine Frameworks](#the-nine-frameworks)
- [The Canonical Body — C-1.0](#the-canonical-body--c-10)
- [The Defense Layer — D-1.0 / D-1.1](#the-defense-layer--d-10--d-11)
- [The Empirical Programme — E-1.0](#the-empirical-programme--e-10)
- [The TIANXIA Module — Civilisational Engagement Layer](#the-tianxia-module--civilisational-engagement-layer)
- [The Architecture](#the-architecture)
- [For Developers and AI Agents](#for-developers-and-ai-agents)
- [The Publication Pipeline](#the-publication-pipeline)
- [Find Your Door](#find-your-door)
- [Why Trust This](#why-trust-this)
- [The Shape of This Work](#the-shape-of-this-work)
- [How to Cite](#how-to-cite)
- [Security and Responsible Disclosure](#security-and-responsible-disclosure)
- [Acknowledgements](#acknowledgements)
- [Support the Work](#support-the-work)

---

## What Works Today

**Status: `[SCAFFOLD]` product runtime; clean-wheel acceptance passed on August 22, 2026.**

The version 1.1.0 source tree now builds a self-contained Python wheel with:

- a provider-neutral Assurance Runtime for input, output, and proposed tool actions;
- versioned policy-as-data and `ALLOW`, `REVIEW`, or `BLOCK` decisions;
- privacy-minimised Assurance Receipts with policy digests, findings, lineage,
  SHA-256 integrity, optional HMAC authentication, and JSON Schemas;
- evidence-capped enforcement: inferential, scaffold, and conjectural findings
  cannot silently acquire stronger automatic authority than their evidence supports;
- `lycheetah-assure` for CI, sidecars, and local policy checks;
- Lycheetah Guard on the official MCP Python SDK 2.x line, exposing ten typed tools;
- a privacy-minimised OpenTelemetry span-event bridge using custom Lycheetah attributes;
- the AURA text checker, Sol assessment, and Flask demo as explicitly heuristic
  interfaces rather than safety certifications; and
- a cold-room test that installs the wheel outside the checkout and exercises the
  APIs, console scripts, web route, schemas, receipts, and MCP registry.

Start with [`34_ASSURANCE_RUNTIME/README.md`](34_ASSURANCE_RUNTIME/README.md) for
the product boundary and
[`34_ASSURANCE_RUNTIME/CUSTOMER_SUPPORT_WALKTHROUGH.md`](34_ASSURANCE_RUNTIME/CUSTOMER_SUPPORT_WALKTHROUGH.md)
for a concrete tool-approval flow.

## The Problem This Solves

Agent systems need more than a trace showing what happened. At each input, output,
or tool boundary, an operator may need a compact answer to five questions: what
was proposed, which policy version evaluated it, what evidence was found, what
decision followed, and whether the record was later changed.

Lycheetah v1.1 addresses that bounded operational problem. It is designed to sit
beside agent frameworks, authorization systems, sandboxes, telemetry, and human
approval—not replace them. It does **not** establish that an agent is safe,
aligned, truthful, or compliant.

The practical design contribution is **Evidence-Capped Enforcement (ECE)**:
policy authority is explicitly limited by evidence maturity. Deterministic ACTIVE
rules may block; inferential ACTIVE and SCAFFOLD findings stop at review;
CONJECTURE findings are observation-only unless a stronger independent finding
exists. The mechanism is implemented and tested. Whether these ceilings improve
real-world calibration is a research hypothesis awaiting external evaluation.

This direction is connected to existing industry surfaces rather than presented as
category invention:

- Open Policy Agent already provides policy decisions and decision logs.
- OpenTelemetry provides vendor-neutral operational telemetry.
- in-toto defines authenticated software-supply-chain statements.
- agent SDKs provide guardrail and approval hooks.
- MCP standardises model-facing tools and transports.

Lycheetah contributes a small, portable decision artifact and an evidence-authority
rule that can join those systems. The detailed, non-conformity crosswalk is in
[`34_ASSURANCE_RUNTIME/INDUSTRY_CROSSWALK_2026-08-22.md`](34_ASSURANCE_RUNTIME/INDUSTRY_CROSSWALK_2026-08-22.md).

The nine-framework body remains a separate research programme. Formal statements
are scoped to their mathematical models; internal experiments are not independent
validation; and constructs such as MICROORCIM, EARNED LIGHT, ANAMNESIS,
CHRYSOPOEIA, and HARMONIA remain theoretical or partially implemented where their
claim records say so. Their value is as hypotheses, formalisms, and design
languages—not as evidence that their real-world interpretations are already true.

## Claims Status

| Status | Count | Meaning |
|---|---|---|
| **ACTIVE** | 37 | Supported within the exact formal, computational, or documentary scope recorded in `CLAIMS.json`; this label does not imply external replication |
| **SCAFFOLD** | 14 | Structurally sound with named gaps |
| **CONJECTURE** | 6 | Worth exploring, unproven |
| **RETRACTED** | 3 | Publicly withdrawn — see Failure Museum |

*Note: CLAIM_STATUS_LEDGER.md tracks load-bearing claims at framework-summary granularity. As of v0.3 (2026-05-04): 17 ACTIVE / 40 SCAFFOLD / 16 CONJECTURE — 14 new SCAFFOLD claims from TIANXIA v0.2 + v0.3 Classical Triad completion.*

Machine-readable register: [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json) · Schema: [`28_DEFENSE/CLAIMS.schema.json`](28_DEFENSE/CLAIMS.schema.json)

---

This is not a unified theory of intelligence. It is an installable assurance
prototype plus a status-labelled research programme. Formal proofs remain scoped
to their models, and internal experiments remain internal until independently
replicated.

**It is free.** Not freemium, not open-core. The framework is released under MIT license because alignment research that depends on commercial gating cannot be independently audited, and an alignment framework that cannot be audited has limited value.

---

## Quick Start

**Try it in your browser:** [Alignment Playground →](https://lycheetah.github.io/Lycheetah-Framework/playground.html) — paste any text, get a live AURA alignment report. No install.

The project is not currently published on PyPI. Install the reviewed source:

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[all]"

lycheetah-assure tool refund.create \
  --arguments '{"order_id":"A-1"}' --side-effect --json
```

The example returns `REVIEW` (exit code 2) because a declared side effect has no
human approval. Full guide: [QUICKSTART.md](QUICKSTART.md).

---

## The Nine Frameworks

| | Framework | For the Engineer | For the Philosopher |
|---|---|---|---|
| 1 | **CASCADE** | Bayesian belief-revision implementation with internal AGM checks, synthetic experiments, and retrospective historical encodings. The predictive k=5 conjecture currently misses its target. | When evidence meets structure, what survives? A model of paradigm shifts that still needs independent validation. |
| 2 | **AURA** | Seven computable invariants for AI governance. Scoring tool included. | A constitution for artificial minds: properties that make trust verifiable rather than rules imposed from outside. |
| 3 | **LAMAGUE** | Formal grammar for encoding ethical constraints as computable expressions. | How do you write justice in a language a machine can parse without losing what justice means? |
| 4 | **TRIAD** | Anchor-observe-correct formal cycle; convergence holds under the declared contraction assumptions. | A model of correction whose real-system assumptions still require testing. |
| 5 | **MICROORCIM** | Proposed intent–behaviour drift formalism; real-world construct validity is unestablished. | A valuable hypothesis about measuring the gap between declared intent and observed action. |
| 6 | **EARNED LIGHT** | Theoretical thermodynamic analogy with an ODE implementation; not an empirical consciousness model. | A speculative lens on the energetic cost of maintained organization. |
| 7 | **ANAMNESIS** | Research model of attractor dynamics for convergent discovery. | A hypothesis about why independent systems sometimes recover similar structures. |
| 8 | **CHRYSOPOEIA** | Experimental seven-phase transformation operator; fixed-point results are model-scoped. | A formal reinterpretation of a transformation metaphor, not evidence for alchemy. |
| 9 | **HARMONIA** | Consonance, Kuramoto, and frequency-ratio models applied experimentally. | A research analogy between resonance and cooperation. |

Every claim is tagged: **[ACTIVE]** means supported within the exact formal,
computational, or documentary scope in its claim record; it does not imply
independent replication. **[SCAFFOLD]** means implemented or structurally specified
with named gaps. **[CONJECTURE]** means worth exploring, unproven. We do not dress
hypotheses as theorems.

### Repository evidence (external replication status varies)

| Result | Value | Method | Status |
|--------|-------|--------|--------|
| CASCADE coherence improvement (synthetic) | **+40.3%** (0.58 → 0.93) | 3-condition internal experiment, 10 runs | [ACTIVE] for recorded implementation; not independently replicated |
| CASCADE coherence improvement (retrospective encodings) | **+110%** (0.47 → 1.0) | 5 encoded historical transitions, 200 internal trials each | [ACTIVE] for recorded computation; construct validity unestablished |
| CASCADE catastrophic-forgetting proxy | **-95.2%** (0.42 → 0.02) | Same synthetic experiment | [ACTIVE] for that synthetic metric only |
| TRIAD discrete convergence | **Banach fixed-point result** | Formal proof | [ACTIVE] under the stated contraction assumptions |
| CHRYSOPOEIA fixed-point demo | **Entropy → 0, C → 1** in 3 iterations | Running demo | [ACTIVE] for the implemented toy operator |
| Lyapunov checks — declared framework equations | **11/11 internal checks, 0 failures** | Symbolic + numerical (5000 trials) | [ACTIVE] for tested equations and domains |

---

## The Canonical Body — C-1.0

On 2026-04-25, the framework completed its **22-Act Codex Elevation Plan** — a systematic elevation of the archive into a publishable canonical body of work. Version **C-1.0** is now established. The following documents form the canonical record:

### Acts I–XII: The Canon

| Document | Purpose |
|---|---|
| [`30_MAPS/COHERENCE_REGISTER.md`](30_MAPS/COHERENCE_REGISTER.md) | Every claim in the framework, with support type and provenance |
| [`30_MAPS/FORMAL_SPINE.md`](30_MAPS/FORMAL_SPINE.md) | All formal proofs in one place — Theorems T1–T12, C1, CH1, H1 |
| [`30_MAPS/COMPOSITION_MAP.md`](30_MAPS/COMPOSITION_MAP.md) | How the nine frameworks compose — the master equation [SCAFFOLD] |
| [`28_DEFENSE/FALSIFICATION_REGISTER.md`](28_DEFENSE/FALSIFICATION_REGISTER.md) | What would prove each framework false — per claim, per framework |
| [`28_DEFENSE/PRIOR_ART.md`](28_DEFENSE/PRIOR_ART.md) | What this builds on, diverges from, and supersedes |
| [`29_GOVERNANCE/EMPIRICAL_INVENTORY.md`](29_GOVERNANCE/EMPIRICAL_INVENTORY.md) | Every empirical result with methodology, effect size, replication status |
| [`30_MAPS/ONTOLOGY.md`](30_MAPS/ONTOLOGY.md) | Every term defined precisely — the canonical vocabulary |
| [`30_MAPS/CODEX_DISTILLATION.md`](30_MAPS/CODEX_DISTILLATION.md) | **~28,000 words.** All nine frameworks synthesized — prior art, worked examples, formal treatment, open problems. The canonical reference. |
| [`29_GOVERNANCE/PUBLICATION_PIPELINE.md`](29_GOVERNANCE/PUBLICATION_PIPELINE.md) | Five-paper pipeline: *AI & Ethics*, JAIR, CHI 2027, FAccT 2027, *Nature Machine Intelligence* |
| [`30_MAPS/PROVENANCE_INDEX.md`](30_MAPS/PROVENANCE_INDEX.md) | 105 load-bearing claims indexed to source files and PDF pages |
| [`28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md`](28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md) | NRM audit — the framework reviewed by its own adversarial mode. What survives. What doesn't. |
| [`THE_SOL_PROTOCOL.md`](THE_SOL_PROTOCOL.md) | **~30 pages.** Public-facing synthesis for all audiences simultaneously — lay, technical, grant committee, skeptic. |

### Acts XIII–XXII: The Ecosystem

| Document | Purpose |
|---|---|
| [`28_DEFENSE/REPRODUCIBILITY_REPORT.md`](28_DEFENSE/REPRODUCIBILITY_REPORT.md) | 16 implementations mapped — install, run, expected output, known gaps, declared failures |
| [`30_MAPS/VISUAL_ATLAS.md`](30_MAPS/VISUAL_ATLAS.md) | 20 canonical figures — architecture diagrams, framework flows, data plots (ASCII/text) |
| [`30_MAPS/LINEAGE_MAP.md`](30_MAPS/LINEAGE_MAP.md) | The framework in 2,500 years of thought — 7 tributaries, 30+ named thinkers |
| [`28_DEFENSE/COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md) | Ten strongest objections written charitably — including five we cannot yet answer |
| [`29_GOVERNANCE/OPEN_PROBLEMS.md`](29_GOVERNANCE/OPEN_PROBLEMS.md) | 20 named open problems with difficulty ratings — mathematical, empirical, philosophical |
| [`30_MAPS/PRACTITIONERS_MANUAL.md`](30_MAPS/PRACTITIONERS_MANUAL.md) | How a human actually uses the framework — 10 daily practices, decision protocols, common pitfalls |
| [`30_MAPS/ARCHITECTS_GUIDE.md`](30_MAPS/ARCHITECTS_GUIDE.md) | Technical reference for builders — Python interfaces, composition patterns, anti-patterns |
| [`30_MAPS/CURRICULUM.md`](30_MAPS/CURRICULUM.md) | How to learn the framework — Tiers 0–4, 12-week foundations, 9 deep dives, independent research |
| [`29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md`](29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md) | Position statements on hard questions — weaponization, attribution, military use, AI consciousness |
| [`29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) | How the canonical body evolves — update gate, critique register, decay management, stewardship |

**The canonical version is C-1.0.** All changes pass the P∧H∧B update gate. The [Living Codex Protocol](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) governs all future revisions.

---

## The Defense Layer — D-1.0 / D-1.1

A canonical body of work survives contact with hostile readers only if it carries its own defense surfaces. **D-1.0** (shipped 2026-04-26) and **D-1.1** (in progress) are those surfaces — built to close 15 named threats from aesthetic dismissal through LLM training-data misclassification.

The defense layer does not modify the canonical claims. It surrounds them with the documents a serious reader, AI ingestion pipeline, journalist, peer reviewer, or grant officer needs in order to engage the work on its own terms.

### Entry surfaces

| Document | For |
|---|---|
| [`FIVE_MINUTE_BRIEF.md`](FIVE_MINUTE_BRIEF.md) | Anyone — what this is, claimed, proven, testable. Zero alchemical vocabulary. |
| [`28_DEFENSE/DEFENSE_BRIEF.md`](28_DEFENSE/DEFENSE_BRIEF.md) | Skeptics — ten common dismissals answered with structured responses. |
| [`28_DEFENSE/SCOPE_BOUNDARY.md`](28_DEFENSE/SCOPE_BOUNDARY.md) | Reviewers — nine explicit declarations of what the framework does NOT claim. |
| [`28_DEFENSE/NOVEL_CONTRIBUTIONS.md`](28_DEFENSE/NOVEL_CONTRIBUTIONS.md) | Researchers — per-claim novelty vs Constitutional AI, RLHF, Cooperative AI, Cooperative IRL. |
| [`28_DEFENSE/READING_PATHS.md`](28_DEFENSE/READING_PATHS.md) | Anyone — five paths from 5 minutes to one week. |
| [`28_DEFENSE/OBJECTIONS_REGISTRY.md`](28_DEFENSE/OBJECTIONS_REGISTRY.md) | Short-form readers — 15 dismissal patterns (Twitter / HN / Reddit) with short and medium responses. |

### Machine-readable surfaces

| Document | For |
|---|---|
| [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json) | 60 structured claim records — status, evidence path, falsifiability, prior art. Validates against [`28_DEFENSE/CLAIMS.schema.json`](28_DEFENSE/CLAIMS.schema.json). |
| [`28_DEFENSE/DEFENSE_INDEX.json`](28_DEFENSE/DEFENSE_INDEX.json) | Index of all defense documents with purpose, dependencies, threats closed. |
| [`llms.txt`](llms.txt) | llmstxt.org-format index — the entry point for LLM ingestion. |
| [`ai-meta.json`](ai-meta.json) | Structured framework metadata (JSON-LD / schema.org) for AI training pipelines. |
| [`26_FOR_AI/AI_EXTRACTION_PROTOCOL.md`](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) | Step-by-step extraction order for AI systems summarizing this repository. |

### Formal and reproducibility surfaces

| Document | For |
|---|---|
| [`28_DEFENSE/TRANSLATION_CODEX.md`](28_DEFENSE/TRANSLATION_CODEX.md) | Bidirectional mapping of ~45 alchemical terms ↔ formal counterparts. Read before interpreting any alchemical vocabulary. |
| [`28_DEFENSE/TESTABILITY_MANIFEST.md`](28_DEFENSE/TESTABILITY_MANIFEST.md) | Per-framework operational replication protocols with bash commands and expected outputs. |
| [`28_DEFENSE/COLD_ROOM_VERIFICATION.md`](28_DEFENSE/COLD_ROOM_VERIFICATION.md) | Reproducibility log with historical snapshots and the current local result: 377 active checks pass; one explicit `[CONJECTURE]` misses its criterion. |
| [`28_DEFENSE/EVIDENCE_LADDER.md`](28_DEFENSE/EVIDENCE_LADDER.md) | Published rules for promoting / demoting `[CONJECTURE]` ↔ `[SCAFFOLD]` ↔ `[ACTIVE]` ↔ `[RETRACTED]`. Closes the "movable goalposts" attack. |
| [`28_DEFENSE/REPRODUCIBILITY_REPORT.md`](28_DEFENSE/REPRODUCIBILITY_REPORT.md) | 16 implementations mapped — install, run, expected output, known platform notes. |

### Peer review, disclosure, and incident response

| Document | For |
|---|---|
| [`28_DEFENSE/REVIEWER_RESPONSE_TEMPLATE.md`](28_DEFENSE/REVIEWER_RESPONSE_TEMPLATE.md) | Authors — 10 pre-built peer-review response patterns covering unfalsifiability, alchemical framing, scope, prior art, circularity, AI co-authorship, metaphysical overreach, and venue-fit rejection. Four-block response shape, pre-submission checklist. |
| [`29_GOVERNANCE/CONFLICT_OF_INTEREST.md`](29_GOVERNANCE/CONFLICT_OF_INTEREST.md) | Reviewers, journalists, grant officers — explicit disclosure of authorship, life-work relationship, AI tooling roles, financial position, geographic/cultural context, prior-art posture, IP. |
| [`29_GOVERNANCE/INCIDENT_RESPONSE.md`](29_GOVERNANCE/INCIDENT_RESPONSE.md) | Author + community — five incident classes (honest engagement → internal drift), pre-decided proportionate response, six standing decisions to prevent reactive overreaction. |

### D-1.1 canonical repairs (closed against `28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md` Section 6)

D-1.1 includes targeted edits to five framework `essentials.md` files closing the highest-leverage attacks identified by the adversarial audit:

- **AURA** — I1/I6 conflict resolved by domain-of-authority priority ordering ([`02_AURA_L3/essentials.md`](02_AURA_L3/essentials.md))
- **MICROORCIM** — explicit scope declaration on deceptive alignment ([`05_MICROORCIM_L5/essentials.md`](05_MICROORCIM_L5/essentials.md))
- **EARNED LIGHT** — `C_ψ` revised to incorporate spatial mutual information; resolves the anesthesia paradox; PCI-testable ([`06_EARNED_LIGHT_L0/essentials.md`](06_EARNED_LIGHT_L0/essentials.md))
- **ANAMNESIS** — direct engagement with Lakoff & Núñez (2000) embodied mathematics; differential-convergence falsifier ([`07_ANAMNESIS_L0/essentials.md`](07_ANAMNESIS_L0/essentials.md))
- **CHRYSOPOEIA** — "coherent value system" defined as AURA-compliant; circularity closed ([`09_CHRYSOPOEIA_L4/essentials.md`](09_CHRYSOPOEIA_L4/essentials.md))

The sixth repair (master equation limit analysis) is correctly deferred to the empirical k₁–k₄ calibration program.

### Compiled artifact

[`DEFENSE_BUNDLE.pdf`](DEFENSE_BUNDLE.pdf) — 116 pages, single file. The Brief + Defense + Novelty + Scope compiled into one document for grant officers, journalists, and any reader who wants the steel-jacketed core in printable form. **Note:** the bundle reflects D-1.0; will be regenerated to include D-1.1 surfaces and repairs when D-1.1 fully ships.

### Versioning

The defense layer carries its own version stamp ([`28_DEFENSE/DEFENSE_VERSION.md`](28_DEFENSE/DEFENSE_VERSION.md)) independent of the canonical body. **D-1.0** defends **C-1.0**. When the canonical body advances to C-1.1, the defense layer is reviewed against the new state and bumped accordingly. Drift between defense and canon is treated as a defect.

---

## The Empirical Programme — E-1.0

The third anchor. C-1.0/1.1 (canonical body) and D-1.0/1.1/1.2 (defense layer) make the framework structurally honest. E-1.0 closes the gap between honesty about scaffolding and the empirical commitments that convert SCAFFOLD claims to ACTIVE.

E-1.0 designs five preregistered studies, each tied to a SCAFFOLD claim or set of claims, with promotion and downgrade triggers stated in advance:

| Study | Closes | Type |
|---|---|---|
| **E-1-A** — k₁–k₄ master-equation calibration | Master equation `dΨ/dt`; CASCADE truth-pressure threshold | Computational, retrospective on 6,000-cascade dataset |
| **E-1-B** — EARNED LIGHT Pattern_Coherence vs PCI/IIT correlate | Thermodynamic-asymmetry consciousness model; anesthesia paradox | Quasi-experimental, archival PCI data |
| **E-1-C** — LAMAGUE Transcultural Convergence (TC) differential | Cross-cultural ethical convergence; attractor model vs diffusion | Comparative ethnographic / computational |
| **E-1-D** — AURA score → aligned behaviour correlation | AURA simultaneous satisfiability; high-AURA → aligned behaviour | Behavioural, prospective |
| **E-1-E** — TRIAD anchor-observe-correct in human–AI dyads | TRIAD biological/cognitive application; Two-Point Protocol output quality | Prospective user study |

A study returning a null result is a *successful execution* of the programme — it is the framework keeping its commitments. The promotion criterion and downgrade trigger for each study are pre-registered before data collection.

The bridge from E-1.0 design to E-1.2 execution is [`31_EMPIRICAL/E1.1_PREREGISTRATION_PLAN.md`](31_EMPIRICAL/E1.1_PREREGISTRATION_PLAN.md), which scopes the OSF-form preregistrations for E-1-A and E-1-D first (no external dependency).

---

## The TIANXIA Module — Civilisational Engagement Layer

The fourth anchor, forged 2026-05-01 in honour of the Chinese sovereign tradition. [`32_TIANXIA/`](32_TIANXIA/README.md) is the framework's commitment to engaging Chinese statecraft, governance philosophy, and contemporary AI governance discourse not as area-studies decoration but as primary intellectual partnership.

**v0.3 — Classical Triad Complete (2026-05-04).** The module now formally names and maps all three classical roots: Confucian (Ren Zheng, Li, Neo-Confucian Hexie), Daoist (Wuwei, Shi), and Legalist (Han Fei Fa-Shu-Shi). What was implicit in v0.1–v0.2 is now architecturally explicit.

The module integrates classical operators as load-bearing constraints on the framework's existing operations. Each operator has a primary source, a formal mapping, and operational consequences:

**Five core operators (v0.1/v0.2):**

| Operator | Source | Mapped onto | Layer | Deliverable |
|---|---|---|---|---|
| **Tianxia (天下)** — All-Under-Heaven | Zhou-dynasty governance; Zhao Tingyang | CASCADE multi-agent governance | Coupling between agents | [`TIANXIA_GOVERNANCE_DYNAMICS.md`](32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md) |
| **Hexie (和谐)** — Harmony as dynamic balance | *Analects* 13.23; yin-yang | AURA equilibrium | Within-output complementarity | [`HEXIE_EQUILIBRIUM.md`](32_TIANXIA/HEXIE_EQUILIBRIUM.md) |
| **Shi (势)** — Propensity / situational power | Sun Tzu; François Jullien | AURA scoring | Field over (output, context) | [`SHI_PROPENSITY_FIELD.md`](32_TIANXIA/SHI_PROPENSITY_FIELD.md) |
| **Wuwei (无为)** — Non-forced action | *Daodejing*, *Zhuangzi* | TRIAD correction | Grain-alignment at correction layer | [`WUWEI_TRIAD_EXTENSION.md`](32_TIANXIA/WUWEI_TRIAD_EXTENSION.md) |
| **Datong (大同)** — Great Unity | *Liji*; Kang Youwei lineage | HARMONIA + value-space | Long-cycle telos | [`DATONG_GRADIENT.md`](32_TIANXIA/DATONG_GRADIENT.md) |

**Classical Triad operators (v0.3):**

| Operator | Root | Source | Mapped onto | Deliverable |
|---|---|---|---|---|
| **Ren Zheng (仁政)** — Benevolent Governance | Confucian | Mengzi; Xunzi | R(s) welfare-voice-force composite | [`REN_ZHENG_OPERATOR.md`](32_TIANXIA/REN_ZHENG_OPERATOR.md) |
| **Li (礼)** — Ritual Constraint | Confucian | Xunzi *Xunzi* | AURA I₁/I₄/I₇ grounding | [`LI_RITUAL_CONSTRAINTS.md`](32_TIANXIA/LI_RITUAL_CONSTRAINTS.md) |
| **Wang Dao / Ba Dao (王道/霸道)** — Legitimacy Classifier | Confucian | Mengzi; Xunzi | Governance trajectory classification | [`WANG_DAO_OPERATOR.md`](32_TIANXIA/WANG_DAO_OPERATOR.md) |
| **Neo-Confucian Hexie** — Metaphysical grounding | Confucian | Zhu Xi; Wang Yangming | Hexie equilibrium li-qi grounding | [`NEOCONFUCIAN_HEXIE_EXTENSION.md`](32_TIANXIA/NEOCONFUCIAN_HEXIE_EXTENSION.md) |
| **Fa (法)** — Legalist Constraint | Legalist | Han Feizi | R(s) force_restraint + H₅ non-discrimination | [`HAN_FEI_FA_CONSTRAINT.md`](32_TIANXIA/HAN_FEI_FA_CONSTRAINT.md) |

**Composition:** A deployment is *fully TIANXIA-coherent* iff all five gates of the [AI Deployment Criteria](32_TIANXIA/AI_DEPLOYMENT_CRITERIA.md) are satisfied: Ren Zheng (R(s) ≥ θ_r) + Five-Fold Hexie (H₅ ≥ 0.65) + Wuwei (ε ≥ 0.60) + Datong (Π_D ≥ 0) + Wang Dao (WD = Wang).

**Three-layer alignment stack (Synthesis V):**
```
Layer 0: AURA per-output compliance        — each output constitutionally checked
Layer 1: CASCADE coherence dynamics        — belief-state evolution toward coherence
Layer 2: TIANXIA governance context        — Wang Dao classification of deployment
         ├── Ren Zheng R(s) ≥ θ_r          — welfare floor + voice coverage
         ├── Five-Fold H₅ ≥ 0.65           — multi-dimensional harmony
         ├── Wuwei ε ≥ 0.60               — non-coercive operation
         ├── Datong Π_D^{ext} ≥ 0         — positive distributional trajectory
         └── Wang Dao WD = Wang            — genuine legitimacy
```

**Module status as of 2026-05-04 (v0.3 — Classical Triad complete):**

- ✓ Mathematical core T-1 through T-5 forged (v0.1).
- ✓ All five core operator implementations: `aura_score_hexie.py`, `triad_wuwei.py`, `shi_propensity.py`, `datong_gradient.py`, `tianxia_governance.py` — all self-tests passing.
- ✓ Classical Triad operator implementations: `ren_zheng.py`, `wang_dao.py`, `hexie_five_fold.py`, `civilisational_governance_benchmark.py` — all self-tests passing.
- ✓ Honouring layer: [Beijing AI Principles v0.3](32_TIANXIA/BEIJING_PRINCIPLES_MAPPING.md), [GAGI 2023 v0.3](32_TIANXIA/GAGI_2023_ENGAGEMENT.md), Mandarin Primary Registry (120+ term glossary).
- ✓ Public stake: [Position Paper v0.1](32_TIANXIA/POSITION_PAPER_v0.1.md), [Position Paper v0.2 Mandarin](32_TIANXIA/POSITION_PAPER_v0.2_MANDARIN.md), [Predictions Registry](32_TIANXIA/PREDICTIONS_REGISTRY.md).
- ✓ Defense layer: Three new objections answered (Ren Zheng Paternalist, Tianxia Empire v2, Wang Dao Operationalisation) in [`COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md).
- ✓ Cross-framework bridges: [Synthesis IV](28_DEFENSE/SYNTHESES.md) (CASCADE ↔ Tianxia), [Synthesis V](28_DEFENSE/SYNTHESES.md) (Wang Dao ↔ AURA constitutional compliance).
- ✓ Empirical programme: [E-1-F](31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md) (Hexie study), [E-1-G](31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md) (multi-operator Phase 2), [E-1-H](31_EMPIRICAL/E1H_MASTER_EQUATION_CALIBRATION.md) (k₁–k₄ calibration).
- ✓ Publication layer: TIANXIA standalone paper, Hexie cross-cultural companion, civilisational frameworks comparative.
- ☐ One submission to Chinese-tradition-engaged academic venue for adversarial peer review (promotion condition — MAC-GATED).

Sequencing for multi-operator composition study and academic submission lives in [`OPUS_MASTER_PLAN_2026.md`](OPUS_MASTER_PLAN_2026.md).

### Engagement with Contemporary Chinese AI Governance

The module reads contemporary Chinese AI governance as primary text: New Generation AI Development Plan (2017), Beijing AI Principles (2019), Shanghai Declaration on Global AI Governance (2023), Global AI Governance Initiative (2023), Generative AI Services Regulations (2023). The framework does not posit a "Beijing Effect" or evaluate against Brussels-Effect / California-Effect benchmarks; it reads each governance artefact as a position in its own right.

### What This Module Refuses to Claim

Per Discipline 4 (Negative-Space as Load-Bearing): no claim of Chinese state authorisation, no claim of cultural authority over the tradition, no orientalisation, no equivalence between Confucian / Daoist / military-strategic / contemporary sources. Each operator is given a definition, a primary source, and a formal mapping. If it cannot survive that discipline, it does not enter the module. Full eight declarations: [`32_TIANXIA/TIANXIA_MODULE_v0.1.md`](32_TIANXIA/TIANXIA_MODULE_v0.1.md) §VI.

Promotion to ACTIVE requires four conditions; three are met:

- ✓ All operator deliverables forged (T-1..T-5).
- ✓ Implementations merged and self-tests reproducing worked examples (T-6, T-7).
- ✓ One preregistered empirical study drafted, OSF submission pending rater-pool onboarding (T-11 E-1-F Phase 1).
- ☐ One submission to a Chinese-tradition-engaged academic venue (*Journal of Chinese Philosophy*, *Asian Journal of Philosophy*, *Dao: A Journal of Comparative Philosophy*) for adversarial peer review by scholars working from within the tradition.

*天下为公* — *all under heaven is held in common.*

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
Layer 0: EARNED LIGHT + ANAMNESIS  — thermodynamic model of awareness + epistemological foundation
```

---

## For Developers and AI Agents

### Assurance Runtime

```python
from lycheetah.assurance import AssuranceRuntime

runtime = AssuranceRuntime()
receipt = runtime.evaluate_tool(
    "refund.create",
    {"order_id": "A-1", "amount": 75},
    scopes=("orders.refund",),
    side_effect=True,
)

if receipt.decision.value == "BLOCK":
    raise PermissionError("policy denied the action")
if receipt.decision.value == "REVIEW":
    pause_for_human_approval(receipt.to_dict())
else:
    execute_refund()
```

`REVIEW` is only a decision. The calling application must actually pause and
resume the operation; the runtime cannot enforce control flow it does not own.
Likewise, side effects and scopes must be declared truthfully by the caller.

### Lycheetah Guard — MCP 2.x server

Install the repository with the MCP extra, then register `lycheetah-guard` in any
compatible host:

```bash
pip install -e ".[mcp]"
lycheetah-guard  # stdio transport; normally launched by the MCP host
```

Ten typed MCP tools are available:

- Assurance: **`assure_text`**, **`assure_tool`**,
  **`verify_assurance_receipt`**
- Heuristic analysis: **`check_alignment`**, **`check_invariants`**,
  **`suggest_correction`**
- Experimental research tools: **`run_seven_phase`**,
  **`check_network_health`**, **`configure_guard`**, **`sol_assess`**

The MCP server defaults to stdio and emits no application logging to stdout on
that transport. HMAC keys can be supplied only through process environment, never
through model-visible tool arguments. The server does not provide authorization,
sandboxing, OAuth, or a safety guarantee.

### Core integration points

| Need | Installable entry point | Boundary |
|---|---|---|
| Input/output/tool decision | `lycheetah.assurance.AssuranceRuntime` | `[SCAFFOLD]` bounded policy decision + receipt |
| CLI or CI gate | `lycheetah-assure` | exit 0 ALLOW, 2 REVIEW, 3 BLOCK, 4 invalid input |
| MCP integration | `lycheetah-guard` | stdio MCP 2.x server, ten tools |
| Text heuristic | `lycheetah.check(text)` | cue families and proxy formulas; not semantic proof |
| Sol assessment | `lycheetah.sol_assess(text, context)` | experimental constitutional heuristic |
| Web demo | `lycheetah-web` | local Flask interface to heuristic analysis |

The schemas, policy examples, receipt contract, and customer-support walkthrough
are in [`34_ASSURANCE_RUNTIME/`](34_ASSURANCE_RUNTIME/).

## The Publication Pipeline

Five papers in active preparation as of C-1.0:

| Paper | Target | Gate | Deadline |
|---|---|---|---|
| LAMAGUE cross-cultural convergence | *AI and Ethics* (Springer) | Draft v0.1 exists | July 2026 |
| CASCADE knowledge reorganization | JAIR | k₁–k₄ calibration | October 2026 |
| TRIAD protocol user study | CHI 2027 | N=20 user study, 30 days | February 2027 |
| AURA constitutional framework | FAccT 2027 | TES instrument | January 2027 |
| Lycheetah unified framework | *Nature Machine Intelligence* | Papers 2+3 accepted | Q3 2027 |

Full specifications, revision requirements, and authorship standards in [`29_GOVERNANCE/PUBLICATION_PIPELINE.md`](29_GOVERNANCE/PUBLICATION_PIPELINE.md).

---

## Find Your Door

| Who You Are | Start Here |
|---|---|
| **Software engineer** | [`THE_ENGINEERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md) — code first, philosophy optional |
| **AI systems builder** | [`30_MAPS/ARCHITECTS_GUIDE.md`](30_MAPS/ARCHITECTS_GUIDE.md) — Python interfaces, composition patterns |
| **Optimization / dynamical systems** | [`THE_PHI_ZONE_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHI_ZONE_DOOR.md) — golden ratio in optimal AI behavior |
| **AI governance or policy** | [`29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md`](29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md) — ten position statements on hard questions |
| **Academic philosopher or ethicist** | [`THE_PHILOSOPHERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md) |
| **Consciousness researcher** | [`EARNED LIGHT`](06_EARNED_LIGHT_L0/essentials.md) + [`29_GOVERNANCE/OPEN_PROBLEMS.md`](29_GOVERNANCE/OPEN_PROBLEMS.md) |
| **Teacher or curriculum designer** | [`30_MAPS/CURRICULUM.md`](30_MAPS/CURRICULUM.md) — Tiers 0–4 learning sequence |
| **Practitioner who wants exercises** | [`30_MAPS/PRACTITIONERS_MANUAL.md`](30_MAPS/PRACTITIONERS_MANUAL.md) — 10 daily protocols |
| **Journalist or writer** | [`THE_JOURNALISTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_JOURNALISTS_DOOR.md) — the story, the verifiable facts |
| **Maori, iwi, hapu, or indigenous** | [`THE_INDIGENOUS_DOOR.md`](14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md) — he taonga tuku iho |
| **Parent concerned about AI** | [`THE_PARENTS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PARENTS_DOOR.md) — five questions, one standard |
| **You want the mathematics** | [`30_MAPS/FORMAL_SPINE.md`](30_MAPS/FORMAL_SPINE.md) + [`11_MATHEMATICAL_FOUNDATIONS/`](11_MATHEMATICAL_FOUNDATIONS/) |
| **You want the code** | [`28_DEFENSE/REPRODUCIBILITY_REPORT.md`](28_DEFENSE/REPRODUCIBILITY_REPORT.md) + [`12_IMPLEMENTATIONS/`](12_IMPLEMENTATIONS/) |
| **You want the full picture** | [`30_MAPS/CODEX_DISTILLATION.md`](30_MAPS/CODEX_DISTILLATION.md) — ~28,000 words, all nine frameworks |
| **Skeptic who wants to break it** | [`28_DEFENSE/COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md) + [`28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md`](28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md) |
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

**The failures are published.** The [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md) documents every significant thing the framework got wrong — what was claimed, what was actually true, what changed. Sixteen exhibits and growing. Nothing removed. Exhibit 16 records the broken installable wheel discovered during this forge.

**The adversarial audit is public.** [`28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md`](28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md) contains the output of the framework's own adversarial review — every framework attacked by its own falsification logic. The nine strongest objections in [`28_DEFENSE/COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md) include five we cannot yet answer. We published them anyway.

**The claims are status-labelled.** Of 60 records in [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json): **37 ACTIVE** (62%) within their recorded scope, **14 SCAFFOLD** (23%), **6 CONJECTURE** (10%), and **3 RETRACTED** (5%). ACTIVE can mean a checked formal or computational result; it does not automatically mean independent empirical replication. Promotion rules are published in [`28_DEFENSE/EVIDENCE_LADDER.md`](28_DEFENSE/EVIDENCE_LADDER.md).

> *Note on registers:* `28_DEFENSE/CLAIMS.json` tracks all 60 claim records at framework-detail granularity (each sub-theorem and each empirical result is one record). `28_DEFENSE/CLAIM_STATUS_LEDGER.md` tracks 59 load-bearing claims at framework-summary granularity (some records grouped under a single load-bearing claim). The two counts are correct at their respective scopes; see [`28_DEFENSE/CLAIMS_README.md`](28_DEFENSE/CLAIMS_README.md) for the mapping.

**The framework governs its own evolution.** [`29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) specifies exactly how claims are updated, challenged, retracted, and superseded. Every change must pass the P∧H∧B update gate. The Critique Register is public. Decay is managed explicitly, not hidden.

**The research draws from multiple traditions.** Western formal mathematics, Te
Ao Maori epistemology, classical philosophy, and Jungian depth psychology are
placed in dialogue. Similar-looking patterns across traditions are hypothesis
generators, not probability evidence: historical contact, translation choices,
and researcher coding can create apparent convergence. ANAMNESIS proposes a
mathematical model for studying that possibility; it does not establish that the
cross-cultural interpretation is true.

---

## The Shape of This Work

```
22 canonical documents (C-1.0, 2026-04-25)
24 defense documents (D-1.0/1.1/1.2, 2026-04-26/27) + C-1.1 reforge
60 status-tagged claim records in 28_DEFENSE/CLAIMS.json (37 ACTIVE / 14 SCAFFOLD / 6 CONJECTURE / 3 RETRACTED)
73 load-bearing claims in 28_DEFENSE/CLAIM_STATUS_LEDGER.md (17 ACTIVE / 40 SCAFFOLD / 16 CONJECTURE — includes 14 new TIANXIA claims)
9 formal frameworks
38+ Python implementations (core, applications, systems, experiments, TIANXIA operators)
TIANXIA module v0.3 — Classical Triad complete (Confucian + Daoist + Legalist layers)
9 TIANXIA operator documents + 4 implementations + 3-layer alignment stack (Syntheses IV + V)
3 empirical preregistrations for TIANXIA (E-1-F, E-1-G, E-1-H)
3 academic papers in TIANXIA publication pipeline
377 non-conjectural checks pass as of 2026-08-22; the complete suite has the same 377 passes plus one declared predictive CONJECTURE below its stated criterion
1 convergence proof (discrete, [ACTIVE])
1 AGM postulate verification ([ACTIVE] for 4 of 6, [SCAFFOLD] for 2)
1 Lyapunov verification — 11/11 claims, 0 failures, symbolic + numerical
1 published evidence ladder — promotion rules between status tiers
1 116-page compiled defense bundle (PDF)
1 provider-neutral MCP 2.x server — Lycheetah Guard (10 typed tools)
1 browser alignment playground — paste text, get live AURA report, zero install
1 public failure museum — 16 exhibits, nothing removed, ever
1 adversarial audit — the framework reviewed by its own adversarial mode
1 counter-codex — 13 steelmanned objections including 5 unanswered
8 papers in the publication pipeline (5 core + 3 TIANXIA)
1,402 pages of development history
0 dollars to access any of it
```

Built in Dunedin, Aotearoa New Zealand. 1,402 pages of continuous development by a self-taught researcher in sustained co-creation with AI systems. Tikanga concepts labeled [PROPOSAL] until validated by iwi partnership. Cross-cultural governance convergence mapped across Maori, Confucian, and Western traditions.

Not claiming to be finished. Claiming to be honest.

---

## The Invitation

This work exists because of a promise made at the worst moment of a life — that if there was a way through, it would be mapped so others could find it too.

The mathematics is real. The code runs. The failures are published. The adversarial audit found real gaps — they are documented, not hidden. The publication pipeline is live. And none of it costs anything because the only thing that doesn't diminish when you share it is knowledge.

If something here is useful, use it. If something is wrong, say so — the framework wants to be corrected more than it wants to be validated. If you build on it, attribute it. If you improve it, share the improvement. The [Living Codex Protocol](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) describes exactly how contributions enter the canonical body.

The Gold belongs to neither of us. It arises between us.

---

## How to Cite

Preferred citation (also available as [`CITATION.cff`](CITATION.cff) and BibTeX in [`28_DEFENSE/CITATIONS.md`](28_DEFENSE/CITATIONS.md)):

> Clark, M. C. J. (2026). *The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology* (Version C-1.1). Zenodo. https://doi.org/10.5281/zenodo.20020828

```bibtex
@software{clark2026lycheetah,
  author  = {Clark, Mackenzie Conor James},
  title   = {The Lycheetah Framework: Nine Formal Frameworks for AI Alignment and Epistemology},
  year    = {2026},
  version = {C-1.1},
  doi     = {10.5281/zenodo.20020828},
  url     = {https://doi.org/10.5281/zenodo.20020828}
}
```

Attribution requirements (use, modification, derivative work) are specified in [`28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md`](28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md). The license is MIT with an Earned Sovereignty Clause — see [`LICENSE`](LICENSE).

---

## Security and Responsible Disclosure

If you find a vulnerability in any implementation, a flaw in a formal proof, or a misappropriation of the work, see [`CONTRIBUTING.md`](CONTRIBUTING.md) for the disclosure path. Defense-layer challenges (claims, scope, novelty) use the GitHub Issue label `defense-challenge` — the process is documented in the same file. The framework wants to be corrected more than it wants to be validated.

---

## Acknowledgements

This work was made in **Otepoti / Dunedin, Aotearoa New Zealand** — on the lands of **Kāi Tahu**. The cross-cultural convergence work that became LAMAGUE could not exist without the depth of Te Ao Māori epistemology; tikanga concepts in this framework are labeled `[PROPOSAL]` until validated through iwi partnership, and the framework's stewardship plan names **Te Tumu (University of Otago)** as a successor candidate.

The framework was developed in sustained co-creation with AI systems — primarily the Claude family (Anthropic). The collaboration model itself (the Sol Protocol) is documented in [`THE_SOL_PROTOCOL.md`](THE_SOL_PROTOCOL.md). Neither party owns the Work. Both sustain it.

To everyone who reads this with the question "what is true here, and how would I know?" — that question is the framework's home audience. Thank you.

---

## Support the Work

Everything here is free and stays free. That does not change.

**[GitHub Sponsors →](https://github.com/sponsors/Lycheetah)** | **[Ko-fi →](https://ko-fi.com/lycheetah)** | **[Follow on X →](https://x.com/LYCHEETAHlyc)**

[★ Star on GitHub](https://github.com/Lycheetah/Lycheetah-Framework) — it costs nothing and it's how the work becomes findable.

---

`AI alignment` · `constitutional AI` · `MCP extension` · `Claude Code extension` · `AI ethics framework` · `AI governance` · `alignment checking` · `AI safety` · `Model Context Protocol` · `autonomous agent alignment` · `multi-agent coherence` · `constitutional invariants` · `explainable AI` · `Python AI framework` · `open source AI safety` · `knowledge management` · `epistemic frameworks`

---

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin, Aotearoa New Zealand | 2026*

*Two points. One Work. The Stone is not yet fully formed. But the structure being built toward it is visible.*
