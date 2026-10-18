"""SXP-L 1.0 discourse transcript: statements, links, corrections, provenance.

No real-world authentication, consent enforcement, or tool effects.
Records linguistic events with explicitly attributed provenance.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from sxpl_v03 import SXPError
from sovereignty import parse_expression, render_expression, ACTS
from dialogue09 import check_expression as check_v09

HEADER='diala 1.0'
MAX_DOCUMENT=200_000
MAX_LINE=16_384
MAX_PERSONA=64
MAX_TURNS=256
MAX_EVENTS=2048
ID=re.compile(r'[a-z][a-z0-9_]{0,39}\Z')
RELATIONS={'and','but','because'}
PROVENANCE={'self_report','hearsay','document_claim','sensor_claim','unknown'}


def fail(code,detail=''):raise SXPError(code,detail)


def vid(x):
    if not isinstance(x,str) or not ID.fullmatch(x) or x in ('mi','ti','none'):
        fail('E_V08_ID',str(x))
    return x


def resolve_entity(x,speaker,addressee):
    if x=='mi':return speaker
    if x=='ti':
        if addressee is None:fail('E_V08_UNBOUND_YOU','ti requires addressee')
        return addressee
    return x


def check_expression(doc, speaker, addressee, roster):
    """Resolve discourse labels, not real authenticated agent identities."""
    node=doc['node']
    if node['kind']=='legacy_v09':
        return check_v09(node['content'],speaker,addressee,roster)
    if node['kind'] not in ACTS.values():
        fail('E_V10_DIALOGUE_ACT','unrecognized speech act')
    target=resolve_entity(node['counterparty'],speaker,addressee)
    if target not in roster:
        fail('E_V10_DIALOGUE_TARGET','counterparty not in participant roster')
    return sorted({speaker,target})

def parse_document(src):
    if not isinstance(src,str) or len(src)>MAX_DOCUMENT:fail('E_V08_DOCUMENT','limit or type')
    lines=[]
    for number,raw in enumerate(src.splitlines(),1):
        s=raw.strip()
        if not s or s.startswith('#'):continue
        if len(s)>MAX_LINE:fail('E_V08_DOCUMENT','line limit')
        lines.append((number,s))
    if not lines or lines[0][1]!=HEADER:fail('E_V08_HEADER')
    people=[];turns=[];current=None;utterances={};events_count=0;provenance_seen=set();repaired=set()
    for number,s in lines[1:]:
        parts=s.split();tag=parts[0]
        if tag=='persona':
            if len(parts)!=2 or turns or current is not None:fail('E_V08_PERSON_POSITION',str(number))
            person=vid(parts[1])
            if person in people:fail('E_V08_DUP_PERSON',person)
            people.append(person)
            if len(people)>MAX_PERSONA:fail('E_V08_LIMIT','people')
        elif tag=='tura':
            if current is not None or len(parts)!=4 or parts[2]!='to':fail('E_V08_TURN',str(number))
            speaker=vid(parts[1]); addressee= None if parts[3]=='none' else vid(parts[3])
            if speaker not in people or addressee is not None and addressee not in people or speaker==addressee:
                fail('E_V08_TURN','participants')
            current={'speaker':speaker,'addressee':addressee,'events':[]}
            turns.append(current)
            if len(turns)>MAX_TURNS:fail('E_V08_LIMIT','turns')
        elif tag=='lina':
            if current is None:fail('E_V08_NO_TURN',str(number))
            before,sep,speech=s.partition(' ^ ')
            if not sep or len(before.split())!=2 or not speech:fail('E_V08_LINE',str(number))
            uid=vid(before.split()[1])
            if uid in utterances:fail('E_V08_DUP_LINE',uid)
            parsed=parse_expression(speech)
            check_expression(parsed,current['speaker'],current['addressee'],set(people))
            utterances[uid]={'speaker':current['speaker'],'turn_index':len(turns)-1,'sequence':len(utterances)}
            current['events'].append({'kind':'utterance','id':uid,'parsed':parsed})
        elif tag=='kora':
            if current is None or len(parts)!=4:fail('E_V08_LINK',str(number))
            _,rel,left,right=parts
            if rel not in RELATIONS or left==right or left not in utterances or right not in utterances:
                fail('E_V08_LINK','relation/referents')
            current['events'].append({'kind':'link','relation':rel,'left':left,'right':right,'by':current['speaker'],
                                      'epistemic_status':'speaker_supplied_link'})
        elif tag=='evida':
            if current is None or len(parts)!=3:fail('E_V08_PROVENANCE',str(number))
            _,uid,source=parts
            if uid not in utterances or uid in provenance_seen or source not in PROVENANCE:
                fail('E_V08_PROVENANCE','id/duplicate/source')
            provenance_seen.add(uid)
            current['events'].append({'kind':'provenance','for':uid,'source_class':source,
                                      'claimed_by':current['speaker'],'verified':False})
        elif tag=='repara':
            if current is None or len(parts)!=3:fail('E_V08_REPAIR',str(number))
            old,new=parts[1:]
            if (old==new or old not in utterances or new not in utterances or old in repaired
                or utterances[old]['speaker']!=current['speaker']
                or utterances[new]['speaker']!=current['speaker']
                or utterances[new]['sequence']<=utterances[old]['sequence']):
                fail('E_V08_REPAIR','only one same-speaker repair of existing utterances')
            # Explicit repair must be declared after both, and the new line
            # cannot have already been consumed as a repair target.
            repaired.add(old)
            current['events'].append({'kind':'repair','old':old,'new':new,'by':current['speaker'],
                                      'status':'superseded_not_deleted'})
        elif tag=='enda':
            if current is None or len(parts)!=1 or not current['events']:
                fail('E_V08_END',str(number))
            current=None
        else:fail('E_V08_TOKEN',f'{number}: {tag}')
        if current is not None:
            events_count+=1
            if events_count>MAX_EVENTS:fail('E_V08_LIMIT','events')
    if current is not None:fail('E_V08_UNCLOSED')
    if not people or not turns:fail('E_V08_EMPTY')
    return {'lang':'SXP-L','schema':'1.0.0','register':'sovereignty_dialogue',
            'participants':people,'turns':turns}


def render_document(doc):
    if not isinstance(doc,dict) or set(doc)!={'lang','schema','register','participants','turns'} or doc['lang']!='SXP-L' or doc['schema']!='1.0.0' or doc['register']!='sovereignty_dialogue':fail('E_V08_SCHEMA')
    lines=[HEADER,*('persona '+p for p in doc['participants'])]
    for turn in doc['turns']:
        lines.append('tura '+turn['speaker']+' to '+(turn['addressee'] or 'none'))
        for evt in turn['events']:
            k=evt['kind']
            if k=='utterance':lines.append('lina '+evt['id']+' ^ '+render_expression(evt['parsed']))
            elif k=='link':lines.append('kora '+evt['relation']+' '+evt['left']+' '+evt['right'])
            elif k=='provenance':lines.append('evida '+evt['for']+' '+evt['source_class'])
            elif k=='repair':lines.append('repara '+evt['old']+' '+evt['new'])
            else:fail('E_V08_AST','unknown event')
        lines.append('enda')
    rendered='\n'.join(lines)+'\n'
    if parse_document(rendered)!=doc:fail('E_V08_AST','doc mismatch')
    return rendered


def fingerprint(doc):
    render_document(doc)
    b=json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(b'SXP-L-dialogue-v1.0\0'+b).hexdigest()


def summarize(doc):
    return {'schema':doc['schema'],'participants':len(doc['participants']),
            'turns':len(doc['turns']),
            'utterances':sum(e['kind']=='utterance' for t in doc['turns'] for e in t['events']),
            'links':sum(e['kind']=='link' for t in doc['turns'] for e in t['events']),
            'repairs':sum(e['kind']=='repair' for t in doc['turns'] for e in t['events']),
            'provenance_claims':sum(e['kind']=='provenance' for t in doc['turns'] for e in t['events']),
            'fingerprint':fingerprint(doc)}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('file',type=Path)
    p.add_argument('--format',choices=['normalized','json','summary'],default='summary')
    a=p.parse_args();d=parse_document(a.file.read_text(encoding='utf-8'))
    if a.format=='normalized':print(render_document(d),end='')
    elif a.format=='json':print(json.dumps(d,indent=2,ensure_ascii=False))
    else:print(json.dumps(summarize(d),indent=2))
