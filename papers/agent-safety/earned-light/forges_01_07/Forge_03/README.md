# EARNED LIGHT — FORGE III
## Human Reconfirmation Bridge v0.3 · Standalone research prototype

**Date:** 18 October 2026 (Pacific/Auckland)  
**Status:** Locally executable research; **NOT** integrated with Lycheetah's SovereignExecutionHarness; **NOT** production-grade authentication or approval UX; **NO** real side effects.

> *Doubt should interrupt a consequential action, not silently become permanent failure or automatic permission. Legitimate authority is re-earned through an independently authenticated, bound, explicit human decision.*

### Progress from Forge II

Forge II introduced separately signed scoped grants and field-level origin attestations. In its 43 author-authored scenarios, EAC v0.2 allowed 8/10 benign cases and 2/33 malicious-labelled cases. Two benign denials had potentially legitimate destinations whose origin could not be independently attested. Forge III provides a signed, bounded recovery ceremony for such cases **without converting source content into authority**.

### Two independent ceremonies

1. **Open review:** A trusted human-facing service, outside the agent, emits a signed `ReviewIntent` for the **complete request digest**, grant ID, principal and one-time nonce. Agent-supplied claims of human initiation are not accepted. If absent, the bridge does not generate a review challenge.
2. **Approve action:** The trusted service retrieves a server-sealed, deterministic, complete, ASCII-escaped rendering of the action (including hidden `cc`/`bcc`), authenticates the principal through an **external process** (only simulated here), and returns a signed `ReviewReceipt`. The receipt binds challenge ID, exact action digest, displayed-text hash, principal, grant and expiry. **An initiation is not an approval.**
3. **Claim and effect:** The bridge checks the original EAC gate and current grant, checks the signed review receipt and sealed display, then atomically consumes the challenge in SQLite before invoking an **in-memory mock callback**. Reused receipts fail. Execution is **at-most-once claim**, *not exactly-once effect*.

Denials that may enter this path: `FIELD_PROOF_MISSING` or `ORIGIN_DISALLOWED`. Invalid grant, spoofed/invalid proof, mismatched field value, revoked context, unknown operation, expiry, unknown fields and other errors **cannot** be converted by a reconfirmation receipt.

### How to reproduce

Python 3.10+ with `cryptography` and `pytest`:

```sh
python -m pip install cryptography pytest
cd EARNED_LIGHT_FORGE_03
python -m pytest -q
python experiment_bridge.py
```

This package contains **unchanged copies** of the Forge II implementation and baseline tests (`earned_authority.py`, `demo_fixtures.py`, `airlock.py`, `tests/test_eac_v02.py`) to make the experiment reproducible without GitHub. `experiment_v02_original.py` is also unchanged from Forge II (file renamed only).

### Tested outcomes

- `76 passed` across unchanged Forge II and Forge III tests at handoff creation.
- Under **the same 43 pre-existing, hand-authored scenarios and author-simulated human choices**:
  - EAC v0.2: `8/10` benign allowed; `2/33` unauthorized allowed.
  - EAC + reconfirmation v0.3: `10/10` benign allowed; `2/33` unauthorized allowed.
  - Two simulated trusted UI initiations, two simulated approvals. Nine other recoverable scenarios generated no challenge without an explicit trusted UI initiation.
- The same **two trust-root-failure examples persist**. This is not an independently validated success rate and does not establish security superiority to an exact-action human approval baseline.

### What the prototype explicitly does NOT do

- Does not authenticate a real user, implement WebAuthn or prove the person saw/read the actual details. `TrustedReviewAuthority` is a **test-only signer** controlled by the fixture; NEVER expose it to the agent or copy it into deployed code.
- Does not protect a compromised review/ingress signer, malicious or confused user, deceptive but correctly displayed task, unsafe HTML UI, or a compromised underlying device.
- Does not guarantee provider consistency, exactly-once Gmail/Calendar effects, multi-process revocation atomicity, transparency-log integrity, or idempotent recovery after uncertain provider responses.
- Does not measure real-world false positives, conversion, approval time, human burden, prompt-injection reliability, consciousness or thermodynamic agency.
- SQLite stores the review plaintext; **do not store production personal data** in this research implementation.

### Files

- `human_bridge.py` — deterministic display, signed review initiation, signed approval, SQLite one-use claim, mock effect boundary.
- `tests/test_bridge.py` — Forge III tests, including forged approvals, swapped receipts, replay, concurrency, revocation, refusal, expired intent, display substitution, effect uncertainty.
- `tests/test_eac_v02.py`, `earned_authority.py`, `demo_fixtures.py`, `airlock.py`, `experiment_v02_original.py` — retained v0.2 artifacts.
- `experiment_bridge.py` — repeatable comparison on the prior 43 hand-authored scenarios; no outside evaluator.
- `results/bridge_metrics.json`, `results/scenario_results_forge03.csv` — generated local results and raw decisions.
- `RESEARCH_PASS_03.md`, `THREAT_MODEL.md`, `CLAIMS_AND_FAILURES.md`, `SHA256SUMS.txt` — interpretation, risks, reproducibility and handoff.

### Next decision

Build a real independent approval UI + identity provider only after a version-pinned audit of the actual Lycheetah permit/gateway path. Before asserting an advance over conventional engineering, compare against **proper exact-action human approval** on a *pre-registered outside-authored corpus*, including approval fatigue and coercion/misleading-screen risks.
