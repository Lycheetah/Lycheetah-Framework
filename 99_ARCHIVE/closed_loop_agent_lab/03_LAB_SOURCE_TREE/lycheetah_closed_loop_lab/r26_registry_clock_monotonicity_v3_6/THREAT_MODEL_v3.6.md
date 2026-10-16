# Threat Model v3.6 — Monotonic Registry Clock

## Security property tested

While the registry database and its storage key remain current, a backward wall-clock movement must not make an expired freshness challenge valid again, and a signed request outside the configured timestamp window must remain invalid after its replay-cache row is pruned.

## New controls

- HMAC-authenticated persistent wall-clock high-water mark.
- Clock sampling inside the serialized write transaction.
- A replay-window value pinned in the authenticated clock state; silent widening is refused.
- Monotonic pruning cutoff authenticated with the high-water state.
- Immutable active request-ID rows and a SQL guard that only allows delete after the active replay cutoff.
- Schema checks for the clock state and request-ID cache.
- The challenge consume path uses the same clock sample as the auth/high-water decision and rejects not-yet-issued challenges.

## Adversarial cases exercised

- Clock moves backward after challenge registration.
- A challenge expires, then the wall clock is moved back into its validity interval.
- Clock state is edited or deleted through ordinary SQL.
- A live request-ID row is directly deleted or rewritten.
- Request IDs age out of the replay window; old signed requests are then rejected by timestamp rather than accepted as new requests.
- Replay-window configuration is widened after old IDs may have been pruned.
- A future-issued but registered challenge is consumed early.
- Request handler receives a deliberately changing clock source and must use only one sample inside the transaction.
- Retained v3.5 anti-rollback/concurrency/failure tests and all frozen v3.2 baseline cases are rerun.

## Residual assumptions / negative controls

1. The high-water mark and request cache live in the same SQLite file as the registry. A coherent restore of an older registry database also restores a valid older high-water mark. Coordinated rollback of primary and registry ledgers can still permit replay; the v3.5 negative control remains.
2. The storage HMAC key must be separately protected. If the database and storage key are both compromised, HMAC state validation no longer helps.
3. This prototype does not defend against a fully privileged local administrator who can disable SQLite triggers, replace the executable, and access the key. File ownership, service identity, process isolation, OS controls and remote operational audit are required.
4. The wall-clock high-water mark is deliberately fail-closed. An accidental forward clock jump can advance the floor and make service unavailable until trusted time catches up or an approved recovery procedure is executed.
5. Challenge records remain append-only and grow over time. Request cache size is bounded by accepted request volume per configured timestamp window, not by a hard row-count cap. Rate limiting and capacity controls remain deployment requirements.
6. Separate SQLite files on one host do not constitute independent administrative or infrastructure trust domains.

## Not established

No real external registry was contacted; no upstream source was changed; no production anti-rollback, WORM, HSM, managed database, or multi-account trust boundary was tested; no full upstream CI run occurred.
