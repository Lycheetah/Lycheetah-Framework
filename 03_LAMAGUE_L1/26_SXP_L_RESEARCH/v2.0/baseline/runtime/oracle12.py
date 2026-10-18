"""Restricted second reader for SXP-L v1.2.

Independent of discourse12/discourse11 and their renderers, but shares
written rules with them. Handles only oracle11's small action/love subset;
not a proof of general semantics or a human study.
"""
from oracle11 import (lex, entity, frame, act, OracleReject, OracleUnsupported)

BECAUSE='larumeko'
THEREFORE='voraneku'
INDIRECT='nimareko'


def parse(text: str):
    words = lex(text)
    if len(words) < 6 or words[0] != 'mi' or words[-1] != 'devora':
        raise OracleReject('invalid outer utterance')
    root = words[1]
    if root in (BECAUSE, THEREFORE):
        first, pos = frame(words, 2)
        second, pos = frame(words, pos)
        if words[pos:] != ['devora']:
            raise OracleReject('unexpected trailing words')
        first_sig, second_sig = act(first), act(second)
        cause, effect = ((second_sig, first_sig) if root == BECAUSE
                         else (first_sig, second_sig))
        return ('directed', 'mi', 'because' if root == BECAUSE else 'therefore',
                cause, effect, 'speaker_supplied_unverified', False)
    if root == INDIRECT:
        source, pos = entity(words, 2)
        contents, pos = frame(words, pos)
        if words[pos:] != ['devora']:
            raise OracleReject('unexpected trailing words')
        return ('indirect', 'mi', source, act(contents),
                'paraphrase_not_verbatim', False)
    raise OracleUnsupported('outside oracle12 coverage')
