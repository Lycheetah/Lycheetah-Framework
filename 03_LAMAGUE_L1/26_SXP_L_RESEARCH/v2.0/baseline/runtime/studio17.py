"""SXP-L v1.7 experimental *authoring* shorthand and explicit conversation repairs.

This is NOT a new spoken register. Legacy v1.4 .sxh files omit repair kinds;
JSON companion + matching .sxh must be retained together. No external actions.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from perspective14 import parse_transcript, render_transcript
from continuity13 import turn_id
from spoken import is_literal_name
from sxpl_v03 import SXPError

VERSION='1.7.0'
MAX_INPUT=32000
MAX_LINES=150
MAX_PARTICIPANTS=16
MAX_TURNS=35
TURN_RE=re.compile(r'([a-z]+)\s*>\s*([a-z]+)\s*((?:(?:[@?~]\d+|#[a-z]+|\^[a-z]+\([a-z]+,[a-z]+\))\s*)*)\s*:\s*(.+)')
MOD_RE=re.compile(r'([@?~]\d+|#[a-z]+|\^[a-z]+\([a-z]+,[a-z]+\))')
FRAMES={'naveriko','belareko','nesaluko'}
KIND={'@':'reply','?':'clarification_request','~':'self_correction'}

def bad(why): raise SXPError('E_V17_STUDIO',why)

def parse_studio(src: str)->dict:
    if not isinstance(src,str) or not 0<len(src)<=MAX_INPUT:bad('bounded nonempty text required')
    lines=[x.strip() for x in src.splitlines() if x.strip()]
    if len(lines)>MAX_LINES or not lines:bad('too many lines or empty input')
    people=lines.pop(0).split()
    if not people or people[0]!='people' or not 2<=len(people)-1<=MAX_PARTICIPANTS:bad('first line: people name name ...')
    people=people[1:]
    if len(set(people))!=len(people) or not all(is_literal_name(x) and x!='sivena' for x in people):bad('duplicate or invalid declared person')
    if not lines or len(lines)>MAX_TURNS:bad('need 1-35 turns')
    legacy=[f'norava gonape {p} dimotu' for p in people]
    relations=[]; meta=[]; effective={}
    for idx,line in enumerate(lines,1):
        m=TURN_RE.fullmatch(line)
        if not m:bad(f'bad turn {idx}; expected name > name [modifiers] : expression')
        speaker,audience,mods,leaf=m.groups()
        if speaker not in people or audience not in people or speaker==audience:bad(f'invalid turn {idx} participants')
        if leaf.endswith(' devora'):leaf=leaf[:-7].strip()
        if not leaf or '  ' in leaf or '\t' in leaf:bad(f'noncanonical leaf in turn {idx}')
        pieces=MOD_RE.findall(mods)
        if ''.join(pieces)!=''.join(mods.split()):bad(f'unknown/duplicated modifiers in turn {idx}')
        link=None;anchor=None;frames=[]
        for code in pieces:
            if code[0] in '@?~':
                if link is not None:bad(f'only one reply/repair link in turn {idx}')
                number=int(code[1:])
                if not 1<=number<idx:bad(f'link at turn {idx} must reference earlier turn')
                link={'kind':KIND[code[0]],'target_index':number,'target_id':turn_id(number)}
            elif code[0]=='#':
                if anchor is not None:bad(f'duplicate anchor in turn {idx}')
                anchor=code[1:]
                if anchor not in people:bad('anchor must be declared')
            else:
                part=code[1:];f_kind,other=part.split('(',1)
                holder,local_aud=other[:-1].split(',')
                if f_kind not in FRAMES or holder not in people or local_aud not in people:bad('unsupported frame or undeclared holder')
                frames.append((f_kind,holder,local_aud))
        if len(frames)>6:bad('too many frames')
        if link:
            old=meta[link['target_index']-1]
            if link['kind']=='self_correction':
                if speaker!=old['speaker'] or old['corrected_by'] is not None:bad('only author may correct an active, uncorrected turn')
                old['corrected_by']=idx
                effective[link['target_index']]='superseded_by_'+str(idx)
            elif link['kind']=='clarification_request' and speaker==old['speaker']:
                bad("clarification requests must address someone else's turn")
        legacy.append(f'taviro gonape {speaker} dimotu gonape {audience} dimotu')
        if anchor:legacy.append(f'rasufe gonape {anchor} dimotu')
        if link:legacy.append(f'repira gonape {link["target_id"]} dimotu')
        for k,h,a in frames:legacy.append(f'{k} gonape {h} dimotu gonape {a} dimotu')
        legacy.extend([leaf+' devora','tevaro'])
        meta.append({'id':turn_id(idx),'index':idx,'speaker':speaker,'audience':audience,
                     'link':link,'corrected_by':None,'frames':[list(f) for f in frames],
                     'anchor':anchor,'leaf':leaf})
        relations.append(link['kind'] if link else 'new_utterance')
    sxh='\n'.join(legacy)+'\n'
    doc=parse_transcript(sxh)
    if render_transcript(doc)!=sxh:bad('legacy parser canonical disagreement')
    for i,turn in enumerate(doc['turns']):
        if turn['id']!=meta[i]['id']:bad('stable turn indexing failed')
    sha=hashlib.sha256(sxh.encode()).hexdigest()
    # A sidecar is necessary: older .sxh format preserves reply target but loses relation kind.
    sidecar={'schema':'SXP-L-studio-1.7','legacy_sha256':sha,'unverified_speaker_identity':True,
             'authorizes':False,'turns':meta,'sidecar_required_for_repair_semantics':True}
    return {'studio_schema':VERSION,'participants':people,'legacy_sxh':sxh,
            'sidecar':sidecar,'legacy_doc':doc,'meaning_loss_if_only_sxh':
            [f'turn {i+1}: {x} not represented by v1.4 reply_to alone' for i,x in enumerate(relations) if x not in {'new_utterance','reply'}]}

def verify_pair(sxh: str, sidecar: dict) -> dict:
    if not isinstance(sidecar,dict) or sidecar.get('schema')!='SXP-L-studio-1.7' or \
       sidecar.get('authorizes') is not False or sidecar.get('unverified_speaker_identity') is not True:
        bad('invalid/untrusted sidecar metadata')
    if hashlib.sha256(sxh.encode()).hexdigest()!=sidecar.get('legacy_sha256'):
        bad('sidecar transcript hash does not match')
    parsed=parse_transcript(sxh)
    if render_transcript(parsed)!=sxh:bad('noncanonical .sxh in pair')
    mts=sidecar.get('turns')
    if not isinstance(mts,list) or len(mts)!=len(parsed['turns']):bad('metadata turn count mismatch')
    # Reconstruct the authoring shorthand from both artifacts, then compare all fields.
    people=parsed['participants']
    lines=['people '+' '.join(people)]
    for pos,(s,t) in enumerate(zip(mts,parsed['turns']),1):
        if s.get('id')!=turn_id(pos) or s.get('index')!=pos or s.get('speaker')!=t['speaker'] or s.get('audience')!=t['audience'] or \
          s.get('anchor')!=t['anchor'] or s.get('leaf')+' devora'!=t['utterance']:
            bad('sidecar turns diverge from source')
        parts=[]
        l=s.get('link')
        if l is not None:
            inv={'reply':'@','clarification_request':'?','self_correction':'~'}
            if l.get('kind') not in inv or not isinstance(l.get('target_index'),int):bad('invalid relation kind')
            parts.append(inv[l['kind']]+str(l['target_index']))
        if s.get('anchor') is not None:parts.append('#'+s['anchor'])
        for f in s.get('frames',[]):
            if not isinstance(f,list) or len(f)!=3:bad('malformed frame')
            parts.append('^'+f[0]+'('+f[1]+','+f[2]+')')
        lines.append(f'{t["speaker"]} > {t["audience"]} '+(' '.join(parts)+' ' if parts else '')+': '+s['leaf'])
    rec=parse_studio('\n'.join(lines))
    if rec['legacy_sxh']!=sxh or rec['sidecar']!=sidecar:bad('semantic overlay tampered or noncanonical')
    return rec

def inspect(src: str)->dict:
    doc=parse_studio(src)
    rows=[]
    for t,m in zip(doc['legacy_doc']['turns'],doc['sidecar']['turns']):
        rows.append({'turn':m['index'],'speaker':m['speaker'],'addressee':m['audience'],
            'link_kind':m['link']['kind'] if m['link'] else None,
            'reply_to':t['reply_to'],'corrected_by':m['corrected_by'],
            'leaf':m['leaf'],'local_first_person':t['leaf_roles']['mi'],
            'local_second_person':t['leaf_roles']['ti'],
            'third_person_status':t['reference']['status'],
            'third_person_candidates':t['reference']['candidates'],
            'third_person_chosen':t['reference']['chosen'],
            'speech_authenticated':False,'authorizes':False})
    return {'turns':rows,'meaning_loss_if_only_sxh':doc['meaning_loss_if_only_sxh'],
            'authorizes':False,'all_speech_claims_unverified':True}

def save(src: str, out: Path)->None:
    d=parse_studio(src)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'conversation.sxh').write_text(d['legacy_sxh'])
    (out/'conversation.sxpl17.json').write_text(json.dumps(d['sidecar'],indent=2)+'\n')
    (out/'analysis.json').write_text(json.dumps(inspect(src),indent=2)+'\n')
    (out/'conversation.studio').write_text(src.rstrip()+'\n')
    verify_pair(d['legacy_sxh'],d['sidecar'])

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('--out',default='studio_output')
    a=parser.parse_args()
    source=Path(a.source).read_text(encoding='utf8')
    save(source,Path(a.out))
    print(json.dumps(inspect(source),indent=2))
