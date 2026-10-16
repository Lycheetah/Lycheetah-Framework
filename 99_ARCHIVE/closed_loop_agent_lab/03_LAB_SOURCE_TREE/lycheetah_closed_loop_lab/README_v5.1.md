# Lycheetah Closed-Loop Agent Lab — v5.1

**Current focus:** agent authorization and durable recovery; external witness integrity; mTLS remote witness and registry processes; shared quotas and ingress abuse resistance; bounded-cardinality overflow state.

## Latest work

### v5.1 — Overflow-State Integrity

The current newest increment is `r41_overflow_state_integrity_v5_1/`. It validates fixed overflow-shard state on reconstruction and fails closed for missing, extra, malformed, or out-of-capacity state rather than silently replenishing it. The direct local test rerun passed **54/54**.

### v5.0 — Bounded-Cardinality Overflow Buckets

`r40_bounded_cardinality_overflow_v5_0/` adds fixed keyed overflow shards for peer and IPv6 aggregate attempt buckets when exact per-source state reaches configured cardinality limits. The direct local test rerun passed **50/50**.

### Previous cumulative baseline

`r39_hierarchical_attempt_quotas_v4_9/` provides the v4.9 local baseline, including hierarchical per-peer and IPv6-aggregate attempt-rate buckets and its fairness probe. Its archived report records 153 passing methods across its four local suite groups.

## Recommended entry points

1. Read this file and `PACK_MANIFEST_v5.1.md`.
2. Read `r41_overflow_state_integrity_v5_1/test_output_v5.1_reverified.log`.
3. Compare `r40_bounded_cardinality_overflow_v5_0/` with `r41_overflow_state_integrity_v5_1/` to see the v5.1 integrity changes.
4. Read `r39_hierarchical_attempt_quotas_v4_9/THREAT_MODEL_v4.9.md` before interpreting the ingress results.

## Boundaries

These are local reference implementations and tests, not upstream CI or production certification. SQLite state authority is same-host; quota controls apply after TCP accept; prefix and overflow buckets can group unrelated clients, including behind NAT; and no upstream branch or pull request was changed.
