# v4.7 vs v4.8 — Hierarchical IPv6 Quota Differential

Configuration: global active maximum 8, per-leaf maximum 1, rate budget 100, leaf prefix `/64`; v4.8 aggregate prefix `/56`, aggregate active maximum 2.

| Scenario | Preserved v4.7 baseline | v4.8 hierarchical mode |
|---|---|---|
| First `/64` inside `2001:db8:1234:5600::/56` | Allowed | Allowed |
| Second distinct `/64` in same `/56` | Allowed | Allowed |
| Third distinct `/64` in same `/56` | Allowed | Denied: `ipv6-aggregate-connection-limit` |
| A peer in `2001:db8:1234:5700::/56` | Allowed | Allowed in independent aggregate bucket |
| IPv4 / IPv4-mapped IPv6 identities | Same normalized `/32` bucket | Same normalized `/32` bucket; no IPv6 aggregate applied |

The script `differential_probe_v4.8.py` runs the pair against two temporary SQLite databases and asserts the expected delta. This demonstrates the accounting behavior of the local reference models; it does not quantify real-world attack reduction or fairness impact.
