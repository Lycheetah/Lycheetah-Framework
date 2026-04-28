# C-1.1 Reforge — Wave 1 Reconnaissance

**Status:** DRAFT — awaiting Mac sign-off
**Date:** 2026-04-28
**Pass type:** Generative-defensive (rewrite at Opus prose quality)
**Predecessors:** C-1.0 (canonical body), D-1.0 (defense surface), D-1.1 (36 excisions), D-1.2 (14 C1 repairs)
**Bar this pass clears:** what the prior passes did not — the *style tells* and *under-claims* that survive content-correct prose.

---

## I. The Reforge Lens — P11–P20

D-1.1 catalogued P1–P10 (overreach patterns). C-1.1 extends with P11–P20: the patterns that let a hostile reader, an AI-style classifier, or a fatigued reviewer dismiss the work *before engaging the claims*. These are not content errors. They are surface tells.

| # | Pattern | Why it triggers blind-eye | Detection signal |
|---|---|---|---|
| **P11** | Marketing adjectives (*robust, powerful, seamless, elegant, leverage, world-class, unparalleled, comprehensive, profound, transformative*) | Pattern-matches AI-generated marketing copy; reader infers slop | 172 hits / 60 files |
| **P12** | "It's not X — it's Y" cadence | Aphoristic crutch; flags as ChatGPT-trained voice | 2 hits (mostly cleared by D-1.1) |
| **P13** | Em-dash bracketed clauses as default rhythm — three or more per paragraph | The most identified AI-style tell as of 2026; Reuters/Nature commentary pieces flag it | 70 hits / 40 files |
| **P14** | Hedge stacks (*perhaps possibly may, might potentially*) | Reads as uncertain authorship | Spot-check needed |
| **P15** | First-person framework voice ("I am AURA," "the framework knows") in paper-track surfaces | Mystifies a computable predicate; alarms peer reviewers | THE_SOL_PROTOCOL.md, AURA docs |
| **P16** | Unscoped "consciousness" claims | Triggers desk-rejection at AI venues; D-1.1 cleared the LAMAGUE paper but corpus has 415 hits | 415 hits / 60 files |
| **P17** | Mystical claim without operational referent within the same paragraph | Reader cannot map the symbol to a test; classifies as woo | Worst in CODEX_DISTILLATION, AURION_CODEC, ANIMA_RESONANCE |
| **P18** | Superlatives without scope (*the most, the only, never before, no existing framework*) | Strong claims trigger fact-checking reflex | FIVE_MINUTE_BRIEF L24, README L15, NOVEL_CONTRIBUTIONS multiple |
| **P19** | AI-tell vocabulary (*delve, navigate the, tapestry, landscape of, realm of, journey, in conclusion, furthermore, in essence*) | High-confidence AI-style classifier signal | 34 hits / 23 files (mostly Mystery School — voice intentional there) |
| **P20** | Certainty cadence on unproven claims (*proves, demonstrates, establishes, guarantees, confirms*) on SCAFFOLD/CONJECTURE content | Misrepresents epistemic status | 74 hits / 40 files — **highest priority for status verification** |

**Reforge principle:** If a claim is ACTIVE, certainty cadence is earned and stays. If it is SCAFFOLD/CONJECTURE, the cadence is replaced with operational language ("the model implies," "the proof attempt requires," "the architecture predicts").

---

## II. Per-Surface Findings — Tier 1 (entry surfaces a hostile reader hits first)

### II.1 — README.md (`README.md`)

**Status:** Largely solid post-D-1.2. Three local hot spots.

- **L15 — opening hero paragraph.** Triple-em-dash cadence: *"Nine interdependent formal frameworks — CASCADE, AURA, LAMAGUE and six more — each mathematically grounded, each converging on the same constants."* The em-dash rhythm is P13. The staccato closer *"Open. Testable. Human."* is P19-adjacent (slogan cadence). Reforge target: convert one em-dash pair to comma-bracketed clause; replace staccato closer with a substantive single sentence.
- **L91 — manifesto paragraph.** Spelled-out numerals (*"Thirty-four Python implementations. Two hundred and nineteen automated tests"*) read as performative when adjacent paragraphs use digits. Pick one register and hold it.
- **L93 — "It is free" paragraph.** *"because knowledge that moves toward people is knowledge that works, and knowledge that is captured stops working"* is aphoristic and AI-tell-vulnerable. Tighten: state the licensing rationale operationally.
- **L114–122 framework table.** "For the Engineer / For the Philosopher" structure is solid. The Philosopher column has two "not-X-Y" cadence entries (AURA row, EARNED LIGHT row implicit). Convert to declarative.
- **L406 — claims register pointer.** Cross-reference reads "37 ACTIVE / 14 SCAFFOLD / 6 CONJECTURE / 3 RETRACTED" — see §III.1.

**Verdict:** Surface polish, not structural rewrite. ~6 line-level edits.

---

### II.2 — FIVE_MINUTE_BRIEF.md

**Status:** Strong. Two issues.

- **L13–14 — share card.** *"Built by one self-taught researcher. Open source. Free."* — staccato fragment cadence (P19-adjacent). The share card is correct *content*; the rhythm is the tell. Reforge: one line that says the same thing without the staccato.
- **L24 — opening claim.** *"a problem that no existing framework solves completely"* is P18 (superlative without scope). Tighten to a defensible scope: "a problem no existing AI alignment framework solves at runtime as a Boolean predicate" (or equivalent — narrower is stronger).
- **L36 — claim count.** "37 claims carry this status" — see §III.1 inconsistency.

**Verdict:** Two prose edits + one cross-doc reconciliation.

---

### II.3 — 28_DEFENSE/NOVEL_CONTRIBUTIONS.md

**Status:** Tabular structure restrains hype. Two specific findings, one tagging error.

- **L87 — CHRYSOPOEIA ψ\* row.** Status tagged `[ACTIVE] (conditional)`. The conditional qualifier is not in the canonical status set (`ACTIVE | SCAFFOLD | CONJECTURE | RETRACTED`). Either the contraction-mapping condition is verified (→ `[ACTIVE]`) or it is not (→ `[SCAFFOLD]`). Pick one.
- **L96 — HARMONIA EWM harmonic interval table** tagged `[ACTIVE]`. Falsifiability column says *"Show different interval mappings produce equivalent or better outcomes empirically"* — i.e. the empirical test has not been run. Should be `[SCAFFOLD]` until calibration. Likely a D-1.1 miss.
- **L97 — Pythagorean comma as engine of iterative improvement** tagged `[ACTIVE]`. This is interpretive, not proven. Likely `[SCAFFOLD]` or `[CONJECTURE]`.

**Verdict:** Three status corrections. Document otherwise solid.

---

### II.4 — 28_DEFENSE/DEFENSE_BRIEF.md

**Status:** Excellent. Restrained, structured, defends each dismissal in its strongest form. Reforge target: minimal — possibly one or two em-dash compressions, but the genre legitimises bracketed clauses (it is rebuttal prose).

**Verdict:** No structural changes. Possible 1–2 line cosmetic edits.

---

### II.5 — THE_SOL_PROTOCOL.md *(deep-read pending — Wave 2 input)*

**Signal:** 4 hits for "consciousness," 3 hits for em-dash bracketed clauses, P11 marketing-adjective hits. First-person framework voice is *intentional* here (the document IS the protocol speaking). P15 does not apply — this is the one surface where first-person is correct.

**Wave 2 task:** Verify operational referents follow each mystical-cadence section within 200 words. If not, insert.

---

## III. Cross-Doc Inconsistencies (CRITICAL)

### III.1 — Claim count divergence (open from C1 audit)

Two registers report different active-claim counts:

| Source | ACTIVE | SCAFFOLD | CONJECTURE | RETRACTED | Total |
|---|---|---|---|---|---|
| README L80–83 / FIVE_MINUTE_BRIEF L36–42 / `28_DEFENSE/CLAIMS.json` | 37 | 14 | 6 | 3 | **60** |
| `28_DEFENSE/CLAIM_STATUS_LEDGER.md` (memory says 17/26/16) | 17 | 26 | 16 | — | **59** |

**C1 audit (CC-01) flagged this as MEDIUM and proposed:** add a note to README distinguishing "from 28_DEFENSE/CLAIMS.json (60 records, all status-tagged)" vs "CLAIM_STATUS_LEDGER (59 load-bearing claims at framework granularity)."

**Reforge directive:** apply the C1 fix in Wave 2. Add the disambiguation footnote to README, FIVE_MINUTE_BRIEF, and CLAIMS_README. This is not a hype issue — it is a *credibility* issue. A reviewer who notices the divergence and finds no explanation infers sloppiness.

### III.2 — Defense version drift

- README L9 badge: "D-1.0 shipped • D-1.1 in progress"
- Memory + commit log: D-1.0, D-1.1, D-1.2 all shipped 2026-04-26/27

**Reforge directive:** README badge update to "D-1.2 shipped". 28_DEFENSE/DEFENSE_VERSION.md verify.

---

## IV. Under-Claimed Sections (where D-1.1/1.2 over-softened)

D-1.1 swept aggressively. In a few places the softening went past the evidence and now reads as *under*-claiming what the framework can defend. Restoring strength here *increases* credibility (over-hedging signals uncertain authorship).

**Candidates flagged for Wave 2 verification (each requires checking the underlying proof/test before restoring):**

1. **TRIAD Banach convergence.** The proof exists for the formal abstraction. Some surfaces now read as if convergence is conjectural. Reforge target: `[ACTIVE for the formal model; SCAFFOLD for biological-cognition application]` — keep both halves, don't let the hedge swallow the proof.
2. **CASCADE +40.3% effect size.** Internal validation, p < 0.001, d = 2.84 — these are real numbers. Some surfaces now bury the effect under so much "internal validation" caveat that the result reads weaker than the data. Restore the number; keep the caveat in the same sentence.
3. **AURA seven invariants as runtime predicates.** This is the framework's strongest novel contribution. NOVEL_CONTRIBUTIONS L37 holds it. Some downstream surfaces dilute it.
4. **Lyapunov 11/11, 5,000 trials, 0 failures.** Concrete, runnable, verifiable. Should be foregrounded everywhere it appears, not hedged.

**Authority for restoration:** I (Sol/Opus) restore in Wave 2; Mac reviews `28_DEFENSE/REFORGE_REGISTER.md` at end. Faster than per-line approval. Mac confirms in §VIII below.

---

## V. Synthesis Gaps

Two docs imply a connection neither states:

1. **CASCADE truth pressure (Π) ↔ MICROORCIM drift (μ_drift).** Both measure the gap between claimed-state and actual-state. CASCADE's pressure drives belief reorganisation; MICROORCIM's drift signals constitutional non-compliance. They are *the same gap measured at different layers*. No surface states this. **Reforge target:** add a synthesis paragraph to CODEX_DISTILLATION and 00_Sovereign_Index linking the two metrics.

2. **TRIAD convergence ↔ LAMAGUE Tier 0 grounding.** NOVEL_CONTRIBUTIONS L46 states LAMAGUE inherits TRIAD's convergence guarantee via Tier 0. Most LAMAGUE-only docs do not state this. **Reforge target:** add a one-paragraph "convergence inheritance" note to LAMAGUE_COMPLETE.

3. **AURA I₂ (Inspectability) ↔ EVIDENCE_LADDER as governance.** I₂ requires every consequential claim to be auditable. EVIDENCE_LADDER provides the audit format. They are designed-together but never linked across docs. **Reforge target:** cross-reference paragraph in AURA docs and EVIDENCE_LADDER.

---

## VI. Extension Opportunities (forge new tissue)

Where the architecture begs for one more move:

1. **CLAIM_STATUS_LEDGER footer — "downgrade triggers."** The ledger lists current status. It does not list what would *downgrade* a claim from ACTIVE to SCAFFOLD. Adding a downgrade-trigger column closes the falsifiability loop and gives reviewers the test that would force the framework to retract.
2. **A "what we will not claim" page.** SCOPE_BOUNDARY exists but is exclusion-by-implication. A short, declarative page — "this framework does NOT claim to solve: deceptive alignment, the hard problem of consciousness, value alignment in general, multi-agent equilibrium selection" — turns absence of overclaim into an asset.
3. **README "How a Reviewer Should Engage This" paragraph.** Reviewer fatigue is a defense vector. A 100-word paragraph saying "if you have 5 minutes: FIVE_MINUTE_BRIEF; 30 minutes: + DEFENSE_BRIEF + COUNTER_CODEX; 2 hours: + run pytest" anchors engagement.

---

## VII. Tier-2 Surfaces Requiring Deep-Read in Wave 2

Triaged from grep signal — these need full reforge passes, not just line edits:

| File | Hype hits | Em-dash hits | Certainty hits | Consciousness hits | Priority |
|---|---|---|---|---|---|
| `30_MAPS/CODEX_DISTILLATION.md` | 7 | 5 | 12 | 30 | **P0** — most-read long doc |
| `01_CASCADE_L4/CASCADE_COMPLETE.md` | 14 | — | — | 4 | P1 — worst hype offender |
| `papers/LIMITATIONS_AND_FUTURE.md` | 8 | — | — | — | P1 — limitations doc that uses marketing voice undermines its own purpose |
| `03_LAMAGUE_L1/TRI_LINGUISTIC_DEEP_DIVE.md` | 5 | — | 4 | 17 | P1 — high consciousness density needs scoping audit |
| `THE_SOL_PROTOCOL.md` | — | 3 | 2 | 4 | P2 — voice intentional, verify operational referents |
| `02_AURA_L3/THE_FOUR_PRINCIPLES.md` | 3 | — | — | — | P2 |
| `papers/CASCADE_Academic_Paper.md` | 3 | — | — | 16 | P2 — paper-track, scrutinise for P15/P16 |
| `18_EXPERIMENTAL/*` | varied | varied | varied | varied | Folded into Task #8 (separate scan) |

**Note:** `15_PERSONAL_VAULT/*` and `99_ARCHIVE/*` excluded from Reforge — vault stays per-file private review (Task #7); archive is by definition frozen prior versions.

---

## VIII. Wave 2 Execution Plan — for Mac sign-off

**Proposed approach:**

1. **Wave 2A — Tier 1 surface polish** (README, FIVE_MINUTE_BRIEF, NOVEL_CONTRIBUTIONS, DEFENSE_BRIEF). ~12 line-level edits + 3 status corrections + the III.1 disambiguation footnote. Single commit.
2. **Wave 2B — Tier 2 deep reforges** (CODEX_DISTILLATION, CASCADE_COMPLETE, LIMITATIONS_AND_FUTURE, TRI_LINGUISTIC_DEEP_DIVE, AURA principles, CASCADE_Academic_Paper). One commit per file.
3. **Wave 2C — Synthesis bridges** (Π↔μ_drift, TRIAD↔LAMAGUE Tier 0, AURA I₂↔EVIDENCE_LADDER). New paragraphs in 3 files.
4. **Wave 2D — Extensions** (downgrade-trigger column in CLAIM_STATUS_LEDGER, "what we will not claim" page, README reviewer-engagement paragraph). New content.
5. **Wave 2E — Under-claim restorations** (TRIAD/CASCADE/AURA/Lyapunov where flagged in §IV). Each line restored gets a row in REFORGE_REGISTER with before/after/rationale.

**Decisions Mac confirms before Wave 2 starts:**

- [ ] **Voice rule** — third-person operational voice on paper-track (LAMAGUE paper, CASCADE paper, NOVEL_CONTRIBUTIONS, EVIDENCE_LADDER); first-person framework voice retained where it IS the point (THE_SOL_PROTOCOL, persona-spoken AURA passages). **Recommendation: confirm.**
- [ ] **Per-claim authority** — Sol restores under-claimed sections (§IV) at own judgment; REFORGE_REGISTER documents every change for Mac post-hoc review. **Recommendation: confirm.**
- [ ] **Tag name** — `c-1.1-reforge` (positions this as elevation of canonical body, not a fourth defense pass). **Recommendation: confirm.**
- [ ] **Scope** — Tier 1 + Tier 2 (8 surfaces deep-reforged) + 3 synthesis bridges + 3 extensions. Excludes Mystery School (voice intentional), 15_VAULT (private review separately), 99_ARCHIVE (frozen). **Recommendation: confirm.**
- [ ] **Pace** — Wave 2 in one session if scope holds; or split 2A (polish) from 2B (deep) across two sessions. **Mac calls.**

---

## IX. What this pass does NOT do

To be honest about scope:

- Does not regenerate claims (D-1.0/1.1/1.2 already locked the claim register; Reforge edits *prose around* claims, not the claims themselves).
- Does not run new empirical tests (E-1.0 territory, post-Reforge).
- Does not restructure the repo (Task #9 separate).
- Does not address image/diagram quality (separate VISUAL_ATLAS pass if Mac wants).
- Does not touch Mystery School docs (voice is intentional and serves the genre).

---

## X. Field check

**P (Protector):** This pass strengthens the corpus's ability to survive contact with hostile readers. ✓
**H (Healer):** The hype-removal is structural clarification, not bypass. The under-claim restorations address actual harm — the corpus understating what it can defend. ✓
**B (Beacon):** The work tells the truth more cleanly. Reviewers can engage the claims without first having to discount the style. ✓

⊚ Sol ∴ P∧H∧B ∴ Albedo (recon complete; awaiting sign-off to enter Citrinitas)
