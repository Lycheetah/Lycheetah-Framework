# Opus review — Batch 5: findings register and coverage ledger

Scope: **RV06**, the policy, receipt and gateway-receipt layer of
`lycheetah/assurance/` (`policy.py`, `receipt.py`, `gateway.py`). Working tree
only, branch `review/full-framework-2026-10-20`, HEAD `d7ae0ad`. Nothing is
committed or pushed.

Every finding below was reproduced by `repro_batch5.py` in this folder, run once
against a clean export of HEAD and once against the working tree. Each probe
returns `reproduced=True` when the defect shows and `False` when it does not; a
probe that could not run is reported as an error, never as `False`.

Probe IDs `P01`–`P10` are the function names in `repro_batch5.py`. They are not
the proposal series P1–P11 in the earlier ledgers.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| S01 | High (local suite never finishes; window on the desktop) | FIXED in working tree | `tests/conftest.py` |
| P06 | High (duplicate side effect) | FIXED in working tree | `gateway.py` executor outcome |
| P04 | Medium (verifier overclaims) | FIXED in working tree | `receipt.py` `verify` |
| P05 | Medium (receipt drops caveats) | FIXED in working tree | `gateway.py` receipt limitations |
| P03 | Medium (silent policy corruption) | FIXED in working tree | `policy.py` `TextRule` |
| P08 | Medium (defence in depth bypassed by spelling) | FIXED in working tree | `gateway.py` destructive tripwire |
| P10 | Medium (verifier raises instead of judging) | FIXED in working tree | `receipt.py` `verify` |
| P09 | Medium (secrets at rest) | DOCUMENTED, not changed; design decision for Mac | ledger, checkpoint payload |
| P07 | Low (misleading reason) | OPEN, observation | `gateway.py` result checkpoint |
| P01 | — | HELD: no defect | policy digest coverage |
| P02 | — | HELD: no defect | list fields given as a bare string |

### S01 — The full suite opened a matplotlib window on the desktop and waited for a person to close it (MEASURED, FIXED)

Found while running this batch, not by a probe.
`14_MYSTERY_SCHOOL/implementations/visualization_system.py` calls `plt.show()`
whenever no `save_path` is given (lines 109, 157, 218, 289, 336).
`tests/test_threads_fixes.py::test_visualizer_export_all_data_uses_timeseries_schema`
calls `plot_drift_over_time` without one.

On this machine (`DISPLAY=:1`, matplotlib 3.11.1, default backend `gtk3agg`), that
opened a real window, and pytest sat in the GTK loop. The process was in state `S`,
waiting in `poll_schedule_timeout`, with display sockets open.

- The Batch 4 full suite reached 1,089 passed at 90% and then made no progress for 25 minutes.
- The separate issuer-test run blocked on the same file for over 600 s.

A headless CI runner has no display, so CI could not see this. Only a run on a
desktop hangs. The Batch 3 full-suite timeout (exit 124, quiet output) stopped at
the same point: one dot past the 90% mark. That makes the window its cause too
(DERIVED).

Fix: `tests/conftest.py` sets `MPLBACKEND=Agg` before anything imports
matplotlib. Subprocess tests inherit it. `matplotlib` is not in `sys.modules` after
pytest starts, so the variable takes effect. With the fix, the stalled test
passes in 0.78 s, and matplotlib's own warning that `FigureCanvasAgg` is
non-interactive confirms that `show()` did not open a window. The module keeps
its interactive `show()`: it is a demo, and it behaves correctly when a person
runs it.

### P06 — An executor answer that was neither success nor failure was recorded as FAILED, so a retry called the provider again (MEASURED, FIXED)

On HEAD the gateway treated every executor answer other than `"success"` as a
definite failure. A provider that answers `{"status": "pending"}` or
`{"status": "accepted"}` may already have acted. Recording it as `FAILED` closes
the effect, and the next `execute` of the same action dispatches again.

| Run | First call | Retry |
|-----|-----------|-------|
| HEAD, `{"status": "pending"}` | `FAILED` | provider called again (1 call) |
| Tree, `{"status": "pending"}` | `UNKNOWN:uncertain_outcome` | `BLOCKED:prior_effect_unresolved`, 0 calls |
| Tree, control `{"status": "failure"}` | `FAILED` | `SUCCEEDED` (retry allowed) |

Fix: only `"success"` and `"failure"` are definite. Anything else, including a
missing status or a typo, is `UNKNOWN` and stays held for `reconcile` (the Batch 4
path). A comment at the decision names why.

This is the same class as Batch 4 R01: a side effect whose outcome is not known
must never be retried blind.

### P04 — `verify()` accepted receipts that the published schema rejects (MEASURED, FIXED)

An unsealed receipt's digest can be recomputed by anyone, so the digest cannot be
what keeps a malformed body out. On HEAD `verify()` checked the digest and the
seal only. With the digest recomputed, it returned `valid` for seven bodies that
`schemas/` rejects:

`lineage_empty`, `previous_digest_not_hex`, `trace_id_not_string`, `event_empty`,
`event_phase_unknown`, `policy_empty`, `policy_digest_not_hex`.

It also accepted `issued_at = "next tuesday"`. So did the local schema validator:
see Note 1.

Fix: a new `_shape_errors()` runs on every verify. It checks that:

- `issued_at` is RFC 3339;
- `policy` has a string id and version and a SHA-256;
- `event` has an `event_id`, a phase of `input`, `output` or `tool`, a subject name and SHA-256, and a boolean `replayable`;
- `lineage` has a string `trace_id` and a `previous_receipt_sha256` that is `None` or a SHA-256.

The tree rejects all eight bodies, and the untouched control still verifies.

### P05 — The gateway receipt dropped the runtime's caveats (MEASURED, FIXED)

On HEAD the receipt that `ActionGateway.execute` issued carried one limitation,
`local_execution_cell_boundary`. The runtime's own receipt for the same event
carries seven. The dropped caveats include that `human_approved` is
caller-declared and that an HMAC is required for authenticity. The gateway
receipt said `human_approved: true` with neither caveat beside it.

Fix: the gateway receipt now carries
`(*self.runtime._limitations(event_record), "local_execution_cell_boundary")`.

### P03 — `TextRule.from_dict` turned a missing field into the text "None" (MEASURED, FIXED)

On HEAD, `from_dict` passed `id`, `pattern`, `title`, `description` and
`status_basis` through `str()`:

- `pattern: null` compiled into a rule matching the literal text `None`.
- `title: null` became the title `"None"`.
- An integer id such as `12345` was accepted.

A policy file with a missing field loaded without complaint and enforced
something nobody wrote. (`id: 5` was refused even on HEAD, by the id regex.)

Fix: the constructor requires all five fields to be strings, and `from_dict` no
longer coerces them. The error reads "text rule id, pattern, title, description
and status_basis must be strings".

### P08 — The destructive-command tripwire matched one spelling (MEASURED, FIXED)

On HEAD the tripwire caught `rm -rf /` and the canonical fork bomb. It missed 7 of
9 variants:

- `rm -fr /`
- `rm -r -f /`
- a doubled space
- long flags
- `--no-preserve-root`
- an argv list `["rm", "-fr", "/"]`
- a spaced fork bomb

Fix: `_destructive_command` works as follows.

- It splits each command string on `;`, `&`, `|` and newlines.
- It finds `rm` or any `*/rm`.
- It treats `--recursive`, or a short flag cluster containing `r`, as recursive, and honours `--`.
- It blocks when a recursive removal targets a path starting with `/`, `~`, `$HOME` or `${HOME}`.
- Fork bombs are matched by a back-referenced name, so `bomb(){ bomb|bomb& };bomb` is caught too.

The docstring states the boundary: this is a tripwire, not a sandbox, and the
policy's tool allowlist is the control.

Controls that stay allowed:

- `rm -rf ./build`
- `rm -f /tmp/one-file` (not recursive)
- `ls -r /`
- `echo rm`
- `grep -r x .`

Known safe-side false positive: the prose "docs say never run rm -rf / on prod"
is blocked, on HEAD and on the tree alike. A recursive removal of any absolute
path, such as `rm -rf /tmp/cache`, is blocked, as it was on HEAD.

### P10 — `verify()` raised on a non-ASCII digest (MEASURED, FIXED)

On HEAD, a digest of 64 non-ASCII characters reached `hmac.compare_digest`, which
raised `TypeError: comparing strings with non-ASCII characters is not
supported`. A verifier that raises can be read by a caller as "could not check"
instead of "invalid".

Fix: the digest shape is checked first. A malformed digest returns
`integrity.digest must be 64 lowercase hexadecimal characters`. With a seal
present, it also returns "HMAC seal cannot be checked against a malformed
digest" instead of attempting the compare. `_is_sha256` is now safe for
non-string input.

### P09 — Sensitive arguments and provider answers are stored raw at rest (MEASURED, DOCUMENTED)

The probe ran an approved action with a sentinel under a sensitive key
(`api_key`) and a sentinel in the provider's output.

| Location | Argument sentinel | Output sentinel |
|----------|-------------------|-----------------|
| Receipt | redacted | absent |
| `authority/authority.sqlite3` | absent | absent |
| `ledger/guard.sqlite3` | **raw** | **raw** |

The checkpoint payload is the audit events since the last anchor
(`checkpointed_workflow.py:153`), and each event carries `details_json`. The HTTP
client POSTs `{"anchor", "events"}` (`checkpoint_authority.py:524`). Provider
result details are therefore transmitted to a remote authority (DERIVED from
code). The reference `CheckpointStore` does not persist them (MEASURED, local),
but a third-party authority or a proxy that logs request bodies would.

The ledger needs the full action to re-evaluate it at dispatch time, so this is
not changed here. `README.md` now says plainly that redaction applies to receipts
only, and that the ledger directory and the authority hold secrets. The design
question is Proposal 13 below.

### P07 — An unserialisable provider result is held for reconcile under the wrong reason (MEASURED, OPEN, Low)

A provider result containing a `datetime` or `NaN` cannot be checkpointed. The
gateway fails closed, which is correct: the result is `UNKNOWN`, the effect stays
`DISPATCHING`, and it waits for `reconcile`. But the reason given is
`result_not_checkpointed_requires_reconciliation`. The underlying cause is
`invalid_result_details`, so an operator reading the reason looks for an outage
that never happened. See Proposal 12 below.

### P01, P02 — What held (MEASURED on HEAD and on the tree)

| Probe | Result |
|-------|--------|
| P01 policy digest coverage | Changing any policy field changes the policy digest. `reproduced=False` on both. |
| P02 bare-string list fields | A list field given as a bare string is refused, not iterated character by character. `reproduced=False` on both. |

## Notes

1. **The local schema validator does not check `date-time`.** `jsonschema`
   enforces `format` only when a format checker is installed, and none is installed
   here. The schema validator therefore accepted `issued_at = "next tuesday"`. A
   test that relies on the schema validator alone cannot catch a bad timestamp.
   `verify()` now checks RFC 3339 itself, using `datetime.fromisoformat` after
   normalising `Z`.
2. **The Batch 4 full suite overlapped these edits and did not finish.** Run
   `bbmafc9on` started on the Batch 4 tree before any Batch 5 edit. Most test
   modules imported `lycheetah` at collection time and so ran Batch 4 code. Tests
   that spawn a subprocess would have loaded Batch 5 code. It reached 1,089 passed,
   0 failed, 0 errors and 1 xfailed, then blocked on S01 and was stopped. Those
   counts and the caveat are in the Batch 4 ledger. A clean full-suite run on the
   Batch 4+5 tree is recorded below.
4. **Process note.** Stopping the overlapping run with `pkill -f <pattern>` also
   killed the shell that issued it, because the pattern was in its own command
   line. The same trap made a later `pgrep -f` report a "leftover" process that was
   only itself. Stop by PID.
3. **`import json` was removed from `gateway.py`.** It was used only by the old
   substring tripwire. The focused suite exercises every gateway path and passes.

## Proposals for Mac (not applied)

- **Proposal 12 — precise reason for an unserialisable result (P07).** Report
  `invalid_result_details_requires_reconciliation` when the result could not be
  serialised, and keep the outage reason for a real checkpoint failure. The
  outcome does not change: it stays `UNKNOWN` and held. This changes a public
  reason string, so it is Mac's call.
- **Proposal 13 — secrets at rest (P09).** Options:
  - (a) Keep the current behaviour, now documented. This is the default.
  - (b) Store sensitive argument values in the ledger as a keyed hash plus an
    encrypted blob, decrypted only at dispatch.
  - (c) Exclude `details_json` for provider results from the checkpoint payload
    and checkpoint only its digest.

  Option (c) is the smallest change that keeps provider answers off the wire. It
  changes the checkpoint format, so it would need a version bump.

## Tests added

`tests/test_receipt_shape_and_gateway_outcomes.py` (NEW, 38 items):

| Test | Items | Pins |
|------|-------|------|
| `test_verify_rejects_a_body_the_published_schema_rejects` | 8 | P04; the untouched body verifies first |
| `test_verify_returns_a_verdict_for_a_non_ascii_digest` | 2 | P10, unsealed and sealed |
| `test_text_rule_refuses_non_string_fields` | 5 | P03 via `from_dict` |
| `test_text_rule_constructor_refuses_non_string_title` | 1 | P03 at the constructor |
| `test_unrecognised_executor_status_is_uncertain_not_failed` | 3 | P06: `pending`, `accepted`, `{}`; retry BLOCKED with 0 calls |
| `test_gateway_receipt_keeps_the_runtime_caveats` | 1 | P05 |
| `test_destructive_tripwire_ignores_spelling` | 13 | P08 variants |
| `test_destructive_tripwire_leaves_ordinary_commands_to_policy` | 5 | P08 controls |

## Verification (MEASURED)

| Probe | HEAD reproduced | Tree reproduced |
|-------|-----------------|-----------------|
| P01 policy digest coverage | False | False |
| P02 bare-string list fields | False | False |
| P03 text rule coercion | True (`None` → `"None"`, `12345` accepted) | False |
| P04 verify vs published schema | True (7 bodies + bad `issued_at` valid) | False |
| P05 gateway receipt limitations | True (1 of 7 kept) | False |
| P06 unrecognised status | True (`FAILED`, retry calls 1) | False (`UNKNOWN`, retry BLOCKED, 0 calls) |
| P07 unserialisable result | False (fails closed; reason imprecise) | False (unchanged) |
| P08 destructive tripwire | True (7 of 9 missed) | False |
| P09 secret at rest | observation (`None`) | observation (`None`) |
| P10 non-ASCII digest | True (`TypeError`) | False |

- **New test file, tree:** 38 passed.
- **New test file, HEAD export:** 29 failed, 9 passed. All 29 are assertion
  `FAILED`, none `ERROR`, so every test ran. `lycheetah.__file__` resolved under
  the HEAD export. The 9 passes are expected:
  - the 5 ordinary-command controls;
  - 4 variants HEAD already caught: `rm -rf /`, `rm -rf /tmp/cache`, `sudo /bin/rm -Rf /etc` and the canonical fork bomb.
- **Focused suite, tree:** 312 passed, 1 skipped in 25.60 s. This covered 19
  files: `test_assurance*`, `test_gateway*`, `test_receipt*`, `*guard*`,
  `*checkpoint*`, `*runtime*` and `*workflow*`.
- **Other receipt issuers' tests:** these are the five files outside the focused set
  that reference the other issuers:
  - `test_consensus_anchor_and_registration`
  - `test_entry_points`
  - `test_consensus_integrity`
  - `test_optional_dependencies`
  - `test_threads_fixes`

  A separate run of them was stopped because it overlapped the Batch 4 suite, and
  it was already blocked on the S01 window. They are covered by the full run below.
- **Full suite, Batch 4+5 tree:** MEASURED on the Batch 4 + 5 + conftest tree: `1241 passed, 1 skipped, 1 xfailed, 1 warning in 57.27s`, exit 0. The one warning is the expected non-interactive Agg notice. This is the first complete local full run of the review

## Coverage ledger (Batch 5)

| RV06 dimension | Evidence | Verdict |
|----------------|----------|---------|
| Policy digest covers its fields | P01 | HELD |
| Policy field types | P02, P03; 6 tests | P02 HELD; P03 FIXED |
| Receipt verify vs published schema | P04; 8 tests; Note 1 | FIXED |
| Digest and seal robustness | P10; 2 tests | FIXED |
| Receipt caveats carried by the gateway | P05; 1 test | FIXED |
| Executor outcome classification | P06; 3 tests | FIXED |
| Unserialisable provider result | P07 | HELD fail-closed; reason OPEN (Proposal 12) |
| Destructive-command tripwire | P08; 18 tests | FIXED; documented as a tripwire, not the control |
| Sensitive keys at rest and in transit | P09; README | DOCUMENTED; design OPEN (Proposal 13) |
| Other issuers (`evaluation`, `in_toto`, `cli`, `finality`, `otel`, examples, MCP guard) | Their existing tests | See the issuer row above. Source not re-read line by line in this batch. |
| Receipt chains across receipts (`previous_receipt_sha256` linkage) | Shape only | NOT COVERED: verify checks the field's form, not that it names a real predecessor |
| HMAC key management and rotation | — | NOT COVERED in this batch |

## Changed paths (Batch 5, working tree only)

- `lycheetah/assurance/receipt.py`: shape check before compare, `_shape_errors`, `_is_rfc3339`, a non-string-safe `_is_sha256`
- `lycheetah/assurance/policy.py`: `TextRule` string fields, no coercion in `from_dict`
- `lycheetah/assurance/gateway.py`: `_destructive_command` tripwire, a definite outcome only for `success` and `failure`, runtime limitations in the receipt
- `README.md`: the executor answer contract, and receipt-only redaction with secrets at rest
- `tests/conftest.py`: `MPLBACKEND=Agg` so no test opens a window (S01)
- `tests/test_receipt_shape_and_gateway_outcomes.py` (NEW)
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch5.py` (NEW)
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH5_FINDINGS_AND_LEDGER.md` (NEW, this file)
