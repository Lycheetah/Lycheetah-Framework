"""Check unified-diff structure against source context embedded in the patch.

This creates a sparse synthetic checkout from each hunk's original-side lines.
Passing means the patch is structurally valid against those contexts, not that a
full upstream checkout or test suite was exercised.
"""
from __future__ import annotations
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PATCH=ROOT/"strict_assurance_wire_types_v1_3.patch"

def git(cwd,*args):
 return subprocess.run(["git",*args],cwd=cwd,text=True,capture_output=True,check=False)

def main():
 patch_lines=PATCH.read_text(encoding="utf-8").splitlines()
 files={}
 current=None
 i=0
 while i<len(patch_lines):
  line=patch_lines[i]
  if line.startswith("diff --git "):
   m=re.match(r"diff --git a/(.+) b/(.+)",line)
   current=m.group(2); files.setdefault(current,{})
   i+=1; continue
  m=re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@",line)
  if m and current:
   old_start=int(m.group(1)); h=[]; i+=1
   while i<len(patch_lines) and not patch_lines[i].startswith("@@ ") and not patch_lines[i].startswith("diff --git "):
    h.append(patch_lines[i]); i+=1
   pos=old_start-1
   for x in h:
    if x.startswith(" ") or x.startswith("-"):
     if len(x)==0: raise AssertionError("empty diff line is invalid")
     raw=x[1:]
     existing=files[current].get(pos)
     if existing is not None and existing!=raw:
      raise AssertionError(f"overlapping synthetic source context in {current}:{pos+1}")
     files[current][pos]=raw; pos+=1
   continue
  i+=1
 temp=Path(tempfile.mkdtemp(prefix="lycheetah-wire-patch-context-"))
 try:
  for rel, indexed in files.items():
   path=temp/rel; path.parent.mkdir(parents=True,exist_ok=True)
   maxline=max(indexed) if indexed else 0
   lines=["# omitted upstream context in synthetic patch preflight"]*(maxline+1)
   for idx,value in indexed.items(): lines[idx]=value
   path.write_text("\n".join(lines)+"\n",encoding="utf-8")
  init=git(temp,"init","-q")
  if init.returncode: raise RuntimeError(init.stderr)
  add=git(temp,"add",".")
  if add.returncode: raise RuntimeError(add.stderr)
  commit=git(temp,"-c","user.name=WirePatchFixture","-c","user.email=wire-fixture@example.invalid","commit","-qm","synthetic source contexts")
  if commit.returncode: raise RuntimeError(commit.stderr)
  check=git(temp,"apply","--check",str(PATCH))
  if check.returncode:
   print("FAIL: patch did not apply to the synthetic hunk context")
   print(check.stderr)
   for rel in sorted(files):
    if rel.endswith("models.py"):
     print("Synthetic models.py relevant preimage:")
     for n, value in enumerate((temp/rel).read_text(encoding="utf-8").splitlines(),1):
      if 114 <= n <= 127: print(f"{n:4}: {value!r}")
   print("scratch removed after diagnostics")
   return 1
  apply=git(temp,"apply",str(PATCH))
  if apply.returncode:
   print("FAIL: patch apply failed after successful check")
   print(apply.stderr)
   return 1
  changed=git(temp,"diff","--stat")
  result={"status":"PASS_SYNTHETIC_PATCH_CONTEXT_ONLY","target_files":sorted(files),"changed":changed.stdout.strip(),"warning":"Not a full upstream checkout; no package tests run."}
  print(__import__("json").dumps(result,indent=2))
  (ROOT/"patch_context_check_v1_3.json").write_text(__import__("json").dumps(result,indent=2)+"\n",encoding="utf-8")
  return 0
 finally:
  shutil.rmtree(temp,ignore_errors=True)

if __name__=="__main__":
 raise SystemExit(main())
