"""SXP-L v0.8: typed conversational expression layer over the v0.7 spoken codec.

This is a controlled *text* grammar, NOT speech recognition or an English
translator. Promise and capacity nodes record linguistic acts/reports; they do
NOT authorize effects, establish legal obligations, or prove mental states.
Unsupported meaning MUST fail, not be silently paraphrased.
"""
from __future__ import annotations
import copy
from sxpl_v03 import SXPError, parse as canonical_parse, render as canonical_render
from compact import speak_compact
from spoken import hear_spoken, speak_spoken, spoken_tokens

VERSION = '0.8.0'
MAX_DEPTH = 8
# The following are v0.8 *proposed* CV-form words, not inherited Native-36 IDs.
ACT_ROOTS = {'vanira':'desire', 'nivara':'intention', 'pamisa':'promise', 'kapera':'capacity_to_promise',
             'hira':'hope', 'fera':'fear', 'vela':'belief', 'kena':'knowledge_claim'}
REVERSE_ACT = {v:k for k,v in ACT_ROOTS.items()}
CONDITIONAL = ('sivane','tanaro') # if ... then ... (not truth of either branch)
NEW_PREDICATES = {'satoma':'stay'}


def fail(code, description=''):
    raise SXPError(code, description)


def _frame(words, cursor):
    """Read a balanced bakumo ... tesavo frame, preserving nested frames."""
    if cursor >= len(words) or words[cursor] != 'bakumo':
        fail('E_V08_FRAME','expected bakumo')
    depth=1; start=cursor+1; i=start
    while i<len(words):
        if words[i]=='bakumo':depth+=1
        elif words[i]=='tesavo':
            depth-=1
            if depth==0:
                if i==start: fail('E_V08_FRAME','empty frame')
                return words[start:i],i+1
        i+=1
    fail('E_V08_FRAME','unclosed bakumo')


def _subject(words):
    """Validate a framed entity with the established v0.7 codec."""
    if not words:fail('E_V08_ACTOR','missing')
    if words[0] in ('mi','ti'):return words[0],1
    if words[0]=='gonape':
        if len(words)<3 or words[2]!='dimotu':fail('E_V08_ACTOR','literal name frame')
        entity_tokens=words[:3]
    elif words[0]=='pulako':
        try:j=words.index('sanuti',1)
        except ValueError:fail('E_V08_ACTOR','spelled name frame')
        entity_tokens=words[:j+1]
    else:fail('E_V08_ACTOR',words[0])
    canonical=canonical_parse(hear_spoken(' '.join(entity_tokens+['liva','mi','devora'])))
    actor=canonical['clause']['roles']['actor']
    if actor['type']!='symbol':fail('E_V08_ACTOR','not symbol')
    return actor['value'],len(entity_tokens)


def _render_actor(actor):
    if actor in ('mi','ti'):return actor
    # Reuse the v0.7 name framing and spelling codec instead of inventing another.
    sample=canonical_render(canonical_parse(f'sa nu love ka {actor} ta mi en'))
    spoken=speak_spoken(speak_compact(sample)).split()
    if spoken[-3:]!=['liva','mi','devora']:fail('E_V08_ACTOR','framing')
    return ' '.join(spoken[:-3])


def _proposition(tokens):
    """Return canonical v0.3 AST for v0.7 proposition or v0.8 'stay'."""
    if not tokens or len(tokens)>4096:fail('E_V08_PROPOSITION','empty or limit')
    # Existing v0.7 syntax is authoritative when it accepts a proposition.
    try:
        old=canonical_parse(hear_spoken(' '.join(tokens+['devora'])))
        if old['clause']['mood']!='assert':fail('E_V08_PROPOSITION','assertions only')
        return old
    except SXPError:
        pass
    pos=0; time='nu'
    if tokens[0] in ('pana','nura','fura'):
        time={'pana':'pa','nura':'nu','fura':'fu'}[tokens[0]];pos+=1
    actor,n=_subject(tokens[pos:]);pos+=n
    negative=pos<len(tokens) and tokens[pos]=='noka'
    if negative:pos+=1
    if pos+1!=len(tokens) or tokens[pos]!='satoma':
        fail('E_V08_PROPOSITION','only v0.7 clauses or v0.8 unary satoma')
    canonical=f'sa {"no " if negative else ""}{time} stay ka {actor} en'
    return canonical_parse(canonical)


def _proposition_text(p):
    canonical=canonical_render(p)
    clause=p['clause']
    if clause['op']=='USR:stay':
        if clause['mood']!='assert' or clause['modality'] is not None or set(clause['roles'])!={'actor'}:
            fail('E_V08_UNSUPPORTED','stay clause features')
        a=clause['roles']['actor']
        if a['type']!='symbol':fail('E_V08_UNSUPPORTED','stay actor type')
        times={'past':'pana','present':'nura','future':'fura'}
        if clause['time'] not in times:fail('E_V08_UNSUPPORTED','stay time')
        return ' '.join(([times[clause['time']]] if clause['time']!='present' else []) +
                        [_render_actor(a['value'])] + (['noka'] if clause['polarity']=='negative' else [])+['satoma'])
    try:
        speech=speak_spoken(speak_compact(canonical))
    except SXPError as e:
        fail('E_V08_UNSUPPORTED',e.code)
    if not speech.endswith(' devora'):fail('E_V08_UNSUPPORTED','embedded question')
    return speech[:-7]


def _actor_of(p):
    val=p['clause']['roles'].get('actor')
    if not val or val['type']!='symbol':fail('E_V08_SCOPE','action actor missing')
    return val['value']


def _parse_node(words,depth):
    if depth>MAX_DEPTH:fail('E_V08_DEPTH')
    if not words:fail('E_V08_EMPTY')
    if words[0]=='sivane':
        a,i=_frame(words,1)
        if i>=len(words) or words[i]!='tanaro':fail('E_V08_CONDITIONAL','missing tanaro')
        b,j=_frame(words,i+1)
        if j!=len(words):fail('E_V08_TRAILING','conditional')
        return {'kind':'conditional','antecedent':_proposition(a),'consequent':_proposition(b),
                'interpretation':'speaker_reported_conditional'}
    # Preserve the exact pre-v0.8 meaning for ALL already accepted spoken clauses.
    try:
        return {'kind':'proposition','content':_proposition(words)}
    except SXPError:
        pass
    actor,i=_subject(words)
    polarity='positive'
    if i<len(words) and words[i]=='noka':polarity='negative';i+=1
    if i>=len(words) or words[i] not in ACT_ROOTS:
        return {'kind':'proposition','content':_proposition(words)}
    root=words[i];mode=ACT_ROOTS[root]
    payload,j=_frame(words,i+1)
    if j!=len(words):fail('E_V08_TRAILING',mode)
    if mode=='capacity_to_promise':
        proposed=_parse_node(payload,depth+1)
        if proposed['kind']!='promise_report' or proposed['polarity']!='positive':
            fail('E_V08_SCOPE','capacity refers to positive proposed promise')
        if proposed['promisor']!=actor:fail('E_V08_SCOPE','promisor differs from capacity holder')
        return {'kind':'capacity_report','holder':actor,'polarity':polarity,
                'candidate_promise':proposed}
    prop=_proposition(payload)
    if mode=='promise':
        if prop['clause']['time']!='future':fail('E_V08_PROMISE','promise action must be future')
        if _actor_of(prop)!=actor:fail('E_V08_PROMISE','promisor must be action actor')
        return {'kind':'promise_report','promisor':actor,'polarity':polarity,'action':prop}
    # Intent and desire are different attitudes; neither asserts event success.
    return {'kind':'attitude_report','stance':mode,'holder':actor,'polarity':polarity,'content':prop}


def parse_expression(text):
    words=spoken_tokens(text)
    if words[-1] not in ('devora','kevonu'):
        fail('E_V08_END','expected devora or kevonu')
    if any(x in ('devora','kevonu') for x in words[:-1]):
        fail('E_V08_END','exactly one end marker')
    # Full v0.7 backward compatibility, including questions and inert directives.
    try:
        old=canonical_parse(hear_spoken(text))
        return {'lang':'SXP-L','schema':VERSION,'register':'pragmatic_spoken_script',
                'node':{'kind':'proposition','content':old}}
    except SXPError:
        pass
    if words[-1]!='devora':fail('E_V08_END','new grammar only supports declarative ends')
    node=_parse_node(words[:-1],0)
    return {'lang':'SXP-L','schema':VERSION,'register':'pragmatic_spoken_script','node':node}


def _render_node(node):
    kind=node.get('kind')
    if kind=='proposition':return _proposition_text(node['content'])
    if kind=='conditional':
        if node.get('interpretation')!='speaker_reported_conditional':fail('E_V08_AST','conditional')
        return f'sivane bakumo {_proposition_text(node["antecedent"])} tesavo tanaro bakumo {_proposition_text(node["consequent"])} tesavo'
    if kind=='attitude_report':
        if node.get('stance') not in ('desire','intention','hope','fear','belief','knowledge_claim'):fail('E_V08_AST','attitude')
        return f'{_render_actor(node["holder"])} {"noka " if node["polarity"]=="negative" else ""}{REVERSE_ACT[node["stance"]]} bakumo {_proposition_text(node["content"])} tesavo'
    if kind=='promise_report':
        return f'{_render_actor(node["promisor"])} {"noka " if node["polarity"]=="negative" else ""}pamisa bakumo {_proposition_text(node["action"])} tesavo'
    if kind=='capacity_report':
        return f'{_render_actor(node["holder"])} {"noka " if node["polarity"]=="negative" else ""}kapera bakumo {_render_node(node["candidate_promise"])} tesavo'
    fail('E_V08_AST','unknown kind')


def render_expression(doc):
    if not isinstance(doc,dict) or set(doc)!={'lang','schema','register','node'} or doc['lang']!='SXP-L' or doc['schema']!=VERSION or doc['register']!='pragmatic_spoken_script':
        fail('E_V08_SCHEMA')
    node=doc['node']
    if node['kind']=='proposition' and node['content']['clause']['mood']!='assert':
        result=speak_spoken(speak_compact(canonical_render(node['content'])))
    else:
        result=_render_node(node)+' devora'
    if parse_expression(result)!=doc:fail('E_V08_AST','roundtrip inconsistency')
    return result


def explain_risk(doc):
    """Conservative semantic warning labels; does not evaluate real truth."""
    node=doc['node']
    kind=node['kind']
    if kind=='proposition':return 'Speaker assertion only; external facts not checked.'
    if kind=='attitude_report':return 'Attitude reported; embedded outcome not established.'
    if kind=='promise_report':return ('No positive promise performed in this negative statement.' if node['polarity']=='negative' else
                                      'Transcript contains promise wording; neither authority nor fulfillment verified.')
    if kind=='capacity_report':return 'Self/other capacity report; candidate promise is not performed.'
    if kind=='conditional':return 'Speaker conditional; neither branch asserted independently.'
    fail('E_V08_AST','risk kind')


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('text',nargs='+')
    a=p.parse_args(); d=parse_expression(' '.join(a.text))
    print(json.dumps(d,ensure_ascii=False,indent=2));print('\nNormalized:',render_expression(d))
    print('Caution:',explain_risk(d))
