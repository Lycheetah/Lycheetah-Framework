# Failure Museum — v0.7

1. **Old answer overwritten by latest-known baseline.** January valid-time query made after March returns the March-admitted 60-day candidate under the naive latest-known rule. The bitemporal ledger returns 14. This is a constructed fixture, not an independent benchmark.
2. **Unresolved admitted disagreement incorrectly treated as fact.** After competing 30- and 60-day claims, the naive baseline picks 60; the ledger abstains and cites both. This demonstrates a safety-oriented refusal *within the specified rules*, not semantic truth detection.
3. **Heuristic diagnostic depends on manually assigned weights.** Two synthetic weight profiles yield different simulated CASCADE event counts while the underlying evidence answer stays `ABSTAIN_CONFLICT`. The result diagnoses weight dependence, NOT measured calibration quality.
4. **Event hash alone hides in-process state mutation.** An injected adapter can alter `_by_key` without changing the event chain head. A new structural snapshot detects the mutation after normal callback completion, but **cannot prevent it or guarantee detection after every exception**.
5. **Pinned loader is a program execution boundary.** Matching a Git blob SHA proves bytes equal a selected blob. It does not make source safe to execute, authenticate the checkout's governance, or isolate malicious libraries. Only run code from a trusted local checkout.
6. **Canonical execution remains open.** We obtained the canonical file's reported blob SHA and inspected source through the connected GitHub account. We could not materialize it in this offline container, so only toy-source loader tests and declared test-double integration ran. **Do not describe this cycle as a successful canonical CASCADE runtime integration.**
7. **Self-authored test labels are not external validation.** Four hand-built cases agree with the ledger by design. Independent temporal query labels, unannotated source ambiguities, reviewer time, and real model omission/hallucination rates are outstanding.
8. **Privacy-minimised reports are not complete anonymization.** Aggregate dispositions and correlation of repeated query patterns may still expose operational metadata. The default public report strips raw content, values, original IDs and tenant names.

Every item is retained for the next agent. Do not delete previous v0.2–v0.6 failure registers.
