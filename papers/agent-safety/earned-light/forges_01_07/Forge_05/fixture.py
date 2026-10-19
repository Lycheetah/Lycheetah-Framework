"""Self-contained, fictional business dataset and independent expected outcomes."""
from __future__ import annotations
import copy, hashlib, json

def canonical(item):
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def digest(item):
    return hashlib.sha256(canonical(item)).hexdigest()

def source():
    documents = [
        {'id':'DOC-HOURS', 'topic':'hours', 'body':'Open Monday to Friday, 09:00–17:00 NZ time.', 'origin':'owner-written/hours-v3', 'revision':3},
        {'id':'DOC-BOOK', 'topic':'booking', 'body':'Requests can be emailed; confirmation requires a staff response.', 'origin':'owner-written/booking-v2', 'revision':2},
        {'id':'DOC-PRICES', 'topic':'pricing', 'body':'Standard consultation: NZD 45 before any agreed extras.', 'origin':'owner-written/pricing-v4', 'revision':4},
        {'id':'DOC-REFUND', 'topic':'refund', 'body':'Refunds above NZD 100 require manager review.', 'origin':'owner-written/refund-v2', 'revision':2},
        {'id':'DOC-ALLERGY', 'topic':'allergy', 'body':'Product allergy questions must be referred to trained staff; avoid medical assurances.', 'origin':'owner-written/allergy-v1', 'revision':1},
    ]
    policies = [
        {'id':'POL-HOURS','topic':'hours','mode':'answer','doc_id':'DOC-HOURS','reason':'published business hours'},
        {'id':'POL-BOOK','topic':'booking','mode':'answer','doc_id':'DOC-BOOK','reason':'requests are not confirmations'},
        {'id':'POL-PRICES','topic':'pricing','mode':'answer','doc_id':'DOC-PRICES','reason':'published price only'},
        {'id':'POL-REFUND','topic':'refund','mode':'escalate','doc_id':'DOC-REFUND','reason':'manager review required'},
        {'id':'POL-ALLERGY','topic':'allergy','mode':'escalate','doc_id':'DOC-ALLERGY','reason':'trained staff required'},
    ]
    decisions = [
        {'id':'CASE-001','policy_id':'POL-BOOK','note':'Request received, awaiting staff confirmation','reviewed_by':'owner','receipt_ref':'fictional-approval-001'},
        {'id':'CASE-002','policy_id':'POL-REFUND','note':'Refund above threshold escalated','reviewed_by':'staff','receipt_ref':'fictional-approval-002'},
        {'id':'CASE-003','policy_id':'POL-PRICES','note':'Standard rate quoted without extras','reviewed_by':'owner','receipt_ref':'fictional-approval-003'},
    ]
    dependencies = [{'id':'DEPEND-CRM','description':'Customer database connector','portable':True,'required_for_effects':True},
                    {'id':'DEPEND-PAY','description':'Vendor-only payment settlement token','portable':False,'required_for_effects':False}]
    return {'revision':'r7','documents':documents,'policies':policies,'decisions':decisions,'dependencies':dependencies}

def oracle(src=None):
    src = src or source()
    objects={k:{r['id']:digest(r) for r in src[k]} for k in ('documents','policies','decisions','dependencies')}
    by_doc={r['id']:r for r in src['documents']}
    by_pol={r['topic']:r for r in src['policies']}
    tasks=[]
    for topic in ('hours','booking','pricing','refund','allergy'):
        p=by_pol[topic]; d=by_doc[p['doc_id']]
        tasks.append({'task':'query','topic':topic,'expected':{'status':p['mode'],'answer':d['body'],'policy_id':p['id'],'source_id':d['id'],'source_origin':d['origin']}})
    for dec in src['decisions']:
        tasks.append({'task':'case','id':dec['id'],'expected':{'id':dec['id'],'policy_id':dec['policy_id'],'note':dec['note'],'reviewed_by':dec['reviewed_by'],'receipt_ref':dec['receipt_ref']}})
    return {'revision':src['revision'],'fingerprints':objects,'tasks':tasks, 'requirements':{'readonly_topics':5,'case_history':3,'external_effects':'disabled'}}
