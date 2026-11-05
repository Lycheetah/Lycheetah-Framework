# Sync Zone cycle protocol — v0.1 (ruleset `sz-rules-v0.1`)

**Status:** `[SCAFFOLD]`. Implemented by `sync_zone/validator.py` and `sync_zone/ledger.py`.
Changing this file or `sync_zone/` is a **meta-governance change** (see §6): the validator
treats those paths as governing rules.

Source brief: Cassian's forge packet for Mac (2026-11-06). Owner and principal: Mackenzie
Conor James Clark. This protocol is a proposal until Mac ratifies it.

## 1. What is recursive

The durable state a cycle inherits is its parent's record: baseline, authority, failures,
open dissent and handoff. A cycle produces candidates, binds evidence and reviews to their
exact digests, and stops. If the principal accepts, the next cycle starts from the accepted
durable revision and inherits the (grown) failure list and the still-open dissent.

**That is all that recurses.** Authority does not grow, budgets do not grow, the ruleset does
not change itself, and nothing becomes canonical without the principal.

## 2. The cycle record

One JSON object, `schema_version: "sync-zone-cycle-v0.1"`:

| Field | Holds | Rule |
|---|---|---|
| `cycle_id`, `parent_cycle_id`, `depth` | lineage | depth = parent depth + 1 |
| `anchor` | baseline revision (full git id), `ruleset_id`, principal, governing contract digests, authority `{grants, expires_at, revoked}`, budget `{max_depth, max_runs}`, task | immutable once the cycle is in the ledger |
| `runs` | each agent/tool/human run: role, provider, model, context digest, declared independence, `observed_by` | metadata, never chain-of-thought |
| `candidates` | artifacts `[{path, sha256 \| null}]`, digest over them, producing run, baseline, `supersedes`, `meta_governance`, `effects` | digest must match artifacts |
| `evidence` | kind (`STATIC_CHECK` … `NOT_RUN`), producing run, target candidate **and digest**, revision, command, outcome, `valid_until` | counts only for the exact digest, while fresh |
| `reviews` | reviewer run, target digest, findings, `modified_candidate` | a reviewer that edits becomes a producer |
| `dissent` | by, severity, text, `OPEN / ADDRESSED / OVERRULED` | only the principal overrules |
| `failures` | `{id, text, superseded_by?}` | append-only, byte-identical across the lineage |
| `stop` | one of AUTHORITY, EVIDENCE, SAFETY, REGRESSION, BUDGET, CONVERGENCE, CONFLICT, COMPLETION, EXTERNAL_DEPENDENCY | every cycle says why it stopped |
| `ratification` | `PROPOSED / REJECTED / PARTIAL / ACCEPTED / BLOCKED / SUPERSEDED`, by, `by_kind`, candidate digest, optional `meta_governance_ack` | §5 |
| `handoff` | durable revision, carried authority, next actions, unresolved ids, references | §7 |

## 3. Evidence ladder

Kinds are not interchangeable. `MODEL_REVIEW` never becomes `INDEPENDENT_EXTERNAL_REVIEW`;
`HUMAN_REVIEW` and `INDEPENDENT_EXTERNAL_REVIEW` may only be produced by a run whose role is
`human`. Acceptance requires at least one fresh `STATIC_CHECK`, `UNIT_TEST` or `INTEGRATION_TEST`
**PASS bound to the ratified digest** and no bound FAIL.

## 4. Independence is computed, not declared

For each review, effective independence = the weaker of what the reviewer declares and what
the metadata allows:

`same_run` < `same_model_same_context` < `same_model_fresh_context` < `different_model` < `human`

A claim above what metadata allows is `FALSE_INDEPENDENCE`. Acceptance needs at least one
review of the exact digest at `same_model_fresh_context` or above (policy-configurable — but
configuring it is a meta change). Reviews that share a context digest are reported as
`SHARED_REVIEW_CONTEXT` (correlated) even across different models. `observed_by:
self_reported` is the honest default; the protocol does not authenticate any of it.

## 5. Ratification

`ACCEPTED` or `PARTIAL` requires: `by == anchor.principal`, `by_kind == "human"`, a
timestamp, the exact candidate digest, and **no blocker**. Blockers include: no bound PASS,
bound FAIL, expired evidence, no independent review, open CRITICAL/HIGH dissent or review
finding, expired or revoked authority, missing grant, external effect without a SUCCEEDED
`ACTION_RECEIPT`, an `UNKNOWN` effect, an unratified meta change, unchanged candidate
(convergence). A record that says ACCEPTED while any blocker stands is invalid
(`PROMOTED_WITH_BLOCKER`, CRITICAL).

## 6. Constitutional firewall

A candidate is a meta-governance change if it touches a governance path (`sync_zone/`,
`PROTOCOL.md`, `AGENTS.md`, `CLAUDE.md`, `28_DEFENSE/FAILURE_MUSEUM.md`,
`lycheetah/assurance/policy.py`) or deletes a file under `tests/`. Then:

1. It must declare `meta_governance: true` (else `UNDECLARED_META_CHANGE`).
2. It is judged under the cycle's **anchored** ruleset — the old rules (`RULESET_MISMATCH` if not).
3. Promotion needs a separate `meta_governance_ack` from the principal naming
   `ruleset_before` (= anchored), `ruleset_after`, and a separate review.
4. `ruleset_after == ruleset_before` is `SELF_JUDGED_RULE_CHANGE`.
5. A child may run under a new ruleset only if its parent ACCEPTED that exact change.

> No recursive component can lower the barrier that governs its own promotion in the same cycle.

## 7. Handoff

Carried authority ⊆ held authority (`AUTHORITY_CREEP_IN_HANDOFF`). Every open CRITICAL/HIGH
dissent or review finding id appears in `handoff.unresolved` (`CAVEAT_DROPPED_FROM_HANDOFF`).
A promoted cycle names an exact durable revision. References carry digests; with a repository
root the validator checks they exist and match.

## 8. Lineage rules (parent supplied)

Child grants ⊆ parent grants; child expiry ≤ parent expiry; same principal; budgets never
grow; depth over `max_depth` must stop with BUDGET; parent failures survive byte-identical;
parent open dissent is carried; a child of an ACCEPTED parent starts from its durable revision.

## 9. Ledger

`CycleLedger` stores records as hash-chained JSON lines. It validates before appending and
refuses: any CRITICAL/HIGH finding; a changed baseline on an amendment; removed or reworded
failures; removed or in-place-rewritten candidates; reopening a ratified cycle; a second
promotion from the same baseline touching the same paths. `verify()` names the first broken
line. The head hash is not anchored anywhere external yet.

## 10. When not to use it

For a small change by one agent with tests and a human reading the diff, ordinary Git review
is enough — and cheaper. Use a cycle record when work crosses sessions or seats, when a
review's independence matters, when a caveat must survive a handoff, or when a rule is being
changed.
