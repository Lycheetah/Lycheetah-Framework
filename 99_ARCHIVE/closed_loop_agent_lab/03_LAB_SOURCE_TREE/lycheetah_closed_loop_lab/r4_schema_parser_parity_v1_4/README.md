# R4: Receipt Schema/Parser Parity v1.4

This experiment compares the inspected receipt JSON Schema with source-equivalent behavior mirrored from `AssuranceReceipt.from_dict`, `Finding.from_dict`, and `ControlReference.from_dict` at the inspected master commit. It does not import the full upstream package.

## Run locally

```bash
python run_differential.py
python -m unittest -v test_schema_parser_parity.py
```

Requirements: Python 3.10+ and `jsonschema`. The signing key is fixture-only.

## Main result

Across 20 authored cases, 18 pass the source-equivalent parser, 10 are rejected by the currently inspected schema, and both strict candidates reject all 20. Eight HMAC-sealed wire mutations preserve verification under the modeled current behavior because they normalize to the original canonical body. This is a representation-contract gap, not an HMAC break or production bypass.

Read `SCHEMA_PARSER_PARITY_AUDIT.md`, `SCHEMA_CHANGE_PROPOSAL_v1.4.md`, and `VERIFICATION_RESULTS_v1.4.md` before using this as a patch candidate.
