# Anon Politician — CASCADE audit kit v0.3

**Status:** research prototype / design proposal. Not a validated political decision system.

## Package contents
- `source_ledger_v0_1.csv` — preserved earlier working ledger for provenance/history.
- `source_claims_audit.csv` — 15 source-derived claims/concepts with PDF page locators and audit assessments.
- `external_evidence_register.csv` — 11 external records, including source type, date, relevance, limitations and URL.
- `audit_findings.csv` — 10 priority findings and required actions.
- `cascade_block.schema.json` — provisional JSON Schema for provenance-first knowledge blocks.
- `cascade.py` — conservative dependency/contradiction review-queue engine.
- `test_cascade.py` — 11 unit tests for structural safety properties.
- `test_run_report.txt` — latest unit-test result and scope limitation.
- `structural_benchmark_cases.json` — 12 synthetic structural conformance fixtures with expected affected-block sets.
- `run_structural_benchmark.py` — deterministic runner for those fixtures.
- `structural_benchmark_results.json` and `structural_benchmark_report.md` — latest machine-readable and human-readable results.
- `review_protocol.md` — proposed comparative evaluation protocol.
- `Anon_Politician_Source_Fidelity_and_Evidence_Audit_v0.3.docx` — narrative source and evidence audit.
- `SONNET_REVIEW_PROMPT.md` — five-pass independent review brief for external adversarial review.
- `Anon_Politician_Source_Audit_v0.3.xlsx` — seven-sheet audit workbook, including separate benchmark summary and case tabs.

## Non-negotiable design rules
1. Internal coherence is not truth.
2. Normative commitments and empirical propositions have different epistemic status.
3. A cascade creates review work; it never automatically promotes, demotes, archives, or deletes a claim.
4. Explicitly contradictory claims and their dependents are also queued for review.
5. Contradictions remain visible until adjudicated with a recorded rationale.
6. Source claims and independent findings must be separately represented.
7. AURA metrics (TE, VTR, PAI) remain unimplemented specifications until formulas, constructs, calibration and validity tests exist.
8. No single scalar score should determine political or policy truth.

## Quick start
Requires Python 3.10+. From this directory, run:

```bash
python -m unittest -v
```

Latest observed result: **11 unit tests passed**. The separate 12-case structural conformance suite also matches all 12 researcher-authored expected sets. Both results test implementation behavior only; expected benchmark labels are not independently adjudicated and neither suite validates factual accuracy, prediction, political symmetry, or policy utility.

## Important limitations
The source audit is a focused first pass, not a complete line-by-line audit or systematic literature review. Major source records have PDF page locators; some still need quote-by-quote verification against rendered pages. External evidence helps refine claims and choose baselines but does not settle every substantive question.

## Key empirical comparator
Stats NZ's *Environmental-economic accounts: Data to 2024* release (5 March 2026) includes environmental-protection expenditure (currently experimental), environmental taxes, marine-economy accounts, and renewable-energy stock accounts, compiled under the UN System of Environmental-Economic Accounting framework. This raises the bar for DEEP: identify a specific, measurable gap before proposing a new protocol. Source: https://www.stats.govt.nz/information-releases/environmental-economic-accounts-data-to-2024/

## Next milestone
Independently review the current 12 synthetic fixtures, then build and freeze a 30–50 case labelled set of realistic claim graphs and compare: (A) a static evidence ledger with manual search; (B) this dependency/contradiction review queue; and (C) a future metric-triggered cascade only after AURA is operationally specified. Predeclare metrics: precision/recall of review alerts, irrelevant alerts, provenance completeness, reviewer workload, political symmetry, and preservation of legitimate disagreement.

## Source integrity
Original input: `Anon Politician.pdf` (62 PDF pages; 4,116,059 bytes). SHA-256: `9a64bba3cdd56887c3f30471fb4272b4c59f8a73e7360c606047c303377de536`. The raw PDF is intentionally not bundled because it contains identifying information; keep the source master private and release only separately reviewed derivatives. Page references in the audit report point to that exact source file.
