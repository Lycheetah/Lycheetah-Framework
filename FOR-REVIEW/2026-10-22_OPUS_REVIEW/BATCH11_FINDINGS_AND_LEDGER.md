# Batch 11 — RV12: blind-review aggregator admission

Reviewer: Sol (Claude Opus 5.5, xhigh), 2026-10-22. Working tree only; nothing committed.

Target (frozen, sealed by the v1.3 handoff `SHA256SUMS.txt`):
`23_NZ_AI_GOVERNANCE/anon_politician/PROJECT_CORE/Anon_Politician_Full_Handoff_v1.3/07_POLICY_LAB_v0.2/Anon_Politician_Policy_Lab_v0_2/evaluation/aggregate_reviews.py`

## What was actually read

| Surface | Read |
|---|---|
| `evaluation/aggregate_reviews.py` (89 lines) | in full |
| `evaluation/prepare_blind_pack.py` | in full; key fields `experiment_id`, `blind_pack_id`, `mapping`, `source_packet_sha256`, `blind_pack_sha256`, `possible_blinding_leaks`, `warning` |
| `evaluation/reviewer.html` | export path (line 77) and reviewer-ID field; driven in headless Chromium |
| `evaluation/benchmark_protocol.md`, `evaluation/review_manual.md` | in full |
| `evaluation/test_evaluation.py`, `tests/test_evaluation.py` | in full; they differ only at line 3 (the `sys.path` line) |
| `TEST_RESULTS.txt`, README lines 44–51, CURRENT_WORK lines 38–53 | read |
| Prior records | `repro_batch1.py rv12()`, `BATCH1_FINDINGS_AND_LEDGER.md` F07, `28_DEFENSE/review_2026_10_20/deeper-reproductions.json` |

Not covered by the root suite. `pyproject.toml` sets `testpaths = ["tests"]` at the repository root, so the
earlier full-suite count (1354 passed) never ran this lab's 16 tests. They run only through
`unittest discover` inside the lab, which is what `repro_batch11.py` does. (DERIVED from the config.)

## Seal check (MEASURED)

- `SHA256SUMS.txt`: 103 entries, 103 match the bytes on disk, 0 differ, 0 missing.
- The four files the patch touches are all listed and all match.
- `aggregate_reviews.py` equals the hash recorded on 20 October (`4213a823…7922`).
- `git status` on the lab is empty before and after; the probe's folder digest is unchanged.
- A gitignored `__pycache__/` (20 Oct 14:58) already sits in `evaluation/`. It was left alone and is excluded from the digest.

## Findings

Names match the keys printed by `repro_batch11.py`. "Normal path" means the defect is reachable through
`prepare_blind_pack.py` → `reviewer.html` → `aggregate_reviews.py` without hand-editing any file.

### F1 — A renamed blind pack counts as a second reviewer (R7) — HIGH, normal path

The pack is saved into the review folder as `case1_pack.json`, a name that does not contain
`blind_review_pack`. One real review sits beside it, and the aggregator is run through its command line.

- Frozen run 1 reports `review_count 2` and `reviewer_count 2` for **every method**. The pack's candidates
  are read as a review by reviewer `"unspecified"`.
- `benchmark_protocol.md` §6 requires at least two independent reviewers. One stray file satisfies that
  count with a single real reviewer.
- Run 2 writes `--out` into the same folder. It then reads its own previous output as a review:
  `review_count 3`.
- Filtering by filename (`blind_review_pack`, `mapping_key`) is the only admission rule `main()` has.

MEASURED. The recon plan for this batch carried the stale-output case as CONJECTURE, and it is now
MEASURED.

Staged: both runs are refused, and the refusal lists every file by index so the stray one can be found.
In a standalone CLI run against a folder holding only `case1_pack.json`, it printed
`Refused: Review 0 has no reviewer_id…` and then `Review files by index: 0=case1_pack.json`.
The refusal is incidental: neither stray file carries a `reviewer_id`. A stray JSON that does carry a
reviewer ID and A/B/C candidates would still be read, but such a file is structurally a review.
Requiring `schema_version` would close this fully, but it breaks the existing fixtures, which carry none.
That choice is left to Mac (decision D3).

### F2 — Duplicate reviews inflate the counts and move the median (R1, R1b, R1c) — HIGH, normal path

`reviewer.html` names each download `review_<id>_<Date.now()>.json`, so a re-export creates a second
file rather than replacing the first (DERIVED from the export code). Frozen results:

| Probe | Input | Frozen result |
|---|---|---|
| R1 | r1=2, r2=0, then r1's file again | `reviewer_count 2`, `n_ratings 3`, ratings `[2,0,2]`, median **2**. The honest median is 1. |
| R1b | r1 exports 0, revises and re-exports 2 | `reviewer_count 1`, `n_ratings 2`, median **1.0**: both opinions are averaged |
| R1c | one review lists candidate A twice | `n_ratings 2` from one reviewer |

`reviewer_count` is a set but the observations are a list, so the two counts silently disagree.
Staged: a second `(reviewer, candidate)` pair is refused with both review indices named.

### F3 — Blank reviewer IDs merge different people (R2, R2b, R2c) — HIGH, normal path

- **Browser witness (headless Chromium, 27 rating controls filled).** The frozen `reviewer.html` exports
  `"reviewer_id": "unspecified"` when the ID field is blank, with no warning.
- **Aggregator.** Two such reviewers fold into `reviewer_count 1`, `n_ratings 2`. Two people are reported
  as one reviewer whose two opinions are averaged.
- **Batch 1 F07.** Its inline patch required `reviewer_id` to be non-empty, but would have admitted the
  literal `"unspecified"`. This batch supersedes that patch.

Staged:

- The aggregator refuses a review whose ID is missing, blank, or `unspecified` (case-insensitive).
- `reviewer.html` stops a blank export with a dialog and no download (witnessed in the browser).
- With `reviewer-07` filled in, the export proceeds unchanged (also witnessed).

### F4 — Bad key binding misattributes scores (R5, R5b–R5e) — HIGH impact, off the normal path

Frozen:

| Probe | Input | Result |
|---|---|---|
| R5 | Reviews carry no `blind_pack_id`; a key for another pack (APB-2) is supplied | The mapping is applied. Alias A's 0 lands under `anon_politician`. The output's `blind_pack_id` is `null`. |
| R5b | One review names the pack, one doesn't | Accepted |
| R5c | Key names no pack | Accepted |
| R5d | Key belongs to another experiment | Accepted |
| R5e | Two different `source_packet_sha256` values | Merged |

This is the defect with the worst outcome: a confident score assigned to the wrong method, in the
benchmark built to compare those methods.

Reach is limited (DERIVED). `prepare_blind_pack.py` always writes `blind_pack_id` into both the pack and
the key, and `reviewer.html` copies it, so in the normal path the frozen mismatch check does fire. The hole
opens only when a pack or key is made by hand, or edited, or comes from a pack without an ID.

Staged:

- Every review must carry the same `blind_pack_id`.
- A key that has a mapping must name its pack.
- The key's pack, experiment and source packet must match the reviews.

### F5 — Mixed or missing case and experiment IDs (R3, R3b, R3c) — MEDIUM

- Frozen R3: two cases are merged into one profile, and only `C1` is reported.
- Frozen R3b and R3c: a missing `case_id` or `experiment_id` is accepted, and the output reports `null`.
- `case_id` was never checked anywhere.

Staged: there must be exactly one non-empty value of each, shared by every review.

### F6 — Candidate identity (R4, R4b, R4c) — MEDIUM

Frozen:

- A lowercase `a` survives the key and becomes a fourth profile named `a`.
- Without a key, alias `D` is accepted.
- A candidate with no `candidate_id` crashes with `TypeError: '<' not supported between instances of
  'str' and 'NoneType'`. That is an uncontrolled crash, not a refusal.

Staged: the candidate ID must be exactly A, B or C, and anything else gets a clear `ValueError`.

### F7 — "Not assessable" and "missing" look the same (R6) — MEDIUM

Frozen: three reviewers rate one dimension. The first chose N/A, the second's rating is absent, the third
scored it. The output shows `reviewer_count 3`, `n_ratings 1`, and nothing that says why two ratings are
gone. A missing rating also takes the `"N/A"` path silently, through
`str(item.get("score","N/A"))`. `reviewer.html` forces every dimension to be rated, so `n_missing` arises
only from hand-edited or truncated files.

Staged: `n_not_assessable` and `n_missing` are reported separately (output 1/1/1). A rating that has no
`score` field is refused.

### F8 — Reviewer disagreement is not computed — LOW, not patched (SCAFFOLD)

`benchmark_protocol.md` §6 asks for reviewer disagreement to be reported, but the aggregator gives only
`range`. This is left unpatched. It is a feature gap, not an admission defect, and the patch does not
claim it.

## Controls (must aggregate identically) — MEASURED

| Control | Frozen | Staged |
|---|---|---|
| R8: two honest reviewers, scores 1 and 2 | median 1.5 | median 1.5 |
| C1: clean three-reviewer study (N/A pattern, one critical flag) | fingerprint `71a731efef793648` | `71a731efef793648` |
| C2: one reviewer split across two files (A, then B+C) | reviewer_count 1 each | reviewer_count 1 each |

C2 matters because the duplicate rule refuses a repeated (reviewer, candidate) pair, not a repeated
reviewer.

## Tests — MEASURED

| Run | `tests/` | `evaluation/` |
|---|---|---|
| Frozen code, frozen tests | 16 ran, OK | 5 ran, OK |
| Staged code, staged tests | 24 ran, OK | 13 ran, OK |
| **Frozen code, staged tests** | 24 ran, **6 FAIL + 1 ERROR** | 13 ran, **6 FAIL + 1 ERROR** |

The seven new tests that do not pass on frozen code:

- duplicate review
- revised re-export
- unidentified reviewers
- different cases
- candidate outside the pack
- key bound to the pack
- N/A versus missing (this one is the ERROR: the frozen output has no `n_not_assessable` key)

The eighth new test, a split reviewer accepted, passes on both by design. It guards against over-refusal.

The only edit to an existing test: one key fixture gains `'blind_pack_id':'APB-123'`. No assertion changes.

## Staged patch — STAGED, NOT APPLIED

- **Patch:** `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV12_aggregate_reviews.patch`. It touches four files:
  `aggregate_reviews.py` (becomes aggregator 0.2.1), `reviewer.html`, and both `test_evaluation.py`.
- **Generator:** `build_rv12_patch.py` in the session scratchpad. It builds from the frozen bytes, and
  every substitution asserts a single occurrence.
- **Apply witness:** on a scratch copy of the lab, `patch -p1 --dry-run` and then `patch -p1` applied
  cleanly. All four results are byte-identical to the generator's output.
- **Compile and syntax:** the staged module compiles under `py_compile`, and the staged `reviewer.html`
  script passes `node --check`.

**Behaviour changes Mac should know about before applying:**

1. Every review must carry `blind_pack_id`, `case_id` and `experiment_id`. Frozen code accepted reviews
   with no pack ID at all. Packs made by `prepare_blind_pack.py` always carry one.
2. `reviewer.html` will not export without a reviewer ID or pseudonym.
3. The output adds `aggregator_version`, `n_not_assessable` and `n_missing`. These are additive, and no
   existing field changes meaning.
4. Applying the patch changes four sealed files. `SHA256SUMS.txt` must be re-sealed, or this ships as a
   new handoff version.

## Decisions for Mac

- **D1.** Apply RV12 as Policy Lab v0.2.1 inside a new handoff version (Sol's recommendation), or
  re-seal v1.3 in place.
- **D2.** Keep the reviewer-ID guard in `reviewer.html` (recommended), or enforce it in the aggregator only.
- **D3.** Also require `schema_version == "anon-politician-review-v0.2"` in `main()`. This closes F1
  completely, but the existing fixtures need that field added.
- **D4.** Whether F8 (reporting disagreement) is wanted before the first real review round.

## Reproduce

```
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch11.py <repo>                      # frozen
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch11.py <repo> <staged> --tests-only # new tests vs frozen code
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch11.py <repo> <staged>              # staged
```

`<staged>` is a folder laid out as `evaluation/` and `tests/`, such as the scratch `rv12/` folder or a
copy patched with `RV12_aggregate_reviews.patch`. Each run copies the lab into a tempdir and compares the
frozen folder's digest before and after.

Next workstream: RV13.
