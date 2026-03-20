# Implementations

Working Python implementations of the Lycheetah Sovereign Framework.

## Requirements

```bash
pip install numpy scipy networkx
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

experiments/                — Real-world domain validation.
  cascade_real_experiments.py       — Multi-domain experimental runner
  domain_quantum_physics.py         — Physics domain implementation
  domain_germ_theory.py             — Biology/medicine domain validation
```

## Quick Start

```python
from core.cascade_engine import CascadeEngine, KnowledgeBlock

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

result = engine.process()
print(result)
```

## Theoretical Basis

Every implementation here has a formal proof in `../11_MATHEMATICAL_FOUNDATIONS/`.
The code is not the primary artifact — the framework is. The code demonstrates
that the mathematics is operationalizable, not just theoretically valid.

*Validated struggle. Not spectacle.*
