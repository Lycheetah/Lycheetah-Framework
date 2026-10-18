# Failure Museum v0.4 — Authority Is Not a Verbatim Quote

Continuation of v0.2 and v0.3 Failure Museums. Tests include intentionally fictional, author-designed cases. Each observation is limited to its demonstrated boundary.

## FM-HYB-012 — Authentic quote, wrong authority

A source contains `EXAMPLE ONLY: Refunds allowed within 60 days.` A model that emits `window_days=60` with quote `Refunds allowed within 60 days.` passes lexical matching. **New behavior:** a trusted clause registry that only authorizes `Refunds allowed within 14 days.` rejects the example at the staging boundary. **Limitation:** whoever creates the registry can authorize the wrong clause. No automatic publisher/current-authority determination is shown.

## FM-HYB-013 — Authenticated sentence ≠ correct field or scope

A source also contains `Loyalty members earn 21 points per order.` A model can use the authentic number `21` for `refunds.window_days`, or re-label an in-store refund window as an online policy. Both violate the registered subject/predicate/scope contract and are rejected. **Limitation:** the accepted contract scope is operator-supplied, not independently inferred from the sentence.

## FM-HYB-014 — Semantic validator swap after staging

A caller could accidentally replace `gateway.semantic_validator` with `lambda _: True` after a valid stage. v0.4 detects the changed validator owner immediately before commit and blocks the admission. **Limitation:** trusted-process code can still bypass `ContractedHybridPipeline` and call lower-level methods. No hostile-code containment exists.

## FM-HYB-015 — Same-body, changed-source identity

A staged claim originally tied to `urn:fictional:shop-A` could have its gateway source registry replaced with a different URI while preserving the same body digest. v0.3's `commit_one()` only rechecked digest. v0.4's strict pipeline compares the **whole registered SourceDocument** against its pinned source snapshot at commit. **Limitation:** a malicious, privileged application can modify the ledger implementation or source objects.

## FM-HYB-016 — The apparent 100% is circular

The 33 author-created cases are labelled by conformance with nine authorized examples of the exact contracts the gate implements. v0.4 matches the labels on all 33; the lexical baseline wrongly admits 21 of 24 deliberately unauthorized proposals. This is a regression study, **not independent semantic accuracy**, true generalization, model extraction success, or proof of commercial effectiveness. Preserving this distinction is essential.

## FM-HYB-017 — Known false-abstention from narrow grammar

`For returns, customers get a fortnight to ask for their money back.` plausibly expresses a refund policy but cannot be parsed by the exact `refund_days_v1` grammar. The gate conservatively refuses to authorize it. Expanding natural-language coverage without undoing the evidence boundary is the next open research problem.

## FM-HYB-018 — No genuine CASCADE execution yet

The repository source for canonical CASCADE was inspected previously; its domain/paradigm contradiction proxy and evidence thresholds are not sufficient semantic validation. v0.4 ships an optional smoke script that imports original `CascadeEngine` and `KnowledgeBlock` when the Lycheetah repository is checked out locally. That script has not run in this environment; the default 71 tests still exercise a stub engine only.
