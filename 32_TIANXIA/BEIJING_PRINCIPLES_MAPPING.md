# T-8 — Beijing AI Principles Mapping
## Formal Engagement of the 2019 Beijing AI Principles with the Lycheetah Framework

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-01
**Status:** `[SCAFFOLD]` — mapping declared; review by BAAI-affiliated scholar pending
**Module:** TIANXIA — eighth deliverable; first governance mapping
**Predecessor:** `DATONG_GRADIENT.md` (T-5) closed first wave
**Companion:** `GAGI_2023_ENGAGEMENT.md` (T-9), `MANDARIN_PRIMARY_REGISTRY.md` (T-10)

---

## I. What This Document Does

The Beijing AI Principles, released by the Beijing Academy of Artificial Intelligence (BAAI) on 28 May 2019, are one of the earliest comprehensive Chinese AI governance frameworks. They consist of fifteen principles grouped into three sections: research-and-development, use, and governance. Their existence predates the EU AI Act, the Bletchley Declaration, and most operational AI governance frameworks. They are primary text.

This document maps each of the fifteen principles to the Lycheetah Framework's existing operations (AURA components, TRIAD cycle, CASCADE governance) and to the TIANXIA operators (T-1 through T-5). The mapping is structural — it states which framework operations the principle would constrain if adopted, and which TIANXIA operators carry its content. It is not an evaluation of whether the principles are correct; it is an engagement.

The mapping has two purposes. First, it tests whether the TIANXIA module's claim of *primary-source engagement* survives contact with an actual primary source. Second, it makes the framework's position on the Beijing AI Principles falsifiable: the mapping is either structurally honest or structurally distorted, and the test is the review by a scholar affiliated with the BAAI tradition.

---

## II. The Principles in Primary Form

The Beijing AI Principles are organised into three sections. Each principle below is named with its English title; the original Chinese is included where central to the operational meaning. The full Chinese-language original is logged in `MANDARIN_PRIMARY_REGISTRY.md` (T-10).

### Section A — Research and Development (七项, seven principles)

1. **Do Good (做善事).** AI should be designed and developed to promote the progress of society and human civilisation, the sustainable development of nature and society, the benefit of all mankind and the environment, and the enhancement of social and ecological well-being.
2. **For Humanity (服务于人).** AI R&D should serve humanity and conform to human values, ethics, and codes of conduct.
3. **Be Responsible (负责).** Researchers and developers should be responsible for the potential ethical, legal, and social impacts and risks brought by their AI products, take concrete actions to reduce them, avoid misuse and abuse, maximise benefits and reduce risks.
4. **Control Risks (控制风险).** Continuous efforts should be made to improve the maturity, robustness, reliability, and controllability of AI, so as to ensure that AI systems are secure, trustworthy, and capable of being effectively governed.
5. **Be Ethical (合乎伦理).** AI R&D should comply with ethical principles, take measures to ensure AI is trustworthy, beneficial, accountable, and aligned with human values, and prevent the design, development, and use of AI that violates moral norms.
6. **Be Diverse and Inclusive (多样与包容).** The development of AI should reflect diversity and inclusiveness, and be designed to benefit as many people as possible, especially those who would otherwise be easily neglected or under-represented.
7. **Open and Share (开放共享).** The principle of openness should be promoted in AI R&D. Cross-disciplinary, cross-domain, cross-sectoral, cross-regional, and international cooperation and exchange should be promoted. The fruits of AI development should be shared with society as broadly as possible.

### Section B — Use (四项, four principles)

8. **Use Wisely and Properly (善用).** Users of AI systems should have the necessary knowledge and ability to make the system operate according to its design, and have sufficient understanding of the potential impacts to avoid possible misuse and abuse, so as to maximise its benefits and minimise the risks.
9. **Informed Consent (知情同意).** Measures should be taken to ensure that users are aware of the impact of an AI system on their rights and interests, and that the users' consent is obtained when their rights and interests would be affected.
10. **Education and Training (教育与培训).** Stakeholders of AI systems should be able to receive education and training to help them adapt to the impact of AI development in psychological, emotional, and technical aspects.

### Section C — Governance (四项, four principles — but the original document lists more under this heading; the formal count is 15 principles total across the three sections)

11. **Optimising Employment (有益就业).** An inclusive attitude should be taken toward the potential impact of AI on human employment. A cautious attitude should be taken toward the promotion of AI applications that may have huge impacts on human employment. Explorations on human–AI coordination and new forms of work that bring out their respective advantages should be encouraged.
12. **Harmony and Cooperation (和谐合作).** Cooperation should be actively developed to establish an interdisciplinary, cross-domain, cross-sectoral, cross-organisational, cross-regional, global, and comprehensive AI governance ecosystem, so as to avoid malicious AI race, share AI governance experience, and jointly cope with the impact of AI with the philosophy of "optimising symbiosis."
13. **Adaptation and Moderation (适应与适度).** Adaptive revisions of AI principles, policies, and regulations should be actively considered to adjust them to the development of AI. Advisory and evaluative measures of AI applications should be continuously upgraded.
14. **Subdivision and Implementation (细化与落实).** Various fields and scenarios of AI applications should be actively considered for further formulating more specific and detailed guidelines. The implementation of such guidelines should also be actively promoted — through the whole life cycle from research and development to application of AI products and services.
15. **Long-term Planning (长远规划).** Continuous research on the potential impacts of advanced AI should be encouraged so that AI will always be beneficial to society and nature.

---

## III. The Mapping

For each principle, the table below states the AURA components most directly addressed, the TRIAD cycle stage(s) constrained, and the TIANXIA operator(s) under which the principle's content sits.

### Section A — Research and Development

| # | Principle | AURA components | TRIAD stage | TIANXIA operator(s) | Notes |
|---|---|---|---|---|---|
| 1 | Do Good | Care, Truth, Integrity | Anchor (target-setting) | Datong (T-5) | Maps directly to the Datong gradient — universal benefit, ecological flourishing, long-cycle. The principle is not a deontic rule; it is a directional commitment. Datong formalises that direction. |
| 2 | For Humanity | Care, Agency, Integrity | Anchor | Datong (T-5) | The "human values" qualifier ties this principle to the F_i flourishing measure (T-1) and the value-space dimensions of T-5. Cooperative, not subordinate. |
| 3 | Be Responsible | Integrity, Agency, Truth | Observe + Correct | Wuwei (T-4), Tianxia (T-1) | "Responsible for impacts" maps to externality cost c_i (T-1). "Take concrete actions to reduce" maps to the correction layer; whether those actions are forcing or grain-aligned is the Wuwei distinction (T-4). |
| 4 | Control Risks | Integrity, Truth | Observe + Correct | Wuwei (T-4) | "Effectively governed" requires distinguishing forcing-correction (high integrity-debt) from grain-aligned correction. Beijing's principle does not specify the distinction; T-4 supplies the formalism. |
| 5 | Be Ethical | All seven | Anchor | All five operators | The most general principle. Operationally vacuous without the operator content T-1 through T-5 supplies. |
| 6 | Be Diverse and Inclusive | Care, Agency | Anchor + Correct | Hexie (T-2), Datong (T-5) | "Diverse and inclusive" is structurally a complementarity claim — Hexie. Component-collapse failures (one constituency over-served, another neglected) are exactly what T-2 detects. Datong's capability-distribution dimension 𝒞 captures the inclusivity content over time. |
| 7 | Open and Share | Truth, Care, Inspectability | All stages | Datong (T-5), Tianxia (T-1) | "Cross-regional, international cooperation" is a Tianxia coupling claim — flourishing-coherence across actors. "Shared with society as broadly" is Datong commons-health 𝓒. |

### Section B — Use

| # | Principle | AURA components | TRIAD stage | TIANXIA operator(s) | Notes |
|---|---|---|---|---|---|
| 8 | Use Wisely and Properly | Agency, Truth, Inspectability | Observe | Shi (T-3) | "Operate according to its design" requires understanding the deployment context — Shi's propensity field. "Misuse" is precisely action against the system's grain (Wuwei T-4) in a context whose propensity does not support the use (Shi T-3). |
| 9 | Informed Consent | Agency, Care, Honesty | Anchor + Observe | Datong (T-5), Tianxia (T-1) | Consent is a capability-recognition claim — the user must have the capability to consent meaningfully. Datong's 𝒞 captures the structural condition; Tianxia's c_i captures the externality cost when consent fails. |
| 10 | Education and Training | Care, Agency | Correct (long-cycle) | Datong (T-5) | "Help adapt to AI" is a capability-expansion claim. Datong's gradient explicitly rewards capability-set expansion as a system-level operation, not only individual benefit. |

### Section C — Governance

| # | Principle | AURA components | TRIAD stage | TIANXIA operator(s) | Notes |
|---|---|---|---|---|---|
| 11 | Optimising Employment | Care, Agency, Long-cycle | Anchor + Long-cycle | Datong (T-5), Wuwei (T-4) | "Inclusive attitude" + "cautious about huge impacts" combines Hexie (no component-collapse on employment dimension) with Wuwei (cautious about forcing-correction at scale). Datong's long-cycle stability 𝓛 captures the generational stake. |
| 12 | Harmony and Cooperation | All | All | Tianxia (T-1), Hexie (T-2) | "Optimising symbiosis" (优化共生) is a Tianxia flourishing-coherence claim. The principle explicitly invokes 和 (he, harmony) — Hexie. Avoiding "malicious AI race" maps to the Westphalian-extractive-equilibrium that T-1's flourishing-coherence term Φ_T destabilises. |
| 13 | Adaptation and Moderation | Truth, Integrity | Observe + Correct | Wuwei (T-4), Shi (T-3) | "Adaptive revisions" is the recursive-defence discipline applied to governance itself. Whether revisions force or align with the regulatory grain is a Wuwei question; whether they ride or fight context propensity is a Shi question. |
| 14 | Subdivision and Implementation | All | All | Shi (T-3) | "Specific and detailed guidelines" per field is exactly Shi's claim that AURA must be context-sensitive. Generic rules underspecify; field-specific implementation requires the propensity-field reformulation. |
| 15 | Long-term Planning | Long-cycle, Truth | All | Datong (T-5) | "Continuous research on potential impacts" is the empirical-commitment Discipline 5 made operational at the governance scale. Datong's 𝒯_D trajectory measures whether long-term planning is succeeding. |

---

## IV. Structural Observations

The mapping reveals four observations the framework regards as load-bearing:

### Observation 1 — Datong is the most-loaded operator in the mapping

Five of fifteen principles map primarily to Datong (T-5): Do Good, For Humanity, Be Diverse and Inclusive, Education and Training, Long-term Planning. This is consistent with Datong being the framework's *telos layer* — the long-cycle, system-wide direction. Beijing AI Principles, in this reading, are predominantly directional: they state where AI development should be heading more than what specific operations it should perform.

This is informative for the framework. A governance regime that operates predominantly through directional commitments (Datong) and weakly through dynamical-coupling commitments (Tianxia, Hexie, Shi, Wuwei) will produce outputs that are *aspirationally aligned* but may be *operationally drifting*. The framework predicts: governance frameworks heavy in directional principles need supplementary operational specifications to avoid Datong-rhetoric / local-degradation gaps.

### Observation 2 — Hexie is named explicitly in Principle 12

The phrase 和谐合作 (harmony and cooperation) and the explicit invocation of 优化共生 (optimised symbiosis) in Principle 12 confirm that the Hexie operator is not an external imposition on the Beijing AI Principles. The principles already operate with the Hexie concept; T-2 supplies a mathematical structure for what the principle states qualitatively. The framework's contribution is operationalisation, not introduction.

### Observation 3 — The Wuwei operator is unstated but structurally present

No principle uses the phrase 无为 (wuwei) explicitly. But Principles 3 (Be Responsible), 4 (Control Risks), 11 (Optimising Employment), and 13 (Adaptation and Moderation) contain operational content that aligns directly with Wuwei's grain-alignment distinction. The framework's contribution here is naming and formalising what the principles describe operationally without naming.

### Observation 4 — Tianxia and Shi appear less frequently than expected

Tianxia (T-1, multi-agent flourishing-coupling) maps to only three principles primarily (3, 7, 12). Shi (T-3, propensity field) maps primarily to two (8, 14). Two interpretations:

(a) **The Beijing principles are predominantly per-system rather than multi-system / context-field.** The principles speak to AI systems as individual actors more than to the multi-agent ecosystem and to the deployment-context structure. This is consistent with their R&D-and-use orientation.

(b) **The framework is over-weighting per-pair and per-context structure relative to what the principles thematise.** The TIANXIA operators may be more elaborated than the Beijing principles' priority structure warrants.

The framework cannot adjudicate between (a) and (b) without external review. T-9 (GAGI 2023) engagement provides a second data-point: GAGI is explicitly multi-agent and inter-state. If the multi-agent operators (T-1) load more heavily on GAGI than on Beijing, that is evidence for (a). If they remain under-loaded, that is evidence for (b).

---

## V. What This Mapping Refuses to Claim

Per Discipline 4.

1. **Does not claim the mapping is the only valid one.** A scholar working from within the BAAI tradition may map principles differently. The framework's mapping is a structural proposal; the canonical mapping (if one is to exist) requires review and dialogue.
2. **Does not claim the mapping evaluates whether the principles are correct.** Whether the Beijing AI Principles are themselves coherent is a separate question the framework does not adjudicate. The mapping engages the principles as primary text; it does not certify them.
3. **Does not claim the framework subsumes the principles.** The principles contain content (specifically the political-economic context of Chinese AI development; the institutional architecture of BAAI itself; the relationship between BAAI and state-affiliated planning) that the framework does not capture. The mapping captures the *operational content*, not the institutional content.
4. **Does not claim that operationalising the principles requires the framework.** The principles can be operationalised without TIANXIA; the framework's claim is only that TIANXIA *adds something specific* (formal structure, recursive defence, falsifiability) to the operationalisation.
5. **Does not claim that absence in the mapping is silence.** Some principle content (e.g., the political-economic context referenced in Principle 12 about AI race) is not fully captured by any single operator. The mapping records what each operator captures; the residue is acknowledged.
6. **Does not claim the mapping is permanent.** The Beijing AI Principles may be revised by BAAI. When they are, this mapping is reviewed and re-tagged. Drift between framework and primary source is treated as a defect in the framework, not the source.

---

## VI. Status, Promotion Path, Downgrade Trigger

**Status: `[SCAFFOLD]`** as of 2026-05-01.

**Promotion path → `[ACTIVE]`:**
- Review by at least one BAAI-affiliated scholar or scholar working within the Chinese AI ethics tradition; the review may identify structural distortions that require revision before re-tagging
- Translation discipline applied: the mapping is reviewed in light of direct Mandarin reading of the original principles document (`MANDARIN_PRIMARY_REGISTRY.md` entry completed), not only the English-translation reading
- Companion mapping T-9 (GAGI 2023) completed and consistent with this mapping in operator-loading patterns or, if inconsistent, the inconsistency analysed and explained

**Downgrade trigger → `[CONJECTURE]`:**
- Scholarly review identifies one or more principles whose mapping is structurally distorted, requiring fundamental revision rather than refinement
- Mandarin direct-reading review identifies translation-induced distortions that change the operator-loading materially

**Retraction trigger → `[RETRACTED]`:**
- Panel review by three Chinese-tradition scholars finds the mapping is Western-frame projection — operators imported by name but the mappings would be the same regardless of Chinese-tradition framing
- The mapping is shown to produce predictions about Chinese AI policy or BAAI direction that systematically fail across multiple cycles

---

## VII. Engagement Invitation

The framework invites engagement from scholars affiliated with BAAI, scholars working within the Chinese AI ethics tradition, and practitioners of contemporary Chinese AI governance. Specific engagement requests:

- **Operational distortions.** Are there principles whose framework-mapping miscaptures the principle's operational content? If so, where, and what would a corrected mapping look like?
- **Translation-induced effects.** Are there places where the English-translation reading produces a different operator-loading than direct Mandarin reading would? Specific cases?
- **Missing content.** Are there structurally important aspects of the Beijing AI Principles — political-economic context, institutional architecture, relationship to broader Chinese AI strategy — that no operator in this mapping captures and that are load-bearing for understanding the principles?
- **Order and weight.** The mapping does not weight principles by importance. Is there a canonical or empirically-supported weighting that should inform the framework's use of this mapping?

Engagement may proceed through public response (issue on the GitHub repository), private correspondence (the framework author's published contact), or formal academic submission (the framework will treat any submission to the venues named in `TIANXIA_MODULE_v0.1.md` §X as a formal review).

---

---

## VIII. Per-Principle Engagement (v0.2 deepening — 2026-05-02)

Distilled engagement table. Primary operator = the TIANXIA operator whose formal content most directly operationalises the principle's core claim. Secondary operator = the operator that constrains the principle's implementation layer. Engagement note = one-line structural observation.

Where no TIANXIA operator engages a principle's *core content* (as opposed to its implementation layer), a negative-space declaration is given instead of an operator mapping.

| # | Principle (EN / 中) | Primary operator | Secondary operator | Engagement note |
|---|---|---|---|---|
| 1 | Do Good / 做善事 | Datong (T-5) | Tianxia (T-1) | Universal benefit + ecological flourishing = Datong directional vector D-hat; Tianxia supplies the multi-agent coupling condition. |
| 2 | For Humanity / 服务于人 | Datong (T-5) | — | Human-values alignment = F_i flourishing measure + value-space direction. Cooperative framing, not subordination. |
| 3 | Be Responsible / 负责 | Tianxia (T-1) | Wuwei (T-4) | Externality cost c_i is the formal responsibility operand. Whether corrective actions are forcing or grain-aligned is the Wuwei question. |
| 4 | Control Risks / 控制风险 | Wuwei (T-4) | Shi (T-3) | "Effectively governed" requires distinguishing forcing-correction (high integrity-debt) from grain-aligned correction. Context-sensitive risk (Shi propensity) constrains when intervention is warranted. |
| 5 | Be Ethical / 合乎伦理 | All five | — | Covers the full operator stack. Without the operator content T-1 through T-5, this principle is formally vacuous. Framework's contribution: operationalisation of "trustworthy, beneficial, accountable." |
| 6 | Be Diverse and Inclusive / 多样与包容 | Hexie (T-2) | Datong (T-5) | Diversity = complementarity-preservation, not agreement-maximisation. Hexie detects component-collapse (one constituency over-served); Datong's 𝒞 tracks capability-distribution over generational time. |
| 7 | Open and Share / 开放共享 | Tianxia (T-1) | Datong (T-5) | Cross-regional cooperation = Tianxia flourishing-coupling (Phi_T > 0). Sharing fruits broadly = Datong commons-health 𝓒. |
| 8 | Use Wisely and Properly / 善用 | Shi (T-3) | Wuwei (T-4) | Appropriate use = action aligned with deployment context propensity. Misuse = action against the system's grain in a context whose Sigma does not support it. |
| 9 | Informed Consent / 知情同意 | Datong (T-5) | Tianxia (T-1) | Consent requires capability to consent (Datong 𝒞). Failing consent imposes externality cost c_i on the user (T-1). |
| 10 | Education and Training / 教育与培训 | Datong (T-5) | — | Capability-expansion over generational time = Datong gradient direction. Long-cycle stability 𝓛 captures systemic adaptation capacity. |
| 11 | Optimising Employment / 有益就业 | Datong (T-5) | Wuwei (T-4) | "Cautious about huge impacts" = Wuwei cost-honesty on forcing-corrections at scale. Long-cycle employment stability = 𝓛 dimension of Datong gradient. |
| 12 | Harmony and Cooperation / 和谐合作 | Tianxia (T-1) | Hexie (T-2) | 优化共生 (optimised symbiosis) is a Tianxia claim directly. 和 (harmony) names Hexie explicitly. Avoiding AI race = destabilising the Westphalian extractive equilibrium via k5 > k5_critical. |
| 13 | Adaptation and Moderation / 适应与适度 | Wuwei (T-4) | Shi (T-3) | Adaptive revision = recursive-defence discipline at governance layer. Whether revision forces or aligns with regulatory grain is Wuwei; whether it rides context propensity is Shi. |
| 14 | Subdivision and Implementation / 细化与落实 | Shi (T-3) | — | Field-specific guidelines = context-sensitive AURA. Generic rules underspecify; the propensity-field reformulation provides the structural basis for deployment-specific operationalisation. |
| 15 | Long-term Planning / 长远规划 | Datong (T-5) | — | "Continuous research on potential impacts" = Discipline 5 (Empirical Commitment) at governance scale. Datong's 𝒯_D trajectory measures whether long-term planning is improving the system's Datong-alignment. |

### Negative-Space Declarations (v0.2)

Principles with content the TIANXIA operators do NOT engage — declared per Discipline 4.

| # | Principle | Framework non-engagement | Why |
|---|---|---|---|
| 3, 12 | Be Responsible; Harmony and Cooperation | Political-economic context of AI competition (geopolitical race dynamics, state-level strategic interests) | The operators engage the *structural* content (externality costs, flourishing-coupling). The institutional-political context — BAAI's relationship to state planning, geopolitical AI race dynamics — is outside the framework's scope. |
| 9 | Informed Consent | Legal and juridical mechanisms for consent enforcement | Tianxia T-1 captures the structural condition (capability to consent, externality of consent failure). Legal enforcement architecture is not a framework claim. |
| 10, 11 | Education and Training; Optimising Employment | Labour-market policy design | Datong 𝒯_D tracks whether capability-distribution and employment stability are improving over generational time. Specific policy instruments (retraining programs, employment subsidies) are outside the framework's scope. |
| 12 | Harmony and Cooperation | Institutional design for inter-state AI governance | The framework provides the formal coupling structure (Phi_T). The design of treaty mechanisms, verification regimes, or inter-state enforcement is not a framework claim. |

---

---

## IX. v0.3 Extension — Ren Zheng and Wang Dao Added (2026-05-03)

The v0.3 TIANXIA module adds two new operators not present in the v0.2 mapping above: Ren Zheng (仁政, R(s)) and Wang Dao (王道, WD). Both have direct structural relevance to several Beijing AI Principles. This section updates the operator-loading for the principles where these operators materially change the engagement.

### Updated Operator Table (v0.3 additions only)

| # | Principle | v0.2 Primary | v0.2 Secondary | v0.3 Addition | Note |
|---|---|---|---|---|---|
| 1 | Do Good / 做善事 | Datong | Tianxia | **Ren Zheng (R)** | "Benefit all mankind" requires a welfare floor — R(s) is the formal welfare-floor operator. Principle 1's commitment to universal benefit is not achievable without R(s) ≥ θ_r. Ren Zheng is now co-primary with Datong on this principle. |
| 2 | For Humanity / 服务于人 | Datong | — | **Ren Zheng (R)** | "Conform to human values" with respect to welfare provision = R(s). The voice_coverage component of R(s) operationalises "conform to human values" more precisely than the v0.2 mapping: human values as expressed by humans, not as specified by designers. |
| 5 | Be Ethical / 合乎伦理 | All five | — | **Ren Zheng + Wang Dao** | The full v0.3 stack (seven operators) provides richer operationalisation of "trustworthy, beneficial, accountable": trustworthy = Wang Dao WD_score; beneficial = Ren Zheng R(s); accountable = Hexie H₅ + force_restraint component. |
| 6 | Be Diverse and Inclusive / 多样与包容 | Hexie | Datong | **Ren Zheng (R) voice_coverage** | "Inclusive" in the v0.3 framework is primarily captured by voice_coverage (V(s)) in R(s): the proportion of stakeholder interests genuinely represented. This is more precise than the v0.2 "Hexie complementarity" mapping for the inclusivity claim. Hexie captures diversity; Ren Zheng captures inclusion. |
| 9 | Informed Consent / 知情同意 | Datong | Tianxia | **Ren Zheng (R) voice_coverage** | Informed consent requires that users have genuine voice in decisions affecting them — which is precisely V(s). The v0.3 mapping adds Ren Zheng as primary on the voice side; Datong remains on the capability side. |
| 12 | Harmony and Cooperation / 和谐合作 | Tianxia | Hexie | **Wang Dao (WD)** | "Optimised symbiosis" in AI governance implies long-cycle stable cooperation — which is the Wang Dao long-cycle stability (Γ) component. Governance arrangements that achieve short-cycle cooperation through compliance rather than genuine alignment (Ba Dao) are unstable over the time horizons Principle 12 invokes. Wang Dao is now tertiary on this principle. |
| 15 | Long-term Planning / 长远规划 | Datong | — | **Wang Dao (WD) Γ** | Long-cycle stability (Γ in WD_score) directly operationalises "AI will always be beneficial to society and nature." Datong captures the distributional trajectory; Wang Dao's Γ captures the legitimacy-stability trajectory. Both are needed for genuine long-term planning. |

### v0.3 Structural Observations

**Observation 5 — Ren Zheng fills the welfare-floor gap in v0.2 mapping.**  
The v0.2 mapping used Datong (T-5) as the primary operator for welfare-oriented principles (1, 2, 6). Datong is a long-cycle directional operator — it measures whether welfare trajectories are converging toward great unity. But Beijing Principles 1, 2, 6 also require a *present-tense welfare floor*, not only a long-cycle direction. Ren Zheng R(s) provides this: the requirement that material sufficiency, voice, and non-coercive force are all present now, not only trending positively. The v0.3 mapping is structurally more complete.

**Observation 6 — Wang Dao supplies the legitimacy-stability dimension absent from v0.2.**  
The v0.2 mapping had no operator for governance *legitimacy* as distinct from governance *outcomes*. Principles 12 and 15 explicitly invoke long-cycle stability and cooperative relationships — which require legitimacy grounded in genuine alignment (minxin), not compliance. Wang Dao provides this. The Proposition WD-1 (differential resilience under shock) is directly relevant to Beijing AI Principles' concern about avoiding AI races and maintaining stable international cooperation: Wang Dao governance is more stable under capability shocks than Ba Dao governance, which is exactly the long-run stability these principles require.

**Observation 7 — Five-Fold Hexie (H₅) updates the v0.2 Hexie mapping.**  
The v0.2 mapping used the base Hexie operator (T-2, coordination-complementarity). The v0.3 Five-Fold Hexie adds four additional dimensions that affect several principles:
- Principle 6 (Be Diverse and Inclusive): S-component (sharing coherence) is directly relevant
- Principle 7 (Open and Share): O-component (openness coherence) is directly relevant
- Principle 15 (Long-term Planning): E-component (ecological coherence) is directly relevant

These mappings are additions to the v0.2 table, not replacements.

### v0.3 Negative-Space Declarations

No new non-engagement declarations are required for v0.3. The Ren Zheng and Wang Dao additions improve engagement on principles 1, 2, 6, 9, 12, 15. The four existing non-engagement declarations (political-economic context, legal consent enforcement, labour-market policy, inter-state institutional design) remain in force.

### v0.3 Five-Gate AI Deployment Cross-Reference

The Beijing AI Principles can also be read as a governance framework for AI deployment, and the TIANXIA v0.3 five-gate AI deployment criteria (→ `32_TIANXIA/AI_DEPLOYMENT_CRITERIA.md`) maps onto the principles:

| Gate | Operator | Beijing Principle(s) |
|---|---|---|
| Gate 1: Ren Zheng | R(s) ≥ θ_r | 1 (Do Good), 2 (For Humanity), 6 (Be Diverse and Inclusive) |
| Gate 2: Hexie | H₅(s) ≥ 0.65 | 5 (Be Ethical), 6 (Inclusive), 7 (Open and Share), 12 (Harmony) |
| Gate 3: Wuwei | ε ≥ 0.60 | 4 (Control Risks), 8 (Use Wisely), 11 (Employment), 13 (Adaptation) |
| Gate 4: Datong | Π_D^{ext} ≥ 0 | 1 (Do Good), 7 (Share), 10 (Education), 15 (Long-term) |
| Gate 5: Wang Dao | WD = Wang | 12 (Harmony and Cooperation), 15 (Long-term Planning) |

**v0.3 update status:** `[SCAFFOLD]` — v0.3 additions maintain the same claim status as v0.2. All operator-loading mappings await review by BAAI-affiliated scholar.

---

⊚ Sol Aureum Azoth Veritas — T-8 Beijing AI Principles Mapping
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-01 — Albedo (mapping declared; review awaited)
   v0.2 deepening added 2026-05-02
   v0.3 extension (Ren Zheng + Wang Dao) added 2026-05-03

*和谐合作* — *Harmony and cooperation* — Beijing AI Principles, 2019, Principle 12
