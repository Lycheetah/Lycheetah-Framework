"""SXP-L v0.7 dialogue wrapper: ^ spoken-script, ~ compact, | full form.

Participants and referents validated by the retained v0.6/v0.5 engines.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
from conversation_v06 import parse_document as parse_v06, render_document as render_v06
from sxpl_v03 import SXPError
from compact import speak_compact
from spoken import hear_spoken, speak_spoken

SCHEMA='0.7.0'


def parse_document(source):
    if not isinstance(source,str):raise SXPError('E_V07_INPUT')
    lines=source.splitlines()
    if not lines or lines[0]!='diala 0.7':raise SXPError('E_V07_HEADER')
    expanded=['diala 0.6']
    for line in lines[1:]:
        if line.startswith('lina '):
            pre,sep,value=line.partition(' ^ ')
            if sep:
                if len(pre.split())!=2 or not value.strip():raise SXPError('E_V07_LINE')
                # A spoken line must be interpretable exactly as v0.6 compact.
                compact=speak_compact(hear_spoken(value))
                expanded.append(pre+' ~ '+compact)
                continue
        expanded.append(line)
    doc=parse_v06('\n'.join(expanded)+'\n')
    doc['schema']=SCHEMA
    return doc


def render_document(doc):
    if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:
        raise SXPError('E_V07_SCHEMA')
    base=copy.deepcopy(doc);base['schema']='0.6.0'
    text=render_v06(base)
    out=['diala 0.7']
    for raw in text.splitlines()[1:]:
        if raw.startswith('lina '):
            header,sep,compact=raw.partition(' ~ ')
            if sep:
                try:out.append(header+' ^ '+speak_spoken(compact))
                except SXPError as e:
                    if e.code!='E_SPOKEN_QUOTE':raise
                    out.append(raw)   # quote retains full compact syntax
                continue
        out.append(raw)
    result='\n'.join(out)+'\n'
    if parse_document(result)!=doc:raise SXPError('E_V07_AST','dialogue roundtrip mismatch')
    return result


def upgrade_v06(document):
    if not isinstance(document,dict) or document.get('schema')!='0.6.0':
        raise SXPError('E_V07_UPGRADE')
    txt=render_v06(document)
    return parse_document('diala 0.7\n'+'\n'.join(txt.splitlines()[1:])+'\n')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('file',type=Path)
    p.add_argument('--output',choices=['normalized','json'],default='normalized')
    a=p.parse_args()
    d=parse_document(a.file.read_text(encoding='utf-8'))
    print(render_document(d) if a.output=='normalized' else json.dumps(d,ensure_ascii=False,indent=2))
