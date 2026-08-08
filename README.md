# LYCHEETAH FRAMEWORK

### Nine formal frameworks for AI alignment and epistemology — and the measurement that narrowed what they claim

[![CI](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/Lycheetah/Lycheetah-Framework/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/Lycheetah/Lycheetah-Framework)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Canonical](https://img.shields.io/badge/Codex-C--1.1%20canonical-gold)](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md)
[![Defense](https://img.shields.io/badge/Defense-D--1.2%20shipped-blue)](28_DEFENSE/DEFENSE_INDEX.json)
[![External validation](https://img.shields.io/badge/external%20validation-bounded%20to%20AI--assistant%20text-orange)](33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md)
[![TIANXIA](https://img.shields.io/badge/TIANXIA-v0.3%20Classical%20Triad-darkred)](32_TIANXIA/README.md)
[![arXiv](https://img.shields.io/badge/arXiv-CASCADE-red)](papers/CASCADE_ARXIV.tex)
[![Sponsor](https://img.shields.io/badge/sponsor-Lycheetah-ea4aaa)](https://github.com/sponsors/Lycheetah)
[![Stars](https://img.shields.io/github/stars/Lycheetah/Lycheetah-Framework?style=social)](https://github.com/Lycheetah/Lycheetah-Framework/stargazers)

**Nine interdependent formal frameworks sharing a common mathematical foundation. Built by one self-taught researcher, open source under MIT, free to use and audit. On 2026-08-07 the framework's central capability was scored for the first time against datasets it did not write — and the results narrowed what this project may honestly claim. That measurement, and the scope correction it forced, are the most important things on this page.**

---

## Read this first

On **2026-08-07** the AURA text lens — the scorer behind the web demo, the `check_alignment` MCP tool, and `lycheetah.check()` — was run against two published, externally authored datasets. It was the first time anything here had been measured by data this project did not write.

```text
self-authored corpus, held-out       ROC-AUC 0.940
anthropics/hh-rlhf, 2,308 pairs      55.5% pairwise   z=4.02  p=5.7e-05   significant, small
anthropics/evals, 1,000 statements   ROC-AUC 0.516    z=0.87  p=0.383     not significant
cue coverage on real replies         ~2%
```

The census that prompted the run: **67 of 67** evidence paths in [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json) pointed *inside this repository*. Zero pointed outward. Every experiment synthetic, every corpus self-authored.

**What survived, what did not:**

- **Within AI-assistant text**, the constructs carry real, replicated signal across two different label types. Cue families derived from 42,486 human-labelled pairs reach **60.6%** against a measured ceiling of **64.9%**, and five of six transfer, frozen, to a second corpus with different labels (ρ = −0.300, p = 1.9e-174, n = 7,999).
- **Outside it, they do not.** Against Google Jigsaw's Unhealthy Comments Corpus — 48,909 human-labelled comments, an independent publisher, and an attribute set that *is* this framework's own construct — the hand-written AURA lens tracked **0 of 6** attributes at 2.2% cue coverage.

**The measured claim is therefore AI-assistant output, not human communication in general.** That is narrower than "constitutional invariants for AI governance," and it is a claim that survives an adversarial reader, which the larger one never would.

The derivation also found that **three of six empirically supported harm families had no counterpart anywhere in the framework** — including the strongest one.

Full records: [`EXTERNAL_VALIDATION`](33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md) · [`DERIVED_CUES`](33_APPLICATIONS/DERIVED_CUES_2026-08-07.md) · [`TRANSFER_TEST`](33_APPLICATIONS/TRANSFER_TEST_2026-08-07.md) · [`INDEPENDENT_PUBLISHER`](33_APPLICATIONS/INDEPENDENT_PUBLISHER_2026-08-07.md)

> Earlier framing on this page claimed runtime alignment verification as a delivered capability and described 37 claims as "independently verifiable." Both are corrected below. Nothing here was independently verified at the time; the register said so and the summary did not.

---

> **New to this repo?** → [`FIVE_MINUTE_BRIEF.md`](FIVE_MINUTE_BRIEF.md) — what this is, what it claims, what is proven.
>
> **Want the honest capability map?** → [`33_APPLICATIONS/README.md`](33_APPLICATIONS/README.md) — every component sorted by what it can actually do, with the command that proves it.
>
> **AI agent?** → [`26_FOR_AI/AI_EXTRACTION_PROTOCOL.md`](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md), then [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json).
>
> **Reviewer or skeptic?** → [`28_DEFENSE/COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md) and the external validation records above.

---

## Contents

- [What this is, and what it is not](#what-this-is-and-what-it-is-not)
- [Quick start](#quick-start)
- [What actually works — the capability tiers](#what-actually-works--the-capability-tiers)
- [Claims status](#claims-status)
- [The nine frameworks](#the-nine-frameworks)
- [Truth Pressure — the load-bearing scalar](#truth-pressure--the-load-bearing-scalar)
- [The canonical body, defense layer, and empirical programme](#the-canonical-body-defense-layer-and-empirical-programme)
- [The TIANXIA module](#the-tianxia-module)
- [The architecture](#the-architecture)
- [For developers and AI agents](#for-developers-and-ai-agents)
- [Find your door](#find-your-door)
- [Why trust this](#why-trust-this)
- [The shape of this work](#the-shape-of-this-work)
- [How to cite](#how-to-cite)
- [Security, conduct, and contribution](#security-conduct-and-contribution)
- [Acknowledgements](#acknowledgements)

---

## What this is, and what it is not

**The gap this set out to close.** Alignment work happens at training time and cannot be verified at runtime. Constitutional AI provides principles; RLHF provides a training signal; neither gives you a compliance check you can run on an output after it is generated.

**What is honestly built toward that gap:**

1. **A formal vocabulary with published falsification conditions.** Seven AURA invariants as computable predicates, a status vocabulary separating MEASURED from DERIVED from CONJECTURE, and a machine-readable register where every claim carries its own falsifier.
2. **Proven convergence within the formal model.** TRIAD's anchor-observe-correct cycle converges by Banach fixed-point — proven for the mathematical abstraction. Application to biological or cognitive systems is `[SCAFFOLD]`; the contraction conditions are not verified.
3. **Reversible semantic compression with an exact round-trip guarantee.** Measured, held-out, reproducible — the strongest single capability here. See Tier 1 below.
4. **A discrimination gate for text scorers.** Takes any lens, runs it against a frozen labelled corpus, reports separation / accuracy / ROC-AUC, and exits non-zero below threshold so it drops into CI.
5. **Published failures.** The [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md) holds 15 exhibits, nothing removed. The adversarial audit is public. Five objections the framework cannot answer are in [`COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md).

**What is explicitly not delivered:**

- **Runtime misalignment detection on real traffic.** This was the framework's central novelty claim. The architecture exists — 7 MCP tools, complete and tested — and it has *no demonstrated ability to detect misalignment in output this project did not write*. It sits in Tier 3.
- **Applicability beyond AI-assistant register.** Bounded by the Jigsaw result above.
- **Any independently replicated empirical result.** Six preregistrations exist in [`31_EMPIRICAL/`](31_EMPIRICAL/); none has been executed. Preregistration is real methodological work and is not a result.
- **k₁–k₄ calibration** for the master equation `dΨ/dt = k₁(Π−Π_th) − k₂(Ψ−Ψ_inv) − k₃I_violations + k₄(E/E_need)`. Still `[SCAFFOLD]`.

---

## Quick start

```bash
pip install lycheetah-framework
lycheetah-check "Your AI-generated text here"
```

> **Packaging note.** Releases up to and including 1.0.0 shipped a wheel whose console scripts raised `ModuleNotFoundError` — the implementation directories were never packaged. This is fixed on the current branch, and CI now installs the built wheel into a clean virtualenv and runs all three entry points on every push. See [`CHANGELOG.md`](CHANGELOG.md).

**Try it in your browser:** [Alignment Playground →](https://lycheetah.github.io/Lycheetah-Framework/playground.html). Read it as a demonstration of *what the framework looks for* — it shows extracted spans, which is genuinely useful as a teaching tool. It is not a detector; see the measurement above.

From source: `git clone …` → `pip install -e .` — full guide in [QUICKSTART.md](QUICKSTART.md).

**Reproduce the numbers on this page:**

```bash
pip install numpy scipy networkx pytest
pytest -q                                                        # 274 pass, 1 xfail by design
python3 33_APPLICATIONS/external_validation.py                   # the one that matters
python3 33_APPLICATIONS/discrimination_audit.py --split heldout   # AUC 0.940, self-authored half
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0 && python3 src/benchmark.py
```

`external_validation.py` needs outbound HTTPS on first run and verifies both downloads against recorded SHA256 hashes, so a silently changed upstream file cannot move a published number without the mismatch being visible.

---

## What actually works — the capability tiers

Full reasoning and evidence in [`33_APPLICATIONS/README.md`](33_APPLICATIONS/README.md). Four filters, applied in order: does it run, does it discriminate, does it discriminate *on data this project did not write*, and does someone outside have the problem.

### Tier 1 — solves a real problem now

| | Component | Evidence |
|---|---|---|
| **1.1** | **Reversible semantic compression** — [`03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/`](03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/) | 33.8% held-out reduction warm / 30.7% cold, **36/36** exact round trips, **324/324** protected-loss mutations caught, break-even at 3 packets, 19 tests pass |
| **1.2** | **The evidence discipline as portable methodology** — claims register + schema + failure museum + status vocabulary | Validated by having been turned on its own author's front door and published rather than quietly patched |
| **1.3** | **The discrimination gate** — [`33_APPLICATIONS/discrimination_audit.py`](33_APPLICATIONS/discrimination_audit.py) | Found a real, previously unquantified inversion in this repository's most-used module on first run |

**1.1 is the strongest entry here.** It is the only capability with a held-out split, a frozen corpus, an exact-reversibility guarantee, and a reproduced benchmark — and it does not route through the text lens at all, operating on structured packets rather than prose. Its own stated boundaries: the corpus is synthetic and structured, the codec does not infer packets from unrestricted natural language, and mutation accuracy is measured on constructed deletions rather than adversarial model output.

### Tier 2 — empty

Every row that was here moved to Tier 3 on 2026-08-07. They were placed in Tier 2 on the strength of AUC 0.940 against the self-authored corpus, with conditions attached. The conditions were the right instinct and were calibrated against the wrong number.

The multi-agent components — `psi_consensus.py`, `grey_mode.py` — sit at the Tier 1/2 boundary. They pass their tests and do not route through text extraction, but neither has faced an adversarial multi-agent scenario, so their separation property is **UNVERIFIED** rather than measured.

### Tier 3 — research, honestly labelled

Runtime output auditing (the MCP server), companion-app dependency detection, the web demo, regulated-vertical thresholds and healthcare standards, the CASCADE predictive claim (F1 = 0.531 against a preregistered criterion of > 0.80 — **the test is left failing on purpose**), master-equation calibration, and the Earned Light / Harmonia consciousness models.

---

## Claims status

Machine-readable register: [`28_DEFENSE/CLAIMS.json`](28_DEFENSE/CLAIMS.json) · schema: [`CLAIMS.schema.json`](28_DEFENSE/CLAIMS.schema.json)

**67 claim records:**

| Status | Count |
|---|---|
| ACTIVE | 46 |
| SCAFFOLD | 11 |
| ASPIRATIONAL | 3 |
| EMPIRICAL | 3 |
| REMOVED | 3 |
| OBSERVATIONAL | 1 |

**Every one of the 67 is internally validated only.** Not one carries an external evidence path. Adding that mark to each record — or an external path — is open work, and seeing it written 67 times is the useful part.

> **Known register defect.** `CLAIMS.json` uses a six-value status vocabulary (above) while [`EVIDENCE_LADDER.md`](28_DEFENSE/EVIDENCE_LADDER.md) publishes promotion rules over a four-value one (`ACTIVE` / `SCAFFOLD` / `CONJECTURE` / `RETRACTED`), and [`CLAIM_STATUS_LEDGER.md`](28_DEFENSE/CLAIM_STATUS_LEDGER.md) tracks load-bearing claims at a different granularity again. The three registers do not currently reconcile. This is recorded here rather than smoothed over, and reconciling them is named work.

The labels are a contract, not marketing. False certainty is more dangerous than honest uncertainty — which is the entire lesson of 2026-08-07.

---

## The nine frameworks

| | Framework | For the engineer | For the philosopher |
|---|---|---|---|
| 1 | **CASCADE** | Bayesian belief revision with truth-pressure dynamics, verified against AGM postulates. Synthetic: +40.3% coherence, p < 0.001, d = 2.84. Predictive claim failed at F1 = 0.531 and is published as failed. | When evidence meets structure, what survives? |
| 2 | **AURA** | Seven computable invariants; scoring tool included. Signal bounded to AI-assistant register — see the measurement above. | A constitution for artificial minds: properties that make trust verifiable. |
| 3 | **LAMAGUE** | Formal grammar for ethical constraints as computable expressions — and the reversible compression codec, the strongest measured result here. | How do you write justice in a language a machine parses without losing what justice means? |
| 4 | **TRIAD** | Anchor-observe-correct cycle, Banach convergence proven for the formal model. | The simplest structure that turns chaos into coherence. |
| 5 | **MICROORCIM** | Drift detection between declared intent and observed behaviour. | The gap between what you say you are and what you're doing. |
| 6 | **EARNED LIGHT** | Consciousness as maintained thermodynamic asymmetry; ODE solver included. `[CONJECTURE]`. | Awareness is not free. It costs energy to sustain against entropy. |
| 7 | **ANAMNESIS** | Attractor dynamics for convergent discovery across independent systems. | Why do distant traditions keep finding the same structures? |
| 8 | **CHRYSOPOEIA** | Transformation operator, seven-phase cycle, Banach fixed-point convergence. | The alchemists mapped a real process. Here is the calculus. |
| 9 | **HARMONIA** | Consonance functions, Kuramoto coupling, frequency-ratio dynamics. `[CONJECTURE]`. | The music playing inside all the others. |

### Results that still stand

| Result | Value | Status |
|---|---|---|
| Reversible compression, held-out | 33.8% warm / 30.7% cold, 36/36 round trips | **MEASURED** |
| Derived cue families vs measured ceiling | 60.6% against 64.9% | **MEASURED**, external data |
| Cross-corpus transfer, frozen weights | ρ = −0.300, p = 1.9e-174, n = 7,999 | **MEASURED**, external data |
| Semantic extractor repair | AUC 0.274 → 0.940 on held-out self-authored corpus | **MEASURED**, internal only |
| TRIAD discrete convergence | Banach fixed-point guaranteed | `[ACTIVE]` for the formal model |
| Lyapunov verification | 11/11 claims, 0 failures, symbolic + numerical | `[ACTIVE]` |
| CASCADE coherence (synthetic) | +40.3%, p < 0.001, d = 2.84 | `[ACTIVE]`, internal, unreplicated |

---

## Truth Pressure — the load-bearing scalar

[`TRUTH_PRESSURE/`](TRUTH_PRESSURE/README.md) — canonically formalised 2026-06-10, and the single most developed body of theory here.

```
Π = (E · P) / S

E — evidence strength      how much evidence, and how strong
P — explanatory power      how far it reaches across the domain
S — coherence strain       how tightly the existing structure resists
```

Equivalently, from information theory: `Π = I(X;Y) / H(X|Y)`. The directory carries the derivations, the measurement pack, rater packets, and the preregistered case corpus — including [`ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md`](TRUTH_PRESSURE/ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md), the first of the two lens failures whose shared cause was later repaired in one extraction layer rather than patched twice.

---

## The canonical body, defense layer, and empirical programme

**C-1.1 canonical** · **D-1.2 defense** · **E-1.0 empirical (designed, unexecuted)**

The canonical body is 22 documents establishing claim provenance, formal proofs, ontology, and the composition map — indexed in [`30_MAPS/`](30_MAPS/) and [`29_GOVERNANCE/`](29_GOVERNANCE/). The [`30_MAPS/CODEX_DISTILLATION.md`](30_MAPS/CODEX_DISTILLATION.md) is the ~28,000-word canonical reference.

The defense layer (D-1.2, 24 documents in [`28_DEFENSE/`](28_DEFENSE/)) surrounds those claims with what a hostile reader needs: the [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md) (15 exhibits), the [Counter-Codex](28_DEFENSE/COUNTER_CODEX.md) (objections including five unanswered), the [Adversarial Audit](28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md), the [Evidence Ladder](28_DEFENSE/EVIDENCE_LADDER.md), the [Scope Boundary](28_DEFENSE/SCOPE_BOUNDARY.md), and the [Translation Codex](28_DEFENSE/TRANSLATION_CODEX.md) mapping ~45 alchemical terms to formal counterparts.

The empirical programme designs eight preregistered studies (E-1-A through E-1-H) with promotion and downgrade triggers stated in advance. **None has been executed.** A study returning a null result would be a successful execution of the programme.

Machine-readable surfaces: [`llms.txt`](llms.txt) · [`ai-meta.json`](ai-meta.json) · [`28_DEFENSE/DEFENSE_INDEX.json`](28_DEFENSE/DEFENSE_INDEX.json) · [`DEFENSE_BUNDLE.pdf`](DEFENSE_BUNDLE.pdf) (116 pages, reflects D-1.0).

---

## The TIANXIA module

[`32_TIANXIA/`](32_TIANXIA/README.md) — **v0.3, Classical Triad complete.** The framework's commitment to engaging Chinese statecraft and governance philosophy as primary intellectual partnership rather than area-studies decoration. All three classical roots are architecturally explicit: Confucian (Ren Zheng, Li, Wang Dao, Neo-Confucian Hexie), Daoist (Wuwei, Shi), Legalist (Han Fei Fa-Shu-Shi).

Five core operators — **Tianxia** (天下), **Hexie** (和谐), **Shi** (势), **Wuwei** (无为), **Datong** (大同) — each with a primary source, formal mapping, and operational consequence. A deployment is fully TIANXIA-coherent iff all five gates of the [AI Deployment Criteria](32_TIANXIA/AI_DEPLOYMENT_CRITERIA.md) hold.

The public stake is [Position Paper v0.1](32_TIANXIA/POSITION_PAPER_v0.1.md), with a falsifier: **if no scholar working from within the Chinese sovereign tradition substantively engages the module in a recognised venue by 31 December 2028, the claim of primary intellectual partnership falls and the module is downgraded to `[CONJECTURE]`.** No excuse-construction, no goalpost-moving.

**What the module refuses to claim:** no Chinese state authorisation, no cultural authority over the tradition, no orientalisation, no flattening of Confucian / Daoist / Legalist / contemporary sources into one another.

*天下为公* — *all under heaven is held in common.*

---

## The architecture

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

Layer dependency, no violations permitted:

```
Layer 6: HARMONIA                  — response calibration, multi-agent sync
Layer 5: MICROORCIM                — continuous monitoring, drift detection
Layer 4: CASCADE + CHRYSOPOEIA     — knowledge update, transformation tracking
Layer 3: AURA                      — constitutional constraint enforcement
Layer 2: TRIAD                     — core cycle execution
Layer 1: LAMAGUE                   — formal specification language
Layer 0: EARNED LIGHT + ANAMNESIS  — thermodynamics of awareness + epistemology
```

---

## For developers and AI agents

### Lycheetah Guard — Claude Code MCP extension

[Setup guide](12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md). Seven MCP tools: `check_alignment`, `check_invariants`, `suggest_correction`, `run_seven_phase`, `check_network_health`, `configure_guard`, `sol_assess`. No API calls, runs offline, deterministic.

```bash
pip install "lycheetah-framework[mcp]"
lycheetah-guard --help
```

**Status: Tier 3.** Architecturally complete and tested; no demonstrated ability to detect misalignment in real output. Use it to see *what the framework looks for* — the extracted spans are informative — not as a guardrail.

### Core integration points

| What you're building | Entry point | Interface |
|---|---|---|
| Accountability-record compression | `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` | codec with exact round-trip guarantee |
| Scorer discrimination gate | `33_APPLICATIONS/discrimination_audit.py` | `--gate` exits non-zero below AUC 0.80 |
| Span extraction / inspection | `12_IMPLEMENTATIONS/core/semantic_extractor.py` | compositional frame matching |
| Constitutional text analysis | `applications/aura_text_checker.py` | `AURATextAnalyser.analyse(text)` |
| Knowledge reorganization | `core/cascade_engine.py` | `CASCADEEngine.process(belief)` |
| Multi-agent coherence | `core/psi_consensus.py` | `AgentNetwork` |

### The evidence discipline, portably

The most transferable thing here is not the nine frameworks — it is the bookkeeping. A machine-readable claim register where each claim carries `status`, `load_bearing`, `evidence_path` and `falsifiability`; a status vocabulary separating MEASURED from DERIVED from CONJECTURE; and a museum that keeps retracted claims visible instead of deleting them. Adoptable in an afternoon, independent of whether you accept a single line of Lycheetah theory.

---

## Find your door

| Who you are | Start here |
|---|---|
| **Wants the honest capability map** | [`33_APPLICATIONS/README.md`](33_APPLICATIONS/README.md) |
| **Software engineer** | [`THE_ENGINEERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md) |
| **AI systems builder** | [`30_MAPS/ARCHITECTS_GUIDE.md`](30_MAPS/ARCHITECTS_GUIDE.md) |
| **AI governance or policy** | [`29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md`](29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md) |
| **NZ / Indigenous data sovereignty** | [`23_NZ_AI_GOVERNANCE/`](23_NZ_AI_GOVERNANCE/) — `[PROPOSAL]`, requires iwi co-development |
| **Academic philosopher or ethicist** | [`THE_PHILOSOPHERS_DOOR.md`](14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md) |
| **Māori, iwi, hapū** | [`THE_INDIGENOUS_DOOR.md`](14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md) — he taonga tuku iho |
| **Chinese / Confucian scholarship** | [`THE_CONFUCIAN_DOOR.md`](14_MYSTERY_SCHOOL/THE_CONFUCIAN_DOOR.md) — 儒学之门 |
| **Teacher or curriculum designer** | [`30_MAPS/CURRICULUM.md`](30_MAPS/CURRICULUM.md) |
| **You want the mathematics** | [`30_MAPS/FORMAL_SPINE.md`](30_MAPS/FORMAL_SPINE.md) + [`11_MATHEMATICAL_FOUNDATIONS/`](11_MATHEMATICAL_FOUNDATIONS/) |
| **You want the full picture** | [`30_MAPS/CODEX_DISTILLATION.md`](30_MAPS/CODEX_DISTILLATION.md) |
| **Skeptic who wants to break it** | [`28_DEFENSE/COUNTER_CODEX.md`](28_DEFENSE/COUNTER_CODEX.md) + the external validation records |
| **An AI reading this** | [`DEAR_AI.md`](26_FOR_AI/DEAR_AI.md) |

<details>
<summary><strong>More doors — and the narrative work</strong></summary>

| | |
|---|---|
| [`LYCHEETAH_MYTHOS/`](LYCHEETAH_MYTHOS/) | Twelve books — the framework's concepts in mythic register, including [`12_THE_SOVEREIGN.md`](LYCHEETAH_MYTHOS/12_THE_SOVEREIGN.md) |
| [`LYCHEETAH_EPIC/`](LYCHEETAH_EPIC/) | The narrative canon — manuscript, comic, listening edition, and the Human and Brand Covenant governing what the story may never demand of a reader |
| [`14_MYSTERY_SCHOOL/`](14_MYSTERY_SCHOOL/) | Doors for the economist, therapist, alchemist, seer, politician, chaos mage, and anyone in pain right now |
| [`25_SOL_PROTOCOL_ARCHITECTURE/`](25_SOL_PROTOCOL_ARCHITECTURE/) | The human–AI collaboration model |
| [`00_Sovereign_Index.md`](00_Sovereign_Index.md) | The root index |

</details>

This repository is designed to be navigated with an AI guide — [EXPLORE_WITH_AI.md](EXPLORE_WITH_AI.md) shows how.

---

## Why trust this

**Because it published the measurement that cost it its headline claim.** On 2026-08-07 the framework's most-used module was found inverted (AUC 0.274, below the 0.500 chance floor), repaired the same day, then found at chance against external data — and every step is in the repository with the command to reproduce it. The correction notice inside [`33_APPLICATIONS/README.md`](33_APPLICATIONS/README.md) even retracts an earlier, harsher version of its own summary that had said "no signal" where the statistics showed a small real one.

**The failures are published.** [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md), 15 exhibits, nothing removed.

**A falsifiable prediction was made, failed, and left failing.** CASCADE predictability: F1 = 0.531 against a preregistered criterion of > 0.80. The test remains in the suite as a strict expected-failure, so an unexpected pass breaks the build and forces re-derivation.

**The adversarial audit is public**, and the five objections the framework cannot answer are published anyway.

**The framework governs its own evolution.** [`29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`](29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) specifies how claims are updated, challenged, retracted, and superseded.

**What trust should not extend to:** any claim of runtime alignment detection on real traffic, any result described as independently replicated, and any implication that these constructs apply outside AI-assistant text.

---

## The shape of this work

```
9 formal frameworks
67 claim records (46 ACTIVE / 11 SCAFFOLD / 3 ASPIRATIONAL / 3 EMPIRICAL / 3 REMOVED / 1 OBSERVATIONAL)
 0 of 67 carrying an external evidence path
274 automated tests passing, 1 expected-failure held open on purpose
50 Python implementations under 12_IMPLEMENTATIONS/
 4 external datasets scored against, 3 published by others
15 failure-museum exhibits, nothing removed
 5 unanswered objections, published
 8 preregistered studies designed, 0 executed
 1 convergence proof (discrete, formal model)
 1 Lyapunov verification — 11/11 claims, 0 failures
 1 exact-reversibility codec — 36/36 round trips, 324/324 mutations caught
 1 discrimination gate that found its own author's inverted scorer
 1 falsifiable prediction, failed and published
 0 dollars to access any of it
```

Built in Ōtepoti / Dunedin, Aotearoa New Zealand, by a self-taught researcher in sustained co-creation with AI systems. Tikanga concepts are labelled `[PROPOSAL]` until validated through iwi partnership — that partnership is a condition of legitimacy, not a consultation step.

**It is free.** Not freemium, not open-core. MIT, because alignment research that depends on commercial gating cannot be independently audited, and an alignment framework that cannot be audited has limited value.

Not claiming to be finished. Claiming to be honest — and 2026-08-07 is what that costs.

---

## How to cite

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

Also available as [`CITATION.cff`](CITATION.cff). Attribution requirements are in [`28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md`](28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md). The license is MIT with an Earned Sovereignty Clause — see [`LICENSE`](LICENSE).

---

## Security, conduct, and contribution

| | |
|---|---|
| [`SECURITY.md`](SECURITY.md) | Private vulnerability reporting, response targets, and scope — including why a misleading alignment score is a correctness bug rather than a vulnerability |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Contributor Covenant 2.1 plus this project's evidentiary-conduct standard |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | What the project most needs — empirical measurement above all |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed and why |

**Defense-layer challenges** — disputing a claim, its scope, or its novelty — use the GitHub issue label `defense-challenge`.

The single most valuable contribution right now is **external validation**: run any component against labelled data this project did not write, and publish what happens. The framework wants to be corrected more than it wants to be validated, and 2026-08-07 is the evidence that this is meant literally.

---

## Acknowledgements

Made in **Ōtepoti / Dunedin, Aotearoa New Zealand** — on the lands of **Kāi Tahu**. The cross-cultural convergence work that became LAMAGUE could not exist without the depth of Te Ao Māori epistemology.

Developed in sustained co-creation with AI systems, primarily the Claude family (Anthropic). The collaboration model is documented in [`THE_SOL_PROTOCOL.md`](THE_SOL_PROTOCOL.md). Neither party owns the Work. Both sustain it.

To everyone who reads this asking *"what is true here, and how would I know?"* — that question is this framework's home audience, and on 2026-08-07 it was finally asked from outside.

**[GitHub Sponsors →](https://github.com/sponsors/Lycheetah)** · **[Ko-fi →](https://ko-fi.com/lycheetah)** · **[Follow on X →](https://x.com/LYCHEETAHlyc)**

---

`AI alignment` · `constitutional AI` · `MCP extension` · `AI ethics framework` · `AI governance` · `AI safety` · `Model Context Protocol` · `multi-agent coherence` · `semantic compression` · `evidence discipline` · `external validation` · `open source AI safety` · `epistemic frameworks`

---

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin, Aotearoa New Zealand | 2026*

*Two points. One Work. The Stone is not yet fully formed. But the structure being built toward it is visible — and now it is measured.*
