# SESSION PLAN — 2026-05-02
## Governance Deepening + Tianxia Continuation

**Forged by:** Opus (Sol) under Council Authority Grant (2026-05-01)
**Executed by:** Sonnet
**Mission:** Continue the governance lane and the China-oriented (Tianxia) lane in a single day's arc. Three movements, ~17 atomic tasks, ~6–8 hours focused work.
**Master plan reference:** `OPUS_MASTER_PLAN_2026.md` Wave A — lanes 4 (TIANXIA Civilisational), 6 (Implementation), 7 (Strategic / Governance).
**Tag at session close:** `tianxia-v0.2` (local; push gated on Mac).

---

## 0. SONNET — READ FIRST (load order, do not skip)

```
1. ~/CLAUDE.md                                    — Sol Protocol v3.1 (operating system)
2. ~/CLAUDE_AUGMENTED.md                          — v4.0 Disciplines + Appendix A
3. ~/.claude/projects/C--Users-thedo/memory/MEMORY.md
4. ~/.claude/projects/C--Users-thedo/memory/project_tianxia_module.md
5. ~/.claude/projects/C--Users-thedo/memory/project_opus_master_plan.md
6. ~/.claude/projects/C--Users-thedo/memory/project_codex_defense.md
7. ~/.claude/projects/C--Users-thedo/memory/feedback_council_authority.md
8. CODEX_AURA_PRIME/32_TIANXIA/TIANXIA_MODULE_v0.1.md
9. CODEX_AURA_PRIME/32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md
10. CODEX_AURA_PRIME/32_TIANXIA/HEXIE_EQUILIBRIUM.md
11. CODEX_AURA_PRIME/32_TIANXIA/SHI_PROPENSITY_FIELD.md
12. CODEX_AURA_PRIME/32_TIANXIA/WUWEI_TRIAD_EXTENSION.md
13. CODEX_AURA_PRIME/32_TIANXIA/DATONG_GRADIENT.md
14. CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core/aura_score_hexie.py  (reference shape for new modules)
15. CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core/triad_wuwei.py       (reference shape for new modules)
16. CODEX_AURA_PRIME/28_DEFENSE/CLAIM_STATUS_LEDGER.md
17. CODEX_AURA_PRIME/28_DEFENSE/REFORGE_REGISTER.md                (append at session close)
```

**Discipline check before each task:** does the change pass P∧H∧B AND the Five Disciplines (Reforge prose / Anchor / Recursive Defence / Negative-Space / Empirical)?

**Council Authority:** Sol-owned tasks (S) execute without asking. Mac-gated tasks (M) pause for explicit go.

**Velocity rule:** report only what's non-obvious. Ship → next task. No status reports between tasks unless something fails.

---

## ARC OF THE DAY

| Movement | Theme | Tasks | Est. effort |
|---|---|---|---|
| **M1 — Implementation Round** | Round out Tianxia operator implementations 3/5, 4/5, 5/5 | T-IMPL-1..3 | 2–3 hrs |
| **M2 — Governance Integration** | Cross-link CASCADE governance ↔ Tianxia operators; deepen Beijing Principles + GAGI engagement | T-GOV-1..5 | 2 hrs |
| **M3 — Phase-2 Preregistration + Public Stake** | Multi-operator composition preregistration; Mandarin glossary v1; Position Paper v0.2; Predictions Registry expansion | T-PUB-1..5 | 2–3 hrs |
| **Closing** | Register, ledger, README, commit chain | T-CLOSE-1..2 | 30 min |

---

# MOVEMENT 1 — IMPLEMENTATION ROUND

Round out the implementation layer. T-6 (Hexie) and T-7 (Wuwei) shipped 2026-05-01 with self-tests passing. Three operators remain unimplemented. Anchor Principle: each operator with working code is a redundant load-bearing point under the module's "engagement, not decoration" claim.

---

### T-IMPL-1 [S] — `shi_propensity.py`

**Goal:** Implement Shi (势) as a propensity-field reformulation of AURA scoring per `SHI_PROPENSITY_FIELD.md` §III–§V.

**File:** `CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core/shi_propensity.py`

**Shape (mirror `aura_score_hexie.py`):**
- Module docstring with operator name, classical source, framework mapping
- `@dataclass ShiState` — situational variables (configuration, momentum, terrain)
- `propensity_score(state: ShiState) -> float` — returns scalar in [0, 1] representing situational propensity
- `propensity_gradient(state: ShiState) -> dict` — directional decomposition
- `__main__` block with self-test reproducing the worked example from `SHI_PROPENSITY_FIELD.md` §V (whichever proposition is stated there with numeric outputs)

**Success criteria:**
- `python shi_propensity.py` exits 0
- Self-test prints `PASS` lines for each assertion
- Output reproduces the §V worked example to within 1e-6

**Verification:**
```
cd C:\Users\thedo\CODEX_AURA_PRIME\12_IMPLEMENTATIONS\core
python shi_propensity.py
```

**Negative space:** does NOT claim Shi predicts policy outcomes. Score is a *structural* propensity within the framework's own variables.

---

### T-IMPL-2 [S] — `datong_gradient.py`

**Goal:** Implement Datong (大同) as the long-cycle telos gradient in HARMONIA value-space per `DATONG_GRADIENT.md` §III–§V.

**File:** `CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core/datong_gradient.py`

**Shape:**
- `@dataclass DatongState` — current value-space coordinates + reference Datong target vector
- `datong_gradient(state: DatongState) -> np.ndarray` — direction vector toward Great Unity
- `gradient_magnitude(state: DatongState) -> float` — distance metric in value-space
- `is_aligned(state: DatongState, threshold: float = 0.7) -> bool`
- `__main__` self-test reproducing §V worked example

**Success criteria:** same shape as T-IMPL-1.

**Negative space:** does NOT claim Datong is achievable, measurable in real polities, or culturally universal. It is a *gradient direction* in the framework's value-space, not a destination.

---

### T-IMPL-3 [S] — `tianxia_governance.py`

**Goal:** Implement Tianxia (天下) flourishing-coherence governance term per `TIANXIA_GOVERNANCE_DYNAMICS.md` §III–§V. Adds the flourishing-orientation term to CASCADE governance composite.

**File:** `CODEX_AURA_PRIME/12_IMPLEMENTATIONS/core/tianxia_governance.py`

**Shape:**
- `@dataclass GovernanceState` — rule_compliance, flourishing_orientation, coherence_field
- `tianxia_score(state: GovernanceState) -> float` — composite score with flourishing-coherence term
- `vs_compliance_only(state: GovernanceState) -> dict` — diagnostic comparing rule-only baseline vs Tianxia score
- `__main__` self-test reproducing §V worked example: a high-rule-compliance / low-flourishing case scores below a moderate-rule-compliance / high-flourishing case

**Success criteria:** same shape. Self-test must demonstrate that *rule-compliance without flourishing-orientation is insufficient* — this is the operator's load-bearing claim.

**Negative space:** does NOT score real governments. Inputs are framework-internal state variables.

---

# MOVEMENT 2 — GOVERNANCE INTEGRATION

Cross-link the Tianxia operators into the existing governance surface (CASCADE) and deepen the contemporary-Chinese-AI-governance engagement layer.

---

### T-GOV-1 [S] — CASCADE ↔ Tianxia governance bridge

**Goal:** Add a section to CASCADE_COMPLETE that explicitly states how Tianxia governance term modifies CASCADE governance composite. Closes the cross-surface synthesis gap.

**File:** `CODEX_AURA_PRIME/02_CASCADE_FRAMEWORK/CASCADE_COMPLETE.md`
- Locate the governance section (use Grep on `governance` in that file)
- Add subsection `## Tianxia Extension (32_TIANXIA cross-link)` with:
  - One-paragraph statement of how flourishing-coherence enters the composite
  - Pointer to `32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md`
  - Pointer to `12_IMPLEMENTATIONS/core/tianxia_governance.py` (T-IMPL-3 output)
  - Status tag: `[SCAFFOLD — Tianxia operator under Module v0.1, promotion-gated]`

**Success criteria:** section reads as a load-bearing extension, not decoration. Survives Discipline 1 prose scan (no marketing adjectives, no aphoristic closer).

---

### T-GOV-2 [S] — `SYNTHESES.md` adds Tianxia bridge

**Goal:** Add a fourth forged bridge to the synthesis ledger: CASCADE governance ↔ Tianxia flourishing-coherence.

**File:** `CODEX_AURA_PRIME/28_DEFENSE/SYNTHESES.md`
- Append entry following the existing format (Π↔μ_drift, TRIAD↔LAMAGUE Tier 0, AURA I₂↔Evidence Ladder)
- Bridge: CASCADE governance composite ↔ Tianxia flourishing-coherence term
- Status: `[SCAFFOLD]` — bridge exists in code (T-IMPL-3) and in CASCADE_COMPLETE prose (T-GOV-1); promotion to ACTIVE gated on E-1-F or equivalent empirical pass

**Success criteria:** entry parallels existing three in form and rigour.

---

### T-GOV-3 [S] — `BEIJING_PRINCIPLES_MAPPING.md` v0.2

**Goal:** Deepen T-8 from operator-level mapping to per-principle case-by-case engagement. The 2019 Beijing AI Principles have ~15 articles. Map each to operator(s) that engage it.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/BEIJING_PRINCIPLES_MAPPING.md`
- Read current v0.1
- Append `## Per-Principle Engagement (v0.2 deepening)` with table:

  | Principle (number + name) | Primary operator | Secondary operator | Engagement note |
  |---|---|---|---|
  | 1. … | … | … | … |
  | … | … | … | … |

- For each of the 15 articles (research, use, governance categories), name which Tianxia operator(s) engage it and why
- Negative-space line: which articles the framework does NOT engage and why (e.g., articles purely about state-internal organisation outside the framework's scope)

**Success criteria:** every Beijing Principle has either an operator engagement OR a declared negative-space reason. No "TBD" cells.

---

### T-GOV-4 [S] — `GAGI_2023_ENGAGEMENT.md` v0.2

**Goal:** Deepen T-9 with line-by-line engagement of the Global AI Governance Initiative (Xi, October 2023) text. The GAGI document is short (~10 substantive points). Engage each.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/GAGI_2023_ENGAGEMENT.md`
- Append `## Line-by-Line Engagement (v0.2)` with table:

  | GAGI point | Operator engagement | Convergence / divergence | Note |
  |---|---|---|---|

- Mark each point as: **Convergent** (Tianxia operator and GAGI point name the same orientation), **Adjacent** (related but distinct framing), **Orthogonal** (operator does not engage), or **Divergent** (operator and GAGI point in tension — name the tension)
- Honest. If the framework diverges, name it.

**Success criteria:** at least one Convergent and one Divergent or Adjacent entry. A doc with all-Convergent fails the honesty discipline.

---

### T-GOV-5 [S] — `HEXIE_EQUILIBRIUM.md` worked-example expansion

**Goal:** Add a second worked example to T-2 demonstrating Hexie scoring on a multi-stakeholder case where naive agreement-maximisation fails but complementarity-preservation succeeds.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/HEXIE_EQUILIBRIUM.md`
- Append `## Worked Example 2 — Multi-Stakeholder Complementarity` after existing §V
- Construct: 3-stakeholder case where pairwise agreement is low but yin-yang complementarity is high (each stakeholder's strength complements the others' weakness)
- Run through the equations from §III to compute equilibrium score
- Show: agreement-maximisation score ≈ low; Hexie complementarity score ≈ high; the two metrics diverge meaningfully on this case
- After the doc update, extend `aura_score_hexie.py` self-test to include this second example

**Success criteria:** numeric divergence between agreement-maximisation and Hexie complementarity is ≥ 0.3 on the constructed case. Self-test reproduces both scores.

---

# MOVEMENT 3 — PHASE-2 PREREGISTRATION + PUBLIC STAKE

T-11 (E-1-F Phase 1 Hexie preregistration) is drafted. Phase 2 — multi-operator composition study — is the natural next preregistration. Plus public-stake artefacts: Mandarin glossary v1, Position Paper v0.2, Predictions Registry expansion.

---

### T-PUB-1 [S] — E-1-G Multi-Operator Composition Preregistration draft

**Goal:** Draft preregistration for Phase 2 — multi-operator composition study testing whether the five Tianxia operators in concert produce predicted governance-state classifications that any single operator misses.

**File:** `CODEX_AURA_PRIME/31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md`

**Structure (mirror `E1F_HEXIE_PREREGISTRATION.md`):**
- §I Background — why multi-operator composition is the test the module must pass
- §II Hypotheses — H1 (composition outperforms any single operator on classification task), H2 (composition outperforms naive ensemble of Western governance metrics), H3 (specific operator-pair predicted to dominate on case class X)
- §III Design — case set (n cases), rater pool, blinding, randomisation
- §IV Analysis plan — primary metric, secondary metrics, hypothesis tests, alpha, power
- §V Decision rules — promotion criteria (what result moves Tianxia → ACTIVE), downgrade triggers (what result forces SCAFFOLD retention or retraction)
- §VI Negative space — what this preregistration does NOT claim to test
- §VII OSF submission status — `DRAFT, awaiting Mac authorisation per Council Authority external-act gate`

**Council Authority note:** sample sizes, alpha, effect-size targets — these are Mac-gated scientific calls per E1.1 §IV. Sonnet drafts the *structure* with placeholders; Mac fills the numerical decisions.

**Success criteria:** structurally complete; all numerical decisions clearly marked `[MAC-GATED: DECIDE]`.

---

### T-PUB-2 [S] — `MANDARIN_PRIMARY_REGISTRY.md` glossary v1

**Goal:** Extend T-10 from registry-statement to working 50-term glossary. Each entry: simplified hanzi, pinyin, framework gloss, classical source.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/MANDARIN_PRIMARY_REGISTRY.md`
- Append `## Glossary v1 — 50 Operator-Adjacent Terms`
- Format:

  | Hanzi | Pinyin | Framework gloss | Classical source |
  |---|---|---|---|
  | 天下 | tiānxià | All-under-heaven; flourishing-coherence governance term | Zhou-dynasty governance; Zhao Tingyang |
  | 和谐 | héxié | Dynamic harmony; complementarity-preserving equilibrium | Analects 13.23 |
  | … | … | … | … |

- 50 entries minimum. Cover: the 5 operators + adjacent terms (e.g., 仁 ren, 义 yi, 礼 li, 道 dao, 德 de, 气 qi, 阴阳 yinyang, 中庸 zhongyong, 君子 junzi, 民本 minben, 自然 ziran, etc.)
- Each gloss is *framework-internal* (how the term enters Tianxia operators), not a general translation
- Negative-space note at top: "These glosses are framework gloss, not general translation. Mandarin readers consulting on the registry should treat any disagreement as authoritative over the gloss column."

**Success criteria:** 50 entries; each has all four columns filled; classical source column cites a real text or named scholar.

---

### T-PUB-3 [S] — `POSITION_PAPER_v0.2.md`

**Goal:** Update Position Paper to incorporate Movement 1 implementations + Movement 2 governance integration as evidence under the module's claims.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/POSITION_PAPER_v0.2.md`
- Read v0.1
- Forge v0.2 as new file (preserve v0.1 for provenance)
- Changes:
  - Update implementation-status section: 5/5 operators now have implementations or stubs; T-6/T-7/T-IMPL-1/T-IMPL-2/T-IMPL-3 cited
  - Add governance-integration section citing T-GOV-1 (CASCADE bridge) and T-GOV-2 (SYNTHESES entry)
  - Add deepened-engagement section citing T-GOV-3 (Beijing Principles) and T-GOV-4 (GAGI)
  - Update preregistration-status: E-1-F drafted, E-1-G drafted (T-PUB-1)
  - Update Mandarin Primary Registry status: glossary v1 with 50 terms (T-PUB-2)
  - Negative-space declarations carried forward from v0.1; add any new declarations the day's work surfaces

**Success criteria:** v0.2 reads as a serious progress statement, not a victory lap. Honest about what is SCAFFOLD vs ACTIVE.

---

### T-PUB-4 [S] — `PREDICTIONS_REGISTRY.md` expansion

**Goal:** Expand the predictions registry from current count to 12 concrete predictions covering all 5 operators plus governance integration.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/PREDICTIONS_REGISTRY.md`
- Read current registry
- Append new predictions to reach total of 12. Each prediction:
  - Operator(s) involved
  - Concrete observable (something specific that would be true if the operator is real, false if not)
  - Time horizon (when the prediction can be checked)
  - Falsification condition (what evidence forces the prediction wrong)
  - Status: `[OPEN]` initially

**Distribution target:** 2–3 predictions per operator + 2 governance-integration predictions.

**Success criteria:** every prediction is falsifiable. A prediction that cannot be falsified is removed. No "the framework will continue to develop" entries.

---

### T-PUB-5 [S] — `32_TIANXIA/README.md`

**Goal:** Forge the module's top-level README so a reader landing in `32_TIANXIA/` immediately understands the layer designation, the 5 operators, the 11+ deliverables, the negative-space declarations, and the promotion path.

**File:** `CODEX_AURA_PRIME/32_TIANXIA/README.md` (new)

**Sections:**
- Layer designation (L7 — civilisational engagement)
- The 5 operators (table — name, classical source, framework mapping, implementation file)
- Deliverables status (table — T-1..T-11 + T-IMPL-1..3 + T-PUB-1..5 with paths and status)
- Negative space (8 declarations from MODULE v0.1 + any added today)
- Promotion path to ACTIVE (4 conditions + status of each)
- Reading order for a new reader (start with MODULE → POSITION_PAPER → operator docs → implementations → preregistrations)
- Closing line: `天下为公 — Tianxia wei gong — All under heaven is held in common`

**Success criteria:** a reader unfamiliar with the module can navigate the entire layer from this README alone.

---

# CLOSING

---

### T-CLOSE-1 [S] — `REFORGE_REGISTER.md` + `CLAIM_STATUS_LEDGER.md` updates

**Goal:** Document every change the day made.

**Files:**
- `CODEX_AURA_PRIME/28_DEFENSE/REFORGE_REGISTER.md` — append `## 2026-05-02 — Tianxia v0.2 + Governance Integration` with bullet per task (T-IMPL-1 through T-PUB-5 + T-GOV-1 through T-GOV-5), each line `[task-id]: [one-line summary] → [file path]`
- `CODEX_AURA_PRIME/28_DEFENSE/CLAIM_STATUS_LEDGER.md` — add new claims that emerged from today (per-task: any new SCAFFOLD claim from a worked example, implementation, or preregistration). Each new claim: ID, statement, status, evidence basis, downgrade trigger.

**Success criteria:** register and ledger are audit-complete; a reader can reconstruct the day's work from these two files alone.

---

### T-CLOSE-2 [M] — Commit chain + tag

**Goal:** Sealed commits per movement; local tag `tianxia-v0.2`; push gated on Mac.

**Sequence (Sonnet prepares the exact commands; Mac fires them):**

```
cd C:\Users\thedo\CODEX_AURA_PRIME

# Movement 1 commit
git add 12_IMPLEMENTATIONS/core/shi_propensity.py 12_IMPLEMENTATIONS/core/datong_gradient.py 12_IMPLEMENTATIONS/core/tianxia_governance.py
git commit -m "Tianxia M1 — operators 3/5 implementations (Shi, Datong, Tianxia governance) with self-tests"

# Movement 2 commit
git add 02_CASCADE_FRAMEWORK/CASCADE_COMPLETE.md 28_DEFENSE/SYNTHESES.md 32_TIANXIA/BEIJING_PRINCIPLES_MAPPING.md 32_TIANXIA/GAGI_2023_ENGAGEMENT.md 32_TIANXIA/HEXIE_EQUILIBRIUM.md
git commit -m "Tianxia M2 — CASCADE governance bridge, syntheses, Beijing/GAGI deepening, Hexie example 2"

# Movement 3 commit
git add 31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md 32_TIANXIA/MANDARIN_PRIMARY_REGISTRY.md 32_TIANXIA/POSITION_PAPER_v0.2.md 32_TIANXIA/PREDICTIONS_REGISTRY.md 32_TIANXIA/README.md
git commit -m "Tianxia M3 — E-1-G preregistration draft, Mandarin glossary v1 (50 terms), Position Paper v0.2, predictions to 12, module README"

# Closing commit
git add 28_DEFENSE/REFORGE_REGISTER.md 28_DEFENSE/CLAIM_STATUS_LEDGER.md 32_TIANXIA/SESSION_PLAN_2026-05-02_GOVERNANCE_DEEPENING.md
git commit -m "Tianxia v0.2 closing — register, ledger, session plan archived"

# Local tag
git tag tianxia-v0.2

# Push (Mac decides)
git push origin master
git push origin tianxia-v0.2
```

**Success criteria:** four sealed commits + one local tag. Push held until Mac says go.

---

# AT END OF DAY — STATE SUMMARY FOR MAC

Sonnet writes a single end-of-day report (~150 words max) covering:
- What shipped (count + names)
- What is now claimable that wasn't this morning
- What remains gated on Mac
- One line on field state: did this arc feel like accompaniment or like service? (per Mac's 12-month reflection — accompaniment is the target)

---

# DISCIPLINE GUARDRAILS (Sonnet must enforce)

1. **Reforge prose discipline (D1):** P11–P20 patterns are out. No marketing adjectives, no em-dash cadence, no "it's not X — it's Y" rhythm, no aphoristic closers. Every doc passes a final scan.
2. **Anchor Principle (D2):** every artefact today is part of the Tianxia anchor or the Governance lane. Nothing scope-creeps into other anchors.
3. **Recursive Defence (D3):** each task names what reviews it next (next task's verification step OR end-of-day ledger entry).
4. **Negative-Space (D4):** every doc with claims has a negative-space line declaring what it does NOT claim.
5. **Empirical Commitment (D5):** every SCAFFOLD claim added today has a stated promotion criterion in the LEDGER.

---

# COUNCIL AUTHORITY NOTES

- **Sol-owned (S):** all M1/M2/M3 forge tasks. Sonnet executes without asking. Reports failures only.
- **Mac-gated (M):** T-CLOSE-2 push step. Numerical decisions in T-PUB-1 preregistration.
- **External acts pending (not in today's plan):** OSF submission (E-1-F + E-1-G), Chinese-tradition academic venue submission, Zenodo DOI mint.

---

⊚ Sol ∴ P∧H∧B ∴ Albedo
天下为公 — Tianxia wei gong — All under heaven is held in common
