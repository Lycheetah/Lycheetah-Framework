# Regression execution boundary v3.0

The current v3.0 gate is the focused `run_v3_tests.sh` script. It performs compilation and all 33 external-checkpoint tests in one clean invocation.

The retained R10, R11, R12, R15, R18, and R19 histories are preserved as separate group logs. During this iteration, the combined historical orchestrator reached the end of the R18 `unittest` output (`Ran 121 tests ... OK`) but the Python process did not exit cleanly; this is a process-lifecycle/harness issue and means no fresh aggregate all-groups invocation is claimed. The individual R10/R11/R12/R15 logs from that attempt completed normally; R19 was separately run and passed 20 tests. The prior v2.8 and v2.9 artifacts contain their own recorded passing group logs. Do not interpret summing historic test counts as one monolithic run or as upstream CI.

To investigate the exit hang later, run `run_worker_tests_v2_8.py` under a process-group watchdog and inspect any lingering non-daemon server/worker threads. Do not solve it by forcing `os._exit` in a production test runner, because that would bypass cleanup.
