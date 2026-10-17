"""Trusted root-only, offline, no-retry crash inspector for synthetic Cycle19 runs.
Not a production recovery protocol; uses demo-known filenames and private service keys.
"""
import json,sys,sqlite3,hashlib
from pathlib import Path
from witness17 import validate_records,read_anchor
from authjournal15 import digest

def inspect(base):
    base=Path(base)
    binding=json.loads((base/'binding.json').read_text())
    raw=(base/'journal'/'journal.jsonl').read_bytes()
    key=(base/'keys'/'journal.key').read_bytes()
    anchor_key=(base/'keys'/'witness.key').read_bytes()
    head=validate_records(raw,binding,key)
    checkpoint=read_anchor(base/'state',anchor_key)
    if checkpoint is None:checkpoint_status='MISSING'
    elif checkpoint['plan']!=digest(binding) or checkpoint['nonce']!=binding['grant_nonce']:checkpoint_status='MISMATCH'
    elif checkpoint['count']>head['count']:checkpoint_status='ROLLBACK'
    elif checkpoint['count']==head['count'] and checkpoint['last_hash']==head['last_hash']:checkpoint_status='MATCH'
    else:checkpoint_status='DIVERGENCE_OR_UNANCHORED_TAIL'
    out={}
    for rel,expected in binding['expected'].items():
        p=base/'jail'/'published'/rel
        if p.is_symlink():status='UNSAFE_SYMLINK'
        elif not p.exists():status='ABSENT'
        elif not p.is_file():status='UNSAFE_TYPE'
        else:status='MATCH' if hashlib.sha256(p.read_bytes()).hexdigest()==expected else 'MISMATCH'
        out[rel]=status
    db=base/'nonce_ledger.db'
    if db.exists():
        with sqlite3.connect(f'file:{db}?mode=ro',uri=True) as con:
            row=con.execute('SELECT state FROM executions WHERE nonce=?',(binding['grant_nonce'],)).fetchone()
        ledger=row[0] if row else 'UNRESERVED'
    else:ledger='UNRESERVED'
    if checkpoint_status!='MATCH' or any(v in ('MISMATCH','UNSAFE_SYMLINK','UNSAFE_TYPE') for v in out.values()):state='QUARANTINE'
    elif all(v=='MATCH' for v in out.values()) and head['count']<3:state='PUBLISHED_BUT_FINAL_EVIDENCE_INCOMPLETE'
    elif all(v=='MATCH' for v in out.values()) and head['count']==3 and ledger=='COMPLETED_VERIFIED':state='VERIFIED_PUBLISHED'
    elif all(v=='ABSENT' for v in out.values()):state='NOT_PUBLISHED_OR_NOT_YET_STARTED'
    else:state='PARTIAL_OR_UNCERTAIN'
    return {'state':state,'checkpoint':checkpoint_status,'journal_events':head['count'],
            'published':out,'ledger_state':ledger,'retry_allowed':False,
            'notice':'offline inspector of disposable test; not authority to resume'}
if __name__=='__main__':print(json.dumps(inspect(sys.argv[1]),indent=2))
