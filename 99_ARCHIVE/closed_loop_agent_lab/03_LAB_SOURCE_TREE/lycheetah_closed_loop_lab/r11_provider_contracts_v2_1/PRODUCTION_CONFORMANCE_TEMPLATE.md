# Actual Provider Conformance Record (fill only from observed tests)

- Provider / API product:
- API version:
- Test environment / account scope:
- Documentation URL and retrieval date:
- Idempotency key scope and retention:
- Same key / same payload replay behavior:
- Same key / different payload behavior:
- Lookup consistency and definitive-not-found semantics:
- Durable outcome after simulated client timeout:
- Concurrent same-key requests:
- Can the provider enforce the authorization precondition at effect commit?
- Is the condition owned by the provider or by another system?
- What happens if the condition changes between precheck and effect?
- Can a reservation/lease/fencing token be enforced provider-side?
- Crash / restart results:
- Request/result hash references (no secrets or customer data):
- Unresolved cases:
- Decision: `CONFORMANT` / `NONCONFORMANT` / `UNKNOWN — RECONCILE ONLY`

Do not mark CONFORMANT based on advertised features alone. Fill with actual sandbox observations and authoritative documentation. Never store credentials or unredacted user information in this record.
