# v4.6 vs v4.7 — Measured IPv6 Prefix Counterexample

A preserved local copy of v4.6's `shared_ingress_quota.py` is compared against v4.7 with `max_active_connections=4`, `max_connections_per_ip=1`, and a full global attempt budget.

| Scenario | v4.6 | v4.7 |
|---|---|---|
| First address `2001:db8:1234:5678::1` reserves | Allowed | Allowed |
| Second address `2001:db8:1234:5678:ffff:ffff:ffff:99` in same `/64` | Allowed as another exact address | Denied: `per-ip-connection-limit` |
| Address `2001:db8:1234:5679::1` in different `/64` | Allowed as another exact address | Allowed as another prefix bucket |
| `192.0.2.44` vs `::ffff:192.0.2.44` | Same identity after mapped-address normalization | Same `ipv4:192.0.2.44/32` bucket |
| Replica configured with IPv6 `/64` vs `/56` on same boot/database | Not applicable to prefix setting | Initialization fails closed on configuration mismatch |

This establishes the intended bucket-accounting change under the local reference implementation. It does not establish a general reduction in network attack traffic; the global attempt rate is still charged after TCP accept, and a multi-prefix attacker can consume different IPv6 buckets.
