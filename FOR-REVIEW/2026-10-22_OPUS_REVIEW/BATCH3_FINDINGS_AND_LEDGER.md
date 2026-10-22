# Opus review — Batch 3: findings register and coverage ledger

Reviewer seat: Sol (Claude Opus 5.5, xhigh). Date: 2026-10-22.
Branch: `review/full-framework-2026-10-20` at `d7ae0ad` (**not** `master`).
Nothing in this batch is committed or pushed. All edits are working-tree only.

Scope: checklist item **RV04** (approval, identity, scope and revocation), traced from
the public entry points (`ActionGateway`, `PersistentActionGuard`, `FinalityGate`) to
the executor. B01b, B05 and B05b touch RV05 (durable workflow), but RV05 is **not**
marked reviewed here. RV01, RV05–RV09, RV13 and RV15–RV37 are still unreviewed.

Reproduction: `repro_batch3.py` in this folder prints one JSON object with a
`reproduced` flag per probe, and a benign control beside every defect probe. It runs
against the working tree and against a `git archive HEAD` export of the same commit.
B08 only proposes commands. It never dispatches one.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| B01 | — | RETRACTED: falsified at the guard | `action_guard.py` `record_result` |
| B01b | High (availability; fails closed) | FIXED in working tree | `action_guard.py` `record_result`, `_audit` |
| B02 | Medium | FIXED in working tree | `action_guard.py`, every mutator |
| B02b | Medium | FIXED in working tree | `action_guard.py` identifiers |
| B03 | Medium | FIXED in working tree | `action_guard.py` `issue_approval` |
| B04 | Low | FIXED in working tree | `action_guard.py` `claim_dispatch` |
| B05 | — | NOTE: by design, boundary is the workflow | raw guard anchor |
| B05b | Medium (deployment truth) | DOCUMENTED; the default → Mac (P10) | `gateway.py` `open_local`, `README.md` |
| B06 | Medium | FIXED in working tree (through B03) | gateway → guard |
| B07 | Low | FIXED in working tree | `gateway.py` `_declared_approver` |
| B08 | High (design) | OPEN, design decision for Mac (P8) | `gateway.py` `evaluate_policy`, `_tool_event` |
| B09 | — | FALSIFIED: the gateway is correct | `gateway.py` dispatch |
| B10 | Medium ([SCAFFOLD] module) | FIXED in working tree | `finality.py` `finalize` |
| B11–B14 | — | HELD: no defect | expiry, substitution, reuse, revocation |

### B01 — NaN in a result did not brick guard replay (RETRACTED, MEASURED)

The suspicion was that a NaN in `record_result` details would break journal replay. It
does not. Python's `json` returns the module's single `nan` object, and dict equality
holds by identity, so the replay comparison passes. The real defect sits one layer up
(B01b).

### B01b — One NaN from a provider blocked every later gateway action (MEASURED, FIXED)

On HEAD, a provider that returned `{"status": "success", "latency_ms": nan}` was handled
in three steps:

1. The guard journalled the NaN, because `record_result` used `json.dumps` without
   `allow_nan=False`.
2. The checkpoint authority's canonical JSON refused to sign that tail.
3. The gateway reported the effect as `UNKNOWN`. Every later, unrelated action then
   returned `BLOCKED:uncheckpointed_audit_tail_detected`.

Reconciliation is itself a checkpointed mutation, so there was no in-band recovery.
Repair needed hand surgery on the database. The failure is closed: nothing unsafe was
dispatched. But a value the provider controls denied service to the whole gateway.

Fix: `record_result` refuses non-finite or unencodable details with
`invalid_result_details` before anything is journalled (`action_guard.py:871`), and
`reconcile_effect` does the same with `invalid_reconciliation_evidence`
(`action_guard.py:911`). `_audit` now uses `allow_nan=False` as a backstop
(`action_guard.py:199`).

After the fix, the effect stays claimed and open for reconciliation. The gateway still
reports that one effect as `UNKNOWN:result_not_checkpointed_requires_reconciliation`,
which is the honest outcome, and the next action succeeds.

### B02 — A float timestamp bricked the ledger (MEASURED, FIXED)

`issue_approval(issued_at=100.5)` was accepted. SQLite stores it as REAL. Replay
compares `int(row["at"])`, so `verify_state_consistency` returned
`approval_table_event_mismatch`, and every later claim, for any effect, returned
`ledger_state_inconsistent`.

An integral float fails differently. `100.0` is stored as INTEGER `100`, but the event
hash was taken over `100.0`. That gives `event_hash_mismatch`, and the next claim
raised `RuntimeError: audit_chain_invalid`.

This is reachable only through the direct guard API. The gateway and the harness both
coerce with `int(time.time())` (`gateway.py:284`, `sovereign_harness.py:193`).

Fix: `_is_timestamp` (`action_guard.py:32`) accepts an `int` that is not a `bool`. It is
enforced in `issue_approval`, `prepare_effect`, `claim_dispatch`, `record_result` and
`reconcile_effect`, which return `invalid_timestamp`, and in `revoke_all`, which raises
`ValueError` because it returns a count.

### B02b — A non-string identity broke the hash chain (MEASURED, FIXED)

`issue_approval(actor=5)` was accepted. The TEXT column stores `"5"`, but the event hash
was taken over `5`, so `verify_audit_chain` returned `event_hash_mismatch`.

Fix: `_is_name` (`action_guard.py:37`) requires a non-empty `str` for the approval id,
actor, approver, scope and effect id.

### B03 / B06 — The executor could approve its own action (MEASURED, FIXED)

The `issue_approval` docstring promised "approval by a distinct approver identity", but
nothing checked it.

- Guard (B03): with the approver equal to the actor, the claim returned
  `dispatch_claimed`.
- Gateway (B06): a side-effecting `deploy.release` with `approver_id == actor == "agent"`
  returned `SUCCEEDED`. The control with no approver returned
  `DENIED:human_approval_required`.

Fix: one check, in the place both paths share. `issue_approval` refuses with
`approver_must_differ_from_actor` (`action_guard.py:611`), and the gateway surfaces it
as `BLOCKED` before any provider call.

**Limit, stated plainly:** identities are still declared strings. This closes
self-approval by the same name. A caller that controls both fields can still name any
other approver. That is the declared-versus-authenticated boundary RV04 asks about,
and it stays open as P9.

### B04 — An unencodable live action raised instead of refusing (MEASURED, FIXED)

`claim_dispatch(..., {"op": nan})` raised `ValueError` from `action_digest` inside the
transaction. The rollback left the effect `PREPARED` (fail-closed), but the caller got
an exception rather than a decision.

Fix: the live digest is computed before `BEGIN`, and the failure returns
`invalid_live_action` (`action_guard.py:763`). A later valid claim still succeeds.

### B05 — The raw guard is only as fresh as the anchor it is handed (MEASURED, NOTE)

A writer with access to the database truncated the audit tail and reset the effect row.
Handed an anchor taken before the first dispatch, `claim_dispatch` re-dispatched the
finished effect. Handed an anchor taken after the result, it returned
`audit_chain_invalid`.

This is by design. `CheckpointedWorkflow.claim_dispatch` passes the externally signed
anchor with `require_exact_audit_anchor=True`, so the boundary is the workflow, not the
raw guard. Recommendation, not applied: state this in the raw `claim_dispatch`
docstring.

### B05b — `open_local` puts the authority beside the ledger (MEASURED, DOCUMENTED)

Through the gateway, rolling back the ledger alone is caught: the replay returned
`BLOCKED:audit_history_invalid_against_external_checkpoint`, with one provider call.

Rolling back the ledger **and** deleting the newer `checkpoint_history` rows in the
co-located `authority/authority.sqlite3` re-ran the provider. There were two provider
calls, and the replay returned `SUCCEEDED:result_recorded`.

`CheckpointStore.store()` refuses rollback, but `latest()` reads whatever newest row
remains. The Ed25519 key is a 0600 PEM in the same directory. `checkpoint_authority.py`
describes the authority as designed to run out of process, but the README quickstart
and the CLI (`cli.py:224`, `~/.lycheetah/guard`) both use `open_local`.

Fix applied (documentation only): the `open_local` docstring and the README now say
which writer this protects against and which it does not, and they name the remedy
(`make_server` plus `CheckpointHTTPClient` in another process or host).

No local-only design defends against a writer who owns the whole directory. The remedy
is a separate trust domain, which is P10.

### B07 — An empty approver was approved at propose and denied at dispatch (MEASURED, FIXED)

`propose(..., approver_id="")` passed the `approver_id is None` check, was recorded as
`policy_auto_allow`, and was then denied at dispatch with `human_approval_required`. The
reserved marker `"policy_auto_allow"` passed as an approver behaved the same way. Both
failures were closed, but propose and dispatch disagreed.

Fix: one normaliser, `_declared_approver` (`gateway.py:51`). It treats a blank,
whitespace-only, non-string or reserved approver as absent, and propose
(`gateway.py:257`), policy evaluation (`gateway.py:243`) and dispatch (`gateway.py:418`)
all use it. The marker is now one constant, `AUTO_ALLOW_APPROVER` (`gateway.py:48`).

### B08 — The side-effect boundary is declared by the actor (MEASURED, OPEN → Mac)

`evaluate_policy` blocks two substrings: `"rm -rf /"` and the fork bomb. Measured with
propose only, never dispatched:

- `rm -r -f /`, `rm -fr /` and `find / -delete` were each **prepared without review**.
  Each became `tool: "generic_tool"` with `side_effect: False` and was auto-allowed.
- `rm -rf /tmp/build-cache` was **blocked**. That is a false positive: the substring
  `rm -rf /` matches the start of `/tmp`.

The real boundary is not the screen. It is `side_effect`, and the actor sets that in
the action it proposes (`gateway.py:242`, default `False`). The harness defaults the
same field to `True` (`sovereign_harness.py:794`). One concept has two defaults.

The CLI `guard run` sets `side_effect: True`, so CLI commands do reach review. An API
caller who leaves the field out does not. Dispatch of the prepared commands was not
run, so "they would execute" is DERIVED from the prepared state, not MEASURED.

This is not fixed in place. It changes what every integrator's actions do, so it is
proposal P8.

### B09 — An unencodable provider result is handled correctly (FALSIFIED, MEASURED)

A provider returned `{"handle": object()}`. The gateway called it once, left the last
event as `DISPATCH_CLAIMED` and returned
`UNKNOWN:result_not_checkpointed_requires_reconciliation`. There was no raise and no
retry. No defect.

### B10 — Finality accepted a PASS about a different subject (MEASURED, FIXED)

In `SUBJECT_STATUS` mode, the default, a requirement with no `required_subject_hash`
went through this sequence:

1. It was admitted on CI evidence for `commit-A`.
2. The store then held a PASS for `commit-B`.
3. `finalize` returned ready, with reason `fresh-evidence-and-current-policy`.

`_predicate_satisfied` checked the subject only when the requirement pinned one, and
`finalize` never compared against the admitted record's subject.

Fix: in `SUBJECT_STATUS`, the current record's `subject_hash` must equal the admitted
one, or the result routes to REVIEW with `evidence-subject-changed-after-admission`
(`finality.py:471`). The mode's meaning is now written on the enum: the record may be
re-issued, but it must stay about the admitted subject. `EXACT` mode is unchanged, and
a re-issued PASS for the same subject still finalizes. The existing test
`test_new_equivalent_subject_status_receipt_remains_usable` passes.

Behaviour change for Mac: a caller who wanted "any subject" semantics now gets REVIEW.
If that is ever wanted, it should be an explicit new mode, not the default.

### B11–B14 — What held (MEASURED on HEAD and on the tree)

| Probe | Result |
|-------|--------|
| B11 expiry | Prepare before issuance → `not_yet_valid`. Prepare at expiry → `expired`. Claim at expiry → `expired`. Inside the window → `dispatch_claimed`. The window is half-open, `[issued_at, expires_at)`. |
| B12 substitution | Actor → `actor_mismatch`. Scope → `scope_mismatch`. Action at prepare → `action_mismatch`. Live action at claim → `live_state_mismatch`. Control → `dispatch_claimed`. |
| B13 reuse | A second effect on one approval → `approval_already_consumed`. |
| B14 revocation | Revoked before claim → `revoked`. A new approval after revocation is issued normally. Revoked **after** claim: the effect is not recalled and its result still records. This is the post-dispatch limit, expected and stated here, not a defect. |

## Notes

- `canonical_action` already refused NaN on HEAD (`allow_nan=False`). That is why B04
  raised rather than journalled.
- Delegation: neither the guard nor the gateway has a delegation construct. The
  harness permit (`authority_id`) was reviewed in Batch 2 (F13). There is nothing
  further to probe here.
- The gateway module docstring already says approval identities are caller-supplied
  metadata that it does not authenticate. B03/B06 made the code honour the narrower
  promise the guard's docstring made.

## Proposals for Mac (none applied)

- **P8 — One side-effect classifier.** The gateway and harness would share a single
  function.
  - An integrator-owned tool registry, not the actor, classifies each tool.
  - Unknown tools and any action that carries `command` default to side-effecting.
  - The substring screen stays, but is labelled a tripwire, not a boundary. It should
    match `/` as a whole argument, which fixes the `/tmp` false positive.
  - This changes the default for every API caller, so it is your call.
- **P9 — Authenticated approvals.** An approval would carry a signature from a key the
  gateway trusts, not a declared name. A signed-approval path exists in
  `papers/ai-futures/hybrid-gateway/v1.2` (`issue_approval(batch, plan, key_id,
  secret)`). It was seen at call sites only and has not been reviewed. Whether to adapt
  it is a design decision.
- **P10 — The authority's trust domain.** Options:
  - (a) keep `open_local` as is, now documented;
  - (b) `open_local` and the CLI warn when the authority shares the ledger's directory;
  - (c) the CLI starts or expects a separate authority process.
  - (a) is applied. (b) and (c) are yours.

## Tests added

`tests/test_action_guard_identity_and_time.py`: 19 tests after parametrisation.

- Non-integer time is refused before it reaches the journal: 100.5, 100.0, `True` and
  `"100"`.
- Every mutator refuses a float time, with integer controls passing in the same test.
- Identifiers must be non-empty strings, for each of four fields.
- Self-approval is refused, and a distinct approver passes.
- An unencodable live action is a refusal, not a crash, and a later claim succeeds.
- A non-finite result is refused and the effect stays open.
- The gateway refuses self-approval, with a distinct approver succeeding.
- The gateway treats a blank, whitespace or reserved approver as none.
- One NaN result no longer blocks later gateway actions.
- Finality stays bound to the admitted subject, with a same-subject control.

**Witnessed against HEAD:** with the file copied into the HEAD export, 18 failed and 1
passed. The one that passed is the same-subject finality control, which must pass on
both. On the working tree, all 19 passed.

## Verification (MEASURED)

- Focused assurance, gateway, harness, handoff and MCP-guard tests, 24 files: **407
  passed, 1 skipped**.
- `repro_batch3.py` on the working tree:
  - B05 and B05b reproduce by design and are documented.
  - B08 reproduces and is open as P8.
  - Every other probe and every control does not reproduce.
- `repro_batch3.py` on the HEAD export: B01b, B02 (both forms), B02b, B03, B04, B05,
  B05b, B06, B07, B08 and B10 reproduce. B01, B09 and B11–B14 do not.
- Full suite on the Batch 3 tree: result line below.

**DID NOT COMPLETE.** The full run hit its 900 s timeout just after 90% (`exit 124`), and the Batch 4 edits landed in the tree while it ran, so it witnesses neither batch. The full run of the combined Batch 3 + 4 tree is recorded in `BATCH4_FINDINGS_AND_LEDGER.md`.

## Coverage ledger (Batch 3)

| RV04 dimension | Evidence | Verdict |
|----------------|----------|---------|
| Action and artifact binding | B12 probes; `claim_dispatch` digest compare read | HELD |
| Actor and approver separation | B03, B06 | FIXED |
| Delegation | No construct in guard or gateway; harness permit in Batch 2 | N/A here |
| Expiry | B11 | HELD |
| Replay | B05, B05b, B13 | B13 HELD; B05 by design; B05b documented, P10 |
| Cross-scope substitution | B12 | HELD |
| Approval authentication | Read: identities are declared strings | OPEN, P9 |
| Revocation timing | B14 | HELD; the post-dispatch limit is stated |
| Post-dispatch limits | B01b, B09, B14 | B01b FIXED; B09 FALSIFIED |
| Input admission (time, identity, encoding) | B02, B02b, B04, B07 | FIXED |
| Finality subject binding | B10 | FIXED |
| Side-effect classification | B08 | OPEN, P8 |

**Read in full this batch:**

- `lycheetah/assurance/action_guard.py`: 947 lines, before the fix
- `checkpointed_workflow.py`: 234 lines
- `checkpoint_authority.py`: 530 lines
- `finality.py`: 530 lines

**Read in part:**

- `gateway.py`, lines 1–470: propose, dispatch, policy, `open_local`
- the README quickstart
- `cli.py`, lines 224–250 and 622–640
- `sovereign_harness.py`, lines 193, 794, 968 and 1025

**Not reviewed in this batch:**

- `policy.py` and `receipt.py` (RV06)
- crash ordering and the dirty tail (RV05)
- the HTTP authority's network path, which was read but not probed (RV05)
- compaction (RV07), the codec (RV08) and the evidence bundle (RV09)

RV04 is reviewed at the guard, gateway and finality boundary. It is not closed while
P8 and P9 are open.

## Changed paths (Batch 3, working tree only)

- `lycheetah/assurance/action_guard.py`
- `lycheetah/assurance/gateway.py`
- `lycheetah/assurance/finality.py`
- `README.md` (one paragraph on `open_local`)
- `tests/test_action_guard_identity_and_time.py` (new)
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch3.py` (new)
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH2_FINDINGS_AND_LEDGER.md` (the suite result line)
- this file
