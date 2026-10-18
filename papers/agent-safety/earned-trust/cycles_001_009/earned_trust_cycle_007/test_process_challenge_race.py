"""Simultaneous CHALLENGE and CLAIM from separate processes, shared SQLite."""
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from dispatch_fence import Fence
from test_dispatch_fence import KEYS, ACTION, seed


def contender(path, witness, start, out, kind):
    f=Fence(path,**KEYS)
    start.wait(timeout=12)
    if kind=='dispatch':
        r=f.claim('effect-1',ACTION,witness,120)
        out.put({'kind':'dispatch','ok':r.allowed,'reason':r.reason})
    else:
        b=f.challenge_body('origin-crm','race-auditor')
        out.put({'kind':'challenge','ok':f.challenge(b,f.sign_challenge(b))})

class ProcessChallengeRace(unittest.TestCase):
    def test_claim_vs_challenge_linear_order_8_times(self):
        ctx=multiprocessing.get_context('spawn')
        for trial in range(8):
            with tempfile.TemporaryDirectory() as td:
                path=Path(td)/'shared.sqlite';f=Fence(path,**KEYS)
                witness=seed(f);start=ctx.Event();out=ctx.Queue()
                ps=[ctx.Process(target=contender,args=(path,witness,start,out,k)) for k in ('dispatch','challenge')]
                for p in ps:p.start()
                start.set()
                responses=[out.get(timeout=25) for _ in ps]
                for p in ps:
                    p.join(timeout=25)
                    self.assertEqual(p.exitcode,0)
                events=f.audit_events()
                dispatch=[e for e in events if e['kind']=='DISPATCH_CLAIMED']
                challenge=[e for e in events if e['kind']=='CHALLENGE']
                self.assertEqual(len(challenge),1)
                self.assertTrue(f.verify_audit())
                d=next(r for r in responses if r['kind']=='dispatch')
                self.assertEqual(bool(dispatch),d['ok'])
                if d['ok']:
                    self.assertLess(dispatch[0]['seq'],challenge[0]['seq'])
                else:
                    self.assertIn(d['reason'],{'stale-governance','source-challenged'})

if __name__=='__main__':unittest.main()
