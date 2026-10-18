"""SXP-L v1.2 experimental directed explanation and INDIRECT attribution.

NOT an English translator, a truth detector, an audio listener, or an action gate.
Explicit directional roles are speaker-supplied; they do not prove causation.
This extension leaves discourse11, v1.0, and older vocabulary unchanged.
"""
from __future__ import annotations

import json
from sxpl_v03 import SXPError
from spoken import spoken_tokens, syllables, lev
from discourse11 import (parse_expression as parse_v11,
                         render_expression as render_v11,
                         _inner, ALL_OLD, NEW as V11_NEW)
from sovereignty import parse_expression as parse_v10, render_expression as render_v10
from consent import _entity
from pragmatics import _render_actor

VERSION = '1.2.0'
REGISTER = 'directed_discourse_spoken_script'
# No 'jiva' alias or new spelling for 'liva': legacy language is immutable.
BECAUSE = 'larumeko'   # stated EFFECT, then stated CAUSE
THEREFORE = 'voraneku' # stated CAUSE, then stated EFFECT
INDIRECT = 'nimareko'  # indirect report: no claim of literal quoted words
NEW = frozenset((BECAUSE, THEREFORE, INDIRECT))
CAUSAL = {BECAUSE: 'because', THEREFORE: 'therefore'}
CAUSAL_BACK = {v: k for k, v in CAUSAL.items()}
MAX_TOKENS = 4096

for word in NEW:
    syllables(word)
    assert all(lev(word, x) > 1 for x in ALL_OLD | V11_NEW)
assert all(lev(a, b) > 1 for a in NEW for b in NEW if a != b)


def fail(code: str, message: str = '') -> None:
    raise SXPError(code, message)


def _parse_new(words: list[str]) -> dict:
    if len(words) < 7 or words[0] != 'mi' or words[-1] != 'devora':
        fail('E_V12_FORM', 'outer speaker + terminator required')
    root = words[1]
    if root in CAUSAL:
        first, pos = _inner(words, 2)
        second, pos = _inner(words, pos)
        if pos != len(words) - 1:
            fail('E_V12_TRAILING', 'extra tokens after causal frames')
        if root == BECAUSE:
            effect_words, cause_words = first, second
        else:
            cause_words, effect_words = first, second
        cause_ast = parse_v10(cause_words)
        effect_ast = parse_v10(effect_words)
        if render_v10(cause_ast) != cause_words or render_v10(effect_ast) != effect_words:
            fail('E_V12_CANON', 'embedded statements must be canonical v1.0 forms')
        return {'kind': 'directed_explanation', 'reporter': 'mi',
                'construction': CAUSAL[root],
                'cause_words': cause_words, 'effect_words': effect_words,
                'cause_ast': cause_ast, 'effect_ast': effect_ast,
                'connection_status': 'speaker_supplied_unverified',
                'authorizes': False}
    if root == INDIRECT:
        source, pos = _entity(words, 2, 'source')
        content_words, pos = _inner(words, pos)
        if pos != len(words) - 1:
            fail('E_V12_TRAILING', 'tokens after indirect report')
        content_ast = parse_v10(content_words)
        if render_v10(content_ast) != content_words:
            fail('E_V12_CANON', 'indirect representation must be canonical')
        return {'kind': 'indirect_report', 'reporter': 'mi', 'source': source,
                'content_ast': content_ast,
                'attribution_status': 'unverified_report',
                'wording_status': 'paraphrase_not_verbatim',
                'embedded_mi_binding': 'reported_source_not_reporter',
                'authorizes': False}
    fail('E_V12_ROOT', 'unknown root')


def parse_expression(text: str) -> dict:
    words = spoken_tokens(text)
    if len(words) > MAX_TOKENS:
        fail('E_V12_LIMIT', 'too many tokens')
    if len(words) > 1 and words[0] == 'mi' and words[1] in NEW:
        node = _parse_new(words)
    else:
        node = {'kind': 'legacy_v11', 'content': parse_v11(text)}
    return {'lang': 'SXP-L', 'schema': VERSION, 'register': REGISTER, 'node': node}


def _render_node(node: dict) -> str:
    if not isinstance(node, dict):
        fail('E_V12_AST', 'node is not an object')
    kind = node.get('kind')
    if kind == 'legacy_v11':
        if set(node) != {'kind', 'content'}:
            fail('E_V12_AST', 'legacy node has extra fields')
        return render_v11(node['content'])
    if kind == 'directed_explanation':
        keys = {'kind', 'reporter', 'construction', 'cause_words', 'effect_words',
                'cause_ast', 'effect_ast', 'connection_status', 'authorizes'}
        if set(node) != keys or node['reporter'] != 'mi' or \
           node['connection_status'] != 'speaker_supplied_unverified' or \
           node['authorizes'] is not False or node['construction'] not in CAUSAL_BACK:
            fail('E_V12_AST', 'invalid explanation metadata')
        cause = render_v10(node['cause_ast'])
        effect = render_v10(node['effect_ast'])
        if node['cause_words'] != cause or node['effect_words'] != effect:
            fail('E_V12_AST', 'clause representations disagree')
        if node['construction'] == 'because':
            first, second = effect, cause
        else:
            first, second = cause, effect
        return f'mi {CAUSAL_BACK[node["construction"]]} bakumo {first} tesavo bakumo {second} tesavo devora'
    if kind == 'indirect_report':
        keys = {'kind','reporter','source','content_ast','attribution_status',
                'wording_status','embedded_mi_binding','authorizes'}
        if set(node) != keys or node['reporter'] != 'mi' or \
           node['attribution_status'] != 'unverified_report' or \
           node['wording_status'] != 'paraphrase_not_verbatim' or \
           node['embedded_mi_binding'] != 'reported_source_not_reporter' or \
           node['authorizes'] is not False:
            fail('E_V12_AST', 'invalid indirect speech metadata')
        try:
            source = _render_actor(node['source'])
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            fail('E_V12_AST', str(exc))
        content = render_v10(node['content_ast'])
        return f'mi {INDIRECT} {source} bakumo {content} tesavo devora'
    fail('E_V12_AST', 'unsupported node kind')


def render_expression(doc: dict) -> str:
    if not isinstance(doc, dict) or set(doc) != {'lang', 'schema', 'register', 'node'} or \
       doc['lang'] != 'SXP-L' or doc['schema'] != VERSION or doc['register'] != REGISTER:
        fail('E_V12_SCHEMA', 'unexpected top-level schema')
    result = _render_node(doc['node'])
    if parse_expression(result) != doc:
        fail('E_V12_ROUNDTRIP', 'the AST cannot be reconstructed')
    return result


def interpret(doc: dict) -> dict:
    """Only a *reader*; no truth inference, ability grant or tool side effects."""
    render_expression(doc)  # fail closed on malformed or externally modified AST
    node = doc['node']
    if node['kind'] == 'directed_explanation':
        return {'kind': 'speaker_directed_explanation',
                'construction': node['construction'],
                'cause': node['cause_ast'], 'effect': node['effect_ast'],
                'causal_connection_verified': False, 'authorizes': False}
    if node['kind'] == 'indirect_report':
        return {'kind': 'indirect_report', 'source': node['source'],
                'reported_content': node['content_ast'],
                'literal_words_authenticated': False,
                'source_authenticated': False, 'authorizes': False}
    return {'kind': 'legacy_v11', 'authorizes': False,
            'warning': 'Language content alone never establishes an executable grant.'}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('words', nargs='+')
    obj = parse_expression(' '.join(p.parse_args().words))
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    print('canonical:', render_expression(obj))
    print(json.dumps(interpret(obj), indent=2, ensure_ascii=False))
