# Research pack manifest — v1.4

The full archive preserves prior closed-loop / authority-gate work and adds `r4_schema_parser_parity_v1_4/`.

## New in v1.4

- `SCHEMA_PARSER_PARITY_AUDIT.md`: source observations and limits.
- `receipt.schema.json`: readable semantic reconstruction of the inspected upstream schema.
- `receipt.schema.strict-candidate.json`: candidate control-reference schema and closed finding schema.
- `schema_parser_parity.py`, `run_differential.py`, `test_schema_parser_parity.py`: source-equivalent differential reproduction and unit tests.
- `differential_results.json`: 20-row matrix across current schema, modeled parser, strict parser, and strict schema.
- `SCHEMA_CHANGE_PROPOSAL_v1.4.md`: suggested schema edits and compatibility gates.
- `STRICT_PARSER_PATCH_DELTA_v1.4.md`: changes beyond the v1.3 patch candidate.
- `PROPOSED_UPSTREAM_TESTS_v1.4.py`: test module intended for a clean checkout; not run against upstream here.
- `VERIFICATION_RESULTS_v1.4.md`: passed local commands and explicit unrun checks.

## Evidence labels

- **Source observation:** inspected repository files and blob hashes at the named commit.
- **Source-equivalent result:** local fixture mirrors specific normalization/check expressions; not the upstream package.
- **Proposed:** patch/schema/test changes have not been integrated or run in upstream CI.
- **Not measured:** live model behavior, production impact, and deployment safety.
