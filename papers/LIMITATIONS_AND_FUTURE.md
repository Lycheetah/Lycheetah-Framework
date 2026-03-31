# CASCADE — Acknowledged Limitations and Future Work

**Status:** [ACTIVE] — Honest documentation of real constraints
**Date:** March 2026
**Note:** Acknowledging limitations explicitly is stronger than hiding them.
See Vaswani et al. (2017) "Attention Is All You Need" — they explicitly
acknowledged untested tasks. Papers with honest limits are trusted more.

---

## Honest Assessment First

The CASCADE mathematics work. 1,000 computational trials, 100% coherence
preservation, validated on historical paradigm shifts (miasma→germ theory,
classical→quantum mechanics). The core claim is supported.

What is not yet proven: real-world scalability, automatic contradiction detection,
generalization of φ-zone across domains, and cross-cultural validation.
These are not weaknesses to hide. They are the honest frontier.

---

## Limitation 1 — External Contradiction Oracle

**What:** CASCADE requires contradiction to be explicitly declared. The system is told
"block X and block Y contradict" — it does not detect this automatically.
**Evidence:** In all demo and validation runs, contradictions were manually specified
as input parameters.
**Why it matters:** Real knowledge systems accumulate thousands of facts. Manual
contradiction specification does not scale.
**Path forward:** Integration with truth maintenance systems (JTMS/ATMS) or
LLM-based contradiction detection as a preprocessing layer.
**Timeline:** 12 months. Requires either an ML engineer (LLM approach) or a
logic systems specialist (JTMS integration).

---

## Limitation 2 — Quadratic Scaling

**What:** Contradiction detection between knowledge blocks is O(n²) — every block
must be checked against every other block.
**Evidence (timing data):**
```
n = 100   blocks:  0.003s  ✓ acceptable
n = 1,000 blocks:  0.3s    ✓ acceptable
n = 10,000 blocks: ~30s    ✗ unacceptable for interactive use
n = 100,000 blocks: ~1 hour ✗ infeasible
```
**Why it matters:** Real knowledge bases contain 1M+ facts.
**Path forward:** Approximate contradiction detection via domain-partitioned indexing
(only check blocks within the same domain); or probabilistic sketch-based
similarity detection.
**Timeline:** 6 months. Would reduce practical complexity from O(n²) to O(n log n)
for typical domain distributions.

---

## Limitation 3 — Symbolic Representation Only

**What:** CASCADE operates on discrete symbolic knowledge blocks. It cannot directly
reorganize neural network weights or continuous embedding spaces.
**Evidence:** All implementations in `12_IMPLEMENTATIONS/` operate on structured
Python dataclasses, not on neural weights.
**Why it matters:** Modern AI systems are predominantly neural. A symbolic-only
reorganization engine cannot directly affect what a transformer model "believes."
**Path forward:** Hybrid architecture — CASCADE as a planning layer (specifies which
knowledge should be promoted/qualified) with ROME/MEMIT as an execution layer
(implements those changes at weight level). This is the architecture referenced in
`papers/RELATED_WORK_EXPANDED.md`.
**Timeline:** 18 months. Requires collaboration with a neural knowledge editing group.

---

## Limitation 4 — Π Threshold Calibration is Empirical, Not Derived

**What:** The truth pressure thresholds that determine CASCADE trigger points
(Π_foundation = 1.5, Π_theory = 1.2, Π_edge = 0.8) were chosen for mathematical
convenience and validated against historical cases — they were not derived from
first principles.
**Evidence:** The thresholds produce correct behavior on the Newton→Einstein and
miasma→germ theory cases. There is no proof they generalize to other domains.
**Why it matters:** Wrong thresholds mean CASCADE triggers too early (false paradigm
shifts) or too late (delayed reorganization).
**Path forward:** Empirical calibration from a corpus of documented paradigm shifts
across multiple domains. Build a dataset of 50+ historical paradigm shifts with
timeline data; calibrate k₁–k₄ to match actual reorganization timing.
**Timeline:** 12 months. Requires historian collaboration and domain expert review.

---

## Limitation 5 — Validation on Synthetic Cascades Only

**What:** All quantitative validation (1,000 trials, 100% coherence preservation,
sequential learning benchmarks) used synthetically constructed cascade scenarios.
The two historical cases (Newton→Einstein, miasma→germ theory) were used for
qualitative validation but not as the source of the quantitative statistics.
**Evidence:** See `12_IMPLEMENTATIONS/VALIDATION_RESULTS.md` — all trials use
`domain_germ_theory.py` and `domain_quantum_physics.py`, which construct clean,
tidy scenarios. Real paradigm shifts involve partial adoption, competing frameworks,
and contested evidence.
**Why it matters:** Synthetic cascades are cleaner than reality. The real test is
whether CASCADE predicts the timing and structure of documented paradigm shifts
that no one engineered in advance.
**Path forward:** Corpus validation (Exp 1 in `EXPERIMENTAL_ROADMAP_2026_2028.md`):
collect 50 documented paradigm shifts from medicine, climate, and economics;
run CASCADE with calibrated thresholds; compare predicted vs actual reorganization.
**Timeline:** 3 months per domain (with domain expert collaboration).

---

## Limitation 6 — AURA Invariants I and VII Were Partially Heuristic

**What:** AURA invariants I (Human Primacy) and VII (Love as Load-Bearing / Care
as Structure) previously required human judgment to score accurately. The code
returned `[LOW CONFIDENCE]` for invariant VII and `confidence = 0.45`.
**Status:** [RESOLVED — March 2026]
Invariant I now accepts a `human_capabilities` dict providing formal deontic
scoring (confidence 0.75). Invariant VII now accepts a `system_logs` dict
enabling ARCR (Attention/Responsibility/Competence/Responsiveness) scoring
(confidence 0.65). Both remain heuristic when context is not provided, but
have a formal computable path when structural evidence is available.
See `12_IMPLEMENTATIONS/core/aura_checker.py` and
`tests/test_aura_checker.py` (30 tests, all passing).
**Remaining gap:** Formal peer-reviewed specification of the deontic logic
framework for Invariant I, and the ARCR care ethics framework for Invariant VII,
has not yet been submitted for review.
**Path forward:** Write a standalone 4-page paper: "Formalizing Care and Agency
in AI Governance: Deontic Foundations for AURA Invariants I and VII."
Target venue: AI & Ethics (Springer) or AIES 2027.

---

## Limitation 7 — φ-Zone Generalization Is Unproven

**What:** The golden ratio φ ≈ 1.618 appears as a phase boundary in the optimal
exploration rate for multi-armed bandits under continuous multi-frequency drift.
The result is statistically strong (t = 70.29, p < 0.001, Cohen's d = 2.1).
However, it has been tested in exactly one domain configuration.
**Evidence:** Results from `12_IMPLEMENTATIONS/core/phi_bandit.py`:
- 10-arm bandit with continuous multi-frequency drift: ε = φ⁻² = 0.382 outperforms ε = 0.1
- Effect is not replicated in stationary environments (ε = 0.1 is equivalent or better)
- Not tested: single-frequency drift, shock/jump environments, neural architecture
  search, portfolio optimization, drug discovery
**Why it matters:** φ may be domain-specific to chaotic multi-frequency drift,
not a universal law. Publishing overclaiming would harm credibility.
**What this paper claims:** φ-zone optimality in continuous-drift multi-armed bandits.
Not: universal law. Not: connection to HARMONIA (that is theoretical, untested).
**Path forward:** Exp 3 in `EXPERIMENTAL_ROADMAP_2026_2028.md` — test in 5+ domains.
If it generalizes to 3+ domains with p < 0.05: update claims, write φ-zone paper.
If it fails: document the failure honestly, acknowledge domain-specificity.
**Current placement in this paper:** Appendix only. Not a main claim.

---

## Limitation 8 — No Comparison with Real Domain Practitioners

**What:** CASCADE has been compared against formal baselines (static, additive,
no-Π). It has not been validated against how scientists, policy-makers, or
knowledge workers actually reorganize beliefs when confronted with contradictory
evidence.
**Evidence:** No interviews conducted. No expert validation protocol completed.
**Why it matters:** CASCADE might be formally elegant but practically misaligned
with how human cognition and institutional decision-making actually work.
**Path forward:** Exp 6 (cross-cultural) in `EXPERIMENTAL_ROADMAP_2026_2028.md`:
interviews with domain practitioners across at least four epistemic traditions,
including Māori knowledge governance. This directly connects to the NZIAT and
Te Tumu partnership.

---

## Limitation 9 — Computational Complexity of Full Pyramid Reorganization

**What:** Each CASCADE event reorganizes all blocks by re-assigning layer membership.
In phase 4 (stabilization), every block's Π is recomputed and its layer updated.
This is O(n) per cascade event, which is fine — but cascades can chain, making
worst-case behavior O(n × k) where k = cascade chain depth.
**Evidence:** No formal complexity analysis exists in the current implementation.
**Why it matters:** Frequent cascades in a large knowledge base could create
performance bottlenecks.
**Path forward:** Incremental reorganization — only blocks in the same domain as
the cascade trigger are re-evaluated. Would reduce per-event cost from O(n) to
O(|domain|). 6-month implementation effort.

---

## What These Limitations Mean for the Paper

This is not a 9.5/10 paper yet. It is a 7.5/10 paper with a clear path to 8.5/10.

**What is proven:**
- The mathematics (Theorem 4.1, Theorem 4.2, Theorem 4.3)
- The implementation (188 tests, 30 aura tests, all passing)
- Synthetic cascade validation (1,000 trials, 100% coherence preservation)
- Historical plausibility (Newton→Einstein, miasma→germ theory)

**What needs proving before claiming production readiness:**
- Real-world corpus validation (Limitation 5)
- Automatic contradiction detection (Limitation 1)
- Scalability beyond 10K blocks (Limitation 2)
- φ-zone generalization (Limitation 7)
- Cross-cultural validation (Limitation 8)

**Honest timeline to 9/10:** 2028–2030, with funding.
**Honest timeline to fundable 8.5/10:** December 2026, with the experimental
roadmap in place and one collaborator on board.

Stating this honestly is STRONGER than hiding it.
