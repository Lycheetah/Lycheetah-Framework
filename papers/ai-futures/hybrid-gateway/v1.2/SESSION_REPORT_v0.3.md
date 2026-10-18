# Lycheetah Hybrid Gateway — session report v0.3

**Date:** 2026-10-18. **Experiment state:** local execution + fixture-model and local HTTP testing. No neural model output was collected and no GitHub branch was created.

## What changed

- Added `neural.py`: actual request transport for compatible chat completion endpoints, strict model-response JSON parsing, field allowlists and size limits; extracts only source/tenant/subject/predicate/scope-bound candidates.
- Added `pipeline.py`: staging on an immutable pre-registered document and conservative commit path requiring domain validator plus caller-supplied review. Staging is inert, no side effects.
- Added `cascade_bridge.py`: adapter-shaped, read-only CASCADE diagnostic integration with explicit evidence parameters; fixture engine used for testing, canonical engine integration not exercised.
- Added operator-pinned effective intervals. Provider-suggested conflicting dates are rejected.
- Added local-model demo script, 12 fresh test methods and a new Failure Museum entry for a caught substring bug.

## Reproducible local checks

- `python -m unittest discover -s tests -q` → 54 tests, all passing.
- `python demo.py` → old v0.2 bitemporal workflow still runs and verifies event chain.
- `python run_eval.py` → B0 8/22, B1 13/22, H1 22/22 on synthetic policy cases, **unchanged from v0.2**.
- Real-loopback transport test: a Python HTTP fixture server received POST `/v1/chat/completions`, returned JSON, and the adapter extracted a bounded candidate. **This does not count as live-model inference**.
- New negative control: before fix, proposed value `1` incorrectly anchored to `14`; after fix whole-value lexical match rejects it. The semantic-misbinding failure remains preserved.

## What is not supported

- No measured accuracy for OpenAI/Ollama/other neural inference providers. No actual LLM or CASCADE implementation was executed in this cycle.
- No end-to-end security, authenticated operator identity, external source retrieval or verification, production-grade bitemporal DB, sandboxed effect execution, trained model, neural weight editing, or real-world performance claims.
- No performance improvement claim over VersionRAG; the prior baselines are weaker by construction.

## Research decision

Keep knowledge authority external to models; let the model propose **evidence-bound candidates**, let a human/verified process admit them, and let CASCADE explore diagnostic reorganization without mutating the primary record. Test real neural extraction accuracy independently before allocating resources to neural weight editing.
