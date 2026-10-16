# Lycheetah Closed-Loop Agent Lab v1.8 — Trusted Witness Prototype

## Goal

Turn the v1.7 admission-witness provenance finding into a concrete defensive reference design and challenge it with local regression tests.

**This is a standalone reference prototype, not an upstream patch and not production-certified security software.** Its runtime and receipt are intentionally minimal test adapters. It does not import the complete `Lycheetah-Framework` package.

## Run it

Requires Python 3.11+ and only the standard library:

```bash
python -m unittest -v test_trusted_witness.py
python witness_provenance_probe.py
```

The second file is copied into this pack from the v1.7 source-equivalent probe and must be read with its source-equivalence limitation. The v1.8 test suite exercises the new SQLite-backed reference design.

## What is implemented

- HMAC-SHA256 over a canonicalized witness body.
- A server-configured evidence requirement set; the caller does not choose weaker requirements on the `admit()` call.
- Event hash and policy identity binding.
- Short-lived witness expiry.
- SQLite durable issuance ledger.
- Atomic one-use consumption using `BEGIN IMMEDIATE` and conditional update.
- Revalidation of exact/subject-status evidence as close as possible to consuming the witness.
- Fail-closed checks for malformed witness envelopes and runtime errors.
- Race test: 25 simultaneous two-caller attempts; exactly one consumption succeeds each time.

## Important remaining gap

The evidence provider is not transactionally coupled to the local SQLite ledger. The test `test_documented_external_provider_toctou_remains_open` intentionally demonstrates that a separate provider may change immediately after returning the status snapshot. For strong guarantees, the provider needs a versioned lease, conditional read/consume, or shared transaction protocol. This prototype also does not atomically couple witness consumption to a remote side effect. That requires an effect broker with durable idempotency keys and provider-side idempotency/reconciliation semantics.

## Upstream source checked

Repository: https://github.com/Lycheetah/Lycheetah-Framework
Inspected commit: `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`

- `lycheetah/assurance/finality.py` blob: `dd97733d45c2261863d24a2a00800baf59fc8bac`
- Relevant test: `tests/test_assurance_finality.py`
- Guard integration limitations: `12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md`

No upstream files, branch, or pull request were changed. The GitHub integration rejected branch creation with HTTP 403. No full checkout or upstream CI run was available in this pass.
