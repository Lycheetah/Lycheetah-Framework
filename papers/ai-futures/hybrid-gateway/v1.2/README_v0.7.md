# LYCHEETAH HYBRID GATEWAY v0.7 — Temporal/CASCADE Boundary Audit

**Research Cycle 7 · 18 October 2026 (NZ). Executable local research prototype; not deployed, not pushed to GitHub.**

This extends the **complete v0.6 codebase** without replacing its atomic batch, SQLite, source-contract, neural-adapter, coverage or evaluation modules. The new work asks a falsifiable question: **when symbolic CASCADE assessments disagree with the evidence-ledger's scoped, time-aware outcome, is that disagreement exposed without silently rewriting knowledge?**

## Quick verification

Python 3.10+ (new code uses standard library; upstream canonical CASCADE separately requires its dependencies).

```bash
python -m unittest discover -s tests -q         # 138 passing at package time
python demo_atomic.py                             # inherited v0.6 transactional demo
python demo_temporal_audit.py                     # synthetic time/weight demonstration
python demo_cascade_canonical.py --framework-root /path/to/Lycheetah-Framework
```

**The last command requires an operator-supplied, trusted checkout of the real repository.** It checks the exact Git blob SHA and imports the real CASCADE classes only if it matches. No canonical checkout or running neural model is bundled; this research environment could inspect GitHub source through the connected repository but could not download that file into its execution environment. **Canonical execution is therefore NOT claimed for this cycle.** The local regression tests use an explicitly labelled test double for adapter mechanics.

### Components added

| Module | Actual implemented function | Limit |
|---|---|---|
| `hybrid_gateway/canonical_loader.py` | SHA-pinned, explicit local-checkout loader for original `CascadeEngine` and `KnowledgeBlock`; rejects file mismatch before import | Tests exercise a toy import only, not the upstream class |
| `hybrid_gateway/temporal_audit.py` | Repeatable `TemporalCase` evaluation, latest-known naive comparison, cross-profile CASCADE diagnostics; privacy-minimised output | Does not create independent ground truth or calibrated evidence weights |
| `hybrid_gateway/cascade_bridge.py` | Stronger pre/post state snapshot beyond merely matching the event head; rejects boolean numeric weights | A callback in the same Python process is not sandboxed, even if mutation is detected |
| `demo_temporal_audit.py` | Four fictional time/evidence scenarios with an openly declared engine emulation | Internal software demonstration, not canonical CASCADE validation |
| `tests/test_temporal_cascade.py` | New regression tests for time, conflict, withdrawal, multi-profile sensitivity, state mutation and SHA pin behavior | Fixtures are self-authored |

The previous v0.6 120-test suite is preserved. At this cycle, 18 new tests bring the suite to **138 passed**.

## Four-case fixture results

The weak baseline picks the latest admitted value for the same exact tenant/subject/predicate/scope while *ignoring effective-time validity, withdrawals and explicit supersession*. It is **not** an advanced version-aware RAG baseline.

| Fictional case | Correct ledger result | Naive latest-known | Interpretation |
|---|---|---|---|
| Asked about January after March | ANSWER 14 | 60 | Historical validity preserved |
| Asked about February before February revision was known | ANSWER 14 | 14 | Knowledge-time boundary preserved |
| Asked after approved 30-day revision became known | ANSWER 30 | 30 | Explicit supersession |
| Asked after unsupported 60-day competing claim was admitted | ABSTAIN_CONFLICT | 60 | Unresolved disagreement surfaced |

**Result: 2/4 baseline matches, 4/4 ledger-defined expected outcomes.** This is agreement with our own constructed rules. It is not independent quality measurement, live neural evaluation or evidence of a novel temporal reasoning method. Separate regression tests cover withdrawal, missing scope, missing calibration, replay and mutation.

Two **illustrative, author-assigned** evidence-weight profiles cause a change in the *test-double* CASCADE diagnostic in the competing-claim case. The ledger answer remains `ABSTAIN_CONFLICT` under both. The profiles do not represent calibrated truth-pressure weights. Do not publish that result as canonical CASCADE validation.

## Canonical file provenance and pin

- Connected repository: [`Lycheetah/Lycheetah-Framework`](https://github.com/Lycheetah/Lycheetah-Framework)
- File: [`12_IMPLEMENTATIONS/core/cascade_engine.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/core/cascade_engine.py)
- Git blob SHA-1 returned by the connected GitHub file API on 2026-10-18: `bf90a47ab17da11c0266d078fc4d74a5d95c9235`
- The loader verifies `sha1(b'blob '+ascii_file_length+b'\0'+file_bytes)`, the standard Git blob hash.
- This is an **identity pin**, not a security sandbox, signature, independently audited artifact, or license on copied code. The real engine is not vendored into this archive.
- The original CASCADE code treats different paradigms within a domain as contradicting while both remain universal; the gateway's domain/subject/predicate/scope/time checks are a different layer. Mere difference between string values does not establish real semantic contradiction.

## Important known limitations

- **No real local/cloud model inference** and **no independently labelled corpus** were run. The self-authored v0.6 external-evaluation format remains available for future measurement.
- **No canonical CASCADE executable run** occurred. We inspected the original source and built a pinned integration loader. An actual pinned checkout plus optional NumPy dependency is needed for verification.
- **Snapshot checking is tamper detection after the fact, not hostile-code containment**. An injected callback can mutate process memory, and an exception before the final snapshot check can bypass that check. Do not use this as a plugin sandbox.
- **Heuristic CASCADE pressures require independently justified evidence weights**. The bridge never manufactures them and cannot authorize ledger changes.
- **Review approval remains an unauthenticated trusted-caller flag**; no external effect execution, key management, real user identity, distributed transactions, production deployment or compliance certification is claimed.
- **The comparison baseline is intentionally weak**. Real comparative performance requires current version-aware RAG systems and independently authored, temporally annotated evaluation cases under the same budgets.

Next steps are in `RESEARCH_HANDOFF_v0.7.md`; failures in `FAILURE_MUSEUM_v0.7.md`.

**Governing principle:** Neural models may propose. Trusted contracts bind evidence. The durable ledger owns admitted history. CASCADE may diagnose structure, but cannot overrule provenance, time or human review.
