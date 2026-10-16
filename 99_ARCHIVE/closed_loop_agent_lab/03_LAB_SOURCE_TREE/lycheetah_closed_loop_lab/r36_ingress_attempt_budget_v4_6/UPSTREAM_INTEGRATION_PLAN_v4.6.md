# Upstream Integration Plan v4.6

1. Review rate semantics with gateway operators: blocked attempts now count toward the shared connection rate. Confirm desired refill/burst capacity and client-facing rejection metrics.
2. Apply the changes only on a clean, non-default branch. Do not mix v4.5 and v4.6 processes against the same shared quota database during rollout.
3. Run the upstream full test suite and the existing mTLS gateway lifecycle runner.
4. In a staging environment, open more connections than the active/per-peer limits while keeping the active slot occupied; verify rejected attempts consume the connection budget and the next connection remains rate-limited after the slot frees.
5. Observe accepted-vs-rejected connection rates and false-positive behavior. Rate tokens apply only after TCP accept, not before the kernel backlog.
6. Consider a separately scoped IPv6 prefix quota in a later iteration only after testing NAT/address aggregation trade-offs; do not treat mapped-address normalization as a defense against rotating native IPv6 addresses.
