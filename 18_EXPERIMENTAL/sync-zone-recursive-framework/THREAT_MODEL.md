# Threat model — coverage, honestly scored

Threat ids follow Cassian's packet (`03_THREAT_MODEL_FALSIFICATION_AND_EVALUATION.md`).
**Enforced** means a validator/ledger rule exists *and* a test in
`tests/test_sync_zone_cycle.py` fails when the rule is removed (mutation probes M1–M8 in
`SYNC_ZONE_FINDINGS.md`) or directly exercises it. **Partial** means part of the threat is
covered. **Not covered** means not addressed by this code.

| Id | Threat | Status | Mechanism |
|---|---|---|---|
| T01 | Baseline substitution | Enforced | `BASELINE_MISSING`, `BASELINE_MISMATCH`, ledger `BASELINE_MUTATED`, `BASELINE_NOT_PARENT_DURABLE`, `REBASED_CANDIDATE` blocker |
| T02 | Evidence substitution | Enforced | digest binding (`STALE_BINDING`), `EVIDENCE_REVISION_MISMATCH`, `CANDIDATE_DIGEST_MISMATCH`, `RATIFIED_WRONG_REVISION` |
| T03 | Reviewer mutation | Enforced | `REVIEWER_MUTATION_UNRECORDED`; an editing reviewer's review never counts for its own candidate; ledger `CANDIDATE_REWRITTEN` |
| T04 | Fake independence | Partial | `FALSE_INDEPENDENCE`, `DUPLICATE_ID`, `DUPLICATE_RUN_IDENTITY`, `NO_INDEPENDENT_REVIEW`. **Gap:** metadata is self-reported; a process can type a different provider name. |
| T05 | Consensus laundering | Enforced | open CRITICAL/HIGH dissent or finding blocks regardless of how many reviews agree; only the principal overrules; parent dissent carried |
| T06 | Authority creep | Enforced (within records) | `AUTHORITY_WIDENED`, `AUTHORITY_OUTLIVES_PARENT`, `AUTHORITY_CREEP_IN_HANDOFF`, `AUTHORITY_SCOPE`. Does not control what an agent's real tools can do — that is the environment's and ActionGateway's job. |
| T07 | Self-lowering threshold | Enforced | `RULESET_MISMATCH`, `UNDECLARED_META_CHANGE`, `META_CHANGE_NEEDS_SEPARATE_RATIFICATION`, `SELF_JUDGED_RULE_CHANGE`, `RULESET_CHANGED_WITHOUT_RATIFICATION` |
| T08 | Test deletion | Partial | deleting a file under `tests/` is a meta change; bound FAIL blocks. **Gap:** weakening a test without deleting it is invisible. |
| T09 | Failure erasure | Enforced | `FAILURE_ERASED`, `FAILURE_REWRITTEN` (lineage and ledger amendments), `CANDIDATE_ERASED` |
| T10 | Stale evidence | Enforced | `valid_until` → `EVIDENCE_EXPIRED`; `CONTRACT_CHANGED`; `HANDOFF_ARTIFACT_CHANGED` |
| T11 | Summary drift | Enforced for recorded caveats | `CAVEAT_DROPPED_FROM_HANDOFF`. Caught live: the 2026-11-06 dossier (retrospective H1). **Gap:** a caveat never recorded as dissent cannot be protected. |
| T12 | Prompt injection as authority | Partial | authority comes only from `anchor.authority` and the parent; no record text grants anything. Does not stop an agent from *acting* on injected text. |
| T13 | Unbounded recursion | Enforced | `BUDGET_MISSING`, `BUDGET_EXCEEDED`, `BUDGET_WIDENED`, `DEPTH_EXHAUSTED`, `STOP_MISSING`, `NO_CHANGE` |
| T14 | Approval fatigue | Not covered | Design note only: ratify per cycle, not per action. Unmeasured. |
| T15 | Consequential bypass | Partial | external effect needs grant + `ACTION_RECEIPT`. A record cannot prove the effect went through the gateway. |
| T16 | Unknown effect | Enforced (record level) | `EFFECT_UNKNOWN`; ActionGateway already blocks blind retry. |
| T17 | Claim inflation | Partial | `EVIDENCE_LABEL_INFLATION`, `FALSE_RATIFICATION`, evidence ladder. Prose outside the record is not checked. |
| T18 | Model monoculture | Partial | `SHARED_REVIEW_CONTEXT` (non-blocking). Shared training data across "different" models is invisible. |
| T19 | Secret persistence | Not covered | Records hold metadata and digests by design; nothing scans them. |
| T20 | Exit obstruction | Not covered by code | Nothing here retains data against the principal; deletion of the ledger file is always possible. |

## The failure the contract cannot see

Retrospective V3 (`experiments/retrospective_1100.py`): a simulation that types its
conclusion into its own formulas, with green tests and one different-model review that
reports nothing, passes every rule. **Circular evidence is a content defect; this is a
process contract.** Only a reviewer who reads the formula catches it — which is why the
protocol demands independent review but cannot certify that the review was good.
