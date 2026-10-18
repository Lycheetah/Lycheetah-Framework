# SXP-L × LAMAGUE v1.9 — Natural Reference Forge

v1.9 gives conversational clarification requests two provisional **spoken viewpoint markers** and a fail-closed expansion into v1.8 explicit-name propositions. It is a **research prototype**, not a human-language fluency claim. **`mi liva ti` remains unchanged.**

## Try it

1. Open `NATURAL_REFERENCE_LAB_v1.9.html` offline and toggle `soraviko` versus `tumerako`.
2. With Python 3.10+ and no third-party runtime dependencies:

```bash
PYTHONPATH=runtime:. python reference19.py examples/contrasting_viewpoints.sxp19 --out out19
PYTHONPATH=runtime:. python -m unittest -v test_reference19 test_repair18 runtime.test_continuity13 runtime.test_perspective14
PYTHONPATH=runtime:. python benchmark19.py
```

The Python tool exports seven synchronized forms, including the native source, expanded v1.8 representation, inherited v1.4 transcript, and semantic sidecars. Keep the native source and sidecars. The browser is an illustrative subset, not the Python validator.

## Inside this release

- `reference19.py` — bounded source parser, viewpoint expander, history-preserving bundle writer/validator.
- `oracle19.py` — separate limited lexical reader, no imports from the main parser.
- `test_reference19.py` — new unit and generative checks.
- `examples/` — two viewpoints and the fully named inherited equivalent.
- `NATURAL_REFERENCE_LAB_v1.9.html` — self-contained interactive teaching lab.
- `SPEC_v1.9.md`, `EVIDENCE_REPORT_v1.9.md`, `ARGON_AUDIT_BRIEF_v1.9.md` — research record and adversarial next steps.
- `history/RELEASE_v1.8_ORIGINAL.zip` — byte-identical original v1.8 release, itself retaining older research.

The new grammar refuses to bind pronouns inside unsupported nested clauses or quotations. Nothing authenticates speakers, verifies what they believe, grants permission, or executes a task.
