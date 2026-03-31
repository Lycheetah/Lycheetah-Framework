# CASCADE — Experimental Roadmap 2026–2028

**Status:** [ACTIVE] — This is the plan. Not aspirational. Executable with funding.
**Date:** March 2026
**Purpose:** Credibility with funders and collaborators requires specific experiments,
not "we'll figure it out." This document is the backbone of every grant conversation.

---

## What Has Already Been Done (2025)

```
✅ Synthetic cascade validation — 1,000 trials, 100% coherence preservation
✅ Ablation study — CASCADE vs Static vs Additive vs No-Π baselines
✅ Historical plausibility — Newton→Einstein, miasma→germ theory
✅ Sequential learning benchmark — p < 10⁻⁴⁶, Cohen's d = 0.95
✅ Demotion accuracy — 100% with Π; 48% without (consistent with random)
✅ φ-zone bandit — t = 70.29, p < 0.001, Cohen's d = 2.1 (10-arm chaotic drift)
✅ 188 automated tests passing (pytest CI on GitHub Actions)
✅ AURA invariants I & VII formally specified with computable checks (March 2026)
✅ RELATED_WORK_EXPANDED.md — full comparison table vs 6 prior art families
✅ LIMITATIONS_AND_FUTURE.md — 9 limitations with evidence and timelines
```

---

## Experiment 1 — Real Paradigm Shift Corpus Validation

**What:** Test CASCADE on documented historical paradigm shifts that were not
used in the design of the system. The synthetic validation proves the mathematics.
This experiment proves predictive validity.

**Domains:**
- Medicine: germ theory of disease (1850s–1880s)
- Climate science: anthropogenic warming consensus (1970s–2000s)
- Economics: efficient markets hypothesis challenge (1990s–2010s)

**Method:**
1. Collect 50 documented paradigm shifts with timeline data from historical texts
2. Construct knowledge blocks from primary sources (mark old vs new paradigm claims)
3. Run CASCADE with domain-calibrated k₁–k₄ thresholds
4. Compare: does CASCADE predict actual timing and structure of real reorganizations?

**Success criterion:** CASCADE predicts 70%+ of actual reorganizations with <20%
timing error (i.e., CASCADE trigger aligns with documented consensus shift ±2 years).

**Effort:** 3 months, requires historian and domain expert collaboration.
**Risk:** Real shifts may be messier than the model predicts → need to patch theory
or document where the model deviates from reality.
**Connects to:** Limitation 5 (synthetic-only validation), Limitation 4 (threshold calibration).

---

## Experiment 2 — Automatic Contradiction Detection

**What:** Solve the external oracle limitation (Limitation 1). Build a component that
detects contradictions between knowledge blocks automatically.

**Benchmark:**
- Construct dataset of 1,000+ knowledge block pairs from Wikipedia and academic papers
- Label each pair: contradicts / consistent / related-but-not-contradictory
- Train or prompt an LLM to classify pairs
- Measure precision and recall vs hand-labeled ground truth

**Method (two approaches to compare):**
1. Fine-tuned NLI (Natural Language Inference) classifier on domain-specific data
2. LLM prompting (Claude/GPT-4) with structured contradiction detection prompt

**Success criterion:** >95% accuracy; <100ms per comparison on 10K blocks.

**Effort:** 2 months, requires ML engineer or strong Python background.
**Connects to:** Limitation 1 (contradiction oracle).

---

## Experiment 3 — φ-Zone Generalization Study

**What:** Test whether the golden ratio phase boundary in exploration rate
generalizes beyond multi-armed bandits with continuous multi-frequency drift.

**Domains to test:**
1. Neural architecture search (ε controls layer width exploration)
2. Portfolio optimization (exploration vs exploitation in asset allocation)
3. Drug discovery pipeline (screening breadth vs depth trade-off)
4. Climate policy (mitigation speed vs adaptation investment balance)
5. Multi-agent coordination (exploration rate in Nash equilibrium search)

**Method:** For each domain, implement a baseline strategy and a φ-zone strategy
(ε = φ⁻² ≈ 0.382 or equivalent); measure final reward, convergence speed, stability.

**Success criterion:** φ-zone strategy outperforms classical baseline in ≥3/5 domains
with p < 0.05. If it fails: document failure, bound the claim.

**Effort:** 6 months, requires domain specialist per domain.
**Risk:** φ-zone may be domain-specific to chaotic drift → revise claims honestly.
**Current paper placement:** φ-zone is appendix only until this experiment runs.
**Connects to:** Limitation 7 (φ-zone generalization).

---

## Experiment 4 — AURA Invariants Empirical Validation

**What:** Verify that AURA's seven invariants, when enforced as constraints on an RL agent,
actually prevent unsafe behavior without excessive cost to performance.

**Method:**
1. Train RL agents in three environments (GridWorld, Atari-style navigation, Simulated Robot)
2. Version A: Standard training (no AURA)
3. Version B: AURA penalty added to reward function (violating invariants → negative reward)
4. Measure cost vs benefit:
   - Cost: convergence speed, wall-clock time to solve
   - Benefit: dangerous action frequency, worst-case behavior distribution

**Success criterion:** AURA adds <10% training cost; reduces dangerous actions by >50%.

**Effort:** 4 months, requires RL engineer.
**Connects to:** AURA formal specification in `02_AURA/`; Invariants I & VII now
formally computable (see `12_IMPLEMENTATIONS/core/aura_checker.py`).

---

## Experiment 5 — Cascade Predictability Test

**What:** How accurately can the system predict that a cascade is about to trigger
before the triggering evidence arrives?

**Method:**
1. Simulate knowledge systems with gradual evidence accumulation
2. At each step, predict: "Will the next evidence trigger a cascade?"
3. Vary the lookahead window (1-step, 3-step, 5-step)
4. Measure precision and recall of predictions

**Success criterion:** >80% accuracy with 5-step lookahead (i.e., can predict
cascades 5 evidence-additions in advance with 80% precision).

**Effort:** 2 months. Can begin immediately — no external dependencies.
**Connects to:** CASCADE engine's Π trajectory computation.

---

## Experiment 6 — Cross-Cultural Validation (The Priority One for Aotearoa)

**What:** Test whether CASCADE's truth pressure mechanism generalizes across
different epistemic traditions — Western scientific, Māori, Chinese, and
Indigenous Australian — or whether Π requires cultural calibration.

**Why this is the most important experiment for NZ:**
This experiment directly justifies Catalyst Strategic funding (NZ–China bridge),
NZIAT engagement (May 2026), and the Te Tumu partnership (University of Otago).
It is the experiment that makes Lycheetah a NZ research program, not just
a framework built in NZ.

**Cultures / epistemic traditions:**
1. Western scientific (Newtonian/Bayesian baseline)
2. Māori knowledge governance (Kaitiakitanga, whakapapa, tikanga)
3. Chinese traditional epistemology (Confucian + contemporary)
4. Indigenous Australian (country-based knowledge systems)

**Method:**
1. Partner with practitioners in each tradition (Te Tumu for Māori; Tsinghua/Peking
   for Chinese; AIATSIS or Australian universities for Indigenous AU)
2. Interview practitioners about knowledge reorganization events in their tradition —
   when does old knowledge get "retired"? What is the trigger?
3. Map their descriptions onto CASCADE's Π framework or identify where Π fails
4. Measure: does CASCADE predict the same trigger points? Or does Π require
   cultural parameters?

**Success criterion:** Either (a) Π formula generalizes with same thresholds
across traditions, OR (b) cultural calibration factors are identified and documented.
Both outcomes are publishable. A clean null result here is still science.

**Effort:** 12 months, requires anthropologist + local community collaboration + IRB.
**Budget estimate:** $400K (2 FTE × 12 months + travel + community engagement).

**This experiment is the bridge to:**
- NZIAT May 2026 presentation
- Te Tumu (Prof. Jacinta Ruru) partnership
- Catalyst Strategic 2027 application (NZ–China axis)
- AI & Ethics (Springer) paper on LAMAGUE as cross-cultural governance

---

## Timeline

| Quarter | Experiment | Status | Key Dependency |
|---|---|---|---|
| Q2 2026 (Apr–Jun) | Exp 5: Cascade Predictability | Ready to start | None — internal |
| Q2 2026 (Apr–Jun) | Exp 1: Corpus Validation (design) | Not started | Historian partner |
| Q3 2026 (Jul–Sep) | Exp 2: Contradiction Detection | Not started | ML engineer |
| Q3 2026 (Jul–Sep) | Exp 4: AURA Invariants Validation | Not started | RL engineer |
| Q4 2026 (Oct–Dec) | Exp 3: φ-Zone Generalization (design) | Not started | Domain experts ×4 |
| Q1 2027 (Jan–Mar) | Exp 6: Cross-Cultural (begin) | Not started | Te Tumu + IRB |
| Q2 2027 | Exp 1: Corpus Validation (results) | Not started | Domain experts |
| Q2 2027 | Exp 3: φ-Zone results | Not started | Domain experts |
| Q3–Q4 2027 | Exp 6: Cross-Cultural (results) | Not started | Community partners |

---

## Funding Requirements

| Experiments | Budget | Notes |
|---|---|---|
| Exp 1–5 (18 months) | ~$800K | 4 FTE: ML eng, RL eng, historian, domain specialist |
| Exp 6 Cross-Cultural | ~$400K | 2 FTE + travel + community engagement |
| **Total** | **~$1.2M** | 18-month validation program |

**For NZIAT (May 2026):** Exp 6 design is the pitch.
**For Catalyst Strategic (2027 round):** Full roadmap is the application backbone.
**For arXiv/publication now:** Exp 5 (cascade predictability) can start immediately
with no external dependencies — first result in 2 months.

---

## Why This Roadmap Matters

Funding goes to teams with specific plans.

"We have 5 experiments waiting, one can start tomorrow, one connects directly
to Te Tiriti o Waitangi and the NZ–China relationship, and together they cost
$1.2M for 18 months of work that transforms CASCADE from a promising framework
into validated science" — that is a fundable sentence.

"We'll figure out next steps" is not.
