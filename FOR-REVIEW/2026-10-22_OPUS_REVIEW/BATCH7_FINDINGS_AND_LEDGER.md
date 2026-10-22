# Opus review — Batch 7: findings register and coverage ledger

Workstream: **RV08, exact codec and consent preservation.** Branch
`review/full-framework-2026-10-20`, HEAD `d7ae0ad`, working tree uncommitted.
Nothing was committed or pushed. The frozen folder
`03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` is byte-for-byte unchanged in git
(`git status --short` empty); its corrections are staged as a patch only.

Method: `repro_batch7.py` loads the maintained codec and the frozen codec by file
path and runs the same probes against the HEAD export and the working tree. New
tests were copied into the HEAD export with `lycheetah` resolving there, and must
fail on HEAD and pass on the tree. The probe now sets `sys.dont_write_bytecode`,
so it cannot leave bytecode beside a sealed manifest.

## Findings register

| ID | Severity | Status | Where |
|----|----------|--------|-------|
| K1 | High (consent changed meaning across a round trip) | HELD in the maintained codec (repair predates this review); frozen counterexample PRESERVED and reproduced | `codec.py` `validate_packet`; frozen `src/lamague_codec.py` |
| W2 | Medium (one wire, two readings: the raw text shows one claim, the decoder returns another) | FIXED in working tree | `codec.py` `decode` |
| W1, W3–W7 | Medium (malleable wire: many wires per packet; an extra array item dropped without notice) | FIXED in working tree | `codec.py` `decode` |
| U1 | Medium (crash instead of a codec error; a wire that cannot be written as UTF-8) | FIXED in working tree | `codec.py` `_require_string` |
| T2 | Medium (published overclaim; the installable package ships the unrepaired codec) | STAGED patch, not applied; Proposal 16 for Mac | frozen `README.md`, `pyproject.toml`, `examples/agent_state_compaction.py` |
| A1 | Medium (archive integrity: the sealed folder no longer matches its seal) | MEASURED, DOCUMENTED; decision for Mac | frozen `SHA256_MANIFEST.json` |
| N1 | Low (boundary) | MEASURED, DOCUMENTED | no Unicode normalisation |
| L1 | — | Lead for the packaging pass | `lycheetah/__init__.py` import graph |
| K2, K3 | — | HELD: no defect | consent sweep, corpus round trip |

### W1–W7 — The decoder accepted wires `encode` never emits (MEASURED, FIXED)

Base wire: corpus packet 0, mutated seven ways. On HEAD the maintained codec and
the frozen codec accepted all seven, and none re-encoded to its source.

- W1 and W2: a repeated key. `json.loads` keeps the last value, so W2 (a second
  `"c":"INJECTED"` appended at the end) decoded the claim `INJECTED` while the
  original claim stayed first in the text. Anyone reading the wire with a
  first-value parser, a log search or their own eyes sees one claim; the decoder
  and the hash see another.
- W3: an extra element in an evidence item. `_expand_object` reads arrays by
  position (`item[0]`, `item[1]`, …), so the extra element vanished.
- W4, W5: added whitespace, reordered keys.
- W6, W7: a protected flag of `1.0` or `true`. The test
  `item[1] in (0, 1, False, True)` admits both through Python equality.

Fix, one rule: `decode` re-encodes the decoded packet with the active codebook
and refuses unless the bytes equal the source. It covers every non-canonical
form, including ones no probe named: an escaped letter, or a codebook string
written out in full in an `L1D` wire. A repeated key is caught earlier by an
`object_pairs_hook`, so the error names the key. Cost: one extra `encode` per
`decode`, linear in packet size.

Compatibility (MEASURED): for all 36 corpus packets, in both modes, the
maintained encoder and the frozen v1.0 encoder emit identical bytes, and the
maintained decoder returns each packet unchanged. That is a test now, so v1.0
wires keep decoding. The CLI strips surrounding whitespace before it decodes
(`lycheetah/cli.py:453`), so a wire file with a trailing newline still works.
The hand-built wire in `tests/test_compaction.py:121` still gets its
out-of-range error, because that check fires first.

The cost: a transport may no longer re-serialise a wire. Pretty-printing or
ASCII-escaping it now fails loudly, where before a different string silently
carried "the same" packet. That is the right property for an envelope that
carries a hash.

Not probed: the frozen `browser/index.html` decoder. JavaScript `JSON.parse` also
keeps the last duplicate key (from memory, not checked against that file).
UNVERIFIED.

### U1 — A lone surrogate passed validation, then crashed hashing (MEASURED, FIXED)

`_require_string` checked only type and emptiness. A claim of
`"Dry run \ud800"` passed `validate_packet` and `encode`. Then `full_hash`,
`critical_hash` and `classify` raised `UnicodeEncodeError` rather than
`CodecError`, so `classify` could not return UNDECODABLE. The resulting wire
cannot be written to a UTF-8 file.

Fix: `_require_string` refuses a string that does not encode as UTF-8. Every
packet string and every codebook entry passes through it, so one change covers
validation, both encoders, decoding, both hashes and `classify`. After the fix,
`validate_packet`, `encode` and `full_hash` raise `CodecError`, and `classify`
returns UNDECODABLE. The frozen codec still crashes.

### K1–K3 — Consent preservation (MEASURED)

- K1: in both modes the maintained codec refuses a literal `R`, `I` or `N` at
  `encode`, so the repair holds. The frozen codec turns `R` into `REVOCABLE`,
  `I` into `IRREVOCABLE` and `N` into `NONE`, and both the full and the critical
  hash change. The counterexample is preserved, and `repro_batch7.py`
  reproduces it.
- K2: a 14-value consent sweep across three modes. No value changed or failed
  in either codec.
- K3: all 36 corpus packets round-trip in both modes on both codecs.
- DERIVED: the corpus uses one consent value, `REVOCABLE`. The 36/36 round-trip
  headline was therefore structurally blind to K1. A passing corpus is evidence
  for its own values, not for every admitted value.

### T2 — Post-seal surfaces claim a proof, and the package installs the unrepaired codec (MEASURED, STAGED)

Commit `dfe7c55` (2026-08-08, "Bridge 1: make the codec installable") came five
days after the seal. It rewrote the frozen README and added `pyproject.toml`
(package `lamague-codec` 1.0.0) and `examples/agent_state_compaction.py`.

- The README says it "**structurally impossible** to drop" the accountability
  fields. `encode` accepts a packet with no authority, no dissent and no
  recovery; only the declared safety rules are enforced.
- It says the hash "proves to a third party they survived". A digest shows
  equality with a reference only to someone who holds that reference from
  another source, and it cannot show the fields were complete or true.
- It says `decode(encode(packet))  # == packet, exactly`, which is false for
  this code (K1). It pitches "a provable floor" and tells readers to
  `pip install` this folder, which installs the v1.0 codec with K1, W1–W7 and
  U1.
- The sealed `docs/CLAIM_BOUNDARY.md` is more careful than the pitch. It lists
  "Proof that the protected field set is complete" as **not earned**.

Staged: `RV08_frozen_post_seal_claims.patch`. It covers README, the pyproject
description and comment, and three lines of the example. It names the three
known defects, says the install carries them, and points to the maintained
codec. `git apply --check` passes and the patch was **not applied**. The staged
example compiles.

The sealed `docs/CODEC_SPEC.md:55`, `article/ARTICLE_DRAFT.md:95` and
`docs/CLAIM_BOUNDARY.md` ("encoded and decoded exactly") were left untouched.
They are the recorded counterexample. `33_APPLICATIONS/BRIDGE_2026-08-08.md:91`
is a dated record of what was done that day and was also left as history.

### A1 — The sealed folder no longer matches its seal (MEASURED)

The manifest was sealed in `a38fec6` (2026-08-03) with 28 entries, each
`{bytes, sha256}`. A structure-aware check gives:

- 25 entries match.
- `README.md` differs. The sealed version is 1315 bytes, and its digest matches
  the `a38fec6` blob. The current file is 4563 bytes, rewritten by `dfe7c55`.
- Two sealed entries are `__pycache__/*.cpython-313.pyc` files. They are absent,
  and `.gitignore:2` ignores them, so no clone can ever re-verify this seal: it
  seals build byproducts.
- Three tracked files are unsealed: `00_CODEX_ORIENTATION.md`,
  `examples/agent_state_compaction.py` and `pyproject.toml`.
- No maintained gate checks this manifest. The only code naming
  `SHA256_MANIFEST` is `33_APPLICATIONS/compression_vs_gzip.py` (DERIVED from a
  grep over `.py`, `.mjs`, `.sh`, `.toml` and `.yml`).
- An untracked, ignored `src/__pycache__/lamague_codec.cpython-312.pyc` is dated
  2026-10-21 08:41 +1300. That is 19 hours before `repro_batch7.py` existed, so
  this batch did not write it. Its origin is UNVERIFIED. The new test executes
  the frozen source without writing bytecode.
- Correction to my own first pass: an early reading of "all 28 DIFF" was my
  parser comparing a dict to a string. RETRACTED.

### N1 — Text is preserved code point for code point (MEASURED, DOCUMENTED)

`Café` in NFC and in NFD are different strings with different critical hashes.
The NFD packet round-trips exactly. An exact codec should not normalise, but two
packets that read identically to a person can carry different digests. Anyone
comparing digests across systems must normalise before hashing.

### L1 — Importing the stdlib-only codec imports the whole package (lead)

Under `python3 -I`, `from lycheetah.compaction.codec import …` fails on
`numpy`. `lycheetah/__init__.py:91` eagerly imports `sovereign_harness`, which
imports `consensus`, which imports `core.grey_mode` from `12_IMPLEMENTATIONS/`
through a path bridge. `numpy` is a declared dependency (`pyproject.toml:34`), so
this is not a defect. But the codec itself cannot be imported alone. Carried to
the packaging and synthesis pass.

## Proposal 16 — One installable codec (for Mac)

Sol's call: **A now, B only if the standalone package matters as a product.**

- **A.** Apply the staged patch, so the frozen folder's own post-seal pages say
  what they install and point to `lycheetah.compaction.codec`. Do not publish
  `lamague-codec` 1.0.0 as it stands. One truth, one implementation: the second
  installable codec has already drifted from the first.
- **B.** Cut `lamague-codec` 1.0.1 in a new versioned folder, carrying the
  maintained validation and strict decode, with its own manifest. v1.0 stays
  sealed as the counterexample. This is the open "frozen patches as new
  versions" decision.
- **C.** Restore the sealed README, which reverts the README half of `dfe7c55`.
  That puts the folder back inside its seal, but it drops the install story Mac
  approved on 2026-08-08.

Whether `lamague-codec` was ever published to a package index is UNVERIFIED.
No network check was made.

## Coverage against the RV08 checklist

| Asked | Done |
|---|---|
| Compare maintained and frozen codecs | Read both in full. They differ in docstrings, the consent refusal, an explicit protected-flag loop, and `classify` (Batch 6). After this batch they also differ in strict decode and the Unicode check. |
| Literal R, I, N in consent, packet and hash values | K1 in both modes on both codecs |
| Both wire modes | `L1` and `L1D` in K1, K2 and K3, the corpus compatibility test, and the literal-codebook-string test |
| Every admitted value | 14-value consent sweep. Consent is free text, so "every" means every class: reserved letters, the three named values, other strings. Risk and operation codes are closed sets checked by `RISK_DECODE` and `VALID_OPS`. |
| Lossless packet scope | 36/36 corpus, plus the canonical-wire rule, so a decoded packet now has exactly one wire |
| Malformed input | W1–W7, U1, the literal codebook string. W8 (top-level codebook reference) did not apply to the base wire and is covered by the `L1D` test instead. |
| Backward compatibility | The frozen and maintained encoders emit byte-identical corpus wires in both modes; v1.0 wires decode unchanged |
| Preserve the frozen counterexample | Frozen folder unchanged. K1 and U1 reproduce on it. Corrections are staged only. |

## Verification (MEASURED)

- HEAD export, `lycheetah` from the export:
  `tests/test_compaction_wire_canonical.py` gave `11 failed, 3 passed in 0.68s`.
  All nine malformed wires, the literal codebook string and the Unicode case
  failed. The canonical control and both corpus-compatibility cases passed.
- Working tree, four compaction files (`test_compaction_wire_canonical.py`,
  `test_compaction.py`, `test_compaction_consent_roundtrip.py`,
  `test_compaction_drift_boundaries.py`): `74 passed in 0.94s`.
- Full suite on the tree: `1280 passed, 1 skipped, 1 xfailed, 1 warning in
  56.64s` (1266 + 14). The exit code was not captured; the summary line shows no
  failure or error. The one warning is the expected non-interactive Agg notice.
- The committed reading copies `docs/lamague-handover-report.json` and
  `docs/lamague-handover.html` were regenerated through the demo's flags for the
  new codec digest. The pinned-copy test passes inside the full suite.
- After the fix, `repro_batch7.py` on the tree shows eight changed rows: W1–W7
  and U1. Its output was byte-identical before and after the bytecode switch.
- `py_compile` passes on `lycheetah/compaction/codec.py` and on the staged
  example.

## Changed paths

- `lycheetah/compaction/codec.py`: `_require_string` refuses text that is not
  valid Unicode; new `_reject_duplicate_keys`; `decode` takes the duplicate-key
  hook, re-encodes to check the wire is canonical, and has a docstring stating
  both.
- `tests/test_compaction_wire_canonical.py`: new, 14 cases.
- `docs/lamague-handover-report.json`, `docs/lamague-handover.html`: regenerated.
- `CHANGELOG.md`: a "Compact wire" bullet group in the 22 October subsection.
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch7.py`: new; bytecode-free.
- `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV08_frozen_post_seal_claims.patch`:
  staged, **not applied**.
- This ledger.

## Open for Mac

Proposal 16 (A, B or C), and A1: leave the seal as history, or restore the
sealed README. The open "frozen patches as new versions" decision now has a
concrete first case.

## Probe table (MEASURED)

`←` marks a row that changed between HEAD and the working tree. The frozen rows
are identical on both, as they must be.

| Probe | Codec | Mode / literal | HEAD `d7ae0ad` | Working tree |
|---|---|---|---|---|
| K1 | frozen | L1 I | encode ok, decode ok, consent_after IRREVOCABLE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after IRREVOCABLE, full_hash_kept False, critical_hash_kept False |
| K1 | frozen | L1 N | encode ok, decode ok, consent_after NONE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after NONE, full_hash_kept False, critical_hash_kept False |
| K1 | frozen | L1 R | encode ok, decode ok, consent_after REVOCABLE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after REVOCABLE, full_hash_kept False, critical_hash_kept False |
| K1 | frozen | L1D I | encode ok, decode ok, consent_after IRREVOCABLE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after IRREVOCABLE, full_hash_kept False, critical_hash_kept False |
| K1 | frozen | L1D N | encode ok, decode ok, consent_after NONE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after NONE, full_hash_kept False, critical_hash_kept False |
| K1 | frozen | L1D R | encode ok, decode ok, consent_after REVOCABLE, full_hash_kept False, critical_hash_kept False | encode ok, decode ok, consent_after REVOCABLE, full_hash_kept False, critical_hash_kept False |
| K1 | maintained | L1 I | encode CodecError | encode CodecError |
| K1 | maintained | L1 N | encode CodecError | encode CodecError |
| K1 | maintained | L1 R | encode CodecError | encode CodecError |
| K1 | maintained | L1D I | encode CodecError | encode CodecError |
| K1 | maintained | L1D N | encode CodecError | encode CodecError |
| K1 | maintained | L1D R | encode CodecError | encode CodecError |
| U1 | frozen | —  | encode ok, validate ok, full_hash UnicodeEncodeError, classify UnicodeEncodeError | encode ok, validate ok, full_hash UnicodeEncodeError, classify UnicodeEncodeError |
| U1 | maintained | —  | encode ok, validate ok, full_hash UnicodeEncodeError, classify UnicodeEncodeError | encode CodecError, validate CodecError, full_hash CodecError, classify ok ← |
| W1_dup_key_first | frozen | —  | accepted | accepted |
| W1_dup_key_first | maintained | —  | accepted | CodecError ← |
| W2_dup_key_last | frozen | —  | accepted (claim `INJECTED`) | accepted (claim `INJECTED`) |
| W2_dup_key_last | maintained | —  | accepted (claim `INJECTED`) | CodecError ← |
| W3_extra_array_element | frozen | —  | accepted | accepted |
| W3_extra_array_element | maintained | —  | accepted | CodecError ← |
| W4_whitespace | frozen | —  | accepted | accepted |
| W4_whitespace | maintained | —  | accepted | CodecError ← |
| W5_keys_reordered | frozen | —  | accepted | accepted |
| W5_keys_reordered | maintained | —  | accepted | CodecError ← |
| W6_protected_float | frozen | —  | accepted | accepted |
| W6_protected_float | maintained | —  | accepted | CodecError ← |
| W7_protected_true | frozen | —  | accepted | accepted |
| W7_protected_true | maintained | —  | accepted | CodecError ← |
| W8_l1d_literal_for_entry | frozen | —  | not applicable to the base packet | not applicable to the base packet |
| W8_l1d_literal_for_entry | maintained | —  | not applicable to the base packet | not applicable to the base packet |

