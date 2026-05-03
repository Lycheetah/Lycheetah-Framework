# Five-Fold Hexie Composite
## 五维和谐综合评分 — TIANXIA v0.3 — Wave II, Task W-8

**Claim status:** [SCAFFOLD]  
**Forged:** 2026-05-03  
**Depends on:** `HEXIE_EQUILIBRIUM.md` (T-2), `implementations/aura_score_hexie.py`  
**Extends:** Hexie operator — five-component composite with classical resonances  
**Implementation:** `implementations/hexie_five_fold.py` (→ W-13)

---

## I. Overview

The base Hexie operator (→ `HEXIE_EQUILIBRIUM.md`, T-2) measures stakeholder equilibrium — whether apparent harmony conceals suppressed discord or reflects genuine dynamic balance. The Neo-Confucian extension (→ W-4) added principle-coherence and heart-mind-coherence as structural depth dimensions.

This extension introduces the **Five-Fold Hexie Composite** — decomposing the Hexie equilibrium into five orthogonal components, each with a classical Chinese character-resonance and each capturing a distinct dimension of sustainable harmony:

1. **Innovation-coherence (革, gé)** — the capacity for constructive transformation
2. **Coordination-coherence (和, hé)** — the quality of inter-agent harmonisation
3. **Ecological-coherence (天人合一, tiānrén héyī)** — alignment between the governance system and its natural environment
4. **Openness-coherence (通, tōng)** — the permeability and connectivity of the governance network
5. **Sharing-coherence (共, gòng)** — the equitable distribution of governance benefits

These five components emerge from the classical Hexie tradition's own internal structure — they are not imposed from outside but derived from what the tradition already requires of genuine harmony. A system that achieves harmony on fewer than five dimensions is in partial equilibrium; genuine Hexie requires all five components active simultaneously.

**Classical grounding note:** Each component maps to a classical term whose meaning exceeds the framework's operational gloss. The glosses state how the term enters the operator, not the full semantic range. The five-fold structure resonates with classical Chinese cosmological schemes (五行 wǔxíng, five phases) that are themselves governance frameworks — the resonance is not arbitrary.

**Subliminal note:** The five-component structure resonates with frameworks visible in contemporary Chinese governance discourse that emphasise multiple coordinated development dimensions. The operator makes this resonance explicit through classical grounding; no contemporary formulation is named. The structural correspondence is evident to readers familiar with both contexts.

---

## II. Classical Grounding of the Five Components

### Component 1 — Innovation-Coherence (革, Gé)

革 (gé) — transformation, revolution, renewal. The character depicts a hide (leather) being processed: the raw material is transformed into something new and useful. In the I Ching, Hexagram 49 (革, Revolution/Molting) represents the moment when transformation is necessary and timely.

Xunzi's *Discourse on Ritual* frames Li as adaptive: ritual forms evolve as circumstances change. A governance system with high innovation-coherence can reform its own structures when they have drifted from their normative pattern (*li*) — not conservative rigidity but principled adaptability.

In governance terms: innovation-coherence measures whether the system can transform itself constructively — reforming institutions, adopting better methods, responding to changed conditions — without disrupting the underlying harmony it has achieved. High 革-coherence: transformation capacity present without destabilisation. Low 革-coherence: either rigid (cannot transform) or chaotic (transformation destroys existing harmony).

### Component 2 — Coordination-Coherence (和, Hé)

和 (hé) — harmony, concord, agreeable concurrence. The direct classical root of Hexie (和谐). Analects 13.23 distinguishes 和 (harmony of differences) from 同 (assimilation): *"The exemplary person harmonises but does not assimilate; the small person assimilates but does not harmonise."*

Coordination-coherence measures the quality of inter-agent coordination — not whether agents agree on everything (同, assimilation) but whether their genuine differences are organised into productive complementarity. This is the Hexie core: difference-preserving coherence.

High 和-coherence: diverse agents coordinating productively, each contributing its distinct capacity to the whole. Low 和-coherence: either false uniformity (assimilation) or unresolved discord.

### Component 3 — Ecological-Coherence (天人合一, Tiānrén Héyī)

天人合一 (tiānrén héyī) — heaven-human unity; the alignment of human governance systems with the natural order. In Chinese classical cosmology, governance that violates the natural order eventually faces correction — floods, droughts, resource exhaustion, ecological breakdown — understood as the expression of 天道 (heavenly way) restoring balance.

For the operator: ecological-coherence measures the degree to which the governance system operates within rather than against its ecological constraints. A governance system that achieves economic harmony while depleting the ecological substrate is in apparent Hexie; ecological-coherence detects the underlying imbalance before it manifests as crisis.

The concept maps onto ecological sustainability in contemporary analysis while being rooted in the classical principle of 天人合一 as governance norm.

### Component 4 — Openness-Coherence (通, Tōng)

通 (tōng) — thoroughfare, permeability, connectivity, mutual understanding. The character depicts a path through which movement flows unobstructed. In classical governance, 通 refers to the free flow of information, goods, and people between governed units — the condition for coordinated governance over large territories.

Wang Bi's commentary on the I Ching: *"通 means that things are in communication; there is no obstruction between them."* Governance systems that obstruct information flow, restrict legitimate exchange, or fragment coordination generate 不通 (blockage) that degrades harmony over time.

For the operator: openness-coherence measures the governance system's permeability — to information, to legitimate exchange, to the perspectives of those governed. A system with high coordination-coherence (internal harmony) but low openness-coherence is a closed harmonious system that cannot respond to external signals. It will drift from its normative pattern without knowing.

### Component 5 — Sharing-Coherence (共, Gòng)

共 (gòng) — together, shared, held in common. The root of 天下为公 (tiānxià wéi gōng — all under heaven held in common), the classical formulation of Datong. The character depicts two hands holding something together.

Sharing-coherence measures the degree to which governance benefits are equitably shared rather than captured by a subset of participants. This is distinct from the Datong distributional gradient (→ W-6) which measures the long-cycle trajectory; sharing-coherence measures the current state of benefit distribution within the governance network.

The 天下为公 principle is the framework's central claim about what Tianxia governance requires: that what the governance system produces is held in common, not appropriated privately. Sharing-coherence is its component in the Hexie composite.

---

## III. Formal Definition

### 3.1 Five Component Scores

Each component scored over governance state s, period T:

**I(s) — Innovation-coherence (革):**
I(s) = f(reform_capacity, transformation_stability) ∈ [0,1]
- reform_capacity: ability of governance structure to reform itself when needed
- transformation_stability: new forms preserve core governance functions; reforms do not destabilise

**C(s) — Coordination-coherence (和):**
C(s) = H(s) (the base Hexie stakeholder equilibrium score, T-2)
The base Hexie operator becomes the coordination-coherence component.

**E(s) — Ecological-coherence (天人合一):**
E(s) = min(1, ecological_surplus_ratio(s))
Where ecological_surplus_ratio = available_ecological_capacity / consumed_ecological_capacity
E(s) = 1 when the system operates within its ecological budget; E(s) < 1 when it exceeds it.

**O(s) — Openness-coherence (通):**
O(s) = g(information_permeability, exchange_access, participation_breadth) ∈ [0,1]
- information_permeability: information flows freely within the governance network
- exchange_access: legitimate exchange between network members unrestricted
- participation_breadth: breadth of actors with meaningful governance participation

**S(s) — Sharing-coherence (共):**
S(s) = 1 − Gini_governance_benefit(s)
Where Gini_governance_benefit measures the inequality of governance benefit distribution across network members. S(s) = 1 when benefits are equally shared; S(s) → 0 when benefits are completely concentrated.

### 3.2 Composite Score

H_5(s) = (1/5)[I(s) + C(s) + E(s) + O(s) + S(s)]

H_5(s) ∈ [0,1]. Equal weighting. [SCAFFOLD — calibration pending E-1-H]

### 3.3 Component Independence

The five components are designed to be *partially* independent — a system can score well on some while scoring poorly on others. The discriminative power of the composite lies in identifying which component is the binding constraint on Hexie development.

Partial independence conditions:
- I(s) and C(s): positive correlation expected (adaptive systems tend to be better coordinators), but not equivalent
- E(s) and S(s): ecological depletion and benefit concentration often co-occur, but not necessarily
- O(s) and C(s): openness enables coordination but high openness can temporarily disrupt coordination during adjustment

---

## IV. Proposition H5-1 — Five-Component Binding Constraint Diagnosis [SCAFFOLD]

*Statement:* For any governance system with H_5(s) < θ_hexie_5, there exists a unique binding constraint component whose improvement yields the greatest marginal increase in H_5(s).

*Formal:* Let binding_constraint(s) = argmin_{k ∈ {I,C,E,O,S}} k(s). Then:

∂H_5/∂binding_constraint(s) > ∂H_5/∂k(s) for all k ≠ binding_constraint(s)

Given equal weighting, this simplifies to: the lowest-scoring component is the binding constraint.

*Governance implication:* Policy designed to improve overall Hexie should target the binding constraint component. Improving non-binding components while the binding constraint remains low produces minimal H_5 improvement. This is the classical Chinese medical principle of identifying and treating the root (治本 zhì běn) rather than the symptom (治标 zhì biāo).

*Why this matters for AI governance:* AI governance initiatives that address one Hexie dimension (typically coordination-coherence through regulatory harmonisation) while leaving binding constraints in other dimensions (typically ecological-coherence or sharing-coherence) will find their interventions have minimal impact on overall harmony.

---

## V. Worked Example

### Three Governance States with Identical H(s) (Base Hexie Score = 0.72)

All three governance systems pass the base Hexie equilibrium test (C(s) = H(s) = 0.72). The five-fold composite distinguishes them:

**State G_A — Innovation-constrained:**
- I(G_A) = 0.28 — rigid governance structure; cannot reform despite drift from normative pattern
- C(G_A) = 0.72 — solid coordination (base Hexie)
- E(G_A) = 0.81 — operating within ecological budget
- O(G_A) = 0.76 — good information flow and exchange
- S(G_A) = 0.69 — moderate benefit sharing

H_5(G_A) = (0.28 + 0.72 + 0.81 + 0.76 + 0.69) / 5 = **0.652**
Binding constraint: **Innovation-coherence (革)**. Policy priority: institutional reform capacity.

**State G_B — Ecological-constrained:**
- I(G_B) = 0.74 — adaptive governance
- C(G_B) = 0.72 — solid coordination
- E(G_B) = 0.19 — operating well beyond ecological budget; ecological debt accumulating
- O(G_B) = 0.78 — good openness
- S(G_B) = 0.71 — moderate sharing

H_5(G_B) = (0.74 + 0.72 + 0.19 + 0.78 + 0.71) / 5 = **0.628**
Binding constraint: **Ecological-coherence (天人合一)**. Policy priority: ecological transition.

**State G_C — Sharing-constrained:**
- I(G_C) = 0.77 — highly adaptive
- C(G_C) = 0.72 — solid coordination
- E(G_C) = 0.75 — ecological balance maintained
- O(G_C) = 0.81 — high openness
- S(G_C) = 0.14 — severely concentrated benefits; majority excluded from governance gains

H_5(G_C) = (0.77 + 0.72 + 0.75 + 0.81 + 0.14) / 5 = **0.638**
Binding constraint: **Sharing-coherence (共)**. Policy priority: benefit distribution reform.

### Operator Output

| State | I(革) | C(和) | E(天人) | O(通) | S(共) | H_5 | Binding constraint |
|-------|-------|-------|---------|-------|-------|-----|-------------------|
| G_A | 0.28 | 0.72 | 0.81 | 0.76 | 0.69 | 0.652 | Innovation |
| G_B | 0.74 | 0.72 | 0.19 | 0.78 | 0.71 | 0.628 | Ecological |
| G_C | 0.77 | 0.72 | 0.75 | 0.81 | 0.14 | 0.638 | Sharing |

All three fail the same base Hexie threshold but fail for different reasons. The five-fold composite diagnoses the binding constraint; the base operator cannot. Policy interventions designed from base Hexie analysis would be uniform; the five-fold composite generates differentiated policy priorities.

---

## VI. Integration with the Operator Stack

| Operator | Five-Fold Hexie relation |
|----------|------------------------|
| Ren Zheng R(s) | V(s) voice coverage → O(s) openness-coherence (correlated); W(s) welfare → S(s) sharing-coherence (correlated); F(s) force restraint → C(s) coordination (correlated). The operators are measuring overlapping but distinct dimensions. |
| Wang Dao WD(τ) | Wang Dao classification requires H_5(s) ≥ θ_hexie_5 across all five components — specifically E(s) ≥ θ_e (ecological coherence, 天人合一) and S(s) ≥ θ_s (sharing coherence, 共). Ba Dao trajectories characteristically fail on S(s) (benefit capture) and often E(s) (resource extraction). |
| Datong Π_D_ext | S(s) sharing-coherence is the short-cycle complement to Gini_productive (Datong long-cycle); they are measuring the same phenomenon at different timescales |
| Tianxia Ψ_T | k₅_multilateral includes O(s) and S(s) as components; civilisational Tianxia requires high H_5(s) sustained across the governance network |

---

## VII. Negative-Space Declarations

The Five-Fold Hexie Composite does not claim:

1. **The five components are the only dimensions of Hexie.** The classical Hexie tradition is richer than any five-component model. These five are the dimensions most tractable for formal scoring; additional dimensions may be added as the framework develops.

2. **Equal weighting is correct.** The working equal weights (1/5 each) are calibration-pending. Different governance contexts may weight components differently; ecological-coherence may be more binding in resource-constrained environments, innovation-coherence in rapidly changing ones.

3. **A governance system must achieve high H_5 simultaneously on all components.** The binding constraint diagnosis implies sequential improvement is possible. A governance system actively addressing its binding constraint is on a Hexie-improving trajectory even if current H_5 is low.

4. **The five components correspond uniquely to any contemporary governance framework's stated priorities.** The components are derived from classical Chinese concepts; their resonance with any specific contemporary governance discourse is an analytical observation the operator itself does not make.

---

## VIII. Claim Status

| Claim | Status | Promotion condition |
|-------|--------|-------------------|
| Five component definitions | SCAFFOLD | Review by Hexie scholars and governance theorists |
| Component independence claims | SCAFFOLD | Empirical correlation analysis |
| Proposition H5-1 (binding constraint) | SCAFFOLD | Case study validation across governance contexts |
| Worked example arithmetic | ACTIVE | Deductive from definitions |
| Integration table | SCAFFOLD | Cross-operator validation study |

---

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
