# Pack Manifest — v2.2

## Latest contents

`r12_stripe_refund_contract_v2_2/`
- `stripe_refund_recovery.py` — offline endpoint-specific recovery logic
- `test_stripe_refund_recovery.py` — 39 regression test methods
- `STRIPE_REFUND_CONTRACT_v2.2.md` — contract + explicit limits
- `SOURCES_v2.2.md` and `provider_facts.json` — official reference log
- `provider_scenarios_v2.2.json` — seven deterministic scenarios
- `run_provider_scenarios.py` — reproducible scenario runner
- `test_output_v2.2.log`, `complete_lab_test_output_v2.2.log`
- `RESULTS_v2.2.md` — verification record

`run_complete_lab_v2_2.py` runs all retained v2.0/v2.1 tests plus v2.2.

## Commands

```bash
cd lycheetah_closed_loop_lab
python -m unittest -v r12_stripe_refund_contract_v2_2.test_stripe_refund_recovery
python r12_stripe_refund_contract_v2_2/run_provider_scenarios.py
python run_complete_lab_v2_2.py
```

## Verification summary

- v2.2 suite: 39 test methods passed.
- Combined v2.0 + v2.1 + v2.2 suite: 117 test methods passed.
- Python compilation passed.
- No external API calls, no production credentials, no real refunds.
- No upstream changes; no full upstream package test/CI claim.
