# Threat Model v3.2 — Equivocation and Freshness

## New risk addressed

A primary anchor can produce valid signatures yet show different signed histories to different clients (split-view/equivocation). A signature authenticates a particular statement; it does not guarantee all clients receive the same statement or that a returned statement is the latest one.

## Assumptions for the reference quorum

- The primary anchor record is validated against a pinned key before witnesses vote.
- Witness public keys and the roster are pinned out of band; the caller cannot lower the fault budget or replace the roster inside a certificate.
- For the claimed four-witness profile, at most one witness identity is Byzantine/compromised.
- Each honest witness's monotonic guard is independently operated, durable and not rolled back with the witness process's local vote database.
- Honest witnesses only attest to the exact next sequence with a parent equal to the guard's current head.
- The verifier obtains fresh head reports with an unpredictable nonce and checks their signed time within a bounded clock-skew window.

## Invariants tested

1. Invalid primary anchor records do not obtain votes.
2. A witness cannot use its API to vote for two distinct records at the same database sequence.
3. A local vote-ledger restore cannot make a stale branch acceptable while the guard retains a later head.
4. A 3-of-4 quorum authenticates one identical head; two votes are insufficient.
5. Certificate threshold is calculated from the pinned roster and configured fault budget (`n >= 3f+1`, `q=floor((n+f)/2)+1`), not accepted from caller claims.
6. A single compromised witness key cannot form a competing quorum once the three honest witnesses have locked the accepted branch.
7. A constructed fork requiring two double-signing witness keys leaves verifiable signed equivocation evidence and exceeds the `f=1` assumption.
8. A new client verifies chain continuity from genesis and compares the chain tip against a nonce-fresh witness quorum; old but valid certificates alone do not establish currentness.
9. Stale reports, wrong nonces, duplicate identities, unknown witness keys, tampered votes and discontinuous parent/sequence links fail closed.

## Not established

- `SQLiteCASGuard` is a test/reference adapter, not an external monotonic service. An attacker who can roll back both guard and local vote DB, or alter their runtime/key stores, can defeat this model.
- Multiple witnesses running under one administrator, host, backup policy or key-management domain are not independent failure domains. Four processes on one host are not four trustworthy operators.
- The prototype does not perform deployment, key provisioning/rotation/revocation or roster governance, and does not expose a remote witness HTTP service.
- The quorum does not prove source data correctness, operator intent, policy wisdom, or real-world side-effect safety.
- No hosted anchor API or Stripe API was called, no refund was created, and no upstream Lycheetah source was changed.
