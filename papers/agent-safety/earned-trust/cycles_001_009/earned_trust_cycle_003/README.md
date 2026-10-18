# LYCHEETAH · EARNED TRUST · CYCLE 003

**18 October 2026, New Zealand**  
**Status:** `SYNTHETIC LOCAL ENGINEERING TESTED` · `NOT DEPLOYED` · `NOT VALIDATED AGAINST REAL FRAMEWORK PACKAGE`  
**Research question:** Can we make a local execution record traceable to one authentic intent, one verified exact action and one locally committed result — without confusing that record with proof of real-world safety?

## Immediate commands

Python 3.10+; standard library only; no external credentials, payments or network calls.

```bash
cd earned_trust_cycle_003
python3 -m unittest -v test_authenticated_provider
python3 run_attacks.py
python3 process_probe.py
sha256sum -c SHA256SUMS.txt
```

Recorded on Python 3.13.5: **50/50 tests pass**; eight named scenarios show their specific outcomes; 4 separate multiprocess rounds × 8 processes each yield exactly 1 local commit and 7 idempotent replies per round. These are reproducible *authored fixtures*, not independent samples or performance/safety estimates.

## Main files

- `authenticated_provider.py` — domain-separated HMAC-SHA256 issuer and provider receipts; strict JSON action schema; one SQLite `BEGIN IMMEDIATE` commit boundary; version-bound evidence and policy; single-use approval; idempotent readback; local hash-chain verification and stored-receipt consistency checks
- `test_authenticated_provider.py` — 50 executed contract and adversarial tests
- `run_attacks.py` / `attack_results.json` — named positive/negative probes with raw outcomes
- `process_probe.py` / `process_results.json` — four isolated eight-process concurrency rounds
- `test_output.txt` — the complete local test transcript
- `real_framework_attempt.txt` — **not run**, import failure for the separate Cycle 002 real-Framework contract suite
- `RESEARCH_REPORT.md` — question, method, results, limitations and follow-up
- `claims.json` — evidence status and falsifiers
- `SHA256SUMS.txt` — checksums

## The control sequence

```text
proposed action (exact typed payload)
           |
      trusted host approval (LAB ASSUMPTION — NOT verified person)
           |
      trusted issuer HMAC authorization token
      [effect + approval + actor + scope + action digest
       + evidence version + policy version + expiry + nonce]
           |
      local provider validates HMAC / schema / exact action
           |
     BEGIN IMMEDIATE — shared local SQLite write transaction
       * replay/effect collision?
       * local stored ledger intact?
       * grant current, unconsumed and not revoked?
       * evidence PASS + eligible + exact version?
       * policy version and amount current?
       * insert effect and hash-chained audit event
       * sign local commit receipt with SEPARATE provider HMAC
     COMMIT
           |
      verifier checks HMAC and exact expected action/token
      optional independently held history checkpoint
```

Receipt schema says `earned-trust.local-commit.v1`: this is **not** a bank, payment processor, external system, or independent observation. The token does **not** authenticate the human who allegedly approved it. It is a MAC, **not** a publicly verifiable signature.

## Most important test

A trusted record that reports PASS/eligible but disagrees with the test's separate `truth` flag still produces a successful signed local receipt. That is an intended failure of the broad safety claim and a successful negative control of the narrower accounting contract. Authentication cannot establish the source record's truth.

## Real-framework installation remains pending

The earlier `earned_trust_cycle_002/run_framework_contract.py` suite directly imports Lycheetah's actual classes. It was attempted without an installed Framework and exited with a missing import; **zero actual Framework tests ran**. Once the real checkout is available, follow the Cycle 002 instructions rather than replacing it with mocks. GitHub's `master` was inspected read-only, with current fetched commit `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` (as observed 18 October 2026 NZ).

For integration, compare canonical action representations across `AssuranceEvent.tool_arguments`, `PersistentActionGuard.action_digest`, and the provider's actual payload. Never infer that passing any two gates proves the third is bound. Do not place signing secrets in model context, generated prompts, or public git source.

## Reproduction and use boundaries

The fixture deliberately gives the signing authority and the provider a common trust domain and current data in one SQLite DB. No distributed atomicity, production approval authentication, process containment, hostile host protection, external attestation, key management/rotation, secret storage, third-party security review or superior safety rate is claimed. Use only disposable fictitious data. There is no GitHub write in this package.
