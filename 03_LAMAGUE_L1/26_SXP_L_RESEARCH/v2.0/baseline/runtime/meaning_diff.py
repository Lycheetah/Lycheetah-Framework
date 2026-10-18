"""SXP-L v0.8: structural meaning-difference inspector for spoken-script clauses.

Computes syntactic/typed semantic AST changes, NOT semantic equivalence of
natural-language statements or world facts. No claims about inference quality.
"""
from __future__ import annotations
import hashlib
import json
from pragmatics import parse_expression

CRITICAL_KEYS={'kind','stance','polarity','time','mood','modality','promisor','holder','interpretation','op'}


def walk(node,prefix=''):
    if isinstance(node,dict):
        for key in sorted(node):
            yield from walk(node[key],prefix+'/'+key)
    elif isinstance(node,list):
        for index,val in enumerate(node):yield from walk(val,prefix+'/'+str(index))
    else:
        yield prefix,node


def compare(a,b):
    first=parse_expression(a);second=parse_expression(b)
    left=dict(walk(first['node'],'/node'));right=dict(walk(second['node'],'/node'))
    differences=[]
    missing=object()
    for path in sorted(set(left)|set(right)):
        l=left.get(path,missing);r=right.get(path,missing)
        if l is missing or r is missing or l!=r:
            category='high' if path.rsplit('/',1)[-1] in CRITICAL_KEYS else 'inspect'
            differences.append({'path':path,'from':{'missing':True} if l is missing else l,
                                'to':{'missing':True} if r is missing else r,
                                'priority':category})
    return {'equivalent_typed_representation':not differences,
            'differences':differences,
            'warning':'Structural AST comparison only; equality does not prove real-world equivalence or translation accuracy.'}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('first',help='First spoken-script expression in quotes')
    p.add_argument('second',help='Second spoken-script expression in quotes')
    args=p.parse_args()
    print(json.dumps(compare(args.first,args.second),ensure_ascii=False,indent=2))
