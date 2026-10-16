# Research pack manifest — v1.3

The archive preserves prior closed-loop / authority-gate experiments and adds `r3_wire_schema_audit_v1_3/`.

## New in v1.3

- `WIRE_SCHEMA_AUDIT_v1.3.md`: source observations, wire-type issue, and bounded impact analysis.
- `strict_assurance_wire_types_v1_3.patch`: proposed strict wire-type patch; not upstream-applied and not verified with the complete source tree.
- `test_assurance_wire_types.py`: proposed upstream regression tests; syntax-compiled only here.
- `source_equivalent_wire_fixture.py` and `test_wire_fixture.py`: runnable source-equivalent coercion fixture (5 test methods).
- `composite_receipt_fixture.py`, `test_composite_receipt_fixture.py`, `run_composite_experiment.py`: complete receipt-shaped digest-normalization probe (2 test methods, 5 controlled mutations).
- `wire_type_results_v1_3.json` and `composite_receipt_results_v1_3.json`: machine-readable results.
- `preflight_wire_patch.py`: clean-branch, source-blob and full-checkout patch-application preflight.
- `check_patch_context.py` and `patch_context_check_v1_3.json`: passing synthetic context reconstruction only; not a real-checkout apply check.
- `VERIFICATION_RESULTS_v1.3.md` and `PATCH_VALIDATION_LIMITS_v1.3.md`: clear distinction between passed fixtures and unrun upstream verification.

## Evidence labels

- **Source observation:** from inspection of the named public GitHub source files and blob hashes.
- **Local fixture result:** runnable source-equivalent fixture only.
- **Proposed:** patch and real-package tests are not integrated upstream.
- **Not measured:** live model-agent behavior, production provider effects, or deployed security impact.
