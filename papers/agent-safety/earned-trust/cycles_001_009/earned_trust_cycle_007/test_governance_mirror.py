"""Boundary experiment: Cycle-006 in-memory registry vs Cycle-007 durable dispatch.

Proves a *gap*, not atomic integration. If a trusted registrar applies a
challenge but fails before mirroring it into the dispatch ledger, the latter
can permit a locally valid claim. No live external systems involved.
"""
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent/'upstream_cycle_006'))
from governed_registry import GovernedRegistry, Authority
from provenance_gate import Source
from dispatch_fence import Fence
from test_dispatch_fence import KEYS, ACTION, seed


def registry():
    sources=[Source('origin-crm','crm-org'),Source('witness-1','one-org',('origin-crm',),True),
             Source('witness-2','two-org',('origin-crm',),True)]
    keys={'witness-1':b'1'*32,'witness-2':b'2'*32}
    authorities=[Authority('r1','north-org','REVIEWER',b'1'*32),
                 Authority('r2','south-org','REVIEWER',b'2'*32),
                 Authority('aud','audit-org','AUDITOR',b'3'*32)]
    return GovernedRegistry(sources,keys,authorities)


def source_challenge(reg):
    op=reg.prepare('CHALLENGE','origin-crm',reason='CRM ancestry may be incomplete')
    reg.apply(op,[reg.sign(op,'aud')])
    valid, reason=reg.verify_history(trusted_checkpoint=reg.checkpoint())
    assert valid,(valid,reason)
    return reg.events[-1]


def mirror_verified_challenge(reg, f):
    """Trusted application relay, deliberately NOT a distributed transaction."""
    is_valid,_=reg.verify_history(trusted_checkpoint=reg.checkpoint())
    if not is_valid:return False
    entry=reg.events[-1]
    op=entry['operation']
    if op['kind']!='CHALLENGE':return False
    body=f.challenge_body(op['target'],entry['hash'])
    return f.challenge(body,f.sign_challenge(body))

class MirrorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f=Fence(Path(self.temp.name)/'dispatch.sqlite',**KEYS)
        self.w=seed(self.f)
        self.reg=registry()

    def test_unmirrored_challenge_is_an_actual_gap(self):
        source_challenge(self.reg)
        # Both systems are internally consistent. They do NOT share an atomic
        # transaction, so the dispatch ledger has not learned about challenge.
        self.assertTrue(self.reg.verify_history(trusted_checkpoint=self.reg.checkpoint())[0])
        self.assertTrue(self.f.verify_audit())
        self.assertTrue(self.f.claim('effect-1',ACTION,self.w,120).allowed)

    def test_relayed_challenge_prevents_cached_claim(self):
        source_challenge(self.reg)
        self.assertTrue(mirror_verified_challenge(self.reg,self.f))
        self.assertEqual(self.f.claim('effect-1',ACTION,self.w,120).reason,'stale-governance')

    def test_refreshed_witness_still_frozen_after_relay(self):
        source_challenge(self.reg)
        mirror_verified_challenge(self.reg,self.f)
        self.assertEqual(self.f.claim('effect-1',ACTION,self.f.witness('effect-1'),120).reason,'source-challenged')

    def test_duplicate_relay_rejected(self):
        source_challenge(self.reg)
        self.assertTrue(mirror_verified_challenge(self.reg,self.f))
        self.assertFalse(mirror_verified_challenge(self.reg,self.f))

if __name__=='__main__':unittest.main()
