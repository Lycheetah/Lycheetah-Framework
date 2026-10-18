from __future__ import annotations
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from agent_gateway import AgentGatewayServer
from test_enforced_boundary import BoundaryFixture
from lab_fixture import ACTION
from upstream_dispatch_fence import canonical


class UnixGatewayTests(BoundaryFixture,unittest.TestCase):
    # Reuses HTTP fixture so socket+provider are composed in each test.
    def setUp(self):
        super().setUp()
        if not hasattr(socket,'SO_PEERCRED'): self.skipTest('Linux SO_PEERCRED required')
        self.sockdir=Path(tempfile.mkdtemp(prefix='earned-trust-uds-'))
        self.sockdir.chmod(0o711)
        self.addCleanup(lambda: self.sockdir.rmdir())
        self.sockpath=str(self.sockdir/'agent.sock')
        self.sockserv=AgentGatewayServer(self.sockpath,self.gateway,{65534:'agent'},clock=50)
        self.sockthread=threading.Thread(target=self.sockserv.serve_forever,daemon=True)
        self.sockthread.start()
        self.addCleanup(self._stop_sock)

    def _stop_sock(self):
        self.sockserv.shutdown();self.sockthread.join(timeout=5);self.sockserv.server_close()

    def request(self,body,*,drop_uid=False):
        code='''import json,socket,sys
s=socket.socket(socket.AF_UNIX);s.settimeout(10);s.connect(sys.argv[1]);s.sendall(sys.argv[2].encode()+b'\\n');data=b''
while not data.endswith(b'\\n'):
    chunk=s.recv(2048)
    if not chunk:break
    data+=chunk
print(data.decode().strip())
'''
        if drop_uid and os.geteuid()!=0:self.skipTest('UID drop requires root')
        def drop():os.setgroups([]);os.setgid(65534);os.setuid(65534)
        p=subprocess.run([sys.executable,'-c',code,self.sockpath,json.dumps(body)],
                         preexec_fn=drop if drop_uid else None,cwd='/tmp',text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        return json.loads(p.stdout)

    def test_unrecognized_root_peer_denied(self):
        self.assertEqual(self.request({'effect_id':'effect-001','action':ACTION})['code'],403)
        self.assertEqual(self.provider.count(),0)
    def test_nobody_peer_authorized_effect_runs(self):
        a=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        self.assertEqual(a['status'],'SUCCEEDED');self.assertEqual(self.provider.count(),1)
    def test_nobody_cannot_dispatch_unknown_effect(self):
        a=self.request({'effect_id':'effect-unknown','action':ACTION},drop_uid=True)
        self.assertEqual(a['code'],404);self.assertEqual(self.provider.count(),0)
    def test_nobody_cannot_dispatch_changed_action(self):
        a=self.request({'effect_id':'effect-001','action':dict(ACTION,refund_cents=2020)},drop_uid=True)
        self.assertEqual(a['status'],'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_nobody_cannot_claim_identity_in_body(self):
        a=self.request({'effect_id':'effect-001','action':ACTION,'actor':'agent'},drop_uid=True)
        self.assertEqual(a['code'],400);self.assertEqual(self.provider.count(),0)
    def test_nobody_challenged_source_pauses(self):
        b=self.auth.challenge_body('crm','test-challenge')
        self.assertTrue(self.auth.challenge(b,self.auth.sign_challenge(b)))
        a=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        self.assertEqual(a['status'],'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_nobody_revoked_actor_pauses(self):
        self.auth.revoke('agent')
        a=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        self.assertEqual(a['status'],'REVIEW');self.assertEqual(self.provider.count(),0)
    def test_nobody_uid_mapped_to_wrong_actor_denied(self):
        self.sockserv.uid_actors[65534]='unapproved-principal'
        a=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        self.assertEqual(a['code'],403)
        self.assertEqual(self.provider.count(),0)
    def test_nobody_repeat_request_does_not_duplicate(self):
        a=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        b=self.request({'effect_id':'effect-001','action':ACTION},drop_uid=True)
        self.assertEqual(a['status'],'SUCCEEDED');self.assertEqual(b['code'],409)
        self.assertEqual(self.provider.count(),1)

if __name__=='__main__':unittest.main(verbosity=2)
