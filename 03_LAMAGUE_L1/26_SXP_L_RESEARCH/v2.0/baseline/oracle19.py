"""Independent LIMITED lexical reader for the new v1.9 binder subset.
No imports from reference19 or historical parser, and no claim to parse arbitrary v1.8.
"""
import re
TURN=re.compile(r'^([a-z]+) > ([a-z]+) : (.+)$')
FRAME=re.compile(r'^mi kelunaro gonape ([a-z]+) dimotu bakumo (soraviko|tumerako) (.+) tesavo devora$')
# Fixed independent reference-ID table for the bounded 1–35-turn study.
from_text='''taba tabe tabi tabo tabu tada tade tadi tado tadu tafa tafe tafi tafo tafu taga tage tagi tago tagu taka take taki tako taku tama tame tami tamo tamu tana tane tani tano tanu'''
IDS=from_text.split()

def entity(words,i):
    if i>=len(words):raise ValueError('missing role')
    if words[i] in ('mi','ti'):return words[i],i+1
    if words[i]=='gonape' and i+2<len(words) and words[i+2]=='dimotu':return words[i+1],i+3
    raise ValueError('bad participant')

def read(text):
    lines=text.strip().splitlines()
    head=lines[0].split()
    if head[0]!='people':raise ValueError('bad header')
    names=head[1:];roles=[];bindings=[]
    for i,line in enumerate(lines[1:],1):
        speaker,audience,sentence=TURN.fullmatch(line).groups()
        match=FRAME.fullmatch(sentence)
        if match:
            ref,marker,content=match.groups()
            if ref not in IDS[:i-1]:raise ValueError('unknown target')
            n=IDS.index(ref)+1
            orig=roles[n-1]
            words=content.split()
            s,p=entity(words,0)
            verb=words[p]
            o,p=entity(words,p+1)
            if verb not in ('liva','luma','rava') or words[p:]!=['devora']:raise ValueError('unsupported content')
            view=orig if marker=='soraviko' else (speaker,audience)
            subj=view[0] if s=='mi' else view[1] if s=='ti' else s
            obj=view[0] if o=='mi' else view[1] if o=='ti' else o
            bindings.append({'turn':i,'reference_turn':n,'frame':marker,'bound_mi':view[0],
                             'bound_ti':view[1],'subject':subj,'verb':verb,'object':obj})
        roles.append((speaker,audience))
    return bindings
