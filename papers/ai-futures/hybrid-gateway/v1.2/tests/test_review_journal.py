"""Cycle 11: persistent approval + rejection, atomic signing journal contract.

All actors are fixture simulations; no real human identity is verified.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import json
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from hybrid_gateway.review_desk import ReviewDesk
from hybrid_gateway.durable import SQLiteLedger
from hybrid_gateway.authorization import issue_approval,ReviewKeyring,batch_digest
from hybrid_gateway.review_journal import ReviewJournalAuthority
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW,SRC

PW = 'long testing password for browser only'
KEY = b'cycle-eleven-internal-hmac-key-40byte!'

class ReviewJournalTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'decisions.db'
        self.db=SQLiteLedger(self.path,require_review_journal=True)
        self.r,self.p,self.b=prepare(self.db)
        self.desk=self.make_desk()

    def make_desk(self,db=None):
        return ReviewDesk(ledger=db or self.db,registry=self.r,plan=self.p,batch=self.b,
            recorded_at=KNOW,key_id='fixture-local',signing_secret=KEY,password=PW)

    def session(self,desk=None):
        desk=desk or self.desk
        token,csrf=desk.login(PW)
        self.assertIsNotNone(desk.start_review(token))
        return token,csrf

    def vote(self,action='approve',desk=None):
        desk=desk or self.desk
        token,csrf=self.session(desk)
        return desk.submit(token,csrf=csrf,presented_digest=desk.view_digest,
                           decision=action,confirmation='YES_REVIEWED_EXACT_BATCH' if action=='approve' else '')

    def audit(self,key=KEY,head=None):
        return SQLiteLedger(self.path).audit_review_decisions(
            ReviewKeyring({'fixture-local':key}),independently_anchored_journal_head=head)

    def authority(self,desk=None):
        desk=desk or self.desk
        return ReviewJournalAuthority(key_id='fixture-local',secret=KEY,
            ledger_id=self.db.ledger_id,presentation_digest=desk.view_digest,
            batch_fingerprint=batch_digest(self.b))

    def permit(self):
        return issue_approval(self.b,self.p,key_id='fixture-local',secret=KEY,
                              recorded_at=KNOW,ledger_id=self.db.ledger_id)

    def test_empty_journal_verifies(self):
        self.assertEqual(self.audit()['total'],0)
        self.assertEqual(self.audit()['invalid_entries'],())

    def test_approval_event_and_signed_record_together(self):
        result=self.vote()
        self.assertEqual(result.disposition,'APPROVED')
        a=self.audit()
        self.assertEqual((a['total'],a['verified_approvals'],a['verified_rejections']), (1,1,0))
        self.assertFalse(a['invalid_entries'])
        self.assertEqual(len(SQLiteLedger(self.path).snapshot().claims),2)
        self.assertEqual(self.audit(head=a['journal_head'])['invalid_entries'],())

    def test_rejection_persists_without_knowledge_event(self):
        self.assertEqual(self.vote('reject').disposition,'REJECTED')
        self.assertFalse(SQLiteLedger(self.path).snapshot().claims)
        a=self.audit()
        self.assertEqual((a['total'],a['verified_rejections']), (1,1))
        self.assertFalse(a['invalid_entries'])

    def test_rejection_prevents_signed_admission_from_another_process(self):
        self.vote('reject')
        reopened=SQLiteLedger(self.path)
        result=reopened.commit_batch(self.b,registry=self.r,plan=self.p,
            recorded_at=KNOW,authorization=self.permit(),trusted_keys=ReviewKeyring({'fixture-local':KEY}),
            review_journal_authority=self.authority())
        self.assertEqual(result.disposition,'BLOCK')
        self.assertFalse(reopened.snapshot().claims)

    def test_old_boolean_and_signed_permit_without_journal_fail(self):
        old=SQLiteLedger(self.path)
        r=old.commit_batch(self.b,registry=self.r,plan=self.p,recorded_at=KNOW,
                           reviewer_approved=True)
        self.assertEqual(r.disposition,'REVIEW')
        r=old.commit_batch(self.b,registry=self.r,plan=self.p,recorded_at=KNOW,
                           authorization=self.permit(),trusted_keys=ReviewKeyring({'fixture-local':KEY}))
        self.assertEqual(r.disposition,'REVIEW')

    def test_approval_replay_rejected(self):
        self.assertEqual(self.vote().disposition,'APPROVED')
        self.assertEqual(self.vote().disposition,'BLOCK')
        self.assertEqual(self.audit()['total'],1)

    def test_two_separate_desks_cannot_reject_same_batch_twice(self):
        other=self.make_desk(SQLiteLedger(self.path))
        self.assertEqual(self.vote('reject').disposition,'REJECTED')
        self.assertEqual(self.vote('reject',other).disposition,'BLOCK')
        self.assertEqual(self.audit()['total'],1)

    def test_prior_rejection_survives_reopening_browser_desk(self):
        self.vote('reject')
        next_desk=self.make_desk(SQLiteLedger(self.path))
        self.assertNotEqual(self.vote('approve',next_desk).disposition,'APPROVED')

    def test_changed_batch_authority_rejected(self):
        a=replace(self.authority(), batch_fingerprint='sha256:'+'a'*64)
        with self.assertRaises(ValueError):
            self.db.record_rejection(self.b,registry=self.r,plan=self.p,authority=a,trusted_keys=ReviewKeyring({'fixture-local':KEY}))
        self.assertEqual(self.audit()['total'],0)

    def test_cross_database_authority_rejected(self):
        other=SQLiteLedger(self.path.parent/'other.db',require_review_journal=True)
        r,p,b=prepare(other)
        with self.assertRaises(ValueError):
            other.record_rejection(b,registry=r,plan=p,authority=self.authority(),trusted_keys=ReviewKeyring({'fixture-local':KEY}))

    def test_explicit_external_journal_anchor_detects_tail_removal(self):
        self.vote('reject')
        first=self.audit()['journal_head']
        with sqlite3.connect(self.path) as conn:
            conn.execute('DELETE FROM review_decisions')
        self.assertEqual(self.audit()['total'],0)
        self.assertIn('external_head_mismatch',self.audit(head=first)['invalid_entries'])

    def test_unsigned_rejection_tampering_detected(self):
        self.vote('reject')
        with sqlite3.connect(self.path) as conn:
            d=json.loads(conn.execute('SELECT payload FROM review_decisions').fetchone()[0])
            d['reason_code']='not-reviewed'
            conn.execute('UPDATE review_decisions SET payload=?',(json.dumps(d),))
        self.assertTrue(self.audit()['invalid_entries'])

    def test_forged_mac_detected(self):
        self.vote('reject')
        with sqlite3.connect(self.path) as conn:
            d=json.loads(conn.execute('SELECT payload FROM review_decisions').fetchone()[0])
            d['signature']='f'*64
            conn.execute('UPDATE review_decisions SET payload=?',(json.dumps(d),))
        self.assertTrue(self.audit()['invalid_entries'])

    def test_wrong_key_rejects_audit(self):
        self.vote('reject')
        self.assertTrue(self.audit(key=b'other-long-cryptographic-fixture-secret')['invalid_entries'])

    def test_rejection_write_failure_not_misreported_as_success(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TRIGGER abort_journal BEFORE INSERT ON review_decisions BEGIN SELECT RAISE(ABORT, 'injected'); END")
        # Browser maps DB failure to a non-success outcome.
        self.assertNotEqual(self.vote('reject').disposition,'REJECTED')
        self.assertEqual(self.audit()['total'],0)
        with sqlite3.connect(self.path) as conn: conn.execute('DROP TRIGGER abort_journal')
        self.assertEqual(self.vote('reject').disposition,'REJECTED')

    def test_approval_journal_write_failure_rolls_back_claims_and_permit(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TRIGGER abort_journal BEFORE INSERT ON review_decisions BEGIN SELECT RAISE(ABORT, 'injected'); END")
        # Browser maps this to a blocking outcome, but must not claim success.
        r=self.vote()
        self.assertNotEqual(r.disposition,'APPROVED')
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM events').fetchone()[0],0)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM used_approvals').fetchone()[0],0)
        with sqlite3.connect(self.path) as conn:conn.execute('DROP TRIGGER abort_journal')
        self.assertEqual(self.vote().disposition,'APPROVED')

    def test_review_journal_is_privacy_minimal(self):
        self.vote('reject')
        with sqlite3.connect(self.path) as conn:
            blob=conn.execute('SELECT payload FROM review_decisions').fetchone()[0]
        self.assertNotIn(SRC.body,blob)
        self.assertNotIn(PW,blob)
        self.assertNotIn(KEY.decode('utf8'),blob)

    def test_journal_mode_persists_reopen(self):
        reopened=SQLiteLedger(self.path)
        self.assertEqual(reopened.commit_batch(self.b,registry=self.r,plan=self.p,
            recorded_at=KNOW,reviewer_approved=True).disposition,'REVIEW')
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone()[0],'journal_v1')

    def test_unknown_journal_policy_fails_closed(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE gateway_settings SET value='unreviewed' WHERE name='review_policy'")
        self.assertNotEqual(self.vote().disposition,'APPROVED')

    def test_rejection_ledger_advanced_stale(self):
        # Trusted direct test path commits before rejecting old source plan.
        signed=self.permit()
        result=self.db.commit_batch(self.b,registry=self.r,plan=self.p,recorded_at=KNOW,
            authorization=signed,trusted_keys=ReviewKeyring({'fixture-local':KEY}),
            review_journal_authority=self.authority())
        self.assertEqual(result.disposition,'ALLOW')
        other=self.make_desk(SQLiteLedger(self.path))
        self.assertNotEqual(self.vote('reject',other).disposition,'REJECTED')

    def test_approval_and_rejection_race_only_one_can_win(self):
        approve=self.make_desk(SQLiteLedger(self.path))
        reject=self.make_desk(SQLiteLedger(self.path))
        with ThreadPoolExecutor(max_workers=2) as pool:
            a=pool.submit(self.vote,'approve',approve)
            b=pool.submit(self.vote,'reject',reject)
            outcomes=(a.result().disposition,b.result().disposition)
        self.assertEqual(sum(x in ('APPROVED','REJECTED') for x in outcomes),1)
        self.assertEqual(self.audit()['total'],1)

    def test_validated_journal_entries_have_no_raw_claims(self):
        self.vote()
        with sqlite3.connect(self.path) as conn:
            content=conn.execute('SELECT payload FROM review_decisions').fetchone()[0]
        self.assertNotIn(SRC.body,content)
        self.assertNotIn('loyalty points',content.lower())

    def test_approval_sqlite_operational_error_returns_no_false_success(self):
        from unittest.mock import patch
        with patch('hybrid_gateway.durable.append_decision',side_effect=sqlite3.OperationalError('simulated io error')):
            result=self.vote('approve')
        self.assertNotEqual(result.disposition,'APPROVED')
        self.assertEqual(self.audit()['total'],0)
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_rejection_sqlite_operational_error_returns_no_false_success(self):
        from unittest.mock import patch
        with patch('hybrid_gateway.durable.append_decision',side_effect=sqlite3.OperationalError('simulated io error')):
            result=self.vote('reject')
        self.assertNotEqual(result.disposition,'REJECTED')
        self.assertEqual(self.audit()['total'],0)

    def test_journal_authority_cannot_use_different_key_than_signed_permit(self):
        otherkey=b'extra-operator-controlled-key-39bytes!!!'
        alternate=ReviewJournalAuthority(key_id='other',secret=otherkey,
            ledger_id=self.db.ledger_id,presentation_digest=self.desk.view_digest,
            batch_fingerprint=batch_digest(self.b))
        result=self.db.commit_batch(self.b,registry=self.r,plan=self.p,recorded_at=KNOW,
            authorization=self.permit(),trusted_keys=ReviewKeyring({'fixture-local':KEY,'other':otherkey}),
            review_journal_authority=alternate)
        self.assertEqual(result.disposition,'REVIEW')
        self.assertEqual(self.audit()['total'],0)
        self.assertFalse(self.db.snapshot().claims)

if __name__=='__main__':unittest.main()

# Additional chain and downgrade tests remain separate from the review-flow tests.
class ReviewJournalChainTests(unittest.TestCase):
    setUp=ReviewJournalTests.setUp
    make_desk=ReviewJournalTests.make_desk
    session=ReviewJournalTests.session
    vote=ReviewJournalTests.vote
    audit=ReviewJournalTests.audit
    def test_two_decisions_are_linked_and_auditable(self):
        self.vote('reject')
        first=self.audit()['journal_head']
        from tests.test_contracts import candidate
        from tests.test_coverage import loyalty_candidate
        self.r,self.p,self.b=prepare(self.db,claims=[
            replace(candidate(),claim_id='new-refund'),
            replace(loyalty_candidate(),claim_id='new-loyalty')])
        self.desk=self.make_desk()
        self.assertEqual(self.vote().disposition,'APPROVED')
        result=self.audit()
        self.assertEqual((result['total'],result['verified_rejections'],result['verified_approvals']), (2,1,1))
        self.assertEqual(result['invalid_entries'],())
        with sqlite3.connect(self.path) as conn:
            newest=json.loads(conn.execute('SELECT payload FROM review_decisions WHERE seq=2').fetchone()[0])
        self.assertEqual(newest['prior_hash'],first)

    def test_tampered_first_decision_prevents_new_decision(self):
        self.vote('reject')
        from tests.test_contracts import candidate
        from tests.test_coverage import loyalty_candidate
        self.r,self.p,self.b=prepare(self.db,claims=[replace(candidate(),claim_id='second-refund'),
                                             replace(loyalty_candidate(),claim_id='second-loyalty')])
        self.desk=self.make_desk()
        with sqlite3.connect(self.path) as conn:
            record=json.loads(conn.execute('SELECT payload FROM review_decisions WHERE seq=1').fetchone()[0])
            record['signature']='0'*64
            conn.execute('UPDATE review_decisions SET payload=? WHERE seq=1',(json.dumps(record),))
        self.assertNotEqual(self.vote().disposition,'APPROVED')
        self.assertEqual(len(self.db.snapshot().events),0)
        self.assertEqual(self.audit()['total'],1)

    def test_existing_event_must_be_migrated_not_silently_retro_certified(self):
        path=self.path.parent/'legacy-events.sqlite3'
        existing=SQLiteLedger(path,require_signed_approval=True)
        registry,plan,batch=prepare(existing)
        p=issue_approval(batch,plan,key_id='fixture-local',secret=KEY,
                         recorded_at=KNOW,ledger_id=existing.ledger_id)
        self.assertEqual(existing.commit_batch(batch,registry=registry,plan=plan,recorded_at=KNOW,
            authorization=p,trusted_keys=ReviewKeyring({'fixture-local':KEY})).disposition,'ALLOW')
        with self.assertRaises(ValueError): SQLiteLedger(path,require_review_journal=True)
        with sqlite3.connect(path) as conn:
            self.assertIsNone(conn.execute("SELECT value FROM gateway_settings WHERE name='review_policy'").fetchone())

class ReviewJournalHTTPTests(unittest.TestCase):
    setUp=ReviewJournalTests.setUp
    make_desk=ReviewJournalTests.make_desk
    audit=ReviewJournalTests.audit

    def _http_vote(self,action):
        from http.client import HTTPConnection
        from threading import Thread
        from urllib.parse import urlencode
        from hybrid_gateway.review_desk import make_review_server
        server=make_review_server(self.desk)
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            addr=f'127.0.0.1:{server.server_port}'
            def post(path,data,cookie=''):
                conn=HTTPConnection('127.0.0.1',server.server_port,timeout=5)
                h={'Host':addr,'Origin':'http://'+addr,'Content-Type':'application/x-www-form-urlencoded'}
                if cookie:h['Cookie']=cookie
                conn.request('POST',path,urlencode(data),h)
                resp=conn.getresponse();body=resp.read().decode();headers=dict(resp.getheaders());code=resp.status
                conn.close()
                return code,body,headers
            status,body,headers=post('/login',{'password':PW})
            self.assertEqual(status,200)
            cookie=headers['Set-Cookie'].split(';')[0]
            import re
            csrf=re.search(r'name="csrf" value="([^"]+)"',body).group(1)
            digest=re.search(r'name="digest" value="([^"]+)"',body).group(1)
            data={'csrf':csrf,'digest':digest}
            if action=='approve':data['confirmation']='YES_REVIEWED_EXACT_BATCH'
            status,body,_=post('/'+action,data,cookie)
            return status,body
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)

    def test_http_rejection_is_durable(self):
        code,body=self._http_vote('reject')
        self.assertEqual(code,200)
        self.assertIn('REJECTED',body)
        self.assertEqual(self.audit()['verified_rejections'],1)
        self.assertFalse(self.db.snapshot().claims)

    def test_http_approval_is_atomically_journaled(self):
        code,body=self._http_vote('approve')
        self.assertEqual(code,200)
        self.assertIn('APPROVED',body)
        self.assertEqual(self.audit()['verified_approvals'],1)
        self.assertEqual(len(self.db.snapshot().claims),2)
