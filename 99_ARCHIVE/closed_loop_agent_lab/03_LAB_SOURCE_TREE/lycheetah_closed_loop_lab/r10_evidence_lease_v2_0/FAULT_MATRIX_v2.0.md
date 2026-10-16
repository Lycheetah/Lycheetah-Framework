# Fault and Race Matrix v2.0

| Fault or interleaving | Expected behavior | Observed in local reference prototype |
|---|---|---|
| Evidence write linearizes before lease acquisition | New lease denied; no effect | Pass |
| Lease acquisition linearizes before evidence write | Evidence write refused while lease active | Pass |
| Provider call crosses token expiry after being claimed `IN_FLIGHT` | Evidence remains pinned until result is confirmed or reconciled | Pass |
| Unclaimed token expires before provider call begins | Lease expires; effect is refused | Pass |
| In-flight operation becomes stuck beyond TTL | Lock remains; automated release requires authoritative status/fencing | Documented fail-safe; full remote fencing not simulated |
| Active lease and second independent operation needs same evidence | Both leases may coexist; evidence remains locked until all release/expire | Pass |
| Any required evidence missing/false in multi-key acquisition | Entire lease acquisition rolls back; no partial lock | Pass |
| Lease token body/HMAC changed | Provider rejects before effect | Pass |
| Lease used with different operation ID or action digest | Provider rejects before effect | Pass |
| New effect attempted with expired lease | Provider rejects before effect | Pass |
| Provider commits but response disappears | Leave lease/outbox recoverable; replay same operation key | Pass |
| Provider effect is known committed but evidence later changes | Query durable provider result first; mark outbox done without repeating effect | Pass |
| Same idempotency ID and same payload | Return prior result, no second effect | Pass |
| Same idempotency ID and different payload | Conflict/reconcile, no second effect | Pass |
| Subject-status requirement gets newer passing record for same subject | Accept only if trusted policy explicitly chose `SUBJECT_STATUS` | Pass |
| External writer bypasses lease authority | Not covered; lease assumptions violated | Not tested; documented gap |
| Real remote provider has no atomic idempotency contract | No exactly-once claim; reconcile | Not tested against real service |

## Concurrency race experiment

`run_evidence_race_experiment.py` launches a writer and a lease acquisition in parallel against one SQLite evidence authority for 200 independent keys. It requires one of two outcomes:

- the update commits and the lease denies the stale exact snapshot; or
- the lease commits and the update is blocked until release.

Any outcome where an invalid snapshot is leased or an update succeeds while a matching `ACTIVE` or `IN_FLIGHT` lease protects that key is a violation. See `evidence_race_results_v2_0.json` for observed counts and zero-violation result.
