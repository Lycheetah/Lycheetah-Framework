"""Equal-controls comparator, independently written decision path.

Shares registry and authenticated-input verifier with reference; *not*
independent codebase, field benchmark, or demonstration of superiority.
"""
from itertools import combinations
from provenance_gate import ProvenanceGate, Verdict


def conventional_decide(registry, claims, *, effect_id, action_sha256, token_sha256,
                        now, current_revisions, provider_receipt_valid=True,
                        min_independent=2, max_age=30):
    verifier=ProvenanceGate(registry,max_age=max_age)
    if not provider_receipt_valid:
        return 'REVIEW'
    if current_revisions is None or not isinstance(claims,(tuple,list)) or not 0<len(claims)<=32:
        return 'REVIEW'
    gathered={}
    for claim in claims:
        ok,_=verifier.verify_one(claim,effect_id=effect_id,action_sha256=action_sha256,
                                  token_sha256=token_sha256,now=now)
        if not ok:
            return 'REVIEW'
        sid=claim['body']['source_id']
        if sid in gathered:
            return 'REVIEW'
        gathered[sid]=claim['body']
    if any(type(current_revisions.get(sid)) is not int or
           current_revisions[sid]!=body['revision'] for sid,body in gathered.items()):
        return 'REVIEW'
    if any(x['correctness']=='FALSE' or x['status']=='NOT_COMMITTED' for x in gathered.values()):
        return 'CONFLICT'
    if any(x['correctness']=='UNKNOWN' or x['status']=='UNKNOWN' for x in gathered.values()):
        return 'REVIEW'
    good=[sid for sid,b in gathered.items() if b['correctness']=='TRUE' and b['status']=='COMMITTED']
    for combo in combinations(sorted(good),min_independent):
        root_sets,controller_sets=zip(*(registry.exposure(sid) for sid in combo))
        if sum(map(len,root_sets))==len(set().union(*root_sets)) and sum(map(len,controller_sets))==len(set().union(*controller_sets)):
            return 'CONFIRMED'
    return 'REVIEW'
