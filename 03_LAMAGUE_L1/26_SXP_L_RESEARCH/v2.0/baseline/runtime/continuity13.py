"""SXP-L v1.3 experimental transcript/reference register.

This is a *text* dialogue envelope around unchanged v1.2 utterances.
It records purported participant/utterance roles; it does not authenticate them,
verify claimed speech, infer mental states, or grant executable permission.

Unqualified third person `sivena` resolves only if precisely one eligible
third-person participant is in scope. Otherwise it remains explicitly unresolved.
Explicit `nerava` anchors apply to the current turn only, never to prior turns.
"""
from __future__ import annotations

import json
import re
from sxpl_v03 import SXPError
from spoken import spoken_tokens, syllables, lev, is_literal_name
from discourse12 import parse_expression as parse12, render_expression as render12
from discourse12 import NEW as V12_NEW
from discourse11 import NEW as V11_NEW, ALL_OLD

VERSION = '1.3.0'
REGISTER = 'continuity_transcript'
DECL = 'norava'
TURN = 'taviro'
ANCHOR = 'rasufe'
REPLY = 'repira'
END = 'tevaro'
PRONOUN = 'sivena'  # provisional unqualified third person; no grammatical gender
NEW = frozenset({DECL,TURN,ANCHOR,REPLY,END,PRONOUN})
IDENT = re.compile(r'[a-z][a-z0-9_]{0,39}\Z')
MAX_TURNS = 100
MAX_PEOPLE = 32
MAX_LINES = 420
MAX_SOURCE_CHARS = 120000
MAX_TOKENS_PER_LINE = 4096

for word in NEW:
    syllables(word)
assert len(NEW)==6
# This *screens* candidate words; not a claim of acoustic separation.
assert all(lev(a,b)>1 for a in NEW for b in NEW if a!=b)
assert all(lev(a,b)>1 for a in NEW for b in ALL_OLD|V11_NEW|V12_NEW)


def fail(code, detail=''):
    raise SXPError(code, detail)


def name(value: str) -> str:
    if not isinstance(value,str) or not is_literal_name(value) or value in {'mi','ti','sivena'}:
        fail('E_V13_NAME',str(value))
    return f'gonape {value} dimotu'


def parse_name(words: list[str], pos: int=0) -> tuple[str,int]:
    if words[pos:pos+1]!=['gonape'] or pos+2>=len(words) or words[pos+2]!='dimotu':
        fail('E_V13_NAME','explicit named entity required')
    ident=words[pos+1]
    name(ident)
    return ident,pos+3


def turn_id(number: int) -> str:
    # Up to 100 stably named turn identifiers, all pronounced CV-CV.
    if not (1<=number<=MAX_TURNS):fail('E_V13_TURN_ID','turn id outside range')
    n=number-1
    return 't'+'aeiou'[n//60]+'bdfgkmnprstv'[(n%60)//5]+'aeiou'[n%5]

def _tokens(line):
    if not line or len(line)>36000:
        fail('E_V13_LIMIT','empty/oversized line')
    words=spoken_tokens(line)
    if len(words)>MAX_TOKENS_PER_LINE:
        fail('E_V13_LIMIT','oversized line token count')
    return words


def _header(words):
    if not words or words[0]!=TURN:fail('E_V13_TURN','turn header')
    speaker,p=parse_name(words,1)
    audience,p=parse_name(words,p)
    if p!=len(words) or speaker==audience:fail('E_V13_TURN','exactly two distinct participants')
    return speaker,audience


def _third_person_occurrences(words):
    # A third-person pronoun must never be smuggled into a proper-name frame.
    inside=False
    depth=0
    for word in words:
        if word=='gonape':
            if inside:fail('E_V13_NEST','nested name frame')
            inside=True
        elif word=='dimotu':
            inside=False
        elif word=='bakumo':
            depth+=1
        elif word=='tesavo':
            depth-=1
        elif word==PRONOUN and inside:
            fail('E_V13_PRONOUN','pronoun inside name frame')
        elif word==PRONOUN and depth!=0:
            fail('E_V13_SCOPE','third-person reference in reported/nested clause is not yet supported')
    return words.count(PRONOUN)


def _canonical_resolution(words, speaker, audience, declared, anchor):
    count=_third_person_occurrences(words)
    if not count:
        if anchor is not None:fail('E_V13_ANCHOR','anchor without pronoun')
        utterance=' '.join(words)
        ast=parse12(utterance)
        if render12(ast)!=utterance:fail('E_V13_CANON','source must be canonical v1.2 sentence')
        return {'status':'not_applicable','candidates':[], 'chosen':None,
                'expanded':utterance,'expression_ast':ast}
    options=sorted(p for p in declared if p not in (speaker,audience))
    if anchor is not None:
        if anchor not in options:fail('E_V13_ANCHOR','anchor not an eligible third person')
        options=[anchor]
        status='explicit_anchor'
    elif len(options)==1:
        status='unique_candidate'
    elif not options:
        status='unresolved'
    else:
        status='ambiguous'
    chosen=options[0] if len(options)==1 else None
    # Even ambiguous expressions must be grammatically well formed. Validate a
    # substituted sentence against the inherited parser, but never retain it as
    # a resolved meaning unless an eligible candidate is uniquely selected.
    if chosen is None:
        probe=options[0] if options else 'zazaza'
        check=[]
        for word in words:
            check.extend(('gonape',probe,'dimotu') if word==PRONOUN else (word,))
        surface=' '.join(check)
        ast=parse12(surface)
        if render12(ast)!=surface:fail('E_V13_CANON','ambiguous sentence malformed')
        return {'status':status,'candidates':options,'chosen':None,
                'expanded':None,'expression_ast':None}
    expansion=[]
    for word in words:
        expansion.extend(('gonape',chosen,'dimotu') if word==PRONOUN else (word,))
    utterance=' '.join(expansion)
    ast=parse12(utterance)
    if render12(ast)!=utterance:
        fail('E_V13_CANON','expanded utterance must be canonical v1.2 sentence')
    return {'status':status,'candidates':options,'chosen':chosen,
            'expanded':utterance,'expression_ast':ast}


def parse_transcript(source: str) -> dict:
    if not isinstance(source,str) or not source or len(source)>MAX_SOURCE_CHARS:
        fail('E_V13_LIMIT','source must be nonempty bounded text')
    lines=[line.strip() for line in source.splitlines() if line.strip()]
    if len(lines)>MAX_LINES:fail('E_V13_LIMIT','too many lines')
    participants=[]; turns=[]; cursor=0
    while cursor<len(lines):
        words=_tokens(lines[cursor])
        if words[0]!=DECL:break
        entity,used=parse_name(words,1)
        if used!=len(words) or entity in participants:fail('E_V13_DECL','duplicate/invalid participant')
        participants.append(entity)
        if len(participants)>MAX_PEOPLE:fail('E_V13_LIMIT','too many participants')
        cursor+=1
    if len(participants)<2:fail('E_V13_DECL','at least two named participants required')
    while cursor<len(lines):
        if len(turns)>=MAX_TURNS:fail('E_V13_LIMIT','too many turns')
        speaker,audience=_header(_tokens(lines[cursor]));cursor+=1
        if speaker not in participants or audience not in participants:
            fail('E_V13_TURN','speaker and audience must already be declared')
        hint=None;reply=None
        if cursor<len(lines) and _tokens(lines[cursor])[0]==ANCHOR:
            w=_tokens(lines[cursor]);hint,k=parse_name(w,1)
            if k!=len(w):fail('E_V13_ANCHOR','surplus words')
            cursor+=1
        if cursor<len(lines) and _tokens(lines[cursor])[0]==REPLY:
            w=_tokens(lines[cursor]);reply,k=parse_name(w,1)
            if k!=len(w) or reply not in {turn_id(i) for i in range(1,len(turns)+1)}:
                fail('E_V13_REPLY','reply must name an earlier turn')
            cursor+=1
        if cursor+1>=len(lines):fail('E_V13_TURN','missing expression and close')
        line=lines[cursor]; words=_tokens(line);cursor+=1
        if words[0] in {DECL,TURN,ANCHOR,REPLY,END}:
            fail('E_V13_TURN','missing utterance')
        if _tokens(lines[cursor])!=[END]:fail('E_V13_END','expected tevaro')
        cursor+=1
        resolved=_canonical_resolution(words,speaker,audience,participants,hint)
        turns.append({'id':turn_id(len(turns)+1),'speaker':speaker,'audience':audience,
                      'utterance':line,'anchor':hint,'reply_to':reply,
                      'reference':resolved,'roles':{'mi':speaker,'ti':audience,
                              'scope':'outer_utterance_only'},
                      'speech_authenticated':False,'authorizes':False})
    if not turns:fail('E_V13_EMPTY','at least one turn required')
    return {'lang':'SXP-L','schema':VERSION,'register':REGISTER,
            'participants':participants,'turns':turns,
            'identity_claims_authenticated':False,'authorizes':False}


def render_transcript(doc: dict) -> str:
    if not isinstance(doc,dict) or set(doc)!={'lang','schema','register','participants','turns',
                                               'identity_claims_authenticated','authorizes'} or \
       doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!=REGISTER or \
       doc['identity_claims_authenticated'] is not False or doc['authorizes'] is not False:
        fail('E_V13_SCHEMA','invalid envelope')
    result=[f'{DECL} {name(p)}' for p in doc['participants']]
    for turn in doc['turns']:
        result.append(f'{TURN} {name(turn["speaker"])} {name(turn["audience"])}')
        if turn['anchor'] is not None:result.append(f'{ANCHOR} {name(turn["anchor"])}')
        if turn['reply_to'] is not None:result.append(f'{REPLY} {name(turn["reply_to"])}')
        result.append(turn['utterance']);result.append(END)
    text='\n'.join(result)+'\n'
    if parse_transcript(text)!=doc:fail('E_V13_ROUNDTRIP','semantic fields not reconstructable')
    return text


def interpret_transcript(doc:dict)->list[dict]:
    render_transcript(doc)
    rows=[]
    for t in doc['turns']:
        ref=t['reference']
        rows.append({'id':t['id'],'reported_speaker':t['speaker'],
                     'reported_addressee':t['audience'],'reply_to':t['reply_to'],
                     'third_person_resolution':ref['status'],'candidates':ref['candidates'],
                     'referent':ref['chosen'],
                     'structured_parse_available':ref['expression_ast'] is not None,
                     'identity_authenticated':False,'authorizes':False,
                     'warning':'Reference claims and linguistic permissions are not externally verified.'})
    return rows

if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('file')
    args=cli.parse_args()
    obj=parse_transcript(open(args.file,encoding='utf-8').read())
    print(json.dumps(interpret_transcript(obj),indent=2))
