"""Build SHA-256 manifest then archive, excluding dynamic verification report."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
skip={'MANIFEST_SHA256.json','results/verification.json','build_package.py'}
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    name=str(p.relative_to(root))
    if name in skip or '__pycache__' in p.parts or name.endswith('.pyc') or name.startswith('results/chromium'):
        continue
    files.append((name,p))
files.sort()
manifest={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in files}
(root/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Manifest:',len(manifest),'files')
