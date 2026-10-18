# LYCHEETAH HYBRID GATEWAY v0.9 — Signed Authority at the Revision Boundary

**18 October 2026 · Local research prototype · Not deployed or independently validated**

**Carry-forward:** complete v0.2–v0.8 history preserved. The base system still provides source-grounded bitemporal claims, operator-selected evidence contracts, a neural extraction interface, completeness auditing, atomic SQLite batches, temporal SQL comparison, and optional read-only CASCADE subprocess diagnostics. **Cycle 9 hardens one known gap: a caller-supplied `reviewer_approved=True` was not authenticated authority.**

## First commands

```bash
python -m unittest discover -s tests -q  # 190 internal tests at packaging
python demo_signed_review.py             # signed two-claim commit, replay defense, audit
python demo_sql_comparison.py            # the historical 2/4 vs 4/4 vs 4/4 synthetic result
python demo_atomic.py                    # legacy v0.6 local atomicity demo
python verify_release.py                 # SHA-256 file manifest integrity
```

## What v0.9 actually implements

- **Opt-in then persistent strict approval**: create the durable store with `SQLiteLedger(path, require_signed_approval=True)`. This persists `approval_policy=signed_v1` in SQLite; ordinary reopening cannot downgrade it via the Python constructor. In this mode `reviewer_approved=True` **alone returns REVIEW**.
- **HMAC-SHA256 permit**: `issue_approval` binds a model-independent operator-controlled key ID, a random single-use nonce, signing purpose, short TTL (maximum 600s), exact audited batch digest (including stages), registered source, plan, registry, original ledger head, database identity, and requested `recorded_at`.
- **Commit-time check**: verify the permit inside the `BEGIN IMMEDIATE` SQLite write transaction, then recheck evidence and stale head before writing one batch event. Store the used nonce and public permit in the *same* transaction as the event.
- **A persisted random database identity** protects against transferring a valid approval to a *different independently initialized database* with the same empty event head. If an entire database is cloned, it retains its identity; this is **not** cryptographic defense against clones.
- **Auditable local approval attachments**: `audit_persisted_approvals` replays events and checks archived MACs, event head linkage, database ID, and event recording time. A separately preserved event-chain head is still needed to detect complete database replacement.
- **Key rotation**: caller controls the trusted keyring. Missing or revoked keys invalidate new approvals and mean past MACs cannot be verified with that reduced keyring. Store retired verification keys securely for historical audit if needed; don't keep signing privileges active merely to audit.

### Operator trust boundary

```python
# This is API shape, NOT a ready-to-use identity or UI workflow.
from hybrid_gateway import SQLiteLedger, ReviewKeyring, issue_approval

store = SQLiteLedger('example.sqlite3', require_signed_approval=True)
# independently register source, create TrustedContractRegistry, ExtractionPlan,
# then generate a COVERAGE-READY AuditedBatch via CoverageAuditor.
# After an authorized *human* review, a SEPARATE trusted signing service signs:
# approval = issue_approval(batch, plan, key_id=..., secret=..., 
#     ledger_id=store.ledger_id, recorded_at=...)
# store.commit_batch(batch, registry=registry, plan=plan, recorded_at=...,
#     authorization=approval, trusted_keys=ReviewKeyring({key_id: secret}))
```

The signing service must control keys and verify *who approved what*. This prototype has **no reviewer authentication, protected signing service, consent UI, hardware key management, sandbox, production clock attestation, or externally anchored ledger head**. HMAC proves possession of a shared secret, not a specific person's review. The *legacy non-strict SQLite API remains intentionally available* for backward compatibility—never deploy a new ledger in that mode when relying on authorization.

## Measured evidence

| Metric | v0.8 (inherited) | v0.9 |
|---|---:|---:|
| Internal automated tests passed | 154 | 190 |
| New authorization boundary tests | 0 | 36 |
| Strict database refuses bare reviewer flag | Not provided | Tested |
| Signed authorization committed with batch event | Not provided | Tested |
| Replay, expiry, key rotation, tampering, cross-database permit misuse | Not provided | Synthetic contract tests |
| Real model / external temporal benchmark / canonical CASCADE executable | Not validated | Still not validated |

**Not evidence of better AI reasoning or historical query quality:** the fair temporal SQL baseline *ties* the gateway on the four synthetic v0.8 examples and 1,200 synthetic differential queries. The novelty hypothesis remains the combined evidence-and-authority workflow under real review costs, not a new temporal database.

See [`SESSION_REPORT_v0.9.md`](SESSION_REPORT_v0.9.md), [`FAILURE_MUSEUM_v0.9.md`](FAILURE_MUSEUM_v0.9.md), [`RESEARCH_HANDOFF_v0.9.md`](RESEARCH_HANDOFF_v0.9.md), and [`AUTHORIZATION_BOUNDARY_v0.9.md`](AUTHORIZATION_BOUNDARY_v0.9.md).

**Local branch proposal (not pushed):** `research/hybrid-intelligence-architecture`.
