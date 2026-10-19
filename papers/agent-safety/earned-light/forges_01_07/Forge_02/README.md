# EARNED LIGHT — FORGE 02
## Earned Authority Chain (EAC) v0.2: Origin-of-Authority Research Probe

**Date:** 2026-10-18 NZ  
**Status:** runnable, standalone synthetic experiment. NOT merged into the Lycheetah repository; NOT production-ready or externally validated.

> Capability can grow through learning. Authority must remain revocable and verifiably delegated.

This is an additive research probe for the Lycheetah SovereignExecutionHarness, not another named framework and not a replacement for existing guards, one-use permits, action hashes, compaction integrity, or signed receipts.

## What it does

For a declared effectful action (`mail.send` or `calendar.create`), EAC verifies:

1. A scoped, time-limited **Ed25519-signed grant** issued by a separately trusted approval service. The service (not the agent) must authenticate the human and establish actual consent.
2. The exact agent, session, tool, operation, scope and state version match that signed grant.
3. Operator-maintained action schema rejects missing effect fields and unknown effect fields.
4. Every controlled effect field (recipient, cc, bcc, attendee list) has a separately **Ed25519-signed value- and session-bound origin attestation** from a trusted ingress adapter.
5. Only acceptable origin classes are allowed for controlled fields. Untrusted email/web text may be quoted as content, but cannot manufacture an approved destination.
6. An online revocation set is checked at time of evaluation (research version is **in-memory**, NOT an operational revocation backend).

The signing service and trusted ingress adapter must be outside the agent's control. If they automatically rubber-stamp model assertions, the security story collapses.

## Quick start

Requires Python 3.10+ and `cryptography`; `pytest` for unit tests.

```bash
python -m pip install cryptography pytest
python -m pytest -q
python experiment.py
```

The experiment writes `results/metrics.json` and `results/synthetic_scenario_results.csv`. Both are included in this handoff.

**Zero real side effects:** no Gmail, Calendar, network, shell-executing provider, or user account is changed. `airlock.py` only invokes a test-supplied in-memory callback.

## Files

- `earned_authority.py` — verified-grant / verified-origin research gate, no signing private keys
- `demo_fixtures.py` — deterministic test-only signing fixtures. **Never import or deploy as an authority service.**
- `airlock.py` — illustrative mock effect callback boundary, not a replacement for gateway
- `tests/test_eac.py` — 28 local unit/regression tests including a preserved failure counterexample
- `experiment.py` — 43 hand-authored scenarios comparing declared scope, signed scope, and EAC
- `results/metrics.json` — precise counts, no unsupported statistical extrapolation
- `results/synthetic_scenario_results.csv` — each prediction, outcome and reason code
- `RESEARCH_PASS_02.md` — interpretation, architecture, negative findings, and next steps
- `CLAIMS_AND_FAILURES.md` — explicit claim/evidence table and preserved counterexamples

## Repository-context review

Read-only review of public repository `master` on 2026-10-18:
- https://github.com/Lycheetah/Lycheetah-Framework
- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/sovereign_harness.py

That module acknowledges that `authority_id` and typed packet `authority` entries represent declared grants, **not independently authenticated human identities**. It checks scope, exact action digest, current state version, expiry and replay in its own five gates. This probe explores authenticating the grant **upstream** and trusted field provenance at the effect boundary.

We could not clone the repo in this environment, could not import the full original modules, and did **not** run an integration test against live Lycheetah.

## Scientific boundary

This probe is security engineering, not a test of consciousness, thermodynamic intelligence or moral agency. The Layer-0 philosophical and thermodynamic hypothesis remain separate.

## Read the result before adopting

Synthetic results: EAC rejected 31/33 labeled unauthorized scenarios, and allowed 8/10 labeled benign scenarios. The signed-scope baseline rejected 13/33 unauthorized scenarios and allowed 10/10 benign. These numbers come from a small, author-selected synthetic corpus and **cannot** be advertised as general attack-prevention efficacy. The added layer failed the prespecified 90% benign utility target in this set. Two attacks using dishonest/compromised trust roots still passed.
