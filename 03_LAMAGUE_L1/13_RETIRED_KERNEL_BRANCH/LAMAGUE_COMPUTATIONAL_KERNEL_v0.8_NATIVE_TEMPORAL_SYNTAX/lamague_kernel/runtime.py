from __future__ import annotations
from dataclasses import replace
from .errors import RuntimeHalt
from .hashes import semantic_hash
from .model import ExecutionReport, SemanticState, TraceRecord

def _rehash(state):
    payload=state.to_dict(); payload["state_hash"]=""
    return replace(state,state_hash=semantic_hash(payload))

class Runtime:
    def execute(self,ir,diagnostics=()):
        state=_rehash(SemanticState(identity=ir.identity,limit=ir.step_limit,horizon=ir.horizon)); trace=[]
        for index,op in enumerate(ir.operations,1):
            if index>ir.step_limit: raise RuntimeHalt("Execution step limit exceeded")
            before=state; state,outcome,detail=self._apply(op,state,ir)
            state=replace(state,step=index,last_operation=op,parent_hash=before.state_hash); state=_rehash(state)
            trace.append(TraceRecord(index,op,before.state_hash,state.state_hash,outcome,detail))
        return ExecutionReport(ir,state,tuple(trace),tuple(d.to_dict() for d in diagnostics))

    def _apply(self,op,s,ir):
        if op=="A":
            anchor=ir.invariants[0].name if ir.invariants else ir.identity; return replace(s,anchor=anchor),"OK",f"Anchored to {anchor}."
        if op=="B": return replace(s,branch_count=max(2,s.branch_count)),"OK","Semantic bridge declared without forced merge."
        if op=="C": return replace(s,cycle_count=s.cycle_count+1),"OK","Bounded cycle advanced."
        if op=="D": return replace(s,drift_detected=True),"OK","Drift marked."
        if op=="E":
            names=tuple(x.name for x in ir.evidence); return replace(s,evidence_bound=names),"OK",f"Bound {len(names)} evidence record(s)."
        if op=="F": return replace(s,memory_folded=True),"OK","State and lineage folded into memory."
        if op=="G":
            if ir.risk in {"medium","high","critical"} and not ir.authorities: raise RuntimeHalt("Guard failed: authority missing")
            if any(e.name=="MayAffect" for e in ir.effects) and not ir.affected_parties: raise RuntimeHalt("Guard failed: affected parties missing")
            if ir.irreversible and set(ir.gates)!={"affected_party","expert","operator","silent_witness"}: raise RuntimeHalt("Guard failed: irreversible gate set incomplete")
            return replace(s,authority_checked=True,affected_checked=bool(ir.affected_parties)),"OK","Authority, affected parties, and gate obligations checked."
        if op=="H": return replace(s,horizon=ir.horizon or "UNDECLARED"),"OK","Horizon bound."
        if op=="I":
            names=tuple(x.name for x in ir.invariants); return replace(s,invariants_locked=names),"OK",f"Locked {len(names)} invariant(s)."
        if op=="J": return replace(s,branch_count=max(2,s.branch_count)),"OK","Junction preserved as distinct branches."
        if op=="K": return replace(s,kernel_active=True),"OK","Kernel initialised."
        if op=="L": return replace(s,limit=ir.step_limit),"OK",f"Limit fixed at {ir.step_limit} step(s)."
        if op=="M":
            if s.unresolved_unknowns and not s.dissent_preserved and ir.dissent: return replace(s,merge_status="BLOCKED"),"BLOCKED","Merge blocked because dissent is not preserved."
            return replace(s,merge_status="SAFE"),"OK","Merge compatibility check passed."
        if op=="N": return replace(s,novelty_detected=True),"OK","Novel semantic content marked."
        if op=="O": return replace(s,observed=True),"OK","Source condition observed."
        if op=="P":
            critical={u.name for u in ir.unknowns if u.required_for and u.name in s.unresolved_unknowns}
            status="UNPROVEN_NO_EVIDENCE" if not s.evidence_bound else ("UNPROVEN_REQUIRED_UNKNOWN" if critical else "SUPPORTED_WITHIN_SCOPE")
            return replace(s,proof_status=status),"OK",status
        if op=="Q":
            qs=tuple(f"What resolves {name}?" for name in s.unresolved_unknowns); return replace(s,queries=qs),"OK",f"Generated {len(qs)} query or queries."
        if op=="R":
            available=set(s.evidence_bound); resolved=[]
            for r in ir.resolutions:
                if r.evidence in available and r.unknown in s.unresolved_unknowns: resolved.append(r.unknown)
            unresolved=tuple(x for x in s.unresolved_unknowns if x not in set(resolved))
            return replace(s,unresolved_unknowns=unresolved,resolved_unknowns=s.resolved_unknowns+tuple(resolved)),"OK",f"Resolved {len(resolved)} unknown(s) through declared evidence."
        if op=="S": return replace(s,snapshot_count=s.snapshot_count+1),"OK","Immutable semantic snapshot created."
        if op=="T":
            if ir.risk in {"medium","high","critical"} and not s.authority_checked: raise RuntimeHalt("Transition blocked: G has not validated authority")
            return replace(s,transition_count=s.transition_count+1),"OK","Authorised transition advanced."
        if op=="U":
            unresolved=tuple(u.name for u in ir.unknowns); return replace(s,unresolved_unknowns=unresolved),"OK",f"Activated {len(unresolved)} typed unknown(s)."
        if op=="V": return replace(s,alternative_path=True),"OK","Alternative path constructed under active invariants."
        if op=="W":
            positions=tuple(f"{d.party}:{d.position}" for d in ir.dissent); return replace(s,dissent_preserved=positions),"OK",f"Preserved {len(positions)} attributable dissent position(s)."
        if op=="X":
            flows=tuple(f"{x.source}->{x.recipient}:{x.kind}" for x in ir.value_flows)
            if any(e.name=="TransfersValue" for e in ir.effects) and not flows: raise RuntimeHalt("Exchange blocked: no value flow declared")
            return replace(s,value_flows_executed=flows),"OK",f"Executed {len(flows)} visible value flow(s)."
        if op=="Y":
            if not s.memory_folded: raise RuntimeHalt("Yield blocked: F has not preserved lineage")
            if ir.risk in {"medium","high","critical"} and not s.authority_checked: raise RuntimeHalt("Yield blocked: authority has not passed G")
            output=ir.yield_text or ir.claim or "BOUNDED_OUTPUT"; return replace(s,yielded=True,output=output),"OK","Bounded output yielded."
        if op=="Z":
            reasons=[]
            if ir.risk in {"high","critical"}: reasons.append("high-impact context")
            if s.unresolved_unknowns: reasons.append("unresolved unknowns")
            if ir.dissent: reasons.append("dissent")
            if ir.decoder_confidence<.80: reasons.append("low decoder confidence")
            if ir.irreversible: reasons.append("irreversibility")
            mode="Z_UP" if reasons else "Z_DOWN"; detail="Expand: "+", ".join(reasons) if reasons else "Compression permitted with recovery."
            return replace(s,compression_mode=mode),"OK",detail
        raise RuntimeHalt(f"Unimplemented operation {op}")
