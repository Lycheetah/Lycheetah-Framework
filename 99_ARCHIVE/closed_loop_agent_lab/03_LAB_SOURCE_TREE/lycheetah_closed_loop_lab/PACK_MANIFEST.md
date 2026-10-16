# Pack manifest — v0.9

- Research pack: Lycheetah Closed-Loop Agent Lab v0.9
- Status: R0 local prototype; source audit read-only
- v0.1-v0.6 retained suite: 65 tests passed separately (`python run_all_tests.py`, prior recorded run)
- v0.7 crash/recovery suite: 26 tests passed separately (`python run_v0_7_tests.py`, prior recorded run)
- v0.8 original catalog-stamping suite: 17 tests passed separately (`python run_v0_8_tests.py`, prior recorded run)
- v0.9 catalog/issuance suite: 21 tests passed (`authority_boundary_lab_v0_9/test_tool_catalog.py`)
- v0.9 separate-process crash/recovery suite: 28 tests passed (`authority_boundary_lab_v0_9/test_crash_recovery.py`)
- v0.9 runner: `python -S run_v0_9_tests.py`; 49 tests passed across two independent interpreter processes. Do not count the previous suites as part of this single run.
- Local v0.8 regression reproducer: `authority_boundary_lab_v0_9/reproduce_v0_8_catalog_bypass.py`; it shows the v0.7 *research harness* accepts an invalid handwritten action, and the v0.9 candidate rejects that schema. Fake provider only.
- Primary new implementation: `authority_boundary_lab_v0_9/tool_catalog.py`, `host_process.py`, `provider_process.py`
- Source audit: `authority_boundary_lab_v0_9/SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.9.md`

## Claims intentionally not made

No live model evaluation, real MCP host dispatch, authenticated reviewer, external provider, production integration, hardened sandbox, independent security review, safety superiority or production reliability claim. The existing Guard MCP code issues receipts and relies on the host to enforce decisions. v0.9 integrates catalog checks into a *synthetic reference host/provider*, not into the public repository.
