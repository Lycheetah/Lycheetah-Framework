"""Simulated remote provider, separate *process* and SQLite database.
Never point at real services. No identity/authentication. Built to study crash windows.
"""
import argparse, json, sqlite3
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

@contextmanager
def db(path):
    c=sqlite3.connect(path,timeout=10,isolation_level=None)
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
        c.execute('CREATE TABLE IF NOT EXISTS operations(op_id TEXT PRIMARY KEY, payload TEXT NOT NULL, effect_id INTEGER NOT NULL, reversible INTEGER NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS effects(effect_id INTEGER PRIMARY KEY AUTOINCREMENT, op_id TEXT NOT NULL, payload TEXT NOT NULL, compensated INTEGER NOT NULL DEFAULT 0)')
        c.execute('CREATE TABLE IF NOT EXISTS compensations(comp_id TEXT PRIMARY KEY, op_id TEXT NOT NULL, status TEXT NOT NULL)')

def apply(path, op_id, payload, *, dedup=True):
    data=json.dumps(payload,sort_keys=True,separators=(',',':'))
    with db(path) as c:
        c.execute('BEGIN IMMEDIATE')
        old=c.execute('SELECT * FROM operations WHERE op_id=?',(op_id,)).fetchone()
        if dedup and old:
            if old['payload'] != data: raise ValueError('same op_id used for different payload')
            result=dict(old);c.execute('COMMIT');return result
        c.execute('INSERT INTO effects(op_id,payload) VALUES (?,?)',(op_id,data))
        eid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        if not old:
            c.execute('INSERT INTO operations VALUES (?,?,?,?)',(op_id,data,eid,1 if payload['kind']=='write' else 0))
        c.execute('COMMIT')
        return dict(op_id=op_id,payload=data,effect_id=eid,reversible=1 if payload['kind']=='write' else 0)

def receipt(path,op_id):
    with db(path) as c:
        r=c.execute('SELECT * FROM operations WHERE op_id=?',(op_id,)).fetchone()
        return dict(r) if r else None

def comp_receipt(path,comp_id):
    with db(path) as c:
        r=c.execute('SELECT * FROM compensations WHERE comp_id=?',(comp_id,)).fetchone()
        return dict(r) if r else None

def compensate(path,op_id,comp_id):
    with db(path) as c:
        c.execute('BEGIN IMMEDIATE')
        prev=c.execute('SELECT * FROM compensations WHERE comp_id=?',(comp_id,)).fetchone()
        if prev:
            if prev['op_id']!=op_id:raise ValueError('comp_id collision')
            c.execute('COMMIT');return dict(prev)
        op=c.execute('SELECT * FROM operations WHERE op_id=?',(op_id,)).fetchone()
        if not op:raise ValueError('operation not found')
        if not op['reversible']:
            status='irreversible'
        else:
            original=c.execute('SELECT * FROM effects WHERE effect_id=?',(op['effect_id'],)).fetchone()
            # This simplistic provider models one independent effect per op; no external actor updates.
            if original['compensated']:
                status='restored'
            else:
                c.execute('UPDATE effects SET compensated=1 WHERE effect_id=?',(op['effect_id'],))
                status='restored'
        c.execute('INSERT INTO compensations VALUES (?,?,?)',(comp_id,op_id,status))
        c.execute('COMMIT')
        return dict(comp_id=comp_id,op_id=op_id,status=status)

def state(path):
    with db(path) as c:
        return dict(effects=[dict(r) for r in c.execute('SELECT * FROM effects ORDER BY effect_id')],operations=[dict(r) for r in c.execute('SELECT * FROM operations ORDER BY effect_id')],compensations=[dict(r) for r in c.execute('SELECT * FROM compensations ORDER BY comp_id')])

def serve(path,port,ready):
    init(path)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def respond(self,status,obj):
            blob=json.dumps(obj,sort_keys=True).encode();self.send_response(status)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(blob)))
            self.end_headers();self.wfile.write(blob)
        def do_GET(self):
            u=urlsplit(self.path);q=parse_qs(u.query)
            if u.path=='/state':self.respond(200,state(path))
            elif u.path=='/operation':self.respond(200,{'receipt':receipt(path,q.get('op_id',[''])[0])})
            elif u.path=='/compensation':self.respond(200,{'receipt':comp_receipt(path,q.get('comp_id',[''])[0])})
            elif u.path=='/health':self.respond(200,{'ok':True})
            else:self.respond(404,{'error':'unknown route'})
        def do_POST(self):
            try:
                if int(self.headers.get('Content-Length','0'))>32768:raise ValueError('request too large')
                data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
                if self.path=='/apply':
                    if data['payload']['kind'] not in ('write','notify'):raise ValueError('unknown kind')
                    result=apply(path,data['op_id'],data['payload'],dedup=data.get('dedup',True))
                elif self.path=='/compensate':result=compensate(path,data['op_id'],data['comp_id'])
                else:self.respond(404,{'error':'unknown route'});return
                self.respond(200,result)
            except (ValueError,KeyError,TypeError) as e:self.respond(400,{'error':str(e)})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    with open(ready,'w') as out:out.write(str(server.server_port))
    try:server.serve_forever(poll_interval=.05)
    finally:server.server_close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--db',required=True);p.add_argument('--ready',required=True);p.add_argument('--port',type=int,default=0)
    a=p.parse_args();serve(a.db,a.port,a.ready)
