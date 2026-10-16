# Changelog — v0.8

- Added `authority_boundary_lab_v0_8/tool_catalog.py` to derive mutation classification, scopes, fixed dispatcher ID/version and argument validation from a trusted registry rather than model-visible proposal fields.
- Bound the declared active policy to the exact tool-catalog digest; catalog drift requires a trusted policy update before issuing approval.
- Added 17 unit/integration tests, including a real local end-to-end path through the existing v0.7 separate-process fake host/provider, plus a post-approval tampering test.
- Added `SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.8.md`, which distinguishes the source-level concern from an actual dispatch vulnerability and documents all unverified trust assumptions.
- The v0.7 26-case crash/recovery suite and the legacy 65-case suites remain retained as separate independently passing runs; see root `NEXT_EXPERIMENT.md` for the combined-run limitation.
- No files have been committed to the Lycheetah GitHub repository. No live model or external provider was exercised.
