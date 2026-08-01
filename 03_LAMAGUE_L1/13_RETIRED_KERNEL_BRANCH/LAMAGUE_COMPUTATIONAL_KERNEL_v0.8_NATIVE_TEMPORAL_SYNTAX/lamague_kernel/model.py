from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class NamedText:
    name: str
    text: str

@dataclass(frozen=True)
class UnknownSpec:
    name: str
    protected: bool = True
    required_for: str = ""

@dataclass(frozen=True)
class AuthoritySpec:
    name: str
    scope: str
    description: str = ""

@dataclass(frozen=True)
class DissentSpec:
    party: str
    position: str

@dataclass(frozen=True)
class ValueFlowSpec:
    source: str
    recipient: str
    kind: str
    consent: str = ""

@dataclass(frozen=True)
class EffectSpec:
    name: str
    args: tuple[str, ...] = ()
    def render(self):
        return self.name if not self.args else f"{self.name}<{','.join(self.args)}>"

@dataclass(frozen=True)
class ResolutionSpec:
    unknown: str
    evidence: str

@dataclass(frozen=True)
class ProgramSpec:
    name: str
    version: str = "0.5"
    identity: str = ""
    purpose: str = ""
    claim: str = ""
    path_tokens: tuple[str, ...] = ()
    risk: str = "low"
    irreversible: bool = False
    decoder_confidence: float = 1.0
    evidence: tuple[NamedText, ...] = ()
    unknowns: tuple[UnknownSpec, ...] = ()
    invariants: tuple[NamedText, ...] = ()
    authorities: tuple[AuthoritySpec, ...] = ()
    participants: tuple[str, ...] = ()
    affected_parties: tuple[str, ...] = ()
    boundaries: tuple[NamedText, ...] = ()
    dissent: tuple[DissentSpec, ...] = ()
    value_flows: tuple[ValueFlowSpec, ...] = ()
    recoveries: tuple[NamedText, ...] = ()
    effects: tuple[EffectSpec, ...] = ()
    resolutions: tuple[ResolutionSpec, ...] = ()
    gates: tuple[str, ...] = ()
    horizon: str = ""
    step_limit: int = 128
    requested_compression: bool = False
    yield_text: str = ""
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class SemanticIR:
    language_version: str
    program_name: str
    identity: str
    purpose: str
    claim: str
    operations: tuple[str, ...]
    risk: str
    irreversible: bool
    decoder_confidence: float
    evidence: tuple[NamedText, ...]
    unknowns: tuple[UnknownSpec, ...]
    invariants: tuple[NamedText, ...]
    authorities: tuple[AuthoritySpec, ...]
    participants: tuple[str, ...]
    affected_parties: tuple[str, ...]
    boundaries: tuple[NamedText, ...]
    dissent: tuple[DissentSpec, ...]
    value_flows: tuple[ValueFlowSpec, ...]
    recoveries: tuple[NamedText, ...]
    effects: tuple[EffectSpec, ...]
    resolutions: tuple[ResolutionSpec, ...]
    gates: tuple[str, ...]
    horizon: str
    step_limit: int
    requested_compression: bool
    yield_text: str
    semantic_id: str = ""
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class SemanticState:
    identity: str
    step: int = 0
    last_operation: str = ""
    observed: bool = False
    evidence_bound: tuple[str, ...] = ()
    unresolved_unknowns: tuple[str, ...] = ()
    resolved_unknowns: tuple[str, ...] = ()
    invariants_locked: tuple[str, ...] = ()
    authority_checked: bool = False
    affected_checked: bool = False
    dissent_preserved: tuple[str, ...] = ()
    value_flows_executed: tuple[str, ...] = ()
    anchor: str = ""
    drift_detected: bool = False
    cycle_count: int = 0
    horizon: str = ""
    kernel_active: bool = False
    limit: int = 128
    novelty_detected: bool = False
    proof_status: str = "UNTESTED"
    queries: tuple[str, ...] = ()
    alternative_path: bool = False
    memory_folded: bool = False
    yielded: bool = False
    output: str = ""
    compression_mode: str = "UNDECIDED"
    branch_count: int = 0
    snapshot_count: int = 0
    transition_count: int = 0
    merge_status: str = "UNTESTED"
    notes: tuple[str, ...] = ()
    parent_hash: str = ""
    state_hash: str = ""
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class TraceRecord:
    index: int
    operation: str
    before_hash: str
    after_hash: str
    outcome: str
    detail: str
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class ExecutionReport:
    ir: SemanticIR
    final_state: SemanticState
    trace: tuple[TraceRecord, ...]
    diagnostics: tuple[dict[str, str], ...]
    def to_dict(self):
        return {"ir": self.ir.to_dict(), "final_state": self.final_state.to_dict(), "trace": [x.to_dict() for x in self.trace], "diagnostics": list(self.diagnostics)}
