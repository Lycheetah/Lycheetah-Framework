"""Optional v0.5 draft lexical register. Pronounceable roots; not final phonology.

Only predicates and typed feelings are eligible for root mapping. This avoids
mistaking a participant *named* "hope" for the lexical predicate "hope".
"""
from sxpl_v03 import tokens, SXPError
from surface import speak, hear

# Draft roots (new v0.5 conventions, NOT legacy LAMAGUE / Native-36 IDs).
ROOTS = {
    'believe':'vela', 'know':'kena', 'hope':'hira', 'miss':'luma',
    'reconnect':'rava', 'feel':'fela', 'understand':'nela',
    'love':'liva', 'longing':'loma', 'affection':'afela',
    'joy':'yora', 'fear':'fera', 'sadness':'sada',
    'see':'siva', 'arrive':'ariva', 'remember':'mora',
    'differ':'diva'
}
BACK={v:k for k,v in ROOTS.items()}
assert len(BACK)==len(ROOTS)
MOODS={'sava','qira','dira'}
PREFIX={'noka','mira','mura','pana','nura','fura'}


def _transform(stream, direction):
    """Recognize clause predicate positions and 'feli' values in v0.4 surface.

    The v0.4 hear() parser is still authoritative; this transforms only lexical
    markers. Bad root positions fail closed even if a noun happens to share a root.
    """
    out=[];i=0;predicate_pending=False;feeling_pending=False
    while i<len(stream):
        t=stream[i]
        if t in MOODS:
            predicate_pending=True;feeling_pending=False
            out.append(t);i+=1;continue
        if t=='feli':
            feeling_pending=True;out.append(t);i+=1;continue
        if t in {'nami','lami'}:
            if i+1>=len(stream):raise SXPError('E_ROOT_VALUE')
            val=stream[i+1]
            eligible=predicate_pending or feeling_pending
            if direction=='encode':
                if t!='nami':raise SXPError('E_ROOT_ENCODE')
                if eligible and val in ROOTS:
                    out.extend(['lami',ROOTS[val]])
                else:out.extend(['nami',val])
            else:
                if t=='lami':
                    if not eligible:raise SXPError('E_ROOT_POSITION',val)
                    if val not in BACK:raise SXPError('E_UNKNOWN_ROOT',val)
                    out.extend(['nami',BACK[val]])
                else:out.extend(['nami',val])
            predicate_pending=False;feeling_pending=False;i+=2;continue
        if predicate_pending and t not in PREFIX:
            # Canonical predicate *must* be prefixed with 'nami' or 'lami'.
            raise SXPError('E_ROOT_PREDICATE',t)
        if feeling_pending:
            raise SXPError('E_ROOT_FEELING',t)
        out.append(t);i+=1
    return ' '.join(out)


def speak_roots(canonical):
    return _transform(tokens(speak(canonical)),'encode')


def hear_roots(human):
    return hear(_transform(tokens(human),'decode'))
