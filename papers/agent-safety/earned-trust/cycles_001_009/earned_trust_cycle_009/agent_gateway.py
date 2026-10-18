"""C009 agent-facing Linux Unix socket gateway (peer-credential authenticated).

Caller may propose (effect_id, action), but cannot mint approval/capability.
Requires Linux SO_PEERCRED and dedicated trusted gateway owner. Not a sandbox;
requires separation of OS users, file permissions, and provider network/keys.
"""
from __future__ import annotations
import json
import os
import socket
import socketserver
import sqlite3
import struct
from pathlib import Path
from upstream_dispatch_fence import canonical
from protected_provider import strict_json

class AgentGatewayServer(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
    daemon_threads=True
    allow_reuse_address=True
    def __init__(self,path, dispatch_gateway,uid_actors:dict[int,str], clock=50):
        if not hasattr(socket,'SO_PEERCRED'):raise RuntimeError('Linux SO_PEERCRED required')
        self.gateway=dispatch_gateway
        self.uid_actors=dict(uid_actors)
        self.clock=clock
        super().__init__(str(path), AgentGatewayRequestHandler)
        os.chmod(path,0o666)  # Auth is via SO_PEERCRED, not socket mode.

    def server_close(self):
        path=self.server_address
        super().server_close()
        try:os.unlink(path)
        except FileNotFoundError:pass

class AgentGatewayRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            packed=self.request.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i'))
            pid,uid,gid=struct.unpack('3i',packed)
            actor=self.server.uid_actors.get(uid)
            if actor is None:
                return self.reply(403,{'error':'unrecognized-peer-uid'})
            raw=self.rfile.readline(16_385)
            if not raw or len(raw)>16_384:return self.reply(413,{'error':'request-size-limit'})
            req=strict_json(raw)
            if not isinstance(req,dict) or set(req)!={'effect_id','action'}:
                return self.reply(400,{'error':'invalid-request'})
            eid=req['effect_id'];action=req['action']
            if not isinstance(eid,str) or not eid or not isinstance(action,dict):
                return self.reply(400,{'error':'invalid-action'})
            auth=self.server.gateway.authority
            with auth._db() as c:
                row=c.execute('SELECT actor FROM effects WHERE effect_id=?',(eid,)).fetchone()
            if row is None:return self.reply(404,{'error':'unapproved-effect'})
            if row['actor']!=actor:return self.reply(403,{'error':'effect-belongs-to-another-actor'})
            witness=auth.witness(eid)
            if witness is None:return self.reply(409,{'error':'witness-unavailable'})
            outcome=self.server.gateway.submit(eid,action,witness,self.server.clock)
            return self.reply(200 if outcome.status=='SUCCEEDED' else 409,
                              {'status':outcome.status,'reason':outcome.reason,
                               'receipt':outcome.receipt})
        except (ValueError,TypeError,UnicodeError,json.JSONDecodeError):
            return self.reply(400,{'error':'bad-json'})
        except sqlite3.Error:
            return self.reply(503,{'error':'authority-unavailable'})

    def reply(self,status:int,data:dict):
        self.wfile.write(canonical({'code':status,**data})+b'\n')
        self.wfile.flush()
