# CASCADE structural conformance benchmark v0.1

- **Fixture suite:** ANON-POLITICIAN-CASCADE-STRUCTURE-001 (version 0.1)
- **Cases:** 12/12 exact matches; 0 failures.
- **False positives vs declared traversal rule:** 0
- **False negatives vs declared traversal rule:** 0
- **Safety invariants:** PASS (statuses unchanged; no automatic status changes; review flags match reported queue).

## Scope and caveat

Researcher-authored expected sets derived from the written traversal rule; not independently adjudicated labels and not ground truth about real-world materiality.

This suite tests conformance to a declared software traversal rule. It does not test whether queued claims are substantively or politically material, whether evidence is true, or whether CASCADE improves on human review or a static evidence ledger. A second reviewer should inspect the expected sets before these fixtures are treated as an evaluation benchmark.

## Case results

| Case | Scenario | Expected affected | Actual affected | Result |
|---|---|---|---|---|
| SB-01 | Direct dependent | B | B | PASS |
| SB-02 | Transitive chain and unrelated node | B, C | B, C | PASS |
| SB-03 | Branching and convergent dependency | B, C, D | B, C, D | PASS |
| SB-04 | One-way contradiction link | B | B | PASS |
| SB-05 | Contradiction partner and its descendant | B, C | B, C | PASS |
| SB-06 | Closure through contradiction chain | B, C, D | B, C, D | PASS |
| SB-07 | Multiple-parent dependent | C | C | PASS |
| SB-08 | Unrelated claim remains out of queue | B | B | PASS |
| SB-09 | Cycle terminates | B | B | PASS |
| SB-10 | Single-node graph has empty review set | — | — | PASS |
| SB-11 | Normative root does not alter traversal semantics or auto-change status | E1, T1 | E1, T1 | PASS |
| SB-12 | Complex dependency and contradiction closure | H, P1, P2, T | H, P1, P2, T | PASS |
