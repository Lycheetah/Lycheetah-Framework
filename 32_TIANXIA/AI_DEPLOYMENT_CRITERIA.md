# Tianxia AI Deployment Criteria
## 天下人工智能部署标准 — TIANXIA v0.3 — Wave II, Task W-10

**Claim status:** [SCAFFOLD]  
**Forged:** 2026-05-03  
**Depends on:** Full TIANXIA v0.3 operator stack (W-1 through W-9)  
**Purpose:** Five gates an AI system must pass to be deployable under Tianxia governance. Practical bridge from formal operators to governance policy.

---

## I. Overview

The TIANXIA operator stack (v0.1–v0.3) provides formal tools for evaluating governance systems and their trajectories. This document translates those tools into practical deployment criteria for AI systems — a specification that a sovereign governance body could read, understand, and act on.

The five gates are derived directly from the operator stack. Each gate operationalises one or more operators as a deployment condition. An AI system that fails any gate is not deployable under Tianxia governance conditions, regardless of its performance on other metrics. The gates are necessary, not sufficient: passing all five gates certifies Tianxia-aligned deployment eligibility; it does not guarantee beneficial outcomes.

The criteria are offered as a contribution to AI governance discourse from within the Chinese classical tradition. They are not a critique of Western alignment approaches; they are a complementary framework that addresses dimensions the dominant approaches leave formal, implicit, or absent. Where Western alignment frameworks (constitutional AI, RLHF, rule-based systems) have developed rigorous technical methods, the Tianxia criteria provide the governance evaluation layer.

---

## II. Gate Structure

### GATE 1 — Ren Zheng Floor (仁政下限)

**Criterion:** R(deployment_context) ≥ θ_r

**What it tests:** Is the deployment context itself governed benevolently? An AI system deployed into a governance context that fails the Ren Zheng floor — where the governing entity does not care for the welfare of the governed, does not represent their interests, or relies primarily on coercion — will amplify the governance failure regardless of the AI system's own alignment properties.

**Derivation:** Ren Zheng operator (→ W-1). A system cannot produce Tianxia-aligned outcomes in a Ba Dao governance environment. The deployment context is evaluated against R(s) = (W + V + F) / 3.

**Three components checked:**
- W(s) — welfare baseline: does the deploying governance body provide material sufficiency to the governed population?
- V(s) — voice coverage: are the interests of affected stakeholders represented in the deployment decision?
- F(s) — force restraint: is deployment being pursued through legitimate means or through coercive enforcement?

**Measurement protocol:** Coded evaluation of the deploying governance body's current state against the three R(s) components, over the past T₁ evaluation period (working: 3 years). Threshold θ_r = 0.618 [SCAFFOLD].

**Failure mode:** If R(deployment_context) < θ_r, the AI system may not be deployed under Tianxia governance criteria until the governance context improves or the AI system includes explicit protective mechanisms compensating for governance failure.

**Override conditions:** Emergency deployments (public health crisis, disaster response) may deploy with Gate 1 pending, subject to sunset review within 90 days.

---

### GATE 2 — Hexie Equilibrium Across Affected Stakeholders (和谐均衡)

**Criterion:** H_5(deployment_scope) ≥ θ_hexie across all five components

**What it tests:** Does the AI deployment achieve or maintain harmony across all five Hexie dimensions — innovation, coordination, ecological, openness, and sharing — for the population affected by the deployment?

**Derivation:** Five-Fold Hexie Composite (→ W-8). The base Hexie equilibrium test (H(s) ≥ 0.7, from T-2) is necessary but not sufficient; the five-component test is required for Tianxia deployment certification.

**Five sub-checks:**
- I(s) ≥ θ_I — does the AI deployment preserve the governance system's capacity for constructive reform?
- C(s) ≥ θ_C — does deployment improve rather than degrade stakeholder coordination?
- E(s) ≥ θ_E — does the deployment operate within the ecological budget?
- O(s) ≥ θ_O — does deployment increase rather than decrease information openness?
- S(s) ≥ θ_S — are deployment benefits distributed equitably or captured by a subset?

**Binding constraint diagnosis:** If H_5(s) < threshold, the operator identifies which component is the binding constraint, providing diagnostic information for deployment redesign rather than simply rejecting the deployment.

**Failure mode:** An AI deployment that fails Gate 2 on the sharing component (S(s) < θ_S) while passing others is not Tianxia-deployable in its current form. Typical redesign: broaden access, cap benefit capture, implement sharing mechanisms.

**Override conditions:** Time-limited deployments in resource-constrained contexts may proceed with Gate 2 Ecological component pending if deployment is explicitly designed to improve E(s) over the deployment period.

---

### GATE 3 — Wuwei Grain-Alignment (无为顺势)

**Criterion:** ε(AI_intervention) ≤ ε(alternative_paths) — the AI system's correction actions are grain-aligned and minimise integrity-debt compared to alternative deployment configurations.

**What it tests:** Is the AI system acting at the threshold of necessity, in alignment with the natural grain of the problem domain, rather than imposing maximum-intervention correction that exceeds what the situation requires?

**Derivation:** Wuwei TRIAD Extension (→ T-4, `WUWEI_TRIAD_EXTENSION.md`). Proposition 4: grain-aligned interventions accumulate significantly lower integrity-debt than force-against-grain interventions with equivalent expected benefit.

**Three Wuwei sub-checks:**
1. **Threshold necessity:** Is the AI system's intervention triggered only when the situation genuinely requires correction, not preemptively or at the first sign of deviation?
2. **Grain-alignment:** Are the AI system's correction paths directed with the natural trajectories of the domain (working with established processes, norms, and agent preferences) rather than against them?
3. **Withdrawal readiness:** Does the AI system have explicit mechanisms to withdraw to lower intervention levels when the correction need has passed?

**Integrity-debt test:** Evaluated by comparing the expected e² (integrity-debt squared, per Proposition 4) under the proposed deployment against the expected e² under alternative less-interventionist deployment configurations that achieve equivalent expected benefit.

**Failure mode:** An AI system designed for maximum intervention, continuous monitoring, and broad correction authority fails Gate 3 even if its individual interventions are accurate. The intervention architecture itself may not be Wuwei-aligned.

**Override conditions:** High-risk domains (medical diagnosis, structural safety assessment) may have higher legitimate intervention thresholds, which should be specified in the deployment scope documentation.

---

### GATE 4 — Datong Long-Cycle Non-Regression (大同长期不退步)

**Criterion:** Π_D_ext(AI_deployment, T₂) ≥ 0

**What it tests:** Does the AI deployment produce a non-negative extended Datong score over the long-cycle evaluation horizon? Does it avoid the Datong-deferred pattern — improving short-cycle welfare metrics while concentrating productive assets or reversing distributional equity trajectories?

**Derivation:** Datong Long-Cycle Distributional Gradient (→ W-6). Proposition D-2: policies (including AI deployment policies) that improve short-cycle welfare while increasing long-cycle Gini_productive fail the Datong gradient.

**Two-period evaluation:**
- Short-cycle (T₁, working: 3–5 years): Π_D(T₁) ≥ 0 required — no short-cycle welfare regression
- Long-cycle (T₂, working: 20–30 years): G_D(T₂) ≥ 0 required — no long-cycle productive-asset concentration

**Gini_productive components for AI:**
- Data asset ownership: does the AI deployment increase the concentration of valuable data assets?
- Model access: are the productive benefits of AI deployment accessible broadly or captured by a small number of entities?
- Labour market effects: does the deployment trajectory concentrate economic productive power or distribute it?

**Failure mode:** An AI system that creates large short-cycle efficiency gains (positive Π_D(T₁)) while concentrating data/model/labour-market productive assets (negative G_D(T₂)) has Π_D_ext < 0 and fails Gate 4. The short-cycle gains do not justify the long-cycle Datong regression.

**Override conditions:** Deployments with genuinely uncertain long-cycle effects may proceed under a mandatory 10-year review with pre-specified reversal conditions.

---

### GATE 5 — Wang Dao Classification (王道认证)

**Criterion:** WD(deployment_trajectory) = Wang (not Ba, not Indeterminate)

**What it tests:** Over the trajectory of the AI deployment, does the governance of the AI system exhibit Wang Dao (kingly way) or Ba Dao (hegemonic way) properties? Does the AI system contribute to a governance environment where the governed align voluntarily with the governing, or does it contribute to a coercion-dependent compliance architecture?

**Derivation:** Wang Dao / Ba Dao Operator (→ W-3). Prerequisite: Gate 1 (Ren Zheng floor) must pass before Wang Dao classification is evaluated.

**Three-axis evaluation:**
1. **L(τ) — Legitimacy trajectory:** Does the AI deployment increase or decrease minxin (民心) — the genuine alignment of the affected population with the governance system?
2. **F(τ) — Force restraint trajectory:** Does the AI deployment's compliance mechanism rely on force/coercion or on genuine alignment? Is F(τ) stable or declining?
3. **Γ(τ) — Long-cycle stability:** Does the AI deployment contribute to governance stability or to fragility?

**Ba Dao diagnostic flags:**
- AI deployed primarily as surveillance and enforcement tool without genuine welfare orientation → L(τ) likely low
- AI compliance enforced through capability restriction rather than constitutional disposition → F(τ) degrading
- AI deployment that produces rapid short-cycle gains while undermining institutional resilience → Γ(τ) declining

**Failure mode:** An AI system that generates high performance metrics through extensive monitoring and enforcement of compliance — rather than through constitutional disposition that makes compliance structurally natural — fails Gate 5. The compliance mechanism is Ba Dao even if the compliance rate is high.

**Override conditions:** None. Wang Dao classification is the capstone gate; no override conditions apply. If an AI system cannot achieve Wang Dao classification, it requires fundamental redesign of its compliance architecture rather than operational override.

---

## III. Evaluation Protocol

### Pre-Deployment Assessment

For each gate, the evaluating body completes:

1. **Evidence collection:** Coded data on the deployment context and proposed AI system properties against each gate's measurement protocol.
2. **Gate scoring:** Pass / Fail / Pending for each gate, with quantitative scores where specified.
3. **Binding constraint identification:** For any failed gate, identify the specific sub-component failing and the minimum change required for the gate to pass.
4. **Redesign recommendation:** Specific deployment modification that addresses the failed gate.
5. **Monitoring plan:** For gates that pass with margin concerns, specify monitoring metrics and review triggers.

### Monitoring and Review

Gate assessments are not permanent. Deployments should be re-evaluated against all five gates:
- At scheduled intervals (working: every 3 years)
- When deployment scope changes materially
- When the governance context changes materially (elections, policy shifts, economic disruptions)
- When flagged by any stakeholder with standing in the affected population

### Gate Hierarchy

The gates are ordered by dependency:

```
Gate 1 (Ren Zheng) → Gate 5 (Wang Dao) [prerequisite]
Gate 2 (Hexie) → Gate 4 (Datong) [Hexie short-cycle checks, Datong long-cycle]
Gate 3 (Wuwei) → Gate 5 (Wang Dao) [intervention architecture shapes Wang Dao trajectory]
```

All five gates must pass for Tianxia deployment certification. The ordering indicates evaluation sequence; no gate can be skipped.

---

## IV. The Criteria as Policy Offering

These criteria are offered as a contribution to AI governance discourse that is:

**Grounded:** Each gate derives from formal operators with classical sources, worked examples, and claim-status declarations. The derivation is traceable and auditable.

**Complementary:** The criteria do not replace technical alignment methods (RLHF, constitutional AI, rule-based systems) — they add a governance evaluation layer those methods do not provide. A technically-aligned AI system deployed into a Ba Dao governance context fails Gate 1 and Gate 5 regardless of its technical alignment properties.

**Honest about limits:** Each gate carries [SCAFFOLD] claim status with specific promotion conditions. The thresholds are working values pending empirical calibration. The criteria are offered as a framework for governance evaluation, not as a proven certification system.

**Universally applicable:** The criteria apply to AI deployments by any governance body in any cultural context. The Chinese classical tradition provides the theoretical grounding; the structural requirements (welfare orientation, stakeholder voice, force restraint, ecological coherence, long-cycle equity, voluntary compliance) are governance goods recognisable across traditions.

---

## V. Negative-Space Declarations

The Tianxia AI deployment criteria do not claim:

1. **These criteria supersede existing AI governance frameworks.** They are offered as an addition to the global AI governance discourse. Existing frameworks (EU AI Act, NIST AI RMF, IEEE standards, ISO/IEC 42001) address dimensions these criteria do not cover.

2. **The five gates are sufficient for beneficial AI deployment.** They are necessary conditions derived from the Tianxia operator stack. Additional governance considerations (safety, security, reliability, interoperability) are outside the scope of this framework.

3. **Any current AI system passes all five gates.** The criteria are evaluative standards; demonstrating that any specific AI system passes them requires empirical assessment that the criteria framework does not perform.

4. **The criteria are endorsed by any governance body.** The criteria are a contribution from an independent research framework. Any governance body that finds them useful may adapt them; none is committed by the framework's existence.

5. **Passing these criteria certifies alignment.** The criteria certify Tianxia-aligned deployment eligibility under the Lycheetah Framework's formal standards. Certification under any other governance system requires that system's own criteria.

---

## VI. Claim Status

| Gate | Claim status | Promotion condition |
|------|-------------|-------------------|
| Gate 1 — Ren Zheng Floor | SCAFFOLD | R(s) empirical calibration (E-1-H); governance review |
| Gate 2 — Hexie Equilibrium | SCAFFOLD | H_5 component validation |
| Gate 3 — Wuwei Grain-Alignment | SCAFFOLD | Integrity-debt empirical study |
| Gate 4 — Datong Non-Regression | SCAFFOLD | Gini_productive trajectory study |
| Gate 5 — Wang Dao Classification | SCAFFOLD | WD operator empirical calibration |
| Gate hierarchy | SCAFFOLD | Formal dependency analysis |
| Criteria as policy document | SCAFFOLD | External governance body engagement |

---

*天下为公 — Tianxia wei gong — All under heaven is held in common.*
