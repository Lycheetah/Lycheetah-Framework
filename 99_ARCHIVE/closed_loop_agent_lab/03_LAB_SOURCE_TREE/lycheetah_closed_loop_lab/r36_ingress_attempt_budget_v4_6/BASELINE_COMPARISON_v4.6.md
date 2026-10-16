# v4.5 vs v4.6 — Measured Counterexample

Command used the same small setup with `max_active_connections=1`, `max_connections_per_ip=1`, and a global bucket capacity of two. One lease was held while multiple different-peer reserve attempts were made, then released before a final attempt.

| Step | v4.5 result | v4.6 result |
|---|---|---|
| First peer reserves | accepted | accepted |
| Second peer while active slot full | `active-connection-limit` | `active-connection-limit` |
| Third peer while slot remains full | `active-connection-limit` | `connection-rate-limit` |
| Slot released; fourth peer attempts | accepted | `connection-rate-limit` |

The baseline was run against the archived v4.5 source, and the changed behavior was run against v4.6. This is a targeted local experiment, not a load test. It demonstrates the intended accounting difference, not an end-to-end DoS mitigation claim.
