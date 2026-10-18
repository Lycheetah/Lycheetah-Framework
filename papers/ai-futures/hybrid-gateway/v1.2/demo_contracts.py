"""Cycle 4: single-file, offline demo of a governed extraction candidate.

Run from this directory: python demo_contracts.py
No real LLM, customer data, network, authenticated approval or tool execution.
"""
from hybrid_gateway import (
    SourceDocument, ClaimProposal, ScriptedNeuralAdapter, HybridGateway,
    TrustedClause, TrustedContractRegistry, ContractedHybridPipeline,
    EvidenceBindingError,
)

WHEN = "2026-10-01T00:00:00Z"
source = SourceDocument("document-1", "fictional-store", "urn:fictional:policies",
    "Refunds allowed within 14 days. Loyalty members earn 21 points per order. "
    "EXAMPLE ONLY: Refunds allowed within 60 days.")
contract = TrustedClause(source.source_id, source.digest, source.tenant,
    "refunds", "window_days", "in_store", "Refunds allowed within 14 days.",
    "refund_days_v1", WHEN)
registry = TrustedContractRegistry([source], [contract])
gateway = HybridGateway(semantic_validator=registry.validate_claim)
gateway.register_source(source)


def run_candidate(identifier, quote, value):
    candidate = ClaimProposal(identifier, source.tenant, "refunds", "window_days",
        "in_store", value, WHEN, source.source_id, quote)
    pipeline = ContractedHybridPipeline(gateway, ScriptedNeuralAdapter("offline-fixture", {
        source.source_id: [candidate],
    }), registry)
    try:
        stage = pipeline.stage(source)[0]
    except EvidenceBindingError:
        print(identifier, "REVIEW: candidate not bound to trusted policy clause")
        return
    print(identifier, "STAGED:", stage.staged.candidate.value)
    decision = pipeline.commit_one(stage, recorded_at="2026-10-03T00:00:00Z")
    print(identifier, "WITHOUT_REVIEW:", decision.disposition)
    # This boolean is only a stand-in for the future authenticated reviewer.
    decision = pipeline.commit_one(stage, recorded_at="2026-10-03T00:00:00Z",
                                   reviewer_approved=True)
    print(identifier, "TRUSTED_CALLER_APPROVED:", decision.disposition)


run_candidate("example-60", "Refunds allowed within 60 days.", "60")
run_candidate("actual-14", "Refunds allowed within 14 days.", "14")
for known in ("2026-10-02T00:00:00Z", "2026-10-04T00:00:00Z"):
    result = gateway.query(tenant="fictional-store", subject="refunds", predicate="window_days",
        scope="in_store", effective_at="2026-10-04T00:00:00Z", known_at=known)
    print("KNOWN_AT", known, "=>", result.disposition, result.value)
print("CHAIN_OK:", gateway.verify_chain(anchored_head=gateway.head_digest))
