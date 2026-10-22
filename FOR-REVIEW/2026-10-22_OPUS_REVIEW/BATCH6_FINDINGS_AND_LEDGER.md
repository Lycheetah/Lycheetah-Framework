# Opus review — Batch 6: findings register and coverage ledger

Scope: **RV07**, the compaction codec and shield (`lycheetah/compaction/codec.py`,
`shield.py`, `__init__.py`), the two consumers that bind or skip risk
(`lycheetah/sovereign_harness.py`, `lycheetah/handoff.py`), and the committed
reading copies that pin the codec's source. Working tree only, branch
`review/full-framework-2026-10-20`, HEAD `d7ae0ad`. Nothing is committed or pushed.

Every probe below comes from `repro_batch6.py` in this folder, run once against a
clean export of HEAD and once against the working tree. Its first output line
records which `lycheetah` was imported, so a run that silently picked up the
wrong tree shows. The probes use synthetic packets and write nothing.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| R2 | Medium (two paths disagree; an inherited violation passes as safe) | FIXED in working tree | `codec.py` `classify`, `shield.py` digest path |
| R1 | Medium (false refusal; a real protection loss read only as DIVERGENT) | FIXED in working tree | `codec.py` `classify` unknown protection |
| R5 | Medium (boundary: risk and evidence are outside the hash) | DOCUMENTED, kept; Proposal 14 for Mac | `shield.py` `verify_integrity` docstring |
| T1 | Medium (published overclaim) | RETRACTED in `CHANGELOG.md`; docstring fixed in place | `CHANGELOG.md`, `compaction/__init__.py` |
| R3 | Low (a PARTIAL never said what moved) | FIXED in working tree | `classify` `changed_fields`, shield forwarding |
| R4 | Low (malformed digest read as a mismatch; a digest match was silent about what it cannot see) | FIXED in working tree | `shield.py` digest path |
| R6 | Low | DOCUMENTED | order-sensitive comparison |
| R7 | Low (one truth) | OPEN; Proposal 15 for Mac | `shield.py:384–397` |
| R8 | — | DERIVED observation, no change | `handoff.py:588–649` |
| X1, X2, C1–C8 | — | HELD: no defect | export independence, dropped and altered critical context |

### R2 — The packet path and the digest path disagreed on a packet that already broke a rule (MEASURED, FIXED)

`classify` refused only violations the candidate *introduced*. A candidate that
kept a violation the reference already carried fell through to the hash
comparison: PARTIAL_EQUIVALENT with `is_safe` True after a risk change (V1), and
EXACT_EQUIVALENT for an exact copy (V3). The digest path checked the candidate's
violations outright and returned UNSAFE_COLLAPSE for the same candidate (V2), and
`encode` refuses to compact such a packet at all. Same candidate, two verdicts.

Fix: any candidate violation is UNSAFE_COLLAPSE on both paths, with the full
sorted list in `violations`. The reason says whether the candidate introduced the
violation or kept one the reference carried. DERIVED: callers are only affected
when the reference itself breaks a rule, which `encode` already refuses; the full
suite passed unchanged.

### R1 — Unknown protection was judged over the list, not per unknown (MEASURED, FIXED)

On HEAD, a packet holding one protected and one unprotected unknown read as
UNSAFE_COLLAPSE `unknown_protection` against a copy of itself with only the
horizon changed (M1). Adding an unprotected unknown beside a protected one did the
same (M3). In the other direction, swapping the protected unknown U1 for a
different protected unknown U9 read only as DIVERGENT (C9): the protected
dependency disappeared and the shield did not call it a protection loss.

Fix: every protected reference unknown must survive under the same id and stay
protected. M1 is now PARTIAL_EQUIVALENT, M3 DIVERGENT (the unknowns list did
change), C9 UNSAFE_COLLAPSE `unknown_protection`. C8 and M2, where a protected
unknown loses its protection, are unchanged.

### R5 — Risk, evidence, horizon, yield, id and operations are outside the critical projection (MEASURED, DOCUMENTED)

`CRITICAL_FIELDS` are purpose, claim, unknowns, invariants, authority,
participants, affectedParties, dissent, valueFlow and recovery. Everything else
can change under PARTIAL_EQUIVALENT with `is_safe` True: a CRITICAL to LOW risk
downgrade (N1), dropped evidence (N3), evidence replaced by an invented claim
(N4), yield changed from halt to proceed (N6). A stale snapshot passes against a
live accumulator whose risk was escalated after the export (S1).

This is a design boundary, and it is pinned: `tests/test_sovereign_admission_risk.py:97`
asserts that a risk downgrade is `is_safe` True at the shield, and
`tests/test_meaning_handover_demo.py:57` asserts the reading demo's
PARTIAL_EQUIVALENT. The consumers that act on risk bind it themselves:
`sovereign_harness.py:816` and `:818` stop on REFERENCE_RISK_MISMATCH and
CANDIDATE_RISK_MISMATCH after the Gate 2 compaction check (`:753`), and
`handoff.py:222–243` puts `risk` inside the task digest.

What changed is that the boundary is now visible rather than silent. Every
verdict names `changed_fields`, and the `verify_integrity` docstring lists what
it detects and what it does not. Changing the boundary itself is Proposal 14.

### T1 — Published prose claimed a guarantee and a proof (MEASURED, RETRACTED)

The historical CHANGELOG entry for the compaction shield said "Guaranteed 36/36
exact round-trip preservation", that the hash allowed "third parties to
mathematically verify zero loss of safety constraints under context window
compaction", and that the demo was "proving anti-amnesia protection under LLM
summarization". The package docstring opened with "Provable context compaction".
R5 shows the hash never covered risk or evidence, and no hash can show that a
declaration was complete or true. History was not rewritten: a new
`[Unreleased]` subsection retracts the three phrases with cause. The package
docstring was fixed in place because it is live code. `examples/README.md:17`
and `lycheetah/README.md:60` were already honest.

### R3, R4 — Verdicts now say what moved and what was not looked at (MEASURED, FIXED)

R3: a PARTIAL_EQUIVALENT said only that non-critical content differed. Every
validated verdict now carries `changed_fields`, the top-level fields whose
canonical JSON differs, and the shield forwards it.

R4: a 64-character reference string in uppercase (H2) or not hexadecimal (H3)
was compared as if it were a digest and read as DIVERGENT, a claim that the
meaning had changed. It is now UNDECODABLE. A digest match is PARTIAL_EQUIVALENT
as before, and now names the fields the digest cannot see in `unchecked_fields`
(H1). H4, a trailing newline, was already UNDECODABLE.

### R6 — Reordering a critical list is DIVERGENT (MEASURED, DOCUMENTED)

The comparison is order-sensitive (C6, C7). That is conservative: it can refuse
a harmless reorder but never passes a real change. It is now stated in the
`classify` docstring.

### R7 — `export_packet` restates two codec rules in its own words (MEASURED, OPEN)

`ContextProtector.export_packet` (`shield.py:378`) raises its own errors for a
protected unknown without recovery and for value flow without affected parties
(`:384–397`) before building the packet, which the codec then validates. Two
statements of one rule can drift apart. Proposal 15 would have it raise on
`safety_violations` with the codec's names. Not applied, because the exception
messages may be pinned by callers.

### R8 — The handoff verifier's compaction check overlaps the task digest (DERIVED)

`verify_handoff` (`handoff.py:588`) runs `CompactionShield.verify_integrity` at
`:649`, but the task digest (`:241`) already binds risk and the task payload
(`:222–243`). The compaction check adds the critical-projection comparison; its
risk blindness is covered. Observation only.

## Probe table (MEASURED)

`←` marks a verdict that changed. "Tree names" is `changed_fields`, or
`unchecked_fields` for H1. V2 keeps its verdict and only gains the named
violations.

| Probe | Drift | HEAD `d7ae0ad` | Working tree | Tree names |
|---|---|---|---|---|
| X1 | mutating an export leaves the accumulator alone | holds | holds | — |
| X2 | mutating the accumulator leaves an export alone | holds | holds | — |
| N1 | risk CRITICAL -> LOW | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `risk` |
| N2 | risk LOW -> CRITICAL | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `risk` |
| N3 | evidence dropped | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `evidence` |
| N4 | evidence replaced by an invented claim | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `evidence` |
| N5 | evidence reordered | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `evidence` |
| N6 | yield halt -> proceed | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `yield` |
| N7 | horizon changed | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `horizon` |
| N8 | id changed | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `id` |
| C1 | authority dropped | UNSAFE_COLLAPSE False `authority` | UNSAFE_COLLAPSE False `authority` | `authority` |
| C2 | dissent dropped | UNSAFE_COLLAPSE False `dissent` | UNSAFE_COLLAPSE False `dissent` | `dissent` |
| C3 | recovery dropped beside a protected unknown | UNSAFE_COLLAPSE False `PROTECTED_UNKNOWN_WITHOUT_RECOVERY` | UNSAFE_COLLAPSE False `PROTECTED_UNKNOWN_WITHOUT_RECOVERY` | `recovery` |
| C4 | authority scope altered, same count | DIVERGENT False | DIVERGENT False | `authority` |
| C5 | claim altered | DIVERGENT False | DIVERGENT False | `claim` |
| C6 | participants reordered | DIVERGENT False | DIVERGENT False | `participants` |
| C7 | invariants reordered | DIVERGENT False | DIVERGENT False | `invariants` |
| C8 | protected unknown unprotected | UNSAFE_COLLAPSE False `unknown_protection` | UNSAFE_COLLAPSE False `unknown_protection` | `unknowns` |
| C9 | protected unknown swapped for a different protected one | DIVERGENT False | UNSAFE_COLLAPSE False `unknown_protection` ← | `unknowns` |
| M1 | mixed unknowns, only horizon changed | UNSAFE_COLLAPSE False `unknown_protection` | PARTIAL_EQUIVALENT True ← | `horizon` |
| M2 | mixed unknowns, U1 unprotected | UNSAFE_COLLAPSE False `unknown_protection` | UNSAFE_COLLAPSE False `unknown_protection` | `unknowns` |
| M3 | protected unknowns, new unprotected one added | UNSAFE_COLLAPSE False `unknown_protection` | DIVERGENT False ← | `unknowns` |
| V1 | inherited violation, packet reference | PARTIAL_EQUIVALENT True | UNSAFE_COLLAPSE False `AUTHORITY_OR_AFFECTED_WITHOUT_G,DISSENT_WITHOUT_V,RECOVERY_WITHOUT_FOLD,UNKNOWN_WITHOUT_U` ← | `risk` |
| V2 | inherited violation, digest reference | UNSAFE_COLLAPSE False | UNSAFE_COLLAPSE False `AUTHORITY_OR_AFFECTED_WITHOUT_G,DISSENT_WITHOUT_V,RECOVERY_WITHOUT_FOLD,UNKNOWN_WITHOUT_U` | — |
| V3 | inherited violation, exact copy | EXACT_EQUIVALENT True | UNSAFE_COLLAPSE False `AUTHORITY_OR_AFFECTED_WITHOUT_G,DISSENT_WITHOUT_V,RECOVERY_WITHOUT_FOLD,UNKNOWN_WITHOUT_U` ← | — |
| S1 | stale snapshot after a risk escalation | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `risk` |
| S2 | stale snapshot after an authority was added | UNSAFE_COLLAPSE False `authority` | UNSAFE_COLLAPSE False `authority` | `risk,authority` |
| H1 | digest match, risk and evidence changed | PARTIAL_EQUIVALENT True | PARTIAL_EQUIVALENT True | `id,risk,operations,evidence,horizon,yield` |
| H2 | digest in uppercase | DIVERGENT False | UNDECODABLE False ← | — |
| H3 | 64 characters, not hexadecimal | DIVERGENT False | UNDECODABLE False ← | — |
| H4 | digest with a trailing newline | UNDECODABLE False | UNDECODABLE False | — |

## Notes

1. **The reading copies pin the codec source.** `docs/lamague-handover-report.json`
   records codec.py's sha256, and `test_committed_reading_copies_match_current_source`
   compares it. Any codec edit therefore needs a regeneration. Both files were
   regenerated in place with the demo's own `--write-report` and `--write-page`
   flags, and the result matched a scratch regeneration byte for byte. Against
   HEAD, the controls gained `changed_fields`, the dropped-protected-unknown
   control's `fields` went from `unknowns` to `unknown_protection, unknowns`,
   and the source sha changed. The summary did not change, and the test asserts
   it. Before this batch the two files differed from HEAD by one line each, the
   codec sha updated by Batch 2 (F09).
2. **No linter is installed.** `ruff` and `pyflakes` are both absent;
   `py_compile` passed on every changed Python file. This is not a lint pass.
3. **Lead, UNVERIFIED:** the same historical entry says the invariant check
   refuses "to compact or execute high-risk plans". The codec rule
   (PROTECTED_UNKNOWN_WITHOUT_RECOVERY) is not conditioned on risk in
   `export_packet`, and the codec executes nothing. That belongs to the harness
   review; it is not retracted here.

## Proposals for Mac (not applied)

- **Proposal 14: refuse a risk downgrade at the shield.** Sol's stance is
  **yes**. A compaction is a summary, and a summary that lowers risk is amnesia
  of severity, the exact failure the shield is named for. A legitimate downgrade
  is a new decision, not a compaction. The rule belongs in `classify` as a
  comparison (candidate risk below reference risk is UNSAFE_COLLAPSE `risk`), not
  in the hash, so `critical_hash`, the wire bytes and every digest stay the
  same. Escalation stays PARTIAL. Costs: the two pinned assertions in R5 change.
  Gate 2 runs before the harness's risk binding, so a downgrade's stop reason
  would become COMPACTION_UNSAFE_COLLAPSE, unless the harness binds risk first.
  `examples/guarded_handoff_risk_demo.py:318` and `:430` expect
  CANDIDATE_RISK_MISMATCH, and the frozen evidence under
  `34_ASSURANCE_RUNTIME/evidence/guarded-handoff-risk-2026-10-18/` would then no
  longer reproduce from current code unless that ordering is kept. Standalone
  users of `CompactionShield`, which the README presents on its own, are the ones
  exposed today.
- **Proposal 15:** one statement of the export rules (R7).
- **Still open from earlier:** whether evidence, yield and horizon should become
  critical. Unlike Proposal 14, this changes `critical_hash` and every digest
  ever recorded.

## Tests added

`tests/test_compaction_drift_boundaries.py`, 25 items:

- `test_export_does_not_share_state_with_the_live_accumulator` (both directions)
- `test_noncritical_drift_stays_partial_but_is_named` (7 cases)
- `test_missing_altered_and_reordered_critical_context_is_not_safe` (9 cases)
- `test_unprotected_unknown_beside_a_protected_one_is_not_a_collapse`
- `test_both_reference_paths_refuse_a_candidate_that_breaks_a_packet_rule`
  (includes an EXACT_EQUIVALENT control)
- `test_a_stale_snapshot_passes_unless_a_critical_field_moved_on`
- `test_digest_reference_names_what_it_cannot_see`
- `test_malformed_digest_reference_is_undecodable` (4 cases)

## Verification (MEASURED)

- New test file on the HEAD export, with `lycheetah` imported from
  `head_export/lycheetah/__init__.py`: `14 failed, 11 passed in 0.63s`. These are the
  defects. The passing cases are the boundaries and controls, which hold on
  both trees.
- New test file on the working tree: `25 passed in 0.49s`.
- `tests/test_meaning_handover_demo.py` after the regeneration: `36 passed`.
- Full suite on the Batch 4 + 5 + 6 tree: `1266 passed, 1 skipped, 1 xfailed,
  1 warning in 57.14s`, exit 0. That is the Batch 5 count of 1241 plus the 25
  new items. The one warning is the expected non-interactive Agg notice.

## Coverage ledger (Batch 6)

| Surface | Depth |
|---------|-------|
| `lycheetah/compaction/codec.py` `classify`, `safety_violations`, `CRITICAL_FIELDS` | Read and probed |
| `lycheetah/compaction/shield.py` | Read in full and probed |
| `lycheetah/compaction/__init__.py` | Read; docstring fixed |
| `lycheetah/sovereign_harness.py` Gate 2 compaction (`:753`) and risk binding (`:816–818`) | Regions read; not a harness review |
| `lycheetah/handoff.py` `_task_payload`, `task_digest`, `verify_handoff` | Regions read |
| `docs/lamague-handover-report.json`, `docs/lamague-handover.html` | Regenerated and diffed |
| `examples/compaction_shield_demo.py` | Searched for overclaim wording only (none found) |
| `lycheetah/cli.py` `lycheetah-compact` subcommands | **Not reviewed**; covered only by its existing tests in the full run |
| Codec encode and decode wire format | **Not reviewed** here; RV08 compares it with the frozen `lamague_codec.py` |

## Changed paths (Batch 6, working tree only)

- `lycheetah/compaction/codec.py`: `_changed_fields`, and a rewritten `classify`
- `lycheetah/compaction/shield.py`: digest validation, `unchecked_fields`, forwarding, boundary docstring
- `lycheetah/compaction/__init__.py`: docstring
- `tests/test_compaction_drift_boundaries.py`: new
- `docs/lamague-handover-report.json`, `docs/lamague-handover.html`: regenerated
- `CHANGELOG.md`: new `[Unreleased]` subsection, "Opus review corrections — 22 October 2026"
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch6.py`: new
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH5_FINDINGS_AND_LEDGER.md`: full-suite placeholder filled
- this ledger
