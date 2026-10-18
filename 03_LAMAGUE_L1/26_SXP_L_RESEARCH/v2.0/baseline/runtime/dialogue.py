"""SXP-L v0.5 experimental dialogue parser. NO natural-language translation or inference.

A line in the human register is attributed to a speaker. A co-reference pronoun
is expanded ONLY in participant-valued semantic roles. Discourse links record
speaker-supplied interpretations, not proven logical entailment or causation.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from sxpl_v03 import parse as parse_clause, render as render_clause, SXPError
from roots import hear_roots, speak_roots

SCHEMA = '0.5.0'
ID = re.compile(r'^[a-z][a-z0-9_]{0,39}$')
CONTROL = {'mi', 'ti', 'none'}
RELATIONS = {'and', 'but', 'because'}
MAX_DOCUMENT = 200_000
MAX_TURNS = 256
MAX_LINES = 2048
MAX_PEOPLE = 64
MAX_LINE = 16_384


def fail(code, detail=''):
    raise SXPError(code, detail)


def valid_id(identifier, reserved=False):
    if not ID.fullmatch(identifier) or (reserved and identifier in CONTROL):
        fail('E_DIALOG_ID', identifier)
    return identifier


def resolve_pronouns(clause, speaker, addressee, roster):
    """Expand mi, ti for actor/target/viewpoint recursively; leave arbitrary quoted data intact."""
    result = copy.deepcopy(clause)

    def resolve(node):
        for role, val in node['roles'].items():
            if role == 'proposition':
                resolve(val['value'])
            elif role in {'actor', 'target', 'viewpoint'} and val['type'] == 'symbol':
                word = val['value']
                if word == 'mi':
                    val['value'] = speaker
                elif word == 'ti':
                    if addressee is None:
                        fail('E_UNBOUND_YOU', 'ti requires addressee')
                    val['value'] = addressee
                # Actor / viewpoint must be named participant in this experimental dialogue subset.
                if role in {'actor', 'viewpoint'} and val['value'] not in roster:
                    fail('E_UNBOUND_PARTICIPANT', val['value'])
    resolve(result['clause'])
    return result


def parse_document(source):
    if len(source) > MAX_DOCUMENT:
        fail('E_DIALOG_LIMIT', 'document size')
    nonblank=[]
    for line_num, raw in enumerate(source.splitlines(), 1):
        line=raw.strip()
        if line and not line.startswith('#'):
            if len(line)>MAX_LINE:fail('E_DIALOG_LIMIT', 'line size')
            nonblank.append((line_num,line))
    if not nonblank or nonblank[0][1] != 'diala 0.5':
        fail('E_DIALOG_HEADER', 'expected diala 0.5')
    people=[]
    turns=[]
    seen_ids=set()
    # Lines may be linked after declaration; no forward references are accepted.
    speaker = None
    addressee = None
    active = None
    lines = 0
    for ln, line in nonblank[1:]:
        parts=line.split()
        key=parts[0]
        if key=='persona':
            if active is not None or turns:
                fail('E_DIALOG_PERSONA_POSITION', str(ln))
            if len(parts)!=2:fail('E_DIALOG_PERSONA', str(ln))
            ident=valid_id(parts[1],reserved=True)
            if ident in people:fail('E_DIALOG_DUP_PERSONA',ident)
            people.append(ident)
            if len(people)>MAX_PEOPLE:fail('E_DIALOG_LIMIT','participants')
        elif key=='tura':
            if active is not None:fail('E_DIALOG_UNCLOSED_TURN',str(ln))
            if len(parts)!=4 or parts[2]!='to':fail('E_DIALOG_TURN',str(ln))
            speaker=valid_id(parts[1]);addressee=valid_id(parts[3]) if parts[3]!='none' else None
            if speaker not in people or addressee is not None and addressee not in people:
                fail('E_DIALOG_UNKNOWN_PERSONA',str(ln))
            if speaker==addressee:fail('E_DIALOG_SELF_ADDRESS',str(ln))
            active={'speaker':speaker,'addressee':addressee,'events':[]}
            turns.append(active)
            if len(turns)>MAX_TURNS:fail('E_DIALOG_LIMIT','turns')
        elif key=='lina':
            if active is None:fail('E_DIALOG_NO_TURN',str(ln))
            lead,sep,surf=line.partition(' | ')
            if not sep or len(lead.split())!=2 or not surf.strip():fail('E_DIALOG_LINE',str(ln))
            uid=valid_id(lead.split()[1]);
            if uid in seen_ids:fail('E_DIALOG_DUP_LINE',uid)
            seen_ids.add(uid)
            # All v0.4 surface content must be explicitly lexically marked (nami).
            canonical=hear_roots(surf)
            raw_ast=parse_clause(canonical)
            normalized_surface=speak_roots(render_clause(raw_ast))
            grounded=resolve_pronouns(raw_ast,speaker,addressee,set(people))
            active['events'].append({'kind':'line','id':uid,'surface':normalized_surface,'resolved':grounded})
            lines+=1
            if lines>MAX_LINES:fail('E_DIALOG_LIMIT','utterances')
        elif key=='kora':
            if active is None:fail('E_DIALOG_NO_TURN',str(ln))
            if len(parts)!=4:fail('E_DIALOG_LINK',str(ln))
            _,rel,left,right=parts
            if rel not in RELATIONS:fail('E_DIALOG_RELATION',rel)
            if left not in seen_ids or right not in seen_ids or left==right:
                fail('E_DIALOG_UNBOUND_LINK',str(ln))
            active['events'].append({'kind':'link','relation':rel,'left':left,'right':right,'by':speaker})
        elif key=='enda':
            if active is None or len(parts)!=1:fail('E_DIALOG_END',str(ln))
            if not active['events']:fail('E_DIALOG_EMPTY_TURN',str(ln))
            active=None;speaker=None;addressee=None
        else:
            fail('E_DIALOG_TOKEN',f'{ln}: {key}')
    if active is not None:fail('E_DIALOG_UNCLOSED_TURN','end of document')
    if not people or not turns:fail('E_DIALOG_EMPTY','missing participants or turns')
    return {'lang':'SXP-L','schema':SCHEMA,'register':'dialogue','participants':people,'turns':turns}


def render_document(document):
    """Validation by reparsing; external input never controls semantics through a JSON shortcut."""
    if not isinstance(document,dict) or set(document)!={'lang','schema','register','participants','turns'} or document['lang']!='SXP-L' or document['schema']!=SCHEMA or document['register']!='dialogue':
        fail('E_DIALOG_SCHEMA')
    if not isinstance(document['participants'],list) or not isinstance(document['turns'],list):
        fail('E_DIALOG_SCHEMA')
    lines=['diala 0.5', *('persona '+p for p in document['participants'])]
    for turn in document['turns']:
        if not isinstance(turn,dict) or set(turn)!={'speaker','addressee','events'}:fail('E_DIALOG_SCHEMA')
        lines.append('tura '+turn['speaker']+' to '+(turn['addressee'] or 'none'))
        for event in turn['events']:
            if event['kind']=='line':
                lines.append('lina '+event['id']+' | '+event['surface'])
            elif event['kind']=='link':
                lines.append('kora '+event['relation']+' '+event['left']+' '+event['right'])
            else: fail('E_DIALOG_SCHEMA')
        lines.append('enda')
    text='\n'.join(lines)+'\n'
    if parse_document(text)!=document:fail('E_DIALOG_AST','AST is inconsistent with document')
    return text


def canonical_bytes(document):
    render_document(document)
    return json.dumps(document,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')


def fingerprint(document):
    return hashlib.sha256(b'SXP-L-dialogue-v0.5\0'+canonical_bytes(document)).hexdigest()


def summarize(document):
    return {'schema':SCHEMA,'participants':len(document['participants']),
            'turns':len(document['turns']),
            'utterances':sum(sum(e['kind']=='line' for e in t['events']) for t in document['turns']),
            'links':sum(sum(e['kind']=='link' for e in t['events']) for t in document['turns']),
            'digest':fingerprint(document)}


def main():
    cli=argparse.ArgumentParser(description='SXP-L v0.5 controlled dialogue parser')
    cli.add_argument('file',type=Path)
    cli.add_argument('--output',choices=['summary','json','normalized'],default='summary')
    args=cli.parse_args()
    ast=parse_document(args.file.read_text(encoding='utf8'))
    if args.output=='summary':print(json.dumps(summarize(ast),indent=2))
    if args.output=='json':print(json.dumps(ast,ensure_ascii=False,indent=2))
    if args.output=='normalized':print(render_document(ast),end='')

if __name__=='__main__':main()
