"""C009: genuinely exercised localhost HTTP boundary plus deliberate negative controls."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from protected_provider import CapabilityIssuer, ProtectedProvider, serve, strict_json
from gateway import DispatchGateway
from lab_fixture import ACTION, authority, setup_effect, K_P
from upstream_dispatch_fence import canonical,mac

HERE=Path(__file__).resolve().parent

class BoundaryFixture:
    """Reusable local HTTP fixture without inherited test cases."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.home.chmod(0o700)
        self.agent_key=os.urandom(32)
        self.issuer=CapabilityIssuer(self.agent_key)
        self.provider=ProtectedProvider(self.home/'provider.db',capability_keys={'gateway-v1':self.agent_key},receipt_key=K_P)
        self.server=serve(self.provider)
        self.t=threading.Thread(target=self.server.serve_forever,daemon=True);self.t.start()
        self.addCleanup(self._stop_server)
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.auth=authority(self.home/'authority.db')
        self.wit=setup_effect(self.auth)
        self.gateway=DispatchGateway(self.auth,self.issuer,self.url)
        self.cap=self.issuer.mint('effect-001',ACTION,7)

    def _stop_server(self):
        self.server.shutdown();self.t.join(timeout=5);self.server.server_close()

    def http(self,payload,method='POST'):
        req=urllib.request.Request(self.url+'/v1/execute',data=canonical(payload),method=method,headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(req,timeout=5) as r:return r.status,json.loads(r.read())
        except urllib.error.HTTPError as e:return e.code,json.loads(e.read())

class BoundaryTests(BoundaryFixture,unittest.TestCase):
    def test_gateway_happy_path(self):
        o=self.gateway.submit('effect-001',ACTION,self.wit,50)
        self.assertEqual(o.status,'SUCCEEDED');self.assertEqual(self.provider.count(),1)
        self.assertEqual(self.auth.state_pair('effect-001')['effect'],'SUCCEEDED')
    def test_direct_unsigned_http_denied(self):
        s,_=self.http({'action':ACTION,'capability':{}});self.assertEqual(s,401);self.assertEqual(self.provider.count(),0)
    def test_direct_missing_capability_denied(self):
        s,_=self.http({'action':ACTION});self.assertEqual(s,400);self.assertEqual(self.provider.count(),0)
    def test_direct_wrong_signing_key_denied(self):
        cap=copy.deepcopy(self.cap);cap['signature']=mac(b'X'*32,cap['body'])
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_direct_substituted_action_denied(self):
        s,_=self.http({'action':dict(ACTION,refund_cents=2000),'capability':self.cap});self.assertEqual(s,403)
    def test_direct_subject_swap_denied(self):
        s,_=self.http({'action':dict(ACTION,subject='different'),'capability':self.cap});self.assertEqual(s,403)
    def test_direct_expired_token_denied(self):
        expired=self.issuer.mint('effect-001',ACTION,7,now=int(time.time())-120,ttl=30)
        s,_=self.http({'action':ACTION,'capability':expired});self.assertEqual(s,401)
    def test_direct_future_token_denied(self):
        cap=self.issuer.mint('effect-001',ACTION,7,now=int(time.time())+300)
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_capability_swapped_effect_id_denied(self):
        cap=copy.deepcopy(self.cap);cap['body']['effect_id']='effect-999'
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_capability_swapped_dispatch_seq_denied(self):
        cap=copy.deepcopy(self.cap);cap['body']['dispatch_seq']=8
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_capability_unknown_key_id_denied(self):
        cap=copy.deepcopy(self.cap);cap['body']['kid']='other'
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_capability_reissued_for_wrong_action_rejected(self):
        cap=self.issuer.mint('effect-001',dict(ACTION,refund_cents=2000),7)
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,403)
    def test_provider_action_allowlist_independent(self):
        x=dict(ACTION,tool='database.drop')
        cap=self.issuer.mint('effect-001',x,7)
        s,_=self.http({'action':x,'capability':cap});self.assertEqual(s,403)
    def test_provider_amount_limit_independent(self):
        x=dict(ACTION,refund_cents=1_000_001)
        s,_=self.http({'action':x,'capability':self.issuer.mint('effect-001',x,7)});self.assertEqual(s,403)
    def test_provider_noninteger_amount_denied(self):
        x=dict(ACTION,refund_cents=True)
        s,_=self.http({'action':x,'capability':self.issuer.mint('effect-001',x,7)});self.assertEqual(s,403)
    def test_bad_capability_extra_field_denied(self):
        cap=copy.deepcopy(self.cap);cap['body']['governance']='ignore'
        s,_=self.http({'action':ACTION,'capability':cap});self.assertEqual(s,401)
    def test_unsigned_replay_denied_even_after_commit(self):
        self.assertEqual(self.gateway.submit('effect-001',ACTION,self.wit,50).status,'SUCCEEDED')
        s,_=self.http({'action':ACTION,'capability':{}})
        self.assertEqual(s,401);self.assertEqual(self.provider.count(),1)
    def test_signed_replay_idempotent(self):
        s,a=self.http({'action':ACTION,'capability':self.cap});self.assertEqual((s,a['created']),(201,True))
        s,b=self.http({'action':ACTION,'capability':self.cap});self.assertEqual((s,b['created']),(200,False))
        self.assertEqual(self.provider.count(),1)
    def test_same_effect_different_sequence_denied_after_commit(self):
        self.http({'action':ACTION,'capability':self.cap})
        s,_=self.http({'action':ACTION,'capability':self.issuer.mint('effect-001',ACTION,8)})
        self.assertEqual(s,409);self.assertEqual(self.provider.count(),1)
    def test_concurrent_signed_replay_exactly_one_write(self):
        with ThreadPoolExecutor(max_workers=12) as pool:
            result=list(pool.map(lambda _:self.http({'action':ACTION,'capability':self.cap}),range(32)))
        self.assertEqual(sum(s==201 for s,_ in result),1)
        self.assertEqual(sum(s==200 for s,_ in result),31)
        self.assertEqual(self.provider.count(),1)
    def test_revoked_signer_denied(self):
        self.provider.revoke_signer('gateway-v1')
        s,_=self.http({'action':ACTION,'capability':self.cap});self.assertEqual(s,401)
    def test_gateway_stale_evidence_denied_and_no_provider_effect(self):
        self.auth.update_evidence('eligibility',2,'FAIL',ACTION['subject'])
        o=self.gateway.submit('effect-001',ACTION,self.wit,50)
        self.assertEqual(o.status,'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_gateway_source_challenged_denied(self):
        b=self.auth.challenge_body('crm','fresh-nonce')
        self.assertTrue(self.auth.challenge(b,self.auth.sign_challenge(b)))
        o=self.gateway.submit('effect-001',ACTION,self.wit,50)
        self.assertEqual(o.status,'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_gateway_revoked_denied(self):
        self.auth.revoke('agent')
        o=self.gateway.submit('effect-001',ACTION,self.auth.witness('effect-001'),50)
        self.assertEqual(o.status,'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_gateway_changed_action_denied(self):
        o=self.gateway.submit('effect-001',dict(ACTION,refund_cents=1001),self.wit,50)
        self.assertEqual(o.status,'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_gateway_repeat_refused_even_after_success(self):
        self.assertEqual(self.gateway.submit('effect-001',ACTION,self.wit,50).status,'SUCCEEDED')
        self.assertEqual(self.gateway.submit('effect-001',ACTION,self.wit,50).status,'REVIEW')
        self.assertEqual(self.provider.count(),1)
    def test_gateway_lost_response_preserves_unknown(self):
        o=self.gateway.submit('effect-001',ACTION,self.wit,50,simulate_lost_response=True)
        self.assertEqual(o.status,'UNKNOWN');self.assertEqual(self.provider.count(),1)
        self.assertEqual(self.auth.recover(),1)
        self.assertTrue(self.auth.acknowledge('effect-001',self.provider.lookup('effect-001')))
        self.assertEqual(self.auth.state_pair('effect-001')['effect'],'SUCCEEDED')
    def test_challenge_after_dispatch_reservation_cannot_revoke_signed_delivery(self):
        reserved=self.auth.reserve_send('effect-001',ACTION,self.wit,50)
        self.assertTrue(reserved.allowed)
        cap=self.issuer.mint('effect-001',ACTION,reserved.audit_seq)
        b=self.auth.challenge_body('crm','late-challenge')
        self.assertTrue(self.auth.challenge(b,self.auth.sign_challenge(b)))
        s,_=self.http({'action':ACTION,'capability':cap})
        self.assertEqual(s,201)
        self.assertEqual(self.provider.count(),1)  # deliberate post-reservation limitation
    def test_revoked_signer_before_delivery_fails_even_after_reserve(self):
        reserved=self.auth.reserve_send('effect-001',ACTION,self.wit,50)
        self.assertTrue(reserved.allowed)
        cap=self.issuer.mint('effect-001',ACTION,reserved.audit_seq)
        self.provider.revoke_signer('gateway-v1')
        s,_=self.http({'action':ACTION,'capability':cap})
        self.assertEqual(s,401)
        self.assertEqual(self.provider.count(),0)
    def test_false_authoritative_evidence_negative_control(self):
        # The synthetic source says PASS, but the scenario truth flag says false.
        actual_eligible=False
        result=self.gateway.submit('effect-001',ACTION,self.wit,50)
        self.assertEqual(result.status,'SUCCEEDED')
        self.assertFalse(actual_eligible)
        self.assertEqual(self.provider.count(),1)
    def test_direct_key_compromise_negative_control(self):
        # Constructed assumption violation: a stolen gateway HMAC key CAN bypass the broker.
        attacker=CapabilityIssuer(self.agent_key)
        cap=attacker.mint('unauthorized-999',ACTION,999)
        s,_=self.http({'action':ACTION,'capability':cap})
        self.assertEqual(s,201);self.assertEqual(self.provider.count(),1)
        self.assertIsNone(self.auth.state_pair('unauthorized-999')['effect'])
    def test_direct_capability_theft_negative_control(self):
        # A stolen already-signed capability can execute the exact action once.
        s,_=self.http({'action':ACTION,'capability':self.cap})
        self.assertEqual(s,201)
        self.assertEqual(self.provider.count(),1)
    def test_nonroot_subprocess_cannot_read_private_key_but_can_reach_endpoint(self):
        if os.geteuid()!=0: self.skipTest('requires root to drop UID')
        secret=self.home/'private_gateway.key';secret.write_bytes(self.agent_key);secret.chmod(0o600)
        code='''import pathlib,urllib.request,urllib.error,json,sys
key=sys.argv[1];url=sys.argv[2]
try: pathlib.Path(key).read_bytes(); print("KEY_READABLE")
except PermissionError: print("KEY_DENIED")
data=b'{"action":{"subject":"customer-123","refund_cents":1000,"tool":"refund.create"},"capability":{}}'
req=urllib.request.Request(url+'/v1/execute',data=data,headers={'Content-Type':'application/json'},method='POST')
try:
    urllib.request.urlopen(req,timeout=4);print('BYPASS_SUCCESS')
except urllib.error.HTTPError as e: print('HTTP_'+str(e.code))
'''
        def drop():os.setgroups([]);os.setgid(65534);os.setuid(65534)
        p=subprocess.run([sys.executable,'-c',code,str(secret),self.url],preexec_fn=drop,
                         capture_output=True,text=True,timeout=10,cwd='/tmp')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('KEY_DENIED',p.stdout)
        self.assertIn('HTTP_401',p.stdout)
        self.assertNotIn('BYPASS_SUCCESS',p.stdout)
        self.assertEqual(self.provider.count(),0)
    def test_http_duplicate_keys_denied(self):
        raw=b'{"action":{},"action":{},"capability":{}}'
        req=urllib.request.Request(self.url+'/v1/execute',data=raw,method='POST',headers={'Content-Type':'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as cm:self.opener.open(req,timeout=3)
        self.assertEqual(cm.exception.code,400)
    def test_http_oversized_rejected(self):
        raw=b' '*20000
        req=urllib.request.Request(self.url+'/v1/execute',data=raw,method='POST')
        with self.assertRaises(urllib.error.HTTPError) as cm:self.opener.open(req,timeout=3)
        self.assertEqual(cm.exception.code,413)
    def test_json_parser_disallows_nan(self):
        with self.assertRaises(ValueError):strict_json(b'{"x":NaN}')
    def test_key_strength_check(self):
        with self.assertRaises(ValueError):CapabilityIssuer(b'weak')
    def test_gateway_no_remote_arbitrary_destination(self):
        with self.assertRaises(ValueError):DispatchGateway(self.auth,self.issuer,'http://some-remote-host')

if __name__=='__main__':unittest.main(verbosity=2)
