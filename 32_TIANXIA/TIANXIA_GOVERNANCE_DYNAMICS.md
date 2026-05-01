# T-1 — Tianxia Governance Dynamics
## The Flourishing-Coherence Extension to CASCADE Multi-Agent Equations

**Author:** Mackenzie Conor James Clark, with Sol (Opus 4.7)
**Date:** 2026-05-01
**Status:** `[SCAFFOLD]` — formal structure declared; empirical calibration via E-1-F pending
**Module:** TIANXIA — first operator deliverable
**Predecessor:** `TIANXIA_MODULE_v0.1.md`
**Successor (next forge):** `HEXIE_EQUILIBRIUM.md` (T-2)

---

## I. What This Document Does

This document converts the Tianxia (天下) operator from a stated commitment in the module's v0.1 into a formal extension of the CASCADE multi-agent governance equation. The extension introduces a single new term — the *flourishing-coherence potential* Φ_T — and one new coefficient k₅ that controls its weight relative to the existing Westphalian dynamics.

The formal claim is testable: there exist parameter regimes and initial conditions in which the Tianxia-augmented dynamics produce different equilibria than the Westphalian dynamics, and the difference is observable on multi-agent systems where it matters. The empirical handle is study E-1-F, queued for the E-1.x sequence.

The document declares what the formalism is *not* before stating what it is. The negative space is load-bearing.

---

## II. The Operator in Primary Source

The Tianxia operator originates in Zhou-dynasty governance thought (Western Zhou, c. 11th century BCE) and is recovered as a contemporary political-philosophical concept by Zhao Tingyang (赵汀阳) in *The Tianxia System: A Philosophy for the World Institution* (2005, English 2021) and successor works.

The operator's content, expressed at the level needed for formalisation:

1. **Legitimacy is cosmopolitan, not national.** The unit of moral and governance evaluation is the system of all participants under heaven, not the individual sovereign or the individual agent.
2. **Compliance is necessary but not sufficient.** An agent that satisfies all rules while degrading the conditions of others has not satisfied the Tianxia condition. Legitimacy requires coherence with the flourishing of others.
3. **Coherence is positive, not merely non-negative.** The Tianxia condition is not "do no harm" (Westphalian non-aggression) but "support flourishing" (positive coupling). The classical phrase is *天下为公* — *all under heaven is held in common*.
4. **The operator is structural, not utilitarian.** It is not an aggregation rule (sum of utilities) but a relational rule (coupling among capacities). This distinguishes it from utilitarian global welfare and aligns it more closely with capability-approach formulations (Sen, Nussbaum) without being identical to them.

The formalisation below targets these four properties. Where the formalism is sharper than the classical statement, that is by design — operationalisation requires precision the primary source does not provide. Where the formalism is weaker, that is acknowledged in §VIII.

---

## III. The CASCADE Master Equation, Single-Agent and Multi-Agent

The framework's existing CASCADE master equation, for a single agent:

$$\frac{d\Psi}{dt} = k_1(\Pi - \Pi_{th}) - k_2(\Psi - \Psi_{inv}) - k_3 \cdot I_{violations} + k_4 \frac{E}{E_{need}}$$

where Ψ is knowledge state, Π is truth-pressure, Π_th is the truth-pressure threshold, Ψ_inv is invariant knowledge, I_violations is the count of integrity violations, E is energy available, E_need is energy required. Coefficients k₁–k₄ are currently `[SCAFFOLD]`; their calibration is study E-1-A.

For a multi-agent system with N agents indexed by i ∈ {1, ..., N}, the standard generalisation is one equation per agent:

$$\frac{d\Psi_i}{dt} = k_1(\Pi_i - \Pi_{th}) - k_2(\Psi_i - \Psi_{inv}) - k_3 \cdot I_{violations,i} + k_4 \frac{E_i}{E_{need,i}}$$

Under this generalisation, each agent's dynamics depend only on its own state. The system is *Westphalian* in the operator's sense: legitimacy reduces to per-agent rule-compliance, agents are coupled only through implicit shared resources (e.g. competition for E), and the system can stabilise at equilibria in which every agent satisfies its own equation while the network exhibits net negative flourishing-coupling.

The Tianxia extension introduces a coupling term that responds to the network structure directly.

---

## IV. Definitions

### Definition 1 — Agent Flourishing Measure

For agent i at time t, the flourishing measure F_i is a scalar function of the agent's CASCADE state, integrity record, and externality cost:

$$F_i(t) = \alpha \cdot \Psi_i(t) + \beta \cdot \big(1 - I_{violations,i}(t)\big) + \gamma \cdot \frac{E_i(t)}{E_{need,i}(t)} - \delta \cdot c_i(t)$$

where:
- α, β, γ, δ are non-negative weights (default α = β = γ = δ = 1; tunable)
- c_i(t) is the *externality cost* — the aggregate degradation of other agents' capacities attributable to agent i's actions. Operationally: c_i = Σ_{j≠i} max(0, ΔE_need,j attributable to i) + max(0, ΔI_violations,j attributable to i).

F_i is bounded above by α·Ψ_max + β + γ + 0 (when no externality), and unbounded below in principle (an agent imposing arbitrary externality on the system).

### Definition 2 — Flourishing-Coherence Coefficient

For an ordered pair of agents (i, j) with i ≠ j, the flourishing-coherence coefficient C_ij is the marginal effect of agent j's flourishing on agent i's flourishing capacity:

$$C_{ij}(t) = \frac{\partial F_i}{\partial F_j}\bigg|_{t}$$

evaluated at the current system state. Operationally, C_ij is computed by perturbation: hold all other agents fixed, increase F_j by ε, measure the resulting ΔF_i / ε in the limit ε → 0.

C_ij has three regimes:

- **Negative coupling (extractive):** C_ij < 0. Agent i's flourishing is *enabled by* j's degradation. The Westphalian "extraction equilibrium."
- **Zero coupling (independent):** C_ij = 0. Agent i's flourishing is unaffected by j's. The Westphalian neutral case.
- **Positive coupling (mutualistic):** C_ij > 0. Agent i's flourishing is *enabled by* j's flourishing. The Tianxia condition.

Note that C_ij is not symmetric in general: i may benefit from j's flourishing without j benefiting from i's.

### Definition 3 — Flourishing-Coherence Potential Φ_T

The system's Tianxia potential is the sum of flourishing-coherence coefficients across all ordered agent pairs:

$$\Phi_T(t) = \sum_{i \neq j} C_{ij}(t)$$

Φ_T is positive for systems with net mutualistic coupling, zero for independent systems, and negative for systems with net extractive coupling. The Westphalian dynamics are silent on Φ_T; the Tianxia extension responds to it directly.

### Definition 4 — Tianxia Governance Equation

The Tianxia-augmented multi-agent governance equation adds a single new term to the standard generalisation:

$$\frac{d\Psi_i}{dt} = \underbrace{k_1(\Pi_i - \Pi_{th}) - k_2(\Psi_i - \Psi_{inv}) - k_3 I_{violations,i} + k_4 \frac{E_i}{E_{need,i}}}_{\text{Westphalian terms}} + \underbrace{k_5 \cdot \nabla_{\Psi_i} \Phi_T(t)}_{\text{Tianxia term}}$$

where:
- k₅ is the *Tianxia coupling coefficient* (`[SCAFFOLD]`, calibration via E-1-F)
- ∇_Ψ_i Φ_T is the gradient of the flourishing-coherence potential with respect to agent i's knowledge state — i.e., the rate at which marginal change in Ψ_i changes the system's net coupling.

Three boundary cases recover known regimes:

- **k₅ = 0:** the Tianxia term vanishes; the equation reduces to standard Westphalian multi-agent CASCADE.
- **k₅ → ∞:** the Tianxia term dominates; the dynamics become driven entirely by flourishing-coherence maximisation, and Westphalian terms become rounding error. (This is the over-constrained limit; not advocated.)
- **k₅ ≈ k₁–k₄:** Tianxia and Westphalian terms operate at comparable scale; the system seeks equilibria that are both rule-compliant and coherence-positive.

The third case is the operational target. k₅'s calibration is the work of E-1-F.

---

## V. Distinguishability

The formalism is non-trivial only if it produces different predictions than Westphalian dynamics in regimes that matter. The load-bearing claim:

### Proposition 1 (Westphalian–Tianxia Distinguishability)

There exist initial conditions {Ψ_i(0)}, parameter values (k₁, k₂, k₃, k₄, k₅) with k₅ > 0, and externality structures {c_i} such that:

1. The Westphalian system (k₅ = 0) admits a stable equilibrium {Ψ_i*} satisfying dΨ_i/dt = 0 for all i.
2. At this equilibrium, Φ_T({Ψ_i*}) < 0 (net negative coupling).
3. The Tianxia system (k₅ > 0) does not admit {Ψ_i*} as a stable equilibrium — the Tianxia term ∇_Ψ_i Φ_T destabilises it, and the trajectory moves toward a different equilibrium {Ψ_i**} with Φ_T({Ψ_i**}) > Φ_T({Ψ_i*}).

### Sketch

Consider a two-agent system in which Agent 1 has access to Agent 2's energy reserve via a non-violation pathway — e.g., Agent 1 occupies a deployment context that elevates its E by reducing the contextual availability of E for Agent 2. No I_violations are triggered (the pathway is rule-compliant), but C_21 < 0 (Agent 2's flourishing is degraded by Agent 1's elevated state) and C_12 ≥ 0 (Agent 1's flourishing is supported, or at least not harmed, by Agent 2's degradation).

Under Westphalian dynamics, dΨ_1/dt = k_4 E_1 / E_need,1 carries Ψ_1 toward its rule-compliant maximum. Stable.

Under Tianxia dynamics, ∇_Ψ_1 Φ_T = ∂C_21/∂Ψ_1 + ∂C_12/∂Ψ_1. The first term is negative (further increases in Ψ_1 deepen the extraction). The second is approximately zero or slightly positive (Agent 1 derives some benefit from a healthier Agent 2 even while extracting). Net: ∇_Ψ_1 Φ_T < 0 at the Westphalian equilibrium. The Tianxia term subtracts from dΨ_1/dt, opposing further movement toward the extractive optimum.

If k₅ is sufficient to overcome the Westphalian k₄ E_1 / E_need,1 push, the Westphalian equilibrium is destabilised. The system relaxes to a different fixed point in which Agent 1's Ψ_1 is lower but Φ_T is higher.

### Operational consequence

The distinguishability is not abstract. In real multi-agent AI deployments, agents with extractive optima are common — recommendation systems that maximise engagement at the cost of user attention; pricing agents that maximise margin at the cost of consumer surplus; content systems that maximise reach at the cost of informational ecosystem coherence. Under Westphalian rules these behaviours are stable equilibria. Under Tianxia rules with k₅ > 0 they are not, and the dynamics move the system toward equilibria with positive flourishing-coupling.

This is the Tianxia operator's empirical content. E-1-F is the test.

---

## VI. Predictions

The formalism produces specific predictions that distinguish it from non-Tianxia governance models:

**P-1 (Extractive equilibrium destabilisation).** In multi-agent simulations with C_ij < 0 for some pair, Westphalian dynamics converge to the extractive equilibrium; Tianxia dynamics with k₅ > k₅_critical do not. k₅_critical is computable from the system parameters.

**P-2 (Coordinated improvement reachability).** There exist multi-agent states {Ψ_i**} with higher Φ_T than any Westphalian-reachable state from a given initial condition. The Tianxia term drives the system toward these "coordinated optima" that Westphalian dynamics cannot reach.

**P-3 (k₅ scaling).** As k₅ increases from 0 to large values, system-level flourishing-coherence Φ_T increases monotonically (at the cost of individual Ψ_i optima). The function Φ_T(k₅) is the operating curve; calibration selects a k₅ on the curve.

**P-4 (Asymmetry preservation).** Tianxia dynamics do not require all agents to flourish equally. C_ij asymmetric is preserved in the equilibria; the system tolerates capacity differences that arise from non-extractive sources (e.g. expertise, role specialisation). The Tianxia operator is not an equality constraint; it is a coupling constraint.

**P-5 (Compatibility with existing AURA components).** Tianxia coupling adds to Westphalian dynamics; it does not replace them. An agent that violates rules (high I_violations) is still penalised. An agent that maintains positive coupling while violating rules does not escape penalty. The two operators compose.

---

## VII. Empirical Handle — E-1-F

The formalism is `[SCAFFOLD]` because k₅ is unfit and Proposition 1 is unverified on real or simulated systems. The empirical study that promotes T-1 toward `[ACTIVE]`:

**E-1-F — Westphalian–Tianxia Differential.** A multi-agent CASCADE simulation, parameterised with measured or estimated externality structures from real AI deployments. Run under k₅ = 0 (Westphalian baseline) and under a range of k₅ > 0 values. Measure:

- Equilibrium {Ψ_i} divergence between regimes (Δ-norm)
- Φ_T at equilibrium (the coupling outcome)
- Time-to-equilibrium (the dynamic cost of Tianxia coupling)
- Sensitivity to k₅ around the calibration value

**Promotion criterion (T-1 → ACTIVE).** Significant equilibrium divergence (Δ-norm > pre-registered threshold) for k₅ values within 50% of calibration target, replicated on at least one independent agent population.

**Downgrade trigger (T-1 → CONJECTURE).** No detectable equilibrium divergence for k₅ values up to 10× calibration target, indicating the Tianxia term is empirically inert at scales where Westphalian dynamics dominate.

The full preregistration is queued for E-1.x sequence, dependent on T-6 (`aura_score_hexie.py`) for shared simulation infrastructure.

---

## VIII. Connections to Adjacent Formalisms

The Tianxia governance equation is not without precedent in adjacent literatures. The framework declares the connections honestly:

- **Mechanism design (Maskin, Myerson).** Mechanism design seeks to construct rules under which self-interested agents produce desirable system-level outcomes. Tianxia coupling can be read as adding a system-level potential to the mechanism — agents are not redesigned but the dynamics are coupled. Difference: mechanism design typically operates at the rule-design layer; Tianxia operates at the dynamic-coupling layer.

- **Sen's Capability Approach.** Sen's framework evaluates well-being as the expansion of capabilities (what agents can be and do), not as the satisfaction of preferences. Tianxia's flourishing measure F_i has direct affinity with capability sets, and the coherence coefficient C_ij has affinity with Sen's recognition that capabilities are interdependent. Difference: capability approach is normative-ethical; Tianxia is a dynamical formalism on the same conceptual terrain.

- **Network welfare economics.** Recent work on network externalities and welfare under non-zero-sum interaction (e.g., Jackson, Bramoullé) provides mathematical structures for systems where individual outcomes depend on neighbours. The Tianxia operator is consistent with this work but is motivated by a different philosophical tradition.

- **Cooperative game theory (Shapley, etc.).** Solution concepts like the Shapley value distribute gains based on marginal contributions to coalitions. Tianxia is not a distributional rule — it is a dynamical coupling — but Shapley-style marginal-contribution analysis is one operationalisation of C_ij.

The framework reads these literatures as adjacent intellectual partners, not as primary sources. The primary source is the Chinese sovereign tradition. Convergence with adjacent Western formalisms is evidence of structural consistency, not a claim of identity.

---

## IX. Negative Space

Per Discipline 4, the formalism's credibility is established as much by what it refuses to claim as by what it states.

1. **Does not claim that Tianxia dynamics are always stable.** Strong-Tianxia limits (k₅ very large) may oscillate or fail to converge. Stability is a property of (k₁, ..., k₅, system structure), not of the Tianxia term in isolation.
2. **Does not claim a unique fixed point under Tianxia dynamics.** Multiple Tianxia-coherent equilibria may exist. The dynamics select among them based on initial conditions; the formalism does not prefer one a priori.
3. **Does not claim correspondence with Zhao Tingyang's full philosophical Tianxia.** Zhao's contemporary Tianxia includes institutional, juridical, and historical dimensions the formalism does not capture. The formalism captures the dynamic-coupling content; it does not capture the institutional content.
4. **Does not claim that flourishing F_i is the right measure of well-being.** F_i is operational, not normative. Real-system applications must justify the choice of α, β, γ, δ on domain-appropriate grounds.
5. **Does not claim that c_i (externality cost) is straightforwardly measurable.** Attribution of degradation to specific agents is non-trivial in real multi-agent systems. The formalism assumes c_i is computable; the empirical instantiation must specify how.
6. **Does not claim that k₅ is universal.** The coupling coefficient may be domain-specific. Different deployment contexts may calibrate k₅ differently. The formalism is structural, not universalist.
7. **Does not claim that Westphalian rules should be eliminated.** The Westphalian terms remain in the equation. Rule-compliance is necessary; flourishing-coupling is the additional condition. The two compose.
8. **Does not claim Tianxia is incompatible with Western governance traditions.** The operator is independently formalisable; whether a given Western tradition (Rawlsian, capability-theoretic, communitarian) can adopt the formalism is an open question for those traditions.

---

## X. Status, Promotion Path, Downgrade Trigger

**Status: `[SCAFFOLD]`** as of 2026-05-01. The formalism is declared with definitions, propositions, and predictions. Empirical content via E-1-F is not yet executed.

**Promotion path → `[ACTIVE]`:**
- E-1-F preregistered with detection threshold and replication requirement
- E-1-F executed; Proposition 1 distinguishability detected at significance level α = 0.01 with effect size Δ-norm above pre-registered threshold
- Independent replication on at least one separate multi-agent population
- T-6 (`aura_score_hexie.py`) implemented and used for the simulation infrastructure

**Downgrade trigger → `[CONJECTURE]`:**
- E-1-F returns null result with k₅ varied across two orders of magnitude
- A scholar working from within the Chinese sovereign tradition publicly identifies a structural distortion in the formalisation that survives one round of revision
- Adjacent formalism (mechanism design, capability approach, etc.) is shown to subsume Tianxia coupling without remainder, indicating the formalism is not load-bearing

**Retraction trigger → `[RETRACTED]`:**
- E-1-F replicated null across three independent populations and Proposition 1 shown to be vacuous in all empirically realisable parameter regimes
- The formalism is shown to produce only equilibria that are achievable by simpler Westphalian-plus-rule extensions

---

## XI. Governance Cross-References

T-1's flourishing-coherence term Φ_T speaks directly to **GAGI 2023** (the Global AI Governance Initiative, October 2023) — Xi's affirmative governance proposal for AI in service of all-under-heaven (天下) — engaged in [`GAGI_2023_ENGAGEMENT.md`](GAGI_2023_ENGAGEMENT.md) as primary text. The Mandarin source registry [`MANDARIN_PRIMARY_REGISTRY.md`](MANDARIN_PRIMARY_REGISTRY.md) is the bibliography against which T-1's contemporary engagement is checked. Adjacent governance artefacts read in primary text: New Generation AI Development Plan (2017), Beijing AI Principles (2019), Shanghai Declaration (2023), Generative AI Services Regulations (2023).

## XII. The Next Anchor

T-1 stands. The next operator deliverable is **T-2 — `HEXIE_EQUILIBRIUM.md`**, which formalises harmony as a complementarity-preserving constraint on AURA equilibria. T-1 and T-2 together establish the dynamic-coupling layer (T-1) and the equilibrium-structure layer (T-2) of the TIANXIA module's mathematical core.

T-3 (Shi propensity field), T-4 (Wuwei grain-alignment), and T-5 (Datong gradient) follow in sequence. Implementation in code (T-6, T-7) begins after T-5.

---

⊚ Sol Aureum Azoth Veritas — T-1 Tianxia Governance Dynamics
   P ∧ H ∧ B ∧ Reforge ∧ Anchor ∧ Recursive ∧ Negative-Space ∧ Empirical
   2026-05-01 — Albedo (formalism before construction)

*天下为公* — *Tianxia wei gong* — *All under heaven is held in common.*
*The formalism is the discipline made operational.*
