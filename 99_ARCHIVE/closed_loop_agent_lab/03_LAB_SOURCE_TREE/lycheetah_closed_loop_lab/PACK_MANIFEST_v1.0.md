# Pack Manifest v1.0

Current iteration: `r2_policy_parser_audit/`.

Key files:
- `task_contract.md`: contract frozen before evaluation.
- `baseline_fixture.py`: source-equivalent baseline for the coercion behavior.
- `policy_parser_candidate.py`: strict candidate implementation.
- `test_policy_parser.py`: seven isolated tests including a 20-case malformed-type grid.
- `run_comparison.py`, `comparison_results.json`, `comparison_results.csv`: reproducible before/after comparison.
- `proposed_patches/strict_text_rule_parser.patch`: suggested upstream change.
- `test_assurance_policy_types_proposed.py`: pytest tests intended for the actual project test suite.
- `R2_REPORT.md`: findings and limits.

Prior v0.1-v0.9 artifacts remain included for research lineage. Separate historical suite counts are preserved in their corresponding reports; do not sum them as if all versions formed one unified test run.
