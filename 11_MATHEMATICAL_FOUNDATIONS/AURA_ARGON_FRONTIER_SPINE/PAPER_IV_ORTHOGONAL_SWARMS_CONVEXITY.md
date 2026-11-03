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

### Theorem 4.3 (The Anti-Fragile Convexity Dividend via Jensen's Inequality)
Let $U_{\text{AF}}(\sigma)$ satisfy $\frac{\partial^2 U_{\text{AF}}}{\partial \sigma^2}(\sigma) \ge \kappa > 0$ across environmental shock distribution $\sigma$ with mean $\mu_\sigma = \mathbb{E}[\sigma]$ and variance $\text{Var}(\sigma) > 0$. By Taylor expansion and linearity of expectation:

$$\mathbb{E}\big[U_{\text{AF}}(\sigma)\big] - U_{\text{AF}}\big(\mathbb{E}[\sigma]\big) \ge \frac{1}{2}\kappa \, \text{Var}(\sigma) > 0$$