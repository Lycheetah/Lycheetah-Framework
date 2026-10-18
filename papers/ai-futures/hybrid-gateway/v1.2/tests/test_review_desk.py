"""Cycle 10: loopback review and authenticated confirmation tests, no live users."""
from dataclasses import replace
from http.client import HTTPConnection
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.parse import urlencode
import re
import secrets
import unittest

from hybrid_gateway.review_desk import ReviewDesk, make_review_server
from hybrid_gateway.durable import SQLiteLedger
from tests.test_atomic_batch import prepare
from tests.test_contracts import KNOW, SRC

PW='LOCAL DEMO PASSWORD ONLY - NOT A REAL REVIEWER'
KEY=b'cycle-10-fixture-signing-key-42A!!!'

class ReviewDeskTests(unittest.TestCase):
    def setUp(self):
        self.t=TemporaryDirectory(); self.addCleanup(self.t.cleanup)
        self.db=SQLiteLedger(Path(self.t.name)/'review.db',require_signed_approval=True)
        self.registry,self.plan,self.batch=prepare(self.db)
        self.desk=ReviewDesk(ledger=self.db,registry=self.registry,plan=self.plan,
            batch=self.batch,recorded_at=KNOW,key_id='fixture-signing',signing_secret=KEY,password=PW)

    def login(self):
        token, csrf = self.desk.login(PW)
        self.desk.start_review(token)
        return token,csrf

    def submit(self, token, csrf, **kw):
        args = {'csrf':csrf,'presented_digest':self.desk.view_digest,
                'decision':'approve','confirmation':'YES_REVIEWED_EXACT_BATCH'}
        args.update(kw)
        return self.desk.submit(token,**args)

    def test_password_length(self):
        with self.assertRaises(ValueError):
            ReviewDesk(ledger=self.db,registry=self.registry,plan=self.plan,batch=self.batch,
                recorded_at=KNOW,key_id='fixture-signing',signing_secret=KEY,password='short')

    def test_cannot_operate_on_legacy_database(self):
        db=SQLiteLedger(Path(self.t.name)/'legacy.db')
        r,p,b=prepare(db)
        with self.assertRaises(ValueError):
            ReviewDesk(ledger=db,registry=r,plan=p,batch=b,recorded_at=KNOW,
                key_id='fixture-signing',signing_secret=KEY,password=PW)

    def test_bad_login_no_token(self):
        self.assertIsNone(self.desk.login('wrong-password'))
        self.assertIsNone(self.desk.session('fake-token'))

    def test_brute_force_lockout(self):
        for _ in range(5):self.assertIsNone(self.desk.login('wrong-password',now=200))
        self.assertIsNone(self.desk.login(PW,now=201))
        self.assertIsNotNone(self.desk.login(PW,now=262))

    def test_session_expires_and_cookie_is_bearer(self):
        token,csrf=self.desk.login(PW,now=10)
        self.assertIsNotNone(self.desk.start_review(token,now=10))
        self.assertIsNone(self.desk.session(token,now=910))
        self.assertEqual(self.submit(token,csrf,now=911).disposition,'REVIEW')

    def test_missing_review_view_blocks_approval(self):
        token,csrf=self.desk.login(PW)
        self.assertEqual(self.submit(token,csrf).disposition,'REVIEW')

    def test_csrf_rejected_and_no_change(self):
        token,csrf=self.login()
        self.assertEqual(self.submit(token,'wrong').disposition,'BLOCK')
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_changed_presentation_rejected(self):
        token,csrf=self.login()
        self.assertEqual(self.submit(token,csrf,presented_digest='sha256:fake').disposition,'BLOCK')
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_explicit_checkbox_required(self):
        token,csrf=self.login()
        self.assertEqual(self.submit(token,csrf,confirmation='').disposition,'REVIEW')
        self.assertEqual(len(self.db.snapshot().events),0)

    def test_approve_exact_two_claim_batch_once(self):
        token,csrf=self.login()
        result=self.submit(token,csrf)
        self.assertEqual(result.disposition,'APPROVED')
        self.assertTrue(result.event_hash)
        self.assertEqual(len(self.db.snapshot(anchored_head=result.event_hash).claims),2)
        self.assertEqual(self.submit(token,csrf).disposition,'BLOCK')
        from hybrid_gateway.authorization import ReviewKeyring
        audit=self.db.audit_persisted_approvals(ReviewKeyring({'fixture-signing':KEY}))
        self.assertEqual(audit['valid_approval_count'],1)

    def test_reject_is_no_commit(self):
        token,csrf=self.login()
        result=self.submit(token,csrf,decision='reject',confirmation='')
        self.assertEqual(result.disposition,'REJECTED')
        self.assertFalse(self.db.snapshot().claims)
        self.assertEqual(self.submit(token,csrf).disposition,'BLOCK')

    def test_session_logout(self):
        token,csrf=self.login();self.desk.logout(token)
        self.assertEqual(self.submit(token,csrf).disposition,'REVIEW')

    def test_changed_plan_is_rejected(self):
        token,csrf=self.login()
        self.desk.plan=replace(self.plan,source_id='foreign')
        self.assertEqual(self.submit(token,csrf).disposition,'REVIEW')
        self.assertFalse(self.db.snapshot().claims)

    def test_changed_candidate_is_rejected(self):
        token,csrf=self.login()
        first=replace(self.batch.stages[0].staged.candidate,value='1000')
        changed=replace(self.batch.stages[0],staged=replace(self.batch.stages[0].staged,candidate=first))
        self.desk.batch=replace(self.batch,stages=(changed,)+self.batch.stages[1:])
        self.assertEqual(self.submit(token,csrf).disposition,'REVIEW')
        self.assertFalse(self.db.snapshot().claims)

    def test_source_xss_is_html_escaped(self):
        # Patch an exposed source object only to exercise output escaping.
        self.desk.source=replace(self.desk.source,body='<script>alert(1)</script>')
        html=self.desk.review_html('testcsrf')
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        token,csrf=self.login()
        self.assertEqual(self.submit(token,csrf).disposition,'REVIEW')

    def test_presentation_contains_all_fields_and_source(self):
        page=self.desk.review_html('x')
        self.assertIn(SRC.body,page)
        self.assertIn('Candidate 1',page)
        self.assertIn('Candidate 2',page)
        self.assertIn('Exact presentation digest',page)
        self.assertIn('effective',page.lower())

    def test_stale_head_not_authorized(self):
        token,csrf=self.login()
        # Another trusted operator path commits before review decision.
        from hybrid_gateway.authorization import issue_approval,ReviewKeyring
        permit=issue_approval(self.batch,self.plan,key_id='fixture-signing',secret=KEY,
                              recorded_at=KNOW,ledger_id=self.db.ledger_id)
        external=self.db.commit_batch(self.batch,registry=self.registry,plan=self.plan,
            recorded_at=KNOW,authorization=permit,trusted_keys=ReviewKeyring({'fixture-signing':KEY}))
        self.assertEqual(external.disposition,'ALLOW')
        result=self.submit(token,csrf)
        self.assertEqual(result.disposition,'REVIEW')
        self.assertEqual(len(self.db.snapshot().events),1)

    def test_observation_has_no_sensitive_source_or_password(self):
        token,csrf=self.login()
        self.submit(token,csrf,decision='reject',confirmation='')
        import json
        row=json.dumps(self.desk.observation())
        self.assertIn('REJECTED',row)
        self.assertNotIn(PW,row)
        self.assertNotIn(SRC.body,row)
        self.assertNotIn('SECRET',row)
        self.assertIn('session_elapsed_seconds',row)

    def test_undecided_observation_cannot_be_counted_as_human_approval(self):
        row=self.desk.observation()
        self.assertEqual(row['status'],'UNDECIDED')
        self.assertIsNone(row['committed_event_hash'])
        self.assertIsNone(row['session_elapsed_seconds'])

    def test_decision_duration_is_measurement_not_attestation(self):
        token,csrf=self.desk.login(PW,now=100)
        self.desk.start_review(token,now=101)
        result=self.submit(token,csrf,decision='reject',confirmation='',now=106)
        self.assertEqual(result.elapsed_seconds,5)

class HTTPReviewTests(unittest.TestCase):
    """Actual loopback HTTP requests; intentionally avoid duplicating unit tests."""
    def setUp(self):
        ReviewDeskTests.setUp(self)
        self.http=make_review_server(self.desk)
        self.thread=Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.thread.join,2)
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)
        self.addr=f'127.0.0.1:{self.http.server_port}'

    def request(self, method, path, data=None, *, cookie='', origin=True,
                content_type='application/x-www-form-urlencoded',host=None):
        conn=HTTPConnection('127.0.0.1',self.http.server_port,timeout=3)
        headers={'Host':host or self.addr}
        if method=='POST':
            if origin:headers['Origin']='http://'+self.addr
            headers['Content-Type']=content_type
        if cookie:headers['Cookie']=cookie
        body=urlencode(data) if isinstance(data,dict) else data
        conn.request(method,path,body,headers)
        resp=conn.getresponse()
        payload=resp.read().decode('utf-8')
        outcome=(resp.status, payload, dict(resp.getheaders()))
        conn.close()
        return outcome

    def http_login(self):
        status,body,headers=self.request('POST','/login',{'password':PW})
        self.assertEqual(status,200)
        cookie=headers['Set-Cookie'].split(';')[0]
        csrf=re.search(r'name="csrf" value="([^"]+)"',body).group(1)
        digest=re.search(r'name="digest" value="([^"]+)"',body).group(1)
        return cookie,csrf,digest,headers

    def test_get_login_has_no_evidence(self):
        code,body,headers=self.request('GET','/')
        self.assertEqual(code,200)
        self.assertNotIn(SRC.body,body)
        self.assertNotIn('Set-Cookie',headers)
        self.assertIn("default-src 'none'",headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'],'no-store')

    def test_bad_password_does_not_open_evidence(self):
        code,body,headers=self.request('POST','/login',{'password':'bad'})
        self.assertEqual(code,403)
        self.assertNotIn(SRC.body,body)
        self.assertNotIn('Set-Cookie',headers)

    def test_loopback_only_host_and_origin_enforced(self):
        code,_,_=self.request('GET','/review',host='evil.com')
        self.assertEqual(code,400)
        code,_,_=self.request('POST','/login',{'password':PW},origin=False)
        self.assertEqual(code,403)
        code,_,_=self.request('POST','/login',{'password':PW},host='evil.com')
        self.assertEqual(code,403)

    def test_get_query_rejected(self):
        code,_,_=self.request('GET','/review?password=hunter2')
        self.assertEqual(code,400)

    def test_login_cookie_security_properties(self):
        cookie,csrf,digest,headers=self.http_login()
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        self.assertIn('SameSite=Strict',headers['Set-Cookie'])
        self.assertNotIn('signing',headers['Set-Cookie'])
        self.assertIn('sha256:',digest)

    def test_approve_no_cookie_blocked(self):
        _,csrf,digest,_=self.http_login()
        code,_,_=self.request('POST','/approve',{
            'csrf':csrf,'digest':digest,'confirmation':'YES_REVIEWED_EXACT_BATCH'})
        self.assertEqual(code,401)
        self.assertFalse(self.db.snapshot().events)

    def test_approve_csrf_attack_blocked(self):
        cookie,csrf,digest,_=self.http_login()
        code,_,_=self.request('POST','/approve',{
            'csrf':'fake','digest':digest,'confirmation':'YES_REVIEWED_EXACT_BATCH'},cookie=cookie)
        self.assertEqual(code,403)
        self.assertFalse(self.db.snapshot().events)

    def test_approve_wrong_digest_blocked(self):
        cookie,csrf,digest,_=self.http_login()
        code,_,_=self.request('POST','/approve',{
            'csrf':csrf,'digest':'different','confirmation':'YES_REVIEWED_EXACT_BATCH'},cookie=cookie)
        self.assertEqual(code,409)
        self.assertFalse(self.db.snapshot().events)

    def test_duplicate_form_fields_blocked(self):
        cookie,csrf,digest,_=self.http_login()
        body=urlencode([('csrf',csrf),('csrf',csrf),('digest',digest),('confirmation','YES_REVIEWED_EXACT_BATCH')])
        code,_,_=self.request('POST','/approve',body,cookie=cookie)
        self.assertEqual(code,400)

    def test_request_body_size_limited(self):
        code,_,_=self.request('POST','/login','a'*8193)
        self.assertEqual(code,400)

    def test_form_cannot_choose_signing_key(self):
        cookie,csrf,digest,_=self.http_login()
        code,_,_=self.request('POST','/approve',{
            'csrf':csrf,'digest':digest,'confirmation':'YES_REVIEWED_EXACT_BATCH',
            'key_id':'attacker'},cookie=cookie)
        self.assertEqual(code,400)
        self.assertFalse(self.db.snapshot().events)

    def test_http_approve_and_replay_blocked(self):
        cookie,csrf,digest,_=self.http_login()
        fields={'csrf':csrf,'digest':digest,'confirmation':'YES_REVIEWED_EXACT_BATCH'}
        code,body,_=self.request('POST','/approve',fields,cookie=cookie)
        self.assertEqual(code,200)
        self.assertIn('APPROVED',body)
        self.assertEqual(len(self.db.snapshot().events),1)
        code,_,_=self.request('POST','/approve',fields,cookie=cookie)
        self.assertEqual(code,409)

    def test_http_reject_and_logout(self):
        cookie,csrf,digest,_=self.http_login()
        code,body,_=self.request('POST','/reject',{'csrf':csrf,'digest':digest},cookie=cookie)
        self.assertEqual(code,200)
        self.assertIn('REJECTED',body)
        self.assertFalse(self.db.snapshot().events)
        code,_,headers=self.request('POST','/logout',{'csrf':csrf},cookie=cookie)
        self.assertEqual(code,200)
        self.assertIn('Max-Age=0',headers['Set-Cookie'])
        code,_,_=self.request('GET','/review',cookie=cookie)
        self.assertEqual(code,200)
        self.assertNotIn(SRC.body,_)

    def test_unauthenticated_source_not_leaked(self):
        code,body,_=self.request('GET','/review')
        self.assertNotIn(SRC.body,body)
        self.assertNotIn(self.desk.view_digest,body)

if __name__=='__main__': unittest.main()
