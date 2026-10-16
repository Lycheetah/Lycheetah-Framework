# R2 Parser Audit — v1.2

This directory tightens the prior strict parser patch to include `status_basis` and the direct `TextRule(...)` construction path.

Run the local source-equivalent experiment:

```bash
python -m unittest -v test_strict_candidate
python run_expanded_comparison.py
```

The upstream-ready test file `test_assurance_policy_text_rule_types_v1_2.py` requires an actual checkout after the patch is applied; it imports the public `lycheetah.assurance` package. Do not interpret the fixture's results as a full package test run.

See `STRICT_PARSER_REVIEW_v1.2.md` for source identity, limitations and promotion gates.
