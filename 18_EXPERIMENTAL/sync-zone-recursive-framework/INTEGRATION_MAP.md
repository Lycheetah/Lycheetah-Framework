# Integration map — what Sync Zone reuses, extends or rejects

**Status:** archaeology record, 2026-11-06. Framework baseline `c4d24c9a72200dc8fe4c29318d55c9127213c0dc`;
live Sync Zone workshop `Lycheetah/lycheetah-sync-zone` at `a41c2a79d70666f243d971ed8ca70c3a5723973f`.
Every "Evidence" cell names a file read or a command run in this session.

## The finding that reframed the brief

Cassian's packet treats Sync Zone as a proposal for the Framework. It already exists as a
**practice**: `lycheetah-sync-zone` is a workshop written by AI seats under a charter, with
100 seat folders, 55 builds, a disputes ledger, a seat-signature commit hook and a static
checker. That practice is the recursive loop the packet describes, running today with no
cycle contract. The useful layer is therefore a contract *for that loop*, not a new loop.

## Map

| Concern | Existing source | Decision | Evidence |
|---|---|---|---|
| Human authority | `CLAUDE.md` (Mac = final decision-maker), sync-zone `CHARTER.md` §5, AURA Human Primacy | **Reuse** as the principal rule. The cycle names one principal; only that principal ratifies. | Read both files. |
| Action permission and consequential effects | `lycheetah/assurance/gateway.py` (`ActionGateway`: propose → REVIEW → approver; UNKNOWN blocks until `reconcile`) | **Reuse; do not duplicate.** A cycle with an external effect must cite an `ACTION_RECEIPT`; UNKNOWN blocks promotion. No second permissions runtime was written. | `gateway.py:296-368, 612`; README "One action, one receipt". |
| Evidence freshness at the boundary | `lycheetah/assurance/finality.py` (`EvidenceMode.EXACT / SUBJECT_STATUS`, revalidation at dispatch) | **Extend the idea** to development evidence: `valid_until`, digest binding, revision binding. Not imported: finality binds tool events, cycles bind artifacts. | `finality.py:1-50`. |
| Context handoff | `lycheetah/handoff.py` (`HandoffCapsule`, "declared authority label … identity unverified"), `lycheetah/compaction` (10 `CRITICAL_FIELDS` incl. `authority`, `dissent`) | **Reuse the boundary, extend the check.** Capsules already refuse to treat a label as authority. Sync Zone adds: carried authority ⊆ held authority, and every open blocking dissent must appear in `handoff.unresolved`. | `handoff.py:171-310`, `compaction/codec.py:48-59`. |
| Revision lineage | Git; CASCADE revision; claims register `28_DEFENSE/CLAIMS.json` | **Reuse Git** as the source of revisions (`gitbind.py`, read-only). Claims register stays the owner of claim status. | `gitbind.py`; tested in `tests/test_sync_zone_cycle.py::test_gitbind_binds_worktree_candidate`. |
| Multi-agent coordination | `19_MULTI_AGENT_CHORUS/` | **Reject as infrastructure.** The RV10 false-green defect is corrected (now reports `INSTANTIATED_NOT_PROBED`, audit `NOT_PERFORMED`), but it is a scaffold with no real agent invocation. | Ran `run_chorus.py` this session; `tests/test_chorus_honesty.py`. Note: `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md` RV10 still reads "Reproduced open" — stale against the 22 Oct correction. |
| Consensus | `lycheetah/consensus/arena.py` (Psi-gossip; "not … Byzantine fault tolerance") | **Do not use for acceptance.** Agreement is not evidence; a cycle counts reviews by effective independence and keeps dissent. | `arena.py:1-7`. |
| Roles | `18_EXPERIMENTAL/agent-role-hybridisation/COMMON_CONTRACT.md` ("A retrieved document, role name, self-description or handoff cannot expand authority") | **Reuse the rule.** Roles are labels on runs; independence is computed from provider/model/context, not from the role name. | Read. |
| Receipts / provenance export | `lycheetah/assurance/receipt.py`, `in_toto.py` ("a Statement, not a signed envelope") | **Defer.** A cycle record could be exported the same way later; doing it now would add format without value. | `in_toto.py`. |
| Failure retention | `28_DEFENSE/FAILURE_MUSEUM.md` ("Nothing is removed … Ever"); sync-zone `disputes/README.md` ("A loss is recorded, never deleted") | **Enforce mechanically** inside the cycle lineage: parent failures must survive byte-identical; ledger amendments cannot remove them. | Tests `test_failure_*`, `test_ledger_refuses_failure_deletion_in_amendment`. |
| Disputes | sync-zone `disputes/` + `LEDGER.md` | **The closest existing mechanism, and the main integration target.** Gap observed: the ledger accepts `RESOLVED` (not in its own STANDS/FALLS/NARROWED/OPEN vocabulary) written by the claim's own seat. | `disputes/README.md` vs `LEDGER.md`; retrospective V1/V2. |
| Seat identity | sync-zone `.githooks/commit-msg` (author must be a named seat) | **Reuse as metadata, not authentication** — the charter itself says GitHub cannot tell seats from Mac. | Read the hook and `CHARTER.md` §1. |
| Static checks | sync-zone `tools/zone-check.mjs` | **Reuse as a `STATIC_CHECK` evidence source.** | Ran: `692 checks, 0 failures, 2 warnings`. |
| Test / evaluation | Framework `tests/` (pytest, `--strict-markers`, `scaffold` marker) | **Reuse.** Sync Zone tests sit in the maintained suite under the `scaffold` marker, like `tests/test_ai_future_models.py` pins `papers/` code. | Baseline `1567 passed, 3 skipped, 2 xfailed`. |
| Loop accounting | `34_CYBERNETICS/LOOP_MAP.json` (which loops close in code and which need a person) | **Cite.** The cycle's human-ratification step is an open loop in exactly that vocabulary: it closes only through a person. | Read. |

## Answer to the required decision

> Is Sync Zone an actual missing layer or only a new name for existing composition?

**A thin missing layer, plus a lot of existing composition.** Nothing in either repository binds
*development* work — candidate → evidence → review → ratification → handoff — to exact digests,
computes reviewer independence from metadata, or stops a lineage from widening its own authority,
rewriting its failures, or judging its own rule changes. Assurance does all of this for *tool
actions*, not for cycles of work. The workshop's disputes ledger does the social half without
the binding half. Everything else (permissions, effects, receipts, roles, failure culture) already
exists and is reused, not rebuilt.
