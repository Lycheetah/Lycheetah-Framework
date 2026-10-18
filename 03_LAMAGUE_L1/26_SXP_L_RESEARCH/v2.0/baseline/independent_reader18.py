"""Restricted independent v1.8 fixture reader; does not import repair18/studio17.

Only checks the two new outer repair forms and their turn linkage. It is not a
second full grammar or an independent human evaluation.
"""
import re
ID=re.compile(r'^t([aeiou])([bdfgkmnprstv])([aeiou])$')
ALPH='aeiou';CONS='bdfgkmnprstv'

def decode_ref(word):
    m=ID.fullmatch(word)
    if not m:return None
    ix=ALPH.index(m[1])*60+CONS.index(m[2])*5+ALPH.index(m[3])+1
    return ix if ix<=100 else None

def read(source):
    lines=[x for x in source.strip().splitlines() if x.strip()]
    if not lines or not lines[0].startswith('people '):raise ValueError('people')
    people=set(lines[0].split()[1:]);prev=[];audiences=[];out=[];corrected=set()
    for idx,line in enumerate(lines[1:],1):
        a=re.fullmatch(r'([a-z]+) > ([a-z]+) : (.+)',line)
        if a is None:raise ValueError('header')
        sp,addr,body=a.groups()
        if sp not in people or addr not in people or sp==addr:raise ValueError('roles')
        r=re.fullmatch(r'mi (kelunaro|remakivo) gonape (t[a-z]{3}) dimotu bakumo (.+) tesavo devora',body)
        if r:
            root,tid,leaf=r.groups();target=decode_ref(tid)
            if target is None or not 1<=target<idx:raise ValueError('ref')
            category='clarification_request' if root=='kelunaro' else 'self_correction'
            if category=='clarification_request' and prev[target-1]!=sp and addr==prev[target-1] and not any(w in {'mi','ti'} for w in leaf.split()):pass
            elif category=='self_correction' and prev[target-1]==sp and audiences[target-1]==addr and target not in corrected:corrected.add(target)
            else:raise ValueError('owner')
            if not leaf.endswith(' devora'):raise ValueError('leaf')
            out.append((category,target,sp,addr,leaf))
        else:
            if not body.endswith(' devora'):raise ValueError('leaf')
            out.append(('ordinary_utterance',None,sp,addr,body))
        prev.append(sp);audiences.append(addr)
    return out
