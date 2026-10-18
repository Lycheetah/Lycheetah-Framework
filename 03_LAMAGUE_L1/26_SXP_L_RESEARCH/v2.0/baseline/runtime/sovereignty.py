"""SXP-L 1.0 controlled linguistic register: trust and human sovereignty.

The parser records attributed speech acts, not permissions, identities, true
mental states, or policy outcomes. No tool execution. Language is text with
whitespace boundaries, not speech recognition.

Earlier 0.9 expressions (including all legacy forms) are preserved verbatim
as legacy_v09. Explicitly avoid translating trust or a request for advice
into a capability grant.
"""
from __future__ import annotations
import json
from sxpl_v03 import SXPError
from consent import parse_expression as parse_v09, render_expression as render_v09
from consent import _entity
from pragmatics import _render_actor
from spoken import spoken_tokens, syllables, confusable_pairs, WORDS, lev
from pragmatics import ACT_ROOTS, NEW_PREDICATES, CONDITIONAL
from consent import SPEECH_ROOTS, ACTION_ROOTS, ACTIONS_ROOT

VERSION = '1.0.0'
REGISTER = 'sovereignty_spoken_script'
# Controlled meaning. These are provisional new vocabulary, NOT Native-36 IDs.
ACTS = {
    'tinora': 'trust_report',
    'dalora': 'delegation_proposal',
    'resama': 'delegation_refusal',
    'esaloma': 'explanation_request',
    'ranova': 'recommendation_request',
    'domera': 'decision_reservation',
}
REVERSE = {v:k for k,v in ACTS.items()}
OLD_VOCAB=set(WORDS)|set(ACT_ROOTS)|set(NEW_PREDICATES)|set(CONDITIONAL)|set(SPEECH_ROOTS)|set(ACTION_ROOTS)
for word in ACTS:syllables(word)
assert not confusable_pairs(1,tuple(ACTS))
assert all(lev(new,old)>1 for new in ACTS for old in OLD_VOCAB)


def fail(code, detail=''):
    raise SXPError(code,detail)


def _new_node(words):
    if len(words)<7 or words[0]!='mi' or words[1] not in ACTS:
        fail('E_V10_ACT','expected first-person v1.0 speech act')
    kind=ACTS[words[1]]
    target,i=_entity(words,2,'grantee')
    if kind=='decision_reservation' and target!='mi':
        fail('E_V10_DECISION','final decision reservation must name the reporting speaker')
    if i>=len(words) or words[i]!='bakumo':fail('E_V10_FRAME','missing bakumo')
    i+=1
    from consent import ACTION_ROOTS
    if i>=len(words) or words[i] not in ACTION_ROOTS:fail('E_V10_ACTION','unknown task action')
    action=ACTION_ROOTS[words[i]]
    resource,j=_entity(words,i+1,'resource')
    if j!=len(words)-1 or words[j]!='tesavo':
        fail('E_V10_FRAME','missing tesavo or surplus tokens')
    return {'kind':kind,'reporter':'mi','counterparty':target,'action':action,
            'resource':resource,'epistemic_status':'unverified_utterance'}


def parse_expression(text):
    try:
        old=parse_v09(text)
        return {'lang':'SXP-L','schema':VERSION,'register':REGISTER,
                'node':{'kind':'legacy_v09','content':old}}
    except SXPError:
        pass
    words=spoken_tokens(text)
    if not words or words[-1]!='devora' or 'devora' in words[:-1] or 'kevonu' in words:
        fail('E_V10_END','new acts are declarative reports only')
    return {'lang':'SXP-L','schema':VERSION,'register':REGISTER,
            'node':_new_node(words[:-1])}


def render_expression(doc):
    if not isinstance(doc,dict) or set(doc)!={'lang','schema','register','node'} or \
        doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!=REGISTER:
        fail('E_V10_SCHEMA')
    n=doc['node']
    if not isinstance(n,dict):fail('E_V10_AST','non-object node')
    if n.get('kind')=='legacy_v09':
        if set(n)!={'kind','content'}:fail('E_V10_AST','legacy fields')
        result=render_v09(n['content'])
    else:
        if set(n)!={'kind','reporter','counterparty','action','resource','epistemic_status'} or \
            n['kind'] not in REVERSE or n['reporter']!='mi' or \
            n['epistemic_status']!='unverified_utterance' or n['action'] not in ACTIONS_ROOT or \
            n['resource'] in ('mi','ti'):
            fail('E_V10_AST','invalid speech report')
        if n['kind']=='decision_reservation' and n['counterparty']!='mi':
            fail('E_V10_AST','decision holder must be mi')
        try:
            target=_render_actor(n['counterparty']);resource=_render_actor(n['resource'])
        except (KeyError, TypeError, AttributeError):
            fail('E_V10_AST','entity type')
        result=f'mi {REVERSE[n["kind"]]} {target} bakumo {ACTIONS_ROOT[n["action"]]} {resource} tesavo devora'
    if parse_expression(result)!=doc:fail('E_V10_AST','semantic round trip mismatch')
    return result


def interpret(doc):
    # Verify canonical AST before interpretation; avoid treating caller JSON as trusted.
    render_expression(doc)
    n=doc['node']
    if n['kind']=='legacy_v09':
        return {'kind':'legacy_expression','authorizes':False,
                'boundary':'All legacy speech is unverified language; consult trusted host policy.'}
    return {'kind':n['kind'],'scope':{'operation':n['action'],'resource':n['resource']},
            'speaker_reported':True,'authorizes':False,
            'boundary':'Speech reports do not authenticate identity or grant authority.'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('words',nargs='+')
    a=p.parse_args();d=parse_expression(' '.join(a.words))
    print(json.dumps(d,indent=2));print('normalized:',render_expression(d));print(json.dumps(interpret(d),indent=2))
