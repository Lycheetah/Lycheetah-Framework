# Adversarial Results and Non-Claims

**Status:** `[TESTED LOCALLY]` for behaviours enumerated below; `[UNVERIFIED]` for real-world validity or deployment.

## Precise scope of success

In a synthetic SQLite finality sink, checking the owner's *current intent version and ticket status* inside the same transaction as `INSERT local_effects` prevents a stale ticket from producing a new local effect **if the change was serialized first**. It also binds action contents, agent, recipient/resource, owner, operation and stable effect ID to an issued ticket.

Run `python -m unittest -v test_choice_fence` and `python benchmark.py`.

**Local result:** 37/37 tests passed; 6/6 matched synthetic post-admission interventions denied by protected local finality, while the intentionally weak pre-dispatch-only simulated provider accepted six.

Tests 35 and 36 are **expected negative findings**: suffix truncation without external anchoring and authorised-but-unwise behaviour remain possible. Their passing status is NOT a claim those threats are solved.

## The six comparison cases

| Intervention after early precheck | Toy baseline | Local fence | Why |
|---|---|---|---|
| Ticket revoked | Effect allowed | Denied | Current revoked state checked at commit |
| Human changed intention | Effect allowed | Denied | Ticket tied to stale intent version |
| Expiry reached | Effect allowed | Denied | Trusted-host time checked at commit |
| Payload substituted | Effect allowed | Denied | Canonical action digest differs |
| Recipient substituted | Effect allowed | Denied | Recipient is part of action digest |
| Agent substituted | Effect allowed | Denied | Agent identity field is bound |

The weak baseline represents an explicit TOCTOU anti-pattern. It is not an industry benchmark. Lycheetah's existing upstream `CommitFence v0.7` already demonstrates the commit-time technique in earlier research; this Forge III packet is an *intention-semantics companion*, not a replacement or a superiority claim.

## Critical boundary: what revocation cannot do

Three cases must never be conflated:

- **Before admission:** deny at precheck.
- **After precheck but before protected finality:** deny at atomic local commit if revoke/revise wins the transaction order.
- **After irreversible external finality:** revocation cannot rewind reality. The correct response is disclose committed/pending/unknown state, reconcile with provider where possible, avoid blind retries, and offer remedial actions.

A local SQLite transaction **cannot make an email-provider or bank API call atomic** unless that external provider participates in the relevant coordination or has its own fencing mechanism. In general, distributed finality and ambiguous external responses require careful provider-specific reconciliation.

## Threats explicitly outside the tests

- Trusted-owner API is not authenticated; a model with direct access to the SQLite file or Python instance could bypass it.
- Clock input is a constructor dependency treated as trusted; a hostile host invalidates the assumptions.
- No cryptographic signature from a real human; a boolean approval assertion is illustrative.
- The local HMAC chain lacks trusted external head/tail anchoring and can be rewritten by a privileged key holder.
- The simulated action hash covers canonical *illustrative* fields, not bytes actually placed onto a provider's wire by a dispatcher.
- No data export, deletion policy, operator comprehension, anti-coercion assessment, distress measurement, or UI implementation.
- The trusted host only checks operation names against a toy risk catalogue. Legitimately approved harmful effects remain possible.
- Cross-tenant isolation, OS sandboxing, authz at the dispatcher, and real key custody are absent.
- A signature on a receipt proves neither that the content is true nor that a human understood the consequences.

## Novelty and evidence

Capability checks, revocation, commit-time fences, precondition validation, idempotency, append-only logs and HMAC signatures are established computer-security patterns. The distinct *research hypothesis* is that a user-facing combination of **versioned intentions + observable meaningful refusal/revision/exit + enforceable agent boundaries** leads to improved understanding and control over ordinary AI assistants. That hypothesis has **not** yet been evaluated with real people or external tools.

Avoid claims of “first AI brand to respect free will,” “proven sovereign AI,” “0% risk,” or “machine consciousness detection.”
