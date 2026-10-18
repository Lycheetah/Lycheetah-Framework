# Cycle 9 handoff for the next research agent

**Do not restart the Hybrid Gateway. Do not push to GitHub without Mac's direction.** The complete v0.2–v0.9 source and dated historical reports are preserved.

## Reproduce

```
python -m unittest discover -s tests -q
python demo_signed_review.py
python demo_sql_comparison.py
python verify_release.py
```

At packaging: 190 passing automated tests. v0.8's fair SQL comparator was 4/4 vs gateway 4/4 in self-authored historical examples and 1,200 synthetic differential agreements. Don't market this as superior temporal retrieval.

## The v0.9 change

`hybrid_gateway/authorization.py` introduces HMAC-based, purpose-bound, short-TTL `SignedBatchApproval`. `SQLiteLedger(..., require_signed_approval=True)` persists strict mode. In strict mode the previous unauthenticated boolean cannot commit. A signature covers the audited extraction batch and its plan, source, registry, original head, ledger ID, commit timestamp, and nonce. Atomic SQLite commit consumes nonce alongside the event. `audit_persisted_approvals(keyring)` verifies archived MAC and event links after restart.

**Do not confuse this with authenticated human review.** A real implementation needs reviewer identity, a protected signing service, an approval UI, revocation and secure audit anchors. The fixture demo directly signs its own candidate for test purposes only.

## Next technical priorities

1. Build actual human review adapter: present exact source/evidence, user identity, explicit decision, a review time record and securely issued permit; measure reviewer burden.
2. Freeze real-world temporal policy evaluation documents with independent human annotations and document digest snapshots; measure omissions, precision, abstention, wrong-field errors, and review time.
3. Run a real model through `probe_live_model.py`, keeping equal inputs/budget for temporal SQL+retrieval and the hybrid gateway. An always-abstain baseline must score 0 recall for answerable queries.
4. Run the pinned canonical CASCADE file inside the v0.8 worker on an operator-trusted checkout and document exact commit hash/dependencies, without granting CASCADE admission authority.
5. Retain an externally trusted event head and build recovery/adjudication tests for DB copies and signing-key loss.

## Nonclaims

Not a new model, trained neural-symbolic LLM, proven AI safety system, independently evaluated RAG architecture, certified identity provider, hostile-code sandbox, or live customer deployment. No GitHub branch/push carried out.
