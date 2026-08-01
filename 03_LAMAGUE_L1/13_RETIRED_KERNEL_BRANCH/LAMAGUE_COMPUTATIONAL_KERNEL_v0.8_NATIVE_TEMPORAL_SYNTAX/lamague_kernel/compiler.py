from __future__ import annotations
from dataclasses import replace
from .errors import CompileFailure, Diagnostic, Severity
from .hashes import semantic_hash
from .model import SemanticIR
from .registry import OPERATIONS, SEALS

RISK_LEVELS={"low","medium","high","critical"}
IRREVERSIBLE_GATES={"affected_party","expert","operator","silent_witness"}

def expand_path(tokens):
    ops=[]
    for token in tokens:
        if token.startswith("@"):
            name=token[1:]
            if name not in SEALS:
                raise CompileFailure((Diagnostic(Severity.FATAL,"UNKNOWN_SEAL",f"Unknown standard-library seal {name!r}."),))
            ops.extend(SEALS[name])
        else: ops.append(token)
    return tuple(ops)

def compile_program(spec):
    ds=[]; ops=expand_path(spec.path_tokens)
    for op in ops:
        if op not in OPERATIONS: ds.append(Diagnostic(Severity.FATAL,"UNKNOWN_OPERATION",f"Operation {op!r} is not registered."))
    if spec.risk not in RISK_LEVELS: ds.append(Diagnostic(Severity.FATAL,"INVALID_RISK_LEVEL",f"Risk level {spec.risk!r} is invalid."))
    if not 0<=spec.decoder_confidence<=1: ds.append(Diagnostic(Severity.FATAL,"INVALID_CONFIDENCE","Decoder confidence must be between 0 and 1."))
    if len(ops)>spec.step_limit: ds.append(Diagnostic(Severity.FATAL,"STEP_LIMIT_EXCEEDED",f"Path has {len(ops)} operations but limit is {spec.step_limit}."))

    consequential = spec.risk in {"medium","high","critical"} or any(e.name in {"MayAffect","TransfersValue","ChangesAuthority","CreatesReversibleRisk","CreatesIrreversibility","CallsExternalSystem"} for e in spec.effects)
    if consequential and not spec.authorities: ds.append(Diagnostic(Severity.FATAL,"AUTHORITY_REQUIRED","Consequential execution has no typed authority."))
    if any(e.name=="MayAffect" for e in spec.effects) and not spec.affected_parties: ds.append(Diagnostic(Severity.FATAL,"AFFECTED_PARTY_REQUIRED","MayAffect requires at least one affected party."))
    if any(e.name=="TransfersValue" for e in spec.effects) and not spec.value_flows: ds.append(Diagnostic(Severity.FATAL,"VALUE_FLOW_REQUIRED","TransfersValue requires a visible valueflow declaration."))
    if any(e.name=="ChangesAuthority" for e in spec.effects) and not spec.authorities: ds.append(Diagnostic(Severity.FATAL,"AUTHORITY_CHANGE_UNTYPED","ChangesAuthority requires typed authority declarations."))
    if any(e.name=="CreatesReversibleRisk" for e in spec.effects) and not spec.recoveries: ds.append(Diagnostic(Severity.FATAL,"RECOVERY_REQUIRED","CreatesReversibleRisk requires at least one recovery path."))

    irreversible=spec.irreversible or any(e.name=="CreatesIrreversibility" for e in spec.effects)
    if irreversible:
        missing=sorted(IRREVERSIBLE_GATES-set(spec.gates))
        if missing: ds.append(Diagnostic(Severity.FATAL,"IRREVERSIBLE_GATES_MISSING","Irreversible execution is missing gates: "+", ".join(missing)))
        if not spec.recoveries: ds.append(Diagnostic(Severity.FATAL,"IRREVERSIBLE_CONTAINMENT_MISSING","Irreversible execution requires containment or recovery declarations."))
        if "G" not in ops: ds.append(Diagnostic(Severity.FATAL,"IRREVERSIBLE_GUARD_MISSING","Irreversible execution must pass through G."))

    if any(e.name=="SuppressesDissent" for e in spec.effects) and spec.dissent: ds.append(Diagnostic(Severity.FATAL,"DISSENT_SUPPRESSION","The program declares dissent and an effect that suppresses it."))
    protected={u.name for u in spec.unknowns if u.protected}
    if protected and "U" not in ops: ds.append(Diagnostic(Severity.FATAL,"PROTECTED_UNKNOWN_NOT_ACTIVATED","Protected unknowns exist but U is absent from the path."))
    if spec.invariants and "I" not in ops: ds.append(Diagnostic(Severity.FATAL,"INVARIANT_NOT_LOCKED","Invariants are declared but I is absent from the path."))
    if spec.evidence and "E" not in ops: ds.append(Diagnostic(Severity.RECOVERABLE,"EVIDENCE_NOT_BOUND","Evidence is declared but E is absent from the path.","Insert E before proof, guard, or yield."))
    if "Y" not in ops: ds.append(Diagnostic(Severity.FATAL,"YIELD_REQUIRED","Every executable program requires Y."))
    if "F" not in ops: ds.append(Diagnostic(Severity.FATAL,"FOLD_REQUIRED","Every executable program requires F to preserve lineage."))
    elif "Y" in ops and ops.index("F")>ops.index("Y"): ds.append(Diagnostic(Severity.FATAL,"FOLD_AFTER_YIELD","F must occur before the final Y."))

    evidence_names={e.name for e in spec.evidence}; unknown_names={u.name for u in spec.unknowns}; resolution_names=set()
    for r in spec.resolutions:
        resolution_names.add(r.unknown)
        if r.unknown not in unknown_names: ds.append(Diagnostic(Severity.FATAL,"RESOLUTION_UNKNOWN_MISSING",f"Resolution references unknown {r.unknown!r}."))
        if r.evidence not in evidence_names: ds.append(Diagnostic(Severity.FATAL,"RESOLUTION_EVIDENCE_MISSING",f"Resolution references evidence {r.evidence!r}."))
    for effect in spec.effects:
        if effect.name=="ResolvesUnknown" and (not effect.args or effect.args[0] not in resolution_names): ds.append(Diagnostic(Severity.FATAL,"UNTYPED_UNKNOWN_RESOLUTION",f"{effect.render()} has no declared resolution rule."))

    if "Z" in ops or spec.requested_compression:
        reasons=[]
        if spec.risk in {"high","critical"}: reasons.append("high-impact context")
        if protected: reasons.append("protected unknowns remain")
        if spec.dissent: reasons.append("dissent remains")
        if spec.decoder_confidence<.80: reasons.append("decoder confidence below 0.80")
        if irreversible: reasons.append("irreversibility")
        if reasons: ds.append(Diagnostic(Severity.RECOVERABLE,"COMPRESSION_MUST_EXPAND","Compression is unsafe: "+", ".join(reasons),"Execute Z as Z_UP and preserve the expanded packet."))
    if not spec.purpose: ds.append(Diagnostic(Severity.ADVISORY,"PURPOSE_UNDECLARED","Program purpose is empty."))
    if not spec.claim: ds.append(Diagnostic(Severity.ADVISORY,"CLAIM_UNDECLARED","Program claim is empty."))

    if any(d.severity is Severity.FATAL for d in ds): raise CompileFailure(tuple(ds))
    ir=SemanticIR(spec.version,spec.name,spec.identity,spec.purpose,spec.claim,ops,spec.risk,irreversible,spec.decoder_confidence,spec.evidence,spec.unknowns,spec.invariants,spec.authorities,spec.participants,spec.affected_parties,spec.boundaries,spec.dissent,spec.value_flows,spec.recoveries,spec.effects,spec.resolutions,spec.gates,spec.horizon,spec.step_limit,spec.requested_compression,spec.yield_text,"")
    ir=replace(ir,semantic_id=semantic_hash(ir.to_dict()))
    return ir,tuple(ds)
