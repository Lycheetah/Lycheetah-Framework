# Failure Museum v0.9 — Preserve the uncomfortable boundaries

**F9.1 — Boolean caller approval was never authentication.** Earlier `reviewer_approved=True` can be supplied by application code without evidence of review. Strict persisted mode now rejects this, but legacy non-strict mode is deliberately retained. **Risk:** unsafe deployment configuration.

**F9.2 — A signed permit is not a person.** HMAC proves control of a signing secret; it does not establish named identity, comprehension, consent, or evidence quality. A model given signing credentials would bypass the intended human boundary. **Unresolved:** actual auth and reviewer UI.

**F9.3 — Matching event heads are not enough to prevent permit transfer.** Two newly initialized ledgers share an empty event head. Initial permit scope without a distinct database identity could be replayed to both. **Fix:** random persisted `ledger_id` included in each permit; an independently created second ledger rejects it. **Residual:** a complete clone preserves the same ID.

**F9.4 — Archived signatures do not certify the historical clock.** Local audit can validate the HMAC and adjacent event linkage, but the event's `recorded_at` is a historical knowledge timestamp, not a trusted wall-clock commit timestamp. **Unresolved:** timestamp attestation and out-of-band external anchors.

**F9.5 — No external/independent AI performance result.** v0.8's fair temporal SQL baseline tied the gateway on synthetic queries. v0.9 does not alter extraction quality and has no live model scores. Counting internal tests as AI accuracy would be misleading.

**F9.6 — Canonical CASCADE code remains unevaluated in-process or out-of-process on this build.** Earlier source inspected and SHA pinned, but the trusted source file was not made available in the isolated runtime. Toy diagnostics are not canonical results.

**F9.7 — Code-level signing is not an end-to-end protected service.** The example demo issues a permit with an ephemeral test key in one process. The signer must be isolated, authenticate a reviewer, and guard keys before any real deployment. This is a development protocol and threat-model example.

**F9.8 — Archived permit does not recreate the user's reviewed screen.** The permit signs the audited batch but the local audit record lacks a separately attested human-visible presentation of the clauses. Independent reviewer consent evidence remains future work.

**F9.9 — Inherited SQLite resource warnings.** Original SQL comparator tests can emit `ResourceWarning: unclosed database` in Python 3.13; they still pass. A future hygiene pass should make comparator connection lifecycle explicit rather than masking warnings.
