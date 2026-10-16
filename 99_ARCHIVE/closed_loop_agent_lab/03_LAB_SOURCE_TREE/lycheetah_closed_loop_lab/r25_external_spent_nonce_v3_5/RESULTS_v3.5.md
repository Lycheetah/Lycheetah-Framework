# Results v3.5 — External Spent-Nonce Registry

## Execution

- `python -m py_compile *.py baseline_v3_2/*.py` — passed.
- `python -m unittest -v test_remote_monotonic_verifier` — **15 test methods passed**.
- `python -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier test_remote_monotonic_verifier` — **71 test methods passed** in one invocation.
- `python reproduce_v3_2_findings.py` — all five frozen v3.2 acceptance findings reproduced.
- `python demo_durable_freshness_v3_4.py` — retained local-only demo passed.
- `python demo_primary_rollback_v3_5.py` — external registry smoke demo passed; primary-only rollback rejected.

## What the test count means

- 37 retained quorum tests from v3.3.
- 19 retained v3.4 challenge lifecycle tests, including the deliberate local-only rollback negative control.
- 15 new remote registry integration tests. A positive regression shows primary-ledger-only rollback is rejected while the registry remains current. One deliberate new negative control shows coordinated rollback of both ledgers permits replay. Across the retained and new suites there are two explicit rollback negative controls (local-only and coordinated rollback).

The tests run against an HTTP service simulator and separate local SQLite files. There are no calls to hosted services.

## Main results

- Valid witness chain/quorum plus matching nonce: accepted, local and remote states consumed.
- Primary database snapshot restored while registry remains current: replay rejected by remote `challenge-already-consumed` result.
- Two database snapshots restored together: the same challenge is accepted again by design, showing why the registry must itself have protected monotonic state and independent restoration controls.
- Remote consume response lost after commit: verification fails closed; a second attempt is rejected as spent.
- Eight concurrent consumers: exactly one accepted result.
- Remote registry unavailable: no successful result is returned.
- Invalid reports do not burn the remote nonce before cryptographic evidence validation.

## Limits

This is not proof of a production anti-rollback service. Registry persistence uses SQLite on the same machine in these tests. Upstream Lycheetah code is unchanged and upstream CI is unrun. No real external service was contacted, no real refund was created, and no production credentials were used.
