"""Conservative, auditable primitives for Anon Politician Policy Lab v0.1.

This module structures review; it does not rank policies, infer public consensus, or
make policy decisions. It is intentionally model-agnostic and uses no external API.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any, Iterable

EVIDENCE_TYPES = {"fact", "forecast", "value", "public_preference", "assumption", "unknown"}
CLAIM_STATUSES = {"proposed", "supported", "contested", "superseded", "unknown"}

@dataclass
class EvidenceItem:
    evidence_id: str
    description: str
    evidence_type: str
    source_url: str = ""
    source_date: str = ""
    limitations: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.evidence_id.strip(): errors.append("evidence_id is required")
        if self.evidence_type not in EVIDENCE_TYPES: errors.append(f"invalid evidence_type: {self.evidence_type}")
        if self.evidence_type in {"fact", "forecast"} and not self.source_url.strip():
            errors.append(f"{self.evidence_id}: factual/forecast evidence needs a source URL or an explicit documented reason for none")
        if self.evidence_type == "forecast" and not self.limitations.strip():
            errors.append(f"{self.evidence_id}: forecast limitations must be recorded")
        return errors

@dataclass
class Claim:
    claim_id: str
    text: str
    claim_type: str  # factual, forecast, value, preference, assumption
    status: str = "proposed"
    depends_on: list[str] | None = None
    source_ids: list[str] | None = None

    def validate(self) -> list[str]:
        errors = []
        if not self.claim_id.strip(): errors.append("claim_id is required")
        if self.claim_type not in {"factual", "forecast", "value", "preference", "assumption"}:
            errors.append(f"{self.claim_id}: invalid claim_type")
        if self.status not in CLAIM_STATUSES: errors.append(f"{self.claim_id}: invalid status")
        return errors

def review_queue(changed_claim_id: str, claims: Iterable[Claim]) -> list[str]:
    """Return transitive dependants requiring review; never edits/deletes claims.

    Edges are represented as claim.depends_on = the IDs it relies upon.
    Output excludes the changed claim itself, is deterministic, and handles cycles.
    """
    claim_list = list(claims)
    known = {c.claim_id for c in claim_list}
    if changed_claim_id not in known:
        raise KeyError(f"Unknown claim ID: {changed_claim_id}")
    reverse: dict[str, set[str]] = defaultdict(set)
    for claim in claim_list:
        for dependency in (claim.depends_on or []):
            if dependency in known:
                reverse[dependency].add(claim.claim_id)
    seen = {changed_claim_id}
    queue = deque([changed_claim_id])
    affected: set[str] = set()
    while queue:
        current = queue.popleft()
        for dependent in sorted(reverse[current]):
            if dependent not in seen:
                seen.add(dependent)
                affected.add(dependent)
                queue.append(dependent)
    return sorted(affected)

def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Validate core structure while preserving unresolved and contradictory content."""
    errors: list[str] = []
    for field in ("case_id", "title", "policy_question", "decision_owner", "last_updated"):
        if not str(packet.get(field, "")).strip(): errors.append(f"packet.{field} is required")
    if packet.get("authority_mode") not in {"advisory", "consultative", "legally_binding"}:
        errors.append("authority_mode must be advisory, consultative, or legally_binding")
    if packet.get("authority_mode") == "legally_binding" and not packet.get("legal_basis"):
        errors.append("legally_binding mode requires a documented legal_basis")
    for item in packet.get("evidence", []):
        try: obj = EvidenceItem(**item)
        except TypeError as exc:
            errors.append(f"evidence item shape invalid: {exc}")
            continue
        errors.extend(obj.validate())
    claims = []
    for item in packet.get("claims", []):
        try: claim = Claim(**item)
        except TypeError as exc:
            errors.append(f"claim item shape invalid: {exc}")
            continue
        claims.append(claim)
        errors.extend(claim.validate())
    ids = [c.claim_id for c in claims]
    if len(ids) != len(set(ids)): errors.append("claim IDs must be unique")
    known_ids = set(ids)
    for claim in claims:
        for dep in claim.depends_on or []:
            if dep not in known_ids: errors.append(f"{claim.claim_id}: unknown dependency {dep}")
        for src in claim.source_ids or []:
            if src not in {e.get("evidence_id") for e in packet.get("evidence", [])}:
                errors.append(f"{claim.claim_id}: unknown source_id {src}")
    # A public opinion signal cannot automatically be treated as a representative consensus.
    public = packet.get("public_input", {})
    if public.get("sample_type") == "open_voluntary" and public.get("representative_claim"):
        errors.append("open voluntary input cannot be labelled representative without a documented sampling/adjustment method")
    # A model-generated recommendation can never silently become a decision.
    if packet.get("decision_status") == "adopted_by_ai":
        errors.append("AI cannot be the accountable decision-maker; record a human decision owner and rationale")
    return errors

def packet_summary(packet: dict[str, Any]) -> dict[str, Any]:
    """Produce an audit summary without creating scores or recommendations."""
    return {
        "case_id": packet.get("case_id"),
        "title": packet.get("title"),
        "claim_count": len(packet.get("claims", [])),
        "evidence_count": len(packet.get("evidence", [])),
        "unresolved_claims": [c.get("claim_id") for c in packet.get("claims", []) if c.get("status") in {"proposed", "contested", "unknown"}],
        "public_input_status": packet.get("public_input", {}).get("status", "not collected"),
        "decision_status": packet.get("decision_status", "not recorded"),
        "policy_recommendation": None,
        "warning": "This summary describes the record. It does not evaluate or rank policy options.",
    }
