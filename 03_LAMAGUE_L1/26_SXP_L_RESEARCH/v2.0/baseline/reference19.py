"""SXP-L v1.9 Natural Reference Forge — narrowly scoped, reversible binders.

The two new bound frames occur ONLY inside a v1.8 clarification candidate.
They do not alter ordinary utterances or any old lexicon entries.
They are not assertions, evidence of actual speech, or permissions.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from repair18 import parse_native as parse18, sha
from runtime.spoken import syllables,lev
from runtime.perspective14 import ALL_OLD,V11_NEW,V12_NEW,V13_NEW,NEW as V14_NEW
from runtime.continuity13 import turn_id
from runtime.sxpl_v03 import SXPError

VERSION='1.9.0'
SOURCE_FRAME='soraviko'  # mi/ti -> original turn's speaker/addressee
CURRENT_FRAME='tumerako' # mi/ti -> current clarification speaker/addressee
NEW=frozenset((SOURCE_FRAME,CURRENT_FRAME))
old=set(ALL_OLD)|set(V11_NEW)|set(V12_NEW)|set(V13_NEW)|set(V14_NEW)|{'kelunaro','remakivo'}
for root in NEW:
    syllables(root)
    if min(lev(root,x) for x in old)<2:raise RuntimeError('root collides with inherited words')
if lev(SOURCE_FRAME,CURRENT_FRAME)<2:raise RuntimeError('new roots too similar')

# The experimental binder can scope ONLY the three atomic transitive predicates
# below, not quotations, belief frames, nested clauses or third-person pronouns.
VERBS={'liva','luma','rava'}
REPAIR_RE=re.compile(r'^mi kelunaro gonape ([a-z]+) dimotu bakumo (soraviko|tumerako) (.+) tesavo devora$')
TURN_RE=re.compile(r'^([a-z]+) > ([a-z]+) : (.+)$')
NAME_RE=re.compile(r'^[a-z]+$')
MAX_DOC=32000

def fail(reason):raise SXPError('E_V19_BINDING',reason)

def actor(tokens: list[str], at: int,declared:list[str]):
    if at>=len(tokens):fail('missing participant role')
    t=tokens[at]
    if t in ('mi','ti'):return t,at+1
    if t=='gonape' and at+2<len(tokens) and tokens[at+2]=='dimotu':
        name=tokens[at+1]
        if name in declared:return name,at+3
    fail('role must be mi, ti, or a declared framed name')

def parse_leaf(inner:str,declared:list[str]):
    """Return two actor roles and one verb. No scope or name inference."""
    tok=inner.split(' ')
    if '' in tok or '\t' in inner:fail('noncanonical space in scoped proposition')
    role1,pos=actor(tok,0,declared)
    if pos>=len(tok) or tok[pos] not in VERBS:fail('restricted binder supports only liva, luma, rava')
    verb=tok[pos];role2,pos=actor(tok,pos+1,declared)
    if tok[pos:]!=['devora']:fail('unsupported nesting/extra words under viewpoint frame')
    return role1,verb,role2

def named(role:str,which:list[str])->str:
    if role=='mi':name=which[0]
    elif role=='ti':name=which[1]
    else:name=role
    return f'gonape {name} dimotu'

def expand19(source:str)->tuple[str,list[dict]]:
    if not isinstance(source,str) or not 0<len(source)<=MAX_DOC:fail('source length limit')
    lines=source.splitlines()
    if lines and lines[-1]=='':lines.pop()
    if len(lines)<2 or not lines[0].startswith('people '):fail('people line required')
    declared=lines[0].split(' ')[1:]
    if not 2<=len(declared)<=16 or len(set(declared))!=len(declared) or not all(NAME_RE.fullmatch(p) for p in declared):fail('invalid people list')
    if len(lines)-1>35:fail('too many turns')
    expanded=[lines[0]]; roles=[]; bindings=[]
    for i,line in enumerate(lines[1:],1):
        m=TURN_RE.fullmatch(line)
        if not m:fail('noncanonical turn line')
        speaker,audience,utterance=m.groups()
        if speaker not in declared or audience not in declared or speaker==audience:fail('invalid participant roles')
        r=REPAIR_RE.fullmatch(utterance)
        if r:
            tid,marker,embedded=r.groups()
            targets=[j for j in range(1,i) if turn_id(j)==tid]
            if len(targets)!=1:fail('unknown/forward reference')
            target=targets[0]
            orig_speaker,orig_audience=roles[target-1]
            if audience!=orig_speaker:fail('clarification must address original speaker')
            subj,verb,obj=parse_leaf(embedded,declared)
            local=(orig_speaker,orig_audience) if marker==SOURCE_FRAME else (speaker,audience)
            expanded_embedded=f'{named(subj,local)} {verb} {named(obj,local)} devora'
            replace=f'mi kelunaro gonape {tid} dimotu bakumo {expanded_embedded} tesavo devora'
            expanded.append(f'{speaker} > {audience} : {replace}')
            bindings.append({'turn':i,'reference_turn':target,'reference_id':tid,
               'frame':marker,'frame_kind':'source_turn' if marker==SOURCE_FRAME else 'current_turn',
               'inner_original':embedded,'inner_expanded':expanded_embedded,
               'bound_mi':local[0],'bound_ti':local[1],
               'proposed_not_asserted':True,'speech_authenticated':False,'authorizes':False})
        else:
            if any(marker in utterance.split() for marker in NEW):fail('viewpoint binder outside clarification')
            expanded.append(line)
        roles.append((speaker,audience))
    return '\n'.join(expanded)+'\n',bindings

def parse_native(source:str)->dict:
    expanded,bindings=expand19(source)
    v18=parse18(expanded)
    # Enforce exact original spelling/spacing for the new source, too.
    canonical=source.rstrip('\n')+'\n'
    if source!=canonical:fail('exact canonical newline required')
    # Restrict expanded-frame agreement with the inherited semantics.
    for frame in bindings:
        derived=v18['meaning18']['turns'][frame['turn']-1]
        if derived['kind']!='clarification_request' or derived['embedded_proposition']!=frame['inner_expanded']:
            fail('inherited parse disagrees with expanded frame')
    meaning={'schema':'SXP-L-reference-1.9','native_sha256':sha(source),
       'expanded_v18_sha256':sha(expanded),
       'legacy_sha256':sha(v18['legacy_sxh']),
       'bindings':bindings,'unverified_speech':True,'authorizes':False,
       'loss_if_expanded_only':'binder choice and authored short words cannot be recovered; keep .sxp19 and sidecar',
       'loss_if_legacy_only':'binder and repair semantics cannot be recovered; keep all artifacts'}
    return {'native':source,'expanded_v18':expanded,'bindings':bindings,'meaning19':meaning,
       'legacy_sxh':v18['legacy_sxh'],'studio17':v18['studio17'],
       'meaning18':v18['meaning18'],'studio17_sidecar':v18['studio17_sidecar']}

def verify_bundle(native, expanded, meaning19, legacy_sxh,meaning18,studio17,sidecar17):
    r=parse_native(native)
    if (r['expanded_v18']!=expanded or r['meaning19']!=meaning19 or r['legacy_sxh']!=legacy_sxh or
        r['meaning18']!=meaning18 or r['studio17']!=studio17 or r['studio17_sidecar']!=sidecar17):
        fail('bundle mismatch, possible tampering or meaning loss')
    return r

def write_bundle(source:str,directory:Path):
    directory=Path(directory)
    r=parse_native(source);directory.mkdir(parents=True,exist_ok=True)
    for fn,value in [('conversation.sxp19',source),('conversation.expanded.sxp18',r['expanded_v18']),
       ('conversation.studio',r['studio17']),('conversation.sxh',r['legacy_sxh'])]:
        (directory/fn).write_text(value,encoding='utf-8')
    for fn,value in [('conversation.sxpl19.json',r['meaning19']),('conversation.sxpl18.json',r['meaning18']),
                     ('conversation.sxpl17.json',r['studio17_sidecar'])]:
        (directory/fn).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    verify_bundle(source,r['expanded_v18'],r['meaning19'],r['legacy_sxh'],r['meaning18'],r['studio17'],r['studio17_sidecar'])
    return r

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('source');p.add_argument('--out',default='reference19_output')
    args=p.parse_args()
    r=write_bundle(Path(args.source).read_text(encoding='utf-8'),Path(args.out))
    print(json.dumps({'bindings':r['bindings'],'authorizes':False},indent=2))
