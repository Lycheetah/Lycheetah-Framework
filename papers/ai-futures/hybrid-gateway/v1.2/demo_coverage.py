"""Demonstrates a v0.4 silent omission versus the v0.5 audit; no network."""
from hybrid_gateway import (
    HybridGateway, ScriptedNeuralAdapter, TrustedContractRegistry,
    ContractedHybridPipeline, CoverageAuditor, ExtractionPlan,
)
from run_coverage_eval import SOURCE, CLAUSES, propose, DATE

g = HybridGateway(semantic_validator=None)
registry = TrustedContractRegistry([SOURCE], CLAUSES)
g.semantic_validator = registry.validate_claim
g.register_source(SOURCE)
# A model outputs one real, correctly attributed claim but omits the other.
model = ScriptedNeuralAdapter('scripted-not-a-model',{SOURCE.source_id:[propose('refund','model-refund')]})
legacy = ContractedHybridPipeline(g,model,registry)
print('v0.4: accepted stages despite a missed loyalty policy:', len(legacy.stage(SOURCE)))
audit = CoverageAuditor(g,model,registry,ExtractionPlan.create(registry,SOURCE.source_id))
batch = audit.audit(SOURCE)
print('v0.5:',batch.receipt.disposition,'expected:',batch.receipt.expected,
      'found:',batch.receipt.supported_unique,'missing:',len(batch.receipt.missing_fingerprints))
print('No mutation:',g.head_digest is None,'eligible stages:',len(batch.stages))
# A complete extraction is review-eligible, not automatically admitted.
model.candidates[SOURCE.source_id]=[propose('refund','model-refund'),propose('loyalty','model-loyalty')]
full=audit.audit(SOURCE)
print('after complete re-extraction:',full.receipt.disposition)
print('without approval:',audit.commit_one(full,0,recorded_at='2026-10-04T00:00:00Z').disposition)
print('after trusted-caller review of first item:',audit.commit_one(full,0,
      recorded_at='2026-10-04T00:00:00Z',reviewer_approved=True).disposition)
print('stale second item:',audit.commit_one(full,1,recorded_at='2026-10-04T00:00:00Z',
      reviewer_approved=True).disposition, '(must re-audit)')
