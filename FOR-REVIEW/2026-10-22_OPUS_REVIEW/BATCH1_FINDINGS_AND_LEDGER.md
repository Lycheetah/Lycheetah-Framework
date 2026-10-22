# Opus review — Batch 1: findings register and coverage ledger

Reviewer seat: Sol (Claude Opus 5.5, xhigh). Date: 2026-10-22.
Branch: `review/full-framework-2026-10-20` at `d7ae0ad` (**not** `master`).
Nothing in this batch is committed or pushed. All edits are working-tree only.

Scope: checklist items RV10, RV11, RV12, RV14 (the four concrete open defects),
plus whatever the baseline suite surfaced. RV01–RV09, RV13 and RV15–RV37 are
**not yet reviewed**. Nothing outside the ledger below is marked reviewed.

## Findings register

| ID | Item | Severity | Status | Where |
|----|------|----------|--------|-------|
| F01 | RV14 | High | FIXED in working tree | `12_IMPLEMENTATIONS/core/lamague_parser.py` |
| F02 | RV14 | Medium | OPEN, Mac's grammar decision | `03_LAMAGUE_L1/04_BNF_GRAMMAR.md`, parser `↯` handling |
| F03 | RV14 | Medium | OPEN, provenance | `FOR-REVIEW/2026-10-21_PROPOSALS/01_PARSER_SILENT_DROP_PATCH_PROPOSAL.md` |
| F04 | RV14 | Low | OPEN | parser `LEAF_TYPES` |
| F05 | RV10 | High | FIXED in working tree | `19_MULTI_AGENT_CHORUS/run_chorus.py` |
| F06 | RV11 | High | REPRODUCED, patch STAGED (frozen source) | `papers/agent-safety/frontier-controls/06_.../policy_evolution_gate.py` |
| F07 | RV12 | High | REPRODUCED, patch STAGED (frozen source) | `23_NZ_AI_GOVERNANCE/.../evaluation/aggregate_reviews.py` |
| F08 | suite | Low | FIXED in working tree | `19_MULTI_AGENT_CHORUS/README.md` |
| F09 | suite | Low | FIXED in working tree (Batch 2) | `34_CYBERNETICS/LOOP_MAP.json`, `docs/lamague-handover-report.json`, `docs/lamague-handover.html` |
| F10 | repo | Process | OPEN, Mac's decision | branch is not `master` |

### F01 — Text after `|` was silently accepted (MEASURED, FIXED)

Aetheron's uncommitted patch added a trailing-token check but stopped
filtering at the first `PIPE`, so everything after `|` was never validated:
`Ψ → Φ | @` was reported valid. Fix: split on `|`. Every segment is checked
for unknown symbols and must parse completely, and an empty constraint is an
error. Constraints are validated but not attached to the tree, because the
BNF has no production for `|` (see F02).

Tests added to `tests/test_lamague_parser.py`: `test_rejects_trailing_tokens`,
`test_collapse_example_parses_completely`, `test_text_after_pipe_is_validated`.
**Planted failure witnessed:** with the parser change stashed, all three fail
(3 failed, 21 passed). With the change applied, all pass.

### F02 — `↯` has two incompatible definitions (DERIVED, OPEN)

`04_BNF_GRAMMAR.md` defines `<dynamic> ::= "↑" | "↯"` (a postfix-style
dynamic), yet its own canonical example `Ψ ↯ Ao → Φ↑ → Ψ_inv` and the junction
form `condition ↯ [option_a], [option_b]` use `↯` as an infix operator. The patch
tokenizes `↯` as an OPERATOR. That makes the parser's DYNAMIC branch for `↯`
unreachable, so a standalone `↯` no longer parses. The grammar also has no
production for `|`. **Decision for Mac:** is `↯` an operator, a dynamic, or both
by position? Once ruled, the BNF and the parser should change together, and
proposal 02 (BNF) is the place for it.

### F03 — Proposal 01's approval and test receipt are not verifiable here (MEASURED)

The proposal says "[APPROVED & IMPLEMENTED] Approved by Mac 2026-10-21 09:30" and
"33/33 tests passed in creations/lamague_check". `creations/lamague_check` does
not exist in this repository, and the patch is uncommitted. Mac's approval can
only be confirmed by Mac. The test count belongs to a different suite and is not
evidence for this parser. The proposal's footer should say which suite produced
the count and where it lives.

### F04 — `LEAF_TYPES` lists `TokenType.FIELD` twice and appears unused (DERIVED)

Cosmetic. Either remove it or use it in `_parse_primary`.

### F05 — Chorus runner fabricated health and audit results (MEASURED, FIXED)

`health_check()` reported every agent `✅ ONLINE` / `operational: True` and
`all_constitutional` with no probe. `run_truth_audit()` returned
`framework_coherence: 1.0` and zero contradictions without reading a file. The
banner and registry said OPERATIONAL. Now: agents are reported
`INSTANTIATED_NOT_PROBED` or `MISSING`, `operational`/`all_constitutional` are
`None`, and the audit reports `NOT_PERFORMED` with `files_scanned: 0`,
`framework_coherence: None`, and the count of Aurora's built-in demo entries.
Banner and registry say SCAFFOLD. Witnessed by running
`python3 run_chorus.py --mode=audit`.

Test: `tests/test_chorus_honesty.py` (2 tests). They build the runner via
`__new__`, which skips the `.agent_state` mkdir side effect. The planted case is a
`None` agent, which the old code reported as online.

### F06 — Policy-evolution gate classifies a weakening as EQUIVALENT (MEASURED)

`group_map()` builds a dict keyed by `group_id`, so a repeated id keeps only the
last group, while `policy_formula()` ANDs every group. Reproduction
(`repro_batch1.py`): active v2 = `[G1={b}, G1={a}]` (formula `a ∧ b`), candidate
v3 = `[G1={a}]`. Structural classifier: **EQUIVALENT**. Truth-table oracle:
**WEAKER**. `activate_candidate` admits EQUIVALENT, so an allow-broadening passes
the gate.

The source is frozen and checksummed, so it was not edited. **Staged patch,
for Mac to apply in a new version with refreshed `SHA256SUMS.json`:**

```python
def group_map(policy: Policy):
    ids = [g.group_id for g in policy.groups]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate group_id(s) in {policy.policy_id} "
                         f"v{policy.version}: {dupes}")
    return {
        g.group_id: frozenset(o.obligation_id for o in g.obligations)
        for g in policy.groups
    }
```

`install_initial()` and `propose()` should also reject duplicates at the gate
entrance. Whether they already reach `group_map` is UNVERIFIED, and the patch
should call the same check explicitly. Required tests: the counterexample above
must raise, and a policy with distinct group ids must classify exactly as
before.

### F07 — Blind-review aggregator double-counts and mixes inputs (MEASURED)

Reproduced in `repro_batch1.py`:

1. The same review submitted twice gives `reviewer_count = 1` but
   `n_ratings = 2`, so a duplicate silently inflates the median.
2. Candidate id `a` (lower case) bypasses a valid `A/B/C` mapping key and
   survives as its own unmapped profile. It is not mapped and not rejected.
3. Reviews for case `C1` and `C2` are merged, and only `C1` is reported.

A missing `reviewer_id` also defaults to `"unspecified"`, which folds anonymous
reviewers into one person. **Staged patch** (frozen source; apply as a new
version):

```python
    case_ids = {r.get("case_id") for r in reviews}
    if len(case_ids) != 1:
        raise ValueError("Review files cover different cases; aggregate separately.")
    seen = set()
    for review in reviews:
        if not review.get("reviewer_id"):
            raise ValueError("Every review must carry a reviewer_id.")
        rid = str(review["reviewer_id"])
        for candidate in review.get("candidates", []):
            cid = candidate.get("candidate_id")
            if key and key.get("mapping") and cid not in key["mapping"]:
                raise ValueError(f"Candidate id {cid!r} is not in the mapping key.")
            if (rid, cid) in seen:
                raise ValueError(f"Duplicate review of {cid!r} by reviewer {rid!r}.")
            seen.add((rid, cid))
            ...
```

The existing 5 tests in that package's `tests/test_evaluation.py` should gain
one known-bad case per rule above, plus a benign control.

### F08 — Chorus README test failed on the baseline (MEASURED, FIXED)

`test_chorus_readme_marks_ci_workflow_missing` requires the word `MISSING`. The
2026-10-21 README rebuild (`cf6ff23`) kept the meaning ("does not exist") but
dropped the word. One-word restore on line 41.

### F09 — Two other baseline failures, not investigated (MEASURED red)

Both failed **before** any Batch 1 edit:
`tests/test_cybernetics.py::test_every_loop_matches_the_map` and
`tests/test_meaning_handover_demo.py::test_committed_reading_copies_match_current_source`.
Both are drift checks (a map and committed copies against live source), so the
likely cause is the same `cf6ff23` rebuild. That is UNVERIFIED and queued for the
next batch.

**Update, Batch 2 (MEASURED, FIXED).** Both were stale mirrors, not code
defects. The loop map's `L-TRIAXIAL` entry lacked a real caller,
`tests/test_implementation_boundaries.py`, so it was added to `known_callers`.
The committed handover copies carried an old `codec.py` hash. They were
regenerated, and the diff changed that hash only. Both tests pass in focused
runs. Which commit introduced the drift was not traced.

### F10 — Review branch is not `master` (MEASURED)

Memory records Framework as master-only. This work sits on
`review/full-framework-2026-10-20`. Merging is Mac's call.

## Coverage ledger (Batch 1)

Read in full: `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md`,
`FOR-REVIEW/README.md`, `FOR-REVIEW/2026-10-21_PROPOSALS/01_...md`,
`12_IMPLEMENTATIONS/core/lamague_parser.py`, `tests/test_lamague_parser.py`,
`19_MULTI_AGENT_CHORUS/run_chorus.py`, `.../evaluation/aggregate_reviews.py`.
Read in part: `03_LAMAGUE_L1/04_BNF_GRAMMAR.md` (dynamic/junction/example
sections), `policy_evolution_gate.py` (model, `group_map`, structural
classifier, `brute_force_relation`, `activate_candidate`),
`19_MULTI_AGENT_CHORUS/README.md`, `tests/test_threads_fixes.py` (chorus tests).

Executed: full suite pre-edit (3 failed, 1144 passed, 1 skipped, 1 xfailed);
focused suites; planted-failure run of the old parser; `repro_batch1.py`
(exit 0, both counterexamples reproduce); `run_chorus.py --mode=audit`.

Not reviewed: every other folder, including all of Appendices A–F.
