# Pack manifest — v2.7

## Focused R17 folder

- `stripe_webhook_inbox.py` — authenticated inbox plus transactional reconciliation queue.
- `test_transactional_reconciliation_queue.py` — 29 tests covering core queue lifecycle/migration/scope/race behavior.
- `test_stripe_webhook_inbox.py` — R16 regression suite, with a queue atomicity assertion added to concurrent duplicate ingestion.
- `test_webhook_http_receiver.py` — R16 loopback tests plus one queue-write-failure `503` case.
- `webhook_http_receiver.py` — loopback-only test receiver.
- `run_webhook_tests_v2_7.py`, `run_complete_tests_v2_7.py`, `run_complete_tests_v2_7.sh` — test runners.
- `focused_tests_v2.7.log`, `smoke_output_v2.7.log`, `python_compile_v2.7.log`, `combined_tests_v2.7.log` — focused and cumulative verification outputs.
- `combined_group_1_r10.log` through `combined_group_5_r17.log`, `combined_tests_v2.7.log` — separately-run retained suite logs and a record of the interrupted cumulative wrapper.
- `README_v2.7.md`, `TRANSACTIONAL_QUEUE_DESIGN_v2.7.md`, `RESULTS_v2.7.md`, `PROVIDER_CONTRACT_SOURCES_v2.7.md`, `SOURCE_PIN_v2.7.json`, `CHANGELOG_v2.7.md` — design, verification, source pins and operation boundary.

## Verification counts

Individually completed suites: R10=49, R11=29, R12=39, R15=85, R16+R17=84; sum=286 methods. The final suite includes 29 queue-specific R17 tests plus one new HTTP receiver regression, alongside retained R16 tests. The revised watchdog-bounded cumulative run passed all five groups in one invocation; earlier unbounded attempts are retained as diagnostic evidence.

No hosted Stripe calls, real refunds or upstream edits occurred.
