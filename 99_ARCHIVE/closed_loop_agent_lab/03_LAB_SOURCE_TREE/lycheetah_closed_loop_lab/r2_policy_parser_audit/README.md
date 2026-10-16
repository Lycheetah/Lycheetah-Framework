# R2 Policy Parser Audit

A bounded micro-experiment on strict JSON type validation in the current Lycheetah Framework `TextRule.from_dict` parser.

Run locally:

```bash
python run_comparison.py
python test_policy_parser.py
```

Expected comparison headline:
- 24 malformed-type probes (six JSON value classes across four fields).
- Expanded source-equivalent baseline accepted 21 of 24 malformed-type probes.
- Strict candidate rejected all 24.

The baseline fixture reproduces the coercion behavior seen in the upstream source; it is not the full installed package. The proposed patch was not applied upstream. See `R2_REPORT.md` and `task_contract.md`.
