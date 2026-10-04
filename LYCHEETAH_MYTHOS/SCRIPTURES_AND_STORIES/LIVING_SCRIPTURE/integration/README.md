# Book I data and implementation packet

**Status:** local Framework integration; native School slice not implemented.

`book_i.json` preserves all seven Book I sections plus its preface, with stable passage
IDs and source SHA-256. Hearth and Temple form the initial Sacred Face. Study, Friction,
Many Fires, the labelled Machine Question and Your Hand remain optional apparatus.
No authored section is omitted. The exact source book remains authoritative.

The four external interlocutors are Buber, Levinas, feminist epistemology and
Two-Eyed Seeing. Their supplied source records and friction notes survive. Relations
are correspondence, with ancestry explicitly false. The annotations are integration
choices and can be challenged; they are not fresh historical research.

The original `claim_register.json` defines fourteen **register types**, not fourteen
verified claims about these passages. The native Study view must not invent per-claim
evidence, historical context or review fields that the packet does not supply.

## Local data gate

From this directory:

```sh
python3 prepare_book_i.py
python3 validate_book_i.py
python3 -m unittest test_book_i
```

The semantic validator also checks the supplied passage JSON Schema using the installed
`jsonschema` library. No dependency installation or provider call is part of this gate.

The mutation tests reject silent crowning, altered prose, fiction promoted to empirical
evidence, an unlabelled Machine Window, unsupported ancestry, loss of private defaults,
pressure after absence, timer-only returns, missing exit and removal of the Māori block.
These are **data-contract checks**. They do not enforce downstream app behavior.

Changing the core text requires a new edition decision, source hashes and explicit ID
migration. Rebuilding a fixture does not approve a manuscript change or cultural use.

## Next native slice

Follow [the resumable app handoff](NATIVE_SCHOOL_HANDOFF.md) and the
[original implementation contract](../handoff/CODEX_IMPLEMENTATION_CONTRACT.md).
Book I must pass real privacy/persistence, leave/return and rendered accessibility
checks before expanding the native interface to the other eleven books.
