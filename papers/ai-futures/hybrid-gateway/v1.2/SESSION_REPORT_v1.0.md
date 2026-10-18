# Cycle 10 session — Human Review Desk

**18 October 2026 · Research continuation from v0.9**

## Goal

Bridge the gap between a code-signable approval permit and a person-accessible evidence review. Keep the trusted operator source/plan/contract boundary, avoid giving neural output signing authority, and retain atomic SQLite admission from v0.9.

## New executable capability

- `ReviewDesk`: password-verifying local reviewer session; 15-minute server-side expiry, CSRF, one-time review outcome, source/batch/registry/ledger binding and full operator-controlled screen digest.
- `make_review_server`: bound to IPv4 loopback only; strict Host and Origin on state changes; no scripts, external resources, arbitrary API endpoint or model-submitted data; basic login attempt throttling, Content Security Policy, cookies and size-bounded POST forms.
- Review screen: complete operator-registered source, every candidate, matching operator clause contract, effective range, evidence quote, source digest, review timestamp and full-batch confirmation.
- Decision: browser can only ask approve/reject; backend independently issues short-lived batch-scoped HMAC approval; v0.9 SQLite ledger atomically admits or declines.
- Optional privacy-minimized local observation for experiment setup; no claims that time equals attention.

## Reproducible evidence

Full tests and release checks are listed in README and manifest; the initial 190 v0.9 tests passed unchanged before edits. New unit/HTTP tests include real loopback login, source confidentiality before login, explicit same-origin/CSRF checks, CSS/script isolation, forged digest/form attempts, replay, wrong password, expired session, altered plan, stale ledger head and rejection without knowledge write.

## What was *not* done

- No real person reviewed the demo. The HTTP client scripted both sides of the test.
- No separately managed key store, reviewer SSO, TLS, production audit anchoring, or independent security review.
- No live Ollama or cloud-model call; no independent temporal RAG/QA benchmark or canonical upstream CASCADE execution.
- No outcome comparison on real business documents. The SQL temporal tie from v0.8 stands.
- No GitHub push or production deployment.

## Interpretation

Cycle 10 enables a more plausible study because a consenting reviewer can now examine exactly what admission will commit. It does *not* yet establish that the additional human-in-the-loop architecture improves facts admitted or makes people faster. That requires a held-out, independent corpus and measured reviewer effort, with the cost of preparing operator contracts included.
