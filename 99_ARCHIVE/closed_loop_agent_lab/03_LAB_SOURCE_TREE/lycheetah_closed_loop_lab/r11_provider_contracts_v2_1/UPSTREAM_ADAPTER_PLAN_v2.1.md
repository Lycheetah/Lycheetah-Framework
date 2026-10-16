# Upstream adapter integration plan

1. Add a provider-adapter contract with explicit capability semantics, endpoint/action identity, key scope, retention horizon, payload-conflict behavior, lookup consistency, and conditional-effect support.
2. Make the adapter implementation—not untrusted metadata—the source of retry decisions. Unknown, expired, or unsupported behavior maps to `RECONCILE`.
3. Keep action deduplication and evidence-condition enforcement as separate checks in configuration and test results.
4. Implement a contract test fixture suite that every new provider adapter must pass in a local fixture and a sandbox account.
5. Add fault injection for: request accepted then response lost; response returned but local acknowledgement lost; provider key aged beyond TTL; same key/different payload; concurrency; condition changes between precheck/commit; provider lookup stale or unavailable.
6. Record docs URL/date and provider API version. Recheck key TTL/scope when adapter/API version changes.
7. Do not promote the adapter if the provider cannot establish a durable outcome after ambiguity. It can still be used for reversible/read-only calls, but irreversible calls route to reconciliation.

The next implementation must target a specific real operation only after its official contract is chosen; generic claims about “idempotent provider” are too broad.
