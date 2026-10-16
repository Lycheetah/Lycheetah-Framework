"""Provisional CASCADE review engine for Anon Politician.

This module builds an auditable review queue, not an autonomous truth engine.

Safety posture:
- Dependency changes trigger review of downstream claims.
- Explicitly contradictory claims and their dependents also enter review.
- No claim is automatically promoted, demoted, archived, or deleted.
- Claim status changes require a timestamped actor and non-empty rationale.
- Normative commitments are not treated as empirical proof.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set

ALLOWED_CLAIM_TYPES = {
    "empirical_claim",
    "empirical_hypothesis",
    "normative_commitment",
    "definition",
    "policy_proposal",
    "reported_result",
    "methodological_rule",
    "source_characterisation",
    "model_output",
}

ALLOWED_STATUSES = {
    "source_asserted",
    "pending_review",
    "supported_within_scope",
    "mixed_evidence",
    "contradicted_within_scope",
    "superseded",
    "withdrawn",
    "historical_only",
}


@dataclass
class KnowledgeBlock:
    block_id: str
    content: str
    claim_type: str
    status: str = "pending_review"
    dependencies: List[str] = field(default_factory=list)
    contradicts: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    provenance_ids: List[str] = field(default_factory=list)
    review_required: bool = False
    history: List[dict] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.block_id, str) or not self.block_id.strip():
            raise ValueError("block_id must be a non-empty string")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError(f"{self.block_id}: content must be a non-empty string")
        if self.claim_type not in ALLOWED_CLAIM_TYPES:
            raise ValueError(f"{self.block_id}: unsupported claim_type {self.claim_type!r}")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"{self.block_id}: unsupported status {self.status!r}")
        if self.block_id in self.dependencies:
            raise ValueError(f"{self.block_id}: self-dependency is not allowed")
        if self.block_id in self.contradicts:
            raise ValueError(f"{self.block_id}: a block cannot contradict itself")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError(f"{self.block_id}: duplicate dependency IDs")
        if len(self.contradicts) != len(set(self.contradicts)):
            raise ValueError(f"{self.block_id}: duplicate contradiction IDs")


@dataclass
class CascadeReview:
    changed_block_id: str
    affected_block_ids: List[str]
    reason: str
    automatic_status_changes: List[str] = field(default_factory=list)
    affected_reasons: Dict[str, List[str]] = field(default_factory=dict)


class KnowledgeGraph:
    def __init__(self, blocks: List[KnowledgeBlock]):
        self.blocks: Dict[str, KnowledgeBlock] = {b.block_id: b for b in blocks}
        if len(self.blocks) != len(blocks):
            raise ValueError("Duplicate block_id")
        for block in blocks:
            missing = set(block.dependencies + block.contradicts) - set(self.blocks)
            if missing:
                raise ValueError(f"{block.block_id} references missing blocks: {sorted(missing)}")

    def dependents_of(self, block_id: str) -> Set[str]:
        if block_id not in self.blocks:
            raise KeyError(block_id)
        return {
            block.block_id for block in self.blocks.values()
            if block_id in block.dependencies
        }

    def transitive_dependents_of(self, block_id: str) -> Set[str]:
        """Return transitive dependents; safe against cycles in the graph."""
        if block_id not in self.blocks:
            raise KeyError(block_id)
        seen: Set[str] = set()
        frontier = list(self.dependents_of(block_id))
        while frontier:
            current = frontier.pop()
            if current == block_id or current in seen:
                continue
            seen.add(current)
            frontier.extend(self.dependents_of(current) - seen - {block_id})
        return seen

    def contradiction_neighbors(self, block_id: str) -> Set[str]:
        """Return explicit contradiction links in either direction."""
        if block_id not in self.blocks:
            raise KeyError(block_id)
        neighbors = set(self.blocks[block_id].contradicts)
        neighbors.update(
            block.block_id for block in self.blocks.values()
            if block_id in block.contradicts
        )
        neighbors.discard(block_id)
        return neighbors

    def propose_cascade(self, changed_block_id: str, reason: str) -> CascadeReview:
        """Create a review closure across dependencies and explicit contradictions.

        The traversal is conservative: when a block enters review, its dependents
        and explicit contradiction partners enter review too, as do their
        dependents. This may include a false-positive review task, so utility must
        be evaluated with precision/recall tests. It never changes epistemic status.
        """
        if changed_block_id not in self.blocks:
            raise KeyError(changed_block_id)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("A non-empty reason is required to propose a cascade")

        seen: Set[str] = {changed_block_id}
        frontier = [changed_block_id]
        reasons: Dict[str, List[str]] = {}

        while frontier:
            current = frontier.pop()
            candidates = []
            candidates.extend((node, f"depends on {current}") for node in self.dependents_of(current))
            candidates.extend((node, f"has an explicit contradiction link with {current}")
                             for node in self.contradiction_neighbors(current))
            for node, why in candidates:
                if node == changed_block_id:
                    continue
                reasons.setdefault(node, [])
                if why not in reasons[node]:
                    reasons[node].append(why)
                if node not in seen:
                    seen.add(node)
                    frontier.append(node)

        affected = sorted(seen - {changed_block_id})
        for block_id in affected:
            self.blocks[block_id].review_required = True

        return CascadeReview(
            changed_block_id=changed_block_id,
            affected_block_ids=affected,
            reason=reason.strip(),
            automatic_status_changes=[],
            affected_reasons={key: reasons[key] for key in affected},
        )

    def record_decision(self, block_id: str, new_status: str, rationale: str,
                        timestamp: str, actor: str):
        """Record an explicit human/reviewer decision with a minimal audit trail."""
        if block_id not in self.blocks:
            raise KeyError(block_id)
        if new_status not in ALLOWED_STATUSES:
            raise ValueError(f"Unsupported status {new_status!r}")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("A non-empty rationale is required")
        if not isinstance(actor, str) or not actor.strip():
            raise ValueError("A non-empty actor identifier is required")
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise ValueError("An ISO-8601 timestamp is required")
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("timestamp must be ISO-8601") from exc

        block = self.blocks[block_id]
        prior = block.status
        block.status = new_status
        block.review_required = False
        block.history.append({
            "event": "status_decision",
            "timestamp": timestamp,
            "actor": actor.strip(),
            "reason": rationale.strip(),
            "prior_status": prior,
            "new_status": new_status,
        })

    def conflicts(self):
        """Return explicitly recorded contradiction links without resolving them."""
        return [
            (block.block_id, target)
            for block in self.blocks.values()
            for target in block.contradicts
        ]
