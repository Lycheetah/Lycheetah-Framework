# Earned Trust — Nine-Cycle Agent Execution Research

**Status: PUBLIC EXPERIMENTAL RESEARCH · NOT DEPLOYED · NOT A SECURITY CERTIFICATION**  
**Dates:** 18 October 2026 · **Authoring project:** Lycheetah Framework · **Evidence:** local tests and self-authored synthetic scenarios

## Purpose

Can an AI action gateway enforce more than persuasive language? These experiments investigate exact-action permission, evidence freshness, witness lineage, challenge governance, crash recovery, and whether a low-privilege subprocess can bypass an action-signing gateway. The research deliberately preserves cases in which properly signed or approved actions are still wrong.

**Do not put this lab in charge of actual money, production credentials, customer data or irreversible systems.** The native `lycheetah.assurance` package was **not** executed in the experiments. Some security demonstrations require Linux/privileged test setup; running their tests on other systems does not establish equivalent containment.

## Results at a glance

The nine local synthetic suites passed **378 tests** in the publication review (per cycle: 20, 29, 50, 38, 42, 59, 47, 46, 47). This is authored engineering verification, not independent field measurement. C004 and C005 include **four native-framework import-error tests each** when default discovery is run without the actual package; those failures are not counted as passes. The code's source and raw scenario results are provided in their original cycle folders.

In C009, a Linux unprivileged subprocess could not read the test gateway's private key file and got HTTP 401 when trying an unsigned direct provider request. It **could** successfully request a previously authorized action via the Unix socket. **Successful counterattacks:** an attacker knowing the issuer's HMAC key forged an unauthorized provider effect, and a stolen unspent action-bound capability was usable once. A later challenge did not retroactively cancel an already reserved provider effect.

The conventional comparison at the C009 provider layer agreed with the experimental provider on all 15 authored cases. **No superior effectiveness, novelty, production safety or full-framework integration is claimed.**

## Research map

| Cycle | Focus |
|---|---|
| 001 | Admission vs finality vs provider commit |
| 002 | Transactional action binding and idempotency |
| 003 | Authenticated intent and receipt integrity |
| 004 | Separate signed observer vs signed provider |
| 005 | Source ancestry and witness independence |
| 006 | Challenged/reviewed provenance registry |
| 007 | Shared transactional dispatch/challenge fence |
| 008 | Crash-observable outbox and reconciliation |
| 009 | Local HTTP provider, HMAC capability and Unix peer-credential gateway |

Read each `earned_trust_cycle_NNN/README.md`, `RESEARCH_REPORT.md` and `CLAIMS.json` (or `claims.json`). Read `PUBLICATION_READINESS.md` for audit details and test-collection limitations. The **original** research handoff is `EARNED_TRUST_MASTER_HANDOFF_CYCLES_001_009.md`.

## Verification

Run **from this folder** with Python 3.10+:

```bash
python3 verify_release.py                  # CRC-equivalent SHA256 manifest and Python syntax checks
python3 verify_release.py --tests          # local authored suites; may require Linux/root for full C009 privilege evidence
```

The runner deliberately selects *local* test modules for C004/005 because the independent native-framework bridge requires a real checkout. It labels that exclusion rather than silently treating the missing modules as green. Inspect and run the bridge in the Framework environment before claiming integration. No live external writes are part of the runner.

## What is not proven

Signatures authenticate key holders, not factual truth. Two witnesses can share an origin or agree falsely. A post-dispatch objection may come too late. Symmetric keys, root privileges, a copied bearer capability or direct provider access can defeat certain assumptions. C009 gateway and provider are hosted in the same trusted lab process; this is not a production split-trust design. No independent threat-model assessment, external security penetration test, live provider deployment, or measured end-user benefit has occurred.

**Suggested home:** `Lycheetah/Lycheetah-Framework/papers/agent-safety/earned-trust/`. Historical files retained; new research belongs in a subsequent cycle rather than rewriting the negative results.
