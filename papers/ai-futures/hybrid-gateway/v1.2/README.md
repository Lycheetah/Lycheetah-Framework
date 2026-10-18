# Lycheetah Hybrid Gateway — v1.2 research candidate

**Evidence-governed AI knowledge revision with explicit, locally audited human decisions.**

**Status: PUBLIC RESEARCH PROTOTYPE — NOT production security, certified AI alignment,
or demonstrated superiority over standard temporal databases.**

This is a modular Python implementation investigating how potentially unreliable neural
extraction can propose changes to knowledge while separately trusted contracts, a
bitemporal ledger, and an operator-controlled review path decide what becomes durable.
It is part of the wider [Lycheetah Framework](https://github.com/Lycheetah/Lycheetah-Framework).

## Reproduce locally

Requires Python 3.10+ (tested in this audit on **Python 3.13**). The standard-library
core and tests run without installing a language-model SDK. Other supported Python
versions are configured for CI but have not been verified by this audit.

```bash
python -m unittest discover -s tests -q
python verify_release.py
python demo_sql_comparison.py
python demo_review_journal.py
```

A loopback-only, fictional browser demonstration is available:

```bash
export LYCHEETAH_REVIEW_PASSWORD='choose-your-own-long-random-demo-password'
python demo_review_desk.py
```

**Do not put this demo on a public server or use real customer policy documents.**

## Architecture at a glance

1. **Source and scope:** immutable source digests, tenant isolation, explicit effective
   and knowledge times, claims with source references and withdrawals.
2. **Proposal:** optional OpenAI-compatible adapter for local/opt-in remote extraction.
   Model output is untrusted and cannot grant approval.
3. **Operator contracts:** specific clauses and extraction plans are registered before
   admission. A quoted string is not automatically semantic proof.
4. **Atomic staging:** batch plans are rechecked for stale ledger state and admitted
   atomically into SQLite only after signed authorization.
5. **Review Desk:** local password session, CSRF-protected browser, explicit approve/reject
   controls; approval is not evidence that an authenticated human actually read the source.
6. **Review journal:** signed chained approval/rejection records, locally auditable after
   restart; rejected batches cannot silently become approved.
7. **External witness (v1.2):** exported HMAC-authenticated checkpoint for a journal
   count and head. **Caller must store checkpoint and witness key outside the DB trust
   boundary.** Populated-journal integration tests exercise detection of tampering and tail deletion.
8. **CASCADE diagnostics:** optional SHA-pinned subprocess adapter; tested with a toy
   engine, **not the authentic canonical CASCADE runtime**.

## Evidence register

| Evidence | Tested finding | Not established |
|---|---|---|
| Python regression suite | **264/264 tests pass** on Python 3.13 in local release audit | Independent review, formal proof, penetration testing |
| Four fictional time-sensitive policy questions | Gateway 4/4, strong SQL baseline 4/4, weak latest-known baseline 2/4 | Advantage over well-designed temporal SQL |
| 1,200 seeded differential temporal queries | Gateway agreed with separately written SQL comparator | External factual validity |
| Decision-journal demos | Locally signed approvals and rejections survive restart | Verified real reviewer identity/attention |
| Witness tests | 10 tests including 5 populated-journal attack checks | Independent deployment/retention of witness |
| Neural adapter | Stub transport tested and opt-in real endpoint code available | Real-model accuracy or throughput |

The code has **no known production deployment** or independent human-review trial in this
research record. All demonstrated datasets are synthetic or investigator-authored. Do not
interpret the test count as an AI reasoning performance metric.

## Start here

- [`SESSION_REPORT_v1.2.md`](SESSION_REPORT_v1.2.md) — newest checkpoint
- [`GITHUB_PUBLICATION_AUDIT.md`](GITHUB_PUBLICATION_AUDIT.md) — publication decision, evidence and caveats
- [`REVIEW_DECISION_JOURNAL_v1.1.md`](REVIEW_DECISION_JOURNAL_v1.1.md) — durable decisions
- [`REVIEW_DESK_BOUNDARY_v1.0.md`](REVIEW_DESK_BOUNDARY_v1.0.md) — local UI security boundary
- [`EXTERNAL_BENCHMARK_PLAN_v0.8.md`](EXTERNAL_BENCHMARK_PLAN_v0.8.md) — evaluation still to do
- [`FAILURE_MUSEUM_v1.1.md`](FAILURE_MUSEUM_v1.1.md) — recorded failures
- [`RESEARCH_HANDOFF_v1.2.md`](RESEARCH_HANDOFF_v1.2.md) — continuation instructions
- Historical cycle documents are retained as `README_v*.md`, `SESSION_REPORT_v*.md` and
  `FAILURE_MUSEUM_v*.md`. Historic performance claims remain labelled by their original evidence.

## Licence and credit

Candidate licence: **MIT**, matching the current Lycheetah-Framework public repository.
Copyright attribution is included in [`LICENSE`](LICENSE). Confirm the choice before pushing.
Research and implementation were co-developed with AI assistants under the human project
owner's direction; the evaluation and limitations should be read before reusing the code.
