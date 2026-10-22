# lamague check

**One command. No dependencies, no account, no notation to learn.**

**Reviewed:** 21 October 2026. Empty or unrelated symbol keys no longer match
every protected field. Short fragments of an alias do not count as that alias.

**Reviewed again:** 22 October 2026. `false`, and lists or objects holding only
placeholders, are gaps now. A suffix must be whole words, so `disclaim` is not a
claim, and a key that denies its field (`no_rollback`, `without_dissent`) does
not carry it. The record's own top-level field beats a nested one of the same
name.

```bash
python3 lamague_check.py your-record.json
python3 lamague_check.py --demo            # see it work on an ordinary incident report
```

## What it does

Reads any JSON decision record and reports which of ten accountability fields it
still carries:

```text
purpose · claim · unknowns · invariants · authority
participants · affectedParties · dissent · valueFlow · recovery
```

These are the codec's own `CRITICAL_FIELDS` — the ten whose deletion
`22_REVERSIBLE_COMPRESSION_v1.0` detects 324 times out of 324.

## Why it reads your field names, not ours

Nobody's incident report has a field called `affectedParties`. So it maps
aliases: `impacted_users`, `blast_radius`, `stakeholders`, `rollback`,
`open_questions`, `approved_by`, `objections`. Point it at a file you already
have.

Measured on the built-in demo — a plausible incident report using none of this
project's vocabulary:

```text
✓ purpose           found as "rationale"
✓ authority         found as "approved_by"
✓ recovery          found as "rollback"
⚠ affectedParties   "impacted_users" is present but empty
✗ dissent           no field found under any known name
✗ valueFlow         no field found under any known name

6/10 protected fields carried
```

And on a real LAMAGUE packet: **10/10, no gaps.**

## In CI

```bash
python3 lamague_check.py record.json --strict   # exit 1 on any gap
```

## What it does not do

It does not check whether populated fields are *true*, *complete*, or *honest*.
Missing, empty and placeholder values are reported as gaps and fail `--strict`.
A populated dissent field can still be false or incomplete; the tool cannot
establish whether it represents the people affected by a decision.

It reads nested fields too, so when a record has no `owner` of its own, a
dependency's `owner` can stand in for its authority. The report prints the path
it used (`found as`), so check that path before trusting the tick.

Presence is the floor. It is also the thing that silently disappears when a
decision travels upward, which is why it is worth a check.
