"""SXP-L 1.0: inspect a dialogue and a separately supplied host-policy result.

The text cannot become an authorization source. The policy gate reads ONLY the
trusted request and signed events passed as distinct arguments. This module
NEVER performs actions. Even an allow decision is a non-executing simulation.
"""
from __future__ import annotations
import json
from pathlib import Path
from dialogue10 import parse_document, render_document, resolve_entity
from authz import decision


def _report(t,expr,utterance_id):
    n=expr['node']
    if n['kind']=='legacy_v09':
        earlier=n['content']['node']
        if earlier['kind']=='legacy_v08':
            return {'id':utterance_id,'speaker':t['speaker'],'kind':'legacy_expression',
                    'linguistic_only':True}
        return {'id':utterance_id,'speaker':t['speaker'],'kind':earlier['kind'],
                'operation':earlier['action'],'resource':earlier['resource'],
                'counterparty':resolve_entity(earlier['grantee'],t['speaker'],t['addressee']),
                'linguistic_only':True}
    return {'id':utterance_id,'speaker':t['speaker'],'kind':n['kind'],
            'operation':n['action'],'resource':n['resource'],
            'counterparty':resolve_entity(n['counterparty'],t['speaker'],t['addressee']),
            'linguistic_only':True}


def collect_reports(doc):
    # Render canonical document to validate the AST, including nested assertions.
    render_document(doc)
    return [_report(t,e['parsed'],e['id']) for t in doc['turns'] for e in t['events'] if e['kind']=='utterance']


def inspect(doc, host_request, signed_events, keys, ownership, *, now):
    """Never use any field derived from doc as a policy input."""
    reports=collect_reports(doc)
    result=decision(host_request,signed_events,keys,ownership,now=now)
    scope=host_request if isinstance(host_request,dict) else {}
    scoped=[r for r in reports if r.get('operation')==scope.get('operation') and
            r.get('resource')==scope.get('resource')]
    # Linguistic review flag only: real host must decide what to do with it.
    boundaries=[r for r in scoped if r['kind'] in ('decision_reservation','delegation_refusal')]
    return {'policy':result,'execution_performed':False,'reports':reports,
            'scope_reports':scoped,
            'reported_boundaries':boundaries,
            'review_advised':bool(result['allowed'] and boundaries),
            'explanation':'Host signature/ownership policy alone determines simulated allow/deny; language is advisory, not executable.'}


if __name__=='__main__':
    doc=parse_document((Path(__file__).parent/'examples/sovereignty_is_not_permission.sxh').read_text())
    req={'grantee':'agena','operation':'publish_post','resource':'darafa'}
    result=inspect(doc,req,[],{}, {},now=150)
    print(json.dumps(result,indent=2))
