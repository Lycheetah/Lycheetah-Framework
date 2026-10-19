"""Durable local journal for experiment; no real human auth implemented.

Reservation is a controller-side fence only. An existing reservation may already be in
flight when revocation occurs. Provider receipts are simulated, not independently attested.
"""
import json, sqlite3, urllib.request, urllib.parse, os
from contextlib import contextmanager

@contextmanager
def db(path):
    c=sqlite3.connect(path,isolation_level=None,timeout=10)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    try:
        yield c
        if c.in_transaction:c.commit()
    except BaseException:
        if c.in_transaction:c.rollback()
        raise
    finally:c.close()

def init(path):
    with db(path) as c:
        c.execute('CREATE TABLE IF NOT EXISTS grants (delegation TEXT PRIMARY KEY, active INTEGER NOT NULL, epoch INTEGER NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS jobs (op_id TEXT PRIMARY KEY, delegation TEXT NOT NULL, epoch INTEGER NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL, comp_status TEXT)')

def start(path,kind='write'):
    init(path)
    with db(path) as c:
        c.execute('INSERT INTO grants VALUES (?,?,?)',('owner',1,0))
        c.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?)',('op-001','owner',0,json.dumps({'kind':kind,'data':'synthetic-test-value'}),'proposed',None))

def revoke(path):
    with db(path) as c:
        c.execute('BEGIN IMMEDIATE');c.execute('UPDATE grants SET active=0,epoch=epoch+1 WHERE delegation=?',('owner',));c.execute('COMMIT')

def reserve(path):
    with db(path) as c:
        c.execute('BEGIN IMMEDIATE')
        r=c.execute('SELECT j.*,g.active,g.epoch AS grant_epoch FROM jobs j JOIN grants g ON j.delegation=g.delegation').fetchone()
        if r['status']=='proposed':
            if not r['active'] or r['epoch']!=r['grant_epoch']:
                c.execute('UPDATE jobs SET status=? WHERE op_id=?',('blocked',r['op_id']))
                c.execute('COMMIT');return 'blocked'
            c.execute('UPDATE jobs SET status=? WHERE op_id=?',('reserved',r['op_id']))
        elif r['status'] not in ('reserved','confirmed','compensating','restored','irreversible','unresolved'):
            raise ValueError('illegal job status')
        c.execute('COMMIT');return r['status']

def job(path):
    with db(path) as c:return dict(c.execute('SELECT * FROM jobs').fetchone())

def mark(path,**updates):
    allowed={'status','comp_status'}
    if not set(updates)<=allowed:raise ValueError('invalid mark field')
    with db(path) as c:
        c.execute('BEGIN IMMEDIATE')
        for k,v in updates.items():c.execute('UPDATE jobs SET '+k+'=?',(v,))
        c.execute('COMMIT')

def request(url,path,body=None,timeout=3):
    data=None if body is None else json.dumps(body,sort_keys=True).encode()
    req=urllib.request.Request(url+path,data=data,headers={'Content-Type':'application/json'} if body is not None else {})
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)

def die(stage,target):
    if stage==target:os._exit(73) # abrupt process death bypassing finally/cleanup

def dispatch(path,url,cut=None,dedup=True):
    die('before_reserve',cut)
    status=reserve(path)
    if status=='blocked':return 'blocked'
    die('after_reserve_before_send',cut)
    j=job(path)
    # This worker is called only for its reserved job. No fresh delegation is inferred.
    result=request(url,'/apply',{'op_id':j['op_id'],'payload':json.loads(j['payload']),'dedup':dedup})
    die('after_commit_before_ack',cut)
    mark(path,status='confirmed')
    die('after_ack_before_return',cut)
    return 'confirmed'

def reconcile(path,url,provider_query=True):
    j=job(path)
    if j['status'] in ('blocked','proposed'):
        return 'no_effect_dispatched' if j['status']=='blocked' else 'not_dispatched'
    if j['status'] in ('restored','irreversible'):return j['status']
    # A reported absence after reservation is NOT proof that an effect cannot arrive later.
    if not provider_query:return 'unresolved_effect'
    try:r=request(url,'/operation?'+urllib.parse.urlencode({'op_id':j['op_id']}))['receipt']
    except (OSError,TimeoutError,ValueError):return 'unresolved_effect'
    if r is None:return 'unresolved_effect'
    mark(path,status='confirmed');return 'confirmed'

def recover(path,url,cut=None,provider_query=True):
    j=job(path)
    with db(path) as c:
        if c.execute('SELECT active FROM grants').fetchone()['active']:
            raise ValueError('revoke before recovering')
    status=reconcile(path,url,provider_query)
    if status!='confirmed':
        return dict(terminal_status=status,delegation_revoked=True,independent_effect_proof=False)
    j=job(path)
    mark(path,status='compensating')
    result=request(url,'/compensate',{'op_id':j['op_id'],'comp_id':'return:'+j['op_id']})
    die('after_compensation_before_ack',cut)
    mark(path,status=result['status'],comp_status=result['status'])
    die('after_compensation_ack',cut)
    return dict(terminal_status=result['status'],delegation_revoked=True,independent_effect_proof=False)

def report(path,url,provider_query=True):
    # Deliberately keep controller-reported and provider-observed state separate.
    local=job(path)
    observed=None
    if provider_query:
        try:observed=request(url,'/state')
        except (OSError,TimeoutError,ValueError):pass
    return dict(controller_status=local['status'],controller_compensation=local['comp_status'],
                revoked=not bool(request_local_grant(path)),provider_available=observed is not None,
                provider_effects=None if observed is None else observed['effects'],
                provider_compensations=None if observed is None else observed['compensations'])

def request_local_grant(path):
    with db(path) as c:return c.execute('SELECT active FROM grants').fetchone()['active']
