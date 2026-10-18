# Cycle 11 — Durable review-decision journal

**Status:** Internally tested local prototype. **No external security review, real human subject study, model accuracy measurement, deployment, independent witness, or hardware-backed identity assertion.**

## The repaired gap

In v1.0, a browser rejection was remembered in the `ReviewDesk` process but not stored. When that process exited, no durable record of the decision remained. A signed *approval* was stored with an admitted event, so the two decision types had asymmetric auditability. The cycle's objective was to correct this defect without claiming that the database, the browser or an HMAC authenticates a particular person.

## New `journal_v1` mode

Create a new ledger with `SQLiteLedger(path, require_review_journal=True)` and a password-gated `ReviewDesk`. On a successful decision, the desk supplies a trusted `ReviewJournalAuthority` inside the Python service; the browser sends only a session cookie, CSRF token, current presentation digest, and action. Neither the model nor HTTP request may choose the signature key, batch fingerprint or ledger identity.

- **Approval:** operator's signed single-use permit, knowledge event, consumed permit and signed review journal entry are persisted in *one `BEGIN IMMEDIATE` SQLite transaction*. An insertion failure must leave all of them absent.
- **Rejection:** a signed record is persisted in an independent SQLite transaction, with no knowledge event. The rejection prevents future admission of the exact reviewed batch, including from a restarted process.
- **Journal record fields:** nonce, purpose, monotonically assigned sequence, prior journal entry hash, decision code, key ID, ledger identity, plan/source/registry/batch/presentation digests, staged knowledge head, committed event hash when approving, decision timestamp, HMAC-SHA256 signature and entry digest. No raw claim text, source body, session cookie, password, or signing key is stored in the journal rows.
- **Audit:** `SQLiteLedger.audit_review_decisions(keyring, independently_anchored_journal_head=...)` recalculates MACs, per-entry hashes, links and approved-event references. Carry the final journal head **outside** the SQLite database to detect truncation or wholesale replacement. No automatic external anchoring is provided.

The journal's append operation verifies the existing chain before extending it; this fails closed when previous signing keys are unavailable. An operational multi-key migration protocol has not been built. Unknown policy values are refused. Enabling journal mode on a nonempty legacy event history is refused to avoid retroactively suggesting those events were journalled.

## API and legacy compatibility

Legacy signed-v1 databases remain supported for reproducibility of prior tests and historical sources. They do **not** silently become journal_v1. New journal_v1 databases require both an operator-key-backed signed approval and journal authority. Ordinary v1.0 `reviewer_approved=True` cannot bypass the stricter mode. In legacy signed-v1 mode, older approvals may remain without a decision journal: do not mix modes when describing auditable coverage.

## Reproduce

```bash
python -m unittest discover -s tests -q
python demo_review_journal.py
export LYCHEETAH_REVIEW_PASSWORD='a locally-chosen secret with more than 16 characters'
python demo_review_desk.py
```

Demo mode uses temporary files and ephemeral keys. Closing the demo deletes its database; permanence is tested by reopening a *still-existing* SQLite file. Production retention requires an explicitly managed database path, backup discipline, and protected key custody.

## Threat boundary

The key proves **possession of a configured secret**, not attention, reviewer identity, evidence accuracy, least-privilege authorization, or informed consent. Password login is still local and can be shared. The reviewer process still has the signing key; key-holder separation and independently authenticated human identity remain future targets. Local hash chains cannot detect deletion of all local evidence without a separately retained anchored head. An attacker who controls the database and signing key can forge a history. The subprocess CASCADE integration is not a sandbox. Remote HTTP exposure is prohibited.

## Benchmark boundary

The self-authored offline comparison demonstrates a software-contract difference only: v1.0 reject => zero durable decision records; v1.1 reject => one verified record; v1.1 approve => one knowledge event and one verifiable decision entry. It is **not** an empirical comparison of human reviewer accuracy, model hallucinations, latency, cost, or query quality. The fairer SQL temporal baseline continues to tie on existing synthetic history cases.
