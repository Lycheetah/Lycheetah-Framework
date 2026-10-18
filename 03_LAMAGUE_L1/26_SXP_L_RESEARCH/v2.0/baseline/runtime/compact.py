"""SXP-L 0.6 compact conversational register (strict, intentionally bounded).

No inference, translation from English, speech recognition, or execution.
Grammar is positional/valency-based. Ambiguous input fails closed.
"""
from __future__ import annotations
import json
import re
import unicodedata
from roots import ROOTS, BACK
from sxpl_v03 import parse as parse_canonical, render as render_canonical, SXPError

# The new compact register is a strict subset of the v0.3 canonical AST.
# Noun syntax deliberately requires @ for named entities; grammar roots cannot
# masquerade as entities. This also makes 'mi' / 'ti' references unambiguous.
IDENT = re.compile(r'[a-z][a-z0-9_]{0,39}\Z')
LEX = re.compile(r'"(?:\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})|[^"\\\x00-\x1f])*"|@[a-z][a-z0-9_]{0,39}|[a-z][a-z0-9_]*|[().?]')
TRANSITIVE = {'love','miss','reconnect','understand','see','arrive','remember','differ'}
ATTITUDE = {'hope','believe','know','fear'}
FEELING = {'longing','affection','joy','fear','sadness','hope'}
FEEL_ROOTS = {ROOTS[x]:x for x in FEELING}
TIMES = {'pana':'pa','nura':'nu','fura':'fu'}
MODALS = {'mira':'ma','mura':'mu'}
MOODS = {'sava':'sa','qira':'qu','dira':'di'}
REV_TIMES={"past":"pana","present":"nura","future":"fura"}
REV_MODALS={"possible":"mira","obligation":"mura"}
REV_MOODS={"assert":"sava","question":"qira","directive":"dira"}
MAX_CHARS=16000
MAX_DEPTH=8
MAX_TOKENS=4096


def fail(code, detail=''):
    raise SXPError(code, detail)


def lex(source):
    if not isinstance(source,str) or not source or len(source)>MAX_CHARS:
        fail('E_COMPACT_LIMIT','empty / non-string / >16000')
    result=[]; pos=0
    for m in LEX.finditer(source):
        if source[pos:m.start()].strip(): fail('E_COMPACT_LEX',source[pos:m.start()][:50])
        result.append(m.group());pos=m.end()
    if source[pos:].strip():fail('E_COMPACT_LEX',source[pos:][:50])
    if len(result)>MAX_TOKENS:fail('E_COMPACT_LIMIT','tokens')
    return result


def entity(token):
    if token in ('mi','ti'):return token
    if token.startswith('@') and IDENT.fullmatch(token[1:]) and token[1:] not in ('mi','ti','none'):
        return token[1:]
    fail('E_COMPACT_ENTITY',token)


def quote(token):
    if not token.startswith('"'):fail('E_COMPACT_CONTEXT',token)
    try:
        value=json.loads(token)
    except (ValueError,TypeError):fail('E_COMPACT_CONTEXT',token)
    if not isinstance(value,str) or unicodedata.normalize('NFC',value)!=value:fail('E_COMPACT_CONTEXT','not NFC')
    return json.dumps(value,ensure_ascii=False)


class Parser:
    def __init__(self,tokens):self.ts=tokens;self.i=0
    def peek(self):return self.ts[self.i] if self.i<len(self.ts) else None
    def take(self):
        if self.peek() is None:fail('E_COMPACT_EOF')
        v=self.peek();self.i+=1;return v
    def want(self,x):
        got=self.take()
        if got!=x:fail('E_COMPACT_EXPECT',f'{x}: got {got}')

    def clause(self,depth=0):
        if depth>MAX_DEPTH:fail('E_COMPACT_DEPTH')
        mood='sa';modal=None;time='nu';neg=False
        if self.peek() in MOODS:mood=MOODS[self.take()]
        if self.peek() in MODALS:modal=MODALS[self.take()]
        if self.peek() in TIMES:time=TIMES[self.take()]
        actor=entity(self.take())
        if self.peek()=='noka':self.take();neg=True
        root=self.take()
        if root not in BACK:fail('E_COMPACT_ROOT',root)
        predicate=BACK[root]
        parts=[mood]
        if neg:parts.append('no')
        if modal:parts.append(modal)
        parts.extend([time,predicate,'ka',actor])
        if predicate in TRANSITIVE:
            parts.extend(['ta',entity(self.take())])
        elif predicate=='feel':
            feeling=self.take()
            if feeling not in FEEL_ROOTS:fail('E_COMPACT_FEELING',feeling)
            parts.extend(['fe',FEEL_ROOTS[feeling]])
            if self.peek() in {'mi','ti'} or (self.peek() or '').startswith('@'):
                parts.extend(['ta',entity(self.take())])
        elif predicate in ATTITUDE:
            self.want('(')
            sub=self.clause(depth+1)
            self.want(')')
            parts.extend(['pr','[',*sub,']'])
        else:fail('E_COMPACT_VALENCY',predicate)
        if self.peek()=='lo':
            self.take();parts.extend(['lo',quote(self.take())])
        parts.append('en')
        return parts


def hear_compact(source):
    """Compact -> v0.3 canonical string; defaults are explicit in the AST."""
    p=Parser(lex(source))
    clause=p.clause()
    punctuation=p.take()
    expected='?' if clause[0]=='qu' else '.'
    if punctuation!=expected:fail('E_COMPACT_PUNCT',f'expected {expected} got {punctuation}')
    if p.peek() is not None:fail('E_COMPACT_TRAILING',p.peek())
    return render_canonical(parse_canonical(' '.join(clause)))


def _actor(v):
    if not isinstance(v,dict) or v.get('type')!='symbol':fail('E_COMPACT_UNSUPPORTED','entity type')
    x=v['value']
    if x in ('mi','ti'):return x
    if not isinstance(x,str) or not IDENT.fullmatch(x) or x in ('none',):fail('E_COMPACT_UNSUPPORTED','entity name')
    return '@'+x


def _compose(c,depth=0):
    if depth>MAX_DEPTH:fail('E_COMPACT_DEPTH')
    if c['time'] not in REV_TIMES or c['modality'] not in (None,*REV_MODALS) or c['mood'] not in REV_MOODS:
        fail('E_COMPACT_UNSUPPORTED','tense / modality / mood')
    if not c['op'].startswith('USR:') or c['op'][4:] not in ROOTS:
        fail('E_COMPACT_UNSUPPORTED','unregistered predicate')
    pred=c['op'][4:]; roles=c['roles']
    permitted={'actor','context'}
    if pred in TRANSITIVE:permitted.add('target')
    elif pred=='feel':permitted.update(['feeling','target'])
    elif pred in ATTITUDE:permitted.add('proposition')
    else:fail('E_COMPACT_UNSUPPORTED','valency')
    if set(roles)-permitted or 'actor' not in roles:fail('E_COMPACT_UNSUPPORTED','roles')
    if 'context' in roles and roles['context'].get('type')!='string':fail('E_COMPACT_UNSUPPORTED','context')
    elements=[]
    if c['mood']!='assert':elements.append(REV_MOODS[c['mood']])
    if c['modality'] is not None:elements.append(REV_MODALS[c['modality']])
    if c['time']!='present':elements.append(REV_TIMES[c['time']])
    elements.append(_actor(roles['actor']))
    if c['polarity']=='negative':elements.append('noka')
    elements.append(ROOTS[pred])
    if pred in TRANSITIVE:
        if 'target' not in roles:fail('E_COMPACT_UNSUPPORTED','target required')
        elements.append(_actor(roles['target']))
    elif pred=='feel':
        f=roles.get('feeling')
        if not f or f.get('type')!='symbol' or f['value'] not in FEELING:
            fail('E_COMPACT_UNSUPPORTED','feeling')
        elements.append(ROOTS[f['value']])
        if 'target' in roles:elements.append(_actor(roles['target']))
    elif pred in ATTITUDE:
        p=roles.get('proposition')
        if not p or p.get('type')!='clause':fail('E_COMPACT_UNSUPPORTED','proposition')
        elements.extend(['(',*_compose(p['value'],depth+1),')'])
    if 'context' in roles:
        elements.extend(['lo',json.dumps(roles['context']['value'],ensure_ascii=False)])
    return elements


def speak_compact(canonical_source):
    """v0.3 canonical -> compact, or E_COMPACT_UNSUPPORTED if not safely representable."""
    ast=parse_canonical(canonical_source)
    c=ast['clause']
    tokens=_compose(c)
    text=' '.join(tokens)+('?' if c['mood']=='question' else '.')
    # No encode output without a proven exact AST round trip.
    if parse_canonical(hear_compact(text))!=ast:fail('E_COMPACT_UNSUPPORTED','round-trip check')
    return text


def meaning_equal(canonical,compact):
    return parse_canonical(canonical)==parse_canonical(hear_compact(compact))


if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('mode',choices=['hear','speak']);cli.add_argument('text',nargs='+')
    args=cli.parse_args()
    print((hear_compact if args.mode=='hear' else speak_compact)(' '.join(args.text)))
