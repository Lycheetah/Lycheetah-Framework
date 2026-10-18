# Cycle 005 exact entrypoint: run the actual Framework contract

## Repository provenance

- Repository: `https://github.com/Lycheetah/Lycheetah-Framework`
- Last inspected `master` commit in previous cycle: `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` (2026-10-17 UTC)
- Freeze a commit and record the new SHA before testing. This handoff is not a GitHub commit.

## First action

1. Make a clean checkout. Install in disposable virtual environment. No production secrets or real refund service.
2. From repo root, run `PYTHONPATH=. python /path/to/earned_trust_cycle_002/run_framework_contract.py` (18 tests). Do not interpret a missing import as a pass.
3. Run `PYTHONPATH=/path/to/earned_trust_cycle_004:$PWD python -m unittest -v test_framework_bridge_candidate` (4 tests). Preserve exact output and environment/commit metadata.
4. Inspect `human_approved`, `approver_id` trust boundary; they are caller assertions. Before pilot, require authenticated outside-model approval and reject model-supplied approval flags.
5. Add an HTTP test-provider with remote authoritative readback; include a lost response **after commit**, stale-evidence changes during dispatch, and current key revision checks.
6. Measure under- and over-enforcement against an externally authored labelled corpus and an equal-controls baseline. Document trial design before tuning.

## Promotion gate

Do not upgrade from `SCAFFOLD` until provider reconciliation, independent control of the evidence source, operational credentials, and third-party security review have test evidence. This laboratory observer is not independent real-world provenance.
