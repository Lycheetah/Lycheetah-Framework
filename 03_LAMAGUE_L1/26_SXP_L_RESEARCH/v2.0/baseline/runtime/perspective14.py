"""SXP-L 1.4 bounded, textual nested-perspective transcript layer.

Three *speaker-attributed* frames: reported speech (not verbatim), belief,
not-knowing-whether.  A frame lists holder and local addressee explicitly.
Only the innermost frame binds the leaf's `mi`/`ti` and third-person reference.
The transcript is NOT authenticated evidence, a truth engine, a grammar for
natural language, or an authorization mechanism.

Imports legacy continuity13 without modifying it. v1.3 surface transcripts
remain valid and reconstructable; no automatic pronoun recency guessing.
"""
from __future__ import annotations
import json
from sxpl_v03 import SXPError
from spoken import syllables, lev
from continuity13 import (DECL, TURN, ANCHOR, REPLY, END, PRONOUN, NEW as V13_NEW,
    MAX_TURNS, MAX_LINES, MAX_SOURCE_CHARS, MAX_PEOPLE, _tokens, _header,
    parse_name, name, turn_id, _canonical_resolution, parse_transcript as parse13)
from discourse12 import NEW as V12_NEW
from discourse11 import NEW as V11_NEW, ALL_OLD

VERSION='1.4.0'
REGISTER='nested_perspective_transcript'
FRAMES={'naveriko':'reported_speech','belareko':'belief','nesaluko':'not_know_whether'}
INVERSE={v:k for k,v in FRAMES.items()}
MAX_DEPTH=6
NEW=frozenset(FRAMES)

for word in NEW:
    syllables(word)
    assert all(lev(word, old)>1 for old in ALL_OLD|V11_NEW|V12_NEW|V13_NEW)
assert all(lev(a,b)>1 for a in NEW for b in NEW if a!=b)


def fail(code, msg=''):
    raise SXPError(code,msg)


def _frame(words:list[str],declared:list[str])->dict:
    if words[0] not in FRAMES:fail('E_V14_FRAME','unknown frame')
    holder, pos=parse_name(words,1)
    audience,pos=parse_name(words,pos)
    if pos!=len(words) or holder not in declared or audience not in declared or holder==audience:
        fail('E_V14_FRAME','holder/addressee must be distinct declared persons')
    return {'kind':FRAMES[words[0]],'holder':holder,'local_addressee':audience,
            'evidence':'outer_speaker_claim_unverified', 'authorizes':False}


def parse_transcript(source:str)->dict:
    if not isinstance(source,str) or not source or len(source)>MAX_SOURCE_CHARS:
        fail('E_V14_LIMIT','bounded nonempty text required')
    lines=[line.strip() for line in source.splitlines() if line.strip()]
    if len(lines)>MAX_LINES:fail('E_V14_LIMIT','too many lines')
    declared=[]; turns=[]; i=0
    while i<len(lines) and _tokens(lines[i])[0]==DECL:
        tokens=_tokens(lines[i]); person,pos=parse_name(tokens,1)
        if pos!=len(tokens) or person in declared:fail('E_V14_DECL','duplicate/invalid declaration')
        declared.append(person)
        if len(declared)>MAX_PEOPLE:fail('E_V14_LIMIT','too many people')
        i+=1
    if len(declared)<2:fail('E_V14_DECL','at least two people required')
    while i<len(lines):
        if len(turns)>=MAX_TURNS:fail('E_V14_LIMIT','turn count')
        speaker,audience=_header(_tokens(lines[i]));i+=1
        if speaker not in declared or audience not in declared:
            fail('E_V14_TURN','undeclared outer roles')
        anchor=None;reply=None
        if i<len(lines) and _tokens(lines[i])[0]==ANCHOR:
            tokens=_tokens(lines[i]); anchor,pos=parse_name(tokens,1)
            if pos!=len(tokens):fail('E_V14_ANCHOR','extra anchor tokens')
            i+=1
        if i<len(lines) and _tokens(lines[i])[0]==REPLY:
            tokens=_tokens(lines[i]);reply,pos=parse_name(tokens,1)
            if pos!=len(tokens) or reply not in {turn_id(x) for x in range(1,len(turns)+1)}:
                fail('E_V14_REPLY','must name earlier turn')
            i+=1
        frames=[]
        while i<len(lines) and _tokens(lines[i])[0] in FRAMES:
            if len(frames)>=MAX_DEPTH:fail('E_V14_DEPTH','maximum nesting exceeded')
            frames.append(_frame(_tokens(lines[i]),declared));i+=1
        if i+1>=len(lines):fail('E_V14_TURN','missing leaf and end')
        leaf=lines[i];words=_tokens(leaf);i+=1
        if words[0] in set(FRAMES)|{DECL,TURN,ANCHOR,REPLY,END}:
            fail('E_V14_TURN','expression expected')
        if _tokens(lines[i])!=[END]:fail('E_V14_END','expected single tevaro')
        i+=1
        local_speaker=frames[-1]['holder'] if frames else speaker
        local_audience=frames[-1]['local_addressee'] if frames else audience
        ref=_canonical_resolution(words,local_speaker,local_audience,declared,anchor)
        turns.append({'id':turn_id(len(turns)+1),'speaker':speaker,'audience':audience,
            'anchor':anchor,'reply_to':reply,'frames':frames,'utterance':leaf,
            'leaf_roles':{'mi':local_speaker,'ti':local_audience,'scope':'leaf_outer_only'},
            'reference':ref,'speech_authenticated':False,'authorizes':False})
    if not turns:fail('E_V14_EMPTY','no turns')
    return {'lang':'SXP-L','schema':VERSION,'register':REGISTER,'participants':declared,
        'turns':turns,'identity_claims_authenticated':False,'authorizes':False}


def render_transcript(doc:dict)->str:
    if not isinstance(doc,dict) or set(doc)!={'lang','schema','register','participants','turns','identity_claims_authenticated','authorizes'} or \
        doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!=REGISTER or \
        doc['identity_claims_authenticated'] is not False or doc['authorizes'] is not False:
        fail('E_V14_SCHEMA','wrong/untrusted outer metadata')
    lines=[f'{DECL} {name(x)}' for x in doc['participants']]
    for t in doc['turns']:
        lines.append(f'{TURN} {name(t["speaker"])} {name(t["audience"])}')
        if t['anchor'] is not None:lines.append(f'{ANCHOR} {name(t["anchor"])}')
        if t['reply_to'] is not None:lines.append(f'{REPLY} {name(t["reply_to"])}')
        for frame in t['frames']:
            if frame['kind'] not in INVERSE:fail('E_V14_FRAME','noncanonical frame')
            lines.append(f'{INVERSE[frame["kind"]]} {name(frame["holder"])} {name(frame["local_addressee"])}')
        lines.extend([t['utterance'],END])
    output='\n'.join(lines)+'\n'
    if parse_transcript(output)!=doc:fail('E_V14_ROUNDTRIP','modified or unsupported semantic fields')
    return output


def interpret_transcript(doc:dict)->list[dict]:
    render_transcript(doc)
    out=[]
    for t in doc['turns']:
        out.append({'id':t['id'],'outer_speaker':t['speaker'],
            'reported_frames':[{'kind':f['kind'],'holder':f['holder'],
                'addressee':f['local_addressee']} for f in t['frames']],
            'leaf_first_person':t['leaf_roles']['mi'],
            'leaf_second_person':t['leaf_roles']['ti'],
            'third_person':t['reference']['chosen'],
            'third_person_status':t['reference']['status'],
            'third_person_candidates':t['reference']['candidates'],
            'proposition_accepted_as_fact':False,'speech_authenticated':False,
            'authorizes':False,
            'warning':'Frames are outer-speaker allegations; beliefs and uncertainty are not facts.'})
    return out


def compatibility_check(old_text:str)->bool:
    """Plain v1.3 transcripts retain same core roles/reference semantics."""
    old=parse13(old_text);new=parse_transcript(old_text)
    if old['participants']!=new['participants'] or len(old['turns'])!=len(new['turns']):return False
    return all(a['speaker']==b['speaker'] and a['audience']==b['audience'] and
        a['utterance']==b['utterance'] and a['reply_to']==b['reply_to'] and
        a['reference']==b['reference'] and not b['frames']
        for a,b in zip(old['turns'],new['turns']))

if __name__=='__main__':
    import argparse
    arg=argparse.ArgumentParser();arg.add_argument('file');args=arg.parse_args()
    text=open(args.file,encoding='utf8').read()
    doc=parse_transcript(text)
    print(json.dumps(interpret_transcript(doc),indent=2))
