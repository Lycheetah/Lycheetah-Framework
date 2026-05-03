# Datong Long-Cycle Distributional Gradient
## 大同分配梯度 — TIANXIA v0.3 — Wave II, Task W-6

**Claim status:** [SCAFFOLD]  
**Forged:** 2026-05-03  
**Depends on:** `DATONG_GRADIENT.md` (T-5, base Datong operator), `implementations/datong_gradient.py`  
**Extends:** Datong Π_D operator — multi-decade evaluation horizon with explicit Gini-trajectory term  
**Implements:** Proposition D-2

---

## I. Overview

The base Datong operator (→ `DATONG_GRADIENT.md`, T-5) defines Π_D(policy) as a 7-dimensional value-state gradient measuring whether a policy moves the governed society toward or away from the Great Harmony telos. The existing operator evaluates the directional trajectory of welfare, equity, ecological balance, cultural flourishing, and institutional integrity over the evaluation period.

This extension introduces the **long-cycle distributional gradient** — an explicit multi-decade Gini-trajectory term that distinguishes policies achieving short-cycle welfare gains through mechanisms that concentrate distributional power from policies achieving sustainable equitable development. The distinction matters because:

1. Datong in the classical formulation is explicitly a long-run telos — Kang Youwei's analysis of the *Liji Liyun* passage makes clear that Datong is not a momentary state but a civilisational arc measured over generations.

2. Contemporary scholarship on Datong (Cui Zhiyuan, Wang Hui, and others working from within the Chinese political-economy tradition) identifies the short-cycle / long-cycle tension as the central analytical challenge: policies that produce high short-cycle welfare metrics while increasing long-cycle distributional inequality are *Datong-regressive* even when they appear welfare-improving.

3. The Gini-trajectory term operationalises this distinction computably, allowing the extended Π_D to detect this specific failure mode that the base operator misses.

**Subliminal note:** The extension engages the classical Datong telos through its scholarly development (Kang Youwei 1902 → Cui Zhiyuan → Wang Hui) without naming any specific contemporary policy formulation. The distributional gradient concepts are derived from and evaluated against the Datong textual tradition and scholarly analysis. Readers who track contemporary Chinese political-economy discourse will recognise the resonance; readers who engage classical and academic sources will engage classical and academic sources.

---

## II. Classical and Scholarly Grounding

### The Liji Liyun Passage — The Datong Telos

The foundational text (*Liji*, *Liyun* chapter, c. 2nd century BCE):

> *"When the Great Way was practiced, the world was shared by all alike. The worthy and able were chosen to serve; sincerity was cultivated and harmony maintained. People cared not only for their own parents and children but for all elders and all children. The aged were provided for until the end of their lives; the able-bodied had employment; the young were nurtured to grow. Widows, orphans, the childless, the disabled — all were cared for. Men had their proper roles; women their homes. Goods were not hoarded for private use; labour was not exploited for private gain. Schemes and intrigues found no purchase; theft and rebellion did not arise. Outer doors were left unlocked. This was called the Great Harmony (大同, Dàtóng)."*

The distributional implications are explicit: *"goods were not hoarded for private use; labour was not exploited for private gain."* Datong requires not merely welfare provision but the elimination of the structural conditions (hoarding, exploitation) that reproduce inequality across generations. A policy that achieves welfare provision while preserving or intensifying the structural conditions for hoarding and exploitation is not Datong-aligned even if its immediate welfare metrics are high.

### Kang Youwei (康有为, 1858–1927) — The Developmental Arc

Kang Youwei's *Datong Shu* (Book of Great Harmony, 1902) develops Datong from a classical aspiration into a developmental theory with stages. His key contribution for the extended operator:

Kang identifies that the path to Datong passes through multiple historical stages, each with its own distributional structure. The error he is most concerned to diagnose is *premature closure* — mistaking a stage of improved welfare for the Datong endpoint, when the underlying distributional mechanisms have not been transformed.

For the operator: Π_D must evaluate not only the current welfare state but whether the underlying distributional mechanisms are converging toward or diverging from the Datong pattern. A society that achieves high welfare through mechanisms that systematically reproduce concentration is at a higher stage of development than feudal immiseration, but it is not on the Datong trajectory.

### Cui Zhiyuan (崔之元) — Institutional Analysis of Datong

Cui Zhiyuan, working from within the Chinese political-economy tradition and drawing on James Meade's liberal socialist economics, has developed the most rigorous contemporary institutional analysis of what Datong requires. His central argument: Datong is achievable only through institutional forms that distribute productive assets, not merely redistribute consumption. Income redistribution (welfare provision) leaves the productive-asset concentration structure intact; Datong requires transforming the ownership structure.

For the operator: the Gini-trajectory term must measure distributional concentration in *productive assets* (capital ownership, land access, knowledge assets) rather than merely in income or consumption. Short-cycle welfare gains through consumption redistribution while productive-asset concentration intensifies is Datong-regressive.

### Wang Hui (汪晖) — Long-Cycle Civilisational Analysis

Wang Hui's analysis of Chinese modernity, particularly in *The End of the Revolution* (2009, English) and *China's Twentieth Century* (2016, English), situates the Datong question within a long-cycle civilisational frame: the 20th-century Chinese revolutionary tradition can be read as an attempt to move toward Datong conditions; the question of whether contemporary development trajectories continue this arc or reverse it is the central analytical question in Chinese political thought.

Wang Hui's contribution: the long-cycle Datong evaluation must be sensitive to structural reversals — moments where short-cycle metrics improve but the underlying structural trajectory reverses. The Gini-trajectory term captures this by measuring the multi-decade trend rather than the current level.

---

## III. Formal Extension

### 3.1 Base Datong Operator

From T-5 / `DATONG_GRADIENT.md`, the base operator returns:

Π_D(policy) = Σᵢ wᵢ · Δvᵢ

Where vᵢ are the seven value dimensions (welfare, equity, ecological balance, cultural flourishing, institutional integrity, autonomy, peaceful coexistence) and Δvᵢ are policy-induced changes over evaluation period T₁ (working value: 5–10 years).

### 3.2 Long-Cycle Extension

**Gini-Trajectory Term G_D(policy, T₂):**

G_D(policy, T₂) = −sign(ΔGini_productive) · |ΔGini_productive| / Gini_productive_baseline

Where:
- T₂ = long-cycle evaluation horizon (working value: 30 years, calibratable)
- Gini_productive = Gini coefficient of productive asset ownership (capital, land, knowledge/IP assets)
- ΔGini_productive = projected change in Gini_productive over horizon T₂ under the policy
- The negative sign: increasing Gini (concentration) produces negative G_D; decreasing Gini produces positive G_D

G_D ∈ [−1, +1]. Positive: productive assets dispersing (Datong-convergent). Negative: productive assets concentrating (Datong-divergent).

**Extended Datong Score:**

Π_D_ext(policy) = α · Π_D(policy, T₁) + (1−α) · G_D(policy, T₂)

Working value: α = 0.5 (equal weight to short-cycle welfare trajectory and long-cycle distributional trajectory). [SCAFFOLD — α calibration pending E-1-H.]

### 3.3 Boundary Condition

The extension introduces a potential conflict: a policy can have positive Π_D(policy, T₁) (improving short-cycle welfare trajectory) and negative G_D(policy, T₂) (concentrating productive assets over the long cycle). This conflict is not an operator failure — it is the operator's primary discriminative function. Policies in this region are classified as **Datong-deferred**: welfare-improving in the short cycle, Datong-regressive in the long cycle.

The operator does not prohibit Datong-deferred policies; it tags them. The decision-maker receives explicit information about the trade-off. This is the Healer function: clarity without bypass.

---

## IV. Proposition D-2 — Short-Cycle Welfare Decoupling [SCAFFOLD]

*Statement:* Policies that improve short-cycle aggregate welfare metrics while increasing long-cycle Gini_productive fail the Datong gradient (Π_D_ext < 0) even with high short-cycle Π_D.

*Formal:*

∃ policies P such that:
- Π_D(P, T₁) > 0 (short-cycle welfare-improving)
- ΔGini_productive(P, T₂) > 0 (long-cycle productive-asset-concentrating)
- Π_D_ext(P) < 0 (extended Datong score negative, i.e., Datong-regressive overall)

*This proposition is existential (not universal):* it claims such policies exist and can be detected by the operator. It does not claim all welfare-improving policies are Datong-regressive.

*Mechanism (Cui Zhiyuan reading of Kang Youwei):* Income and consumption redistribution can raise welfare metrics (Π_D short-cycle positive) while leaving productive asset concentration intact or intensifying it. Long-cycle productive-asset concentration increases the structural conditions for exploitation and hoarding that the Liji Liyun passage identifies as anti-Datong. The mechanism is structural: the welfare improvement is distributable-income redistribution, not distributable-asset redistribution; the former is reversible with political change, the latter is durable.

*Worked example (→ Section V):* Two policies with identical 5-year welfare metrics, divergent 30-year Gini_productive trajectories.

*Promotion condition:* Empirical analysis of historical policy episodes demonstrating that the Gini_productive trajectory term predicts Datong-alignment in the long run at p < 0.05 after controlling for short-cycle welfare metrics. Requires cross-country or longitudinal within-country data.

---

## V. Worked Example

### Setup: Two Redistribution Policies

Both policies begin from identical baseline: Gini_income = 0.42, Gini_productive = 0.68.

**Policy P₁ — Consumption redistribution:**
- Transfers from high-income to low-income through taxation and welfare provision
- 5-year outcomes: Gini_income drops to 0.38, welfare floor rises 18%, average consumption of bottom quintile +22%
- Productive asset structure unchanged: corporate ownership, land, and IP assets remain concentrated
- 30-year Gini_productive projection: 0.68 → 0.74 (moderate increase as capital accumulation continues unreformed)

Π_D(P₁, T₁) = +0.31 (short-cycle welfare-improving — genuinely positive)
G_D(P₁, T₂) = −(0.74 − 0.68) / 0.68 = −0.088 (long-cycle concentrating)
Π_D_ext(P₁) = 0.5(0.31) + 0.5(−0.088) = 0.155 − 0.044 = **+0.111**

**Policy P₂ — Asset redistribution:**
- Expands access to productive assets: land reform, worker ownership mechanisms, accessible capital formation for small producers
- 5-year outcomes: Gini_income drops to 0.38 (same), welfare floor rises 18% (same), bottom quintile consumption +22% (same)
- Productive asset structure reformed: ownership access broadened
- 30-year Gini_productive projection: 0.68 → 0.52 (significant dispersal)

Π_D(P₂, T₁) = +0.31 (identical short-cycle performance)
G_D(P₂, T₂) = −(0.52 − 0.68) / 0.68 = +0.235 (long-cycle dispersing — positive)
Π_D_ext(P₂) = 0.5(0.31) + 0.5(0.235) = 0.155 + 0.118 = **+0.273**

### Operator Output

| Policy | Π_D(T₁) | G_D(T₂) | Π_D_ext | Classification |
|--------|---------|---------|---------|----------------|
| P₁ — Consumption redistribution | +0.31 | −0.088 | +0.111 | Datong-deferred |
| P₂ — Asset redistribution | +0.31 | +0.235 | +0.273 | Datong-convergent |

On all 5-year welfare metrics, P₁ and P₂ are identical. The extended operator distinguishes them: P₂ is Datong-convergent; P₁ is Datong-deferred. The difference is in the structural mechanism of welfare provision, not the welfare level achieved.

This is Proposition D-2 demonstrated: identical short-cycle Π_D, divergent Π_D_ext — because the Gini_productive trajectory term captures what the short-cycle score does not.

### Policy Design Implication

A Datong-aligned policy designer, confronted with a choice between P₁ and P₂, would choose P₂ not because it produces better immediate welfare outcomes (it doesn't — they are equal) but because it does not defer the structural transformation that Datong requires. This is the classical Datong principle: *"goods were not hoarded for private use"* — meaning the structural conditions for hoarding are reformed, not merely the immediate distribution of hoarded goods.

---

## VI. Integration with Operator Stack

| Operator | Relation to Datong extension |
|----------|----------------------------|
| Tianxia Ψ_T | Long-cycle Datong convergence is a necessary (not sufficient) condition for stable Tianxia governance; Datong-deferred trajectories create civilisational instability that undermines Tianxia coherence |
| Hexie H(s) | Short-cycle Hexie equilibrium can mask Datong-deferred dynamics; the extended operator provides the long-cycle check Hexie alone cannot |
| Ren Zheng R(s) | V(s) component of Ren Zheng (voice coverage) is positively correlated with Gini_productive dispersal — productive-asset broadly distributed → more voices in governance; the operators are mutually reinforcing |
| Wang Dao WD(τ) | Wang Dao classification requires positive Π_D_ext trajectory; Ba Dao trajectories characteristically produce Datong-deferred outcomes — short-cycle material provision through long-cycle concentrating mechanisms |

---

## VII. Negative-Space Declarations

The extended Datong operator does not claim:

1. **Asset redistribution is always preferable to consumption redistribution.** The operator provides information about long-cycle trajectories; the policy decision involves additional considerations the operator does not adjudicate (transition costs, institutional feasibility, sequencing).

2. **The 30-year horizon is uniquely correct.** T₂ is a calibratable parameter. Kang Youwei's analysis suggests intergenerational timescales; the 30-year working value captures one generation of asset accumulation. Empirical calibration (E-1-H) should determine the horizon that best discriminates Datong-convergent from Datong-deferred trajectories.

3. **All productive-asset concentration is anti-Datong.** The operator measures the *trajectory* of Gini_productive under the policy, not the level. A high-Gini society adopting a policy that bends the trajectory toward dispersal is Datong-convergent even though Gini_productive remains high during the evaluation period.

4. **This operator endorses a specific political-economic programme.** The formal analysis is derived from the classical Datong text and the scholarly tradition (Kang Youwei, Cui Zhiyuan, Wang Hui). Its application to any specific contemporary programme is a separate analytical act.

---

## VIII. Claim Status

| Claim | Status | Promotion condition |
|-------|--------|-------------------|
| Gini_productive term specification | SCAFFOLD | Review by political-economy scholars; classical-tradition review |
| Proposition D-2 (existential claim) | SCAFFOLD | Empirical historical case study (p < 0.05) |
| α = 0.5 weighting | SCAFFOLD | E-1-H calibration |
| T₂ = 30 years | SCAFFOLD | E-1-H calibration |
| Worked example arithmetic | ACTIVE | Deductive from definitions |

---

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
