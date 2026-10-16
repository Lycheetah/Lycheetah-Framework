# Package manifest — Anon Politician CASCADE Audit Kit v0.3

This bundle contains a research prototype, a source-fidelity review, an external evidence register, a structural conformance pilot, and the current audit workbook.

## Included
- `README.md` — project status, source integrity, quick start and next milestone.
- `cascade.py` — conservative dependency/contradiction review-queue prototype.
- `test_cascade.py` — 11 unit tests for structural safety properties.
- `test_run_report.txt` — observed test summary and limitations.
- `cascade_block.schema.json` — provisional JSON Schema for provenance-first knowledge blocks.
- `source_claims_audit.csv` — 15 source-derived entries with PDF page locators and proposed handling.
- `external_evidence_register.csv` — 11 external sources with URLs, source types, dates and limitations.
- `audit_findings.csv` — 10 priority findings and required actions.
- `review_protocol.md` — comparative evaluation protocol, baselines, metrics, stop conditions and the limits of the pilot.
- `SONNET_REVIEW_PROMPT.md` — five-pass independent source-fidelity, red-team, architecture and experimental-design review brief.
- `structural_benchmark_cases.json` — 12 synthetic structural conformance cases.
- `run_structural_benchmark.py` — benchmark runner.
- `structural_benchmark_results.json` and `structural_benchmark_report.md` — latest output; expected sets are not independently reviewed.
- `source_ledger_v0_1.csv` — preserved earlier working ledger for provenance/history.
- `Anon_Politician_Source_Fidelity_and_Evidence_Audit_v0.3.docx` — narrative audit report.
- `Anon_Politician_Source_Audit_v0.3.xlsx` — seven-tab workbook with Read Me, Source Claims, External Evidence, Audit Findings, Test Run, Benchmark Summary and Benchmark Cases tabs.

## Deliberately excluded
The original 62-page `Anon Politician.pdf` is not included because it contains identifying attribution and context. It is the private source master in the conversation. Do not label the original file anonymous or assume redaction guarantees anonymity.

## Validation scope
The current unit-test suite contains 11 tests. These test code behavior only. The 12-case structural conformance pilot matches researcher-authored expected sets, not independently adjudicated labels. Neither the unit tests nor this pilot validate claim truth, metric validity, political neutrality, predictive performance, or policy quality. The external evidence pass is targeted, not a systematic review.
