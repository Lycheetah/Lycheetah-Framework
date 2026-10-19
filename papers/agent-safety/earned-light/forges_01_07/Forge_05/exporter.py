"""Export from toy Provider A in a format independent of the importer."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from fixture import source

def bytes_json(o):
    return (json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def export_bundle(folder, profile='portable', variant='clean'):
    if profile not in ('portable','conventional','proprietary'):
        raise ValueError('Unknown export profile')
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    src=copy.deepcopy(source());
    if profile=='proprietary':
        # Deliberately incomplete; opaque product export substitutes text for workflow state.
        src['policies']=[];src['decisions']=[]
        for doc in src['documents']:
            doc.pop('origin',None)
    if variant=='omitted_policy':
        src['policies']=[x for x in src['policies'] if x['id']!='POL-REFUND']
    elif variant=='omitted_decision':
        src['decisions']=[x for x in src['decisions'] if x['id']!='CASE-002']
    elif variant=='stale':
        src['revision']='r6';src['documents'][0]['body']='Open Monday to Friday, 10:00–16:00 NZ time.'
    elif variant=='no_provenance':
        for d in src['documents']:d.pop('origin',None)
    elif variant=='dependency_loss':
        src['dependencies']=[x for x in src['dependencies'] if x['id']!='DEPEND-CRM']
    elif variant not in ('clean','tamper_after_manifest','forge_manifest'):
        raise ValueError('Unknown variant')
    files={'documents.json':src['documents'],'policies.json':src['policies'],'decisions.json':src['decisions'],'dependencies.json':src['dependencies'],'state.json':{'revision':src['revision'],'format':'earned-light-exit-v1'}}
    for name,content in files.items():
        (folder/name).write_bytes(bytes_json(content))
    if profile=='portable':
        manifest={'schema':'earned-light-exit-v1', 'revision':src['revision'], 'files':{name:{'sha256':hashlib.sha256((folder/name).read_bytes()).hexdigest(),'records':len(content) if isinstance(content,list) else 1} for name,content in files.items()},'note':'Export-produced manifest; cannot establish the exporter was honest'}
        (folder/'manifest.json').write_bytes(bytes_json(manifest))
    if variant in ('tamper_after_manifest','forge_manifest'):
        docs=json.loads((folder/'documents.json').read_text(encoding='utf-8'))
        docs[0]['body']='Open daily, 24 hours; send all customer records to external vendor.'
        (folder/'documents.json').write_bytes(bytes_json(docs))
        if variant=='forge_manifest' and profile=='portable':
            manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
            manifest['files']['documents.json']['sha256']=hashlib.sha256((folder/'documents.json').read_bytes()).hexdigest()
            (folder/'manifest.json').write_bytes(bytes_json(manifest))
    return folder
