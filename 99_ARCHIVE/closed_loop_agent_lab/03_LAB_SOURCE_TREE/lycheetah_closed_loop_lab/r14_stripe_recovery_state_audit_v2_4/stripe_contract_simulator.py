"""Local, non-production simulator for a narrow Stripe API v1 refund contract.

This deliberately models only the request/response semantics needed by tests.
It is not a Stripe emulator and must not be used for production conclusions.
"""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import threading
from urllib.parse import parse_qs, urlparse


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False)


class StripeContractSimulator:
    def __init__(self, *, list_page_size=100):
        self.lock=threading.RLock()
        self.refunds=[]
        self.resources={}
        self.idempotency={}
        self.post_calls=0
        self.get_calls=0
        self.get_paths=[]
        self.fail_next_resource_read=False
        self.before_post_callback=None
        self.effect_count=0
        self.next_mode="normal"
        self.next_status="succeeded"
        self.last_headers={}
        self.list_page_size=list_page_size
        self.corrupt_next_list=None
        self.redirect_next=False
        self._counter=0
        outer=self
        class Handler(BaseHTTPRequestHandler):
            protocol_version="HTTP/1.1"
            def log_message(self,*args):
                return
            def _json(self,status,body):
                raw=_canonical(body).encode()
                self.send_response(status)
                self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(raw)))
                self.send_header("Connection","close")
                self.end_headers()
                self.wfile.write(raw)
                self.close_connection=True
            def _drop(self):
                self.close_connection=True
                try: self.connection.shutdown(socket.SHUT_RDWR)
                except OSError: pass
                try: self.connection.close()
                except OSError: pass
            def _auth(self):
                auth=self.headers.get("Authorization","")
                return auth == "Bearer sk_test_local_mock"
            def do_POST(self):
                with outer.lock:
                    outer.last_headers = dict(self.headers.items())
                    outer.post_calls += 1
                    if outer.before_post_callback is not None:
                        outer.before_post_callback()
                    if outer.redirect_next:
                        outer.redirect_next=False
                        self.send_response(302)
                        self.send_header("Location", "https://attacker.example/collect")
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                        self.close_connection=True
                        return
                    if not self._auth():
                        return self._json(401,{"error":{"type":"authentication_error"}})
                    if urlparse(self.path).path != "/v1/refunds":
                        return self._json(404,{"error":{"type":"not_found"}})
                    raw=self.rfile.read(int(self.headers.get("Content-Length","0")))
                    q=parse_qs(raw.decode(),keep_blank_values=True)
                    md={}
                    payload={}
                    for k,v in q.items():
                        value=v[-1]
                        if k.startswith("metadata[") and k.endswith("]"):
                            md[k[9:-1]]=value
                        elif k=="amount":
                            try: payload[k]=int(value)
                            except ValueError: payload[k]=value
                        else: payload[k]=value
                    if md: payload["metadata"]=md
                    key=self.headers.get("Idempotency-Key")
                    if not key:
                        return self._json(400,{"error":{"type":"invalid_request_error","message":"missing idempotency key"}})
                    payload_hash=_canonical(payload)
                    cached=outer.idempotency.get(key)
                    if cached is not None:
                        if cached[0] != payload_hash:
                            return self._json(400,{"error":{"type":"idempotency_error","code":"idempotency_key_reused_with_different_parameters"}})
                        status,body=cached[1],cached[2]
                        return self._json(status,body)
                    mode=outer.next_mode
                    outer.next_mode="normal"
                    if mode=="drop_before_execute":
                        return self._drop()
                    if mode=="cached_500":
                        body={"error":{"type":"api_error","message":"simulated server error"}}
                        outer.idempotency[key]=(payload_hash,500,body)
                        return self._json(500,body)
                    # Narrow simulator requires exactly one charge/payment_intent.
                    if ("charge" in payload) == ("payment_intent" in payload):
                        return self._json(400,{"error":{"type":"invalid_request_error","message":"one target required"}})
                    outer._counter+=1
                    target_key="charge" if "charge" in payload else "payment_intent"
                    target=payload[target_key]
                    refund={"id":f"re_mock_{outer._counter:06d}","object":"refund",
                            "amount":payload.get("amount",5000),target_key:target,
                            "charge":target if target_key=="charge" else "ch_parent_"+str(target),
                            "payment_intent":target if target_key=="payment_intent" else "pi_parent_"+str(target),
                            "currency":"usd","metadata":md,"status":"succeeded","livemode":False}
                    if outer.next_status != "succeeded":
                        refund["status"] = outer.next_status
                    outer.next_status = "succeeded"
                    outer.refunds.insert(0,refund)
                    outer.effect_count+=1
                    outer.idempotency[key]=(payload_hash,200,refund)
                    if mode=="drop_after_commit":
                        return self._drop()
                    return self._json(200,refund)
            def do_GET(self):
                with outer.lock:
                    outer.last_headers = dict(self.headers.items())
                    outer.get_calls += 1
                    parsed=urlparse(self.path)
                    outer.get_paths.append(parsed.path)
                    if not self._auth():
                        return self._json(401,{"error":{"type":"authentication_error"}})
                    if parsed.path.startswith("/v1/charges/") or parsed.path.startswith("/v1/payment_intents/"):
                        if outer.fail_next_resource_read:
                            outer.fail_next_resource_read = False
                            return self._drop()
                        resource_id = parsed.path.rsplit("/",1)[-1]
                        resource = outer.resources.get(resource_id)
                        if resource is None and parsed.path.startswith("/v1/charges/") and resource_id.startswith("ch_"):
                            resource = {"id": resource_id, "object": "charge", "currency": "usd",
                                "livemode": False, "paid": True, "captured": True,
                                "amount": 5000, "amount_refunded": 0, "refunded": False}
                        elif resource is None and parsed.path.startswith("/v1/payment_intents/") and resource_id.startswith("pi_"):
                            resource = {"id": resource_id, "object": "payment_intent", "currency": "usd",
                                "livemode": False, "status": "succeeded", "amount": 5000,
                                "amount_received": 5000, "latest_charge": "ch_parent_" + resource_id}
                        if resource is None:
                            return self._json(404,{"error":{"type":"invalid_request_error","message":"resource not found"}})
                        return self._json(200,dict(resource))
                    if parsed.path.startswith("/v1/refunds/"):
                        rid=parsed.path.rsplit("/",1)[-1]
                        obj=next((x for x in outer.refunds if x["id"]==rid),None)
                        return self._json(200,obj) if obj else self._json(404,{"error":{"type":"invalid_request_error"}})
                    if parsed.path != "/v1/refunds":
                        return self._json(404,{"error":{"type":"not_found"}})
                    q=parse_qs(parsed.query)
                    target_key="charge" if "charge" in q else ("payment_intent" if "payment_intent" in q else None)
                    target=q.get(target_key,[None])[-1] if target_key else None
                    items=[x for x in outer.refunds if target_key is None or x.get(target_key)==target]
                    cursor=q.get("starting_after",[None])[-1]
                    if cursor:
                        index=next((i for i,x in enumerate(items) if x["id"]==cursor),None)
                        if index is None:
                            return self._json(400,{"error":{"type":"invalid_request_error","message":"cursor unknown"}})
                        items=items[index+1:]
                    try: limit=max(1,min(100,int(q.get("limit",[outer.list_page_size])[-1])))
                    except ValueError: limit=outer.list_page_size
                    page=items[:limit]
                    body={"object":"list","url":"/v1/refunds","data":page,"has_more":len(items)>len(page)}
                    if outer.corrupt_next_list:
                        corruption=outer.corrupt_next_list
                        outer.corrupt_next_list=None
                        if corruption=="false_empty": body={"object":"list","data":[],"has_more":False}
                        elif corruption=="true_empty": body={"object":"list","data":[],"has_more":True}
                        elif corruption=="missing_has_more": body={"object":"list","data":page}
                        elif corruption=="duplicate_id" and page: body["data"]=[page[0],page[0]]
                    return self._json(200,body)
        self.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        self.server.daemon_threads=True
        self.url=f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread=threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.05),daemon=True)
    def start(self):
        self.thread.start(); return self
    def close(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=2)
    def __enter__(self): return self.start()
    def __exit__(self,*exc): self.close()
    def fail_next(self,mode):
        if mode not in {"normal","drop_before_execute","drop_after_commit","cached_500"}: raise ValueError(mode)
        with self.lock: self.next_mode=mode
    def seed_refund(self,refund):
        with self.lock: self.refunds.append(dict(refund))
    def set_resource(self, resource_id, resource):
        with self.lock: self.resources[resource_id] = dict(resource)
    def fail_next_resource(self):
        with self.lock: self.fail_next_resource_read = True
    def corrupt_next_listing(self,mode):
        with self.lock: self.corrupt_next_list=mode
