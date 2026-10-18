# Failure Museum — Cycle 8

## F-08-1: Apparent temporal query advantage disappears with a fair baseline

Earlier v0.7 four-case fixture: latest-known baseline 2/4, ledger 4/4. Added a fully temporal, independently written SQLite comparator: **SQL 4/4**. The initial benefit was largely a baseline choice, not a demonstrated distinctive temporal-query algorithm. Preserve this negative result in all promotion material.

## F-08-2: Canonical CASCADE still not executable in this environment

The previous repository source was inspected and identity-pinned, but no trusted upstream checkout could be loaded into the local Python runtime. The v0.8 child runner passes tests with an explicitly toy engine only. Do not describe that as canonical validation. Next step is an operator machine with a trusted full checkout and pinned dependencies.

## F-08-3: Process boundary is not a hostile-code sandbox

The subprocess removes direct references to the parent's in-memory ledger, but child Python can still affect accessible filesystem and network. The worker is not isolated by kernel facilities, and no security certification follows from `-I`, hashes or timeouts. Treat optional upstream code as **trusted operator-selected** code, not user-uploaded scripts.

## F-08-4: Agreement with a SQL implementation is not independent truth

Both algorithms consume the same registered documents, approved claims, timestamps and supersession flags. They can agree on the wrong source, invalid approval or fabricated policy. The 1,200 generated comparisons are robust regression tests, not accuracy against external annotation.

## F-08-5: Real neural performance still unmeasured

No local inference endpoint available, no public benchmark downloaded into Python, and no human evaluation completed. The proper next cycle must measure extraction precision/recall, omission, field and scope errors, correct abstention, review burden and latency against independently annotated sources.
