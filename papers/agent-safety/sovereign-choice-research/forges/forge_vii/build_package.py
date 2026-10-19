from __future__ import annotations
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'LYCHEETAH_SOVEREIGN_CHOICE_FORGE_VII_COMPLETE_v0.1.zip'
SKIP={'MANIFEST_SHA256.json','results/verification.json'}
paths=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
    rel=p.relative_to(ROOT).as_posix()
    paths.append((rel,p))
paths.sort()
manifest={rel:hashlib.sha256(p.read_bytes()).hexdigest() for rel,p in paths if rel not in SKIP}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
paths=[(p.relative_to(ROOT).as_posix(),p) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
paths.sort()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for rel,p in paths:z.write(p,arcname='sovereign_choice_forge_vii/'+rel)
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    if bad:raise ValueError(f'zip corruption: {bad}')
print(json.dumps({'path':str(OUT),'size_bytes':OUT.stat().st_size,'files':len(paths),
                  'manifest_entries':len(manifest),'lineage_bytes':(ROOT/'lineage/FORGE_VI_COMPLETE.zip').stat().st_size},indent=2))
