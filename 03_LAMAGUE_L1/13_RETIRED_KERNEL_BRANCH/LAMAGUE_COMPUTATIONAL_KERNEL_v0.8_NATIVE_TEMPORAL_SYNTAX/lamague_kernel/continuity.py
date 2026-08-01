from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ContinuityResult:
    classification: str
    lost_fields: tuple[str,...]
    added_fields: tuple[str,...]
    explanation: str
    def to_dict(self): return {"classification":self.classification,"lost_fields":list(self.lost_fields),"added_fields":list(self.added_fields),"explanation":self.explanation}

def _protected(report):
    ir=report["ir"]; final=report["final_state"]
    return {
        "invariants":set(final.get("invariants_locked",[])),
        "unknowns":set(final.get("unresolved_unknowns",[]))|set(final.get("resolved_unknowns",[])),
        "authority":{f"{x['name']}::{x['scope']}" for x in ir.get("authorities",[])},
        "affected_parties":set(ir.get("affected_parties",[])),
        "dissent":{f"{x['party']}::{x['position']}" for x in ir.get("dissent",[])},
        "recoveries":{x["name"] for x in ir.get("recoveries",[])},
    }

def classify(parent,child):
    p=_protected(parent); c=_protected(child); lost=[]; added=[]
    for field in sorted(p):
        lost += [f"{field}:{v}" for v in sorted(p[field]-c[field])]
        added += [f"{field}:{v}" for v in sorted(c[field]-p[field])]
    same=parent["ir"].get("identity")==child["ir"].get("identity")
    invariant_loss=any(x.startswith("invariants:") for x in lost)
    if lost and same and invariant_loss: cls="IMPOSTOR"; exp="The child claims the same identity after losing a protected invariant."
    elif lost: cls="FORK"; exp="The child loses protected semantic fields and must remain visibly forked."
    elif added: cls="DESCENDANT"; exp="The child preserves the parent and adds protected structure."
    else: cls="CONTINUATION"; exp="Protected semantic commitments remain equivalent."
    return ContinuityResult(cls,tuple(lost),tuple(added),exp)
