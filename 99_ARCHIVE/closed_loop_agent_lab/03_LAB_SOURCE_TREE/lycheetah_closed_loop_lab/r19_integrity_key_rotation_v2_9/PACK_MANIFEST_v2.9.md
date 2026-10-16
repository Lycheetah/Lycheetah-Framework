# Pack Manifest v2.9

## Core implementation
- `integrity_key_rotation.py` — atomic offline key rotation and verification CLI.
- `stripe_webhook_inbox.py` — copied v2.8 inbox/queue source used to match the exact row MAC format.
- `operation_ledger.py` — copied v2.8 operation ledger source used to match the exact row MAC format.

## Tests and evidence
- `test_integrity_key_rotation.py` — 20 focused tests.
- `run_key_rotation_tests_v2_9.sh` — reliable focused runner for the new migration utility.
- `focused_tests_v2.9.log` — latest focused test output.
- `group_r10.log`, `group_r11.log`, `group_r12.log`, `group_r15.log`, `group_r18.log` — retained suites each passed in a separate invocation.
- `ISOLATED_REGRESSION_SUMMARY_v2.9.json` — test counts and the precise invocation boundary.
- `python_compile_v2.9.log` — syntax compile output.
- `archive_verification_v2.9.json` and checksum files are delivered in `/mnt/data`.

## Operations and limitations
- `ROTATION_RUNBOOK_v2.9.md`
- `DESIGN_AND_THREAT_MODEL_v2.9.md`
- `RESULTS_v2.9.md`
- `SOURCE_PIN_v2.9.json`
- `CHANGELOG_v2.9.md`

Keys and endpoint secrets are synthetic in tests; none are written into the pack.
