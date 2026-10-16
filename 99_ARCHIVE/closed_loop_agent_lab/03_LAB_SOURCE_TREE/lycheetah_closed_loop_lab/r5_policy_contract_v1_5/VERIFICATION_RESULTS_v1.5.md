# Verification results — v1.5

## Executed locally

Command, run from this directory:

```bash
python -m unittest -v test_policy_contract_parity.py
```

Result: **5 test methods passed**.

The test matrix also ran independently:

```bash
python policy_contract_parity.py
```

Result: 20 differential cases generated and recorded in `results.json`.

| Measurement | Result |
|---|---:|
| Cases | 20 |
| Current schema accepts | 8 |
| Source-equivalent parser accepts | 7 |
| Current schema/parser agreement | 7/20 |
| Candidate schema accepts | 4 |
| Proposed strict-type parser model accepts | 1 |
| Candidate schema/parser agreement before semantic/number-policy resolution | 17/20 |

The tests assert that malformed text-rule wire types are rejected by the proposed type guard and candidate schema, while parser-specific semantic checks (invalid regex and duplicate rule IDs) remain parser responsibilities.

## Not executed

- No test imported `lycheetah.assurance` from a complete, clean upstream checkout.
- `PROPOSED_UPSTREAM_TESTS_v1.5.py` is a handoff file and was not run against the project package.
- No wheel/sdist build or GitHub Actions run was performed.
- No repository branch, file, issue, or pull request was changed.

## Caution

These are source-equivalent fixture results. They show specific mismatches in inspected conversion and validation rules; they are not a security certification or a measurement of production failure rates.
