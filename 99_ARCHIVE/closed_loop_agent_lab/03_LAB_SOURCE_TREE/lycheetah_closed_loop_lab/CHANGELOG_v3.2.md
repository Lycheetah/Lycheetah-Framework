# Changelog v3.2 — Independent Witness Quorum

- Added Ed25519 checkpoint witness votes over the exact primary-signed checkpoint head.
- Added per-database witness sequence locks and a separate CAS guard abstraction; the SQLite implementation is explicitly reference-only.
- Added Byzantine quorum threshold `q=floor((n+f)/2)+1` under `n>=3f+1`, enforcing quorum intersection greater than the configured fault budget. The n=4, f=1 profile requires 3-of-4 signatures.
- Added quorum certificate construction and verification with a pinned witness roster and exact head binding.
- Added full certificate-chain verification from genesis; single signed checkpoint certificates do not by themselves prove continuous history.
- Added unpredictable nonce-bound fresh-head reports, clock-window checks, fresh quorum agreement and current-tip comparison to prevent stale-but-valid certificate rollback from being treated as current.
- Added signed equivocation evidence extraction for conflicting certificates at the same database sequence.
- Added 31 focused test methods. Retained v3.1 groups passed separately: 33 + 14 + 14 + 13. Total: 105 passing methods across five independent test-process invocations (not one monolithic run).
- No real hosted anchor/Stripe calls, no refunds, and no upstream source changes. Production monotonic guard and witness deployment remain unimplemented.
