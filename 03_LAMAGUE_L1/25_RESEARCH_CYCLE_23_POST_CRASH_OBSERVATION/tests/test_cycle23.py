import os,sys,tempfile,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from cycle23 import *
class Cycle23Tests(unittest.TestCase):
 def test_crash(self):
  with tempfile.TemporaryDirectory() as d:
   r=experiment(Path(d)/'case');self.assertEqual(sorted(r['observations'].values()),['ABSENT','MATCH']);self.assertEqual(r['check'],'MATCH');self.assertFalse(r['auto_retry'])
 def test_normal(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(list(experiment(Path(d)/'case',None)['observations'].values()),['MATCH','MATCH'])
 def setup_case(self,d):
  b=Path(d);(b/'case').mkdir();j,data,p,g,k=create_case(b/'case');binding=build_binding(p,g);ed=b/'e';ed.mkdir();st=b/'state';st.mkdir();return j,p,g,k,binding,ed/'events.jsonl',st,os.urandom(32),os.urandom(32)
 def test_unapproved(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d)
   with self.assertRaises(EvidenceError):observe_and_append(path,jk,b,j/'published','unapproved.txt')
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d);rel=next(iter(b['expected']));observe_and_append(path,jk,b,j/'published',rel)
   contents=path.read_text().replace('ABSENT','MATCH');path.write_text(contents)
   with self.assertRaises(EvidenceError):read_events(path,jk,b)
 def test_grant_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d);observe_and_append(path,jk,b,j/'published',next(iter(b['expected'])));g['signature_ed25519_b64']='AAAA'
   with self.assertRaises(Refusal):witness_action(path,b,p,g,k,jk,st,wk)
 def test_rollback(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d);rels=list(b['expected']);observe_and_append(path,jk,b,j/'published',rels[0]);prefix=path.read_bytes();observe_and_append(path,jk,b,j/'published',rels[1]);self.assertEqual(witness_action(path,b,p,g,k,jk,st,wk),'ANCHORED');path.write_bytes(prefix);self.assertEqual(witness_action(path,b,p,g,k,jk,st,wk,'CHECK'),'ROLLBACK_DETECTED')
 def test_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d);rel=next(iter(b['expected']));observe_and_append(path,jk,b,j/'published',rel)
   with self.assertRaises(EvidenceError):observe_and_append(path,jk,b,j/'published',rel)
 def test_truncated(self):
  with tempfile.TemporaryDirectory() as d:
   j,p,g,k,b,path,st,jk,wk=self.setup_case(d);observe_and_append(path,jk,b,j/'published',next(iter(b['expected'])));path.write_bytes(path.read_bytes()[:-1])
   with self.assertRaises(EvidenceError):read_events(path,jk,b)
if __name__=='__main__':unittest.main()
