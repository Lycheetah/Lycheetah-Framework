# Failure Museum v0.3 — preserve what the test found

This supplements, and does not replace, `FAILURE_MUSEUM_v0.2.md`.

### FM-HYB-006 — substring evidence loophole

**Observed during v0.3 tests:** A proposed `window_days=1` initially passed lexical anchoring because `1` appeared inside the source's **14**. A unit test failed, correctly exposing the bug. The neural adapter now requires a whole lexical value using token boundaries. **Limit:** That still does not establish semantic relation; 21 loyalty points vs 21 refund days still requires the separate domain validator. This stricter lexical check applies to the **new neural adapter**, not retroactively to all `core.py` ingestion paths.

### FM-HYB-007 — model-controlled effective dates

A model can attach a plausible valid_from to an authentic statement, even when the source did not specify the effective date. New `ExtractionTarget.effective_from` / `effective_until` options let the trusted operator pin the expected effective interval; a conflicting model interval is rejected. **Limit:** When no operator interval is supplied the model can still suggest a date; independent review is mandatory, and date provenance is not established automatically.

### FM-HYB-008 — structured output is not truth

JSON-schema constrained outputs reduce invalid payloads. They do not establish factual correctness, refuse all prompt injection, or detect omissions. The adapter rejects undeclared fields such as `reviewer_approved`, attempts to switch tenants/scope, nonexistent evidence quotes, and invalid datetimes. Tests used fixture-generated responses; **no live model adversarial trial has occurred**.

### FM-HYB-009 — CASCADE proxy does not grant authority

Canonical CASCADE's historical symbolic `same-domain/different-paradigm` contradiction heuristic is not independently calibrated to customer policy revisions. New bridge restricts inputs to a time-and-scope-filtered ledger snapshot and refuses missing evidence weights. Its test engine is a stub, not the canonical CASCADE implementation. CASCADE diagnostics are not permitted to override `ABSTAIN_CONFLICT` or to revise the ledger.

### FM-HYB-010 — no authenticated review or network containment

`reviewer_approved=True` is a caller claim, not a signature. An attacker controlling the trusted caller could approve an unsupported claim. URL restrictions, response limits, and no-redirect logic are useful protective checks but not a full SSRF/egress policy or a data exfiltration guarantee. Third-party inference needs explicit consent, credentials discipline, isolation and cost limits.

### FM-HYB-011 — no strong baseline evaluation yet

The prior 22-case test remains a hand-authored synthetic ledger comparison. The additional 12 malformed/hostile output cases are unit-test fixtures. No independent temporal QA benchmark, production customer data, or model output distribution has been evaluated. The strongest research target is now **live extraction precision and recall at fixed review burden**, followed by rigorous VersionRAG-class comparisons.
