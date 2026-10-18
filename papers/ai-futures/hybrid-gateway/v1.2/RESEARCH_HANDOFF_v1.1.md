# Cycle 11 handoff — durable decisions before distributed authority

This package preserves v0.2 through v1.1. Start with `README.md`, `REVIEW_DECISION_JOURNAL_v1.1.md`, `SESSION_REPORT_v1.1.md`, and `FAILURE_MUSEUM_v1.1.md`. The canonical knowledge source remains the user's Lycheetah repository; this local package is not a new canonical CASCADE fork.

## Reproduction commands

```bash
python -m unittest discover -s tests -q
python demo_review_journal.py
export LYCHEETAH_REVIEW_PASSWORD='local-use-only-password-longer-than-sixteen'
python demo_review_desk.py
python verify_release.py
```

No web, LLM endpoint or API key is required. New `journal_v1` mode is **opt-in**: `SQLiteLedger(path, require_review_journal=True)`. Strict signed-v1 mode is retained only for tests and historical compatibility; describe audit coverage precisely.

## Provenance

The v1.1 work extends v1.0 ReviewDesk + v0.9 HMAC permission + v0.6 SQLite transaction. No source file was removed. The additional 30 tests are local regressions, not an independent benchmark. Append-only journal records include HMAC, previous hash, batch/plan/source/presentation binding and optional event reference. Rejection is permanent for an exact reviewed batch unless a new proposed batch is staged, with a new fingerprint; false decisions can still be made by an authorized operator.

## Do not overstate

No verified human identity, actual human usability trial, remote deployment, externally anchored journal, remote key custody, production SQLite crash-resilience claim, independently validated model performance, or executed canonical CASCADE run. The subprocess integration remains experimental.

## Next technical action

Design and test an independent signing service and irrevocable decision audit anchored outside the database, then run a true external review/evaluation. A real key-holder must be separate from the browser app, and any new public interface requires an explicit threat model plus authentication and security review.

Nothing was pushed to GitHub. Suggested future branch remains `research/hybrid-intelligence-architecture` unless Mac chooses otherwise.
