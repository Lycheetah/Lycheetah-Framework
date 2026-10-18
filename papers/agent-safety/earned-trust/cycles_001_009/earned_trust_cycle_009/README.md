# EARNED TRUST — Cycle 009: The Enforced Boundary

**Date:** 18 October 2026 · **Evidence level:** locally executed engineering experiment · **External effects:** DISABLED

## Research question

Can an untrusted agent bypass a policy gateway and reach an effect provider directly? What assumptions must hold for a gateway denial to become an enforced denial?

## Architecture tested

```text
untrusted Python process (OS uid 65534 / nobody)
  | Unix-domain socket; kernel SO_PEERCRED actor mapping
  v
trusted agent-facing gateway (root-owned lab process)
  | verifies pre-approved exact action via C008 SQLite authority
  | issues short-lived action-bound HMAC capability AFTER dispatch reservation
  v
loopback-only HTTP provider /v1/execute
  | verifies token signature, expiry, key ID, bound action, amount and tool
  | SQLite BEGIN IMMEDIATE, UNIQUE effect ID + matching dispatch sequence
  v
synthetic committed effect + signed result
  | returns authenticated provider receipt to C008 ledger
```

**The actual Lycheetah Framework package is NOT imported by this lab.** `upstream_dispatch_fence.py` is the unchanged Cycle 007 *synthetic* controller, and `crashsafe_authority.py` the unchanged Cycle 008 *synthetic* outbox. The bridge contract requires a real Framework checkout; see `INTEGRATION_HANDOFF.md`.

## Executed evidence

- `python -W error::ResourceWarning -m unittest discover -p 'test_*.py' -v`: **47 tests passed** (Linux root-capable container, including tests that drop child UID to 65534).
- Previous Cycle 008 `test_crashsafe_authority`: **46 tests passed** in this turn.
- `python run_scenarios.py`: **15/15 exact outcomes match** a separate conventional HMAC + SQLite implementation **at the provider layer only**. This is no evidence of superiority or parity for the whole architecture.
- Upstream native `lycheetah` module: `NOT_EXECUTED` (import unavailable; repository network access not available in container).

The fixed 15-case scenario corpus is self-authored and artificial. It is not an empirical field security test.

## Run (Linux + Python 3.10+)

```bash
cd earned_trust_cycle_009
python -W error::ResourceWarning -m unittest discover -p 'test_*.py' -v
python run_scenarios.py
```

`test_socket_gateway.py` exercises SO_PEERCRED. Running as root permits dropping the subprocess UID to 65534 and testing the filesystem permission separation. On less privileged hosts, those tests skip rather than pretending isolation was exercised. Provider only binds to `127.0.0.1`, no money moves, and no GitHub writes occur.

## Files

- `protected_provider.py`: signature, scope, expiry, exact action and SQLite at-most-once effect handling; local HTTP server
- `gateway.py`: reservation-to-provider adapter (trusted key retained in gateway)
- `agent_gateway.py`: Linux Unix socket SO_PEERCRED agent principal mapping
- `conventional_baseline.py`: separately written conventional provider control
- `test_enforced_boundary.py`, `test_socket_gateway.py`: exercised tests and negatives
- `run_scenarios.py`, `scenario_results.json`: fixed matched provider scenarios
- `upstream_dispatch_fence.py`, `crashsafe_authority.py`, `lab_fixture.py`: preserved C007/C008 synthetic dependency and demo keys
- `run_actual_framework_contract.py`: prepared native-framework contract, not executed here
- `RESEARCH_REPORT.md`, `CLAIMS.json`, `INTEGRATION_HANDOFF.md`: findings and next steps

## Explicit failure boundaries

1. A stolen gateway HMAC key mints capabilities for arbitrary actions: demonstrated **successful unauthorized effect**.
2. An intercepted valid signed capability can be used by another bearer for its exact action once: demonstrated.
3. A source challenge after the dispatch reservation does **not** cancel an already issued capability or prevent provider execution: demonstrated.
4. Authenticated false authoritative evidence can still cause an incorrect effect: demonstrated.
5. A privileged host attacker, shared-UID user with secret access, forged trusted gateway, or remote provider with different atomicity semantics is outside these guarantees.
6. The provider accepts gateway-signed claims; it does not cryptographically consult the C008 ledger. A stolen key invalidates the entire trust assumption.
7. The gateway and provider run in the same trusted test process, while the attacker is a separate unprivileged process. This is **not** isolation between separate gateway and provider containers.
8. No TLS, rate limiting, seccomp, sandboxing, hardware-backed keys, external checkpoint trust, distributed fault testing, or independent review.

**Conclusion:** the tested unprivileged direct-HTTP bypass fails without a capability. This is a bounded demonstration of mandatory credential mediation for that route, not a universal claim that bypass is impossible.
