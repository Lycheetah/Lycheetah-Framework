# Baseline Comparison v4.9

## Scenario

Configuration in both arms: global attempt budget 5/minute; one noisy peer sends 8 rapid attempts; an unrelated peer attempts afterward. Active leases are closed immediately so active concurrency does not confound this rate-bucket experiment.

| Outcome | Local v4.8 global-only baseline | v4.9 peer cap = 2 |
|---|---:|---:|
| Noisy peer attempts accepted | 5 | 2 |
| Noisy peer tier-specific denials | N/A | 6 |
| Unrelated peer admitted afterward | No | Yes |
| Approx global tokens after unrelated peer attempt | 0 | 2 (minor refill may appear in rounded snapshot) |

The machine-readable result is `differential_probe_v4.9.json`. The baseline is the preserved local v4.8 `shared_ingress_quota.py`, not a claim of byte-equivalence with GitHub.

## Interpretation

The new peer token bucket preserves a share of the global attempt budget under this narrow source-flood workload. It does not prove general network fairness: source IPs may be shared, spoofing/rotation can distribute attempts, and each accepted TCP flow still consumes work before this application-level code runs. The optional aggregate IPv6 cap extends the same concept across configured `/64` leaf buckets within a chosen parent prefix.
