"""SXP-L experimental v0.2 clause kernel. Not a security authorization engine."""
import hashlib
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation

SCHEMA = '0.2.0'
WORDS = {'sa':'assert','qu':'question','di':'directive'}
MOODS = {v:k for k,v in WORDS.items()}
MODS = {'ma':'possible','mu':'obligation'}
MODS_REV = {v:k for k,v in MODS.items()}
TIMES = {'pa':'past','nu':'present','fu':'future'}
TIMES_REV = {v:k for k,v in TIMES.items()}
ROLES = {'ka':'actor','ta':'target','lo':'context','se':'source','au':'authorizer','sc':'scope','co':'confidence'}
REV_ROLES = {v:k for k,v in ROLES.items()}
ROLE_ORDER = list(ROLES)
OPERATIONS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_.-]*$')
NUM = re.compile(r'^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')
TOK = re.compile(r'"(?:\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})|[^"\\\x00-\x1f])*"|[^\s"]+')
RESERVED = set(WORDS)|set(MODS)|set(TIMES)|set(ROLES)|{'no','xi','en','ve'}

class SXPError(ValueError):
    def __init__(self, code, info=''):
        super().__init__(f'{code}: {info}')
        self.code = code

def tokens(s):
    out=[]; pos=0
    for m in TOK.finditer(s):
        if s[pos:m.start()].strip(): raise SXPError('E_LEX','invalid token boundary')
        out.append(m.group()); pos=m.end()
    if s[pos:].strip(): raise SXPError('E_LEX','invalid trailing characters')
    if not out: raise SXPError('E_EMPTY')
    return out

def parse_value(tok):
    if tok.startswith('"'):
        try: v=json.loads(tok)
        except (ValueError, json.JSONDecodeError): raise SXPError('E_STRING',tok)
        if not isinstance(v,str): raise SXPError('E_STRING',tok)
        return {'type':'string','value':unicodedata.normalize('NFC',v)}
    if tok == 'xi': return {'type':'unknown'}
    if NUM.fullmatch(tok): return {'type':'number','value':tok}
    if ID.fullmatch(tok) and tok not in RESERVED and tok not in OPERATIONS:
        return {'type':'symbol','value':tok}
    raise SXPError('E_VALUE',tok)

def parse(s):
    t=tokens(s)
    if t[-1]!='en': raise SXPError('E_TERMINATOR','expected en')
    if t.count('en')!=1: raise SXPError('E_TERMINATOR','embedded en')
    p=0
    if t[p] not in WORDS: raise SXPError('E_MOOD',t[p])
    mood=WORDS[t[p]]; p+=1
    neg=False; mod=None; tim=None
    if p<len(t)-1 and t[p]=='no': neg=True;p+=1
    if p<len(t)-1 and t[p] in MODS: mod=MODS[t[p]];p+=1
    if p<len(t)-1 and t[p] in TIMES: tim=TIMES[t[p]];p+=1
    if p>=len(t)-1: raise SXPError('E_PREDICATE')
    op=t[p];p+=1
    if op not in OPERATIONS and not (ID.fullmatch(op) and op not in RESERVED):
        raise SXPError('E_PREDICATE',op)
    op=('N36:'+op) if op in OPERATIONS else ('USR:'+op)
    roles={}
    while p < len(t)-1:
        mark=t[p];p+=1
        if mark not in ROLES: raise SXPError('E_ROLE',mark)
        key=ROLES[mark]
        if key in roles: raise SXPError('E_DUP_ROLE',mark)
        if p>=len(t)-1: raise SXPError('E_MISSING_VALUE',mark)
        v=parse_value(t[p]);p+=1
        if key=='confidence':
            if v['type']!='number': raise SXPError('E_CONFIDENCE','must be numeric')
            try: dec=Decimal(v['value'])
            except InvalidOperation: raise SXPError('E_CONFIDENCE','invalid')
            if not 0<=dec<=1 or dec.as_tuple().exponent < -6:
                raise SXPError('E_CONFIDENCE','range 0..1, max 6 decimal places')
            v={'type':'fixed6','micros':int(dec*1000000)}
        roles[key]=v
    return {'lang':'SXP-L','schema':SCHEMA,'register':'canonical', 'clause':{
        'mood':mood,'polarity':'negative' if neg else 'positive','modality':mod,'time':tim,
        'op':op,'roles':{k:roles[k] for k in (ROLES[r] for r in ROLE_ORDER) if k in roles}}}

def validate_ast(ast):
    if not isinstance(ast,dict) or ast.get('lang')!='SXP-L' or ast.get('schema')!=SCHEMA or ast.get('register')!='canonical':
        raise SXPError('E_SCHEMA')
    c=ast.get('clause')
    if not isinstance(c,dict) or set(c)!={'mood','polarity','modality','time','op','roles'}:raise SXPError('E_AST')
    if c['mood'] not in MOODS or c['polarity'] not in ('positive','negative') or c['modality'] not in (None,*MODS_REV) or c['time'] not in (None,*TIMES_REV):raise SXPError('E_AST')
    op=c['op']
    if not isinstance(op,str) or not (op.startswith('N36:') and op[4:] in OPERATIONS or op.startswith('USR:') and ID.fullmatch(op[4:]) and op[4:] not in RESERVED):raise SXPError('E_AST')
    roles=c['roles']
    if not isinstance(roles,dict) or any(k not in REV_ROLES for k in roles):raise SXPError('E_AST')
    for k,v in roles.items():
        if not isinstance(v,dict) or v.get('type') not in ('string','symbol','number','unknown','fixed6'):raise SXPError('E_AST')
        typ=v['type']
        if (k=='confidence') != (typ=='fixed6'): raise SXPError('E_AST')
        if typ=='fixed6':
            if set(v)!={'type','micros'} or type(v['micros']) is not int or not 0<=v['micros']<=1000000:raise SXPError('E_AST')
        elif typ=='unknown':
            if set(v)!={'type'}:raise SXPError('E_AST')
        elif set(v)!={'type','value'} or not isinstance(v['value'],str):raise SXPError('E_AST')
        elif typ=='number' and not NUM.fullmatch(v['value']):raise SXPError('E_AST')
        elif typ=='symbol' and (not ID.fullmatch(v['value']) or v['value'] in RESERVED or v['value'] in OPERATIONS):raise SXPError('E_AST')
        elif typ=='string' and unicodedata.normalize('NFC',v['value'])!=v['value']:raise SXPError('E_AST')

def render(ast):
    validate_ast(ast);c=ast['clause']
    parts=[MOODS[c['mood']]]
    if c['polarity']=='negative':parts.append('no')
    if c['modality']:parts.append(MODS_REV[c['modality']])
    if c['time']:parts.append(TIMES_REV[c['time']])
    parts.append(c['op'].split(':',1)[1])
    for mark,key in ROLES.items():
        if key not in c['roles']:continue
        v=c['roles'][key];parts.append(mark)
        if v['type']=='unknown':parts.append('xi')
        elif v['type']=='fixed6':parts.append(f"{Decimal(v['micros'])/Decimal(1000000):f}")
        elif v['type']=='string':parts.append(json.dumps(v['value'],ensure_ascii=False))
        else:parts.append(v['value'])
    parts.append('en')
    return ' '.join(parts)

def canonical(ast):
    validate_ast(ast)
    return json.dumps(ast,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')

def fingerprint(ast):return hashlib.sha256(b'SXP-L\x00'+canonical(ast)).hexdigest()

if __name__=='__main__':
    import argparse
    cli=argparse.ArgumentParser();cli.add_argument('sentence',nargs='+');args=cli.parse_args()
    a=parse(' '.join(args.sentence))
    print(json.dumps(a,indent=2,ensure_ascii=False));print('normalized:',render(a));print('sha256:',fingerprint(a))
