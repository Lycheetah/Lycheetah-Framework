# Packaging and reproduction boundary

**Status: SCAFFOLD integration; original results remain supplied historical evidence until locally reproduced.**

The original 4 October handoff and all its supplied manifests are preserved unchanged in the private intake receipt. Its top-level 74 declared hashes matched, but that does not establish that every nested packet was complete.

- Components 01 and 03 omitted `effect_finality_gate.py`. A new public `research_support.Action` implements only the synthetic action fields and deterministic hash needed by those callers. Imports are redirected explicitly. This is reconstruction, not recovery of the historical implementation or reproduction of its exact hashes.
- Component 02 omitted `reserve_worker.py`; a newly authored public worker calls its existing ledger and returns the existing dataclass decision. Its nested manifest also lists an absent copy of component 01's `commit_fence.py`; no component 02 code imports that file, so a duplicate was not added.
- Component 07's supplied `reports/report.json` does not match its nested source manifest. Both incoming bytes and the stale manifest are retained. A fresh integration manifest describes the actually imported bytes; the original digest is not silently corrected.
- Component 08 omits the original `benchmark.py` and `reports/extended_gap_report.json`. Its supplied replacement reproducer is separate and explicitly identifies itself as newly authored. Reproducing headline classifications does not recover those absent artifacts or test hostile execution.
- The incoming importer compares SHA256 output to three forty-character Git blob identifiers. Those identifiers match `git hash-object` of the basis files, not SHA256. It also requires a clean checkout. The dirty canonical checkout was backed up and integrated through exact paths and additive API/README merges instead of running that importer or erasing existing work.

The supplied manifests are provenance records. `INTEGRATION_MANIFEST.json` records current package bytes after these explicit changes. Local reruns and remaining gates are in [LOCAL_VERIFICATION.md](LOCAL_VERIFICATION.md). No private lab implementation was copied into the public packet. No superiority, novelty, provider atomicity or production security is established.

The imported nested manifests are now named `SOURCE_SHA256SUMS.json`. Maintained `SHA256SUMS.json` files and the root integration manifest describe current bytes. Original naming and bytes remain in the source archive.
