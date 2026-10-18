"""SXP-L v0.9: speakable *reports* of permission, request, denial or revocation.

IMPORTANT: parsed text never constitutes verified authority. The authorization
module consumes independently attested capabilities, not these speech acts.
This is a typed text grammar, not speech recognition or a general NL parser.
"""
from __future__ import annotations
from sxpl_v03 import SXPError
from spoken import spoken_tokens, syllables, WORDS, confusable_pairs
from pragmatics import parse_expression as parse_v08, render_expression as render_v08
from pragmatics import _subject, _render_actor

VERSION = '0.9.0'
SPEECH_ROOTS = {'periva': 'grant_report', 'pekora': 'permission_request',
                'nelora': 'denial_report', 'revona': 'revocation_report'}
ROOTS_SPEECH = {v: k for k, v in SPEECH_ROOTS.items()}
ACTION_ROOTS = {'mesara': 'send_email', 'lenova': 'read_file',
                'rekova': 'delete_file', 'sotira': 'schedule_event',
                'tavona': 'publish_post'}
ACTIONS_ROOT = {v: k for k, v in ACTION_ROOTS.items()}
# All new vocabulary adheres to the inherited CV phonology and is separately screened.
assert len(ROOTS_SPEECH) == len(SPEECH_ROOTS)
assert len(ACTIONS_ROOT) == len(ACTION_ROOTS)
for root in (*SPEECH_ROOTS, *ACTION_ROOTS): syllables(root)
assert not confusable_pairs(0, (*SPEECH_ROOTS, *ACTION_ROOTS))


def fail(code, detail=''):
    raise SXPError(code, detail)


def _entity(words, cursor, kind):
    if cursor >= len(words): fail('E_V09_ENTITY', 'truncated '+kind)
    text = words[cursor:]
    if text[0] in ('mi', 'ti'):
        if kind == 'resource': fail('E_V09_RESOURCE', 'resource requires stable identifier')
        return text[0], cursor + 1
    if text[0] == 'gonape':
        span = text[:3]
    elif text[0] == 'pulako':
        try: end = text.index('sanuti', 1)
        except ValueError: fail('E_V09_ENTITY', 'missing sanuti')
        span = text[:end+1]
    else:
        fail('E_V09_ENTITY', 'expected framed name or pronoun')
    identifier, used = _subject(span)
    if used != len(span) or identifier in ('mi', 'ti'):
        fail('E_V09_ENTITY', 'ambiguous entity')
    return identifier, cursor+len(span)


def _parse_permission(words):
    if not words or words[0] != 'mi':
        fail('E_V09_SOURCE', 'speaker must be mi: reported first-person speech act')
    if len(words) < 7 or words[1] not in SPEECH_ROOTS:
        fail('E_V09_ROOT', 'unrecognized speech act')
    kind = SPEECH_ROOTS[words[1]]
    grantee, i = _entity(words, 2, 'grantee')
    if i >= len(words) or words[i] != 'bakumo': fail('E_V09_FRAME', 'missing bakumo')
    i += 1
    if i >= len(words) or words[i] not in ACTION_ROOTS:
        fail('E_V09_ACTION', 'unknown allowed action')
    action = ACTION_ROOTS[words[i]]
    resource, i = _entity(words, i+1, 'resource')
    if i != len(words)-1 or words[i] != 'tesavo':
        fail('E_V09_FRAME', 'missing tesavo or unexpected extra words')
    return {'kind': kind, 'reporter':'mi', 'grantee':grantee,
            'action':action, 'resource':resource, 'epistemic_status':'unverified_utterance'}


def parse_expression(text):
    # The earlier grammar has priority: new roots cannot reinterpret old utterances.
    try:
        old = parse_v08(text)
        return {'lang':'SXP-L','schema':VERSION,'register':'consent_spoken_script',
                'node':{'kind':'legacy_v08','content':old}}
    except SXPError:
        pass
    words = spoken_tokens(text)
    if not words or words[-1] != 'devora' or 'devora' in words[:-1] or 'kevonu' in words:
        fail('E_V09_END', 'new speech acts are declarative utterance reports only')
    node = _parse_permission(words[:-1])
    return {'lang':'SXP-L','schema':VERSION,'register':'consent_spoken_script','node':node}


def render_expression(doc):
    if not isinstance(doc, dict) or set(doc) != {'lang','schema','register','node'} or \
            doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!='consent_spoken_script':
        fail('E_V09_SCHEMA')
    n = doc['node']; kind = n.get('kind')
    if kind == 'legacy_v08':
        result = render_v08(n['content'])
    else:
        if set(n) != {'kind','reporter','grantee','action','resource','epistemic_status'} or \
                kind not in ROOTS_SPEECH or n['reporter']!='mi' or n['epistemic_status']!='unverified_utterance':
            fail('E_V09_AST','invalid report schema')
        if n['action'] not in ACTIONS_ROOT or n['resource'] in ('mi','ti'):
            fail('E_V09_AST','invalid action or resource')
        grantee = _render_actor(n['grantee'])
        resource = _render_actor(n['resource'])
        result = f'mi {ROOTS_SPEECH[kind]} {grantee} bakumo {ACTIONS_ROOT[n["action"]]} {resource} tesavo devora'
    if parse_expression(result) != doc: fail('E_V09_AST', 'round-trip mismatch')
    return result


def interpret(doc):
    n=doc['node']
    if n['kind']=='legacy_v08':
        return {'event_type':'legacy_expression','authorizes':False,
                'reason':'Earlier attitudes, promises and directives are not authorizations.'}
    return {'event_type':n['kind'],'speaker_reported':True,'authorizes':False,
            'action':n['action'],'resource':n['resource'],
            'reason':'Words alone cannot authenticate identity, authority, scope or revocation.'}


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('text',nargs='+');a=p.parse_args()
    d=parse_expression(' '.join(a.text))
    print(json.dumps(d,indent=2));print('normalized:',render_expression(d))
    print(json.dumps(interpret(d),indent=2))
