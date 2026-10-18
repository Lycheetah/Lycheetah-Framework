#!/usr/bin/env python3
"""Audit preservation manifests and optionally run explicitly scoped local tests.

Native Lycheetah integration is NOT executed here; run bridge tests separately
inside an authentic Framework checkout with the package available.
"""
from __future__ import annotations
import argparse, ast, hashlib, re, subprocess, sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
MODULES={
 1:['test_earned_trust_probe'],
 2:['test_binding_contract','test_transactional_provider'],
 3:['test_authenticated_provider'],
 4:['test_independent_witness','test_matched_baseline'],
 5:['test_baseline_consistency','test_provenance_gate'],
 6:['test_baseline_comparison','test_governed_registry'],
 7:['test_dispatch_fence','test_governance_mirror','test_process_challenge_race'],
 8:['test_crashsafe_authority'],
 9:['test_enforced_boundary','test_socket_gateway'],
}
EXPECTED={1:20,2:29,3:50,4:38,5:42,6:59,7:47,8:46,9:47}

def manifests():
 total=0
 for i in range(1,10):
  d=BASE/f'earned_trust_cycle_{i:03d}'
  lines=(d/'SHA256SUMS.txt').read_text().splitlines()
  for line in lines:
   m=re.fullmatch(r'([0-9a-f]{64})\s+\*?(.+)',line)
   if not m: raise RuntimeError(f'cannot parse manifest entry: {line[:80]}')
   sha, rel=m.groups(); f=d/rel.removeprefix('./')
   if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=sha:
    raise RuntimeError(f'missing or changed: {f}')
   total+=1
 print(f'PASS: {total} manifest SHA-256 entries')
 count=0
 for f in BASE.rglob('*.py'):
  if '__pycache__' in f.parts:continue
  ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
  count+=1
 print(f'PASS: {count} Python files parsed')

def tests():
 grand=0
 for i,mods in MODULES.items():
  d=BASE/f'earned_trust_cycle_{i:03d}'
  result=subprocess.run([sys.executable,'-m','unittest','-q',*mods],cwd=d,capture_output=True,text=True)
  output=result.stdout+result.stderr
  found=re.search(r'Ran (\d+) tests? in',output)
  count=int(found.group(1)) if found else 0
  print(f'C{i:03d}: {count} tests '+('PASS' if result.returncode==0 else 'FAIL'),flush=True)
  if result.returncode!=0 or count!=EXPECTED[i]:
   print(output[-4000:]);raise SystemExit(1)
  grand+=count
 print(f'Selected locally-authored suites: {grand} passing tests')
 print('Native Lycheetah class integration: NOT EXECUTED by this command')

if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--tests',action='store_true')
 args=parser.parse_args()
 manifests()
 if args.tests:tests()
