"""Independent restricted reader for SXP-L v1.4 viewpoint claims.

Does not import perspective14 or its parser. Supports declarative participants,
plain frame paths and the exact `mi liva ti devora` / `mi liva sivena devora`
leaf templates. Does not pretend to validate full v1.2 grammar.
"""
from __future__ import annotations
import re

TOK=re.compile(r'^[a-z]+(?: [a-z]+)*$')
FRAME_KINDS={'naveriko':'reported_speech','belareko':'belief','nesaluko':'not_know_whether'}

def read(source:str)->list[dict]:
    ls=[x.strip() for x in source.splitlines() if x.strip()]
    if len(ls)>420:raise ValueError('line limit')
    if not all(TOK.fullmatch(x) for x in ls):raise ValueError('lexical form')
    i=0;participants=[]
    def identity(w,start):
        if w[start:start+1]!=['gonape'] or start+2>=len(w) or w[start+2]!='dimotu':
            raise ValueError('framed name expected')
        return w[start+1],start+3
    while i<len(ls) and ls[i].startswith('norava '):
        w=ls[i].split();p,k=identity(w,1)
        if k!=len(w) or p in participants:raise ValueError('declaration')
        participants.append(p);i+=1
    out=[]
    while i<len(ls):
        w=ls[i].split();i+=1
        if w[0]!='taviro':raise ValueError('turn')
        speaker,k=identity(w,1);audience,k=identity(w,k)
        if k!=len(w) or speaker not in participants or audience not in participants:raise ValueError('turn roles')
        anchor=None
        if i<len(ls) and ls[i].startswith('rasufe '):
            w=ls[i].split(); anchor,k=identity(w,1)
            if k!=len(w):raise ValueError('anchor')
            i+=1
        frames=[]
        while i<len(ls) and ls[i].split()[0] in FRAME_KINDS:
            w=ls[i].split();i+=1
            holder,k=identity(w,1);dest,k=identity(w,k)
            if k!=len(w) or holder not in participants or dest not in participants or holder==dest:
                raise ValueError('frame roles')
            frames.append((FRAME_KINDS[w[0]],holder,dest))
        if i+1>=len(ls):raise ValueError('truncated')
        leaf=ls[i];i+=1
        if ls[i]!='tevaro':raise ValueError('close')
        i+=1
        if leaf not in ('mi liva ti devora','mi liva sivena devora'):
            raise ValueError('unsupported leaf subset')
        local=frames[-1][1:3] if frames else (speaker,audience)
        eligible=sorted(set(participants)-set(local))
        if 'sivena' not in leaf:
            status='not_applicable'; chosen=None
        elif anchor is not None:
            if anchor not in eligible:raise ValueError('invalid anchor')
            status='explicit_anchor';chosen=anchor
        elif len(eligible)==1:
            status='unique_candidate';chosen=eligible[0]
        else:
            status='unresolved' if not eligible else 'ambiguous';chosen=None
        out.append({'speaker':speaker,'local_mi':local[0],'local_ti':local[1],
                    'frame_kinds':[f[0] for f in frames], 'reference_status':status,
                    'referent':chosen,'candidates':([anchor] if anchor else eligible) if 'sivena' in leaf else []})
    return out
