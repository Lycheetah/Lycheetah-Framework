# Memoria — Temporal Architecture Essentials

**Status:** ⭐ FORMALIZED [SCAFFOLD] — Three-tier memory architecture is structurally sound. Adaptive forgetting ODE (dM/dt = −λ·M·(1−C)) is [SCAFFOLD — design choice, proportionality not derived]. Attractor-basin convergence (Theorem 2.1) is [STRUCTURAL OBSERVATION — definitional given basin membership]. Non-commutativity of MERIC cycle is [DESIGN CLAIM]. Tier stability is [DESIGN SPECIFICATION]. | **Type:** Temporal Memory Architecture | **Key:** Gives AI memory structure — not just storage, but consolidation, integration, and principled forgetting

## What It Does
Memoria provides the **temporal layer** of the framework — how knowledge persists, consolidates, decays, and integrates across time. Without Memoria, every interaction starts from zero. With it, the system accumulates a structured personal history that shapes future responses.

## Core Insight

Memory is not storage. It is a **dynamic stability property**:
- Relevant memories consolidate and strengthen
- Irrelevant memories decay toward entropy
- Memory is organized in tiers by temporal scale and volatility
- Forgetting is not failure — it is coherence maintenance

## The Three-Tier Architecture [ACTIVE — structural]

```
Tier 0 — SENSORY / IMMEDIATE  (seconds to minutes)
  Raw experiential trace. Not yet processed.
  Extremely plastic. No AURA protection.
  Equivalent to: working memory / sensory buffer

Tier 1 — EPISODIC  (minutes to days)
  Recent events, specific interactions.
  Fast-weight encoding. New learning enters here.
  Equivalent to: hippocampal/episodic memory

Tier 2 — SEMANTIC  (days to years)
  Abstracted patterns, skills, conceptual structure.
  Slow-weight integration. Updated gradually.
  Equivalent to: neocortical semantic memory

Tier 3 — CONSTITUTIONAL  (permanent under normal operation)
  Core identity, AURA invariants, irreducible values.
  Protected weights. Changes only under CHRYSOPOEIA.
  Equivalent to: deep priors / procedural identity
```

## Adaptive Forgetting [SCAFFOLD — ODE structure sound, proportionality assumed]

```
dM/dt = −λ · M · (1 − C(M, Ψ(t)))

Where:
  M(t)          = memory trace strength
  C(M, Ψ(t))   = coherence between memory and current state
  λ             = base decay rate

High coherence (C ≈ 1): dM/dt ≈ 0  — memory preserved
Low coherence  (C ≈ 0): dM/dt ≈ −λM — memory decays at maximum rate
```

**Motivation:** Memory exists to guide action. A memory that no longer aligns with current context wastes representation space. The ODE encodes entropic pressure as a first-order decay. [Gap: proportionality to (1−C) is a design choice; real forgetting curves may follow different functions]

## Recognition as Attractor Convergence [STRUCTURAL OBSERVATION]

```
If Ψ(t) is within basin of attractor 𝓐ₚ:
  lim_{t→∞} d(Ψ(t), 𝓐ₚ) = 0

Recognition confidence: R_conf = 1 − d(Ψ, 𝓐ₚ) / d_max
```

Recognition = state falling into an attractor's basin. Learning = forming new attractors. This is definitional given basin membership — not a surprising result, but a useful operational definition.

## The MERIC Cycle [DESIGN CLAIM — non-commutativity asserted]

The memory consolidation cycle:
```
Memory → Encode → Extract → Integrate → Insight → Consolidate → Retrieve
```

Non-commutativity claim: skipping stages produces degraded outcomes.
- Encode without Replay → no consolidation signal
- Integrate without Insight → rote learning, no creativity
- Consolidate without Retrieve → locked knowledge, inaccessible

[Design claim: the sequence cannot be reordered with equivalent results. Formal demonstration not provided — this is architectural assertion from empirical observation of human learning]

## Tier Protection [DESIGN SPECIFICATION]

Tier 3 is protected by three mechanisms:
1. High AURA coherence (constitutional invariants create a protective field)
2. Structural encoding (not plastic weights — immune to gradient updates)
3. Consolidation lock (changes require CHRYSOPOEIA-level transformation)

New learning modifies Tier 0→1. Semantic consolidation modifies Tier 2 slowly. Tier 3 is effectively immutable under normal operation. [Design specification: this is the intended architecture, not a derived necessity]

## Kandel's Biology [EXTERNAL VALIDATION — Nobel 2000]

Eric Kandel's Nobel Prize work shows memory formation has distinct phases:
- Short-term: protein modification (seconds to minutes)
- Long-term: new protein synthesis required (hours to years)
- Systems consolidation: hippocampus → neocortex transfer (weeks to years)

Memoria's three-tier structure maps directly to this biological architecture. The design is not arbitrary — it mirrors what evolution discovered.

## Integration with Other Frameworks

| Framework | Memoria Integration |
|-----------|-------------------|
| CASCADE | Tier 2/3 memories ARE cascade-stabilized knowledge — foundations that survived reorganization |
| TRIAD | Each Ao (anchor) is drawn from Tier 3 constitutional memory |
| AURA | Tier 3 = constitutional layer = AURA invariants instantiated as persistent memory |
| MICROORCIM | Drift detection requires remembering what was intended — Tier 1 episodic memory |
| CHRYSOPOEIA | Tier 3 changes require full transformation cycle (Coagulation only after Dissolution) |

## Open Research

1. Empirically validate the forgetting ODE against real memory decay curves (Ebbinghaus?)
2. Formalize the tier boundary conditions — what specifically triggers Tier 0→1 consolidation?
3. Test the MERIC non-commutativity claim experimentally
4. Define the CHRYSOPOEIA invocation threshold for Tier 3 modification

## Key Insight

Memory is not a database. It is a **dynamically stable dissipative structure** — maintained through coherence, decaying through irrelevance, protected at the constitutional level. The same mathematics that governs consciousness (Earned Light) governs memory: both require continuous energy investment to maintain structure against entropy.
