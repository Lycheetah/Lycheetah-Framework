"""V0.4 trusted clause contracts: evidence binding, not generic natural-language inference.

An operator must identify the applicable EXACT source clause, target, scope,
effective interval, and permitted supersession edges. The model only proposes
values. This deliberately trades annotation effort for auditability. Contract
objects are frozen, but operator/caller trust and source authority are external.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterable

from .core import ClaimProposal, SourceDocument, canonical_digest, json_bytes, utc
from .pipeline import HybridPipeline, StagedClaim


class EvidenceBindingError(ValueError):
    """A whole model batch could not be bound to trusted evidence metadata."""


# Each grammar is an intentionally narrow, whole-clause parser. Unknown expressions
# MUST be reviewed instead of falling back to numeric/string proximity.
_GRAMMARS = {
    "refund_days_v1": re.compile(r"Refunds allowed within (?P<value>[0-9]+) days\."),
    "online_refund_days_v1": re.compile(r"Online orders: refunds within (?P<value>[0-9]+) days\."),
    "loyalty_points_v1": re.compile(r"Loyalty members earn (?P<value>[0-9]+) points per order\."),
}
_GRAMMAR_SLOT = {
    "refund_days_v1": ("refunds", "window_days"),
    "online_refund_days_v1": ("refunds", "window_days"),
    "loyalty_points_v1": ("loyalty", "points_per_order"),
}


@dataclass(frozen=True)
class TrustedClause:
    source_id: str
    source_digest: str
    tenant: str
    subject: str
    predicate: str
    scope: str
    exact_quote: str
    grammar: str
    effective_from: str
    effective_until: str | None = None
    permitted_supersedes: tuple[str, ...] = ()

    def __post_init__(self):
        if (self.grammar not in _GRAMMARS or
                (self.subject, self.predicate) != _GRAMMAR_SLOT[self.grammar]):
            raise ValueError("unknown grammar or wrong claim slot")
        if any(not isinstance(v, str) or not v.strip() for v in
               (self.source_id, self.source_digest, self.tenant, self.subject,
                self.predicate, self.scope, self.exact_quote)):
            raise ValueError("incomplete trusted contract")
        if not isinstance(self.permitted_supersedes, tuple) or any(
                not isinstance(x, str) or not x for x in self.permitted_supersedes):
            raise ValueError("invalid trusted supersession identifiers")
        if len(set(self.permitted_supersedes)) != len(self.permitted_supersedes):
            raise ValueError("duplicate trusted supersession identifiers")
        start = utc(self.effective_from)
        end = utc(self.effective_until) if self.effective_until is not None else None
        if end is not None and end <= start:
            raise ValueError("invalid trusted interval")
        if not _GRAMMARS[self.grammar].fullmatch(self.exact_quote):
            raise ValueError("contract clause fails its whole-clause grammar")

    @property
    def parsed_value(self) -> str:
        return _GRAMMARS[self.grammar].fullmatch(self.exact_quote).group("value")

    @property
    def fingerprint(self) -> str:
        return canonical_digest(json_bytes({
            "source_id": self.source_id, "source_digest": self.source_digest,
            "tenant": self.tenant, "subject": self.subject,
            "predicate": self.predicate, "scope": self.scope,
            "exact_quote": self.exact_quote, "grammar": self.grammar,
            "effective_from": utc(self.effective_from),
            "effective_until": utc(self.effective_until) if self.effective_until else None,
            "permitted_supersedes": self.permitted_supersedes,
        }))

    def validate_source(self, source: SourceDocument) -> bool:
        # Exactly one verbatim instance; repeated/misplaced occurrences require review.
        return (source.source_id == self.source_id and
                source.tenant == self.tenant and
                source.digest == self.source_digest and
                source.body.count(self.exact_quote) == 1)

    def matches(self, candidate: ClaimProposal) -> bool:
        try:
            return (candidate.source_id == self.source_id and
                    candidate.tenant == self.tenant and
                    (candidate.subject, candidate.predicate, candidate.scope) ==
                    (self.subject, self.predicate, self.scope) and
                    candidate.evidence_quote == self.exact_quote and
                    candidate.value == self.parsed_value and
                    utc(candidate.valid_from) == utc(self.effective_from) and
                    (utc(candidate.valid_until) if candidate.valid_until else None) ==
                    (utc(self.effective_until) if self.effective_until else None) and
                    tuple(candidate.supersedes) == self.permitted_supersedes)
        except (ValueError, TypeError, OverflowError):
            return False


class TrustedContractRegistry:
    """Frozen contract snapshot. Bind to same trusted sources used by gateway."""

    def __init__(self, sources: Iterable[SourceDocument], clauses: Iterable[TrustedClause]):
        docs = tuple(sources)
        records = tuple(clauses)
        if not records:
            raise ValueError("no trusted clause contracts")
        self._sources = {s.source_id: s for s in docs}
        if len(self._sources) != len(docs):
            raise ValueError("duplicate source identifiers")
        self._clauses = records
        seen: set[tuple[str, str, str, str, str]] = set()
        for c in records:
            if c.source_id not in self._sources or not c.validate_source(self._sources[c.source_id]):
                raise ValueError("contract is not anchored uniquely in a registered source")
            identity = (c.source_id, c.subject, c.predicate, c.scope, c.exact_quote)
            if identity in seen:
                raise ValueError("duplicate clause authority")
            seen.add(identity)
        self.fingerprint = canonical_digest(json_bytes(sorted(c.fingerprint for c in records)))

    @property
    def sources(self) -> tuple[SourceDocument, ...]:
        return tuple(self._sources.values())

    def contracts_for_source(self, source_id: str) -> tuple[TrustedClause, ...]:
        """Immutable snapshot of the operator-annotated clauses for a registered source.

        This does NOT identify unannotated clauses, or establish whether annotations
        are complete. That is an external ground-truth and governance problem.
        """
        if source_id not in self._sources:
            raise ValueError("unknown source")
        return tuple(c for c in self._clauses if c.source_id == source_id)

    def registered_source(self, source_id: str) -> SourceDocument | None:
        return self._sources.get(source_id)

    def matched_contract(self, candidate: ClaimProposal) -> TrustedClause | None:
        for c in self._clauses:
            if c.matches(candidate) and c.validate_source(self._sources[c.source_id]):
                return c
        return None

    def validate_claim(self, candidate: ClaimProposal) -> bool:
        return self.matched_contract(candidate) is not None


@dataclass(frozen=True)
class BoundStage:
    staged: StagedClaim
    contract_fingerprint: str
    registry_fingerprint: str


class ContractedHybridPipeline(HybridPipeline):
    """Conservative replacement for HybridPipeline with complete-batch contracts.

    Still needs a trusted caller, real identity/reviewer authentication, durable
    storage and an external action gateway. A stamp is NOT a credential or signature.
    """

    def __init__(self, gateway, adapter, registry: TrustedContractRegistry):
        if gateway.semantic_validator is not registry.validate_claim and (
                getattr(gateway.semantic_validator, "__self__", None) is not registry or
                getattr(gateway.semantic_validator, "__func__", None) is not TrustedContractRegistry.validate_claim):
            raise ValueError("gateway must enforce exactly this contract registry")
        super().__init__(gateway, adapter)
        self.registry = registry
        for source in registry.sources:
            if gateway.sources.get(source.source_id) != source:
                raise ValueError("contract source must already be registered, unchanged")

    def stage(self, source: SourceDocument) -> tuple[BoundStage, ...]:
        # Full-batch failure: never retain a partial set of claims.
        staged = super().stage(source)
        bound = []
        for item in staged:
            contract = self.registry.matched_contract(item.candidate)
            if contract is None:
                raise EvidenceBindingError("model candidate not bound to a trusted clause; no batch staged")
            bound.append(BoundStage(item, contract.fingerprint, self.registry.fingerprint))
        return tuple(bound)

    def commit_one(self, staged: BoundStage, *, recorded_at: str, reviewer_approved: bool = False):
        from .core import Decision
        if not isinstance(staged, BoundStage) or staged.registry_fingerprint != self.registry.fingerprint:
            return Decision("BLOCK", "unrecognized trusted contract snapshot")
        if (getattr(self.gateway.semantic_validator, "__self__", None) is not self.registry or
                getattr(self.gateway.semantic_validator, "__func__", None) is not TrustedContractRegistry.validate_claim):
            return Decision("BLOCK", "semantic validator changed after contract staging")
        source_id = staged.staged.candidate.source_id
        if self.gateway.sources.get(source_id) != self.registry.registered_source(source_id):
            return Decision("BLOCK", "registered source identity changed after staging")
        contract = self.registry.matched_contract(staged.staged.candidate)
        if contract is None or contract.fingerprint != staged.contract_fingerprint:
            return Decision("REVIEW", "staged evidence contract no longer matches")
        return super().commit_one(staged.staged, recorded_at=recorded_at,
                                  reviewer_approved=reviewer_approved)
