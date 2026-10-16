# Changelog v4.4

- Closes the documented same-host pre-TLS quota multiplication gap by adding an opt-in shared SQLite ingress ledger for global active connections, per-peer active connections, and global connection-rate tokens.
- Reserves global and per-peer active slots plus a rate token in one `BEGIN IMMEDIATE` transaction before the gateway creates a request thread or begins TLS.
- Hooks the lease into `process_request` / `process_request_thread`; local v4.3 per-process limits remain as an additional layer, not as a replacement.
- Adds two real mTLS gateway integration tests using two separate gateway objects sharing one DB: aggregate active connection cap and aggregate connection-rate cap.
- Adds 15 store tests including a spawned multi-process race, persistence, boot change, clock rollback, filesystem controls and aggregate-only snapshots.
- Preserves v4.3 shared authenticated coordinator quotas and all prior quorum / witness tests.
- Verification target: 117 local test methods across four suites; source pins, compilation and ZIP CRC checks.
- Scope remains same-host / same local SQLite file; no upstream source, hosted endpoint or production deployment is changed.
