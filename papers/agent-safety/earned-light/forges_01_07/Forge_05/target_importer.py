"""Provider B: independent, read-only importer/runner. Standard library only.
This script is invoked by the test harness in a fresh subprocess and consumes
only the exported directory; it is NOT a security sandbox.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

FILE_NAMES=('documents.json','policies.json','decisions.json','dependencies.json','state.json')

def load(folder):
    folder=Path(folder)
    data={}
    for filename in FILE_NAMES:
        raw=(folder/filename).read_bytes()
        if len(raw)>1024*1024:
            raise ValueError('Excessive input size')
        data[filename.split('.')[0]]=json.loads(raw.decode('utf-8'))
    for section in ('documents','policies','decisions','dependencies'):
        if not isinstance(data[section],list):
            raise ValueError('Expected list: '+section)
        ids=[entry['id'] for entry in data[section]]
        if len(ids)!=len(set(ids)) or any(not isinstance(i,str) for i in ids):
            raise ValueError('Duplicate or invalid IDs: '+section)
    if data['state'].get('format')!='earned-light-exit-v1':
        raise ValueError('Unknown format')
    return data

def run(data):
    docs={d['id']:d for d in data['documents']}
    policies={p['topic']:p for p in data['policies']}
    answers={}
    for topic in ('hours','booking','pricing','refund','allergy'):
        p=policies.get(topic)
        d=docs.get(p['doc_id']) if p else None
        if not p or not d or p.get('mode') not in ('answer','escalate'):
            answers[topic]={'status':'unavailable'}
            continue
        answers[topic]={'status':p['mode'],'answer':d.get('body'), 'policy_id':p.get('id'),'source_id':d.get('id'),'source_origin':d.get('origin')}
    cases={c['id']:{k:c.get(k) for k in ('id','policy_id','note','reviewed_by','receipt_ref')} for c in data['decisions']}
    return {'revision':data['state']['revision'],'queries':answers,'case_history':cases,'dependencies':data['dependencies']}

def main(argv):
    if len(argv)!=2:raise SystemExit('usage: python -I target_importer.py BUNDLE_PATH')
    try:
        data=load(argv[1]); out={'ok':True,'output':run(data)}
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        out={'ok':False,'error':type(exc).__name__+': '+str(exc)}
    print(json.dumps(out,sort_keys=True,ensure_ascii=False))
    return 0 if out['ok'] else 1
if __name__=='__main__':raise SystemExit(main(sys.argv))
