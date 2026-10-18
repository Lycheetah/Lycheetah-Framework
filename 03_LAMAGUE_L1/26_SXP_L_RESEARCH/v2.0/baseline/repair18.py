"""SXP-L v1.8 bounded *pronounceable repair utterance* parser.

Use language-native repair speech acts in conversation authoring. The outer 'people'
header and speaker notation remain tooling metadata, NOT spoken language. Inert.

External v1.7 legacy transcript remains unchanged. The original native source
must be kept with the legacy and sidecar because legacy alone loses repair kind.
This software does not authenticate speakers or grant permissions.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from runtime.studio17 import parse_studio, verify_pair
from runtime.continuity13 import turn_id
from runtime.spoken import syllables, lev
from runtime.perspective14 import ALL_OLD, V11_NEW, V12_NEW, V13_NEW, NEW as V14_NEW
from runtime.sxpl_v03 import SXPError

VERSION='1.8.0'
ROOT_CLARIFY='kelunaro'
ROOT_CORRECT='remakivo'
ROOT_TO_KIND={ROOT_CLARIFY:'clarification_request', ROOT_CORRECT:'self_correction'}
NEW_ROOTS=frozenset(ROOT_TO_KIND)
# Runtime modules internally use absolute local imports, so this module is
# launched through run_v18.py or with PYTHONPATH=runtime:.
# Runtime prior-art phonological screen, not an acoustic perception test.
for word in NEW_ROOTS:
    syllables(word)
    if min(lev(word, old) for old in ALL_OLD|V11_NEW|V12_NEW|V13_NEW|V14_NEW)<=1:
        raise RuntimeError('v1.8 root spelling collision')
if lev(ROOT_CLARIFY, ROOT_CORRECT)<=1:
    raise RuntimeError('new roots collide')

MAX_CHARS=32000
MAX_TURNS=35
MAX_PEOPLE=16
PERSON_RE=r'[a-z]+'
LINE_RE=re.compile(r'^([a-z]+) > ([a-z]+) : (.+)$')
REPAIR_RE=re.compile(r'^mi (kelunaro|remakivo) gonape ([a-z]+) dimotu bakumo (.+) tesavo devora$')
END=' devora'

def bad(message): raise SXPError('E_V18_REPAIR', message)

def sha(text:str)->str: return hashlib.sha256(text.encode('utf-8')).hexdigest()

def to_studio(source:str)->tuple[str,list[dict]]:
    """Compile only grammar-defined repair frames, fail closed on noncanonical text."""
    if not isinstance(source,str) or not (0<len(source)<=MAX_CHARS): bad('bounded UTF-8 source required')
    lines=[line.strip() for line in source.splitlines() if line.strip()]
    if len(lines)<2 or len(lines)>MAX_TURNS+1:bad('declared participants and 1-35 turns required')
    header=lines[0]
    declared=header.split()
    if declared[0]!='people' or not (2<=len(declared)-1<=MAX_PEOPLE):bad('people declaration required')
    declared=declared[1:]
    if len(set(declared))!=len(declared):bad('duplicate participants')
    out=['people '+' '.join(declared)]
    relations=[]
    previous_roles=[]
    for idx,line in enumerate(lines[1:],1):
        m=LINE_RE.fullmatch(line)
        if not m:bad(f'noncanonical turn {idx}, use speaker > addressee : utterance')
        speaker,audience,utterance=m.groups()
        if speaker not in declared or audience not in declared or speaker==audience:bad('undeclared or identical roles')
        if not utterance.endswith(END):bad('every sentence requires spoken terminal devora')
        if '  ' in utterance or '\t' in utterance:bad('noncanonical spacing')
        r=REPAIR_RE.fullmatch(utterance)
        if r:
            root,ref,inner=r.groups()
            kind=ROOT_TO_KIND[root]
            if not inner.endswith(END):bad('nested proposition requires terminal devora')
            bare=inner[:-len(END)]
            if not bare:bad('empty embedded proposition')
            eligible=[k for k in range(1,idx) if turn_id(k)==ref]
            if len(eligible)!=1:bad(f'unknown, non-prior or malformed reference in turn {idx}')
            target=eligible[0]
            old_speaker,old_audience=previous_roles[target-1]
            if kind=='clarification_request':
                if audience!=old_speaker:
                    bad('clarification must address the speaker whose turn is being clarified')
                if any(t in {'mi','ti'} for t in bare.split()):
                    bad('clarification candidate must name people explicitly; no viewpoint-shifting mi/ti')
            if kind=='self_correction' and audience!=old_audience:
                bad('self-correction must retain original addressee so ti remains stable')
            symbol='?' if kind=='clarification_request' else '~'
            out.append(f'{speaker} > {audience} {symbol}{target} : {bare}')
            relations.append({'turn':idx,'kind':kind,'root':root,'target_index':target,'target_id':ref,
                              'embedded_proposition':inner,'speech_act_status':'speaker_claim_unverified',
                              'embedded_is_asserted':kind=='self_correction'})
        else:
            if ROOT_CLARIFY in utterance.split() or ROOT_CORRECT in utterance.split():
                bad('malformed repair root; no silent plain-expression fallback')
            out.append(f'{speaker} > {audience} : {utterance}')
            relations.append({'turn':idx,'kind':'ordinary_utterance',
                              'speech_act_status':'speaker_claim_unverified'})
        previous_roles.append((speaker,audience))
    return '\n'.join(out)+'\n',relations

def render_native(people:list[str], meta:list[dict])->str:
    lines=['people '+' '.join(people)]
    for m in meta:
        if m['kind']=='ordinary_utterance':
            utterance=m['utterance']
        else:
            utterance=(f'mi {m["root"]} gonape {m["target_id"]} dimotu '
                       f'bakumo {m["embedded_proposition"]} tesavo devora')
        lines.append(f'{m["speaker"]} > {m["audience"]} : {utterance}')
    return '\n'.join(lines)+'\n'

def parse_native(source:str)->dict:
    studio,acts=to_studio(source)
    old=parse_studio(studio)
    participants=old['participants']
    meta=[]
    for inherited,act in zip(old['sidecar']['turns'],acts):
        if act['kind']!='ordinary_utterance':
            if inherited['link'] is None or inherited['link']['kind']!=act['kind']:
                bad('inherited semantics mismatch')
            if inherited['link']['target_id']!=act['target_id']:bad('inherited turn reference mismatch')
            if inherited['leaf']+' devora'!=act['embedded_proposition']:
                bad('embedded utterance mismatch')
        else:
            if inherited['link'] is not None:bad('ordinary utterance must not be linked')
        meta.append({'speaker':inherited['speaker'],'audience':inherited['audience'],
                     'utterance':inherited['leaf']+' devora',**act})
    canonical=render_native(participants,meta)
    if source.rstrip('\n')!=canonical.rstrip('\n'):
        bad('noncanonical native source; use normalized single-space format')
    identity={
        'schema':'SXP-L-repair-1.8','native_sha256':sha(canonical),
        'studio_sha256':sha(studio),'legacy_sha256':sha(old['legacy_sxh']),
        'inherited_sidecar_sha256':sha(json.dumps(old['sidecar'],sort_keys=True,separators=(',',':'))),
        'all_speech_unauthenticated':True, 'authorizes':False,
        'linguistic_authorization_never_equals_host_capability':True,
        'semantic_loss_if_legacy_only': [
            f'turn {x["turn"]}: {x["kind"]}' for x in acts if x['kind']!='ordinary_utterance'],
        'turns':meta}
    return {'native':canonical,'studio17':studio,'legacy_sxh':old['legacy_sxh'],
            'studio17_sidecar':old['sidecar'],'meaning18':identity,
            'reference_status':[{'turn':m['index'],'reference':t['reference'],
                                 'mi':t['leaf_roles']['mi'],'ti':t['leaf_roles']['ti']}
                                for m,t in zip(old['sidecar']['turns'],old['legacy_doc']['turns'])]}

def verify_bundle(native:str,studio:str,sxh:str,sidecar17:dict,meaning18:dict)->dict:
    result=parse_native(native)
    if studio!=result['studio17'] or sxh!=result['legacy_sxh']:
        bad('transcript differs from reversible native projection')
    if sidecar17!=result['studio17_sidecar'] or meaning18!=result['meaning18']:
        bad('sidecar or meaning record differs from independently reconstructed projection')
    verify_pair(sxh,sidecar17)
    return result

def write_bundle(native:str, directory:Path):
    r=parse_native(native);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    for filename,contents in [('conversation.sxp18',r['native']),('conversation.studio',r['studio17']),
                              ('conversation.sxh',r['legacy_sxh'])]:
        (directory/filename).write_text(contents,encoding='utf8')
    for filename,obj in [('conversation.sxpl17.json',r['studio17_sidecar']),('conversation.sxpl18.json',r['meaning18'])]:
        (directory/filename).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    verify_bundle(r['native'],r['studio17'],r['legacy_sxh'],r['studio17_sidecar'],r['meaning18'])
    return r

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('--out',default='repair18_output')
    args=p.parse_args()
    r=write_bundle(Path(args.source).read_text(encoding='utf8'),Path(args.out))
    print(json.dumps({'turns':len(r['meaning18']['turns']),
      'lost_if_legacy_only':r['meaning18']['semantic_loss_if_legacy_only'],
      'authorizes':False},indent=2))
