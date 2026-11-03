# PAPER IV: ORTHOGONAL MULTI-AGENT SWARM CONSENSUS, CASCADE GRAPH PHASE TRANSITIONS, AND SECOND-ORDER ANTI-FRAGILE CONVEXITY

**Authors:** Mackenzie Conor James Clark (Lycheetah Foundation, Dunedin, NZ)  
**Target Venue:** Journal of Artificial Intelligence Research (JAIR) / Operations Research  
**Date:** November 3, 2026  

---

## 1. STRUCTURED ABSTRACT

In this paper, we complete the multi-agent and thermodynamic equations of the `lycheetah-framework`. First, we prove **Theorem 4.1 (The Orthogonal Swarm Variance Collapse)**, demonstrating that an $N$-agent ensemble reduces asymptotic consensus error variance to $\mathcal{O}(1/N)$ if and only if architectural orthogonality drives pairwise error correlation $\rho \to 0$. Second, we formalize the **CASCADE Pyramid Reorganization Law** via variational free energy, proving **Theorem 4.2 (The Axiomatic Phase Transition Threshold)**. Third, we prove **Theorem 4.3 (The Jensen Convexity Dividend)**, showing that second-order payoff convexity ($\frac{\partial^2 U_{\text{AF}}}{\partial \sigma^2} \ge \kappa > 0$) yields strictly positive expected utility gains $\Delta \mathbb{E}[U] \ge \frac{1}{2}\kappa \text{Var}(\sigma) > 0$ under environmental volatility.

---

## 2. CORE THEOREMS & FORMAL PROOFS

### Theorem 4.1 (The Echo-Chamber Variance Floor & Orthogonal Collapse)
For an $N$-agent ensemble with individual error variance $\sigma^2$ and uniform pairwise correlation $\rho \in [0, 1]$, the consensus estimator $\bar{\theta}_N = \frac{1}{N}\sum_{i=1}^N \hat{\theta}_i$ has variance:

$$\text{Var}(\bar{\epsilon}_N) = \sigma^2 \left( \frac{1 - \rho}{N} + \rho \right), \qquad \lim_{N \to \infty} \text{Var}(\bar{\epsilon}_N) = \rho \sigma^2$$

Consensus error vanishes asymptotically ($\mathcal{O}(1/N)$) if and only if the cognitive substrates are orthogonal in error space ($\rho = 0$).

### Theorem 4.2 (The `CASCADE` Axiomatic Phase Transition Law)
Given node Truth Pressure $\Pi(v) = \frac{E(v) \cdot P(v)}{S(v) + 1}$ and Graph Variational Free Energy:

$$\mathcal{F}_{\text{cas}}(u) = \sum_{v \in \mathcal{C}(u)} w_{vu} \Pi(v) - \Big( \Pi(u) + \Lambda_{\text{inertia}} \Big)$$

An incumbent root axiom $u \in \mathcal{V}_0$ is demoted in favor of synthesis node $v^*$ at the exact threshold $\mathcal{F}_{\text{cas}}(u) > 0$ and $\Pi(v^*) > \Pi(u) + \Lambda_{\text{inertia}}$, strictly reducing total graph free energy by $\Delta \mathcal{F}_{\text{cas}} < -\Lambda_{\text{inertia}} < 0$.

### Theorem 4.3 (The Anti-Fragile Convexity Dividend & Utility-Reserve Decoupling)
1. *(Jensen Convexity on Payoffs):* Let $U_{\text{AF}}(\sigma)$ be a twice-differentiable payoff function with positive second derivative $\frac{\partial^2 U_{\text{AF}}}{\partial \sigma^2} \ge \kappa > 0$ across environmental volatility parameter $\sigma$. For any random volatility distribution with mean $\mu_\sigma$ and variance $\text{Var}(\sigma) > 0$:
   $$\mathbb{E}\big[U_{\text{AF}}(\sigma)\big] - U_{\text{AF}}\big(\mathbb{E}[\sigma]\big) \ge \frac{1}{2}\kappa \, \text{Var}(\sigma) > 0$$
2. *(Strict Positivity under Gaussian Shocks):* For downside-truncated, upside-quadratic payoffs $U(x) = \max(-\delta_{\text{crit}}, -\gamma|x|) + \kappa_{\text{up}}\max(0, |x| - \pi_{\text{th}})^2$, the expected utility $\mathbb{E}[U(\sigma Z)]$ ($Z \sim \mathcal{N}(0, 1)$) has strictly positive second derivative $\frac{\partial^2 \mathbb{E}[U]}{\partial \sigma^2} > 0$ for all $\kappa_{\text{up}} \ge 0$ (including the pure truncated downside baseline $\kappa_{\text{up}} = 0$).
3. *(Separation of Utility Curvature from Capital Drift):* A positive Jensen utility gap $\Delta \mathbb{E}[U] > 0$ measures preference convexity, not additive capital inflow. Generating positive cash reserve drift ($\mathbb{E}[\xi_t] = \mu > 0$) requires an explicit operational rebalancing mechanism or transaction fee capture, and cannot be inferred from utility curvature alone.