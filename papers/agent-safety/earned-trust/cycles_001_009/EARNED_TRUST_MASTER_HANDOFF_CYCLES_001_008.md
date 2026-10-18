# EARNED TRUST — Master Research Handoff, Cycles 001–008

**18 October 2026, Pacific/Auckland**  
**Current status:** eight locally authored synthetic research cycles, **not** an independently validated Lycheetah assurance deployment. GitHub and live external providers remain untouched.

## Purpose

Trace accountability from AI-proposed text to tool action, exact human authorization, evidence freshness, provider commit, signed receipts, disputed provenance, and process-crash recovery, without treating a correct signature as proof that the underlying evidence is true.

## Cycle lineage

| Cycle | Research target | Preserved limit |
|---|---|---|
| 001 | Admission vs finality vs conditional provider writes | Synthetic labels and false evidence |
| 002 | Local transactional execution and concurrency | Real Framework bridge not executed |
| 003 | Action-bound signed authorization and receipt | Authentication does not prove truth |
| 004 | Separate outcome witness | Correlated or jointly false testimony |
| 005 | Declared provenance ancestry | Unknown/false source relationships |
| 006 | Governed source registry and challenges | Registry challenges accepted in separate store may not reach dispatch |
| 007 | Last-responsible-moment SQLite dispatch fence | Two-store challenge relay gap; remote provider outside transaction |
| **008** | **Durable outbox, process crash recovery, authenticated reconciliation** | **UNKNOWN remains ambiguous; direct provider bypass; native integration absent** |

## Cycle 008 decisive findings

**Within one cooperating SQLite writer domain**, send reservation and revalidation of an upstream source challenge share one transaction. A source challenge committed first prevents the action's local reservation. The outbox row moves to `SENDING` only together with `DISPATCHING` and its audit event. Once a reservation commits, a later challenge cannot reverse a potential remote provider action.

A terminated process after local reservation may have sent nothing; a terminated process after the simulated provider commit may have caused an effect. Both are recovered as `UNKNOWN` until an authoritative, action-bound provider status record is presented. This avoids automatic duplicate retries at the cost of stalled, unreconciled effects.

Cryptographically valid fixture receipts and correct permission gates can still propagate false evidence. Direct provider access bypasses the gate. A challenge accepted in a separate registry but not relayed to this authority remains invisible—Cycle 008 does not magically make cross-store integration atomic.

## Local verification — rechecked this turn

- C001: 20 synthetic tests pass
- C002: 29 synthetic tests pass
- C003: 50 synthetic tests pass
- C004: 38 synthetic tests pass *only when excluding the four native integration candidate tests, whose imports fail*
- C005: 42 synthetic tests pass *only when excluding the four native integration candidate tests, whose imports fail*
- C006: 59 synthetic tests pass
- C007: 47 synthetic tests pass
- C008: 46 synthetic tests pass with ResourceWarnings-as-errors

**Selected synthetic total: 331 passing.** The default C004/C005 complete suites report errors; `historical_recheck_results.json` preserves the exact outputs. The C007 real-framework contract exits code 4 with `No module named 'lycheetah'`, so **0 native Framework tests executed here**. Do not interpret 331 as default-suite, external or integrated validation.

The C008 fixed scenario matrix matches the author's 22 expected outcomes, **including four explicit negative/limit cases**: late challenge, false authoritative evidence, direct provider bypass and a challenge stranded in another datastore. Raw results are in `earned_trust_cycle_008/scenario_results.json`.

## How to resume

1. Read `earned_trust_cycle_008/README.md`, `RESEARCH_REPORT.md`, `CLAIMS.json` and `INTEGRATION_HANDOFF.md`.
2. Run its 46 tests and 22-case matrix against the included byte-identical C007 `upstream_dispatch_fence.py`.
3. Re-run C001–007 with `earned_trust_cycle_008/run_historical_recheck.py` and preserve native-import errors separately.
4. Acquire a real pinned checkout of `Lycheetah/Lycheetah-Framework` (historical reference `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`) and install dependencies. Run the C007 native four-case contract. Do not patch imported tests to make a missing package look successful.
5. Decide who authoritatively commits governance challenges. **Never assume accepting one in the Cycle 006 store implies visibility in C008's dispatch store.**
6. Test mandatory provider-side authorization, restricted access credentials, durable reconciliation and request-in-flight revocation under a matched conventional baseline.
7. Get independent review and genuinely external data before making general safety, commercial, or novelty claims.

## Threat model and hard restrictions

All keys and business events are lab fixtures. No independently authenticated actor, customer dataset, production API, secure remote enclave, distributed consensus, or real power-loss test exists in this packet. SQLite WAL `FULL` durability relies on SQLite's documented conditions and the host filesystem. Real external effect execution is **disabled**. The code is **not production-ready**; the tests do not certify safety or correctness outside the stated synthetic cases.

**Research motto:** Veritas before victory — keep the counterexamples.
