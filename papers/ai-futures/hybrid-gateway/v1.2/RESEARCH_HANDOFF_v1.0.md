# Cycle 10 handoff — reviewability before claims of useful intelligence

**Complete v0.2–v1.0 lineage preserved. Do not restart from scratch or push to GitHub without Mac's direction.**

## Reproduce

```bash
python -m unittest discover -s tests -q
python demo_signed_review.py
python demo_sql_comparison.py
export LYCHEETAH_REVIEW_PASSWORD='a different 16+ character local demo password'
python demo_review_desk.py --report /tmp/review-observation.json
python verify_release.py
```

## New files

- `hybrid_gateway/review_desk.py`: password-gated, loopback-only HTTP review server and typed one-batch review facade; exact presentation digest, locked operator fields, source/contract text escaping, authorization-issued atomic commit, local session elapsed observation.
- `tests/test_review_desk.py`: programmatic unit tests and real `http.client` loopback POST/GET tests.
- `demo_review_desk.py`: fictional, ephemeral database and key; optional privacy-minimized export.
- `REVIEW_DESK_BOUNDARY_v1.0.md`, `REVIEW_EVALUATION_STUDY_v1.0.md`, `FAILURE_MUSEUM_v1.0.md`.

## Key test distinction

Passing HTTP security regression tests are **not** a penetration test. Demo operator password ≠ authenticated named person. Review elapsed interval ≠ active reviewing. HTML-escaped quote ≠ truthful evidence. Signed HMAC ≠ external notarization. The baseline temporal SQL *tie* survives unchanged. No live LLM, external reviewer or pinned upstream CASCADE was executed here.

## Next engineering targets

1. Separate signing into a dedicated key-holder with authenticator-specific approval, explicit policy grants and mTLS/secure local IPC (never network-expose the current HTTP server).
2. Create durable approval/rejection/presentation receipts with a clear atomic persistence contract and external event-head anchoring.
3. Run real model extraction on independently prepared documents, compare fair temporal SQL+RAG and hybrid workflows with full annotation/review time included.
4. Execute the canonical CASCADE checkout by matching the source hash on the exact local file; preserve diagnostics as read-only and no admission authority.
5. Test with actual consenting human reviewers, not script-generated sessions, and seek usability/security review.

No repository branch or deployment was created. Suggested branch name: `research/hybrid-intelligence-architecture`.
