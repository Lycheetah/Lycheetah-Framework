# Threat Model v3.3 — Quorum Verifier Contract Hardening

## Four baseline acceptance classes reproduced in v3.2

`reproduce_v3_2_findings.py` executes against frozen v3.2 source and confirms:

- A caller-constructed `FreshHeadQuorum` object could be passed to `verify_current_chain()` and was accepted without verifying any signed fresh-head reports.
- Multiple witness IDs could alias the same Ed25519 public key, allowing one private key to produce multiple identity-labelled signatures and count as a quorum.
- A certificate could set `sequence=True` or `max_byzantine=True`, recompute its public certificate digest, and pass because Python treats `True == 1`.
- A pluggable monotonic guard could return `(True, record_hash)` and `attest()` would treat the Boolean as sequence 1, even though the fresh-report path already checked types.

These are verifier API/type/roster configuration gaps. The reproduction is local and does not contact a hosted service.

## Fixes in v3.3

- Currentness verification accepts raw reports and verifies them internally; summary dataclasses are output values only, not trusted input proofs.
- Witness registries reject duplicate raw Ed25519 public-key bytes across IDs.
- Certificate scalars and container shapes are strictly typed before comparisons.
- The pluggable guard return shape, sequence type, and digest are validated at every witness-side read.
- Witness vote and freshness-report signature domain/version has been moved to v3.3 to prevent cross-version message reuse.

## Assumptions

- Primary anchor keys and the witness roster are pinned/authenticated independently of caller-supplied certificates.
- At most `f` witness private keys/control domains are Byzantine, and each honest witness's monotonic guard cannot be rolled back with its vote ledger.
- A new client validates chain history from genesis (or incrementally from a separately trusted prior head) and obtains nonce-fresh head reports.
- The consuming application keeps challenge nonces unpredictable and does not reuse them; if durable one-time challenge enforcement is required across verifier restarts, it must be implemented in the verifier's protected state store.

## Non-goals and residual risks

- Distinct public keys do not imply distinct administrators, machines, clouds, backup processes, or key custodians. Roster governance must establish independent failure domains out of band.
- `SQLiteCASGuard` is not a production non-rollbackable high-water mark. If guard, witness database, private key, and backups share one control domain, coordinated rollback/compromise defeats this reference model.
- The quorum authenticates a checkpoint statement and mitigates certain split-view/equivocation cases under its assumptions. It does not prove the underlying data are correct, safe, or policy-compliant.
- The system is not an implementation of RFC 9162 Certificate Transparency and does not provide Merkle inclusion/consistency proofs.
- No production hosted anchor or Stripe API was called. No real refund was created. No upstream Lycheetah source changed. Upstream CI has not run.
