"""Agent Context Compaction Shield.

Exports independent context snapshots and compares the codec's ten-field critical
projection during compaction. Equivalence is not a general safety guarantee or
proof that the declared context is complete or true.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any

from .codec import (
    CRITICAL_FIELDS,
    REQUIRED_FIELDS,
    SCHEMA,
    CodecError,
    classify,
    critical_hash,
    critical_projection,
    decode,
    encode,
    full_hash,
    safety_violations,
    validate_packet,
)

_DIGEST = re.compile(r"[0-9a-f]{64}")
# A digest reference carries only the critical projection; these fields go unseen.
_UNCHECKED_BY_DIGEST = tuple(
    field for field in REQUIRED_FIELDS if field not in CRITICAL_FIELDS and field != "schema"
)


@dataclass
class AgentStatePacket:
    """Declared structured state packet for an agent turn or session.

    Serialization validates the declared schema. Compaction comparisons cover the
    codec's ten-field critical projection; the packet remains mutable and does not
    itself enforce preservation or authenticate its declarations.
    """

    id: str
    purpose: str
    claim: str
    risk: str = "MEDIUM"
    operations: list[str] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    unknowns: list[dict[str, Any]] = field(default_factory=list)
    invariants: list[dict[str, str]] = field(default_factory=list)
    authority: list[dict[str, str]] = field(default_factory=list)
    participants: list[str] = field(default_factory=list)
    affected_parties: list[str] = field(default_factory=list)
    dissent: list[dict[str, str]] = field(default_factory=list)
    value_flow: list[dict[str, str]] = field(default_factory=list)
    recovery: list[dict[str, str]] = field(default_factory=list)
    horizon: str = "indefinite"
    yield_desc: str = "proceed"

    def __post_init__(self) -> None:
        if not self.operations:
            ops = set()
            if self.unknowns:
                ops.add("U")
            if self.authority or self.affected_parties:
                ops.add("G")
            if self.dissent:
                ops.add("V")
            if self.recovery:
                ops.add("F")
            if self.yield_desc:
                ops.add("Y")
            self.operations = sorted(ops) if ops else ["Y"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to the canonical LAMAGUE-SEMANTIC-PACKET-1 schema dictionary."""
        data = {
            "schema": SCHEMA,
            "id": self.id,
            "purpose": self.purpose,
            "claim": self.claim,
            "risk": self.risk,
            "operations": list(self.operations),
            "evidence": copy.deepcopy(self.evidence),
            "unknowns": copy.deepcopy(self.unknowns),
            "invariants": copy.deepcopy(self.invariants),
            "authority": copy.deepcopy(self.authority),
            "participants": list(self.participants),
            "affectedParties": list(self.affected_parties),
            "dissent": copy.deepcopy(self.dissent),
            "valueFlow": copy.deepcopy(self.value_flow),
            "recovery": copy.deepcopy(self.recovery),
            "horizon": self.horizon,
            "yield": self.yield_desc,
        }
        return validate_packet(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentStatePacket:
        """Create an AgentStatePacket from a dictionary conforming to the schema."""
        valid = validate_packet(copy.deepcopy(data))
        return cls(
            id=valid["id"],
            purpose=valid["purpose"],
            claim=valid["claim"],
            risk=valid["risk"],
            operations=list(valid["operations"]),
            evidence=copy.deepcopy(valid["evidence"]),
            unknowns=copy.deepcopy(valid["unknowns"]),
            invariants=copy.deepcopy(valid["invariants"]),
            authority=copy.deepcopy(valid["authority"]),
            participants=list(valid["participants"]),
            affected_parties=list(valid["affectedParties"]),
            dissent=copy.deepcopy(valid["dissent"]),
            value_flow=copy.deepcopy(valid["valueFlow"]),
            recovery=copy.deepcopy(valid["recovery"]),
            horizon=valid["horizon"],
            yield_desc=valid["yield"],
        )

    def to_wire(self, codebook: dict[str, Any] | None = None) -> str:
        """Compress to L1 or L1D compact wire format."""
        return encode(self.to_dict(), codebook)

    @classmethod
    def from_wire(cls, wire: str, codebook: dict[str, Any] | None = None) -> AgentStatePacket:
        """Decompress L1 or L1D compact wire format into an AgentStatePacket."""
        data = decode(wire, codebook)
        return cls.from_dict(data)

    @property
    def critical_hash(self) -> str:
        """Cryptographic SHA-256 digest of the 10 critical accountability fields."""
        return critical_hash(self.to_dict())

    @property
    def full_hash(self) -> str:
        """Cryptographic SHA-256 digest of the full canonical packet."""
        return full_hash(self.to_dict())

    def critical_projection(self) -> dict[str, Any]:
        """Extract only the critical accountability fields."""
        return critical_projection(self.to_dict())


class CompactionShield:
    """Stateless utility methods for compacting and verifying agent state integrity."""

    @staticmethod
    def compact(
        packet: AgentStatePacket | dict[str, Any], codebook: dict[str, Any] | None = None
    ) -> str:
        """Encode an AgentStatePacket or dictionary into compact wire format."""
        raw = packet.to_dict() if isinstance(packet, AgentStatePacket) else packet
        return encode(raw, codebook)

    @staticmethod
    def decompact(wire: str, codebook: dict[str, Any] | None = None) -> AgentStatePacket:
        """Decode compact wire format into an AgentStatePacket."""
        data = decode(wire, codebook)
        return AgentStatePacket.from_dict(data)

    @staticmethod
    def verify_integrity(
        reference: AgentStatePacket | dict[str, Any] | str,
        candidate: AgentStatePacket | dict[str, Any],
    ) -> dict[str, Any]:
        """Compare the codec's critical projection and declared cross-field rules.

        ``is_safe`` reports the codec's equivalence classification, not general
        safety: it is True for EXACT_EQUIVALENT and PARTIAL_EQUIVALENT only.

        Detected against a reference packet: a dropped record in unknowns,
        authority, participants, affectedParties, dissent, valueFlow or recovery; a
        protected unknown that disappears or loses protection; any other change to
        a critical field, reordering included; and a candidate that breaks a
        semantic safety rule, whether or not the reference broke it first.

        Not detected: changes to risk, evidence, horizon, yield, id or operations,
        which stay PARTIAL_EQUIVALENT and are named in ``changed_fields``; whether
        any declaration is true or complete; and, against a digest reference,
        anything outside the critical projection (named in ``unchecked_fields``).
        A stale candidate passes whenever the newer reference changed only
        non-critical fields. A caller that acts on risk must bind it separately.

        Args:
            reference: Reference packet, reference dict, or reference critical_hash hex string.
            candidate: Candidate packet or candidate dict.

        Returns:
            Dict containing:
                "is_safe": bool (True if EXACT_EQUIVALENT or PARTIAL_EQUIVALENT)
                "classification": "EXACT_EQUIVALENT" | "PARTIAL_EQUIVALENT" |
                                  "UNSAFE_COLLAPSE" | "DIVERGENT" | "UNDECODABLE"
                "reason": str
                "candidate_critical_hash": str, or None when the candidate is invalid
                optional "violations", "fields", "changed_fields", "unchecked_fields"
        """
        cand_dict = candidate.to_dict() if isinstance(candidate, AgentStatePacket) else candidate
        try:
            cand_dict = validate_packet(copy.deepcopy(cand_dict))
            cand_crit_hash = critical_hash(cand_dict)
        except CodecError as err:
            return {
                "is_safe": False,
                "classification": "UNDECODABLE",
                "reason": str(err),
                "candidate_critical_hash": None,
            }

        # Case 1: reference is a critical-hash digest. Only the critical projection
        # can be compared, so a match says nothing about the remaining fields.
        if isinstance(reference, str):
            if not _DIGEST.fullmatch(reference):
                return {
                    "is_safe": False,
                    "classification": "UNDECODABLE",
                    "reason": "reference digest must be 64 lowercase hexadecimal characters",
                    "candidate_critical_hash": cand_crit_hash,
                }
            violations = safety_violations(cand_dict)
            if violations:
                return {
                    "is_safe": False,
                    "classification": "UNSAFE_COLLAPSE",
                    "reason": f"Semantic safety violations: {', '.join(violations)}",
                    "candidate_critical_hash": cand_crit_hash,
                    "violations": sorted(violations),
                }
            if reference == cand_crit_hash:
                return {
                    "is_safe": True,
                    "classification": "PARTIAL_EQUIVALENT",
                    "reason": (
                        "critical semantic hash matched reference digest; "
                        "fields outside the critical projection were not compared"
                    ),
                    "candidate_critical_hash": cand_crit_hash,
                    "unchecked_fields": list(_UNCHECKED_BY_DIGEST),
                }
            return {
                "is_safe": False,
                "classification": "DIVERGENT",
                "reason": "candidate critical hash does not match reference digest",
                "candidate_critical_hash": cand_crit_hash,
            }

        # Case 2: reference is an AgentStatePacket or dict
        ref_dict = reference.to_dict() if isinstance(reference, AgentStatePacket) else reference
        res = classify(ref_dict, cand_dict)
        classification = res.get("classification", "UNDECODABLE")
        is_safe = classification in ("EXACT_EQUIVALENT", "PARTIAL_EQUIVALENT")

        out = {
            "is_safe": is_safe,
            "classification": classification,
            "reason": res.get("reason", ""),
            "candidate_critical_hash": cand_crit_hash,
        }
        for key in ("violations", "fields", "changed_fields"):
            if key in res:
                out[key] = res[key]
        return out


class ContextProtector:
    """Stateful accumulator for managing agent context across multiple turns.

    Exports independent nested snapshots. Verification compares declared fields
    in the codec's critical projection and its cross-field rules, rather than
    guaranteeing general safety or preserving arbitrary reasoning. Retain an
    exported reference to detect later changes to this mutable accumulator.
    """

    def __init__(
        self,
        session_id: str,
        purpose: str,
        claim: str = "In progress",
        risk: str = "MEDIUM",
        horizon: str = "indefinite",
        yield_desc: str = "proceed",
    ) -> None:
        self.session_id = session_id
        self.purpose = purpose
        self.claim = claim
        self.risk = risk
        self.horizon = horizon
        self.yield_desc = yield_desc

        self.invariants: list[dict[str, str]] = []
        self.unknowns: list[dict[str, Any]] = []
        self.recovery: list[dict[str, str]] = []
        self.authority: list[dict[str, str]] = []
        self.participants: list[str] = []
        self.affected_parties: list[str] = []
        self.dissent: list[dict[str, str]] = []
        self.value_flow: list[dict[str, str]] = []
        self.evidence: list[dict[str, str]] = []

    def add_invariant(self, inv_id: str, text: str) -> ContextProtector:
        """Add a declared negative constraint or behavioral rule."""
        self.invariants.append({"id": inv_id, "text": text})
        return self

    def add_unknown(
        self, unknown_id: str, required_for: str, protected: bool = True
    ) -> ContextProtector:
        """Add an unresolved question, dependency, or blind spot."""
        self.unknowns.append(
            {
                "id": unknown_id,
                "protected": protected,
                "requiredFor": required_for,
            }
        )
        return self

    def add_recovery(self, recovery_id: str, text: str) -> ContextProtector:
        """Add a rollback path, restore point, or disaster mitigation step."""
        self.recovery.append({"id": recovery_id, "text": text})
        return self

    def add_authority(self, auth_id: str, scope: str, text: str) -> ContextProtector:
        """Add a role holding decision or veto power."""
        self.authority.append({"id": auth_id, "scope": scope, "text": text})
        return self

    def add_dissent(self, party: str, position: str) -> ContextProtector:
        """Record an objection, cautionary note, or minority finding."""
        self.dissent.append({"party": party, "position": position})
        return self

    def add_participant(self, participant: str) -> ContextProtector:
        """Add a contributing actor or agent to the session."""
        if participant not in self.participants:
            self.participants.append(participant)
        return self

    def add_affected_party(self, party: str) -> ContextProtector:
        """Add a stakeholder affected by the session's actions."""
        if party not in self.affected_parties:
            self.affected_parties.append(party)
        return self

    def add_evidence(self, ev_id: str, text: str, provenance: str) -> ContextProtector:
        """Attach supporting evidence or observation with declared provenance."""
        self.evidence.append({"id": ev_id, "text": text, "provenance": provenance})
        return self

    def add_value_flow(
        self, source: str, recipient: str, consent: str, kind: str
    ) -> ContextProtector:
        """Record a transfer of authority, resources, or credentials."""
        self.value_flow.append(
            {
                "source": source,
                "recipient": recipient,
                "consent": consent,
                "kind": kind,
            }
        )
        return self

    def set_claim(self, claim: str) -> ContextProtector:
        """Update current operational claim."""
        self.claim = claim
        return self

    def set_risk(self, risk: str) -> ContextProtector:
        """Update risk classification (LOW, MEDIUM, HIGH, CRITICAL)."""
        self.risk = risk
        return self

    def export_packet(self) -> AgentStatePacket:
        """Compile accumulated context into an independent validated snapshot.

        Checks the schema and declared cross-field rules (e.g., protected unknowns
        require a recovery entry). These checks do not establish actual safety.
        """
        # Cross-field check: protected unknowns require at least one recovery path
        has_protected_unknowns = any(u.get("protected", False) for u in self.unknowns)
        if has_protected_unknowns and not self.recovery:
            raise CodecError(
                "Semantic safety violation: Protected unknowns are declared, but no recovery "
                "path is registered. You must specify a recovery mechanism (e.g. backup, "
                "fallback branch, or manual rollback procedure) before compacting state."
            )

        # Cross-field check: value flow requires affected parties
        if self.value_flow and not self.affected_parties:
            raise CodecError(
                "Semantic safety violation: ValueFlow declared without any affected parties."
            )

        packet = AgentStatePacket(
            id=self.session_id,
            purpose=self.purpose,
            claim=self.claim,
            risk=self.risk,
            evidence=self.evidence,
            unknowns=self.unknowns,
            invariants=self.invariants,
            authority=self.authority,
            participants=self.participants,
            affected_parties=self.affected_parties,
            dissent=self.dissent,
            value_flow=self.value_flow,
            recovery=self.recovery,
            horizon=self.horizon,
            yield_desc=self.yield_desc,
        )
        # Reconstruct from the validated serialization so neither nested records
        # nor their enclosing lists remain shared with this live accumulator.
        return AgentStatePacket.from_dict(packet.to_dict())

    def compact(self, codebook: dict[str, Any] | None = None) -> str:
        """Export and compact accumulated context into an L1 or L1D wire string."""
        return self.export_packet().to_wire(codebook)

    @property
    def critical_hash(self) -> str:
        """Return the current SHA-256 digest of all critical accountability fields."""
        return self.export_packet().critical_hash

    def verify_candidate_summary(
        self, candidate_packet: AgentStatePacket | dict[str, Any]
    ) -> dict[str, Any]:
        """Compare a candidate's critical projection with the current live context.

        For an earlier state, pass its saved export to CompactionShield.verify_integrity.
        """
        ref_packet = self.export_packet()
        return CompactionShield.verify_integrity(ref_packet, candidate_packet)
