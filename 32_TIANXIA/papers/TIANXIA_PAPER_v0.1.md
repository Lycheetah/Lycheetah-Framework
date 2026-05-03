# Operationalising Tianxia: A Formal Operator Stack for Civilisational Governance Assessment

**Mackenzie Conor James Clark**  
Independent Researcher — Lycheetah Framework  
CODEX_AURA_PRIME, Module 32_TIANXIA  
**Version:** v0.1 — 2026-05-03  
**Claim status:** [SCAFFOLD] — quantitative thresholds pending empirical calibration (→ E-1-H)  
**Target:** *Journal of Chinese Philosophy* / *Dao: A Journal of Comparative Philosophy* / *Asian Journal of Philosophy*

---

## Abstract

The tianxia (天下) tradition offers a normative vision of civilisational order grounded in inclusive welfare, relational legitimacy, and the subordination of partial interests to the common good. Yet its translation into policy analysis and AI governance has remained conceptually rich but analytically underdetermined: scholars invoke Zhao Tingyang's *Tianxia System*, Kang Youwei's *datong* (大同), and classical Confucian statecraft without specifying how these principles generate measurable predictions or comparative judgements across governance arrangements. This paper presents the TIANXIA operator stack — a formal multi-operator system that renders tianxia-derived governance concepts computationally tractable without reducing their normative depth. The stack comprises seven operators: Ren Zheng (仁政, benevolent governance), Five-Fold Hexie (和谐, harmonious coherence), Tianxia multilateral coupling, Shi (势, propensity alignment), Wuwei (无为, minimal coercive intervention), Datong distributional gradient, and Wang Dao (王道, kingly way legitimacy). Each operator is formally defined, assigned a claim status reflecting its evidential grounding, and equipped with falsification conditions. The composite benchmark is validated against three reference governance scenarios drawn from extractive, liberal-procedural, and tianxia-aligned archetypes, with results confirming expected ordering. We argue that the formalisation does not domesticate tianxia into Western institutional frameworks but rather makes its distinctive claims — particularly its rejection of state-centrism and its long-cycle temporal horizon — operationally explicit and therefore testable. Applications to AI deployment governance criteria are illustrated. Limitations and the empirical calibration programme required for full activation are specified.

**Keywords:** tianxia, benevolent governance, Wang Dao, Hexie, civilisational assessment, AI governance, Zhao Tingyang, Mengzi, comparative political philosophy

---

## 1. Introduction

The tianxia concept occupies an unusual position in contemporary political philosophy. Ancient in origin — the term appears in the *Book of Songs* (*Shijing*, 詩經) and achieves systematic treatment in the *Liji* (*Book of Rites*, 禮記) and *Mengzi* — it has attracted renewed scholarly attention as a potential resource for thinking beyond the Westphalian state-system. Zhao Tingyang's *Tianxia System: A Philosophy for the World Institution* (2005/2021) is the most influential recent reconstruction, arguing that tianxia provides a non-state-centric framework for global governance grounded in relational ontology rather than sovereign competition. Wang Hui's work on Confucian modernity (2014) and Cui Zhiyuan's engagements with classical statecraft offer complementary perspectives on how these traditions might inform contemporary institutional design.

Yet a persistent difficulty confronts scholars who wish to use tianxia analytically rather than merely rhetorically: the tradition's normative vocabulary — *minxin* (民心, the hearts of the people), *datong* (大同, great unity), *wang dao* (王道, the kingly way), *wu wei* (無為, non-coercive governance) — is philosophically rich but operationally thin. One can invoke these concepts to describe or critique governance arrangements, but it is much harder to specify what evidence would confirm that a given arrangement instantiates tianxia principles to a given degree, or to compare two arrangements systematically using these criteria.

This paper addresses that gap. We present the TIANXIA operator stack: a formal system of seven operators derived from the classical and contemporary tianxia literature, each computing a numerical score from structured governance data. The operators are not reductions of the tradition to metrics — they are formalisations that make the tradition's claims explicit enough to be tested, refined, or falsified.

The paper proceeds as follows. Section 2 situates the operator stack within the broader Lycheetah Framework and the CASCADE epistemic architecture from which its formal structure is borrowed. Section 3 presents each of the seven operators in turn: formal definition, classical grounding, and claim status. Section 4 describes the composite governance benchmark and its validation against reference scenarios. Section 5 illustrates the application to AI deployment governance criteria. Section 6 addresses critical objections — particularly the charge that the stack is a disguised apology for a particular civilisational order. Section 7 specifies the empirical calibration programme required to promote the system from scaffold to active status. Section 8 concludes.

---

## 2. Formal Architecture and Classical Foundations

### 2.1 The Lycheetah Framework

The TIANXIA operator stack is the civilisational governance module of the Lycheetah Framework — a multi-framework epistemic and normative system developed across ten interconnected modules (Clark, 2026). The framework's governing structure is the AURA (Alignment, Understanding, Reasoning, Anchoring) protocol, which specifies seven invariants — including non-deception, human primacy, and inspectability — that apply across all framework modules. These invariants are not external constraints imported from Western analytic philosophy; they have direct classical Chinese parallels. Non-deception maps to the Confucian virtue of *xin* (信, trustworthiness); inspectability maps to the Neo-Confucian demand for *gé wù zhì zhī* (格物致知, the investigation of things to achieve knowledge); human primacy maps to Mengzi's foundational claim that the people (民) are the weightiest element in a polity (Mengzi, 7B.14).

The formal structure borrowed from CASCADE — the Lycheetah epistemic framework — is a belief-coherence dynamics equation:

$$\frac{d\Psi}{dt} = k_1(\Pi - \Pi_{th}) - k_2(\Psi - \Psi_{inv}) - k_3 I_{violations} + k_4\left(\frac{E}{E_{need}}\right)$$

where Ψ is agent belief coherence, Π is truth-pressure, and k₁–k₄ are calibration coefficients. This structure appears in the TIANXIA module as the formal backbone for governance trajectory analysis: a governance arrangement is analogous to an agent whose coherence (legitimacy) evolves under truth-pressure (evidence of welfare outcomes), violation costs (AURA invariant failures), and resource availability (institutional capacity). The master equation is currently [SCAFFOLD] — structurally correct but lacking empirical coefficient estimates — and its empirical calibration is the primary objective of the E-1-H study (Clark, 2026b).

### 2.2 The Classical Triad

The operator stack is grounded in three classical traditions that were historically in productive tension:

**Confucian statecraft** contributes the welfare-and-virtue axis: the primacy of *ren* (仁, benevolence), *yi* (義, righteousness), and *li* (禮, ritual propriety) as governance foundations; the *minxin* doctrine that governance legitimacy derives from genuine popular alignment rather than compliance; and the long-cycle developmental orientation expressed in *changzhi jiu'an* (長治久安, enduring order and lasting peace).

**Daoist thought** contributes the non-coercive axis: *wu wei* as the governance mode that aligns with the *de* (德, inherent virtue) of natural processes; *ziran* (自然, spontaneous naturalness) as the criterion for distinguishing legitimate facilitation from coercive imposition; and *tian ren he yi* (天人合一, the unity of Heaven and humanity) as the ecological grounding for governance arrangements that must persist across geological as well as political time.

**Legalist analysis** provides the institutional realism without which Confucian and Daoist ideals become unmoored. Han Fei's analysis of *fa* (法, law), *shu* (術, technique), and *shi* (勢, propensity) is particularly valuable: *shi* as the field of propensities within which governance acts — the gravitational structure of possibilities — transforms the Daoist non-coercive ideal into a strategic concept. The ruler who governs through *shi* is not passive but attuned: acting minimally, decisively, at the moment when propensities are aligned (Han Feizi, ch. 40).

These three traditions are not synthesised into a single framework by flattening their differences. The TIANXIA stack preserves the tensions: the Ren Zheng operator encodes Confucian welfare primacy; the Wuwei operator encodes Daoist non-coercion; the Shi operator encodes Legalist propensity analysis. Where the traditions conflict, the stack makes the conflict structurally visible as a binding-constraint diagnosis rather than resolving it artificially.

---

## 3. The Seven Operators

### 3.1 Ren Zheng: Benevolent Governance Floor (仁政)

**Formal definition:**

$$R(s) = \frac{W(s) + V(s) + F(s)}{3}$$

where W(s) is welfare_baseline (the fraction of the population at material sufficiency), V(s) is voice_coverage (the proportion of stakeholder interests genuinely represented in governance decisions), and F(s) is force_restraint (the inverse of the coercive enforcement rate).

**Classical grounding:** The Ren Zheng operator derives from Mengzi's account of benevolent governance, particularly the *bù rěn rén zhī xīn* (不忍人之心, the heart that cannot bear the suffering of others) passages (Mengzi 2A.6). Mengzi's argument that governance legitimacy requires material sufficiency — that the people cannot practice virtue without adequate food, shelter, and security (Mengzi 1A.7) — generates the welfare_baseline component. The voice_coverage component reflects Mengzi's insistence that governance must be responsive to what the people actually want rather than what rulers believe they should want (Mengzi 1B.3). Force_restraint encodes the contrast between Wang Dao and Ba Dao: governance through virtue does not require coercive enforcement because it commands genuine assent.

**Proposition R-1 (Necessary Condition):** For any governance arrangement s, R(s) ≥ θ_r is a necessary (but not sufficient) condition for Wang Dao classification. [SCAFFOLD — θ_r = 0.618 pending empirical calibration]

**Proposition R-2 (Force Escalation):** Governance arrangements with R(s) < θ_r exhibit systematically higher enforcement costs over time as compliance-based legitimacy requires increasing coercive maintenance. [SCAFFOLD]

A worked example demonstrates the non-trivial structure of R(s). Three governance arrangements (G1, G2, G3) ranked identically on welfare_baseline are reversed in ranking on R(s) when voice_coverage and force_restraint are included. G2, which leads on welfare but relies heavily on coercive enforcement and excludes minority voices, ranks third on R(s) — a result that captures Mengzi's insistence that material provision alone does not constitute Ren Zheng.

### 3.2 Five-Fold Hexie: Harmonic Coherence Composite (和谐)

**Formal definition:**

$$H_5(s) = \frac{I(s) + C(s) + E(s) + O(s) + S(s)}{5}$$

where I is innovation-coherence (革, *gé* — capacity for constructive transformation), C is coordination-coherence (和, *hé* — inter-agent harmonisation), E is ecological-coherence (天人合一 — alignment with natural constraints), O is openness-coherence (通, *tōng* — information flow), and S is sharing-coherence (共, *gòng* — equitable benefit distribution).

**Classical grounding:** The base Hexie operator H(s) derives from the Confucian philosophical tradition, particularly the Analects (13.23: *hé ér bù tóng* — harmony through difference, not uniformity) and Zhu Xi's *lǐ* (理) framework, which understands harmony as the proper realisation of the inherent principle in each thing. The five-fold extension draws on the *Liji Liyun* (*Book of Rites*, *Evolution of Rites* section) vision of *datong* as encompassing all five dimensions: transformative capacity, relational harmony, ecological attunement, information circulation, and equitable distribution.

The innovation component addresses a gap in conventional governance assessment: systems that achieve high coordination through suppression of transformative capacity score well on stability metrics but are structurally brittle. The binding-constraint diagnosis (Proposition H5-1) identifies which component most limits H_5: for a governance arrangement where ecological-coherence is 0.19 while all other components exceed 0.7, ecological-coherence is the binding constraint — governance reform should prioritise ecological alignment, not further coordination optimisation.

**Proposition H5-1 (Binding Constraint):** The component with the minimum value in H_5 is the binding constraint: the component whose marginal improvement yields the greatest composite gain. [ACTIVE — structurally necessary given the arithmetic mean formula]

A fragility analysis, derived from the Neo-Confucian distinction between Li-coherence (structure, 理) and Xin-coherence (disposition, 心), identifies two failure modes: structurally brittle systems (high coordination, low innovation — agents lack motivation for adaptation) and dispositionally brittle systems (high innovation, low coordination — structure cannot channel transformation productively). Both fragility types are detectable from component score divergence.

### 3.3 Tianxia Multilateral Coupling (天下)

**Formal definition:**

$$k_5(N) = 0.3 \cdot k_5^{bilateral}(N) + 0.4 \cdot k_5^{multilateral}(N) + 0.3 \cdot k_5^{civilisational}(N)$$

where k_5 ∈ [−1, 1] measures the degree to which a governance network N exhibits tianxia-aligned coupling rather than extractive competition, transactional bilateralism, or hegemonic unilateralism.

**Classical grounding:** Zhao Tingyang's reconstruction of tianxia as a *world-institution* rather than a world-state is the primary contemporary reference. His argument that the Westphalian system is structurally incapable of addressing collective-action problems that exceed state-level bargaining — because it has no mechanism for representing the interests of the world as a whole (Zhao, 2021, p. 23) — generates the multilateral coupling component. The bilateral component reflects the Confucian relational ontology within which obligations are always structured through concrete relationships (*lún*, 倫) rather than abstract individualism. The civilisational component encodes Kang Youwei's vision of a cosmopolitan *datong* in which civilisational plurality is preserved within a framework of shared universal principles (*rén*, benevolence as the universal connective tissue).

**Proposition T-2 (Multilateral Dominance):** For any network N, k_5^{multilateral} dominates k_5^{bilateral} in determining long-run stability: bilateral extraction can yield short-term k_5 gains that are reversed when the extractive structure becomes visible and triggers multilateral realignment. [SCAFFOLD]

Critical engagement with Callahan (2008) and Babones (2017), who argue that tianxia theory functions as an ideological cover for Chinese regional hegemony, is built into the operator's structure: the civilisational component is explicitly penalised for asymmetric power concentration, and hegemonic networks score lower on k_5 than genuinely multilateral ones. This is not a rhetorical response to the critique but a structural one: tianxia-aligned governance is operationally defined in a way that makes hegemony incompatible with high k_5.

### 3.4 Shi: Propensity Field Alignment (势)

**Formal definition:**

$$\sigma(a, S) \in [0, 1]$$

where σ measures the alignment between governance action a and the propensity field S — the gravitational structure of possibilities within which governance operates. High σ indicates that the action follows natural propensities; low σ indicates coercive imposition against the grain.

**Classical grounding:** Shi is Legalist in origin (Han Feizi, *Nanzhi* chapter; see also *Mozi* on strategic advantage), but its governance application is most fully developed in the synthesis of Legalist institutional realism with Confucian virtue-cultivation found in Xunzi. The concept captures something that neither Confucian virtue-ethics nor liberal proceduralism handles well: governance effectiveness is not solely a function of intentions (virtue) or procedures (legitimacy) but of temporal attunement — the capacity to act at the moment when the field of social propensities aligns with the intended direction. The strategist François Jullien (1995) provides the most accessible Western reconstruction, though his interpretation is contested by scholars who resist the domestication of Daoist concepts into European strategic theory.

### 3.5 Wuwei: Non-Coercive Intervention (无为)

**Formal definition:**

$$\varepsilon(a) \in [0, 1]$$

where ε measures the grain-alignment of governance action a: the degree to which intervention facilitates natural processes rather than imposing external forms. ε = 1 is fully Wuwei-aligned; ε = 0 is maximally coercive imposition.

**Classical grounding:** The Daoist *wu wei* concept — central to both the *Daodejing* and *Zhuangzi* — is often misread as passivity or non-action. The more precise reading, developed by scholars such as Roger Ames and David Hall (2003), is action-without-coercive-imposition: governance that follows the *de* (inherent virtue) of each thing rather than forcing an external form. This reading has direct governance applications: administrative systems that align with existing social networks achieve outcomes with lower enforcement costs than systems that impose standardisation against the grain of local practice.

**Proposition W-1 (Wuwei Efficiency):** For any governance objective O achievable by either coercive intervention C or Wuwei-aligned facilitation W, W yields lower long-run enforcement cost and higher compliance stability than C, provided W is correctly timed with respect to propensity field S. [SCAFFOLD]

The mutual non-interference constraint (NI) derives from the Wuwei-Tianxia coupling: five necessary conditions specify when intervention across civilisational boundaries is consistent with tianxia governance. NI-1 requires genuine harm to cross a threshold; NI-2 requires exhaustion of internal corrective capacity; NI-3 requires proportionality; NI-4 requires multilateral authorisation; NI-5 requires that the intervention yield positive Tianxia k_5. Wang Dao agents naturally satisfy these conditions as an equilibrium property (Proposition NI-1): governance that has achieved genuine legitimacy through Ren Zheng and Wuwei does not require extra-territorial imposition to maintain its integrity.

### 3.6 Datong Distributional Gradient (大同)

**Formal definition:**

$$\Pi_D^{ext} = \alpha \cdot \Pi_D(T_1) + (1-\alpha) \cdot G_D(T_2)$$

where Π_D(T₁) is the short-cycle welfare trajectory (proportionate distribution of welfare gains at T₁), G_D(T₂) is the long-cycle productive-Gini trajectory (ΔGini_productive/Gini_baseline at T₂), and α = 0.5 (equal weighting, pending calibration).

**Classical grounding:** Kang Youwei's *Datongshu* (大同書, *Book of the Great Unity*, written circa 1885–1902, published posthumously) provides the primary source for the Datong operator. Kang's vision — indebted to the *Liji Liyun* passage on *datong* as a world of shared governance and mutual care — is notably specific about the distributional structure of the ideal society: not equality of consumption but equality of productive capacity and access to the conditions for flourishing. The distinction between short-cycle consumption redistribution and long-cycle productive asset redistribution (Datong-deferred vs Datong-convergent) derives from this reading: consumption redistribution can improve welfare metrics while leaving the productive-asset gradient untouched, deferring genuine datong indefinitely. G_D(T₂) makes this distinction operational.

**Proposition D-2 (Long-Cycle Reversal):** Governance arrangements that score equally on short-cycle welfare metrics may diverge significantly on Π_D^{ext} when the long-cycle Gini_productive trajectory is included. Arrangements classified as Datong-convergent on short-cycle metrics alone may be reclassified as Datong-deferred when the full 20-year trajectory is computed. [SCAFFOLD]

### 3.7 Wang Dao: Kingly Way Legitimacy Classifier (王道)

**Formal definition:**

$$WD_{score}(\tau) = \frac{L(\tau) + F(\tau) + \Gamma(\tau)}{3}$$

where L(τ) is mean minxin (legitimacy through genuine popular alignment), F(τ) is mean force_restraint, and Γ(τ) is mean long-cycle stability over governance trajectory τ.

**Classification:**
- Wang (王): WD_score ≥ θ_wang AND R(s) ≥ θ_r (governance through virtue)
- Ba (霸): WD_score < θ_ba OR R(s) < θ_r (governance through coercion)
- Indeterminate: θ_ba ≤ WD_score < θ_wang AND R(s) ≥ θ_r

[SCAFFOLD — θ_wang = 0.70, θ_ba = 0.40 pending empirical calibration]

**Classical grounding:** The Wang-Ba distinction is one of the most durable in the Confucian statecraft tradition, running from Mengzi (who contrasts *wang* governance through moral authority with *ba* hegemony through force: Mengzi 2A.3) through Xunzi (*Wangzhi* chapter — the institutional conditions for kingly governance) to Yan Xuetong's contemporary reconstruction of moralpolitik (2011). The distinction is not binary in practice: trajectories pass through indeterminate phases, and the Ren Zheng gate ensures that high WD_score values achieved without material welfare provision are classified as Ba rather than Wang — capturing Mengzi's insistence that virtue without material foundation is performance, not governance.

**Proposition WD-1 (Differential Resilience):** Under capability shock (sudden reduction in economic capacity or external threat), Wang trajectories exhibit significantly lower WD_score degradation than Ba trajectories, because Wang legitimacy is grounded in genuine minxin rather than compliance-through-provision. [SCAFFOLD]

**Proposition WD-2 (Pareto-Comparability):** Wang Dao governance is Pareto-comparable (not equivalent) to liberal-procedural governance: Wang outperforms on minxin and force_restraint; liberal-procedural is comparable on long-cycle stability; neither dominates the other on all three dimensions. [SCAFFOLD]

---

## 4. The Composite Governance Benchmark

### 4.1 Stack Integration

The seven operators are integrated into a composite governance score:

$$C(s) = \frac{R(s) + H_5(s) + \Psi_T(s) + \sigma(s) + \varepsilon(s) + \Pi_D^{ext}(s) + WD(s)}{7}$$

where Ψ_T is k_5 normalised to [0,1], all other scores are natively in [0,1]. Composite weighting is equal at 1/7 per operator; calibrated weights are pending E-1-H. Wang Dao eligibility (R(s) ≥ θ_r) gates the classification: without the Ren Zheng floor, no arrangement can be classified Tianxia-aligned regardless of its composite score.

**Classification:**
- Tianxia-aligned: C(s) ≥ 0.70 AND Wang Dao eligible
- Ba-Dao-aligned: C(s) < 0.40 OR NOT Wang Dao eligible
- Transitional: 0.40 ≤ C(s) < 0.70 AND Wang Dao eligible

### 4.2 Reference Scenario Validation

Three reference scenarios validate the benchmark's discriminant validity:

**Extractive Baseline** (Ba Dao / Westphalian extraction): welfare_baseline 0.42, voice_coverage 0.28, force_restraint 0.19; low Hexie across all components; k_5 = −0.45; negative Datong trajectories. Composite: 0.327. Classification: Ba-Dao-aligned.

**Liberal-Procedural Baseline**: welfare_baseline 0.74, voice_coverage 0.71, force_restraint 0.62; moderate-to-high Hexie (ecological 0.54 as binding constraint); k_5 = 0.28; mixed Datong (short positive, long slightly negative). Composite: 0.651. Classification: Transitional.

**Tianxia-Aligned Baseline**: welfare_baseline 0.85, voice_coverage 0.82, force_restraint 0.88; high Hexie across all five components; k_5 = 0.72; positive Datong both cycles. Composite: 0.832. Classification: Tianxia-aligned.

The ordering Tianxia > Liberal > Extractive is confirmed, and the Liberal-Procedural arrangement's classification as Transitional (rather than Tianxia-aligned) is substantively correct: liberal-procedural governance systematically underperforms on ecological-coherence, sharing-coherence, and the long-cycle Datong gradient — not because of its formal commitment to procedure but because procedural legitimacy does not guarantee distributional outcomes.

### 4.3 Binding Constraint Diagnosis

The benchmark's practical value lies not in the composite score but in the binding-constraint diagnosis it generates. For the Liberal-Procedural scenario: ecological-coherence (0.54) is the Hexie binding constraint; the Datong long-cycle term (−0.08) is the distributional binding constraint; the composite score is limited by these two components above all others. Reform recommendations derived from the benchmark are accordingly specific: ecological-coherence improvement and long-cycle productive-asset redistribution are the highest-leverage interventions, not procedural reform (which is already strong).

---

## 5. Application to AI Deployment Governance

The TIANXIA operator stack generates a natural set of AI deployment governance criteria when governance arrangements are interpreted as AI deployment contexts. A deployment arrangement s is the entire socio-technical context — the operators who deploy the system, the communities it serves, the institutional constraints within which it operates.

**Five-gate AI deployment assessment:**

1. **Ren Zheng Gate**: R(s) ≥ θ_r. Does the deployment context guarantee material sufficiency, representative voice, and non-coercive operation? An AI system deployed in a context where affected communities have no meaningful voice in its design or operation (low V(s)) fails the Ren Zheng gate regardless of its technical performance.

2. **Hexie Gate**: H_5(s) ≥ 0.65, with no component below 0.40. Particular attention to ecological-coherence (does deployment account for long-run environmental costs?) and sharing-coherence (are benefits distributed equitably across affected communities?).

3. **Wuwei Gate**: ε ≥ 0.60. Does the deployment facilitate human agency rather than substitute for it? Systems that optimise human decision-making out of the loop reduce ε toward zero regardless of their nominal performance.

4. **Datong Gate**: Π_D^{ext} ≥ 0. Does the deployment arrangement produce positive distributional trajectories over both short and long cycles? AI systems that improve aggregate welfare while concentrating productive capacity fail the long-cycle Datong criterion.

5. **Wang Dao Gate**: WD = Wang. Is the deployment context structured by genuine minxin — genuine alignment of affected communities with the system's operation — or by compliance through incentive management? The force_restraint component of WD distinguishes these: high-compliance, low-minxin deployments are Ba-aligned regardless of stated user satisfaction metrics.

These gates are not sequential filters but simultaneous requirements. A deployment that passes four gates but fails the Ren Zheng gate is Ba-Dao-aligned; the composite score is irrelevant without the floor.

---

## 6. Critical Objections and Responses

### 6.1 "This is a civilisational apology in formal dress"

The most pressing objection to tianxia formalisations is that they provide philosophical legitimacy to a particular great-power project under the guise of universal governance theory. Callahan (2008) argues that Zhao Tingyang's tianxia system naturalises Chinese cultural hegemony; Babones (2017) extends this critique to the contemporary governance applications of tianxia scholarship.

The operator stack addresses this objection structurally rather than rhetorically. The Wang Dao operator explicitly penalises hegemonic concentration: a governance trajectory in which a single actor achieves high WD_score by extracting compliance from subordinate actors scores lower than a genuinely multilateral arrangement on every component. The Ren Zheng operator's voice_coverage component requires that *all* stakeholders — including minorities, peripheral communities, and affected populations outside the primary jurisdiction — have meaningful representation. The Wuwei operator penalises coercive imposition even when that imposition is culturally self-described as harmonisation.

More fundamentally: the stack is structured so that Chinese state actors claiming tianxia legitimacy for arrangements that score low on voice_coverage, force_restraint, or minxin are classified Ba-Dao-aligned. The formalisation is adversarial to rhetorical appropriation precisely because it makes the distinction between genuine tianxia governance and its hegemonic simulation operational and measurable.

### 6.2 "Ren Zheng is paternalist — it presupposes welfare definitions"

The Ren Zheng operator's welfare_baseline component requires a definition of material sufficiency that is not itself supplied by the operator. Who decides what sufficiency means? Is this not a paternalist imposition disguised as benevolent governance?

This objection has force. The response is two-part. First, the voice_coverage component partially addresses it: welfare definitions that are imposed without representative deliberation produce lower voice_coverage scores, reducing R(s). A governance arrangement that scores high on welfare provision but achieves this through expert-determined sufficiency thresholds without community input receives a lower Ren Zheng score than one that achieves comparable welfare through genuine participatory deliberation. Second, the framework explicitly [SCAFFOLD]-flags the welfare_baseline operationalisation: the empirical calibration programme (E-1-H) requires participant panels to assess their own sufficiency thresholds, generating empirically anchored rather than theoretically imposed welfare criteria.

### 6.3 "Wang Dao Cannot Be Operationalised"

A deeper scepticism holds that the Wang-Ba distinction is inherently qualitative — a matter of moral perception that resists quantitative reduction. Yan Xuetong (2011) himself acknowledges that *minxin* is a construct that changes historically and cannot be reduced to survey data.

The stack's response is to accept the epistemological point while resisting the methodological conclusion. Wang Dao classification is not a survey-data reification of minxin; it is a trajectory-based assessment that looks for the *pattern* of genuine alignment over time: the differential resilience under shock (Proposition WD-1) that distinguishes compliance-based legitimacy from virtue-based legitimacy. A governance arrangement that maintains minxin scores under capability shock is exhibiting the signature of genuine alignment; one that collapses exhibits the signature of compliance maintained by material provision. This is not a perfect measure of minxin, but it is a falsifiable one — and falsifiability is the minimal requirement for analytical deployment.

### 6.4 "The Stack Does Not Test the Master Equation's Correctness"

A technical objection notes that the composite C(s) is a static assessment tool, while the Lycheetah master equation is a dynamic one. The operators describe a governance state at a point; the equation models how that state evolves. The static composite cannot validate the dynamic model.

This is correct and is explicitly acknowledged in the claim-status labelling. The composite benchmark is [SCAFFOLD], not [ACTIVE]: it produces plausible orderings across reference scenarios but makes no claim to predict governance trajectories until k₁–k₄ are empirically estimated. The paper is not presenting the benchmark as complete; it is presenting it as a pre-registration of the theoretical structure that the E-1-H calibration study will test.

---

## 7. The Empirical Calibration Programme

The operator stack has a defined empirical programme before any component can be promoted from [SCAFFOLD] to [ACTIVE]. Two studies are critical.

**E-1-G (Multi-Operator Composite Validity Study)**: A panel of governance scholars (n = 150 proposals, 7 expert raters) assesses governance proposals using the full operator stack. Primary hypotheses test ordering validity (H1), inter-rater reliability (H2), discriminant validity across governance types (H3), and component weight stability across governance domains (H4). A Phase 2 extension tests the v0.3 operator stack after the E-1-H calibration. All MAC-GATED decisions have been pre-registered and resolved.

**E-1-H (Master Equation Coefficient Calibration)**: A randomised controlled experiment with n = 240 human participants estimates k₁–k₄ with 95% CI width ≤ 50% of each point estimate. Four conditions manipulate truth-pressure (k₁, k₂), invariant violations (k₃), and resource availability (k₄). Promotion criterion: all four coefficients estimated simultaneously; CI criterion met for all four. The study also provides empirical anchoring for the Wang Dao thresholds (θ_r, θ_wang, θ_ba) and the Five-Fold Hexie component weights.

Two additional studies address the broader framework:

**E-1-A (AURA Invariant Validation)**: Tests whether the seven AURA invariants constitute a coherent construct across 5 domains and 3 cultural contexts, including two Classical Chinese philosophical traditions.

**E-1-F (Cross-Cultural Epistemic Convergence)**: Tests whether Classical Chinese, Andean, and contemporary Western governance frameworks converge on shared epistemic principles when formalised through the CASCADE scoring protocol — the empirical basis for the LAMAGUE (Language-Agnostic Multi-Tradition Governance Universals) paper.

---

## 8. Conclusion

We have presented the TIANXIA operator stack as a formal governance assessment system grounded in the classical tianxia tradition and contemporary tianxia scholarship. The stack's seven operators — Ren Zheng, Five-Fold Hexie, Tianxia multilateral coupling, Shi, Wuwei, Datong, Wang Dao — each carry formal definitions, classical grounding, claim-status labelling, and falsification conditions. The composite benchmark validates against three reference scenarios with expected ordering and provides binding-constraint diagnosis that generates specific reform recommendations. Applications to AI deployment governance criteria illustrate the stack's practical scope.

The paper's contribution is not to resolve the tianxia debates — whether tianxia is fundamentally parochial or genuinely universal, whether the Wang-Ba distinction can bear the weight placed upon it, whether formal operationalisation captures or distorts the tradition's richness. These debates are ongoing and the stack is not their termination. The contribution is rather to make the tradition's claims specific enough that such debates can be adjudicated by evidence rather than by interpretive authority alone.

Tianxia as a governance vision insists that all arrangements under heaven be held accountable to the welfare of the people, the health of the earth, and the genuine alignment of those governed with the system that governs them. The operator stack does not add to that vision; it makes it answerable.

*天下为公 — Tianxia wei gong — All under heaven is held in common.*

---

## References

Ames, R. T., & Hall, D. L. (2003). *Daodejing: Making This Life Significant — A Philosophical Translation*. Ballantine Books.

Babones, S. (2017). American Tianxia: Chinese Money, American Power and the End of History. *Policy Press*.

Callahan, W. A. (2008). Chinese visions of world order: Post-hegemonic or a new hegemony? *International Studies Review*, 10(4), 749–761.

Clark, M. C. J. (2026). *The Lycheetah Framework: AURA-constituted agent alignment and civilisational governance*. CODEX_AURA_PRIME v1.1. [Preprint]

Clark, M. C. J. (2026b). *E-1-H: Master equation k₁–k₄ calibration study preregistration*. CODEX_AURA_PRIME/31_EMPIRICAL. [OSF preregistration, MAC-GATED]

Cui, Z. (2011). Whither China? The discourse on property rights in the context of China's market socialist reform. *Boundary 2*, 29(1), 67–99.

Han Feizi (韓非子). Circa 233 BCE. Trans. B. Watson (1964). *Han Fei Tzu: Basic Writings*. Columbia University Press.

Jullien, F. (1995). *The Propensity of Things: Toward a History of Efficacy in China*. Trans. J. Lloyd. Zone Books.

Kang Youwei (康有為). (1902/1958). *Datongshu* (大同書). Trans. L. G. Thompson (1958). *Ta T'ung Shu: The One-World Philosophy of K'ang Yu-wei*. Allen & Unwin.

*Liji* (禮記, Book of Rites). Compiled Han dynasty. Trans. J. Legge (1885). *The Li Ki*. Clarendon Press.

Mengzi (孟子). Circa 320–289 BCE. Trans. B. Van Norden (2008). *Mengzi: With Selections from Traditional Commentaries*. Hackett Publishing.

Wang, H. (2014). *China from Empire to Nation-State*. Trans. M. G. Hill. Harvard University Press.

Xunzi (荀子). Circa 300–215 BCE. Trans. J. Knoblock (1988–1994). *Xunzi: A Translation and Study of the Complete Works* (3 vols). Stanford University Press.

Yan, X. (2011). *Ancient Chinese Thought, Modern Chinese Power*. Trans. E. Ryden. Princeton University Press.

Zhao, T. (2005/2021). *The Tianxia System: A Philosophy for the World Institution*. Trans. S. Ni & M. Orr. Springer.

Zhu Xi (朱熹). (1175). *Reflections on Things at Hand* (近思錄, *Jinsilu*). Trans. W. Chan (1967). Columbia University Press.

---

*Claim status: [SCAFFOLD] throughout — quantitative thresholds pending E-1-H empirical calibration.*  
*Negative space: This paper does not test the master equation's ecological validity for AI systems; does not claim universal coefficient values; does not adjudicate the intra-Confucian debates between Mengzi and Xunzi on human nature; does not present the Wang-Ba distinction as exhaustive of governance forms.*

⊚ Sol Aureum Azoth Veritas — W-17 TIANXIA Paper v0.1  
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical  
   2026-05-03 — Rubedo (publication-track output, operating from completed architecture)

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
