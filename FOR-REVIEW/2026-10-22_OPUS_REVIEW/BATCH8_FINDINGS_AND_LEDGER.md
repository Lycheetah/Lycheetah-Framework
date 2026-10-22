# Opus review — Batch 8: findings register and coverage ledger

Workstream: **RV09, exported evidence bundle and independent verifier.** The
checklist carried it as "Reported repaired." Branch
`review/full-framework-2026-10-20`, HEAD `d7ae0ad`, working tree uncommitted.
Nothing was committed or pushed. The retained evidence folder
`34_ASSURANCE_RUNTIME/evidence/guarded-handoff-risk-2026-10-18/` is unchanged.

Method: `repro_batch8.py <repository root>` exports a fresh bundle with that
repository's own demo, then verifies mutated copies. "Resealed" means the probe
also recomputed each run record's witness digest and the manifest. Neither needs
a secret: both are public SHA-256 hashes. The probe ran against the HEAD export
and the working tree. New tests were copied into the HEAD export, with
`lycheetah` and `examples` resolving there, and must fail on HEAD and pass on the
tree.

Read in full: `examples/guarded_handoff_risk_demo.py` (529 lines at HEAD),
`tests/test_guarded_handoff_bundle.py` (270 lines at HEAD), the harness witness
envelope (`lycheetah/sovereign_harness.py:540-612`) and every document that
describes the verifier: `examples/README.md`, `README.md:104-116`,
`34_ASSURANCE_RUNTIME/GUARDED_HANDOFF_ADMISSION_v0.1.md:128-146`,
`28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md:418-440` and
`lycheetah/README.md:63`. Not re-read in this batch: the internals of
`verify_handoff` and of the receipt's own `verify`, which the verifier calls.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| G1 | Medium (the verifier vouched for report claims it never compared: production mode, no limits, LOW risk against a HIGH permit, an added approval field) | FIXED in working tree | `verify_bundle` |
| G2 | Medium (control records not bound to the run: another permit, another action, a phantom consensus agent) | FIXED in working tree | `verify_bundle` |
| G3 | Medium (the completion could claim attestation it never had) | FIXED in working tree | `verify_bundle`, `run_demo` |
| G4 | Low (RecursionError escaped `verify_bundle`) | FIXED in working tree | `verify_bundle` |
| G5 | Low (`1e400` read as infinity past the nonfinite guard) | FIXED in working tree | `_read_json` |
| G6 | Low (type checked by name, then the file read by name again) | FIXED in working tree | `_read_regular` |
| G7 | Medium (a non-canonical `context.l1` verified) | FIXED by Batch 7's strict decode; reconfirmed here | `lycheetah/compaction/codec.py` |
| D1 | Medium (published claim false at HEAD) | CORRECTED | `examples/README.md:43-46` |
| D2 | — | DOCUMENTED; dated record, not rewritten | `28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md:434-440` |
| B1 | Boundary | UNCHANGED, now stated | complete rewrite, no signature, shared library |
| H1 | — | HELD: no defect | refusals listed below |

G1 to G3 are Medium rather than High because a separately retained manifest
digest catches every one of them. They matter in the mode the documentation
described as "its included records agree".

### Probe results

| Probe | Mutation (resealed) | HEAD | Tree |
|-------|---------------------|------|------|
| R1 | `limits: []` | SELF_CONSISTENT | INVALID: mode, limits or workspace |
| R2 | `mode: PRODUCTION_ATTESTED` | SELF_CONSISTENT | INVALID: mode, limits or workspace |
| R3 | top-level `bound_risk: LOW` against a HIGH permit | SELF_CONSISTENT | INVALID: summary differs from the permit |
| R4 | added `authenticated_human_approval: true` | SELF_CONSISTENT | INVALID: missing or unexpected fields |
| R5 | `critical_hash_unchanged_by_risk_downgrade: false` | SELF_CONSISTENT | INVALID: not a risk-only change |
| R6 | `temporary_workspace_removed_on_exit: false` | SELF_CONSISTENT | INVALID: mode, limits or workspace |
| C0 | witness digests recomputed, nothing else changed (benign control) | SELF_CONSISTENT | SELF_CONSISTENT |
| C1 | replay control names permit digest `0`×64 | SELF_CONSISTENT | INVALID: another permit, consensus, scope or state |
| C2 | downgrade control names action hash `0`×64 | SELF_CONSISTENT | INVALID: a control names the wrong action |
| C3 | replay `evaluated_at` set to the permit's `issued_at` | SELF_CONSISTENT | SELF_CONSISTENT (no-op, below) |
| C4 | `phantom-agent` added to every record's healthy agents | SELF_CONSISTENT | INVALID: consensus names other agents |
| N1 | completion notes "Externally attested by an independent auditor" | SELF_CONSISTENT | INVALID: completion claims more than the local observation |
| N2 | completion summary "Verified in production" | SELF_CONSISTENT | INVALID: completion claims more than the local observation |
| X1 | garbage `context.l1` | INVALID | INVALID |
| X2 | non-canonical `context.l1` for the same packet | SELF_CONSISTENT | INVALID: not the canonical encoding |
| X3 | `task.json` is `{}` | INVALID | INVALID |
| X4 | receipt is `{}` | INVALID | INVALID |
| X5 | `action.json` nested 200,000 arrays deep | raised RecursionError | INVALID |
| X6 | packet risk `BANANA` | INVALID | INVALID |
| F1 | `_read_json(b'[1e400]')` | returned `[inf]` | refused: nonfinite |

C3 changed nothing (DERIVED). The four run records are stamped in whole seconds,
and the permit window already forces the executed record's time to be at least
the permit's issue time. C3 still verified on the tree, whose order check
requires replay to be no earlier than the executed record, so all three times were
already equal. The tests use real reversals instead.

### G1 — The run report's own claims were never compared (MEASURED, FIXED)

At HEAD the verifier checked the four run records, the observed file and the
executor-call count in `run-report.json`. Six other fields were written by the
exporter and never read back: mode, limits, permit schema, bound risk, the
risk-downgrade flag and the workspace statement. An added key was ignored. R1 to
R6 all verified as `SELF_CONSISTENT`.

Fix: the report must hold exactly the exporter's fields (`REPORT_KEYS`). Mode,
limits and the workspace statement must equal the exporter's constants. Permit
schema and bound risk must equal the permit. The downgrade flag is derived instead
of trusted: it must be true, and the downgrade control must carry the packet's
critical hash with a candidate risk different from the packet's.

### G2 — Control records were not bound to the run (MEASURED, FIXED)

At HEAD each denied control was checked for its stop reason, `provider_called:
false`, its format and its witness digest. The witness digest is a public hash, so
recomputing it after an edit costs nothing. A control could name another permit
(C1) or another action (C2), and all four records could name an agent that never
took part (C4).

Fix:

- Every record carries the executed permit, the same consensus summary, the
  task's scope and the permit's state version.
- Each control is denied: `accepted` false, `status` DENIED, no provider call and
  no gateway result.
- The downgrade and replay controls name the declared action, and the
  substitution control names a different one.
- Records run in the export's order, starting no earlier than the permit's issue
  time.
- Consensus names only the task's recipient and authority, once each, with none
  quarantined.

This binds the names. It does not show that any agent ran: the consensus in this
demo is synthetic (B1).

### G3 — The completion could claim attestation it never had (MEASURED, FIXED)

The completion's summary and evidence notes are free text. `HandoffResult`
checks that they are text (`lycheetah/handoff.py:130-133`), not what they say. N1
replaced "Local in-process observation; no external human or filesystem
attestation" with "Externally attested by an independent auditor", and the
bundle verified.

Fix: both strings are module constants (`COMPLETION_SUMMARY`, `COMPLETION_NOTES`)
that `run_demo` writes and the verifier requires, so each has one definition. A
bundle whose exporter wrote other text is refused. This verifier vouches only for
bundles this script writes, which is the only kind it was ever able to judge.

### G4 — Deep nesting escaped as RecursionError (MEASURED, FIXED)

Python's JSON decoder raises RecursionError on X5. That is a RuntimeError, not a
ValueError, so it escaped `verify_bundle`. The CLI caught it through its
RuntimeError handler, printed "Handoff demonstration failed" and exited 2. That
fails closed, but with the wrong message, and a library caller got an exception
instead of a verdict. RecursionError is now in the verifier's refusal tuple.

### G5 — An overflowing number became infinity (MEASURED, FIXED)

`parse_constant` refuses the literals `NaN`, `Infinity` and `-Infinity`. `1e400`
is an ordinary number literal that overflows to `inf`, so it slipped past the
"nonfinite JSON value" guard. A `parse_float` hook now refuses any non-finite
result. Whether any record field would act on an infinite value was not traced
(UNVERIFIED). The guard now does what its message says.

### G6 — Type checked by name, then read by name (FIXED; race simulated, not timed)

At HEAD the manifest and each evidence file were checked with `is_symlink`,
`is_file` and `stat`, then read with `read_bytes`, and each call resolved the path
again. A file swapped for a FIFO between check and read would block the verifier
waiting for a writer. One swapped for a symlink would be followed. The 20 October
record names a "nonregular-manifest read hazard" as repaired. That repair added
the check, not a check of what was actually opened.

`_read_regular` opens once with `O_NOFOLLOW | O_NONBLOCK`, checks the opened
descriptor with `fstat` (a regular file within the size bound), and reads at most
one byte past the bound. The test simulates the race: the name-based check reports
the FIFO as a regular file, and the test fails if anything then reads it by name.
That shows which code path runs; it is not a timed race against a live writer.
Exploiting the gap needs write access to the bundle directory during
verification.

### G7 — Non-canonical context (MEASURED; fixed by Batch 7)

X2 replaced `context.l1` with a different wire for the same packet. HEAD verified
it. The tree refuses it through Batch 7's strict decode (W1 to W7). Nothing
changed for it in this batch.

### D1, D2 — Documents

- D1, `examples/README.md`: "Without a separately retained digest,
  `SELF_CONSISTENT` means its included records agree." False at HEAD (R1 to N2).
  It now says that `SELF_CONSISTENT` means every relationship the verifier
  checks holds, including the run report and its three denied controls, and that
  a complete, consistent replacement of the whole bundle still passes.
- D2, `28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md:434-436`: "Independent AI
  review caught contradictory run reports, omitted completion paths and a
  nonregular-manifest read hazard in the first verifier." The ten existing
  `valid_execution` contradiction tests pass at HEAD, so that repair held for the
  executed record. The report's other fields, the controls and the completion
  text stayed unchecked, and the manifest check-then-read stayed open (G6). This
  is a dated record. This ledger is its correction, and the file is not
  rewritten.
- `34_ASSURANCE_RUNTIME/GUARDED_HANDOFF_ADMISSION_v0.1.md:139-140` names the
  relationships between task, context, action, receipt and observed bytes, which
  held at HEAD. `README.md:104-116` claims internal consistency only. Both are
  unchanged.

### B1 — What a SELF_CONSISTENT bundle still cannot show (unchanged, DERIVED)

- **A complete, consistent replacement verifies.** The demo does not sign its
  receipt and exports no checkpoint key, so anyone with the library can produce a
  fresh bundle that passes. Only a digest retained separately at export pins one
  bundle.
- **Independent of execution, not of implementation.** The verifier runs no
  action. It does call the same `lycheetah` parsers and digest functions that
  produced the evidence, so a defect shared by both sides would pass.
- **The witness projection is restated deliberately.** `_recorded_witness_digest`
  restates the harness's witness envelope (`sovereign_harness.py:546-563`)
  instead of importing it. Any drift between the two fails every
  export-then-verify test in `tests/test_guarded_handoff_bundle.py`, so it cannot
  pass silently. The restatement is what lets the verifier notice if the harness
  changes what its digest covers. Left as is.
- **The standing limits remain.** Consensus is synthetic, approval is a declared
  label, the writer is trusted fixed code and the callback is not a sandbox. The
  bundle's `limits` still states all four, and the verifier now requires them.

### H1 — Held

X1, X3, X4 and X6 were refused at HEAD. The existing tests also held at HEAD:

- no overwrite of an existing export, refused before the gateway;
- dangling and evidence symlinks, missing files, an empty directory and
  `../outside`;
- duplicate keys, rehashed output and receipt mutation;
- ten `valid_execution` contradictions, and a completion omitting the write;
- the FIFO manifest;
- the read-only CLI and the digest usage error.

No exported bundle is committed in the repository. `git grep` finds the bundle
schema only in the demo itself, so the stricter verifier invalidates no retained
evidence.

## Verification ledger

| Check | Result |
|-------|--------|
| 19 new tests on the HEAD export | 18 failed, 1 passed (the benign re-witness control). The 18 failures: 15 `assert True is False` (the verifier answered valid), 1 FIFO read by name, 1 `DID NOT RAISE` for `1e400` and 1 RecursionError escaping. None failed on a missing name. |
| `tests/test_guarded_handoff_bundle.py` on the tree | 55 passed |
| Full suite on the tree | `1299 passed, 1 skipped, 1 xfailed, 1 warning in 59.72s`. The warning is the expected non-interactive Agg notice. |
| `repro_batch8.py`, HEAD and tree | the probe table above |
| Frozen and evidence folders | no tracked change (`git status --short`) |
| `py_compile` | demo and tests compile |

## Changed paths

- `examples/guarded_handoff_risk_demo.py`
- `tests/test_guarded_handoff_bundle.py`: 19 cases appended, earlier cases
  unchanged
- `examples/README.md` (D1)
- `CHANGELOG.md`: the "Guarded handoff bundle" group
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch8.py` and this ledger

## Coverage against the RV09 checklist item

| RV09 asks for | Covered by |
|---------------|------------|
| All eight evidence files plus the manifest | read and cross-checked |
| Every cross-link the checklist names | probes and tests |
| Duplicate keys | held |
| FIFOs, symlinks and non-regular paths | G6 |
| Omitted files | held |
| Contradictory reports | G1, G2, G3 |
| No-overwrite behaviour | held |
| The retained-digest boundary and the four standing limitations | B1 |

Not covered:

- the internals of `verify_handoff` and of receipt verification (called, not
  re-read);
- the receipt HMAC path, which the demo leaves unused;
- a live, timed race.

Next workstream: RV10, the chorus.
