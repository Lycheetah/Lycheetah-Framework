# Fault Matrix v1.9

| Fault / adversarial case | Expected safe result | Local outcome |
|---|---|---|
| Process fails before enqueue transaction commit | Entire local transaction rolls back | No outbox; witness still unused; retry can enqueue |
| Local commit succeeds, acknowledgement is lost | Retry finds the outbox row tied to the witness | Same operation ID returned; no second row |
| Process stops after enqueue but before dispatch | Worker resumes from durable pending row | One provider effect after dispatch |
| Provider commits effect, response is lost | Retry same operation ID | Provider returns stored result; one effect |
| Worker stops after provider response, before local acknowledgement | Recover `IN_FLIGHT` row and retry same key | One effect under provider idempotency contract |
| Two worker threads dispatch same operation | Same remote idempotency key | One simulated provider-side effect |
| Same idempotency key, different payload | Provider rejects conflict | No second effect |
| Provider lacks durable idempotency | Do not send; require reconciliation | `RECONCILE`, zero remote calls |
| Stored outbox JSON digest mismatch | Reject before remote call | `RECONCILE`, zero remote calls |
| Evidence changes before enqueue recheck | Refuse authorization-to-outbox handoff | No outbox action |
| Evidence source changes immediately after supplying passing snapshot | Prototype may still enqueue | **Known unresolved TOCTOU limitation**, deliberately tested |
| Naive non-idempotent baseline loses acknowledgement and retries | Re-applies the same request | Two simulated effects; demonstrates why naïve retry is unsafe |

The results refer to deterministic local fault injection. They are not production reliability rates.
