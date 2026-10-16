# Pack Manifest v3.1

Primary implementation: `remote_anchor_http.py`
Protocol tests: `test_remote_anchor_http.py`
Compatibility regression tests: `test_external_checkpoint.py`
Test runner: `run_v3_1_tests.sh`
Test group launchers: `run_remote_group1.py`, `run_remote_group2.py`, `run_remote_group3.py`
Requirements: `requirements.txt`
Protocol contract: `API_CONTRACT_v3.1.md`
Threat model: `THREAT_MODEL_v3.1.md`
Source and scope: `SOURCES_v3.1.md`
Recorded results: `RESULTS_v3.1.md`
Recorded test logs: `test_logs/`

Counts:
- Existing checkpoint test methods: 33
- Remote HTTP protocol test methods: 41
- Total unique test methods: 74
- Recorded pass results: 74
- Hosted Stripe requests / real refunds: 0
- Upstream source changes: 0
