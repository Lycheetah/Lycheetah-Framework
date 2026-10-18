"""Bounded, standard-library-only prototype for hybrid evidence revision (not CASCADE core)."""
from .core import (
    HybridGateway, SourceDocument, ClaimProposal, QueryResult, Decision,
    ScriptedNeuralAdapter, SourceRegistrationError, canonical_digest, refund_window_quote_validator,
)
__all__ = ["HybridGateway", "SourceDocument", "ClaimProposal", "QueryResult", "Decision", "ScriptedNeuralAdapter", "SourceRegistrationError", "canonical_digest", "refund_window_quote_validator"]
from .neural import OpenAICompatibleAdapter, ProviderConfig, ExtractionTarget, ExtractionError
__all__ += ["OpenAICompatibleAdapter", "ProviderConfig", "ExtractionTarget", "ExtractionError"]
from .pipeline import HybridPipeline, StagedClaim
from .cascade_bridge import EvidenceWeights, CascadeDiagnostic, diagnose_with_cascade
__all__ += ["HybridPipeline", "StagedClaim", "EvidenceWeights", "CascadeDiagnostic", "diagnose_with_cascade"]
from .contracts import (TrustedClause, TrustedContractRegistry, ContractedHybridPipeline,
                        BoundStage, EvidenceBindingError)
__all__ += ["TrustedClause", "TrustedContractRegistry", "ContractedHybridPipeline", "BoundStage", "EvidenceBindingError"]

from .coverage import ExtractionPlan, CoverageAuditor, CoverageReceipt, AuditedBatch

from .durable import SQLiteLedger
__all__ += ['ExtractionPlan', 'CoverageAuditor', 'CoverageReceipt', 'AuditedBatch', 'SQLiteLedger']
from .evaluation import EvaluationReport, evaluate
__all__ += ['EvaluationReport', 'evaluate']
from .canonical_loader import load_canonical_classes, git_blob_sha, PINNED_GIT_BLOB_SHA1
from .temporal_audit import TemporalCase, CaseAudit, audit_temporal_cases, public_report
__all__ += ['load_canonical_classes', 'git_blob_sha', 'PINNED_GIT_BLOB_SHA1',
            'TemporalCase', 'CaseAudit', 'audit_temporal_cases', 'public_report']
from .sql_temporal_baseline import SQLTemporalBaseline, SQLAnswer
from .isolated_cascade import diagnose_isolated, IsolatedDiagnostic
__all__ += ['SQLTemporalBaseline','SQLAnswer','diagnose_isolated','IsolatedDiagnostic']

from .authorization import ReviewKeyring, SignedBatchApproval, issue_approval, verify_approval
__all__ += ['ReviewKeyring','SignedBatchApproval','issue_approval','verify_approval']

from .review_journal import ReviewJournalAuthority, ReviewDecisionRecord
__all__ += ['ReviewJournalAuthority','ReviewDecisionRecord']
