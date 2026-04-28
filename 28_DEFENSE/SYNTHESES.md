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

*This document is part of the Lycheetah Framework C-1.1 Reforge (2026-04-28). It defends C-1.0 (canonical body, 2026-04-25) by stating three structural connections that were implicit in the corpus and load-bearing in the architecture.*
