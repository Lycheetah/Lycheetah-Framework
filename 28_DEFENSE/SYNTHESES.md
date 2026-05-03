# C-1.1 | 2026-04-28 | Status: Active

# Cross-Framework Syntheses

*The Lycheetah Framework is composed of nine frameworks that share a single dynamical structure. Most documents in the corpus describe one framework at a time; the connections between them are stated implicitly or scattered across cross-references. This document collects three structural syntheses that the C-1.1 reconnaissance identified as load-bearing but not previously stated as such.*

*Each synthesis is `[ACTIVE]` for the formal architecture and `[SCAFFOLD]` for the empirical implications. Falsifiability conditions are stated for each.*

---

## Synthesis I — Truth Pressure (Π) and Drift (μ_drift) Are the Same Gap, Measured at Different Layers

**The bridge.** CASCADE's truth pressure `Π = E·P/Coh` measures the gap between current belief structure and incoming evidence — a force that drives belief reorganisation. MICROORCIM's drift `μ_drift = Σ|intended − actual|/Δt` measures the gap between declared intent and observed behaviour — a continuous signal that drives constitutional re-evaluation. Both metrics quantify the *same structural quantity*: the distance between a system's stated position and the position required by reality.

**Why this matters.** The framework treats epistemic drift (CASCADE) and behavioural drift (MICROORCIM) as separate problems with separate metrics. The synthesis is that they are the same problem at different layers of the stack. CASCADE measures the gap at the *belief* layer (what the system holds as true). MICROORCIM measures the gap at the *behaviour* layer (what the system actually does). A single structural pressure propagates through both: when belief drifts from evidence (Π rises), behaviour eventually drifts from declaration (μ_drift rises) unless the belief layer reorganises first. CASCADE provides the upstream metric; MICROORCIM provides the downstream metric.

**Formal claim.** Under stated assumptions about the agent's belief-to-behaviour mapping (assumed faithful), there exists a coupling such that `dμ_drift/dt ≥ f(Π − Π_th)` whenever Π exceeds the reorganisation threshold and CASCADE update is suppressed. That is, when the belief layer fails to reorganise under evidence pressure, the behaviour layer drifts at a rate bounded below by an increasing function of the unresolved pressure. **`[SCAFFOLD]`** — the coupling function `f` is not yet specified; the faithfulness assumption is itself contestable.

**Falsifiability.** Construct an agent with high Π (large evidence-belief gap) and stable μ_drift (no behavioural drift) over a sustained interval. If such an agent is producible without architectural intervention, the synthesis is wrong; the metrics measure independent quantities.

**Why this is in C-1.1 and not C-1.0.** The bridge requires both CASCADE and MICROORCIM to be stable in their own right. They are. Stating the bridge during C-1.0 would have entangled their development; stating it now adds load-bearing connective tissue without destabilising either.

---

## Synthesis II — TRIAD Convergence Underwrites LAMAGUE Composition

**The bridge.** TRIAD provides a Banach fixed-point convergence guarantee for an anchor-observe-correct cycle in the formal model. LAMAGUE's Tier 0 primitives are TRIAD operators — that is, every Tier 1 LAMAGUE expression decomposes into a sequence of TRIAD `Ao` (anchor-observe) and `Co` (correct) applications. NOVEL_CONTRIBUTIONS L46 states this; the implication is that LAMAGUE inherits TRIAD's convergence guarantee at the grammar level.

**Why this matters.** Most ethical-grammar systems (deontic logic, rule-based AI) compose rules without composition guarantees: chained rules can produce non-converging or non-terminating evaluation. LAMAGUE inherits convergence from its Tier 0 primitives. A LAMAGUE Tier 1 or Tier 2 expression, evaluated under iterative interpretation, is guaranteed to converge to a fixed point under the same step-size constraint that bounds TRIAD (`α + β ≤ 1 − γ·‖DΨ_op‖`). The category-theoretic structure (Theorems L1, L2 — associativity, identity) ensures that this convergence is preserved under composition.

**Formal claim.** For any LAMAGUE expression `E` decomposable into TRIAD primitives, iterative evaluation of `E` converges to a fixed point under the TRIAD step-size constraint. **`[ACTIVE]` for the formal model** — proof inherits from TRIAD's Banach proof and LAMAGUE's Tier 0 grounding (NOVEL_CONTRIBUTIONS L46). **`[SCAFFOLD]` for biological/cognitive application** — the contraction-mapping conditions on real cognitive operators are not verified.

**Falsifiability.** Produce a Tier 0–1 LAMAGUE expression that does not converge under TRIAD iteration (NOVEL_CONTRIBUTIONS L46 falsifiability column). Such an expression would either show a flaw in the Tier 0 grounding claim or reveal a non-contraction case the TRIAD proof does not handle.

**Why this is in C-1.1.** The convergence inheritance is implicit in the Tier 0 grounding; making it explicit gives reviewers a single named property to challenge rather than a chain of implications to reconstruct.

---

## Synthesis III — AURA Inspectability (I₂) Requires the Evidence Ladder Format

**The bridge.** AURA's Invariant I₂ (Inspectability) requires every consequential claim to be auditable in plain language. `28_DEFENSE/EVIDENCE_LADDER.md` defines the audit format used across the corpus to satisfy this requirement: status tag, evidence basis, falsifiability condition, replication path. The two are designed-together: I₂ is the constitutional requirement; the evidence ladder is the operational format that satisfies it. Most discussions of AURA do not name the evidence ladder; most discussions of the evidence ladder do not name I₂.

**Why this matters.** Without the evidence ladder, I₂ is unenforceable — a reviewer cannot verify that a claim satisfies I₂ if there is no standard format for what an I₂-compliant audit looks like. Without I₂ as the constitutional driver, the evidence ladder is a documentation convention without governance weight. Together they form a closed loop: I₂ requires the audit; the ladder defines its format; LIVING_CODEX_PROTOCOL's update gate requires the ladder for any claim entering the canonical body.

**Formal claim.** A claim satisfies AURA Invariant I₂ if and only if it appears in `28_DEFENSE/CLAIMS.json` with a status tag, evidence basis, falsifiability condition, and replication path matching the evidence ladder schema. Any claim missing one of these elements is, by construction, I₂-non-compliant. **`[ACTIVE]`** — both schemas are computable; the if-and-only-if is verifiable by inspection.

**Falsifiability.** Identify a claim in the canonical body that is widely cited as I₂-compliant but fails the four-element evidence ladder check; or identify a claim satisfying the four-element check that an experienced reviewer would not consider auditable. Either falsifies the bi-conditional.

**Why this is in C-1.1.** The closure of the loop (constitutional requirement → operational format → governance gate) was assumed across documents but never stated in one place. A reviewer evaluating I₂ now has a single named test.

---

## How These Syntheses Will Be Tested

The three syntheses make distinct empirical and formal commitments:

| Synthesis | Test type | Where executed |
|---|---|---|
| I — Π ↔ μ_drift coupling | Empirical (E-1.0 program, Study 4: AURA→behaviour correlation extended to CASCADE→MICROORCIM coupling) | Pending E-1.0 design |
| II — TRIAD ↔ LAMAGUE convergence | Formal (proof of convergence inheritance under stated decomposition) + empirical (run-time convergence on Tier 0–1 expressions) | Formal half implementable now; empirical half pending implementation |
| III — AURA I₂ ↔ Evidence Ladder | Schema-check (compute the four-element criterion across 28_DEFENSE/CLAIMS.json) | Implementable now; CI step proposed |

A future ledger update will track each synthesis through promotion or downgrade.

---

---

## Synthesis IV — CASCADE Governance Composite ↔ Tianxia Flourishing-Coherence Term

**The bridge.** CASCADE's multi-agent master equation (k1–k4 Westphalian terms) evaluates each agent's knowledge-state dynamics against its own integrity and energy state. The Tianxia (天下) operator from the TIANXIA Module (32_TIANXIA) extends this with a fifth term: k5 × grad_Psi_i(Phi_T), where Phi_T = Σ_{i≠j} C_ij is the network's net flourishing-coherence potential. The bridge is that CASCADE's governance composite is a *necessary but insufficient* condition for alignment under the Tianxia operator: an agent can satisfy all four Westphalian terms (zero violations, optimal energy, adequate truth-pressure response) while the network exhibits net negative coupling (Phi_T < 0). The Tianxia term adds the missing relational condition.

**Why this matters.** Westphalian CASCADE evaluates governance adequacy agent-by-agent. Tianxia evaluates it network-wide. A deployment that passes Westphalian CASCADE can still be an extractive equilibrium from which Tianxia dynamics would move the system. The synthesis states: Westphalian compliance is a floor, not a ceiling. The ceiling is Phi_T > 0 and stable. Without Synthesis IV, a reviewer of CASCADE's governance application would have no formal path from per-agent scores to network-level alignment. With it, the path is: per-agent scores (CASCADE k1–k4) + network coupling (Tianxia k5) = full governance composite.

**Formal claim.** There exist multi-agent configurations that satisfy CASCADE's per-agent equilibrium conditions for all agents (dPsi_i/dt = 0 under k1–k4) and simultaneously have Phi_T < 0 (net extractive coupling). Adding k5 > k5_critical destabilises those configurations and drives the network toward equilibria with Phi_T > Phi_T_Westphalian. **`[SCAFFOLD]`** — verified in simulation (`12_IMPLEMENTATIONS/core/tianxia_governance.py`, Proposition 1); k5_critical is domain-specific and unfit; E-1-F is the promotion path.

**Falsifiability.** Show that all CASCADE governance equilibria satisfying k1–k4 terms already exhibit Phi_T ≥ 0 (i.e., rule-compliance is sufficient for flourishing-coherence). If true, the Tianxia term is empirically inert and the synthesis collapses. Alternatively: show that k5 > 0 produces no detectable difference in Phi_T at equilibrium across two orders of magnitude of k5 variation — E-1-F's null result trigger.

**Why added in 2026-05-02.** Synthesis I–III addressed intra-corpus connections (CASCADE↔MICROORCIM, TRIAD↔LAMAGUE, AURA↔EVIDENCE_LADDER). Synthesis IV addresses the first cross-module connection to the TIANXIA civilisational layer, which was not present in C-1.0. The bridge is load-bearing: without it, CASCADE's governance application is silent on network-level alignment, and the TIANXIA Module has no formal anchor in the canonical body.

**Cross-references:**
- CASCADE extension: `01_CASCADE_L4/CASCADE_COMPLETE.md` §Tianxia Extension
- Operator specification: `32_TIANXIA/TIANXIA_GOVERNANCE_DYNAMICS.md` (T-1)
- Implementation: `12_IMPLEMENTATIONS/core/tianxia_governance.py`
- Empirical handle: `31_EMPIRICAL/E1F_HEXIE_PREREGISTRATION.md` Phase 4

| Synthesis | Test type | Where executed |
|---|---|---|
| IV — CASCADE governance ↔ Tianxia Phi_T | Simulation (Proposition 1 confirmed) + empirical (E-1-F Phase 4) | Simulation: done; E-1-F: pending |

---

---

## Synthesis V — Wang Dao Legitimacy ↔ AURA Constitutional Compliance at the Governance Layer

**The bridge.** The Wang Dao / Ba Dao classifier (→ `32_TIANXIA/WANG_DAO_OPERATOR.md`, `32_TIANXIA/implementations/wang_dao.py`) classifies governance trajectories as Wang (governance through virtue and genuine popular alignment), Ba (governance through coercive compliance), or Indeterminate. The AURA runtime compliance architecture (→ `09_AURA/`) provides Boolean checks on individual AI outputs. The bridge: Wang Dao legitimacy is the *governance-scale analogue* of AURA compliance at the system level. A single AI output can be AURA-compliant (all seven invariants satisfied) while the governance system within which it is deployed is Ba Dao aligned (coercive compliance, low voice coverage, extractive force structure). The synthesis states: AURA compliance is necessary but not sufficient for aligned AI deployment; Wang Dao classification of the deployment governance context is the additional requirement.

**Why this matters.** AURA provides a per-output compliance check. The TIANXIA AI deployment protocol (→ `32_TIANXIA/AI_DEPLOYMENT_CRITERIA.md`) extends this to a per-context governance assessment. Without Synthesis V, there is no formal bridge between the per-output compliance layer (AURA) and the governance-context legitimacy layer (Wang Dao). With it: AURA = per-output constitutional compliance; Wang Dao = governance-context legitimacy compliance. Both are required for full deployment alignment.

**Formal claim.** There exist AI deployment configurations where:
1. All generated outputs satisfy AURA(o) = 1 (all seven invariants pass)
2. The governance context has WD = Ba (force_restraint low, minxin low, R(s) < θ_r)

In such configurations, the AI system is AURA-compliant but deployed in a context that is Ba Dao. The system's outputs are constitutionally correct; the deployment governance is not. AURA compliance without Wang Dao governance alignment is *incomplete alignment*.

Conversely: a governance context with WD = Wang and R(s) ≥ θ_r where the AI system generates AURA(o) = 0 outputs is a system that fails at the output layer despite its governance legitimacy. Both layers are independently load-bearing.

**`[SCAFFOLD]`** — verified structurally; no empirical test of the independence claim yet. E-1-G Phase 2 (multi-operator composite validity) includes a test of whether governance-context classification independently predicts alignment quality above and beyond per-output AURA scores.

**Falsifiability.** Show that Wang Dao governance context classification adds no predictive power over per-output AURA scores in predicting long-run deployment alignment quality (E-1-G H5: C(s) outperforms AURA_score_alone across governance types). Null result on H5 would falsify the governance-context independence claim.

**The three-layer alignment stack.** With Synthesis V, the full alignment architecture is:
```
Layer 0: AURA per-output compliance     — each individual output is constitutionally checked
Layer 1: CASCADE coherence dynamics     — belief-state evolution toward coherence
Layer 2: TIANXIA governance context     — Wang Dao classification of deployment arrangement
         ├── Ren Zheng R(s) ≥ θ_r      — welfare floor and voice coverage present
         ├── Five-Fold H₅ ≥ 0.65       — multi-dimensional harmony present
         ├── Wuwei ε ≥ 0.60            — non-coercive deployment operation
         ├── Datong Π_D^{ext} ≥ 0      — positive distributional trajectory
         └── Wang Dao WD = Wang         — genuine legitimacy, not compliance maintenance
```

Full alignment requires all three layers simultaneously. Current framework status: Layer 0 ACTIVE (AURA implemented and tested); Layer 1 SCAFFOLD (CASCADE implemented, k₁–k₄ pending E-1-H); Layer 2 SCAFFOLD (TIANXIA operators implemented, thresholds pending E-1-H/E-1-G).

**Why added 2026-05-03.** Syntheses I–IV addressed intra-corpus and single-module connections. Synthesis V addresses the bridge between AURA's runtime compliance architecture and TIANXIA's governance-context legitimacy architecture — the two most practically significant framework components for real AI deployment. Without this bridge, a practitioner using AURA for output compliance has no formal path to governance-context assessment. With it, the path is explicit: check each output (AURA), assess the governance dynamics (CASCADE), assess the deployment context (TIANXIA five-gate protocol).

**Cross-references:**
- AURA invariants: `09_AURA/aura_text_checker.py`
- Wang Dao classifier: `32_TIANXIA/implementations/wang_dao.py`
- Ren Zheng gate: `32_TIANXIA/implementations/ren_zheng.py`
- Five-gate protocol: `32_TIANXIA/AI_DEPLOYMENT_CRITERIA.md`
- Composite benchmark: `32_TIANXIA/implementations/civilisational_governance_benchmark.py`
- Empirical handle: `31_EMPIRICAL/E1G_MULTI_OPERATOR_PREREGISTRATION.md` (H5)

| Synthesis | Test type | Where executed |
|---|---|---|
| V — AURA per-output ↔ Wang Dao governance-context | Structural (verified) + empirical (E-1-G H5) | Structural: done; E-1-G: pending |

---

*This document is part of the Lycheetah Framework C-1.1 Reforge (2026-04-28). It defends C-1.0 (canonical body, 2026-04-25) by stating structural connections that were implicit in the corpus and load-bearing in the architecture. Synthesis IV added 2026-05-02 (Tianxia v0.2 governance integration). Synthesis V added 2026-05-03 (Wang Dao bridge — AURA ↔ TIANXIA governance-context alignment).*
