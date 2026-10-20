# Implementations

Python engines, applications and research experiments for the Lycheetah Framework.

**Guide refreshed:** 21 October 2026. The installable wrapper is owned by
[`lycheetah/`](../lycheetah/); this directory owns the foundational engine sources.
[Current synthesis](../13_SYNTHESIS_REPORTS/CURRENT_FRAMEWORK_SYNTHESIS.md) ·
[Complete map](../00_Sovereign_Index.md) · [Capability/evidence guide](../33_APPLICATIONS/README.md).

## Choose the right source

| Work | Maintained entry | Boundary |
|---|---|---|
| Foundational engine APIs | [core guide](core/README.md) | Models and implementations vary in maturity |
| Bounded policy decisions and receipts | [Assurance Runtime](../34_ASSURANCE_RUNTIME/README.md) | Not a certificate of agent safety |
| Permission, action and recovery experiments | [agent-safety packets](../papers/agent-safety/README.md) | Versioned research snapshots, not replacements for every engine |
| Knowledge revision continuation | [Hybrid Gateway](../papers/ai-futures/hybrid-gateway/README.md) | Separate research version and conventional baseline |
| Handover/record preservation | [own-task instrument](../examples/meaning_handover/README.md) | Exact fields and codec behaviour; human benefit remains unmeasured |


**Start with the [core engine guide](core/README.md):** all 29 modules explained
in plain language, grouped by the job they do, with their main Python APIs and
links to the installed runtime tools.

## Improvements checked on 21 October

The deeper [Framework review](../28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md)
now includes numerical boundary fixes in the maintained engines:

- TRIAD requires both a small update and a small gradient before reporting its
  numerical stop condition. Its recorded coherence belongs to the recorded state.
  Stationarity can still be a minimum; this is not a proof of a unique optimum.
- TRI-AXIAL rejects nonfinite measurements, invalid violation counts, negative
  friction and incomplete vector pairs. Large finite vectors use a scaled cosine
  calculation. These remain caller-supplied metrics with uncalibrated thresholds.
- The existing sheaf/factorial tests were rerun alongside the changes. Their
  numerical contracts do not establish the broader scientific interpretation.

The focused implementation, sheaf and execution-boundary run passed **167 tests**.
This is a targeted run, not a fresh execution of the entire maintained suite.
See the [boundary regressions](../tests/test_implementation_boundaries.py).

## Requirements

From the repository root:

```bash
python3 -m pip install -e .
```

## Structure

```
core/                       — Start here. The foundational engines.
  cascade_engine.py         — CASCADE knowledge reorganization (domain-agnostic)
  lamague_reference.py      — LAMAGUE symbol system and grammar parser

systems/                    — Integration references and experiments.
  aura_sovereign_codex.py   — AURA + CASCADE + LAMAGUE integration reference
  cascade_reality_bridge.py — Experimental model/reality bridge
  unified_field.py          — Unified field implementation across all frameworks
  knowledge_genome.py       — Knowledge genome encoding and evolution

applications/               — Specific applications of the framework.
  mystery_school_cascade.py         — Adaptive learning system
  cascade_curriculum_architect.py   — Curriculum generation engine
  cascade_temporal_oracle.py        — Temporal pattern prediction
  cascade_resonance_engine.py       — HARMONIA resonance implementation

experiments/                — Synthetic domain experiments and comparisons.
  cascade_simulation_experiments.py       — Multi-domain experimental runner
  domain_quantum_physics.py         — Physics domain implementation
  domain_germ_theory.py             — Constructed germ-theory example
```

## Quick Start

```python
from lycheetah.core.cascade_engine import CascadeEngine, KnowledgeBlock

engine = CascadeEngine()
engine.add_block(KnowledgeBlock(
    id="example_claim",
    content="Knowledge reorganizes under truth pressure",
    domain="epistemology",
    paradigm="cascade",
    evidence_strength=0.9,
    explanatory_power=2.1,
    uncertainty=0.1,
))

print(engine.layer_distribution())
```

## Theoretical Basis

Maturity varies by module: this directory contains executable models, reference
scaffolds and synthetic experiments. Formal arguments, assumptions and incomplete
specifications live in the corresponding Framework chapters and
[`11_MATHEMATICAL_FOUNDATIONS/`](../11_MATHEMATICAL_FOUNDATIONS/).
Running a model or passing its authored checks does not independently establish
its broader scientific interpretation. The [core guide](core/README.md) explains
the main boundaries and points to recorded evidence.

*Validated struggle. Not spectacle.*
