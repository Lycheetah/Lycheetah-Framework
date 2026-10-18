"""Safe boundary between neural extraction, review, and the bitemporal ledger.

Stages are inert; commits require independently supplied trusted-caller approval.
Caller booleans are not identity authentication: this is a reference protocol only.
"""
from __future__ import annotations
from dataclasses import dataclass
from .core import HybridGateway, ClaimProposal, SourceDocument, Decision, CandidateAdapter


@dataclass(frozen=True)
class StagedClaim:
    candidate: ClaimProposal
    registered_source_digest: str


class HybridPipeline:
    def __init__(self, gateway: HybridGateway, adapter: CandidateAdapter):
        if gateway.semantic_validator is None:
            raise ValueError("pipeline requires a separate domain-specific semantic validator")
        self.gateway = gateway
        self.adapter = adapter

    def stage(self, source: SourceDocument) -> tuple[StagedClaim, ...]:
        registered = self.gateway.sources.get(source.source_id)
        if registered != source:
            raise ValueError("operator must pre-register unchanged source in trusted registry")
        # Model gets no ability to write to the ledger or source registry.
        candidates = self.adapter.extract(source)
        if any(p.source_id != source.source_id or p.tenant != source.tenant for p in candidates):
            raise ValueError("adapter returned out-of-bound source or tenant")
        return tuple(StagedClaim(p, source.digest) for p in candidates)

    def commit_one(self, staged: StagedClaim, *, recorded_at: str,
                   reviewer_approved: bool = False) -> Decision:
        source = self.gateway.sources.get(staged.candidate.source_id)
        if source is None or source.digest != staged.registered_source_digest:
            return Decision("BLOCK", "source registry no longer matches staged evidence")
        return self.gateway.ingest(staged.candidate, recorded_at=recorded_at,
                                   reviewer_approved=reviewer_approved)
