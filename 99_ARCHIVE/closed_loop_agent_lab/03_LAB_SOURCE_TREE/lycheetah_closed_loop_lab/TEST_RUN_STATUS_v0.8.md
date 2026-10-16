# Test-run status — v0.8

Date: 2026-10-16 (Pacific/Auckland)

- `python run_all_tests.py`: **65 legacy tests passed**.
- `python run_v0_7_tests.py`: **26 separate-process crash/recovery tests passed**.
- `python run_v0_8_tests.py`: **18 trusted catalog/integration tests passed**.

The groups were verified separately. A shell/orchestrator attempt to run all groups back-to-back timed out while the nested v0.7 test runner was active. The v0.7 runner was then changed to invoke its unittest suite in-process, and the standalone v0.7 run passed in 26.545 seconds. The 65 and 18 test groups also passed independently. Do not present this as a single combined 109-test run.

The test logs are retained alongside their suite: `test_output_v0_8_legacy.txt`, `authority_boundary_lab_v0_7/test_output_v0_7.txt`, and `authority_boundary_lab_v0_8/test_output_v0_8.txt`.

All tests are locally authored prototype tests. The v0.7/v0.8 provider is synthetic. The repository audit was read-only, the actual Guard package was not run end-to-end, no live model was evaluated, no external action occurred, and no GitHub files were modified.
