# R3 wire-schema audit v1.3

Purpose: test whether typed wire records are strictly validated before normalization.

Start here:
- `WIRE_SCHEMA_AUDIT_v1.3.md` — finding and threat boundary.
- `VERIFICATION_RESULTS_v1.3.md` — passed and unrun checks.
- `PATCH_VALIDATION_LIMITS_v1.3.md` — explicit patch application caveat.
- `strict_assurance_wire_types_v1_3.patch` — proposed source patch, not upstream-applied.
- `test_assurance_wire_types.py` — proposed upstream regression tests; compile-checked only here.
- `source_equivalent_wire_fixture.py` and `test_wire_fixture.py` — runnable low-level fixture.
- `composite_receipt_fixture.py`, `test_composite_receipt_fixture.py`, `run_composite_experiment.py` — receipt-shaped digest normalization probe, five controlled mutations.
- `wire_type_results_v1_3.json` and `composite_receipt_results_v1_3.json` — machine-readable fixture results.
- `preflight_wire_patch.py` — clean-branch, expected-blob and full-checkout apply preflight.
- `check_patch_context.py` — passed synthetic context reconstruction only; not an authoritative real-checkout apply check.

Run the local fixture from this directory:

```bash
python -m unittest -v test_wire_fixture.py
python run_wire_experiment.py
```

The local tests do not import or validate a full upstream checkout.
