# Lycheetah Sovereign Choice Protocol — Research Forge II (v0.1)

**Research date:** 18 October 2026  
**Status:** `[LOCAL REFERENCE IMPLEMENTATION / SYNTHETIC TESTS]` — **not production security, not a human study, not a proof of free will, not committed to GitHub.**

## The distinction this packet makes

> A system that faithfully executes yesterday's plan may violate today's choice.

This project separates:

1. **Practical free will** — a contested philosophical notion of meaningful human choice, *not a software metric*.
2. **A microorcim-event** — a symbolic name for noticing and redirecting a choice.
3. **Observable agency** — whether a person has effective options to revise, revoke, inspect, and exit.
4. **Machine authority compliance** — a tractable property: tool actions must stay within the **latest valid** human mandate.

Sovereignty is not equated with productivity, conformity, perfect intentions, or an AI's preference for its own goals. The reference code only tests the fourth item.

## What works in this packet

- SQLite-authority records bound to one owner, agent, operation, resource, use count, and expiry.
- A human **intent version**; revising it invalidates all grants from the old version.
- Specific grant revocation.
- Host-controlled clock for permission checks.
- High-impact operations require a separate **one-use approval for an exact request + payload digest**.
- Request replay detection and `BEGIN IMMEDIATE` serialized authorisation.
- Local HMAC-SHA256 audit chain; mutation of recorded internal events is detectable with the original trusted key and complete chain.
- No real email, file, payment, network or other external effect is executed.

## Test results (same session, local)

`python -m unittest discover -s tests -v`: **28/28 passing**.  
`python counterfactual_lab.py`: **8/8 paired synthetic interventions passed**.  
`python demo.py`: blocked an unauthorised send, blocked a stale previously-approved send, and allowed a newly-authorised draft.

The paired lab holds an initial plan constant, then changes one permission condition. This is a policy-component test, **not a baseline comparison against real vendors, commercial agents, or even the stronger existing Lycheetah commit fence**.

## Run

Python 3.10+ and the standard library only:

```bash
cd sovereign_choice_protocol_v0_1
python -m unittest discover -s tests -v
python demo.py
python counterfactual_lab.py
```

The synthetic lab writes `counterfactual_results.json`. It never connects to external services.

## Package contents

- `sovereign_choice.py` — minimal policy model and audit receipt chain.
- `tests/test_sovereign_choice.py` — 27 unit and concurrency tests.
- `demo.py` — accessible example of a changed mind.
- `counterfactual_lab.py` + `counterfactual_results.json` — paired counterfactual-style policy tests.
- `docs/SOVEREIGN_CHOICE_ADDENDUM_v0.2.md` — philosophical synthesis and Microorcim repair.
- `docs/FRAMEWORK_INTEGRATION_PATH.md` — how to build *on* the current repo, not create an alternative security core.
- `docs/THREAT_MODEL_AND_LIMITS.md` — explicit limits and safe pilot conditions.
- `docs/CLAIMS_REGISTER.md` — what is tested, proposed, and unverified.
- `docs/LYCHEETAH_FREE_WILL_SOVEREIGNTY_MICROORCIM_CHARTER_v0.1.md` — prior research charter, preserved.

## Existing work and non-novelty disclaimer

The Lycheetah-Framework repo already includes a **Sovereign Execution Harness**, **Assurance Receipts**, and **Commit-Time Authorization Fence v0.7**. The last specifically tests revocation races at a protected finality sink. This packet is **a companion semantic layer and teaching/reference sandbox**, not a replacement or first implementation of revocable agent permissions.

Least privilege, revocable grants, one-use tokens, optimistic state versions, authoritative clocks, audited changes, action digests and finality fencing are established engineering techniques. Lycheetah's proposed contribution is the **explicit philosophical connection to human choice and its translation into auditable product obligations** — which still needs real usability and comparative evidence.

## Safeguards deliberately NOT claimed

This prototype does **not** independently authenticate users; any Python process with access to its owner methods and database could bypass policy. The model doesn't execute tools or control what a separate untrusted tool dispatcher does. Its return value does not guarantee a remote provider's effect was stopped after admission. It does not verify that a reviewed payload is exactly what downstream tools execute, or prevent all attacks by a privileged actor. Real systems need commit-time finality and protection at the external effect boundary.

If a claim requires a trustworthy finality sink, use the existing repo's **commit-time fence** as a starting point and test integration there instead of assuming this demo is enough.

> **The light you carry is not given; it is earned. And it remains yours.**
