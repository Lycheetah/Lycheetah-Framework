# Opus review — Batch 4: findings register and coverage ledger

Reviewer seat: Sol (Claude Opus 5.5, xhigh). Date: 2026-10-22.
Branch: `review/full-framework-2026-10-20` at `d7ae0ad` (**not** `master`).
Nothing in this batch is committed or pushed. All edits are working-tree only.

Scope: checklist item **RV05** (durable workflow and dispatch): crash ordering, retry,
reconciliation, reopen, and more than one writer on a ledger. The path traced runs from
`ActionGateway.execute` through `CheckpointedWorkflow` to `PersistentActionGuard` and
the `CheckpointStore`, plus the operator surface in `lycheetah/cli.py`.
RV01, RV06–RV09, RV13 and RV15–RV37 are still unreviewed.

Reproduction: `repro_batch4.py` in this folder prints one JSON object with a
`reproduced` flag per probe, and a benign control where one makes sense. It runs
against the working tree and against a `git archive HEAD` export of the same commit.
Executors only count calls. Nothing touches the OS.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| R01 | High (duplicate side effect) | FIXED in working tree | `action_guard.py` `prepare_effect` |
| R02 | High (no recovery path) | FIXED in working tree | `checkpointed_workflow.py`, `gateway.py`, `cli.py` |
| R03 | High (availability; fails closed) | OPEN, design decision for Mac (P11) | `checkpointed_workflow.py` `_trusted_checkpoint` |
| R04 | Medium (availability; fails closed) | FIXED in working tree | `action_guard.py`, `checkpointed_workflow.py` |
| R05 | — | HELD: no defect | `gateway.py` dispatch, explicit `{}` live action |
| R06 | — | HELD: no defect | `gateway.py` dispatch, second dispatch |
| R07 | High (same root as R01) | Redispatch HELD; same-action retry FIXED with R01 | claim → crash → reopen |

### R01 — Retrying an action whose outcome is unknown called the provider again (MEASURED, FIXED)

`README.md` said: "An uncertain or uncheckpointed result requires reconciliation before
retry." Nothing enforced it. The provider times out, so the effect is `UNKNOWN`. The
same action is then executed again. HEAD prepared a fresh approval and effect and called
the provider a second time (`retry SUCCEEDED`, provider calls 1). For a payment or a
deploy, that is the duplicate the README promised could not happen.

**HEAD hid this inside one second.** HEAD derived approval ids from action, actor and
the current second. A retry in the same second collided on `approval_id_exists`, so an
in-second probe looked safe. Across a second boundary the retry reached the provider:

| HEAD retry | Result |
|------------|--------|
| same second | `BLOCKED:approval_id_exists`, provider calls 0 |
| after 1.1 s | `SUCCEEDED:result_recorded`, provider calls 1 |

The working tree's random approval and effect ids, from an earlier fix in this
review, removed the collision. That made the duplicate deterministic.
**Landing constraint:** the random-id change must not land without this fix.
`repro_batch4.py` now sleeps 1.1 s before each retry, so HEAD reproduces every run.

Fix: `prepare_effect` refuses a new effect while an effect with the same `action_hash`
is `DISPATCHING` or `UNKNOWN`. The refusal is `prior_effect_unresolved`. It is audited
as `PREPARE_DENIED` and committed, and replay ignores that event like any other
denial. The gateway's BLOCKED result names the unresolved effect in `effect_id`, and
the CLI `run` output now prints it. That gives an operator the id to reconcile.
Control: a different action in the same state still succeeds.

### R02 — There was no checkpointed way to reconcile (MEASURED, FIXED)

`PersistentActionGuard.reconcile_effect` existed and had **zero callers**.
`CheckpointedWorkflow` and `ActionGateway` had no reconcile method, and the CLI had no
command. The only route was the raw guard. On HEAD that settled the effect
(`FAILED`) but left an uncheckpointed tail. The next action was
`BLOCKED:uncheckpointed_audit_tail_detected`, and reopening raised
`WorkflowBlocked:bootstrap_requires_synchronized_journal`. The documented recovery
step therefore bricked the ledger.

Fix:
- `CheckpointedWorkflow.reconcile_effect` mirrors `record_result`: it checks the
  trusted checkpoint, pins the write to that checkpoint's anchor, then publishes.
- `ActionGateway.reconcile(effect_id, outcome, evidence)` returns an `ExecutionResult`
  with `provider_called=False`. It returns `reconciled`, `DENIED` with the guard's
  reason, `BLOCKED` when the checkpoint is not trusted, or `UNKNOWN` /
  `reconciliation_not_checkpointed` when the publish fails.
- `lycheetah-guard reconcile EFFECT_ID --outcome success|failure --evidence JSON
  [--dir]` exits 0 only on `reconciled`.

After the fix, the effect settles, the journal stays synchronized, the ledger reopens,
and the same action can be prepared again.

### R03 — One failed publish after a local commit blocks the ledger forever (MEASURED, OPEN → P11)

The authority fails on the claim's publish. The gateway answers
`DENIED:checkpoint_unavailable` with 0 provider calls, which is correct. When the
authority comes back, every later action is
`BLOCKED:uncheckpointed_audit_tail_detected`, and reopening raises. HEAD and the tree
behave the same way. This is deliberate: `test_uncheckpointed_tail_blocks_dispatch`,
`test_failed_checkpoint_is_not_blessed_by_a_later_proposal` and
`test_restart_does_not_bootstrap_a_dirty_tail` pin "never publish previously
uncheckpointed history". So it is **not patched**. The problem is that nothing,
including an operator, can move the ledger forward. One transient network failure
ends the ledger's life. See P11.

### R04 — Two gateways on one ledger bricked it (MEASURED, FIXED)

Two `open_local` gateways on one directory is what two concurrent `lycheetah-guard
run` calls are. A holds its own per-instance `RLock` and B holds a different one.
B passed its checkpoint check, then A completed a whole checkpointed write. B then
wrote on top and published from its stale prior, and the store refused the batch with
a sequence gap (`checkpoint_unavailable`). From then on, every action was BLOCKED and
reopening raised. Run in sequence, the same two gateways are fine (control).

Fix: every guard mutation takes an optional `expected_audit_anchor`. Inside `BEGIN
IMMEDIATE`, `_refuse_stale` compares event count, last seq and root hash with the
anchor. On a mismatch it rolls back and refuses `audit_checkpoint_stale`.
`revoke_all` raises, and the workflow turns that into the same refusal. The workflow
now passes its trusted anchor on **every** mutation; before, only `claim_dispatch` was
pinned. On a stale refusal, `_run_checkpointed_mutation` publishes nothing, because
the events after its anchor belong to the other writer. That also removes a latent
copy of the bug: a stale `claim_dispatch` used to publish the other writer's events
too. After the fix, B gets `audit_checkpoint_stale`, B's retry succeeds, and the
ledger reopens.

### R05, R06, R07 — What held (MEASURED on HEAD and on the tree)

| Probe | Result |
|-------|--------|
| R05 explicit empty live action | `dispatch(current_action={})` → `DENIED:live_state_mismatch`, effect `CANCELLED`, provider calls 0. `{}` is not replaced by the approved action. |
| R06 duplicate dispatch | Second dispatch of one effect → `DENIED:effect_not_prepared`. Provider called exactly once. |
| R07 crash after claim | Claim checkpointed, process dies before the provider call. Reopen succeeds, the effect stays `DISPATCHING`, and redispatch → `DENIED:effect_not_prepared` with 0 calls. **But** on HEAD, executing the same action again ran the provider: the R01 defect. On the tree it is `BLOCKED:prior_effect_unresolved` until reconciled. |

## Notes

1. **`mutation_exception` is reported as `checkpoint_unavailable`** (Low, not fixed).
   An exception inside a guard mutation becomes `OperationReceipt(…, checkpointed=False)`,
   and the gateway reports it as a checkpoint outage. The decision is still fail-closed.
   Only the label is wrong.
2. **The per-instance lock is not a ledger lock.** `effect_session` serializes one
   gateway object. Across processes, the anchor pin (R04) is what now keeps one batch per
   checkpoint generation. DERIVED: there is a window between one writer's local commit and
   its publish. A second writer that checks in that window sees a tail and gets a
   transient `BLOCKED:uncheckpointed_audit_tail_detected`. That is retryable, not
   permanent, but the reason text is misleading. If the first writer dies inside that
   window, the tail is permanent, which is R03.
3. **`prior_effect_unresolved` is keyed on `action_hash` alone,** across actors and
   scopes. The provider effect is the same whoever asks, so this is deliberate. Mac can
   narrow it if a real deployment needs per-actor retry.
4. **Reconciliation evidence is declared, not verified.** The gateway records what the
   caller says the provider read showed. That is the same trust class as approver identity
   (P9). The ledger proves who settled what and when, not that the provider read was true.
5. **The raw guard keeps its old contract.** `expected_audit_anchor` defaults to `None`.
   Direct guard callers stay responsible for their own anchoring (B05, by design).
6. **The MCP server has no dispatch path.** `12_IMPLEMENTATIONS/applications/
   lycheetah_guard_mcp.py` does not import `ActionGateway`, so it needs no reconcile tool.
   (DERIVED from source search.)
7. **Revocation can now be refused as stale.** Under a concurrent writer, `revoke_all`
   returns `audit_checkpoint_stale` and must be retried. Before, it committed and then
   bricked the ledger on publish. That also stopped every action, but permanently. The
   caller sees `allowed=False` either way. Nothing in `lycheetah/` calls the workflow's
   `revoke_all` today.
8. **Assumptions.** One ledger directory on a local filesystem: SQLite WAL needs shared
   memory, and its documentation (from memory, not re-read this session) warns against
   network filesystems. The authority's trust domain is as stated in Batch 3 (B05b, P10).

## Proposal for Mac (not applied)

**P11 — Give an operator a reviewed way past a dirty tail.** Sol's stance: build
option (b). A ledger that one network blip kills permanently is not fail-closed
design. It is fail-dead, and it pushes operators to delete the directory, which
destroys the very history the checkpoint exists to protect.

- (a) Keep today's behaviour: permanent block, with recovery only by hand outside the
  tool.
- (b) **Recommended.** Add `lycheetah-guard adopt-tail --operator NAME --reason TEXT`.
  It verifies the hash chain and state replay, prints every uncheckpointed event, and
  requires that the tail extends the latest checkpoint exactly. It then appends a
  `TAIL_ADOPTED` event naming the operator, reason and adopted range, and publishes the
  whole range as one new generation. Every adoption stays visible in the history, so
  nothing is blessed silently. The three pinning tests stay true for automatic paths.
- (c) Retry the publish automatically on the next mutation. Rejected: that is exactly
  the silent blessing the existing tests forbid.

## Tests added

`tests/test_gateway_durable_dispatch.py` has 8 functions and 9 test items:

- Retry while `UNKNOWN` is refused, names the unresolved effect, and reaches the
  provider 0 times. A different action still succeeds.
- `gateway.reconcile` settles `failure` → `FAILED` and `success` → `SUCCEEDED`. The
  journal stays synchronized, the ledger reopens, and a later action succeeds.
- After a reconciled failure, the same action can be retried and succeeds once.
- Reconcile refuses an effect that already succeeded, and an unknown id
  (`missing_effect`). The journal stays synchronized.
- Crash after a checkpointed claim: reopen, the same-action retry is refused, reconcile
  works, and then the retry succeeds once.
- Two gateways on one ledger: the stale writer is refused `audit_checkpoint_stale`, its
  retry succeeds, the other writer still executes, and the ledger reopens.
- A stale revocation is refused without writing, the journal stays synchronized, and
  the retry revokes.
- CLI: `reconcile` exits 0 with `reconciled`, and repeating it exits 1 with `DENIED`.

## Verification (MEASURED)

`repro_batch4.py`, HEAD export (`lycheetah.__file__` confirmed under `head_export/`)
against the working tree:

| Probe | HEAD reproduced | Tree reproduced |
|-------|-----------------|-----------------|
| R01 retry while unknown | True (provider calls 1) | False (`prior_effect_unresolved`, 0) |
| R02 reconcile path | True (raw guard; later BLOCKED; reopen raises) | False (gateway; later SUCCEEDED; reopen opens) |
| R03 outage tail | True | True (by design, P11) |
| R04 two instances | True (`checkpoint_unavailable`, then BLOCKED; reopen raises) | False (`audit_checkpoint_stale`, later SUCCEEDED; reopen opens) |
| R04 sequential control | False | False |
| R05 empty live action | False | False |
| R06 duplicate dispatch | False | False |
| R07 crash after claim | True (retry calls 1) | False (retry BLOCKED, 0 calls) |

- **Planted failure:** `tests/test_gateway_durable_dispatch.py` copied into the HEAD
  export gives **9 failed**. Every item ran and failed at an assertion or a missing
  method; none was a collection error. On the tree, the file plus
  `test_gateway_boundaries.py`, `test_assurance_cli.py` and `test_entry_points.py`
  gives **48 passed**.
- **Focused assurance run:** the 23 guard, gateway, checkpoint, assurance, sovereign,
  finality and entry-point test files gave **339 passed, 1 skipped**. That run came
  before the last small change (naming the unresolved effect, plus the CLI test); the
  48-item run above covers that change.
- **Full suite:** did not complete. Run `bbmafc9on` (`pytest -v`, Batch 4 tree)
  reached 1,089 passed, 0 failed, 0 errors, 1 xfailed at 90%, then blocked for 25
  minutes on `tests/test_threads_fixes.py::test_visualizer_export_all_data_uses_timeseries_schema`,
  which opened a GTK matplotlib window on the desktop (Batch 5 finding S01). It was
  stopped by PID (exit 143); the last ~10% did not run. Batch 5 edits landed while it
  ran: in-process tests had already imported Batch 4 code, subprocess tests may have
  loaded Batch 5 code. The clean full run is recorded in the Batch 5 ledger.
- **Batch 3's full run did not complete.** It hit its 900 s timeout just after 90%
  (`exit 124`), and the Batch 4 edits landed while it ran. The full run above is on
  the combined Batch 3 + 4 tree and is verbose, so a stall names its test.

## Coverage ledger (Batch 4)

| RV05 dimension | Evidence | Verdict |
|----------------|----------|---------|
| Dirty tail blocks | R03; `test_uncheckpointed_tail_blocks_dispatch`, `test_failed_checkpoint_is_not_blessed_by_a_later_proposal` | HELD fail-closed; recovery OPEN, P11 |
| Reopen / bootstrap | Reopen in R02, R03, R04, R07; `test_restart_does_not_bootstrap_a_dirty_tail` | HELD; reopen after reconcile and after a race FIXED |
| Claim before dispatch | R07; `test_uncheckpointed_dispatch_claim_never_reaches_executor` | HELD |
| Live action at dispatch | R05; `test_explicit_empty_live_action_is_not_replaced_by_approved_action` | HELD |
| Current policy at dispatch | `test_newly_denied_tool_is_rechecked_before_dispatch` (read, passing) | HELD (existing test, no new probe) |
| Crash ordering | R07 | Redispatch HELD; same-action retry FIXED |
| Duplicate dispatch | R06 | HELD |
| Rollback / fork at the store | Batch 3 B05, B05b; `CheckpointStore.store` read (rollback, same-count fork, sequence gap) | Covered in Batch 3 |
| Post-effect `UNKNOWN` | R01, R02; `test_result_checkpoint_failure_reports_unknown_after_executor` | FIXED |
| More than one writer | R04 | FIXED; transient window in Note 2 |
| Operator recovery surface | CLI `reconcile`; `run` prints the effect id | NEW |
| Exception labelling | Note 1 | OPEN, Low |

## Changed paths (Batch 4, working tree only)

- `lycheetah/assurance/action_guard.py`: `_refuse_stale`; `expected_audit_anchor` on
  `issue_approval`, `prepare_effect`, `record_result`, `reconcile_effect`,
  `revoke_all`; `prior_effect_unresolved` in `prepare_effect`.
- `lycheetah/assurance/checkpointed_workflow.py`: `reconcile_effect`; an anchor on every
  mutation; no publish after a stale refusal; stale revocation becomes a refusal.
- `lycheetah/assurance/gateway.py`: `reconcile`; a prepare refusal names the unresolved
  effect.
- `lycheetah/cli.py`: `reconcile` subcommand; `run` prints the effect id on a
  non-success result.
- `README.md`: reconcile API, no automatic recovery from an uncheckpointed write, two
  processes on one directory.
- `tests/test_gateway_durable_dispatch.py` (new).
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch4.py` (new).
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH4_FINDINGS_AND_LEDGER.md` (this file).
