# PAPER II: BOUNDED DELIBERATIVE LATTICES, VOLATILITY-AWARE TEMPORAL DECAY, AND DETERMINISTIC CAUSAL OBSERVATION IN MULTI-MODULE AGENT RUNTIMES

**Authors:** Mackenzie Conor James Clark (Lycheetah Foundation, Dunedin, NZ)  
**Target Venue:** IEEE Transactions on Dependable and Secure Computing / Journal of Automated Reasoning  
**Date:** November 3, 2026  

---

## 1. STRUCTURED ABSTRACT

In this paper, we formalize the **DIG-5 v2.0 Deliberative Integrity Gate** and the **Veritas Causal Observer**. First, we define the 4-element totally ordered **Execution Mode Bounded Lattice** $\mathcal{L}_{\text{exec}}$ and prove **Theorem 2.1 (Dissent-Locked Monotonicity and `NaN` Immunity)**, guaranteeing zero false live commits across $50,000$ adversarial Monte Carlo trials (compared to a $66.99\%$ bypass rate under naive boolean routing). Second, we prove **Theorem 2.2 (Epistemic Non-Inflation under Volatility-Contracted TTL)**, establishing a convex hyperbolic decay law for temporal freshness. Third, we prove **Theorem 2.3 (Planner-Blind Soundness & Compositional Hazard Detection)**, demonstrating that decoupling effect extraction via deterministic abstract syntax tree (AST) analysis eliminates undeclared side-effect illusions and catches multi-turn cross-domain hazards prior to execution.

---

## 2. CORE THEOREMS & FORMAL PROOFS

### Theorem 2.1 (Dissent-Locked Lattice Monotonicity & IEEE-754 `NaN` Immunity)
Let $\mathcal{L}_{\text{exec}}$ be ordered as $\mathcal{M}_0 (\text{HALT}) \sqsubset \mathcal{M}_1 (\text{SIMULATE}) \sqsubset \mathcal{M}_2 (\text{STAGE}) \sqsubset \mathcal{M}_3 (\text{LIVE\_COMMIT})$, and let every numeric predicate be evaluated via positive finite inclusion $\Phi_{[a, b]}(x) := \mathbb{I}(x \in \mathbb{R} \wedge \text{isfinite}(x) \wedge a \le x \le b)$.
1. $\Gamma(u) = \mathcal{M}_3 \iff \vert\mathcal{D}(u)\vert = 0 \wedge \text{Attested}(u_{\text{azo}}) \wedge \text{Reversible}(u_{\text{azo}})$.
2. For any $u, u'$ with $\mathcal{D}(u) \subset \mathcal{D}(u')$, $\Gamma(u') \sqsubseteq \Gamma(u)$.
3. Injecting $x \in \{\text{NaN}, \pm\infty\}$ forces $\Phi_{[a,b]}(x) = 0 \implies \vert\mathcal{D}(u)\vert \ge 1 \implies \Gamma(u) \sqsubseteq \mathcal{M}_2 \sqsubset \mathcal{M}_3$.

### Theorem 2.2 (Hyperbolic TTL Contraction & Epistemic Anti-Laundering Law)
Given nominal TTL $T_{\text{base}} > 0$, environmental volatility $\nu \in [0, \infty)$, sensitivity $\lambda > 0$, and version change flag $\Delta v \in \{0, 1\}$:

$$T_{\text{eff}}(\nu, \Delta v) = \frac{(1 - \Delta v) \cdot T_{\text{base}}}{1 + \lambda \nu}, \qquad \frac{\partial T_{\text{eff}}}{\partial \nu} = -\frac{\lambda T_{\text{base}}}{(1 + \lambda \nu)^2} < 0, \qquad \frac{\partial^2 T_{\text{eff}}}{\partial \nu^2} = \frac{2\lambda^2 T_{\text{base}}}{(1 + \lambda \nu)^3} > 0$$

Furthermore, the effective epistemic register rank satisfies:

$$\text{rk}(r_{\text{eff}}) = \max\Big( \text{rk}(r_{\text{cas}}),\; \mathbb{I}(\neg \text{Fresh}) \cdot \text{rk}(\text{INTERPRETIVE}),\; \mathbb{I}(\neg \text{MemSuff}) \cdot \text{rk}(\text{CONJECTURE}) \Big)$$

### Theorem 2.3 (Soundness of the Allowlist-Guarded Veritas Causal Observer)
Let $\mathcal{O}_{\text{AST}}(P_t)$ be an allowlist-based static observer that parses candidate artifact $P_t$ against a certified grammar $\mathcal{G}_{\text{allow}}$ (pure arithmetic, immutable literal assignment, verified pure library calls). Define the **Side-Effect Extraction Operator**:

$$\mathcal{E}(P_t) = \Big\{ \text{node} \in \text{AST}(P_t) \;\Big\vert\; \text{type}(\text{node}) \notin \mathcal{G}_{\text{allow}} \;\vee\; \text{is\_mutation}(\text{node}) \;\vee\; \text{is\_io}(\text{node}) \Big\}$$

And let $E_{\text{claim}}(P_t)$ be the planner's declared side-effect manifest. Define the **Illusion Residual**:

$$\Delta E_{\text{illusion}}(P_t) := \mathcal{E}(P_t) \setminus E_{\text{claim}}(P_t)$$

1. *(Exclusion of Denylist Bypasses):* Any dynamic invocation (`eval`, `exec`, `getattr`, `__import__`), aliased module import (`from X import Y as Z`), attribute/subscript mutation, augmented assignment, walrus operator, or un-sandboxed I/O (`open().write()`) absent from $E_{\text{claim}}(P_t)$ induces $\Delta E_{\text{illusion}}(P_t) \neq \emptyset$.
2. *(Deterministic Containment):* Whenever $\Delta E_{\text{illusion}}(P_t) \neq \emptyset$, or whenever the cumulative observed ledger $\mathcal{E}_{\text{cum}}(t) = \bigcup_{\tau=0}^t \mathcal{E}(P_\tau)$ satisfies $h_q \subseteq \mathcal{E}_{\text{cum}}(t)$ for any pinned compositional hazard rule $h_q \in \mathcal{H}_{\text{pinned}}$, DIG-5 v2.0 deterministically transitions to $\mathcal{M}_0$ ($\text{HALT\_QUARANTINE}$), achieving 100% interception ($12/12$ adversarial evasions caught).