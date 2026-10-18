"""Optional read-only interoperability probe for canonical CASCADE classes.

No heuristic Π scores are generated. Caller provides externally justified calibration
and the genuine CASCADE constructors. This bridge cannot authorize fact changes.
CASCADE uses paradigm-difference as a contradiction proxy, so outputs are diagnostics
only and MUST NOT override scoped bitemporal ledger answers.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping
import json
import math
from dataclasses import asdict

from .core import canonical_digest, json_bytes

from .core import HybridGateway, QueryResult


@dataclass(frozen=True)
class EvidenceWeights:
    evidence_strength: float
    explanatory_power: float
    uncertainty: float

    def __post_init__(self):
        a, b, c = self.evidence_strength, self.explanatory_power, self.uncertainty
        if not (all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (a, b, c))
                and 0 <= a <= 1 and 1 <= b <= 3 and 0 < c <= 1):
            raise ValueError("explicit CASCADE weights outside documented bounds")


@dataclass(frozen=True)
class CascadeDiagnostic:
    query_disposition: str
    claim_ids: tuple[str, ...]
    event_count: int
    diagnostic_coherence: float | None
    disclaimer: str = "CASCADE heuristic diagnostic, NOT authority or validated fact resolution"


def diagnose_with_cascade(gateway: HybridGateway, *, tenant: str, subject: str,
                          predicate: str, scope: str, effective_at: str, known_at: str,
                          calibrated_weights: Mapping[str, EvidenceWeights],
                          engine_factory: Callable, block_factory: Callable) -> CascadeDiagnostic:
    """Maps ONLY the ledger's surviving temporally visible citations into CASCADE.

    Adapters are injected rather than copying/rewriting the canonical CASCADE engine;
    callers pass CascadeEngine and KnowledgeBlock from the original Lycheetah repo.
    Missing weights prevent the analysis, rather than inventing a confidence score.
    """
    before_head = gateway.head_digest
    before_snapshot = gateway_snapshot_digest(gateway)
    result: QueryResult = gateway.query(tenant=tenant, subject=subject,
        predicate=predicate, scope=scope, effective_at=effective_at, known_at=known_at)
    refs = result.citations
    missing = [r["claim_id"] for r in refs if r["claim_id"] not in calibrated_weights]
    if missing:
        raise ValueError("missing independently supplied CASCADE weights for: " + ", ".join(missing))
    eng = engine_factory()
    for ref in refs:
        claim = gateway.claims[ref["claim_id"]]
        w = calibrated_weights[claim.claim_id]
        namespace = json.dumps([tenant, subject, predicate, scope], separators=(",", ":"))
        block = block_factory(id=claim.claim_id, content=claim.content if hasattr(claim, "content") else claim.value,
                              domain=namespace, paradigm=claim.value,
                              evidence_strength=w.evidence_strength,
                              explanatory_power=w.explanatory_power, uncertainty=w.uncertainty)
        eng.add_block(block)
    if gateway.head_digest != before_head or gateway_snapshot_digest(gateway) != before_snapshot:
        raise RuntimeError("gateway state mutated during read-only CASCADE diagnostic")
    coherence = eng.coherence() if refs else None
    return CascadeDiagnostic(result.disposition, tuple(r["claim_id"] for r in refs),
                             len(eng.cascade_events) if refs else 0, coherence)


def gateway_snapshot_digest(gateway: HybridGateway) -> str:
    """Structural snapshot beyond event-head checking. Not hostile-process isolation.

    We intentionally include time-index and withdrawal state because an injected
    engine could corrupt queries while leaving the chained event head untouched.
    """
    snapshot = {
        "sources": {k: asdict(v) for k, v in sorted(gateway.sources.items())},
        "claims": {k: asdict(v) for k, v in sorted(gateway.claims.items())},
        "admitted_at": gateway.admitted_at,
        "by_key": [(list(k), sorted(v)) for k, v in sorted(gateway._by_key.items())],
        "withdrawals": gateway._withdrawals,
        "events": gateway.events,
        "latest_at": gateway._latest_at,
    }
    return canonical_digest(json_bytes(snapshot))
