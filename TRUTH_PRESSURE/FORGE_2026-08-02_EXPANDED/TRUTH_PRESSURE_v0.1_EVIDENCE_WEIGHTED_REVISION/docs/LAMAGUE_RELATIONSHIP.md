# Relationship to LAMAGUE

Truth Pressure is not part of the LAMAGUE Core ontology.

LAMAGUE Core supplies typed symbolic expressions, invariants, transformation structure, semantic hashes and lossless macros.

Truth Pressure is an epistemic metric adapter that may annotate a claim.

Proposed adapter-level form:

```lamague
claim K_new {
    evidence_quality = 0.91;
    source_independence = 0.82;
    reproducibility = 0.88;
    provenance_completeness = 0.96;
    load_bearing_centrality = 0.90;
    scope_of_consequence = 0.85;
    contradiction_strength = 0.92;
    uncertainty = 0.18;
    source_count = 6;
}

pressure K_new against K_found;
```

A future adapter may compile this syntax into the JSON packet used by v0.1. The core symbol `Π` can reference the result without redefining the metric.
