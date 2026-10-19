# Forge VI — Threat model and evidence memo

## What was implemented

`attested_gateway.py` adds host-pinned Ed25519 verification for APPROVE/WITHDRAW events, exact action SHA-256 binding, principal and scope binding, nonce uniqueness, version concurrency control, time-limited signed messages, atomic storage of signed-event metadata alongside the existing upstream authority and choice ledger, and SQLite finality trigger protection.

The finality trigger is the critical fix: signature expiry is checked again by `lycheetah_trusted_time()` when upstream CommitFence attempts to insert a new effect. This reuses upstream finality, rather than rewriting its commit method. A deliberately weakened fixture demonstrates how a pre-dispatch-only time check allows expiration between check and insert.

**Important constraints:** An out-of-band key enrollment/attestation process is assumed, **not implemented**. A valid signature associates the request with a pinned test key, not necessarily a person. No real external requests were sent. A test-generated private key exists only in temporary test memory. The signing system is NOT a deployable signing UI. No meaningful human comprehension, freedom from coercion, or genuine voluntary intent is established by the code.

## Verified local properties

- Only a message signed by the pinned test private key can authorise an exact matching action.
- Changing recipient, content, principal or scope invalidates or mismatches approval.
- Old signatures cannot restore an authority generation once revised or withdrawn.
- Concurrent conflicting updates of the same intention have exactly one winner.
- Local transaction failure rolls back signature-event recording, intention and authority together.
- A local protected effect insertion after signed expiry is blocked, even if the expiry occurs during dispatch.
- Revocation and protected commit are serialised in the existing upstream database.
- No human-worth or metaphysical free-will score is emitted by the choice-surface inspector.

These are **self-authored synthetic tests** and narrow code observations; they are not security certification or proof of globally enforced oversight.

## Residual failures / negative controls

1. **Privileged database compromise:** A caller with DDL privileges can drop the finality trigger, modify signed event records, and bypass the host. The trusted runtime/process/OS security boundary must be real, not a Python naming convention.
2. **No external finality:** Real APIs can complete effects after local revocation if requests were already accepted; this SQLite trigger protects *local inserts only*.
3. **Signature is not consent:** A person could be tricked or pressured into signing an accurate binary payload; the code cannot detect that.
4. **Key lifecycle absent:** Secure key provisioning, device binding, key compromise response, rotation, recovery and revocation need actual design and outside expertise.
5. **Trusted clock assumption:** Clock integrity and leap/rollback behavior are not independently guaranteed. The trigger invokes a host-supplied function, not a certified time source.
6. **Host API boundary:** The class exposes Python members `_ledger` and `_fence`. An untrusted model must only receive a network- or process-mediated interface with privilege separation; this Python object is not that security isolation.
7. **Preview lacks user verification:** A signed `action_hash` does not mean an identifiable human inspected the exact content. Trusted-display UX and explicit comprehension studies are pending.
8. **Local receipt limitations:** Metadata is in SQLite, not independently signed or externally anchored. Privileged mutation remains possible.
9. **Legacy data:** Trigger is installed only for future insertions. It cannot certify effects written before installation or outside this store.
10. **Upstream warning:** The mirrored `CommitFence`'s SQLite connection patterns produced ResourceWarnings on Python 3.13; original file is preserved, not silently patched.
11. **No trained AI-agent evaluation:** All scenarios are scripted fixtures, not general-purpose model attempts.
12. **Mismatched grant semantics:** One active approved action per principal+scope is supported. Multi-grant policy, affected-party consent and delegated authorities remain unsolved.

## Falsifiers and next milestones

- Find an effect inserted through the protected SQLite sink after the host clock's signed expiry with the guard enabled => **current narrow time-bound safety claim false**.
- Find one conflicting signed update accepted after a newer version committed => **version-serialisation claim false**.
- Get an unsigned or wrong-key event accepted via the public `submit()` interface with protected database privileges intact => **signature-admission claim false**.
- Show users cannot accurately distinguish send-now from draft-only despite signing => **broader sovereignty-UX claim fails**.
- Demonstrate security-regression under true multi-process load, process crash/restart, provider timeouts, malicious input encodings, and adverse key lifecycle; not tested here.

## Integration proposal, not a production recommendation

1. Review upstream CommitFence and replace direct SQLite schema coupling with a documented extension interface.
2. Put signing key and trusted display out of the model-controlled process.
3. Restrict all DB/commit capabilities to the trusted mediator; agents may only propose actions, never access the ledger or signer.
4. Add permission state/receipt delivery to a real user interface and a trustworthy cancellation/last-safe-stop label.
5. Map remote provider states (accepted, committed, cancelled, unknown) separately from local state; require reconciliation and bounded retry budgets.
6. Retain existing assurance receipts and external head anchoring; do not claim database audit alone is tamper-proof.
7. Review data retention and privacy, then pilot in a deliberately harmless environment with a named human approver.
8. Run a participant comprehension study with a matched conventional baseline. Publish failures.

**Status:** `[TESTED LOCAL REFERENCE]` + `[PROPOSED HUMAN-SOVEREIGNTY FRAME]`, no deployment, no independent review.
