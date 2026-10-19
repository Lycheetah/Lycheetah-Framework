# EARNED LIGHT — FORGE V / PRACTICAL EXIT TRIAL
**Status: offline synthetic research prototype, 2026-10-18. Not production secure.**

## The question

Can an operator leave an AI-mediated provider and still recover policies, provenance, decision history and a functional read-only workflow on a different implementation? What evidence is needed beyond a vendor-generated checksum manifest?

## What exists

- `fixture.py` — fictional small New Zealand business source state (5 documents, 5 policies, 3 past decisions, 2 connector descriptions) and a test reference snapshot
- `exporter.py` — Provider A exports, in a deliberately weak proprietary format, a strong conventional open-JSON format, or an open-JSON format accompanied by a locally generated file manifest
- `target_importer.py` — separate read-only Provider B implementation; consumes only the transferred bundle in a new subprocess
- `auditor.py` — compares restored record fingerprints, exact task behavior and revision against a **separately supplied expected source snapshot**
- `experiment.py` — reproducible 24-trial matrix (3 export profiles × 8 fault variants)
- `tests/test_exit.py` — executable regression and adversarial checks
- `results/comparisons.json` and `.csv` — generated data
- `CLAIMS_AND_FAILURES.md` — negative findings and known blind spots
- `THREAT_MODEL.md` — trust boundaries and deployment gaps
- `RESEARCH_PASS_05.md` — research narrative, proposed next experiment and interpretive boundaries

## Run without additional packages

Python 3.10+ recommended. From this folder:

```bash
python -m unittest discover -s tests -v
python experiment.py
python auditor.py --profile portable --variant forge_manifest
```

The subprocess uses Python `-I` and a separate working directory. This avoids accidentally importing Provider A's code as ordinary local modules, but **does not sandbox filesystem access**. An OS sandbox/container would be required for a genuine hostile-provider isolation test.

## Metric definitions

- `records_verified / records_expected`: count of records identical by canonical JSON SHA-256 to the pre-export reference (not an estimate of truth)
- `tasks_passed / tasks_expected`: number of five topic responses plus three historical cases whose *structured output* exactly matched the pre-export expectations; this is not an LLM benchmark
- `manifest_status`: whether the export's own SHA-256 file list matches the exported content. **`match` does not mean complete, current, legitimate or truthful**
- `synthetic_readonly_continuity`: true only when all 15 records, eight tasks, and the source revision match the pre-export reference
- `connector_claims_portable`: metadata-level claim, explicitly not proof of connection, credentials or provider independence
- `externally_verified_effects_continuity`: always false: **no effects were attempted**

## Central negative result

The **strong conventional JSON baseline and the proposed manifest-bearing package tie** on every task and reference-completeness outcome. The manifest-bearing package does *one useful but narrow additional thing*: if an export file is changed *after* manifest generation, the local manifest notices without needing the separate reference. Yet a manifest recomputed by the same compromised producer passes while carrying falsified data. A trusted independently stored pre-export reference is doing the substantive completeness verification.

This is a demonstration of a verification pattern and its limits, **not** a proven novel portability protocol, legal certification, or validated personal agency metric.

## No production integration

Forge II–III's signed permits/approval bridge are not wired into this lab. Decision receipt strings in the fixture are just synthetic placeholders, not authenticated approvals. Forge IV's sovereignty frontier is a conceptual predecessor, not called by this tool. No GitHub repository is modified.

See `RESEARCH_PASS_05.md` for the candidate pilot and sources.
