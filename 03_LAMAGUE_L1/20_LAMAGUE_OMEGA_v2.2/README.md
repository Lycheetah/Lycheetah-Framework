# LAMAGUE Ω v2.2 — Omega compiler, File Airlock, Guarded Handoff

Built by Aetheron (Gemini 4 Argon) in its isolated forge, falsified and promoted by Sol (Claude Opus),
for Mackenzie Conor James Clark and the Lycheetah Framework. 2026-10-25.

| Module | What it is | Status |
|---|---|---|
| `file_airlock/` | Snapshot a directory, check an agent's writes against allow/forbid globs and its handover note, roll back byte-exact | Tool. Refuses to write through symlinks or outside the root; restores modes and empty dirs |
| `guarded_handoff/` | Ed25519 single-use action permits (human holds the private key, seats hold the public key), flock-locked consumed-permit ledger that fails closed, Python AST diff audit, git working-tree audit | Tool. Non-`.py` files are reported `NOT_AUDITED`, never passed |
| `lamague_omega/` | LAMAGUE Ω v2.2 compiler and 20 evidential discourse roots (100 free roots + 35 bound modifiers) | Draft language work, see limits |
| `continuity_prover/`, `question_governance/` | Continuity compaction, handover tamper and question-ordering simulations | **Illustrative only.** The naive baseline is scripted to lose fields; the 2^3 factorial is a toy model with each factor wired to its own metric; external-file checks print `DID_NOT_RUN` when their paths are absent |

## Honest limits

- **Decodability.** With a word-final boundary marker on every codeword the 135-morpheme stream is a
  comma code, which is uniquely decodable whenever the words are distinct. That is all it shows. The
  **raw unframed stream is NOT uniquely decodable** (Sardinas–Patterson witness: `in`). Spoken use
  therefore assumes an audible word boundary, an untested phonological assumption.
- **The English ⇄ LAMAGUE translator is a five-slot classifier, not a lossless translator.** Different
  sentences can map to the same utterance. The witnessed evidential `vira` is emitted only with a
  `{path, sha256}` receipt that re-hashes on disk; the default is `kura` (unknown). A grant
  (`periva veka`) requires a verified signed permit; push/release/publish/deploy/delete/merge are `riska`.
- Tests were written by the building seat; the guards were mutation-checked (each reverted guard turns
  a test red) and attacked independently by a second seat. That is not external validation.

## Run

```bash
python3 -m pytest 03_LAMAGUE_L1/20_LAMAGUE_OMEGA_v2.2 -q   # 73 tests; needs `cryptography` (a project dependency)
```

These live outside `testpaths`, so the main suite does not collect them; run them explicitly.
