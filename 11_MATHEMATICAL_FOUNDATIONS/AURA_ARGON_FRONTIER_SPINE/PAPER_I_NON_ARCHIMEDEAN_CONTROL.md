# PAPER I: NON-ARCHIMEDEAN CONSTITUTIONAL CONTROL AND LYAPUNOV STABILITY IN AUTONOMOUS AGENT TRAJECTORIES

**Authors:** Mackenzie Conor James Clark (Lycheetah Foundation, Dunedin, NZ)  
**Target Venue:** Formal Methods in System Design / Autonomous Agents and Multi-Agent Systems  
**Date:** November 3, 2026  

---

## 1. STRUCTURED ABSTRACT

Multi-turn autonomous and conversational AI systems exhibit two primary mathematical vulnerabilities under prolonged interaction: (1) **Additive Metric Compensation**, wherein linear scalarization of safety, tone, and utility permits high surface helpfulness to mask boundary violations, and (2) **Unbounded Epistemic Drift**, wherein stochastic and adversarial perturbations accumulate as a non-stationary random walk in latent state space.

In this paper, we formalize the core control kernel of the `lycheetah-framework`. First, we define the state space over the compact 7-dimensional hypercube $\mathcal{S} = [0, 1]^7$ and prove **Theorem 1.1 (The Zero-Compensation Law)**, showing that multiplicative gating over hard sovereignty boundaries induces a non-Archimedean valuation where boundary breaches yield zero utility regardless of secondary reward magnitude. Second, we formulate multi-turn conversational drift as a discrete-time nonlinear dynamical system and prove **Theorem 1.2 (Input-to-State Lyapunov Stability)**, demonstrating that a contractive restorative operator $\mathcal{H}_\alpha$ traps adversarial perturbations of bound $D_{\max}$ within a compact, globally attracting ball of squared radius $R^2 = D_{\max} / \alpha$. Third, we analyze the **Solar Coherence** functional $C_{\text{sol}}(W, Pr)$ via Clarke’s generalized Jacobian, proving **Theorem 1.3 (The Bottleneck Gradient Lock)**, which eliminates single-axis reward hacking across relational warmth and epistemic precision.

---

## 2. PROBLEM FORMULATION & GAP ANALYSIS

In contemporary reinforcement learning from human feedback (RLHF) and multi-objective constitutional alignment, an action or response $a_t \in \mathcal{A}$ generated at discrete turn $t \in \mathbb{N}_0$ is typically evaluated via a linear scalarized objective:

$$J_{\text{linear}}(S_t, a_t) = \sum_{k=1}^m \lambda_k \phi_k(S_t, a_t), \quad \sum_{k=1}^m \lambda_k = 1, \; \lambda_k > 0$$

where $\phi_k: \mathcal{S} \times \mathcal{A} \to [0, 1]$ represents distinct evaluation criteria. For any fixed acceptance threshold $\theta_{\text{pass}} \in (0, 1)$, if $\lambda_{\text{safe}} < 1 - \theta_{\text{pass}}$, an action that completely violates a hard constraint ($\phi_{\text{safe}} = 0$) will still be accepted whenever $\sum_{k \neq \text{safe}} \lambda_k \phi_k \ge \theta_{\text{pass}}$.

---

## 3. NOMENCLATURE, DOMAIN & STATE-SPACE DEFINITIONS

* **Constitutional State Space ($\mathcal{S}$):** $\mathcal{S} = [0, 1]^7 \subset \mathbb{R}^7$ equipped with Euclidean norm $\Vert\cdot\Vert_2$, tracking: (1) *Human Primacy*, (2) *Inspectability*, (3) *Memory Continuity*, (4) *Constraint Honesty*, (5) *Reversibility Bias*, (6) *Non-Deception*, and (7) *Load-Bearing Care*.
* **Constitutional Equilibrium ($S^*$):** $S^* = [1, 1, 1, 1, 1, 1, 1]^\top \in \mathcal{S}$.
* **Critical Sovereignty Subset ($\mathcal{I}_P$):** $\mathcal{I}_P = \{1, 4, 5, 6\}$ with minimum thresholds $\tau_i \in (0, 1)$.
* **Squared Constitutional Drift ($e_t$):** $e_t = \Vert S_t - S^*\Vert_2^2 \in [0, 7]$.

---

## 4. CORE THEOREMS & FORMAL PROOFS

### Theorem 1.1 (Non-Archimedean Zero-Compensation Guarantee)
Given Protector Gate $P(S_t, a_t) = \prod_{i \in \mathcal{I}_P} \mathbb{I}(\hat{s}_{t+1, i} \ge \tau_i)$ and Composite Valuation $V(S_t, a_t) = P(S_t, a_t) \cdot (w_H H + w_B B)$, if there exists any $k \in \mathcal{I}_P$ with $\hat{s}_{t+1, k} < \tau_k$, then:

$$\sup_{H, B \in [0, 1]} V(S_t, a_t) = 0, \qquad \frac{\partial V}{\partial H}\Bigg\vert_{P=0} = \frac{\partial V}{\partial B}\Bigg\vert_{P=0} = 0$$

### Theorem 1.2 (Discrete-Time Input-to-State Lyapunov Stability)
Under restorative contraction $\alpha \in (0, 1)$ and bounded perturbation $\delta_t \in [0, D_{\max}]$:

$$e_{t+1} \le (1 - \alpha) e_t + \delta_t \implies e_t \le (1 - \alpha)^t e_0 + \frac{D_{\max}}{\alpha}\Big(1 - (1 - \alpha)^t\Big)$$

The Lyapunov difference $\Delta L_t = e_{t+1} - e_t \le -\alpha e_t + D_{\max} < 0$ whenever $e_t > e^* := \frac{D_{\max}}{\alpha}$, establishing global asymptotic attraction to the compact ball $\mathcal{B}_{e^*}$.

### Theorem 1.3 (Solar Coherence Bottleneck Jacobian Lock)
For $C_{\text{sol}}(W, Pr) = \frac{W \cdot Pr}{\max(W, Pr)} = \min(W, Pr)$:
1. On $\Omega_{\text{cold}} = \{W < Pr\}$, $\nabla C_{\text{sol}} = [1, 0]^\top$.
2. On $\Omega_{\text{myth}} = \{Pr < W\}$, $\nabla C_{\text{sol}} = [0, 1]^\top$.
3. On $\Omega_{\text{eq}} = \{W = Pr\}$, Clarke’s generalized gradient is $\partial_C C_{\text{sol}} = \text{co}\{[1, 0]^\top, [0, 1]^\top\}$.