"""SXP-L v0.6 dialogue with short-form 'lina id ~ ...' and v0.5 fallback.

All speaker attribution and co-reference resolution stay delegated to v0.5.
Only the surface register changes. No implicit authority, no truth evaluation.
"""
import argparse
import copy
import json
from pathlib import Path
from dialogue import parse_document as parse_v05, render_document as render_v05, fingerprint as fingerprint_v05
from roots import speak_roots, hear_roots
from sxpl_v03 import SXPError, parse as parse_clause
from compact import hear_compact, speak_compact

SCHEMA='0.6.0'


def parse_document(source):
    if not isinstance(source,str):raise SXPError('E_V06_INPUT')
    lines=source.splitlines()
    # Reject ambiguous headers. v0.5 parser catches document shape and limits.
    if not lines or lines[0]!='diala 0.6':raise SXPError('E_V06_HEADER')
    expanded=['diala 0.5']
    for line in lines[1:]:
        if line.startswith('lina '):
            name,sep,expression=line.partition(' ~ ')
            if sep:
                if len(name.split())!=2 or not expression.strip():raise SXPError('E_V06_LINE')
                canonical=hear_compact(expression)
                full=speak_roots(canonical)
                expanded.append(name+' | '+full)
                continue
        expanded.append(line)
    doc=parse_v05('\n'.join(expanded)+'\n')
    doc['schema']=SCHEMA
    return doc


def render_document(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:
        raise SXPError('E_V06_SCHEMA')
    old=copy.deepcopy(doc)
    old['schema']='0.5.0'
    # Legacy validator checks all other fields incl. resolved participant links.
    canonical=render_v05(old)
    compact=['diala 0.6']
    for raw in canonical.splitlines()[1:]:
        if raw.startswith('lina '):
            header,sep,surface=raw.partition(' | ')
            if not sep:raise SXPError('E_V06_LINE')
            try:
                short=speak_compact(hear_roots(surface))
                compact.append(header+' ~ '+short)
            except SXPError as e:
                # Lossless fallback to full register, including unsupported roles.
                if e.code !='E_COMPACT_UNSUPPORTED':raise
                compact.append(raw)
        else:compact.append(raw)
    output='\n'.join(compact)+'\n'
    if parse_document(output)!=doc:raise SXPError('E_V06_AST','render mismatch')
    return output


def upgrade_v05(document):
    """Upgrade an already-validated v0.5 AST to v0.6 without meaning changes."""
    valid=render_v05(document)
    upgraded=parse_document('diala 0.6\n'+'\n'.join(valid.splitlines()[1:])+'\n')
    return upgraded


def stats(doc):
    count=sum(e['kind']=='line' for t in doc['turns'] for e in t['events'])
    return {'schema':SCHEMA,'participants':len(doc['participants']),
            'turns':len(doc['turns']),'utterances':count,
            'links':sum(e['kind']=='link' for t in doc['turns'] for e in t['events'])}


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('file',type=Path)
    cli.add_argument('--output',choices=['summary','json','normalized'],default='summary')
    a=cli.parse_args()
    d=parse_document(a.file.read_text(encoding='utf8'))
    if a.output=='summary':print(json.dumps(stats(d),indent=2))
    elif a.output=='json':print(json.dumps(d,ensure_ascii=False,indent=2))
    else:print(render_document(d),end='')

if __name__=='__main__':main()
