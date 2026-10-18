"""C006 matched-controls conventional reference, independent pair-selection logic.

Shares authenticated fixture configuration, trust-checkpoint and signature verifier
with candidate. Therefore it is NOT independent implementation/security validation.
"""
from __future__ import annotations
from hashlib import sha256
import hmac
from itertools import combinations
from typing import Mapping, Sequence
from provenance_gate import ProvenanceGate, canonical, object_sha
from governed_registry import GovernedRegistry


def decide(r: GovernedRegistry, envelopes: Sequence[dict], *, trusted_checkpoint: dict | None,
           effect_id: str, action_sha256: str, token_sha256: str, now: int,
           current_revisions: Mapping[str, int] | None,
           provider_receipt_valid: bool = True) -> str:
    integrity, _ = r.verify_history(trusted_checkpoint=trusted_checkpoint)
    if not integrity or not provider_receipt_valid or not envelopes or len(envelopes) > 32:
        return "REVIEW"
    validator = ProvenanceGate(r._registry)
    bodies = {}
    for envelope in envelopes:
        if not isinstance(envelope,dict) or set(envelope) != {"statement", "binding", "binding_mac"}:
            return "REVIEW"
        raw, bound, signature = envelope["statement"], envelope["binding"], envelope["binding_mac"]
        if not isinstance(raw,dict) or not isinstance(raw.get("body"),dict) or not isinstance(bound,dict):
            return "REVIEW"
        if set(bound) != {"statement_sha256","registry_head"}:
            return "REVIEW"
        signer=raw["body"].get("source_id")
        if not isinstance(signer,str) or signer not in r._keys:
            return "REVIEW"
        expect=hmac.new(r._keys[signer],canonical(bound),sha256).hexdigest()
        if not isinstance(signature,str) or not hmac.compare_digest(signature,expect):
            return "REVIEW"
        if bound["registry_head"] != r.head or bound["statement_sha256"] != object_sha(raw):
            return "REVIEW"
        if any(r._depends_on(signer,x) for x in r._challenges):
            return "REVIEW"
        valid,_=validator.verify_one(raw,effect_id=effect_id,action_sha256=action_sha256,
                                     token_sha256=token_sha256,now=now)
        if not valid or signer in bodies:
            return "REVIEW"
        bodies[signer]=raw["body"]
    if current_revisions is None:
        return "REVIEW"
    for signer,body in bodies.items():
        if type(current_revisions.get(signer)) is not int or current_revisions[signer] != body["revision"]:
            return "REVIEW"
    if any(b["correctness"] == "FALSE" or b["status"] == "NOT_COMMITTED" for b in bodies.values()):
        return "CONFLICT"
    if any(b["correctness"] != "TRUE" or b["status"] != "COMMITTED" for b in bodies.values()):
        return "REVIEW"
    # Straight conventional pairwise check, not the C005 backtracking selector.
    for left,right in combinations(bodies,2):
        lr,lc=r._registry.exposure(left)
        rr,rc=r._registry.exposure(right)
        if lr.isdisjoint(rr) and lc.isdisjoint(rc):
            return "CONFIRMED"
    return "REVIEW"
