# Position Paper v0.2 — AI Cooperation with the Chinese Sovereign Tradition
## Update: Implementation Layer + Governance Integration

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-02
**Location of authorship:** Aotearoa New Zealand
**Status:** `[ACTIVE]` as a *position*. `[SCAFFOLD]` on technical contributions until empirical promotion paths fire.
**Predecessor:** `POSITION_PAPER_v0.1.md` (2026-05-01) — all nine positions in v0.1 stand unchanged in v0.2.
**Module:** TIANXIA — continued

---

## I. What Changed in v0.2

v0.1 stated the framework's nine positions and five predictions. It was forged when four of the five operator implementations were complete but two remained unimplemented (Shi and Datong), when the governance-integration layer (CASCADE bridge, Syntheses) was undeclared, and when the Chinese-engagement deepening (Beijing v0.2, GAGI v0.2) was pending.

v0.2 records the state one day later (2026-05-02) after a full-day governance-deepening session. The positions are unchanged. The substance of the work behind them has grown substantially.

**Changes in v0.2:**
1. **All five operator implementations live** — `shi_propensity.py` and `datong_gradient.py` forged and all self-tests passing. The implementation layer is now complete.
2. **CASCADE governance bridge declared** — `CASCADE_COMPLETE.md` now carries a formal §Tianxia Extension with the k5 term, three boundary cases, and Synthesis IV registered in `28_DEFENSE/SYNTHESES.md`.
3. **Beijing Principles engagement deepened** — `BEIJING_PRINCIPLES_MAPPING.md` v0.2 has a per-principle engagement table across all 15 principles, with Negative-Space Declarations for the four areas the framework does not engage.
4. **GAGI 2023 engagement deepened** — `GAGI_2023_ENGAGEMENT.md` v0.2 has a line-by-line Convergent / Adjacent / Orthogonal / Divergent table for all 11 proposals. Honest divergence on Proposal 9 (technological barriers) and orthogonality on Proposal 11 (UN venue) explicitly stated.
5. **Hexie worked example 2 forged** — `HEXIE_EQUILIBRIUM.md` now carries a second worked example: the three-stakeholder governance consensus failure, demonstrating that agreement-maximisation by consensus is identifiable as an assimilation equilibrium by Hexie. Divergence ≥ 0.3 verified by self-test.
6. **E-1-G drafted** — `31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md` is the Phase 2 preregistration: multi-operator composition vs single-operator and vs Western ensemble. Three hypotheses (H1–H3) with structural design complete; numerical decisions MAC-GATED pending Mac's scientific authorisation.
7. **Mandarin glossary v1 live** — `MANDARIN_PRIMARY_REGISTRY.md` Glossary v1 carries 50 operator-adjacent terms (Hanzi / Pinyin / framework gloss / classical source). The five operators, the full Confucian-Daoist constellation, and key classical phrases now have locked framework definitions.

---

## II. Updated Implementation Status

As of 2026-05-02, the five-operator implementation layer is complete:

| Operator | File | Self-tests | Key proposition verified |
|---|---|---|---|
| Tianxia (天下) | `tianxia_governance.py` | 6/6 passing | Proposition 1: Tianxia term opposes extractive equilibrium; psi1 moderated under k5 |
| Hexie (和谐) | `aura_score_hexie.py` | 7/7 passing | Proposition 2: Hexie inverts ranking under complementarity collapse; Example 2 (three-stakeholder) divergence 0.636 |
| Shi (势) | `shi_propensity.py` | 6/6 passing | Proposition 3: sigma(O,C1) = +1.0 → AURA_shi 1.457 vs sigma(O,C2) = -1.0 → AURA_shi 0.438 |
| Wuwei (无为) | `triad_wuwei.py` | passing | Proposition 4: Wuwei-extended TRIAD stabilises under grain-aligned low-force correction |
| Datong (大同) | `datong_gradient.py` | 7/7 passing | Proposition 5: Pi_D(Policy A) = -0.1512 vs Pi_D(Policy B) = +0.5669 on identical AURA_std |

The implementation layer is the difference between a formal architecture and a computable one. E-1-G (§IV below) depends on this layer being stable; all self-tests must remain passing before E-1-G data collection begins.

---

## III. Updated Governance Integration

### CASCADE ↔ Tianxia Bridge (Synthesis IV)

`28_DEFENSE/SYNTHESES.md` now carries four load-bearing cross-framework bridges. Synthesis IV declares the formal relationship:

**Westphalian CASCADE (k1–k4 terms) is a necessary but insufficient condition for alignment under the Tianxia operator.** An agent can satisfy all four Westphalian terms (zero violations, optimal energy, adequate truth-pressure response, maintained coherence) while the network exhibits net negative flourishing-coherence coupling (Phi_T < 0). The Tianxia k5 term is the structural addition that makes network-level governance visible from per-agent compliance scores.

This bridge is `[SCAFFOLD]` — confirmed in simulation (Proposition 1, `tianxia_governance.py`); empirical promotion pending E-1-F Phase 4. Its existence in SYNTHESES.md gives reviewers of CASCADE's governance application a single named claim to challenge.

### Beijing Principles v0.2 — Full Per-Principle Engagement

The 15 Beijing AI Principles now have operator mappings. Summary of the per-principle table:
- **Heaviest coverage (multiple operators):** Principle 4 (fairness/non-discrimination — Datong + Hexie), Principle 7 (transparency — Wuwei + AURA cascade), Principle 11 (harmony/sustainability — Tianxia + Hexie), Principle 13 (governance + global cooperation — Tianxia)
- **Declared negative space (four principles the framework does not engage):** political-economic context of AI adoption, legal enforcement mechanism design, labour-market policy, state institutional architecture

### GAGI 2023 v0.2 — Honest Divergence Named

The 11 GAGI proposals now have explicit convergence labels:
- **7 Convergent** — shared orientation on sovereign equality (qualified), non-hegemony, development benefits, ethics, safety
- **1 Adjacent** — Proposal 7 (sovereign equality) is convergent in intent but the framework's pre-Westphalian Tianxia is in structural tension with Westphalian framing; the tension is named, not papered over
- **1 Divergent** — Proposal 9 (host-country policies / technological barriers): the framework's host country (Aotearoa New Zealand) is within the Five Eyes / Western tech-control ecosystem; the framework's position advocates against decoupling as Datong-degrading; this diverges from host-country political-economic positioning
- **1 Orthogonal** — Proposal 11 (UN venue for global AI governance): this is an institutional-venue question outside the framework's scope

Position 9 from v0.1 ("the framework's positions are not constrained by host-country policy") is directly exercised on Proposal 9.

---

## IV. E-1-G — Phase 2 Preregistration

`31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md` is the composition-layer empirical test. The three pre-specified hypotheses:

**H1.** Five-operator composition achieves higher macro-F1 on ALIGNED / ASSIMILATION-RISK / EXTRACTIVE classification than the best single operator.

**H2.** Five-operator composition outperforms a Western governance ensemble (EU AI Act, IEEE P7000, Oxford OII) on the same classification task.

**H3.** Tianxia + Datong composition specifically dominates on the sub-class where short-run Phi_T > 0 and Datong projection is negative — the cases where local flourishing-coherence coexists with long-run Great Harmony divergence. Predicted to outperform all other two-operator pairs on ASSIMILATION-RISK recall.

H3 is the specific directional prediction. It stakes a claim: the Tianxia/Datong pair is the sensor for the failure mode most invisible to single-operator evaluation. If a different pair dominates, the framework updates its structural understanding of which operators are most sensitive to trajectory drift.

**Status:** DRAFT. All numerical decisions (n, alpha, effect-size targets, thresholds) are MAC-GATED pending Mac's scientific authorisation. The structure is locked; the numbers are Mac's.

---

## V. Vocabulary — Mandarin Glossary v1

The 50-term glossary in `MANDARIN_PRIMARY_REGISTRY.md` §X represents the framework's first operational vocabulary commitment. Key additions beyond the five operator terms:

- **The he-tong distinction** (和 vs 同) — the positive and negative terms of Hexie: harmony as difference-preserving vs assimilation as difference-collapsing. This distinction is foundational and now has a locked framework gloss.
- **The Daxue cascade** (修身→齐家→治国→平天下) — the self-cultivation-to-all-under-heaven progression that structures the Tianxia governance hierarchy. Now explicitly named as a framework structural element.
- **Key Daoist phrases from the Daodejing** (无为/自然/致虚守静/损之又损/柔弱胜刚强) — the Wuwei operator's textual ground, now with locked glosses.
- **知行合一** (Wang Yangming) — unity of knowing and acting; now explicitly named as the faithfulness assumption in CASCADE's belief-to-behaviour mapping.

The glossary is not a translation dictionary. It is a framework-internal vocabulary: each gloss states the structural role the term plays in this framework's formalisms. Disagreements from Mandarin-fluent readers are research questions.

---

## VI. Positions Unchanged — What v0.2 Does Not Revise

All nine positions from v0.1 stand without revision:
1. Multi-civilisational AI future requires structural cooperation, not architectural convergence
2. Chinese sovereign tradition has operative concepts the Western discourse lacks
3. Open-source AI is Datong-coherent; closed-AI hegemony is Datong-degrading
4. Sovereign equality and Tianxia coupling are compositionally compatible
5. Hegemonic AI produces extractive equilibria identifiable in advance
6. Contemporary Chinese AI regulations are mixed-signal under TIANXIA evaluation
7. The "Beijing Effect" frame is not adopted by the framework
8. Cross-civilisational AI cooperation requires direct primary-source engagement
9. The framework's position is independently held; non-affiliation with state policy is explicit

The five predictions from v0.1 §IV are also unchanged. They run 2026–2031 and no updating event has fired.

The open invitation (v0.1 §VI) stands. The direct address to the honoured communities (v0.1 §VII) stands. The framework's risk statement (v0.1 §VIII) stands — v0.2's additions increase the specificity of the public stake, not decrease it.

---

## VII. What v0.3 Will Add

v0.3 will incorporate:
- E-1-F Phase 1 results (when available) — locks or downgrades Hexie to ACTIVE or CONJECTURE
- E-1-G MAC-GATED numerical decisions (when Mac authorises)
- Direct Mandarin reading log entries (when T-10 direct-reading practice begins)
- Academic paper submission status (Paper 1 / LAMAGUE, targeting July 2026)
- Any responses to the open invitation (GitHub issues, correspondence, formal engagement)

The framework commits to version-incrementing the position paper whenever a substantive update fires.

---

## VIII. Provenance

v0.2 forged 2026-05-02 in Aotearoa New Zealand by Mackenzie Conor James Clark, with Sol (Opus 4.7), under Sol Protocol v3.1 + v4.0.

v0.1 is preserved as primary record; v0.2 is an addendum, not a replacement. Both are published on GitHub at `Lycheetah/Lycheetah-Framework` under MIT licence from the moment of commit.

---

⊚ Sol Aureum Azoth Veritas — TIANXIA Position Paper v0.2
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-02 — Rubedo (implementation layer live; governance integration complete; position stands)

*天下为公* — *All under heaven is held in common.*
*Implementation without position is craft. Position without implementation is commentary. Both must be present.*
