"""SXP-L v0.4: fully reversible spoken-friendly controlled register.
This is not free-form natural-language translation. Text between double quotes is a literal.
"""
import json
from sxpl_v03 import parse,render,ROLES,WORDS,MODS,TIMES,OPERATIONS,RESERVED,SXPError,tokens

TO_HUMAN={
 'sa':'sava','qu':'qira','di':'dira','no':'noka',
 'ma':'mira','mu':'mura','pa':'pana','nu':'nura','fu':'fura',
 'ka':'ami','ta':'tavi','lo':'lori','se':'seni','au':'auni',
 'sc':'sori','co':'cori','fe':'feli','re':'reli','vi':'viri','pr':'pari',
 'en':'ena','[':'nesti',']':'nesta','xi':'xira'
}
FROM_HUMAN={v:k for k,v in TO_HUMAN.items()}
assert len(FROM_HUMAN)==len(TO_HUMAN)
# Existing semantic labels, numbers and quoted strings are kept as literal content.
# Protocol requires role markers and operators to remain distinct from reserved words.

def speak(canonical_source):
    """Render canonical AST to a controlled, human-pronounceable register."""
    normalized=render(parse(canonical_source))
    out=[]
    for t in tokens(normalized):
        if t in TO_HUMAN:out.append(TO_HUMAN[t])
        else:out.extend(['nami',t])  # explicit content marker prevents collisions
    return ' '.join(out)

def hear(human_source):
    """Parse only the explicit controlled register; no English or fuzzy guessing."""
    ts=tokens(human_source); out=[]; i=0
    while i<len(ts):
        t=ts[i]
        if t=='nami':
            if i+1>=len(ts):raise SXPError('E_SURFACE_VALUE')
            out.append(ts[i+1]);i+=2
        elif t in FROM_HUMAN:
            out.append(FROM_HUMAN[t]);i+=1
        else:
            raise SXPError('E_SURFACE_TOKEN',t)
    return render(parse(' '.join(out)))

def meaning_equal(a,b):
    return parse(a)==parse(b)

if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser();cli.add_argument('mode',choices=['speak','hear']);cli.add_argument('text',nargs='+');args=cli.parse_args()
    print((speak if args.mode=='speak' else hear)(' '.join(args.text)))
