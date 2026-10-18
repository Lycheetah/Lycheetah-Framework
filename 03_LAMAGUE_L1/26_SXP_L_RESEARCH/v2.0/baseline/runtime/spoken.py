"""SXP-L v0.7 spoken-script codec and provisional pronunciation guide.

This is text representing carefully separated spoken words, NOT ASR or acoustic
word segmentation. Exact, bounded, reversible subset of v0.6 compact grammar.
Input is inert. No directives are executed.
"""
from __future__ import annotations
import re
from itertools import combinations
from compact import hear_compact, speak_compact, lex, IDENT
from sxpl_v03 import SXPError, parse as parse_canonical
from roots import ROOTS

# Spoken lexical aliases: older 0.6 spellings remain unchanged in compact form.
ALIASES = {'qira':'kesari', 'dira':'dutami', 'mira':'mopaku', 'mura':'tukemo'}
BACK_ALIASES = {v:k for k,v in ALIASES.items()}
# Spoken structural words have no punctuation; name/scope boundaries are explicit.
FRAMES = {
    '(':'bakumo', ')':'tesavo', '.':'devora', '?':'kevonu',
    'name_open':'gonape', 'name_close':'dimotu',
    'spell_open':'pulako', 'spell_close':'sanuti'
}
REVERSE_FRAMES={v:k for k,v in FRAMES.items()}
# Fixed pronounceable CV spelling codebook for a-z, 0-9, underscore.
SYMBOLS='abcdefghijklmnopqrstuvwxyz0123456789_'
SPELL_CODES=[c+v for c in 'bdfgkmnp' for v in 'aeiou']
SPELL={ch:SPELL_CODES[i] for i,ch in enumerate(SYMBOLS)}
UNSPELL={v:k for k,v in SPELL.items()}
assert len(set(SPELL.values()))==len(SYMBOLS)
SPOKEN_LIMIT=36000
MAX_WORDS=20000
# Provisional grapheme-to-phoneme model. 'r' is a tap, 'y' is /j/.
CONS={'b':'b','d':'d','f':'f','g':'ɡ','h':'h','k':'k','l':'l',
      'm':'m','n':'n','p':'p','r':'ɾ','s':'s','t':'t','v':'v','y':'j','z':'z'}
VOWELS={'a':'a','e':'e','i':'i','o':'o','u':'u'}
VALID_C=set(CONS)
VALID_V=set(VOWELS)
ALL_REGISTERED = set(ROOTS.values()) | {'mi','ti','sava','qira','dira','mira',
    'mura','pana','nura','fura','noka','lo'}
WORDS = (ALL_REGISTERED - set(ALIASES)) | set(ALIASES.values()) | set(FRAMES.values())


def fail(code,detail=''):
    raise SXPError(code,detail)


def syllables(word:str)->tuple[str,...]:
    """Parse strictly as (C)V repeated, with optional vowel-only syllables.

    This deliberately excludes non-CV proper names from literal pronunciation;
    spelling codes can still encode them without inventing foreign phonemes.
    """
    if not isinstance(word,str) or not re.fullmatch(r'[a-z]+',word):
        fail('E_PHONE_WORD',repr(word))
    pieces=[]; i=0
    while i<len(word):
        if word[i] in VALID_C:
            if i+1>=len(word) or word[i+1] not in VALID_V:
                fail('E_PHONE_SHAPE',word)
            pieces.append(word[i:i+2]);i+=2
        elif word[i] in VALID_V:
            pieces.append(word[i]);i+=1
        else:
            fail('E_PHONE_CHAR',word[i])
    if not pieces:fail('E_PHONE_WORD',word)
    return tuple(pieces)


def ipa(word:str)->str:
    syl=syllables(word)
    def render(s):return ''.join(CONS.get(x,VOWELS.get(x,'')) for x in s)
    if len(syl)==1:return render(syl[0])
    return '.'.join(('ˈ' if i==len(syl)-2 else '') +render(x) for i,x in enumerate(syl))


def is_literal_name(name:str)->bool:
    if not IDENT.fullmatch(name) or name in ('mi','ti','none') or name==FRAMES['name_close']:
        return False
    try:syllables(name)
    except SXPError:return False
    return True


def spoken_tokens(text:str)->list[str]:
    if not isinstance(text,str) or not text or len(text)>SPOKEN_LIMIT:
        fail('E_SPOKEN_LIMIT','empty or too long')
    # Actual acoustic word separation is NOT established by this input format.
    if not re.fullmatch(r'[a-z]+(?:\s+[a-z]+)*',text):
        fail('E_SPOKEN_LEX','words must be ASCII lowercase separated by whitespace')
    result=text.split()
    if len(result)>MAX_WORDS:fail('E_SPOKEN_LIMIT','too many words')
    return result


def speak_spoken(compact_text:str)->str:
    """Strict compact written form -> pronounceable textual speech register.

    Unsupported quoted strings fail rather than being lost. All names, including
    machine-style identifiers, are supported via framed CV character spelling.
    """
    try:
        # First require full compact syntactic/semantic validation.
        c=hear_compact(compact_text)
        normalized=speak_compact(c)
    except SXPError:
        raise
    out=[]
    for t in lex(normalized):
        if t.startswith('"') or t=='lo':
            fail('E_SPOKEN_QUOTE','opaque contexts have no v0.7 spoken encoding')
        if t.startswith('@'):
            name=t[1:]
            if is_literal_name(name):
                out.extend([FRAMES['name_open'],name,FRAMES['name_close']])
            else:
                out.extend([FRAMES['spell_open'],*(SPELL[x] for x in name),FRAMES['spell_close']])
        elif t in FRAMES:out.append(FRAMES[t])
        else:
            mapped=ALIASES.get(t,t)
            if mapped not in WORDS:fail('E_SPOKEN_UNKNOWN',mapped)
            syllables(mapped)
            out.append(mapped)
    result=' '.join(out)
    # Not merely printable: require an exact AST round trip.
    if parse_canonical(hear_spoken(result))!=parse_canonical(c):
        fail('E_SPOKEN_MISMATCH')
    return result


def hear_spoken(text:str)->str:
    """Spoken-script tokens -> canonical v0.3 clause with exact scoped meaning."""
    arr=spoken_tokens(text)
    out=[]; i=0
    while i<len(arr):
        w=arr[i];i+=1
        if w==FRAMES['name_open']:
            if i+1>=len(arr):fail('E_SPOKEN_FRAME','name truncated')
            name,close=arr[i:i+2];i+=2
            if close!=FRAMES['name_close'] or not is_literal_name(name):
                fail('E_SPOKEN_FRAME','bad literal-name frame')
            out.append('@'+name)
        elif w==FRAMES['spell_open']:
            pieces=[]
            while i<len(arr) and arr[i]!=FRAMES['spell_close']:
                sym=UNSPELL.get(arr[i])
                if sym is None:fail('E_SPOKEN_SPELL','unrecognized spelling syllable')
                pieces.append(sym);i+=1
                if len(pieces)>40:fail('E_SPOKEN_SPELL','identifier length')
            if i==len(arr):fail('E_SPOKEN_FRAME','unterminated spelled name')
            i+=1
            name=''.join(pieces)
            if not IDENT.fullmatch(name) or name in ('mi','ti','none'):
                fail('E_SPOKEN_SPELL','invalid identifier')
            out.append('@'+name)
        elif w in REVERSE_FRAMES:
            key=REVERSE_FRAMES[w]
            if key not in '().?':fail('E_SPOKEN_FRAME','unexpected delimiter')
            out.append(key)
        elif w in BACK_ALIASES:
            out.append(BACK_ALIASES[w])
        elif w in WORDS and w not in FRAMES.values():
            out.append(w)
        else:
            fail('E_SPOKEN_WORD',w)
    return hear_compact(' '.join(out))


def lev(a:str,b:str)->int:
    """Literal grapheme edit distance: exploratory screening, NOT perceptual risk."""
    row=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        new=[i]
        for j,cb in enumerate(b,1):
            new.append(min(new[-1]+1,row[j]+1,row[j-1]+(ca!=cb)))
        row=new
    return row[-1]


def confusable_pairs(max_edit=1,lexicon=None):
    words=sorted(lexicon if lexicon is not None else WORDS)
    return [(a,b,lev(a,b)) for a,b in combinations(words,2) if lev(a,b)<=max_edit]


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['say','hear','ipa','audit'])
    p.add_argument('text',nargs='*')
    a=p.parse_args(); s=' '.join(a.text)
    if a.mode=='say':print(speak_spoken(s))
    elif a.mode=='hear':print(hear_spoken(s))
    elif a.mode=='ipa':
        for w in spoken_tokens(s):print(f'{w:18s} {"-".join(syllables(w)):18s} /{ipa(w)}/')
    else:
        for x in confusable_pairs():print(*x)
