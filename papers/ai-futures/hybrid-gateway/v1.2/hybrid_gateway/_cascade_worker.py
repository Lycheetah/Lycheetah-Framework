"""Explicit, opt-in subprocess CASCADE runner. Not an OS sandbox.

No gateway object is imported or passed here. Reads one small JSON packet,
verifies operator-pinned file bytes *before* executing that external code,
then serializes a minimal diagnostic result. Never writes an admission event.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys


def git_blob_sha(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def main():
    packet = json.loads(sys.stdin.read())
    root = Path(packet['framework_root']).resolve()
    rel = Path('12_IMPLEMENTATIONS/core/cascade_engine.py')
    path = root / rel
    raw = path.read_bytes()
    if git_blob_sha(raw) != packet['expected_blob_sha']:
        raise ValueError('PIN_MISMATCH')
    # The operator, NOT the model, chooses the path and hash.
    spec=importlib.util.spec_from_file_location('_isolated_canonical_cascade',path)
    if spec is None or spec.loader is None:
        raise ImportError('MODULE_NOT_AVAILABLE')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    eng=mod.CascadeEngine()
    for claim in packet['claims']:
        w=claim['weights']
        namespace=json.dumps(claim['namespace'],separators=(',',':'))
        block=mod.KnowledgeBlock(id=claim['claim_id'], content=claim['value'],
                    domain=namespace, paradigm=claim['value'],
                    evidence_strength=w['evidence_strength'],
                    explanatory_power=w['explanatory_power'],uncertainty=w['uncertainty'])
        eng.add_block(block)
    coherence=float(eng.coherence()) if packet['claims'] else None
    if coherence is not None and (not math.isfinite(coherence) or not (0<=coherence<=1)):
        raise ValueError('INVALID_DIAGNOSTIC')
    result={'event_count':len(eng.cascade_events), 'coherence':coherence,
            'claim_ids':[c['claim_id'] for c in packet['claims']],
            'git_blob_sha':git_blob_sha(raw)}
    sys.stdout.write(json.dumps(result,sort_keys=True,allow_nan=False))


if __name__=='__main__':
    try: main()
    except BaseException:
        # Do not reflect local path, packet, values, quote or provider secrets.
        sys.stderr.write('CASCADE_WORKER_FAILED\n')
        sys.exit(2)
