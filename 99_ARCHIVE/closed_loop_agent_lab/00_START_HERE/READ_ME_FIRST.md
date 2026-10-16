# Lycheetah Research Vault — 17 October 2026

Brother, this is the consolidated preservation archive of the Lycheetah closed-loop agent-safety / cybernetics research and its companion packs. It preserves the current cumulative lab, the focused v5.0/v5.1 overflow-state increment, and earlier ZIP releases for provenance.

## Start here (recommended order)

1. **Current cumulative lab:** `01_LATEST_RELEASES/lycheetah_closed_loop_agent_lab_v5.1.zip`. This extends the previous v4.9 cumulative snapshot through v5.1. It includes the full source-and-results tree without Python bytecode caches.
2. **Focused newest module:** `01_LATEST_RELEASES/lycheetah_ingress_overflow_state_integrity_v5.1.zip`. Use this to inspect/re-run the v5.0 and v5.1 bounded-cardinality overflow tests.
3. Read `03_LAB_SOURCE_TREE/lycheetah_closed_loop_lab/README.md`, then `README_v5.1.md` and `PACK_MANIFEST_v5.1.md`.
4. For the latest increment, read `r41_overflow_state_integrity_v5_1/test_output_v5.1_reverified.log`; it reports 54 tests passed. Its v5.0 comparison run reports 50 tests passed.
5. Use `04_COMPANION_RECORDS/ZIP_CATALOG.csv` and the generated root `SHA256SUMS.txt` to inventory and verify nested release archives.

## Current technical focus

The newest increment adds explicit validation of fixed overflow-shard state to the hierarchical ingress attempt-rate quota system. It rejects missing/extra/malformed overflow rows and out-of-bound token values instead of silently recreating quota capacity when an existing ledger is reopened. This follows v5.0's fixed-shard fallback for bounded cardinality pressure, which in turn builds on v4.9's optional per-peer and IPv6-aggregate attempt-rate fairness controls.

## What is preserved

- Latest cumulative research snapshot and a separate v5.0/v5.1 package.
- All prior non-empty ZIP artifacts found at the archive-build time, including cumulative snapshots, provider/refund packs, mTLS/witness/quota focused releases, Human-AI Transition research, Rabbit Holes architecture notes and tool-definition attestation.
- The clean `lycheetah_closed_loop_lab` source tree, result logs, manifests, threat models, API contracts, source pins and integration plans (excluding `__pycache__` / `.pyc`).
- Companion checksum and archive-verification files where present.

## Verification and honest limits

- v5.0 direct local tests: **50/50 passed**.
- v5.1 direct local tests: **54/54 passed**.
- Prior cumulative v4.9 report: **153 local test methods across four local suite groups**.
- The v4.9 archive had passed ZIP integrity checks when inspected. New v5.1 archives and the master vault are checked during this build.
- These are local research and reference implementations—not upstream CI, a production security certification, or proof against a malicious OS/filesystem administrator.
- The ingress controls use same-host SQLite coordination and operate after TCP accept; they do not prevent upstream link saturation or SYN-flood exhaustion. Prefix caps and overflow shards may aggregate distinct clients and remain configuration-dependent.
- No GitHub branch, pull request or upstream source was changed by this archival step. No hosted provider was called.

## Archive structure

- `01_LATEST_RELEASES/`: use these first.
- `02_HISTORICAL_AND_FOCUSED_ZIPS/cumulative_snapshots/`: previous cumulative snapshots retained for history.
- `02_HISTORICAL_AND_FOCUSED_ZIPS/focused_standalone_modules/`: focused packages for testing individual milestones.
- `02_HISTORICAL_AND_FOCUSED_ZIPS/companion_research/`: companion architecture and Human-AI research.
- `03_LAB_SOURCE_TREE/`: readable extracted current tree.
- `04_COMPANION_RECORDS/`: catalog, checksum files and retest logs.
- `SHA256SUMS.txt` hashes all packed files except itself; `CONTENTS_MANIFEST.csv` deliberately excludes itself and `SHA256SUMS.txt` to avoid recursive hashes.
