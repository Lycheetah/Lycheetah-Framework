# Upstream Integration Plan v4.7

1. Review `request_deadline_seconds` as a transport-socket deadline, not a general application deadline; set explicit values for deployment endpoints.
2. Apply on a clean non-default branch; run the actual upstream suite and CI before promotion.
3. Run the header/body slow-drip regressions and confirm the slot is released near the configured deadline with no registry mutation.
4. Test a legitimate request whose quorum dispatch takes longer than the socket deadline. Confirm that the client observes ambiguity and that retry/reconciliation uses the same request idempotency key.
5. Add cooperative deadline/cancellation semantics at the application/RPC layer if business dispatch itself must be time-bounded. Do not assume closing the client socket cancels it.
6. Monitor deadline expirations, application completion-after-disconnect, and reconciliation outcomes separately; avoid logging request data or raw client IPs.
