"""SQLite-backed, whole-batch commit for operator-reviewed Hybrid Gateway claims.

Uses SQLite BEGIN IMMEDIATE / COMMIT as a conventional local durable transaction.
The source registry and event chain are stored in SQLite, and are replayed and
validated before each write. No network identity, credential, secret management,
or external notarization is supplied. Treat DB file access as privileged.

The caller must retain a head digest OUTSIDE the DB if protection against a
malicious rewrite of the entire database is required. Tests only show transaction
and replay behavior, not power-loss reliability or adversarial machine security.
"""
from __future__ import annotations

from dataclasses import asdict
from contextlib import closing
import json
import hmac
import hashlib
from pathlib import Path
import sqlite3
import secrets
from typing import Optional

from .core import (HybridGateway, SourceDocument, SourceRegistrationError,
                   Decision, ClaimProposal, canonical_digest, json_bytes, utc)
from .coverage import (AuditedBatch, ExtractionPlan, _fingerprint_candidate)
from .contracts import TrustedContractRegistry, BoundStage
from .authorization import SignedBatchApproval, ReviewKeyring, verify_approval, PURPOSE, batch_digest
from .review_journal import (ReviewJournalAuthority, initialize_schema, append_decision, audit_decisions)


class SQLiteLedger:
    """A single-file local event store, never exposed to an untrusted model."""

    def __init__(self, path: str | Path, *, require_signed_approval: bool = False,
                 require_review_journal: bool = False):
        path = str(path)
        if path == ':memory:':
            raise ValueError('pass a real filesystem path for durable storage')
        self.path = path
        if not isinstance(require_signed_approval, bool):
            raise TypeError('require_signed_approval must be boolean')
        with closing(self._connect()) as conn:
            conn.execute('PRAGMA journal_mode=DELETE')
            conn.execute('''CREATE TABLE IF NOT EXISTS sources
                            (source_id TEXT PRIMARY KEY, payload TEXT NOT NULL)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS events
                            (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS gateway_settings
                            (name TEXT PRIMARY KEY, value TEXT NOT NULL)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS used_approvals
                            (nonce TEXT PRIMARY KEY, batch_digest TEXT NOT NULL, event_hash TEXT NOT NULL, approval_json TEXT NOT NULL)''')
            conn.execute("INSERT OR IGNORE INTO gateway_settings(name,value) VALUES ('ledger_id',?)",
                         (secrets.token_hex(24),))
            initialize_schema(conn)
            if require_review_journal:
                existing=conn.execute('SELECT COUNT(*) AS n FROM events').fetchone()['n']
                mode=conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()
                if existing and mode is None:
                    raise ValueError('cannot silently enable decision journal over unjournaled event history')
                require_signed_approval = True
                conn.execute("INSERT OR REPLACE INTO gateway_settings(name,value) VALUES ('review_policy','journal_v1')")
            if require_signed_approval:
                conn.execute("INSERT OR REPLACE INTO gateway_settings(name,value) VALUES ('approval_policy','signed_v1')")

    @property
    def ledger_id(self) -> str:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT value FROM gateway_settings WHERE name='ledger_id'").fetchone()
            if row is None:
                raise ValueError('missing ledger identity')
            return row['value']

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA synchronous=FULL')
        conn.execute('PRAGMA busy_timeout=5000')
        return conn

    @staticmethod
    def _sources(conn) -> list[SourceDocument]:
        result = []
        for row in conn.execute('SELECT payload FROM sources ORDER BY source_id'):
            d = json.loads(row['payload'])
            digest = d.pop('digest')
            s = SourceDocument(**d)
            if s.digest != digest:
                raise ValueError('registered source digest mismatch')
            result.append(s)
        return result

    @staticmethod
    def _load(conn, *, registry: Optional[TrustedContractRegistry] = None,
              anchored_head: Optional[str] = None) -> HybridGateway:
        sources = SQLiteLedger._sources(conn)
        records = [json.loads(row['payload']) for row in
                   conn.execute('SELECT payload FROM events ORDER BY seq')]
        if registry is not None:
            for registered in registry.sources:
                if registered not in sources:
                    raise ValueError('trusted contract source not present or mutated in store')
        if records:
            head = records[-1]['hash']
            if anchored_head is not None and anchored_head != head:
                raise ValueError('independently anchored head mismatch')
            return HybridGateway.restore(
                sources=sources,
                event_jsonl='\n'.join(json_bytes(row).decode('utf8') for row in records),
                pinned_head=head,
                semantic_validator=registry.validate_claim if registry else None,
            )
        if anchored_head is not None:
            raise ValueError('anchored head supplied for empty ledger')
        gateway = HybridGateway(semantic_validator=registry.validate_claim if registry else None)
        for s in sources:
            gateway.register_source(s)
        return gateway

    def register_source(self, source: SourceDocument) -> None:
        with closing(self._connect()) as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                old = conn.execute('SELECT payload FROM sources WHERE source_id=?',
                                   (source.source_id,)).fetchone()
                if old is not None:
                    data = json.loads(old['payload'])
                    digest = data.pop('digest')
                    previous = SourceDocument(**data)
                    if previous.digest != digest:
                        raise ValueError('persisted source digest mismatch')
                    if previous != source:
                        raise SourceRegistrationError('source ID cannot be rebound')
                else:
                    # Reuse the ledger's metadata validation.
                    witness = HybridGateway()
                    witness.register_source(source)
                    conn.execute('INSERT INTO sources (source_id,payload) VALUES (?,?)',
                                 (source.source_id, json_bytes(asdict(source)).decode('utf8')))
                conn.execute('COMMIT')
            except BaseException:
                conn.execute('ROLLBACK')
                raise

    def snapshot(self, *, registry: Optional[TrustedContractRegistry] = None,
                 anchored_head: Optional[str] = None) -> HybridGateway:
        with closing(self._connect()) as conn:
            return self._load(conn, registry=registry, anchored_head=anchored_head)

    def audit_persisted_approvals(self, keyring: ReviewKeyring) -> dict:
        """Verify archived MACs and attachment to replayed events.

        Not proof of human review or a guarantee against replacing the local DB.
        """
        if not isinstance(keyring, ReviewKeyring):
            raise TypeError('trusted keyring required')
        with closing(self._connect()) as conn:
            gateway = self._load(conn)
            events_by_hash = {event['hash']: event for event in gateway.events}
            seen = set()
            bad = []
            rows = conn.execute('SELECT nonce,batch_digest,event_hash,approval_json FROM used_approvals').fetchall()
            for row in rows:
                try:
                    approval = SignedBatchApproval(**json.loads(row['approval_json']))
                    secret = keyring.get(approval.key_id)
                    event = events_by_hash.get(row['event_hash'])
                    ledger_id = conn.execute("SELECT value FROM gateway_settings WHERE name='ledger_id'").fetchone()
                    if (secret is None or event is None or event['kind'] != 'BATCH_ADMIT'
                        or ledger_id is None or approval.ledger_id != ledger_id['value']
                        or approval.purpose != PURPOSE or approval.nonce != row['nonce']
                        or approval.batch_digest != row['batch_digest']
                        or approval.recorded_at != event['at']
                        or approval.ledger_head_at_stage != event['prev_hash']
                        or row['event_hash'] in seen):
                        raise ValueError('approval-event mismatch')
                    actual = hmac.new(secret,json_bytes(approval.unsigned_payload()),hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(actual,approval.signature):
                        raise ValueError('invalid archived MAC')
                    seen.add(row['event_hash'])
                except (ValueError, KeyError, TypeError, AttributeError):
                    bad.append(row['nonce'])
            unverified = [event['hash'] for event in gateway.events
                          if event['kind']=='BATCH_ADMIT' and event['hash'] not in seen]
            return {'valid_approval_count':len(seen),
                    'invalid_approval_nonces':tuple(sorted(bad)),
                    'batch_events_without_verified_approval':tuple(unverified),
                    'verified_event_head':gateway.head_digest,
                    'limitations':'local MAC and event attachment, not human identity or external anchor'}

    def commit_batch(self, batch: AuditedBatch, *, registry: TrustedContractRegistry,
                     plan: ExtractionPlan, recorded_at: str,
                     reviewer_approved: bool = False,
                     independently_anchored_head: Optional[str] = None,
                     authorization: Optional[SignedBatchApproval] = None,
                     trusted_keys: Optional[ReviewKeyring] = None,
                     review_journal_authority: Optional[ReviewJournalAuthority] = None) -> Decision:
        """Commit an entire covered batch or none, as one SQLite transaction.

        The review receipt is not a signature. Recheck every candidate against the
        operator-locked plan and live database head UNDER the database write lock.
        No trusted review identity is established by reviewer_approved=True.
        """
        if authorization is None and not reviewer_approved:
            return Decision('REVIEW', 'separate trusted reviewer approval required')
        if not isinstance(batch, AuditedBatch) or not isinstance(plan, ExtractionPlan):
            return Decision('BLOCK', 'invalid batch or plan object')
        if batch.receipt.disposition != 'READY_FOR_REVIEW':
            return Decision('REVIEW', 'incomplete coverage audit cannot be committed')
        receipt = batch.receipt
        if (receipt.source_id != plan.source_id or
                receipt.source_digest != plan.source_digest or
                receipt.plan_fingerprint != plan.fingerprint or
                receipt.registry_fingerprint != registry.fingerprint or
                plan.registry_fingerprint != registry.fingerprint):
            return Decision('BLOCK', 'receipt or plan does not match contract authority')
        expected = set(plan.required_contract_fingerprints)
        if (not expected or len(expected) != len(plan.required_contract_fingerprints)
                or receipt.expected != len(expected)
                or receipt.received != len(expected)
                or receipt.supported_unique != len(expected)
                or receipt.missing_fingerprints or receipt.duplicate_fingerprints
                or receipt.unexpected_candidate_digests
                or len(batch.stages) != len(expected)
                or len(receipt.stage_candidate_digests) != len(expected)):
            return Decision('BLOCK', 'batch plan or coverage is incomplete or inconsistent')
        observed: set[str] = set()
        claims: list[ClaimProposal] = []
        for i, stage in enumerate(batch.stages):
            if not isinstance(stage, BoundStage):
                return Decision('BLOCK', 'invalid stage type')
            candidate = stage.staged.candidate
            if (not isinstance(candidate, ClaimProposal)
                    or stage.registry_fingerprint != registry.fingerprint
                    or stage.staged.registered_source_digest != receipt.source_digest
                    or candidate.source_id != receipt.source_id
                    or _fingerprint_candidate(candidate) != receipt.stage_candidate_digests[i]):
                return Decision('BLOCK', 'stage evidence no longer matches audited receipt')
            contract = registry.matched_contract(candidate)
            if (contract is None or contract.fingerprint != stage.contract_fingerprint
                    or contract.fingerprint not in expected or contract.fingerprint in observed):
                return Decision('BLOCK', 'unbound, duplicate or out-of-plan contract')
            observed.add(contract.fingerprint)
            claims.append(candidate)
        if observed != expected:
            return Decision('BLOCK', 'batch omitted an operator-required clause')
        # BEGIN IMMEDIATE serializes this read-check-write with other SQLite writers.
        with closing(self._connect()) as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                policy = conn.execute("SELECT value FROM gateway_settings WHERE name='approval_policy'").fetchone()
                if policy is not None and policy['value'] != 'signed_v1':
                    raise ValueError('unknown persisted authorization policy; fail closed')
                strict = policy is not None
                journal_policy=conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()
                if journal_policy is not None and journal_policy['value'] != 'journal_v1':
                    raise ValueError('unknown journal policy; fail closed')
                if journal_policy is not None:
                    if (not isinstance(review_journal_authority,ReviewJournalAuthority)
                            or not isinstance(trusted_keys,ReviewKeyring)
                            or not isinstance(authorization,SignedBatchApproval)
                            or review_journal_authority.key_id != authorization.key_id
                            or trusted_keys.get(review_journal_authority.key_id) != review_journal_authority.secret):
                        conn.execute('ROLLBACK')
                        return Decision('REVIEW','trusted signed review-journal authority required')
                ledger_id_row = conn.execute("SELECT value FROM gateway_settings WHERE name='ledger_id'").fetchone()
                if ledger_id_row is None:
                    raise ValueError('missing persisted ledger identity')
                if strict or authorization is not None:
                    if not verify_approval(authorization, batch=batch, plan=plan,
                          keyring=trusted_keys, recorded_at=recorded_at,
                          ledger_id=ledger_id_row['value']):
                        conn.execute('ROLLBACK')
                        return Decision('REVIEW', 'valid signed batch authorization required')
                    used = conn.execute('SELECT nonce FROM used_approvals WHERE nonce=?',
                                         (authorization.nonce,)).fetchone()
                    if used is not None:
                        conn.execute('ROLLBACK')
                        return Decision('BLOCK', 'approval nonce already consumed')
                if journal_policy is not None:
                    old=conn.execute('SELECT seq FROM review_decisions WHERE batch_digest=?',
                                     (batch_digest(batch),)).fetchone()
                    if old is not None:
                        conn.execute('ROLLBACK')
                        return Decision('BLOCK','review decision already recorded for this batch')
                gateway = self._load(conn, registry=registry,
                                     anchored_head=independently_anchored_head)
                if gateway.head_digest != receipt.ledger_head_at_stage:
                    conn.execute('ROLLBACK')
                    return Decision('REVIEW', 'ledger advanced since coverage audit; re-audit')
                source = registry.registered_source(plan.source_id)
                if source is None or source.digest != plan.source_digest:
                    conn.execute('ROLLBACK')
                    return Decision('BLOCK', 'operator source or plan changed')
                decision = gateway.ingest_batch(claims, recorded_at=recorded_at,
                                                reviewer_approved=True)
                if decision.disposition != 'ALLOW':
                    conn.execute('ROLLBACK')
                    return decision
                event = gateway.events[-1]
                if event['kind'] != 'BATCH_ADMIT':
                    raise AssertionError('atomic write did not create batch event')
                conn.execute('INSERT INTO events(seq,payload) VALUES (?,?)',
                             (event['seq'], json_bytes(event).decode('utf8')))
                if authorization is not None:
                    conn.execute('INSERT INTO used_approvals(nonce,batch_digest,event_hash,approval_json) VALUES (?,?,?,?)',
                        (authorization.nonce, authorization.batch_digest, event['hash'],
                         json_bytes(asdict(authorization)).decode('utf8')))
                if journal_policy is not None:
                    append_decision(conn,authority=review_journal_authority,batch=batch,plan=plan,
                        action='APPROVED',reason_code='WHOLE_BATCH_APPROVED',
                        event_hash=event['hash'], ledger_id=ledger_id_row['value'])
                conn.execute('COMMIT')
                return decision
            except BaseException:
                if conn.in_transaction:
                    conn.execute('ROLLBACK')
                raise

    def record_rejection(self, batch: AuditedBatch, *, registry: TrustedContractRegistry,
                         plan: ExtractionPlan, authority: ReviewJournalAuthority,
                         trusted_keys: ReviewKeyring) -> str:
        """Atomically persist a rejection, preventing this same batch from admission.

        Requires an independently authenticated reviewer workflow to supply a
        ReviewJournalAuthority. Never exposes the signing key over HTTP.
        """
        if (not isinstance(batch,AuditedBatch) or not isinstance(plan,ExtractionPlan) or
            not isinstance(authority,ReviewJournalAuthority) or
            not isinstance(trusted_keys,ReviewKeyring) or
            trusted_keys.get(authority.key_id) != authority.secret):
            raise TypeError('trusted review objects required')
        if (batch.receipt.disposition != 'READY_FOR_REVIEW' or
            batch.receipt.plan_fingerprint != plan.fingerprint or
            batch.receipt.registry_fingerprint != registry.fingerprint or
            plan.registry_fingerprint != registry.fingerprint or
            batch.receipt.source_digest != plan.source_digest or
            batch.receipt.source_id != plan.source_id):
            raise ValueError('incomplete or inconsistent review batch')
        with closing(self._connect()) as conn:
            try:
                conn.execute('BEGIN IMMEDIATE')
                policy=conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()
                approval_policy=conn.execute("SELECT value FROM gateway_settings WHERE name='approval_policy'").fetchone()
                if (policy is None or policy['value']!='journal_v1' or
                        approval_policy is None or approval_policy['value']!='signed_v1'):
                    raise ValueError('strict journal policy required')
                stored_id=conn.execute("SELECT value FROM gateway_settings WHERE name='ledger_id'").fetchone()
                if stored_id is None or stored_id['value']!=authority.ledger_id:
                    raise ValueError('ledger identity changed')
                gateway=self._load(conn,registry=registry)
                if gateway.head_digest != batch.receipt.ledger_head_at_stage:
                    raise ValueError('review is stale; re-audit')
                if registry.registered_source(plan.source_id) not in self._sources(conn):
                    raise ValueError('review source changed')
                rec=append_decision(conn,authority=authority,batch=batch,plan=plan,
                    action='REJECTED',reason_code='WHOLE_BATCH_REJECTED',event_hash=None,
                    ledger_id=stored_id['value'])
                conn.execute('COMMIT')
                return rec.entry_hash
            except BaseException:
                if conn.in_transaction: conn.execute('ROLLBACK')
                raise

    def audit_review_decisions(self, keyring: ReviewKeyring, *,
                               independently_anchored_journal_head: str | None = None) -> dict:
        with closing(self._connect()) as conn:
            self._load(conn)
            return audit_decisions(conn,ledger_id=self.ledger_id,keyring=keyring,
                expected_head=independently_anchored_journal_head)
