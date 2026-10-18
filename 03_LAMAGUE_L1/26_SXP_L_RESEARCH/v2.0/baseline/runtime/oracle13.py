"""Independent *limited* reference-status oracle for a flat one-turn v1.3 sample.

Does NOT import continuity13 or any earlier SXP-L parser. It only checks
participant inventory, explicit roles and optional anchor; it does not validate
v1.2 grammar, and must not be described as a full independent parser.
"""
from __future__ import annotations
import re


class OracleUnsupported(Exception): pass


def read_flat_one_turn(text: str) -> dict:
    lines=[line.split() for line in text.splitlines() if line.strip()]
    i=0; people=[]
    while i<len(lines) and lines[i][0]=='norava':
        w=lines[i]
        if len(w)!=4 or w[1]!='gonape' or w[3]!='dimotu' or w[2] in people:
            raise OracleUnsupported('declaration')
        people.append(w[2]);i+=1
    if i>=len(lines) or len(people)<2:raise OracleUnsupported('participants')
    w=lines[i];i+=1
    if len(w)!=7 or w[0]!='taviro' or w[1]!='gonape' or w[3]!='dimotu' or w[4]!='gonape' or w[6]!='dimotu':
        raise OracleUnsupported('turn header')
    speaker,audience=w[2],w[5]
    if speaker==audience or speaker not in people or audience not in people:raise OracleUnsupported('participants')
    anchor=None
    if i<len(lines) and lines[i][0]=='rasufe':
        w=lines[i];i+=1
        if len(w)!=4 or w[1]!='gonape' or w[3]!='dimotu':raise OracleUnsupported('anchor')
        anchor=w[2]
    if i+1>=len(lines) or lines[i][-1]!='devora' or lines[i+1]!=['tevaro'] or i+2!=len(lines):
        raise OracleUnsupported('expression')
    if 'sivena' not in lines[i]:raise OracleUnsupported('no third-person reference')
    eligible=sorted(set(people)-{speaker,audience})
    if anchor is not None:
        if anchor not in eligible:raise OracleUnsupported('bad anchor')
        return {'status':'explicit_anchor','chosen':anchor,'candidates':[anchor]}
    if len(eligible)==1:
        return {'status':'unique_candidate','chosen':eligible[0],'candidates':eligible}
    return {'status':'ambiguous' if eligible else 'unresolved',
            'chosen':None,'candidates':eligible}
