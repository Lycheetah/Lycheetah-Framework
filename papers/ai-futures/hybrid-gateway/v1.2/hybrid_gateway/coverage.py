"""Coverage audits for the v0.5 hybrid gateway.

v0.4 contract binding detects unsupported *admissions* but not model *omissions*:
`[]` can be a syntactically valid extraction even with operator-annotated clauses.
This module audits exactly one model batch against an explicit trusted extraction
plan. All model outputs stay untrusted, and even a READY batch is not authorized.

This is not a natural-language completeness oracle. An unannotated source clause
cannot be counted as missing, and a bad plan can misstate ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import (BoundStage, ContractedHybridPipeline,
                        TrustedContractRegistry, TrustedClause)
from .core import (ClaimProposal, Decision, HybridGateway, SourceDocument,
                   canonical_digest, json_bytes)
from .pipeline import StagedClaim


@dataclass(frozen=True)
class ExtractionPlan:
    """Operator-locked clause expectations for one source / one extraction pass.

    `required` can be empty, meaning the model is supposed to abstain on the
    selected extraction task. This is distinct from never having annotated the
    document; the caller must review that interpretation externally.
    """
    source_id: str
    source_digest: str
    registry_fingerprint: str
    required_contract_fingerprints: tuple[str, ...]

    @classmethod
    def create(cls, registry: TrustedContractRegistry, source_id: str,
               *, selected: tuple[str, ...] | None = None) -> "ExtractionPlan":
        source = registry.registered_source(source_id)
        if source is None:
            raise ValueError("source not in trusted registry")
        authorized = {c.fingerprint for c in registry.contracts_for_source(source_id)}
        chosen = tuple(sorted(authorized)) if selected is None else selected
        if not isinstance(chosen, tuple) or len(set(chosen)) != len(chosen):
            raise ValueError("duplicate or malformed operator extraction plan")
        if not all(isinstance(s, str) and s in authorized for s in chosen):
            raise ValueError("plan refers to unregistered or foreign clause")
        return cls(source_id, source.digest, registry.fingerprint, chosen)

    @property
    def fingerprint(self) -> str:
        return canonical_digest(json_bytes(self.__dict__))


@dataclass(frozen=True)
class CoverageReceipt:
    disposition: str  # READY_FOR_REVIEW / REVIEW_MISSING / REVIEW_UNEXPECTED / REVIEW_DUPLICATE / REVIEW_MIXED
    source_id: str
    source_digest: str
    plan_fingerprint: str
    registry_fingerprint: str
    ledger_head_at_stage: str | None
    expected: int
    received: int
    supported_unique: int
    missing_fingerprints: tuple[str, ...]
    duplicate_fingerprints: tuple[str, ...]
    unexpected_candidate_digests: tuple[str, ...]
    stage_candidate_digests: tuple[str, ...]
    note: str = "Operator-plan conformance only; not real-world completeness or authenticated approval"


@dataclass(frozen=True)
class AuditedBatch:
    receipt: CoverageReceipt
    stages: tuple[BoundStage, ...]


def _fingerprint_candidate(candidate: ClaimProposal) -> str:
    from dataclasses import asdict
    return canonical_digest(json_bytes(asdict(candidate)))


class CoverageAuditor:
    """Inert adapter -> contract coverage -> explicit human review boundary.

    One-shot commits are optimistic: if any admission changes the ledger head,
    remaining stages must be reaudited; this is not a multi-record transaction.
    """

    def __init__(self, gateway: HybridGateway, adapter,
                 registry: TrustedContractRegistry, plan: ExtractionPlan):
        self.gateway = gateway
        self.adapter = adapter
        self.registry = registry
        self.plan = plan
        self._pipeline = ContractedHybridPipeline(gateway, adapter, registry)
        self._assert_plan_valid()

    def _assert_plan_valid(self) -> None:
        doc = self.registry.registered_source(self.plan.source_id)
        if doc is None or doc.digest != self.plan.source_digest:
            raise ValueError("plan source identity changed")
        if self.plan.registry_fingerprint != self.registry.fingerprint:
            raise ValueError("plan registry snapshot changed")
        allowed = {c.fingerprint for c in self.registry.contracts_for_source(self.plan.source_id)}
        if (len(set(self.plan.required_contract_fingerprints)) != len(self.plan.required_contract_fingerprints)
                or not set(self.plan.required_contract_fingerprints) <= allowed):
            raise ValueError("unregistered plan clause")
        if self.gateway.sources.get(doc.source_id) != doc:
            raise ValueError("gateway registered source has changed")

    def audit(self, source: SourceDocument) -> AuditedBatch:
        """Exactly one extraction call; never stages partial results for commit.

        Assumes the adapter only returns ClaimProposal objects, as specified by
        CandidateAdapter; malformed provider output yields a safe exception.
        """
        self._assert_plan_valid()
        if source.source_id != self.plan.source_id or source.digest != self.plan.source_digest:
            raise ValueError("audit source does not match operator plan")
        head = self.gateway.head_digest
        candidates = self.adapter.extract(source)
        if not isinstance(candidates, (list, tuple)) or any(
                not isinstance(p, ClaimProposal) for p in candidates):
            raise ValueError("adapter must produce only typed claim proposals")
        matched: dict[str, list[ClaimProposal]] = {}
        unexpected: list[str] = []
        expected = set(self.plan.required_contract_fingerprints)
        # No model can widen the plan, even by quoting another valid contract.
        for candidate in candidates:
            clause = self.registry.matched_contract(candidate)
            if (candidate.source_id != source.source_id or candidate.tenant != source.tenant
                    or clause is None or clause.fingerprint not in expected):
                unexpected.append(_fingerprint_candidate(candidate))
            else:
                matched.setdefault(clause.fingerprint, []).append(candidate)
        missing = tuple(sorted(expected - set(matched)))
        duplicate = tuple(sorted(fp for fp, xs in matched.items() if len(xs) > 1))
        unexpected = tuple(sorted(unexpected))
        problems = sum(bool(x) for x in (missing, duplicate, unexpected))
        status = ("READY_FOR_REVIEW" if not problems else
                  "REVIEW_MIXED" if problems > 1 else
                  "REVIEW_MISSING" if missing else
                  "REVIEW_DUPLICATE" if duplicate else "REVIEW_UNEXPECTED")
        eligible = tuple((fp, xs[0]) for fp, xs in sorted(matched.items())) if status == "READY_FOR_REVIEW" else ()
        receipt = CoverageReceipt(status, source.source_id, source.digest,
                                  self.plan.fingerprint, self.registry.fingerprint, head,
                                  len(expected), len(candidates), len(matched),
                                  missing, duplicate, unexpected,
                                  tuple(_fingerprint_candidate(candidate) for _, candidate in eligible))
        # A failed batch must not be partially committed. A successful one is
        # *eligible for human review*, NEVER pre-authorized.
        stages = () if status != "READY_FOR_REVIEW" else tuple(
            BoundStage(StagedClaim(candidate, source.digest), fp, self.registry.fingerprint)
            for fp, candidate in eligible)
        if self.gateway.head_digest != head:
            raise RuntimeError("ledger changed during read-only coverage audit")
        return AuditedBatch(receipt, stages)

    def commit_one(self, batch: AuditedBatch, stage_index: int, *, recorded_at: str,
                   reviewer_approved: bool = False) -> Decision:
        """No commit without an explicit caller-controlled review decision.

        Never accept arbitrary stages unbound to a freshly provided batch. This
        remains an in-process trust check, not user authentication or a lock.
        """
        if not isinstance(batch, AuditedBatch) or batch.receipt.disposition != "READY_FOR_REVIEW":
            return Decision("REVIEW", "coverage audit not ready for human review")
        if not isinstance(stage_index, int) or isinstance(stage_index, bool) or not 0 <= stage_index < len(batch.stages):
            return Decision("BLOCK", "invalid audited stage selection")
        self._assert_plan_valid()
        r = batch.receipt
        if (r.source_id != self.plan.source_id or r.source_digest != self.plan.source_digest
                or r.plan_fingerprint != self.plan.fingerprint
                or r.registry_fingerprint != self.registry.fingerprint):
            return Decision("BLOCK", "stale or foreign coverage receipt")
        if self.gateway.head_digest != r.ledger_head_at_stage:
            return Decision("REVIEW", "ledger advanced since coverage audit; re-audit")
        if not reviewer_approved:
            return Decision("REVIEW", "human review is still required")
        # Structural check: reject arbitrary injection of stages into an audited
        # container even though this is NOT an authenticated/hostile-process API.
        stage = batch.stages[stage_index]
        if (len(batch.stages) != len(r.stage_candidate_digests) or
                _fingerprint_candidate(stage.staged.candidate) != r.stage_candidate_digests[stage_index]):
            return Decision("BLOCK", "audited stage or receipt mutated")
        matched = self.registry.matched_contract(stage.staged.candidate)
        if matched is None or matched.fingerprint not in self.plan.required_contract_fingerprints:
            return Decision("BLOCK", "stage is not in operator extraction plan")
        return self._pipeline.commit_one(stage, recorded_at=recorded_at,
                                         reviewer_approved=True)
