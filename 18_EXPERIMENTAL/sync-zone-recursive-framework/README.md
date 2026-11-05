# Sync Zone — bounded recursive integration (experimental)

**EXPERIMENTAL / `[SCAFFOLD]` · 2026-11-06 · PROPOSED, awaiting Mac's ratification.**
Lycheetah Framework and the Sync Zone: **Mackenzie Conor James Clark**. Research brief:
Cassian (forge packet, 2026-11-06). Archaeology, contract, code and tests: a Claude Code cloud
session working for Mac. Default claim status in this folder is `[CONJECTURE]` (see
`../README.md`) except where a line names a run.

> **Recursive improvement without recursive sovereignty.**

## What it is, in one paragraph

The Sync Zone already exists: [`lycheetah-sync-zone`](https://github.com/Lycheetah/lycheetah-sync-zone)
is a workshop where AI seats build, dispute and hand work to each other under Mac's charter.
Each round inherits the last. What it lacks is a **cycle contract**: a record that binds each
candidate, test, review and decision to exact digests, works out how independent each review
really was, refuses to let authority or budgets grow down a lineage, keeps every failure and
open objection, and lets nothing become canonical until Mac ratifies it. This folder is that
contract, a standard-library validator for it, an append-only ledger, and tests that try to break it.

## Try it

```sh
python3 -m pytest -q tests/test_sync_zone_cycle.py          # from the repository root
cd 18_EXPERIMENTAL/sync-zone-recursive-framework/experiments
python3 -B retrospective_1100.py                             # real Sync Zone events, scored
python3 -B session_cycle.py                                  # this forge, as cycle SZ-0001
```

## The thirteen questions (packet "success criteria")

| # | Question | Answer | Where |
|---|---|---|---|
| 1 | What exactly is Sync Zone? | A practice that exists (the workshop) plus, here, a contract for its cycles. Not an autonomous self-improving system. | above; [INTEGRATION_MAP](INTEGRATION_MAP.md) |
| 2 | What does it reuse? | ActionGateway for effects, handoff/compaction boundaries, finality's freshness idea, Git, pytest, the Failure Museum and disputes culture, the role contract. Rejects Chorus and consensus as reviewers. | [INTEGRATION_MAP](INTEGRATION_MAP.md) |
| 3 | What does it add? | Digest-bound evidence and reviews for *development* work; computed reviewer independence; lineage rules (authority, budget, failures, dissent, ruleset); caveat survival in handoffs; a hash-chained ledger. | [PROTOCOL](PROTOCOL.md) §2–9 |
| 4 | Where is the authority boundary? | One named human principal ratifies; carried authority ⊆ held ⊆ parent's; external effects need a grant and a gateway receipt. | PROTOCOL §5, §7, §8 |
| 5 | What is recursive, exactly? | The parent's durable revision, failures and open dissent become the child's starting state. Nothing else. | PROTOCOL §1 |
| 6 | What can it never ratify itself? | Its own rules, budgets, authority, test deletions, and any promotion at all. | PROTOCOL §6 |
| 7 | How is provenance retained? | Runs, digests, baseline, contract digests in each record; hash-chained ledger; Git for revisions. | `sync_zone/ledger.py`, `gitbind.py` |
| 8 | How are failures and dissent retained? | Byte-identical across the lineage and across ledger amendments; open dissent carried and named in every handoff. | PROTOCOL §7–9; tests `test_failure_*`, `test_*dissent*` |
| 9 | How does the loop stop? | Every cycle records one of nine stop reasons; depth/run budgets cannot grow; no-change must stop as CONVERGENCE; PROPOSED stops on AUTHORITY. | PROTOCOL §2, §8 |
| 10 | What falsifies the benefit? | A matched comparison where ordinary Git + tests + review loses no more caveats, catches no fewer self-certifications and costs less. Not yet run. | [CLAIMS_AND_LIMITS](CLAIMS_AND_LIMITS.md) |
| 11 | What code exists and what was tested? | ~900 lines stdlib Python; 66 author-written tests; 8 mutation probes all caught; no regression in the full suite. | [SYNC_ZONE_PROGRESS](SYNC_ZONE_PROGRESS.md) |
| 12 | What remains only proposed? | Identity authentication, external anchoring of the ledger head, an orchestrator, any comparator experiment, promotion into `lycheetah/`. | [SYNC_ZONE_TASKS.json](SYNC_ZONE_TASKS.json) |
| 13 | What should Mac review next? | The decisions below. | below |

## Decision memo for Mac

**Recommendation: continue as an experimental runtime, adopted first as a protocol for the
workshop's disputes and round handoffs. Do not promote into the package yet.**

| Option | Verdict | Why |
|---|---|---|
| Abandon as redundant | No | Two live failures in the workshop (SZF-02 self-settled dispute, SZF-04 dropped caveat) are exactly what the contract catches and what nothing else in either repository checks. |
| Protocol only | Partly | The record format alone would have caught SZF-04 if seats filled it in. |
| **Experimental runtime** | **Yes** | The validator is cheap, deterministic and tested; it can run in the workshop the way `zone-check` does. |
| Promote into `lycheetah/` | Not yet | The packet's own promotion criteria are unmet: no comparator experiment, no outside review. |

**Decisions only you can make:**

1. Ratify, amend or reject this protocol (`sz-rules-v0.1`). This cycle is recorded as PROPOSED
   with one honest blocker: no review of it by a different model exists yet.
2. Whether a different seat (Caelorynth/Codex is the natural one) reviews this branch — that is
   what would lift the `NO_INDEPENDENT_REVIEW` blocker on SZ-0001.
3. Whether to invite a seat to open a dispute against dispute 1100's falsifier (SZF-02), and to
   ask the dossier's author to restore dispute 400's verdict beside its Brier number (SZF-04).
4. How this branch lands: this session could not push to the Framework (SZF-12).

## What this does not do

It does not authenticate anyone, it does not see circular reasoning, and a green record does
not mean the work is right. Read [CLAIMS_AND_LIMITS](CLAIMS_AND_LIMITS.md) before relying on it.

## Files

| File | Job |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | The rules (`sz-rules-v0.1`). Governance path. |
| [THREAT_MODEL.md](THREAT_MODEL.md) | T01–T20, scored enforced / partial / not covered |
| [CLAIMS_AND_LIMITS.md](CLAIMS_AND_LIMITS.md) | Supported, plausible, explicitly unsupported |
| [INTEGRATION_MAP.md](INTEGRATION_MAP.md) | Reuse / extend / reject, with evidence |
| [SYNC_ZONE_FINDINGS.md](SYNC_ZONE_FINDINGS.md) | Failures and rejected designs, append-only |
| [SYNC_ZONE_PROGRESS.md](SYNC_ZONE_PROGRESS.md) · [SYNC_ZONE_TASKS.json](SYNC_ZONE_TASKS.json) | Session state for the next agent |
| `sync_zone/` | `validator.py`, `ledger.py`, `gitbind.py`, `canonical.py` — governance path |
| `experiments/` | `retrospective_1100.py`, `session_cycle.py` |
| `records/` | Generated reports and the SZ-0001 ledger |
