# Lycheetah Closed-Loop Agent Lab — Current Index v5.1

**Latest cumulative research artifact:** `lycheetah_closed_loop_agent_lab_v5.1.zip`

**Latest research topic:** overflow-state integrity for hierarchical ingress attempt quotas.

## What changed

- **v5.1** verifies the persisted fixed overflow-shard state set, bounds and finite values, and fails closed rather than silently replenishing missing rows on ordinary ledger reconstruction. Latest direct test rerun: **54/54 passed**.
- **v5.0** adds fixed keyed overflow shards for bounded fallback when exact peer/aggregate bucket tables reach cardinality pressure. Direct test rerun: **50/50 passed**.
- **v4.9** is the previous packaged cumulative snapshot and adds optional per-peer and IPv6-aggregate attempt-rate buckets with a fairness differential probe.

## Downloads

- `lycheetah_closed_loop_agent_lab_v5.1.zip` — cumulative lab archive through v5.1.
- `lycheetah_ingress_overflow_state_integrity_v5.1.zip` — focused standalone v5.0/v5.1 package.
- `lycheetah_research_vault_2026-10-17.zip` — all useful release ZIPs, prior snapshots, companion research packs, source tree, catalog and checksums in one archive.

## Current limits

All newest v5.0/v5.1 results are local reference tests. They are not upstream CI, production certification, or proof against a malicious host/filesystem administrator. The current design uses same-host SQLite coordination and its controls operate after TCP accept. No source branch or pull request was changed.
