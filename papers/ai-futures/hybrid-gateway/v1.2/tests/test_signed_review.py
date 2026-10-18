"""Cycle 9: strict review approval is bound, short-lived, and consumed atomically."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from hybrid_gateway.authorization import (
    ReviewKeyring, issue_approval, verify_approval, SignedBatchApproval, batch_digest)
from hybrid_gateway.durable import SQLiteLedger
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW

KEY_A=b'a'*32
KEY_B=b'b'*32

class SignedReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'signed.sqlite3'
        self.store=SQLiteLedger(self.path, require_signed_approval=True)
        self.registry,self.plan,self.batch=prepare(self.store)
        self.keyring=ReviewKeyring({'operator-a':KEY_A})

    def approval(self, **kw):
        return issue_approval(self.batch,self.plan,key_id='operator-a',
                              secret=KEY_A,recorded_at=KNOW,ledger_id=self.store.ledger_id,**kw)

    def commit(self, approval=None, **kw):
        return self.store.commit_batch(self.batch, registry=self.registry,
            plan=self.plan,recorded_at=KNOW, authorization=approval,
            trusted_keys=self.keyring,**kw)

    def test_legacy_boolean_cannot_bypass_strict_policy(self):
        self.assertEqual(self.commit(reviewer_approved=True).disposition,'REVIEW')
        self.assertEqual(len(self.store.snapshot().events),0)

    def test_legacy_boolean_cannot_bypass_after_reopen(self):
        reopened=SQLiteLedger(self.path)
        d=reopened.commit_batch(self.batch,registry=self.registry,plan=self.plan,
                                recorded_at=KNOW,reviewer_approved=True)
        self.assertEqual(d.disposition,'REVIEW')

    def test_correct_approval_admits_exact_whole_batch(self):
        approval=self.approval()
        self.assertTrue(verify_approval(approval,batch=self.batch,plan=self.plan,
            recorded_at=KNOW,keyring=self.keyring,ledger_id=self.store.ledger_id))
        d=self.commit(approval)
        self.assertEqual(d.disposition,'ALLOW')
        g=SQLiteLedger(self.path).snapshot(anchored_head=d.event_hash)
        self.assertEqual(len(g.events),1)
        self.assertEqual(len(g.claims),2)
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute('select count(*) from used_approvals').fetchone()[0],1)

    def test_used_approval_cannot_commit_twice(self):
        p=self.approval()
        self.assertEqual(self.commit(p).disposition,'ALLOW')
        self.assertNotEqual(self.commit(p).disposition,'ALLOW')

    def test_tampered_signature_rejected(self):
        p=self.approval()
        self.assertEqual(self.commit(replace(p,signature='0'*64)).disposition,'REVIEW')
        self.assertEqual(len(self.store.snapshot().events),0)

    def test_wrong_key_rejected(self):
        p=self.approval()
        self.keyring=ReviewKeyring({'operator-a':KEY_B})
        self.assertEqual(self.commit(p).disposition,'REVIEW')

    def test_revoked_key_id_rejected(self):
        p=self.approval()
        self.keyring=ReviewKeyring({'operator-b':KEY_B})
        self.assertEqual(self.commit(p).disposition,'REVIEW')

    def test_wrong_recorded_at_rejected(self):
        p=self.approval()
        d=self.store.commit_batch(self.batch,registry=self.registry,plan=self.plan,
                                  recorded_at='2026-10-05T00:00:00Z',authorization=p,
                                  trusted_keys=self.keyring)
        self.assertEqual(d.disposition,'REVIEW')

    def test_forged_batch_digest_rejected(self):
        p=self.approval()
        self.assertEqual(self.commit(replace(p,batch_digest='sha256:'+'0'*64)).disposition,'REVIEW')

    def test_nonce_tampering_rejected(self):
        p=self.approval()
        self.assertEqual(self.commit(replace(p,nonce='0'*48)).disposition,'REVIEW')

    def test_purpose_tampering_rejected(self):
        p=self.approval()
        self.assertEqual(self.commit(replace(p,purpose='general')).disposition,'REVIEW')

    def test_future_issued_at_rejected(self):
        future=datetime.now(timezone.utc)+timedelta(hours=1)
        p=self.approval(now=future)
        self.assertEqual(self.commit(p).disposition,'REVIEW')

    def test_expired_signature_rejected(self):
        old=datetime.now(timezone.utc)-timedelta(seconds=900)
        p=self.approval(now=old)
        self.assertEqual(self.commit(p).disposition,'REVIEW')

    def test_ttl_bounded(self):
        with self.assertRaises(ValueError): self.approval(ttl_seconds=9000)

    def test_signature_cannot_be_reused_for_other_batch(self):
        p=self.approval()
        from dataclasses import replace as r
        other=r(self.batch, receipt=r(self.batch.receipt, note='changed presentation'))
        self.assertFalse(verify_approval(p,batch=other,plan=self.plan,
                                         recorded_at=KNOW,keyring=self.keyring,ledger_id=self.store.ledger_id))

    def test_failed_db_write_rolls_back_approval_use(self):
        p=self.approval()
        # Force event insertion failure via SQLite abort trigger.
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TRIGGER abort_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.commit(p)
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute('select count(*) from used_approvals').fetchone()[0],0)
            self.assertEqual(conn.execute('select count(*) from events').fetchone()[0],0)
            conn.execute('DROP TRIGGER abort_event')
        self.assertEqual(self.commit(p).disposition,'ALLOW')

    def test_key_rotation_allows_new_key_only(self):
        old=self.approval()
        self.keyring=ReviewKeyring({'operator-b':KEY_B})
        self.assertEqual(self.commit(old).disposition,'REVIEW')
        new=issue_approval(self.batch,self.plan,key_id='operator-b',secret=KEY_B,recorded_at=KNOW,ledger_id=self.store.ledger_id)
        self.assertEqual(self.commit(new).disposition,'ALLOW')

    def test_no_secret_written_to_sqlite_file(self):
        key=b'SECRET_MARKER_FOR_TEST_'+b'Z'*32
        signed=issue_approval(self.batch,self.plan,key_id='test',secret=key,recorded_at=KNOW,ledger_id=self.store.ledger_id)
        self.keyring=ReviewKeyring({'test':key})
        self.assertEqual(self.commit(signed).disposition,'ALLOW')
        self.assertNotIn(key,self.path.read_bytes())

    def test_duplicate_signed_nonce_cannot_admit_new_batch(self):
        p=self.approval(nonce='a'*48)
        self.assertEqual(self.commit(p).disposition,'ALLOW')
        # Reseal a different authorization with same nonce after first event; it still fails.
        self.registry,self.plan,newbatch=prepare(self.store)
        self.batch=newbatch
        newer=self.approval(nonce='a'*48)
        self.assertEqual(self.commit(newer).disposition,'BLOCK')

    def test_malformed_key_rejected(self):
        with self.assertRaises(ValueError): ReviewKeyring({'x':b'bad'})
        with self.assertRaises(ValueError): ReviewKeyring({'weird key':b'1'*32})

    def test_independent_database_cannot_reuse_approval(self):
        p=self.approval()
        other_path=Path(self.tmp.name)/'other.sqlite3'
        other=SQLiteLedger(other_path,require_signed_approval=True)
        r,plan,batch=prepare(other)
        self.assertNotEqual(self.store.ledger_id,other.ledger_id)
        d=other.commit_batch(batch,registry=r,plan=plan,
            recorded_at=KNOW,authorization=p,trusted_keys=self.keyring)
        self.assertEqual(d.disposition,'REVIEW')

    def test_ledger_identity_survives_reopen(self):
        self.assertEqual(self.store.ledger_id,SQLiteLedger(self.path).ledger_id)

    def test_tampered_ledger_identity_fails_signature(self):
        p=self.approval()
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE gateway_settings SET value=? WHERE name='ledger_id'",('0'*48,))
        self.assertEqual(self.commit(p).disposition,'REVIEW')

    def test_unknown_auth_policy_fails_closed(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE gateway_settings SET value='unsigned' WHERE name='approval_policy'")
        with self.assertRaises(ValueError): self.commit(self.approval())

    def test_signed_mode_upgrade_is_persistent(self):
        path=Path(self.tmp.name)/'upgrade.sqlite3'
        legacy=SQLiteLedger(path)
        self.assertIsNone(legacy.snapshot().head_digest)
        strict=SQLiteLedger(path,require_signed_approval=True)
        registry,plan,batch=prepare(strict)
        self.assertEqual(SQLiteLedger(path).commit_batch(batch,registry=registry,plan=plan,
            recorded_at=KNOW,reviewer_approved=True).disposition,'REVIEW')

    def test_cross_key_id_mismatch_rejected(self):
        p=self.approval()
        self.assertEqual(self.commit(replace(p,key_id='operator-b')).disposition,'REVIEW')

    def test_negative_ttl_rejected(self):
        with self.assertRaises(ValueError): self.approval(ttl_seconds=-2)

    def test_missing_ledger_id_rejected_at_signing(self):
        with self.assertRaises(TypeError):
            issue_approval(self.batch,self.plan,key_id='operator-a',secret=KEY_A,recorded_at=KNOW)

    def test_archived_authorization_can_be_verified_after_restart(self):
        p=self.approval()
        self.assertEqual(self.commit(p).disposition,'ALLOW')
        audit=SQLiteLedger(self.path).audit_persisted_approvals(self.keyring)
        self.assertEqual(audit['valid_approval_count'],1)
        self.assertEqual(audit['invalid_approval_nonces'],())
        self.assertEqual(audit['batch_events_without_verified_approval'],())

    def test_archived_authorization_fails_with_wrong_key(self):
        self.assertEqual(self.commit(self.approval()).disposition,'ALLOW')
        audit=self.store.audit_persisted_approvals(ReviewKeyring({'operator-a':KEY_B}))
        self.assertEqual(audit['valid_approval_count'],0)
        self.assertEqual(len(audit['invalid_approval_nonces']),1)
        self.assertEqual(len(audit['batch_events_without_verified_approval']),1)

    def test_archived_authorization_detects_tampered_mac(self):
        p=self.approval()
        self.assertEqual(self.commit(p).disposition,'ALLOW')
        import json
        with sqlite3.connect(self.path) as conn:
            row=conn.execute('SELECT nonce,approval_json FROM used_approvals').fetchone()
            item=json.loads(row[1]);item['signature']='0'*64
            conn.execute('UPDATE used_approvals SET approval_json=? WHERE nonce=?',
                         (json.dumps(item),row[0]))
        audit=self.store.audit_persisted_approvals(self.keyring)
        self.assertEqual(audit['valid_approval_count'],0)
        self.assertEqual(len(audit['invalid_approval_nonces']),1)

    def test_archived_authorization_detects_wrong_event_link(self):
        p=self.approval()
        self.assertEqual(self.commit(p).disposition,'ALLOW')
        with sqlite3.connect(self.path) as conn:
            conn.execute('UPDATE used_approvals SET event_hash=?',('sha256:'+'a'*64,))
        audit=self.store.audit_persisted_approvals(self.keyring)
        self.assertEqual(len(audit['invalid_approval_nonces']),1)

    def test_before_admission_audit_is_empty(self):
        audit=self.store.audit_persisted_approvals(self.keyring)
        self.assertEqual(audit['valid_approval_count'],0)
        self.assertEqual(audit['batch_events_without_verified_approval'],())

    def test_archived_ledger_id_mismatch_is_detected(self):
        self.assertEqual(self.commit(self.approval()).disposition,'ALLOW')
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE gateway_settings SET value=? WHERE name='ledger_id'",('f'*48,))
        audit=self.store.audit_persisted_approvals(self.keyring)
        self.assertEqual(len(audit['invalid_approval_nonces']),1)

    def test_no_keys_rejected(self):
        with self.assertRaises(ValueError): ReviewKeyring({})

    def test_signed_permission_does_not_claim_human_identity(self):
        self.assertNotIn('reviewer_identity',self.approval().unsigned_payload())

if __name__=='__main__': unittest.main()
