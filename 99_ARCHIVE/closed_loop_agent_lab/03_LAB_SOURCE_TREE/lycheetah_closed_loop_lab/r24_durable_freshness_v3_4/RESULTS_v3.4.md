# Results v3.4

## Executed

- `python -m py_compile *.py baseline_v3_2/*.py` — passed.
- `python -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier` — **56 test methods passed** in one local invocation.
- `python reproduce_v3_2_findings.py` — all five frozen v3.2 cases reproduced as accepted by baseline.
- `demo_durable_freshness_v3_4.py` — passed; valid current chain accepted once, then replay denied as `challenge-already-consumed`; no network calls.
- Source checksum check confirms retained `remote_anchor_http.py` has SHA-256 `0a002d054800fbfaed20b100c38f7333c934ff71f7a971aec3631bd49a61afe3`, matching v3.3 pin.

## Interpretation of the 56 test methods

- 37 tests exercise the retained v3.3 quorum protocol.
- 19 tests exercise the v3.4 durable challenge layer.
- One v3.4 test is an intentionally successful negative control: it proves a privileged whole-database rollback restores a pending nonce and allows replay. It passes because the test asserts this known limitation. The other 55 tests check baseline invariants or defensive properties.

## Main outcomes

- Challenge verification and consume is one-use under an eight-thread concurrent race.
- Consumption survives ordinary verifier process restart when the same current ledger and HMAC key are reused.
- Expired challenges, forged/unissued nonces, wrong-database envelopes, changed rosters/fault budgets, incompatible schema and individual ledger tampering are rejected.
- A pre-consumption SQLite snapshot restoration defeats the local one-use property. This is expected and documented; production requires externally administered monotonic consumption state.

## Not claimed

Not upstream CI, not production security certification, and not rollback resistant. No remote anchor or Stripe API calls, no real refunds, no branch/PR, and no upstream source changes.
