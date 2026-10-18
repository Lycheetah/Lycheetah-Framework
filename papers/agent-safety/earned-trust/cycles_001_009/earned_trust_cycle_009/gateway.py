"""Trusted C009 adapter to Cycle 008 synthetic authority and protected provider.

NOT wired to real Lycheetah Framework. This is a reference boundary contract.
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from protected_provider import CapabilityIssuer
from upstream_dispatch_fence import canonical


@dataclass(frozen=True)
class GatewayOutcome:
    status:str
    reason:str
    receipt:dict|None=None


class DispatchGateway:
    def __init__(self,authority,issuer:CapabilityIssuer,provider_url:str):
        if not provider_url.startswith('http://127.0.0.1:'):
            raise ValueError('lab gateway only supports loopback provider')
        self.authority=authority;self.issuer=issuer;self.provider_url=provider_url
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def submit(self,effect_id:str,action:dict,witness:dict,now:int, *, simulate_lost_response=False)->GatewayOutcome:
        decision=self.authority.reserve_send(effect_id,action,witness,now)
        if not decision.allowed:
            return GatewayOutcome('REVIEW',decision.reason)
        cap=self.issuer.mint(effect_id,action,decision.audit_seq)
        req=urllib.request.Request(self.provider_url+'/v1/execute',data=canonical({'action':action,'capability':cap}),
                                   headers={'Content-Type':'application/json'},method='POST')
        try:
            with self.opener.open(req,timeout=3) as resp:
                result=json.loads(resp.read())
                if resp.status!=201 and resp.status!=200:
                    return GatewayOutcome('UNKNOWN','provider-not-confirmed')
            if simulate_lost_response:
                return GatewayOutcome('UNKNOWN','lost-provider-response-after-commit')
            if not self.authority.acknowledge(effect_id,result):
                return GatewayOutcome('UNKNOWN','receipt-rejected-by-authority')
            return GatewayOutcome('SUCCEEDED','signed-provider-acknowledged',result)
        except (urllib.error.URLError,TimeoutError,ValueError,OSError):
            return GatewayOutcome('UNKNOWN','network-or-provider-outcome-unknown')
