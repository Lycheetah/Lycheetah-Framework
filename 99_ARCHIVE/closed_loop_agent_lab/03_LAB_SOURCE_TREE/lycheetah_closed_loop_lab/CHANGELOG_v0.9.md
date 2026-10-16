# v0.9 change log — 2026-10-16

- Integrated trusted-catalog validation into the host and fake-provider boundaries; the catalog is no longer checked only in a separate stamping utility.
- Added `catalog_sha256` to stamped action envelopes; host rederives trusted metadata and strict argument contract at approval issuance and execution claim.
- Validated current and stored policy JSON against the pinned catalog digest and its own durable SHA-256 at host claim, provider commit, and recovery retry.
- Added direct provider-boundary regression test to ensure malformed catalog metadata is rejected before provider/authority DBs are opened.
- Corrected a recovery design edge: already-committed provider effects remain reconcilable when current catalog configuration changes, but retrying an absent effect requires current catalog/policy approval.
- Added `reproduce_v0_8_catalog_bypass.py` to retain the older lab's failure: v0.7 accepts a handcrafted invalid action, while v0.9 rejects that action schema and accepts a valid catalog-stamped action. Fake SQLite only.
- v0.9 test runner passed 21 catalog/issuance tests plus 28 separate-process crash/recovery tests, 49 total across two interpreter processes.
- Updated root roadmap and audit notes. No public repository files were changed; no live model, authenticated approval UI, real external provider or production host was tested.
