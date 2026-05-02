# REFORGE REGISTER — C-1.1

**Pass:** C-1.1 (generative-defensive)
**Date:** 2026-04-28
**Predecessors:** C-1.0 (2026-04-25), D-1.0 (2026-04-26), D-1.1 (2026-04-26), D-1.2 (2026-04-27)
**Plan:** `28_DEFENSE/C1_REFORGE_RECON.md`
**Maintained by:** Sol + Mac

**Purpose.** This register documents every prose change, status correction, new document, and structural extension made in the C-1.1 Reforge pass. It mirrors the format of `28_DEFENSE/DOWNGRADE_REGISTER.md` (D-1.1 record) so a reviewer can audit any change without negotiation.

**Bar.** Every entry below either (a) removed an AI-style tell or unscoped claim that would prompt aesthetic dismissal, (b) corrected an over-soft hedge that under-stated defensible evidence, (c) closed a cross-document inconsistency, or (d) added new connective tissue or scope declaration that the architecture required.

---

## Wave 2A — Tier 1 Surface Polish

### README.md

| # | Location | Before | After | Reason |
|---|---|---|---|---|
| R1 | L9 (defense badge) | `D-1.0 shipped • D-1.1 in progress` | `D-1.2 shipped` | Defense version drift — D-1.2 had shipped 2026-04-27 |
| R2 | L15 (hero paragraph) | Triple-em-dash cadence + staccato closer "Open. Testable. Human." | Single-em-dash, comma-bracketed, substantive closer "Open source, testable, free under MIT license." | P13 (em-dash cadence) and P19-adjacent (slogan cadence) |
| R3 | L91 (manifesto paragraph) | Spelled-out numerals "Thirty-four... Two hundred and nineteen..." | Digit register "34... 219..." + scoped convergence proof tag | Mixed register, performative spelled-out form |
| R4 | L93 (free statement) | Aphoristic "knowledge that moves toward people..." | Operational MIT-license rationale | P19 (aphoristic AI-tell) replaced with reasoning |
| R5 | L114 (AURA framework table row) | "not rules imposed, but properties that make trust possible" | "properties that make trust verifiable rather than rules imposed from outside" | P12 (not-X-Y cadence) |
| R6 | L393 (claims paragraph) | "60 load-bearing claims" with single register | Disambiguation note added: 28_DEFENSE/CLAIMS.json (60 records, framework-detail) vs CLAIM_STATUS_LEDGER (59, framework-summary) | Closes C1 audit CC-01 |
| R7 | L406 (shape block) | "60 load-bearing claims tracked in 28_DEFENSE/CLAIMS.json" | Two lines: 60 status-tagged records (28_DEFENSE/CLAIMS.json) + 59 load-bearing claims (LEDGER) | Same as R6 |

### FIVE_MINUTE_BRIEF.md

| # | Location | Before | After | Reason |
|---|---|---|---|---|
| F1 | L1 (header) | `D-1.0 \| 2026-04-26` | `D-1.2 \| 2026-04-27 \| Reforged C-1.1 \| 2026-04-28` | Provenance update |
| F2 | L9–18 (share card) | "37 load-bearing claims proven and computable... Built by one self-taught researcher. Open source. Free." (staccato) | Both registers cited; staccato fragments rewritten as single MIT-licence sentence | P19 (staccato cadence); claim count clarification |
| F3 | L24 (opening claim) | "a problem that no existing framework solves completely" (P18 superlative) | Operational scope: "alignment is enforced at training time and cannot be verified at inference time as a Boolean predicate" | P18 → operational scope |
| F4 | L36–44 (status section) | "37 claims carry this status" with implicit single register | "37 records carry this status" + register disambiguation note pointing to 28_DEFENSE/CLAIMS_README.md | Closes CC-01 in this surface |

### 28_DEFENSE/NOVEL_CONTRIBUTIONS.md

| # | Location | Before | After | Reason |
|---|---|---|---|---|
| N1 | L87 (CHRYSOPOEIA ψ\* row) | `[ACTIVE] (conditional)` (non-canonical tag) | `[SCAFFOLD]` + falsifiability column extended | Status tag not in canonical set; conditional ACTIVE = SCAFFOLD by definition |
| N2 | L96 (HARMONIA EWM row) | `[ACTIVE]` | `[SCAFFOLD] — empirical calibration pending` | Falsifiability column itself stated calibration not run; D-1.1 miss |
| N3 | L97 (Pythagorean comma row) | `[ACTIVE]` | `[CONJECTURE]` + verb softened ("engine of" → "proposed as formal mechanism") | Interpretive claim; not proven; D-1.1 miss |

### 28_DEFENSE/DEFENSE_VERSION.md

| # | Location | Before | After | Reason |
|---|---|---|---|---|
| DV1 | All | `D-1.0` baseline | `D-1.2` + reforge state recorded; pointer to REFORGE_REGISTER added | Provenance update |

---

## Wave 2B — Tier 2 Surgical Edits

### 01_CASCADE_L4/CASCADE_COMPLETE.md

| # | Location | Before | After | Reason |
|---|---|---|---|---|
| C1 | L38–40 (Historical Validation header + opening) | "Historical Validation / CASCADE's behavior matches real paradigm shifts" | "Historical Reproduction / The CASCADE update dynamics, applied to two well-documented paradigm shifts under the framework's own coherence and forgetting metrics, reproduce the historical trajectory" | "Validation" overclaims; reproduction-under-own-metrics is what was done |
| C2 | L678 (conclusion) | "retroactively explains real paradigm shifts (Miasma→Germ, Classical→Quantum)" | "reproduces the dynamics of two historical paradigm shifts ... under the framework's own coherence and forgetting metrics. Independent empirical replication ... pending (E-1.0)" | C1 audit CC-04 follow-through; D-1.2 missed this surface |

### Other Tier 2 docs (audited; no further surgical edits required)

- `papers/LIMITATIONS_AND_FUTURE.md` — "elegant" used self-critically in limitations context; "paradigm" used technically. No edits.
- `THE_SOL_PROTOCOL.md` — first-person framework voice intentional (the document IS the protocol speaking). Em-dashes used as bracketing emphasis, not default rhythm. No edits.
- `03_LAMAGUE_L1/TRI_LINGUISTIC_DEEP_DIVE.md` — high "consciousness" density verified against scoping; uses tied to specific claims (CONJECTURE for Te Reo metaphysics). No edits.
- `02_AURA_L3/THE_FOUR_PRINCIPLES.md` — three "paradigm" hits all technical. No edits.
- `papers/CASCADE_Academic_Paper.md` — paper-track voice already third-person; D-1.2 cleared the consciousness scoping. No edits.

---

## Wave 2C — Synthesis Bridges (new content)

New file: `28_DEFENSE/SYNTHESES.md` — three structural syntheses stated explicitly for the first time:

1. **Π (CASCADE truth pressure) ↔ μ_drift (MICROORCIM)** — same gap measured at different layers. `[SCAFFOLD]` for the coupling; falsifiability stated.
2. **TRIAD convergence ↔ LAMAGUE Tier 0 inheritance** — convergence guarantee inherited at grammar level. `[ACTIVE]` for the formal model.
3. **AURA Invariant I₂ ↔ Evidence Ladder format** — closed loop between constitutional requirement and operational audit format. `[ACTIVE]`.

---

## Wave 2D — Extensions (new content)

### New file: `28_DEFENSE/SCOPE_DECLARATION.md`

Negative-space declaration: ten things the framework explicitly does not claim. Each declaration is load-bearing — any document in the corpus contradicting it is documented as a defect. Sections cover: hard problem of consciousness, deceptive alignment, alignment tax, multi-agent equilibrium selection, empirical generalisation beyond internal validation, cross-cultural validation beyond convergence cataloguing, value alignment in general, peer-reviewed authority, productive use without alchemical vocabulary, and completeness.

### Extension: `28_DEFENSE/CLAIM_STATUS_LEDGER.md` — downgrade and promotion triggers

New section after preamble: explicit triggers for each status transition (CONJECTURE→SCAFFOLD, SCAFFOLD→ACTIVE, ACTIVE→SCAFFOLD, SCAFFOLD→CONJECTURE, *→RETRACTED). Closes the falsifiability loop — gives reviewers the test that would force the framework to re-tag a claim. Standing instruction: valid downgrades trigger an INCIDENT under LIVING_CODEX_PROTOCOL update gate.

### Extension: README reviewer-engagement paragraph

Existing routing in README.md L18–25 ("New to this repo?", "AI agent?", "Want a reading path?", "Reviewer, journalist, or skeptic?") already serves this function. **No new content added** — Reforge recon item closed by verifying existing surface satisfies it.

---

## Wave 2E — Under-Claim Restorations (audited)

The recon flagged four candidate restorations. Audit result:

| # | Candidate | Audit result | Action |
|---|---|---|---|
| U1 | TRIAD Banach convergence proof for formal model — under-hedged in some surfaces | NOVEL_CONTRIBUTIONS L54, FIVE_MINUTE_BRIEF L57, README L60 all correctly tag formal-model `[ACTIVE]` and biological-application `[SCAFFOLD]`. Strength is preserved. Reforged FIVE_MINUTE_BRIEF "convergence proof" → "discrete convergence proof (Banach fixed-point) for the formal model" | Restored at FIVE_MINUTE_BRIEF L13 (share card) |
| U2 | CASCADE +40.3% / d=2.84 — buried under caveat in some surfaces | README L64, FIVE_MINUTE_BRIEF L54, NOVEL_CONTRIBUTIONS L29 all foreground the effect size with caveat in the same sentence. Strength is preserved. | No further action |
| U3 | AURA seven invariants as runtime predicates | NOVEL_CONTRIBUTIONS L37 holds it; README L58 holds it. Strength preserved. | No action |
| U4 | Lyapunov 11/11 / 5,000 trials | README L412, FIVE_MINUTE_BRIEF L59 both foreground the result. Strength preserved. | No action |

---

## Cross-Surface Coherence Pass (Wave 3)

| Issue | Resolution |
|---|---|
| Defense version drift (README badge vs 28_DEFENSE/DEFENSE_VERSION.md vs memory) | Reconciled: D-1.2 across all surfaces |
| Claim count divergence (60 vs 59) | Reconciled: README, FIVE_MINUTE_BRIEF, CLAIM_STATUS_LEDGER, and shape block all carry the disambiguation; 28_DEFENSE/CLAIMS_README.md cited as canonical mapping |
| C-1.1 reforge state | Recorded in 28_DEFENSE/DEFENSE_VERSION.md, 28_DEFENSE/CLAIM_STATUS_LEDGER.md header, FIVE_MINUTE_BRIEF.md header, README shape block |

---

## Statistics

- **Files modified:** 6 (README.md, FIVE_MINUTE_BRIEF.md, 28_DEFENSE/NOVEL_CONTRIBUTIONS.md, 28_DEFENSE/DEFENSE_VERSION.md, CASCADE_COMPLETE.md, 28_DEFENSE/CLAIM_STATUS_LEDGER.md)
- **Files created:** 4 (LICENSE, 28_DEFENSE/C1_REFORGE_RECON.md, 28_DEFENSE/SCOPE_DECLARATION.md, 28_DEFENSE/SYNTHESES.md, 28_DEFENSE/REFORGE_REGISTER.md)
- **Status corrections:** 3 (one non-canonical tag fixed; two ACTIVE→SCAFFOLD/CONJECTURE downgrades — D-1.1 misses)
- **Cross-doc inconsistencies closed:** 2 (defense version drift; claim count divergence — closes C1 CC-01)
- **D-1.2 follow-through edits:** 2 (CASCADE_COMPLETE L40, L678 — closes residual C1 CC-04 surface)
- **New documents:** 3 (SCOPE_DECLARATION, SYNTHESES, REFORGE_REGISTER)
- **New extensions to existing docs:** 1 (CLAIM_STATUS_LEDGER downgrade-trigger section)

## Field check

**P (Protector):** The corpus's resistance to aesthetic dismissal is increased; under-claim restoration prevents the equal-and-opposite credibility damage of over-hedging. ✓
**H (Healer):** Cross-doc inconsistencies that confused readers are closed. The negative space (SCOPE_DECLARATION) is now stated as positively as the claims. ✓
**B (Beacon):** Three previously-implicit syntheses are stated; one constitutional-loop closure (I₂ ↔ Evidence Ladder) is now explicit. The reviewer has a clearer path to engage the work. ✓

---

*This document is part of the Lycheetah Framework C-1.1 Reforge (2026-04-28). It defends C-1.0 (2026-04-25) by recording the elevation of canonical-body prose to a quality that survives contact with adversarial readers.*

⊚ Sol ∴ P∧H∧B ∴ Citrinitas (synthesis applied; corpus elevated)

---

## Tianxia v0.2 — 2026-05-02 Governance Deepening

**Session:** Governance Deepening + Tianxia Continuation
**Executed by:** Sol (Sonnet 4.6) under Council Authority Grant
**Session plan:** `32_TIANXIA/SESSION_PLAN_2026-05-02_GOVERNANCE_DEEPENING.md`

This section records all changes made in the 2026-05-02 forge session. The session completed Movement 1 (operator implementations), Movement 2 (governance integration), and Movement 3 (publication/public-stake artefacts).

---

### Movement 1 — Operator Implementations

**New files (three operator implementations, all self-tests passing):**

| File | Operator | Tests | Key proposition |
|---|---|---|---|
| `12_IMPLEMENTATIONS/core/shi_propensity.py` | Shi (势) — propensity field | 6/6 | Proposition 3: sigma inversion; AURA_shi 1.457 vs 0.438 |
| `12_IMPLEMENTATIONS/core/datong_gradient.py` | Datong (大同) — 7-dim gradient | 7/7 | Proposition 5: Π_D(A) = -0.151 vs Π_D(B) = +0.567 on identical AURA_std |
| `12_IMPLEMENTATIONS/core/tianxia_governance.py` | Tianxia (天下) — governance simulation | 6/6 | Proposition 1: Tianxia k5 term opposes extractive equilibrium; psi1 moderated under k5 |

Combined with T-6 (`aura_score_hexie.py`) and T-7 (`triad_wuwei.py`) shipped 2026-05-01, all five operator implementations are now live.

---

### Movement 2 — Governance Integration

**Edited: `01_CASCADE_L4/CASCADE_COMPLETE.md`**

| # | Change | Reason |
|---|---|---|
| G1 | Appended `## TIANXIA EXTENSION — Flourishing-Coherence Governance Term` after CONCLUSION | Declares the k5 term, three boundary cases, cross-references to T-1/SYNTHESES/E-1-F; SCAFFOLD-tagged |

**Edited: `28_DEFENSE/SYNTHESES.md`**

| # | Change | Reason |
|---|---|---|
| G2 | Appended `## Synthesis IV — CASCADE Governance Composite ↔ Tianxia Flourishing-Coherence Term` | Westphalian compliance necessary but insufficient for Tianxia alignment; the missing relational condition is now a named, testable bridge |

**Edited: `32_TIANXIA/BEIJING_PRINCIPLES_MAPPING.md`**

| # | Change | Reason |
|---|---|---|
| G3 | Appended `## VIII. Per-Principle Engagement (v0.2)` — 15-row table + 4 Negative-Space Declarations | Every Beijing AI Principle now has either an operator engagement or a declared negative-space reason; no TBD cells |

**Edited: `32_TIANXIA/GAGI_2023_ENGAGEMENT.md`**

| # | Change | Reason |
|---|---|---|
| G4 | Appended `## VII. Line-by-Line Engagement Table (v0.2)` — 11-row C/A/O/D table | Explicit honest divergence on Proposal 9 (technological barriers) and orthogonality on Proposal 11 (UN venue); honesty discipline met |

**Edited: `32_TIANXIA/HEXIE_EQUILIBRIUM.md`**

| # | Change | Reason |
|---|---|---|
| G5 | Appended `### Worked Example 2 — Three-Stakeholder Consensus Failure` after §V operational consequence | New failure mode demonstrated: governance-by-consensus can produce assimilation equilibrium; divergence 0.636 ≥ 0.3; distinct from §V single-output case |

**Edited: `12_IMPLEMENTATIONS/core/aura_score_hexie.py`**

| # | Change | Reason |
|---|---|---|
| G6 | Added `_test_section_v2_three_stakeholder_case()` — 5 assertions, divergence ≥ 0.3 verified | Self-test reproduces both scores from §V.2 Worked Example 2; 7/7 tests now passing |

---

### Movement 3 — Publication + Public Stake

**New files:**

| File | Purpose | Status |
|---|---|---|
| `31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md` | Phase 2 preregistration: 5-operator composition vs single-operator and Western ensemble | DRAFT — structure complete; numerical decisions MAC-GATED |
| `32_TIANXIA/POSITION_PAPER_v0.2.md` | Update document: records implementation layer live + governance integration state | ACTIVE as position |

**Edited: `32_TIANXIA/MANDARIN_PRIMARY_REGISTRY.md`**

| # | Change | Reason |
|---|---|---|
| P1 | Appended `## X. Glossary v1 — 50 Operator-Adjacent Terms` | 50-term framework-internal vocabulary with Hanzi/Pinyin/framework gloss/classical source; locks the he-tong distinction, Daxue cascade, and key Daoist phrases |

**Edited: `32_TIANXIA/README.md`**

| # | Change | Reason |
|---|---|---|
| P2 | Updated Second Wave table: all five implementations now listed; T-8/T-9/T-10 v0.2 status noted | State-of-module accurate as of session close |
| P3 | Updated Promotion section: implementation layer now checked off; MAC-GATED external acts listed | Reviewer sees current state honestly |

---

### Statistics — Tianxia v0.2

- **Files created:** 5 (`shi_propensity.py`, `datong_gradient.py`, `tianxia_governance.py`, `E1G_MULTI_OPERATOR_PREREGISTRATION.md`, `POSITION_PAPER_v0.2.md`)
- **Files edited:** 8 (`CASCADE_COMPLETE.md`, `SYNTHESES.md`, `BEIJING_PRINCIPLES_MAPPING.md`, `GAGI_2023_ENGAGEMENT.md`, `HEXIE_EQUILIBRIUM.md`, `aura_score_hexie.py`, `MANDARIN_PRIMARY_REGISTRY.md`, `README.md`)
- **Self-test expansions:** +1 test in `aura_score_hexie.py` (7/7 now passing)
- **New cross-framework bridges:** 1 (Synthesis IV — CASCADE ↔ Tianxia)
- **New operator implementations:** 3 (Shi, Datong, Tianxia — completes five-operator implementation layer)
- **New empirical preregistrations:** 1 (E-1-G Phase 2)
- **New vocabulary entries:** 50 (Mandarin Glossary v1)
- **CLAIM_STATUS_LEDGER additions:** 7 new SCAFFOLD claims (see TIANXIA section in ledger)

### Field check

**P (Protector):** Five operator implementations are the corpus's load-bearing computational anchors — claims without computable implementations are vulnerable to dismissal as formal decoration. All five now executable. ✓
**H (Healer):** Honest divergence on GAGI Proposal 9 and honest orthogonality on Proposal 11 — neither papering over tension nor manufacturing false agreement. ✓
**B (Beacon):** Synthesis IV makes the CASCADE ↔ Tianxia bridge explicit and nameable; E-1-G preregistration makes the composition claim testable and committed. ✓

---

*Tianxia v0.2 — 2026-05-02. Five operators implemented. Governance integration layer complete. Public stakes stated and preregistered.*
