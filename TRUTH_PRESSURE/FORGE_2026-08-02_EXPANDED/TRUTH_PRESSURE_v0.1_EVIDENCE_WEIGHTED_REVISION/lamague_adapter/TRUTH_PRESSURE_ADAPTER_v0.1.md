# LAMAGUE Truth Pressure Adapter v0.1

This file specifies the boundary between LAMAGUE Core and Truth Pressure.

```text
LAMAGUE expression
→ claim identifier and semantic hash
→ evidence packet
→ Truth Pressure evaluation
→ Π annotation
→ optional Cascade review request
```

The adapter must never infer evidence scores from a glyph alone. It must preserve source references and state which dimensions were human-rated, model-rated or calculated.
