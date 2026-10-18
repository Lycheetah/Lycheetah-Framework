"""SXP-L v0.3: experimental recursive semantic kernel, not a natural-language translator."""
import json,hashlib,unicodedata
from sxpl_v02 import tokens,parse_value,SXPError,WORDS,MOODS,MODS,MODS_REV,TIMES,TIMES_REV,OPERATIONS,ID,RESERVED,NUM

SCHEMA='0.3.0'
ROLES={'ka':'actor','ta':'target','lo':'context','se':'source','au':'authorizer','sc':'scope','co':'confidence',
       'fe':'feeling','re':'relation','vi':'viewpoint','pr':'proposition'}
# A published starter lexicon, not asserted universals of human experience.
FEELINGS={'longing','affection','joy','fear','sadness','anger','hope','grief','uncertain'}
RELATIONS={'loves','knows','trusts','misses','family','friend','other'}
MAX_DEPTH=8
MAX_TOKENS=4096
MAX_STRING=10000

def _value(token, role):
    v=parse_value(token)
    if v['type']=='string' and len(v['value'])>MAX_STRING:raise SXPError('E_LIMIT','string too long')
    if role=='confidence':
        from decimal import Decimal
        if v['type']!='number':raise SXPError('E_CONFIDENCE')
        d=Decimal(v['value'])
        if not 0<=d<=1 or d.as_tuple().exponent < -6:raise SXPError('E_CONFIDENCE')
        return {'type':'fixed6','micros':int(d*1000000)}
    if role in ('feeling','relation'):
        allowed=FEELINGS if role=='feeling' else RELATIONS
        if v['type']!='symbol' or v['value'] not in allowed:raise SXPError('E_LEXICON',role)
    return v

def parse(source):
    ts=tokens(source)
    if len(ts)>MAX_TOKENS:raise SXPError('E_LIMIT','too many tokens')
    clause,index=_parse_clause(ts,0,0)
    if index!=len(ts):raise SXPError('E_TRAILING')
    return {'lang':'SXP-L','schema':SCHEMA,'register':'canonical','clause':clause}

def _parse_clause(ts,i,depth):
    if depth>MAX_DEPTH:raise SXPError('E_DEPTH')
    if i>=len(ts) or ts[i] not in WORDS:raise SXPError('E_MOOD')
    mood=WORDS[ts[i]];i+=1
    polarity='positive';modality=None;time=None
    if i<len(ts) and ts[i]=='no':polarity='negative';i+=1
    if i<len(ts) and ts[i] in MODS:modality=MODS[ts[i]];i+=1
    if i<len(ts) and ts[i] in TIMES:time=TIMES[ts[i]];i+=1
    if i>=len(ts):raise SXPError('E_PREDICATE')
    op=ts[i];i+=1
    if op in OPERATIONS:op='N36:'+op
    elif ID.fullmatch(op) and op not in RESERVED and op not in ROLES:op='USR:'+op
    else:raise SXPError('E_PREDICATE')
    roles={}
    while i<len(ts) and ts[i]!='en':
        marker=ts[i];i+=1
        if marker not in ROLES:raise SXPError('E_ROLE',marker)
        role=ROLES[marker]
        if role in roles:raise SXPError('E_DUP_ROLE',marker)
        if i>=len(ts):raise SXPError('E_MISSING_VALUE',marker)
        if role=='proposition':
            if ts[i]!='[':raise SXPError('E_NESTED_OPEN')
            sub,i=_parse_clause(ts,i+1,depth+1)
            if i>=len(ts) or ts[i]!=']':raise SXPError('E_NESTED_CLOSE')
            i+=1
            roles[role]={'type':'clause','value':sub}
        else:
            roles[role]=_value(ts[i],role);i+=1
    if i>=len(ts) or ts[i]!='en':raise SXPError('E_TERMINATOR')
    i+=1
    return {'mood':mood,'polarity':polarity,'modality':modality,'time':time,'op':op,'roles':roles},i

def _render_clause(c,depth=0):
    if depth>MAX_DEPTH:raise SXPError('E_DEPTH')
    if not isinstance(c,dict) or set(c)!={'mood','polarity','modality','time','op','roles'}:raise SXPError('E_AST')
    if c['mood'] not in MOODS or c['polarity'] not in ('positive','negative') or c['modality'] not in (None,*MODS_REV) or c['time'] not in (None,*TIMES_REV):raise SXPError('E_AST')
    op=c['op'];raw=op[4:] if isinstance(op,str) and (op.startswith('USR:') or op.startswith('N36:')) else ''
    if not (op=='N36:'+raw and raw in OPERATIONS or op=='USR:'+raw and bool(ID.fullmatch(raw)) and raw not in RESERVED and raw not in ROLES and raw not in OPERATIONS):raise SXPError('E_AST')
    roles=c['roles']
    if not isinstance(roles,dict) or any(k not in ROLES.values() for k in roles):raise SXPError('E_AST')
    parts=[MOODS[c['mood']]]
    if c['polarity']=='negative':parts.append('no')
    if c['modality']:parts.append(MODS_REV[c['modality']])
    if c['time']:parts.append(TIMES_REV[c['time']])
    parts.append(raw)
    for marker,role in ROLES.items():
        if role not in roles:continue
        v=roles[role]
        if not isinstance(v,dict) or 'type' not in v:raise SXPError('E_AST')
        parts.append(marker)
        if role=='proposition':
            if set(v)!={'type','value'} or v['type']!='clause':raise SXPError('E_AST')
            parts.extend(['[',*_render_clause(v['value'],depth+1),']']);continue
        if role=='confidence':
            if set(v)!={'type','micros'} or v['type']!='fixed6' or type(v['micros']) is not int or not 0<=v['micros']<=1000000:raise SXPError('E_AST')
            from decimal import Decimal
            parts.append(format(Decimal(v['micros'])/1000000,'f'));continue
        if v['type']=='unknown' and set(v)=={'type'}:parts.append('xi');continue
        if set(v)!={'type','value'} or not isinstance(v['value'],str):raise SXPError('E_AST')
        value=v['value']
        if v['type']=='string' and len(value)<=MAX_STRING and unicodedata.normalize('NFC',value)==value:parts.append(json.dumps(value,ensure_ascii=False));continue
        if v['type']=='number' and NUM.fullmatch(value):parts.append(value);continue
        if v['type']=='symbol' and ID.fullmatch(value) and value not in RESERVED and value not in OPERATIONS and value not in ROLES:
            if role=='feeling' and value not in FEELINGS or role=='relation' and value not in RELATIONS:raise SXPError('E_LEXICON')
            parts.append(value);continue
        raise SXPError('E_AST')
    parts.append('en')
    return parts

def render(ast):
    if not isinstance(ast,dict) or ast.get('lang')!='SXP-L' or ast.get('schema')!=SCHEMA or ast.get('register')!='canonical' or set(ast)!={'lang','schema','register','clause'}:raise SXPError('E_SCHEMA')
    s=' '.join(_render_clause(ast['clause']))
    if parse(s)!=ast:raise SXPError('E_AST','AST does not round trip')
    return s

def canonical(ast):return json.dumps(parse(render(ast)),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def fingerprint(ast):return hashlib.sha256(b'SXP-L-v0.3\0'+canonical(ast)).hexdigest()

if __name__=='__main__':
    import sys
    obj=parse(' '.join(sys.argv[1:]))
    print(json.dumps(obj,ensure_ascii=False,indent=2));print(render(obj))
