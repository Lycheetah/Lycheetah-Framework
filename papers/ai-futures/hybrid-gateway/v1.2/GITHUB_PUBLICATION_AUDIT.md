# GitHub Publication Audit — Lycheetah Hybrid Gateway (v1.2 candidate)

## Recommendation

**Publish as a separate clearly labelled research prototype, with a link from
Lycheetah-Framework / lycheetah-frontier-public.** Avoid merging directly into a production
runtime or marketing as independently validated agent safety. Obtain the owner's approval
for repository location and MIT licence first. No GitHub push was made during this audit.

## What actually works

- Bitemporal namespace-scoped claim storage, explicit source anchoring and event history;
  suppression, withdrawals and conflicting outcomes lead to bounded decisions.
- Clauses and operator-selected scope/effective times; neural suggestions remain proposals.
- SQLite atomic batch commits with stale-head verification and consumed signed permits.
- Local browser Review Desk with controlled sessions, CSRF and all-or-nothing review.
- Signed privacy-minimized, persistent approval/rejection journal with transactional link
  to approvals; rejections persist across restart.
- Out-of-process SHA-pinned optional CASCADE adapter, verified only with an explicitly toy
  implementation, not the canonical runtime.
- v1.2 external journal witness API + 10 tests (5 inherited empty, 5 populated with
  tamper/truncation/restart). Independent witness custody/storage not implemented.

## Reproduced during this audit

- Extracted supplied v1.2 research ZIP without corruption.
- Original v1.2 tree: `python -m unittest discover -s tests -q`: **259/259 pass**.
- Added five populated-journal witness tests: **264/264 pass** on Python 3.13.
- `demo_review_journal.py` produced durable approval/rejection vs ephemeral old reject.
- `demo_sql_comparison.py` reproduced the 4/4 gateway = 4/4 SQL, 2/4 naive comparison.
- Static grep for common secret signatures found no obvious live credentials; not a
  complete credentials audit.
- The original v1.2 archive's `verify_release.py` **failed** because the stale manifest
  omitted four v1.2 files. Candidate manifest was regenerated after final changes.
- Inherited suite emits some `sqlite3.Connection` ResourceWarnings; tests still pass.

## What has not been tested or established

1. Accuracy on independently prepared documents and truly independent human annotations.
2. Performance on a live model endpoint; optional transport is implemented but no live
   inference result is reported.
3. Real execution and calibration of canonical CASCADE.
4. Human reviewer identity, attention, operational user cost or customer value.
5. Production readiness, red-team security assurance, multi-user concurrency at scale,
   network TLS/SSO, protected key service, or independently operated witness storage.
6. Formal proof that the security architecture cannot be bypassed in an adversarial host.
7. CI across advertised Python versions until GitHub Actions runs complete.

## Release gates

- [x] Preserve full source history in the research release.
- [x] Complete combined Python suite after new witness tests.
- [x] Demonstrate a populated journal rollback/tampering check.
- [x] Correct README version and evidence summary.
- [x] Include reproducible commands, CI workflow, `.gitignore`, and a verified manifest.
- [x] Include licence text aligned with main Framework (**owner to approve**).
- [ ] Decide standalone repository name and visibility.
- [ ] Confirm rights/licence and review commit diff before pushing.
- [ ] Have CI pass on every declared interpreter version.
- [ ] Conduct independent security review before external service deployment.

## Publish metadata recommendation

Suggested name: `lycheetah-hybrid-gateway`.
Suggested topic tags: `python`, `bitemporal`, `ai-agents`, `human-in-the-loop`,
`audit-logs`, `research-prototype`.
Suggested release label: `v1.2.0-research` (NOT stable 1.2.0 production).
Suggested short description: "Research prototype for evidence-governed AI knowledge
revision, signed human-review decisions and a bitemporal SQLite ledger."

## Continuation priorities

1. Separate signer/witness from the web process and protect keys independently.
2. Add operator-managed witness persistence and rollback recovery workflows.
3. Run a preregistered evaluation on independent evolving documents; compare against a
   competent temporal SQL/RAG review baseline, including cost and human review time.
4. Integrate genuine canonical CASCADE with frozen calibration, or drop the claim.
5. Move from static local demos to an authenticated and audited multi-user UX only after
   threat modelling, security hardening and external review.
