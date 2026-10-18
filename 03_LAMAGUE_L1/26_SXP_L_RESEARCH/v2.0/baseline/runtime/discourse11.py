"""SXP-L 1.1 experimental *reported* quotation and speaker-asserted relations.

This is NOT a translator, audio recognizer, authentication service or a tool executor.
The quoted clause is represented as mentioned language, NOT enacted language.
Quotation is lexically faithful at the normalized word-token level only.
The implementation deliberately supports single-level quotations of v1.0
expressions rather than guessing about nested quotation/scopes.
"""
from __future__ import annotations

import json
from sxpl_v03 import SXPError
from spoken import spoken_tokens, syllables, lev, WORDS
from sovereignty import parse_expression as parse_v10, render_expression as render_v10
from sovereignty import ACTS, OLD_VOCAB
from consent import SPEECH_ROOTS, ACTION_ROOTS, _entity
from pragmatics import _render_actor

VERSION = '1.1.0'
REGISTER = 'attributed_discourse_spoken_script'
QUOTE = 'kavira'
RELATION = {'kasora': 'contrast_report', 'borema': 'causal_claim_report'}
RELATION_BACK = {v: k for k, v in RELATION.items()}
NEW = frozenset({QUOTE, *RELATION})
ALL_OLD = set(OLD_VOCAB) | set(WORDS) | set(ACTS) | set(SPEECH_ROOTS) | set(ACTION_ROOTS)
for root in NEW:
    syllables(root)
    assert min(lev(root, old) for old in ALL_OLD) > 1
assert all(lev(a, b)>1 for a in NEW for b in NEW if a != b)

# Bounded input and frames; each embedded sentence has its own termination word.
MAX_TOKENS = 4096
MAX_LITERAL_WORDS = 1500


def fail(code: str, detail: str = ''):
    raise SXPError(code, detail)


def _inner(words: list[str], start: int) -> tuple[str, int]:
    """Consume a `bakumo` framed expression, counting nested lexical boundaries."""
    if start >= len(words) or words[start] != 'bakumo':
        fail('E_V11_FRAME', 'expected bakumo')
    depth = 1
    cursor = start + 1
    body = []
    while cursor < len(words):
        word = words[cursor]
        cursor += 1
        if word == 'bakumo':
            depth += 1
        elif word == 'tesavo':
            depth -= 1
            if depth == 0:
                if not body: fail('E_V11_EMPTY', 'empty embedded speech')
                if len(body) > MAX_LITERAL_WORDS:
                    fail('E_V11_LIMIT', 'embedded expression length')
                return ' '.join(body), cursor
            if depth < 0:
                fail('E_V11_FRAME', 'extra close marker')
        body.append(word)
    fail('E_V11_FRAME', 'unterminated embedded expression')


def _parse_new(words: list[str]) -> dict:
    if len(words) < 7 or words[0] != 'mi' or words[-1] != 'devora':
        fail('E_V11_FORM', 'expected first-person discourse report')
    root = words[1]
    if root == QUOTE:
        source, pos = _entity(words, 2, 'source')
        literal, pos = _inner(words, pos)
        if pos != len(words)-1:
            fail('E_V11_TRAILING', 'tokens after quotation')
        embedded = parse_v10(literal)
        # v1.0 normalizes supported written forms; preserve normalized *tokens*.
        if render_v10(embedded) != literal:
            fail('E_V11_CANON', 'quoted tokens must be canonical v1.0 surface')
        return {'kind': 'attributed_quote', 'reporter': 'mi',
                'source': source, 'quoted_words': literal,
                'quoted_ast': embedded, 'attribution_status': 'unverified_report',
                'quoted_mi_binding': 'quoted_source_not_reporter',
                'authorizes': False}
    if root in RELATION:
        left, pos = _inner(words, 2)
        right, pos = _inner(words, pos)
        if pos != len(words)-1:
            fail('E_V11_TRAILING', 'tokens after reported relation')
        lnode = parse_v10(left)
        rnode = parse_v10(right)
        if render_v10(lnode) != left or render_v10(rnode) != right:
            fail('E_V11_CANON', 'linked clauses must be canonical')
        return {'kind': 'speaker_relation', 'reporter': 'mi',
                'relation': RELATION[root], 'left_words': left,
                'right_words': right, 'left_ast': lnode, 'right_ast': rnode,
                'relation_status': 'speaker_supplied_not_verified',
                'authorizes': False}
    fail('E_V11_ROOT', root)


def parse_expression(text: str) -> dict:
    words = spoken_tokens(text)
    if len(words)>MAX_TOKENS: fail('E_V11_LIMIT', 'token bound')
    if len(words) >= 2 and words[:1] == ['mi'] and words[1] in NEW:
        node = _parse_new(words)
    else:
        node = {'kind': 'legacy_v10', 'content': parse_v10(text)}
    return {'lang': 'SXP-L', 'schema': VERSION, 'register': REGISTER, 'node': node}


def _validate_ast(node: dict):
    if not isinstance(node, dict): fail('E_V11_AST', 'non-object node')
    kind = node.get('kind')
    if kind == 'legacy_v10':
        if set(node) != {'kind', 'content'}: fail('E_V11_AST', 'legacy keys')
        result = render_v10(node['content'])
    elif kind == 'attributed_quote':
        expected={'kind','reporter','source','quoted_words','quoted_ast',
                  'attribution_status','quoted_mi_binding','authorizes'}
        if set(node)!=expected or node['reporter']!='mi' or \
           node['attribution_status']!='unverified_report' or \
           node['quoted_mi_binding']!='quoted_source_not_reporter' or node['authorizes'] is not False:
            fail('E_V11_AST', 'invalid quotation metadata')
        try: source = _render_actor(node['source'])
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            fail('E_V11_AST', str(exc))
        literal = render_v10(node['quoted_ast'])
        if literal != node['quoted_words']:
            fail('E_V11_AST', 'quote words and AST disagree')
        result = f'mi {QUOTE} {source} bakumo {literal} tesavo devora'
    elif kind == 'speaker_relation':
        expected={'kind','reporter','relation','left_words','right_words','left_ast',
                  'right_ast','relation_status','authorizes'}
        if set(node)!=expected or node['reporter']!='mi' or \
           node['relation'] not in RELATION_BACK or \
           node['relation_status']!='speaker_supplied_not_verified' or node['authorizes'] is not False:
            fail('E_V11_AST','invalid relation metadata')
        left=render_v10(node['left_ast']); right=render_v10(node['right_ast'])
        if left!=node['left_words'] or right!=node['right_words']:
            fail('E_V11_AST','relation words and AST disagree')
        result=f'mi {RELATION_BACK[node["relation"]]} bakumo {left} tesavo bakumo {right} tesavo devora'
    else:
        fail('E_V11_AST', 'unknown kind')
    return result


def render_expression(doc: dict) -> str:
    if not isinstance(doc,dict) or set(doc) != {'lang','schema','register','node'} or \
        doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!=REGISTER:
        fail('E_V11_SCHEMA', 'wrong schema or surplus fields')
    rendered=_validate_ast(doc['node'])
    if parse_expression(rendered)!=doc:
        fail('E_V11_ROUNDTRIP', 'non-reversible AST')
    return rendered


def interpret(doc: dict) -> dict:
    """Information-only interpretation. All quoted/linked speech is inert."""
    render_expression(doc)
    node = doc['node']
    if node['kind']=='attributed_quote':
        return {'kind': 'attributed_quote', 'reported_source': node['source'],
                'quoted_mi_refers_to': node['source'],
                'reported_contents_are_verified': False, 'authorizes': False,
                'quoted_words': node['quoted_words'],
                'warning': 'Mention of a purported permission or instruction never authenticates it.'}
    if node['kind']=='speaker_relation':
        return {'kind': node['relation'], 'relation_is_fact': False,
                'authorizes': False, 'warning': 'A speaker-supplied causal link is not causal evidence.'}
    return {'kind': 'legacy_utterance', 'authorizes': False,
            'warning': 'For legacy reported speech, consult the separate trusted policy gate.'}


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('words',nargs='+')
    d=parse_expression(' '.join(p.parse_args().words))
    print(json.dumps(d,ensure_ascii=False,indent=2))
    print('normalized:',render_expression(d))
    print(json.dumps(interpret(d),ensure_ascii=False,indent=2))
