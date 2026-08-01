# Required LAMAGUE Operation Definitions

Only the primitive operations used in Experiment 001 are included.

## E — Evidence

Attach or inspect evidence without treating evidence as certainty.

Accepts: `Claim, SourceSet`  
Returns: `EvidenceRecord`

## F — Fold

Fold a state into recoverable memory while preserving lineage and residue.

Accepts: `History, Kernel`  
Returns: `State`

## G — Guard

Guard boundaries, authority, consent, and protected conditions before passage.

Accepts: `Predicate, Action, Fallback`  
Returns: `Action`

## I — Invariant

Declare or preserve an invariant that must survive transformation.

Accepts: `Predicate, Scope`  
Returns: `Invariant`

## O — Observe

Observe the stated target, context, or condition without silently changing it.

Accepts: `Target, ObserverContext`  
Returns: `Snapshot`

## P — Prove

Prove only to the degree supported by visible evidence and unresolved unknowns.

Accepts: `Claim, Evidence, InvariantSet`  
Returns: `ProofStatus`

## U — Unknown

Mark unresolved information explicitly and preserve its type.

Accepts: `Type`  
Returns: `Unknown`

## V — Vector Invert

Vector-invert a blocked or conflicting route into an alternative that preserves intent and constraints.

Accepts: `FailedPath, Intent`  
Returns: `AlternativeSet`

## W — Weave

Weave participants or positions into coordination without merging their identities.

Accepts: `AgentSet, Provenance, BoundaryPolicy`  
Returns: `RelationalGraph`

## X — Exchange

Record a directional exchange of value, data, cost, consent, and reversibility.

Accepts: `Agent, Agent, Resource, LedgerPolicy`  
Returns: `LedgerUpdate`

## Y — Yield

Yield the resulting state, including scope, proof status, unknowns, dissent, and value flow.

Accepts: `Value, ProofStatus`  
Returns: `Output`

## Z — Compress

Compress only when meaning remains recoverable; otherwise force semantic expansion.

Accepts: `Expression, InvariantSet, CompressionLevel`  
Returns: `Expression`
