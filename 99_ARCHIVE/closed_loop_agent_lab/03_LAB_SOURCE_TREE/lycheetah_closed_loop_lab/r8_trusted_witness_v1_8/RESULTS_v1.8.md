# Verification Results v1.8

- `python -m unittest -v test_trusted_witness.py`: **16 test methods passed**.
- The test named `test_concurrent_finalize_allows_exactly_one_consumer` exercised 25 independent two-thread finalization races; exactly one consumption succeeded in each pair.
- The test named `test_documented_external_provider_toctou_remains_open` intentionally demonstrates a remaining cross-system race. It passes because the observed prototype behavior matches the documented limitation; it is not evidence that the race is safe.
- `source_equivalent_baseline_results.json` reproduces the v1.7 acceptance-logic mirror, where a forged/rehashed witness is accepted under the modeled current semantics. This is not full upstream execution.
- Python source parses and runs under the local Python environment; archive integrity is separately checked when packed.

## Not run

- The full Lycheetah-Framework checkout/package tests.
- Actual `FinalityGate` integration.
- A production database or multiple independent hosts.
- Real CI/evidence provider, a remote effect provider, process-kill crash tests, or fault injection against an actual action broker.
- Security review of key management, deployment topology, or operational access controls.

## Source anchor

The source-equivalent baseline refers to upstream revision `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`, `lycheetah/assurance/finality.py` blob `dd97733d45c2261863d24a2a00800baf59fc8bac`.
