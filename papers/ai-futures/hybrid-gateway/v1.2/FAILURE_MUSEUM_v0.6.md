# Failure Museum — Cycle 6 (2026-10-18)

## F06-01: v0.5 permitted partial historical updates [LOCALLY FIXED]

When two approved claims had been extracted, `commit_one` accepted the first but the later ledger head invalidated the second. A half-applied policy was possible. `HybridGateway.ingest_batch` now preflights on a shadow ledger then appends one `BATCH_ADMIT` event. SQLite `BEGIN IMMEDIATE` and single-event insertion make the local write all-or-nothing. Invalid second candidates and forced SQL errors leave zero batch claims in storage. **Not** a distributed transaction or authenticated approval.

## F06-02: Self-hashed history is not external attestation [OPEN]

A file editor with privileged access could rewrite the SQLite store and regenerate its event hashes. The optional `independently_anchored_head` detects such rewriting only if retained outside the store. No trusted remote witness, signature service or root-of-trust implemented.

## F06-03: All-abstain can game a single safety metric [SCORER FIX]

On the shipped *fictional self-authored 14-case instrumentation fixture*, "all abstain" has 100% correct abstention on five negative documents, but zero TP and zero positive-document recall on the nine answerable documents. Scorer publishes both measures, never conflates them. This does **not** demonstrate a neural model weakness.

## F06-04: Perfect contract matching is not independent truth [OPEN]

A mistaken operator annotation can be flawlessly enforced and still produce an incorrect policy answer. Clause whitelisting measures conformance to a chosen contract, not the correctness of that contract. Unmarked facts remain invisible to omission checks.

## F06-05: Privileged reviewer can be impersonated in-process [OPEN]

`reviewer_approved=True` is a trusted-caller signal, not a signature, identity or delegation token. A malicious writer executing within the trusted process can call the API as an approver. Production requires external identity, authorization, protected keys and separation of duties.

## F06-06: Strict grammar and source authority ceiling [OPEN]

Exact English grammars cannot parse many exception-heavy, negated, multilingual or novel facts. Even a source quote with a plausible number can be semantically wrong outside the three hardcoded grammar slots. A real held-out study with independent ground truth is required.

## F06-07: Only local SQLite atomicity covered [BOUNDARY]

Tests cover an intentional SQL insertion abort, two competing SQLite writers and an abrupt child-process exit before commit. They do not simulate physical power loss, filesystem corruption, external network effects, cross-service distributed commits or restoration from backup.

## F06-08: Neither live neural model nor canonical CASCADE run [OPEN]

We extended the gateway's source admission and evaluation infrastructure. The provider adapter and read-only diagnostic bridge remain prior work; their actual live neural-to-CASCADE path was not exercised here. Do not rename this outcome as end-to-end neural-symbolic validation.

## F06-09: User time/cost not measured [OPEN]

Fixture `review_minutes=0` are placeholders. Observed annotation and reviewer times must be collected on a real task before any time-saving commercial claim.

## F06-10: Replay cost rises with event history [OPEN]

Each SQLite commit replays all prior events and revalidates source bindings. This is a simple correctness-oriented research implementation; its throughput, memory, and adversarial input limits are not quantified.

**Preserve the limits alongside the passes.**
