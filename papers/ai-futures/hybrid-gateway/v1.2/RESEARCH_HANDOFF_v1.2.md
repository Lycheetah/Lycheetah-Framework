# Lycheetah Hybrid Gateway — Cycle 12 research and publication handoff

The v1.2 release candidate extends all code from v1.1 and preserves the historical
research documents. External witness checkpoint code is in
`hybrid_gateway/external_witness.py`; tests are in `tests/test_external_witness.py`
and `tests/test_witness_populated.py`.

The externally retained witness is only a **mechanism**, not an independently operated
service. The checkpoint and witness secret must be held outside SQLite's administrative
trust boundary for truncation detection to have operational meaning.

Run `python verify_release.py`, `python -m unittest discover -s tests -q`,
`python demo_sql_comparison.py`, and `python demo_review_journal.py`.

Read `GITHUB_PUBLICATION_AUDIT.md` before pushing. The candidate uses an MIT licence
consistent with the main Lycheetah Framework repo, subject to owner approval.

Next: durable witness export to independently managed storage, reviewer/signer process
separation, independently annotated temporal extraction baseline, genuine canonical
CASCADE trial, and real reviewer outcomes/cost.
