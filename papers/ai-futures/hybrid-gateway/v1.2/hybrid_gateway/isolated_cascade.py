"""One-way, out-of-process CASCADE diagnostic integration v0.8.

Separates gateway object from optional external CASCADE code; offers an explicit
blob identity pin, bounded packet size and timeout. Not a sandbox (child can
access same OS/file resources), not calibrated truth measurement, and not
permission to update the ledger. No in-process model-supplied code callbacks.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import math
import subprocess
import sys
from typing import Mapping
from .canonical_loader import PINNED_GIT_BLOB_SHA1
from .cascade_bridge import EvidenceWeights, gateway_snapshot_digest
from .core import HybridGateway

WORKER=Path(__file__).with_name('_cascade_worker.py').resolve()
MAX_PACKET_BYTES=1024*128


@dataclass(frozen=True)
class IsolatedDiagnostic:
    query_disposition: str
    claim_ids: tuple[str,...]
    event_count: int
    diagnostic_coherence: float | None
    canonical_blob_sha: str
    boundary: str='subprocess, NOT sandbox; advisory diagnostic only'


def diagnose_isolated(gateway: HybridGateway, *, tenant: str, subject: str,
                     predicate: str, scope: str, effective_at: str, known_at: str,
                     calibrated_weights: Mapping[str,EvidenceWeights],
                     framework_root: str|Path,
                     expected_blob_sha: str=PINNED_GIT_BLOB_SHA1,
                     timeout_seconds: float=6.0) -> IsolatedDiagnostic:
    if (not isinstance(expected_blob_sha,str) or len(expected_blob_sha)!=40
            or any(ch not in '0123456789abcdef' for ch in expected_blob_sha)):
        raise ValueError('expected Git blob SHA-1 must be explicitly pinned')
    if (not isinstance(timeout_seconds,(int,float)) or isinstance(timeout_seconds,bool)
            or not math.isfinite(timeout_seconds) or not .1<=timeout_seconds<=30):
        raise ValueError('invalid worker timeout')
    before_head=gateway.head_digest
    before=gateway_snapshot_digest(gateway)
    result=gateway.query(tenant=tenant,subject=subject,predicate=predicate,
                         scope=scope,effective_at=effective_at,known_at=known_at)
    rows=[]
    for ref in result.citations:
        cid=ref['claim_id']
        if cid not in calibrated_weights:
            raise ValueError('missing calibrated weights for '+cid)
        w=calibrated_weights[cid]
        if not isinstance(w,EvidenceWeights):
            raise TypeError('weights must be validated EvidenceWeights')
        claim=gateway.claims[cid]
        rows.append({'claim_id':cid,'value':claim.value,
                     'namespace':[tenant,subject,predicate,scope],
                     'weights':asdict(w)})
    # Source quotes, URIs, document contents, tokens and agent state are never sent.
    packet={'framework_root':str(Path(framework_root).expanduser().resolve()),
            'expected_blob_sha':expected_blob_sha,'claims':rows}
    content=json.dumps(packet,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    if len(content.encode('utf8'))>MAX_PACKET_BYTES:
        raise ValueError('CASCADE packet too large')
    try:
        # Isolated interpreter; no PYTHONPATH, no inherited stdin, no shell.
        run=subprocess.run([sys.executable,'-I','-B',str(WORKER)],input=content,
               capture_output=True,text=True,timeout=timeout_seconds,check=False)
    except subprocess.TimeoutExpired as e:
        raise TimeoutError('isolated CASCADE diagnostic timeout') from None
    if run.returncode!=0:
        raise RuntimeError('isolated CASCADE diagnostic failed (pin, import or execution)')
    try:
        response=json.loads(run.stdout)
        assert isinstance(response,dict)
        assert response['git_blob_sha']==expected_blob_sha
        assert response['claim_ids']==[x['claim_id'] for x in rows]
        events=response['event_count']
        assert type(events)==int and events>=0
        coherence=response['coherence']
        assert coherence is None or (type(coherence) in (float,int) and math.isfinite(coherence) and 0<=coherence<=1)
        assert (coherence is None)==(not rows)
    except (KeyError,ValueError,AssertionError,TypeError) as e:
        raise RuntimeError('invalid isolated CASCADE response') from None
    if gateway.head_digest!=before_head or gateway_snapshot_digest(gateway)!=before:
        raise RuntimeError('ledger changed during isolated diagnostic')
    return IsolatedDiagnostic(result.disposition,tuple(x['claim_id'] for x in rows),
                              events,coherence,expected_blob_sha)
