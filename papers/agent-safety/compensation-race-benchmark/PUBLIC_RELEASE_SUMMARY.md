# Public release summary — Compensation Race Benchmark v0.1

## One-sentence result

A repair authorization based on an earlier snapshot can become stale before execution; revalidating every repair target at the same atomic commit point as the restoration prevents the benchmarked overwrite and partial-repair failures.

## Evidence

Frozen deterministic stress, 1,000 rounds per case:

| Mechanism | Observed result |
|---|---:|
| precheck then write | 1,000/1,000 overwrote a legitimate post-permit update |
| sequential per-item compare-and-set | 1,000/1,000 left a partial repair in the stale-target fixture |
| atomic commit-fenced repair, stale target | 1,000/1,000 refused with zero writes |
| atomic commit-fenced repair, clean targets | 1,000/1,000 succeeded |
| atomic commit-fenced partial repairs | 0/1,000 |

## Evidence status

- Implemented: yes.
- Reproducible locally: yes.
- Uses real SQLite transactions: yes.
- Purpose-built deterministic fixtures: yes.
- Real external provider/database benchmark: no.
- Production deployment: no.
- Formal proof: no.
- Novelty claim: no.

## Public/private boundary

This release deliberately omits the private Lycheetah mechanisms for causal attribution, cross-witness equality, repair-set derivation, witness-independence cuts, and independent recovery legality. It publishes only the general commit-time race and a conventional transactional mitigation.
