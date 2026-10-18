# Implementations

Python engines, applications and research experiments for the Lycheetah Framework.

**Start with the [core engine guide](core/README.md):** all 29 modules explained
in plain language, grouped by the job they do, with their main Python APIs and
links to the installed runtime tools.

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

systems/                    — Full integrated systems built on core.
  aura_sovereign_codex.py   — Complete AURA + CASCADE + LAMAGUE unified system
  cascade_reality_bridge.py — Self-correcting reality verification layer
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
